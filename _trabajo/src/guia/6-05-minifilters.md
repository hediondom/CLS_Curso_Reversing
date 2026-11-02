---
title: "6.5 · Minifilters y callbacks: observación del sistema de archivos"
description: "Entender dónde se conecta un minifilter, cómo lo ordenan altitudes y grupos de carga, qué callbacks observa, a qué IRQL corren y qué evidencia usar para analizar uno; sin interceptar ni alterar datos ajenos."
etapa: "Etapa 6 · Kernel y drivers (rama optativa)"
---

# Minifilters y callbacks: observación del sistema de archivos

:::{aviso} Alcance de lectura
No construyas un filtro para bloquear, cambiar o capturar archivos de terceros. La práctica usa documentación, una muestra didáctica y archivos descartables de la VM. No cargues, descargues, adjuntes ni separes filtros del sistema.
:::

:::{nota} Propósito
Ubicar un minifilter en la pila de filesystem y describir pre/post callbacks, orden y límites de observación. Al terminar deberías poder leer la lista de filtros de una VM, ubicar cada uno por su altitud y explicar qué puede y qué no puede haber visto de una operación.
:::

**Prerrequisitos**

- *Obligatorios:* [6.1 I/O y stacks](6-01-arquitectura-kernel.html), [6.3 WinDbg](6-03-debug-kernel.html).
- *Recomendados:* [6.4 revisión de drivers](6-04-revision-driver.html).

## Funcionamiento

Un minifilter se conecta a una o más pilas de filesystem y puede recibir callbacks antes y después de operaciones de I/O. El Filter Manager y el registro de operaciones ordenan la interacción con otros filtros. Según propósito puede observar, modificar o impedir operaciones; esta lección estudia la observación y el orden conceptual, no modifica contenido.

Una operación visible en un callback no necesariamente llega al disco ni representa una acción completa: puede fallar, cancelarse, ser reintentada o transformarse en otra operación. Correlacioná status, contexto, proceso y archivo de prueba.

## Filter Manager, instancias y frames

El **Filter Manager** (`FltMgr.sys`) es un driver del sistema que se activa cuando se carga un minifilter y se adjunta a la pila de filesystem de cada volumen. Un minifilter **no** se adjunta directamente: se **registra** ante el Filter Manager con los tipos de operación que quiere ver. La adhesión de un minifilter a un volumen, a una altitud determinada, se llama **instancia**. Para convivir con filtros heredados (*legacy*), el Filter Manager puede tener varios **frames** en la pila, cada uno cubriendo un rango de altitudes.

Un minifilter puede recibir tres clases de operaciones: las basadas en IRP, las de **fast I/O** y las de callbacks del sistema de archivos. Una misma acción del usuario puede llegar por un camino u otro, así que “no vi el IRP” no significa “no hubo operación”.

## Altitudes y grupos de carga

Cada minifilter tiene una **altitud**: un número (interpretado como decimal) que fija su posición en la pila. Microsoft asigna las altitudes y define **grupos de carga** con rangos por tipo de producto. Algunos ejemplos de la tabla oficial:

| Grupo de carga | Rango de altitud | Propósito declarado |
|---|---|---|
| FSFilter Activity Monitor | 360000–389999 | Observar e informar sobre la E/S de archivos |
| FSFilter Anti-Virus | 320000–329999 | Detectar y desinfectar durante la E/S |
| FSFilter Replication | 300000–309999 | Replicar datos a servidores remotos |
| FSFilter Content Screener | 260000–269999 | Impedir la creación de ciertos archivos o contenidos |
| FSFilter Encryption | 140000–149999 | Cifrar y descifrar durante la E/S |
| FSFilter Virtualization | 130000–139999 | Virtualizar rutas de archivo |

Para el análisis, la altitud es una **pista de propósito**: un filtro en el rango de antivirus probablemente pertenece a un producto de seguridad. Microsoft publica además una lista de altitudes asignadas con empresa y nombre de archivo, útil para identificar un filtro desconocido. Que la altitud caiga en un rango no prueba qué hace el filtro, pero un filtro sin correspondencia en la lista pública es algo a preguntar.

## Orden de los callbacks

Cuando el Filter Manager recibe una operación, llama a los **preoperation callbacks** en orden de altitud **de mayor a menor**, y después, al completarse, a los **postoperation callbacks** en orden **inverso**, de menor a mayor. Un filtro alto ve la operación primero en la ida y último en la vuelta.

**Qué puede decidir un preoperation callback** (valores documentados):

| Valor devuelto | Significado |
|---|---|
| `FLT_PREOP_SUCCESS_NO_CALLBACK` | Deja pasar la operación y no quiere su postoperation |
| `FLT_PREOP_SUCCESS_WITH_CALLBACK` | Deja pasar y quiere ver el resultado final en el postoperation |
| `FLT_PREOP_PENDING` | La deja pendiente para completarla o continuarla después |
| `FLT_PREOP_SYNCHRONIZE` | Pide que el postoperation corra en el mismo hilo que el pre |
| `FLT_PREOP_COMPLETE` | Termina la operación ahí, con un estado final propio |

`FLT_PREOP_COMPLETE` es el caso en que un filtro **impide** o **responde** una operación sin que llegue a los filtros inferiores ni al sistema de archivos: por eso un filtro alto puede hacer que otro, más bajo, nunca vea algo.

**IRQL y contexto.** Un preoperation se llama a `PASSIVE_LEVEL` o `APC_LEVEL`, casi siempre en el hilo que originó la E/S. Un postoperation, como una rutina de completion, se llama a IRQL de hasta `DISPATCH_LEVEL` y en un hilo arbitrario, salvo excepciones documentadas (post-create a `PASSIVE_LEVEL` en el hilo original, operaciones sincronizadas y fast I/O). Esto explica por qué un filtro bien escrito toma en el pre la información que necesitará en el post.

## Inspección de solo lectura

- **En la VM, con privilegios de administrador:** `fltmc filters` lista los minifilters cargados con su altitud y cantidad de instancias, y `fltmc instances` muestra en qué volúmenes está cada uno. Las otras órdenes de `fltmc` (cargar, descargar, adjuntar, separar) **no** se usan en este curso.
- **Con el depurador de kernel de la 6.3:** la extensión `!fltkd` ofrece `!filters`, `!frames`, `!instance` y `!volumes`, y `!cbd`, el equivalente de `!irp` para los datos de callback del Filter Manager.

## Ejemplo trabajado

*(Flujo esquemático ficticio.)*

```text
app solicita abrir C:\Lab\sample.txt
  -> pre-operation callback (observa operación/flags)
  -> filesystem y filtros inferiores
  -> post-operation callback (status final/contexto)
  -> app recibe resultado
```

El callback de pre-op no prueba que la apertura haya tenido éxito; el status final aparece después. Un driver distinto puede alterar el orden observado.

Ficha de inventario de una VM (ilustrativa; nombres y altitudes ficticios):

| Filtro | Altitud | Grupo inferido | Instancias | Lectura |
|---|---|---|---|---|
| `labmon` | 370100 | Activity Monitor | C:, D: | Observa E/S en ambos volúmenes |
| `labav` | 321500 | Anti-Virus | C: | Ve la operación **después** de `labmon` en la ida y **antes** en la vuelta |
| `labcrypt` | 141000 | Encryption | D: | Si cifra, los filtros más altos ven datos en claro y los más bajos, cifrados |

Lo que **no** se puede afirmar con esta ficha: qué hace cada filtro con las operaciones, si alguno completa operaciones en el pre, ni a qué producto pertenece sin contrastar la lista pública de altitudes y el inventario de software.

## Práctica

Lee el diagrama y callbacks de una muestra oficial de minifilter sin instalarla. Opcionalmente, inspecciona un minifilter ya presente en una VM con herramientas administrativas de solo lectura y registra nombre/altitud/estado. No descargues ni cambies filtros del sistema. Si se usa una muestra cargada por el instructor, solo observa accesos a archivos creados para el lab y revierte snapshot.

1. En la muestra, enumerá qué operaciones registra, qué devuelve cada pre y si hay post.
2. En la VM, completá la ficha de inventario con `fltmc filters` y `fltmc instances`.
3. Ubicá cada filtro en su grupo por la altitud y contrastalo con la lista pública de altitudes asignadas.

## Entregable

Diagrama de stack con altitudes, puntos pre/post, ficha de inventario, datos observados, límites y confirmación de que no se alteraron archivos ni filtros de la máquina.

## Repaso

?? ¿Pre-operation demuestra que la operación se completó?
!! No. La operación aún puede fallar o cancelarse; hay que leer resultado/post-op.

?? ¿Un minifilter siempre modifica datos?
!! No. Puede observar, filtrar o modificar; depende de su implementación.

?? ¿En qué orden se llaman los callbacks de varios minifilters?
!! Los pre, de mayor a menor altitud; los post, en orden inverso.

?? ¿Qué significa `FLT_PREOP_COMPLETE` para los filtros inferiores?
!! Que la operación terminó en ese filtro: los inferiores y el sistema de archivos no la ven.

?? ¿Por qué un postoperation no puede usar memoria paginada en general?
!! Porque puede correr hasta `DISPATCH_LEVEL` en un hilo arbitrario, salvo las excepciones documentadas.

?? ¿Qué te dice la altitud de un filtro?
!! Su posición en la pila y, por el rango, el tipo de producto declarado; no prueba qué hace.

?? ¿Por qué no retirar un filtro desconocido durante análisis?
!! Puede pertenecer al sistema o producto crítico; documenta y consulta al administrador para preservar estabilidad/evidencia.

:::{nota} Puerta optativa
Podés explicar el recorrido de una operación, ubicar filtros por altitud y grupo, distinguir callback previo de resultado final, explicar el efecto de cada valor de retorno del pre y documentar un inventario con alcance y límites.
:::

---

## 6.5.b — Windows Filtering Platform (WFP): El "Minifilter" de la Red

Así como el **Filter Manager** (`FltMgr.sys`) gobierna la intercepción de archivos en disco, el subsistema de red de Windows implementa **WFP (Windows Filtering Platform)** para mediar, inspeccionar, autorizar y modificar el tráfico de red en modo kernel. WFP es la base técnica de los firewalls de próxima generación, soluciones EDR, proxies locales y sistemas de prevención de intrusiones corporativos.

### Arquitectura Interna de WFP vs. Minifilters de Filesystem
A diferencia del modelo de altitudes de filesystem, WFP está integrado directamente en el stack TCP/IP (`tcpip.sys`) y en el driver del cliente de filtrado (`fwpkclnt.sys`). Opera mediante una jerarquía de capas (*Filtering Layers*), filtros, subcapas y módulos de llamada (*Callouts*):

1. **Capas de Filtrado Clave (*Layers*):**
   - **`FWPM_LAYER_ALE_AUTH_CONNECT_V4` / `_V6`:** *Application Layer Enforcement* para conexiones salientes. Intercepta la llamada de red en el momento exacto en que un proceso invoca `connect()`, **antes** de que el paquete TCP SYN salga al cable. Provee el PID del proceso emisor, el path completo del ejecutable y las tuplas IP/puerto de origen y destino.
   - **`FWPM_LAYER_ALE_AUTH_RECV_ACCEPT_V4` / `_V6`:** Intercepta intentos de conexión entrante (`listen()` / `accept()`), permitiendo bloquear puertos a nivel de proceso.
   - **`FWPM_LAYER_INBOUND_TRANSPORT_V4` / `FWPM_LAYER_OUTBOUND_TRANSPORT_V4`:** Intercepción a nivel de paquete de transporte (TCP/UDP) post-reasignación. Provee acceso al descriptor de memoria de red `NET_BUFFER_LIST` (`NBL`).
   - **`FWPM_LAYER_DATAGRAM_DATA_V4` / `_V6`:** Inspección de payloads UDP crudos.

2. **Callouts de Kernel (`FWPS_CALLOUT`):**
   Un controlador de seguridad registra un Callout llamando a `FwpsCalloutRegister`. La estructura define tres punteros de función fundamentales:
   - **`classifyFn`:** La función principal invocada por WFP cada vez que un paquete o conexión coincide con las reglas de filtrado.
   - **`notifyFn`:** Notifica al driver cuando se añaden o eliminan reglas asociadas al Callout.
   - **`flowDeleteFn`:** Notifica cuando un flujo de red contextual se termina, permitiendo liberar memoria de rastreo.

### Anatomía de la Función de Clasificación (`classifyFn`)
```c
void ClassifyCallback(
    const FWPS_INCOMING_VALUES0* inFixedValues,
    const FWPS_INCOMING_METADATA_VALUES0* inMetaValues,
    void* layerData,
    const void* classifyContext,
    const FWPS_FILTER0* filter,
    UINT64 flowContext,
    FWPS_CLASSIFY_OUT0* classifyOut
) {
    // 1. Obtener el PID del proceso desde los metadatos ALE
    UINT64 processId = 0;
    if (FWPS_IS_METADATA_FIELD_PRESENT(inMetaValues, FWPS_METADATA_FIELD_PROCESS_ID)) {
        processId = inMetaValues->processId;
    }

    // 2. Extraer dirección IP y puerto de destino (en FWPM_LAYER_ALE_AUTH_CONNECT_V4)
    UINT32 ipDest = inFixedValues->incomingValue[FWPS_FIELD_ALE_AUTH_CONNECT_V4_IP_REMOTE_ADDRESS].value.uint32;
    UINT16 puertoDest = inFixedValues->incomingValue[FWPS_FIELD_ALE_AUTH_CONNECT_V4_IP_REMOTE_PORT].value.uint16;

    // 3. Decisión defensiva de filtrado:
    // FWP_ACTION_PERMIT  : Permite el tráfico sin restricciones.
    // FWP_ACTION_BLOCK   : Descarta el paquete o rechaza la conexión TCP de inmediato.
    // FWP_ACTION_CONTINUE: Pasa la decisión a las subcapas siguientes.
    if (puertoDest == 4444) { // Detección de puerto sospechoso de reversa
        classifyOut->actionType = FWP_ACTION_BLOCK;
        classifyOut->flags |= FWPS_CLASSIFY_OUT_FLAG_ABSORB; // Absorbe el paquete para evitar RST
        return;
    }

    classifyOut->actionType = FWP_ACTION_PERMIT;
}
```

### Herramientas de Inspección Defensiva de WFP
Un analista de malware o respuesta a incidentes debe auditar qué filtros y callouts están instalados en una máquina para verificar si una amenaza o software de seguridad está interceptando el tráfico de red:

1. **Inspección Nativa con `netsh`:**
   ```cmd
   netsh wfp show state
   ```
   Este comando genera un archivo **`wfpstate.xml`** en el directorio actual. Al parsearlo, se listan todos los proveedores (`providers`), filtros activos (`filters`) con sus condiciones booleanas, y los GUIDs de los callouts enlazados a drivers de terceros.
2. **Inspección con `wfptool` y WinDbg:**
   - La herramienta de auditoría `wfptool.exe` permite listar filtros activos filtrando por PID del proceso o por capa (`ALE_AUTH_CONNECT_V4`).
   - En WinDbg kernel mode:
     ```text
     !wfp layers
     !wfp callouts
     ```
     Permite inspeccionar los punteros a `classifyFn` en la memoria del kernel para identificar qué driver (`.sys`) maneja cada capa de red.


## Fuentes

- Microsoft Learn: [About File System Filter Drivers](https://learn.microsoft.com/en-us/windows-hardware/drivers/ifs/about-file-system-filter-drivers), [Filter Manager concepts](https://learn.microsoft.com/en-us/windows-hardware/drivers/ifs/filter-manager-concepts), [Writing Preoperation Callback Routines](https://learn.microsoft.com/en-us/windows-hardware/drivers/ifs/writing-preoperation-callback-routines), [Writing Postoperation Callback Routines](https://learn.microsoft.com/en-us/windows-hardware/drivers/ifs/writing-postoperation-callback-routines).
- Microsoft Learn, altitudes y herramientas: [Load Order Groups and Altitudes for Minifilter Drivers](https://learn.microsoft.com/en-us/windows-hardware/drivers/ifs/load-order-groups-and-altitudes-for-minifilter-drivers), [Allocated filter altitudes](https://learn.microsoft.com/en-us/windows-hardware/drivers/ifs/allocated-altitudes), [Tools for Minifilter Development and Testing (Fltmc, !fltkd)](https://learn.microsoft.com/en-us/windows-hardware/drivers/ifs/development-and-testing-tools).

:::{nota} Etiquetas
**Núcleo conceptual:** monitoreo de procesos como contexto. **Conocimiento externo:** Filter Manager/minifilters, altitudes, valores de retorno e IRQL de callbacks. **Ejemplo ilustrativo:** flujo de archivo y ficha de inventario ficticia. **Laboratorio verificado:** no.
:::
