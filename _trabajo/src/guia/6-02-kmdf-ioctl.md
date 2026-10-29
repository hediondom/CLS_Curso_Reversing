---
title: "6.2 · KMDF: driver propio con IOCTL inocuo"
description: "Recorrido de una solicitud IOCTL desde DeviceIoControl hasta EvtIoDeviceControl, controles de acceso del dispositivo y del código, puntos de observación defensiva y un driver KMDF propio que responde una estructura fija."
etapa: "Etapa 6 · Kernel y drivers (rama optativa)"
---

# KMDF: driver propio con IOCTL inocuo

:::{peligro} Solo en VM de pruebas
La carga de drivers altera el kernel. Necesitás VM descartable, snapshot conocido, consola de recuperación y un paquete propio. No cambies Secure Boot, firmas ni protecciones del equipo principal. Si la VM no puede probar un driver firmado según la documentación vigente del WDK, no cargues uno sin firma: completá el análisis estático.
:::

:::{nota} Propósito
Entender cómo WDF traduce solicitudes a callbacks y practicar un canal mínimo con límites estrictos: un IOCTL consulta una estructura fija, sin lectura/escritura arbitraria de memoria. Al terminar deberías poder seguir una solicitud desde la aplicación hasta el driver, decir **en qué puntos** se controla el acceso y **dónde** se puede observar cada paso.
:::

**Prerrequisitos**

- *Obligatorios:* [6.1 arquitectura](6-01-arquitectura-kernel.html), C/estructuras, IRP/IRQL y [2D.1 ACL](2d-01-objetos.html).
- *Recomendados:* [2D.2 memoria/loader](2d-02-memoria-loader.html); [6.3 debugging de kernel](6-03-debug-kernel.html); documentación de instalación WDK para el build exacto de la VM.

## WDF y la interfaz

WDF ofrece dos marcos: **KMDF** ejecuta el driver en kernel; **UMDF** hospeda drivers compatibles en user mode, con menor impacto potencial ante fallos. El marco encapsula parte del modelo WDM, pero no elimina responsabilidades de seguridad.

El laboratorio se limita a un dispositivo software KMDF. Una única solicitud `IOCTL_BLOCLAB_QUERY_VERSION` acepta cero bytes y devuelve una estructura fija `{Size, Version, State}`. El callback verifica código, longitudes y tamaño del buffer; cualquier código desconocido se rechaza. Elegí `METHOD_BUFFERED` para este intercambio pequeño y aplica SDDL restrictiva (por ejemplo, acceso solo a Administrators/SYSTEM en la VM). No incluyas IOCTL de lectura/escritura de direcciones, mapas físicos, procesos o memoria arbitraria.

## Recorrido de una solicitud IOCTL

Seguí el camino completo; cada paso tiene su propio control y su propio punto de observación.

1. **Apertura del dispositivo.** La aplicación abre el dispositivo con `CreateFile`, normalmente a través de una **interfaz de dispositivo** (o, en drivers antiguos, de un nombre o enlace simbólico). El I/O manager compara el token del llamador con el **descriptor de seguridad del dispositivo** y entrega un handle con los derechos concedidos. WDF siempre marca sus objetos de dispositivo con `FILE_DEVICE_SECURE_OPEN`, para que ese descriptor también se aplique a cualquier nombre “dentro” del namespace del dispositivo.
2. **Envío del código.** La aplicación llama a `DeviceIoControl(handle, código, entrada, salida…)`. El I/O manager mira el campo **Access** del código: si exige `FILE_READ_DATA` o `FILE_WRITE_DATA` y el handle no tiene ese derecho, **la solicitud no llega al driver**. Con `FILE_ANY_ACCESS`, basta con tener un handle.
3. **Construcción del IRP.** El I/O manager crea un IRP `IRP_MJ_DEVICE_CONTROL`. Con `METHOD_BUFFERED`, reserva **un único buffer de sistema** del tamaño del mayor entre entrada y salida, copia ahí la entrada y lo expone en `Irp->AssociatedIrp.SystemBuffer`. El driver lee la entrada **antes** de escribir la salida en el mismo buffer.
4. **Del IRP al objeto request.** Como el driver es de WDF, el framework atiende el despacho, crea un **objeto request** (`WDFREQUEST`) que representa el IRP y lo coloca en una **cola** (`WDFQUEUE`). Según cómo se configuró la cola (secuencial, paralela o manual), el framework entrega la solicitud.
5. **Callback del driver.** El framework llama a `EvtIoDeviceControl(Queue, Request, OutputBufferLength, InputBufferLength, IoControlCode)`. El driver ya recibe las longitudes y el código: ahí valida.
6. **Acceso al buffer.** `WdfRequestRetrieveOutputBuffer(Request, MinimumRequiredSize, &buffer, &length)` devuelve el buffer solo si mide al menos `MinimumRequiredSize`; si no, devuelve `STATUS_BUFFER_TOO_SMALL`. Pasar `sizeof(BLOCLAB_INFO)` como mínimo hace que el propio framework rechace buffers cortos.
7. **Finalización.** El driver completa con `WdfRequestCompleteWithInformation(Request, status, bytes)`. El I/O manager copia `bytes` del buffer de sistema al buffer de salida del usuario y `DeviceIoControl` devuelve, con `lpBytesReturned` igual a esos bytes. Después de completar, el driver ya no puede tocar el buffer.

```text
App (user)        CreateFile ──► [ACL del dispositivo] ──► handle (derechos)
                  DeviceIoControl(code) ──► [bits Access del código vs. handle]
I/O manager       IRP_MJ_DEVICE_CONTROL + SystemBuffer (METHOD_BUFFERED)
WDF               WDFREQUEST ──► WDFQUEUE ──► EvtIoDeviceControl
Driver            valida código/longitudes ──► RetrieveOutputBuffer(min) ──► llena todo
                  ──► CompleteWithInformation(status, bytes)
I/O manager       copia bytes al buffer de la app ──► DeviceIoControl retorna
```

## Qué recibe el driver según el método del IOCTL

Los dos bits **Method** del código deciden cómo describe el I/O manager los dos buffers de `DeviceIoControl` (el primero, “de entrada”, y el segundo, “de salida” en los nombres de la API). Desde el lado del driver:

| Método | Primer buffer (entrada) | Segundo buffer (salida) | Qué hizo el I/O manager antes | Cómo lo obtiene un driver KMDF |
|---|---|---|---|---|
| `METHOD_BUFFERED` | `Irp->AssociatedIrp.SystemBuffer` | El **mismo** `SystemBuffer` | Reservó un buffer de sistema del tamaño mayor y copió la entrada; al completar copia `Information` bytes a la app. | `WdfRequestRetrieveInputBuffer` y `WdfRequestRetrieveOutputBuffer` (mismo buffer de sistema). |
| `METHOD_IN_DIRECT` / `METHOD_OUT_DIRECT` | `SystemBuffer` (copia, `InputBufferLength`) | Un **MDL** en `Irp->MdlAddress` que describe las páginas del buffer de la app (`OutputBufferLength`) | Verificó el acceso al segundo buffer y bloqueó sus páginas. `IN_DIRECT` asegura acceso de lectura (datos hacia el driver); `OUT_DIRECT`, de escritura (datos hacia la app). | Primer buffer como en buffered; el segundo, con `WdfRequestRetrieveOutputBuffer` (dirección de sistema) o `WdfRequestRetrieveOutputWdmMdl` (el MDL). |
| `METHOD_NEITHER` | `Parameters.DeviceIoControl.Type3InputBuffer`: dirección **de usuario** | `Irp->UserBuffer`: dirección **de usuario** | **Nada**: no copia, no valida, no bloquea. | Solo en `EvtIoInCallerContext` (contexto del hilo llamador): `WdfRequestRetrieveUnsafeUserInputBuffer`/`…OutputBuffer` y luego `WdfRequestProbeAndLockUserBufferForRead`/`…ForWrite`, antes de devolver la solicitud a una cola. |

Tres consecuencias para leer un driver:

- Con `METHOD_BUFFERED` el driver no toca memoria de usuario… **salvo** que la estructura de entrada contenga punteros. Un puntero embebido es una dirección de usuario sin validar, con los mismos riesgos que `METHOD_NEITHER`.
- Con direct I/O las páginas del segundo buffer están bloqueadas y accesibles, pero siguen perteneciendo al proceso: conviene tratar su contenido como dato no confiable que puede cambiar mientras el driver lo lee (conocimiento externo; la documentación citada describe el bloqueo, no esta garantía).
- Con `METHOD_NEITHER`, el driver asume todo el trabajo que en los otros métodos hace el I/O manager, y solo un driver del nivel más alto, en el contexto del hilo que llamó, puede hacerlo. Por eso en la [6.4](6-04-revision-driver.html) se trata como **patrón de revisión de riesgo**.

El laboratorio de esta lección usa `METHOD_BUFFERED` y no tiene punteros embebidos a propósito.

## Controles de acceso: cuatro capas que no se reemplazan

| Capa | Qué controla | Cómo se fija | Límite |
|---|---|---|---|
| Exposición del dispositivo | Qué caminos existen para abrirlo. | Preferir **interfaces de dispositivo**; nombrar el objeto o crear enlaces simbólicos solo si hace falta. | Cada nombre adicional es otro camino de apertura. |
| Descriptor de seguridad del dispositivo | **Quién** puede abrir un handle y con qué derechos. | `WdfDeviceInitAssignSDDLString` en el driver o seguridad declarada en el INF. Si el driver nombra el dispositivo sin SDDL propia, WDF aplica `SDDL_DEVOBJ_SYS_ALL_ADM_ALL`. | No valida el contenido de las solicitudes. |
| Bits **Access** del código IOCTL | **Qué derechos** del handle exige cada operación. | En `CTL_CODE`: `FILE_ANY_ACCESS`, `FILE_READ_DATA`, `FILE_WRITE_DATA`. Microsoft advierte que `FILE_ANY_ACCESS` solo se use si se está seguro de que no abre un camino de abuso. `IoValidateDeviceIoControlAccess` permite controles más estrictos. | Solo mira derechos del handle, no los datos. |
| Validación en el callback | **Qué datos** acepta el driver. | Lista cerrada de códigos, longitudes exactas, tamaño mínimo al pedir buffers, inicialización completa de la salida. | Es la última línea: si falla, las capas anteriores no compensan. |

## Ejemplo trabajado

*(Contrato ilustrativo, no salida de compilación ni de una VM.)*

```text
IOCTL: BLOCLAB_QUERY_VERSION
  = CTL_CODE(0x8000, 0x800, METHOD_BUFFERED, FILE_READ_DATA)
  = (0x8000 << 16) | (1 << 14) | (0x800 << 2) | 0
  = 0x80006000
Input bytes: 0
Output bytes: sizeof(BLOCLAB_INFO) = 12   ; tres ULONG
Respuesta fija: { Size=12, Version=1, State=READY }
Otros códigos / buffer corto -> error y sin escritura fuera del buffer
```

Lectura del código: `DeviceType` `0x8000` (rango de fabricante, con el bit *Common* encendido), función `0x800` (rango de fabricante, bit *Custom*), `METHOD_BUFFERED` y `FILE_READ_DATA`: un handle abierto sin derecho de lectura **no** llega al driver con esta solicitud. El mismo desglose sirve en reversing para leer constantes que aparecen en el `switch` de un driver ajeno.

Tabla de casos que debería producir el diseño:

| Caso | Dónde se decide | Resultado esperado |
|---|---|---|
| Handle sin `FILE_READ_DATA` | I/O manager (bits Access) | La solicitud no llega a `EvtIoDeviceControl`; error de acceso. |
| Código desconocido | Callback (`default:` del `switch`) | `STATUS_INVALID_DEVICE_REQUEST`, 0 bytes. |
| Salida menor que 12 bytes | `WdfRequestRetrieveOutputBuffer` con mínimo 12 | `STATUS_BUFFER_TOO_SMALL`, 0 bytes, sin escritura. |
| Entrada distinta de 0 bytes | Callback (comparación de `InputBufferLength`) | `STATUS_INVALID_PARAMETER` (decisión de diseño del laboratorio). |
| Caso válido | Callback | `STATUS_SUCCESS`, 12 bytes, estructura completa. |

La verificación del tamaño debe ocurrir antes de obtener o copiar buffers. La respuesta se inicializa por completo para no filtrar pool; no contiene punteros ni direcciones del kernel.

## Puntos de observación defensiva

Sirven tanto para tu driver como para revisar uno ajeno en la [6.4](6-04-revision-driver.html). Separá lo que se puede ver **sin cargar nada** de lo que requiere la VM.

**Estático (sin cargar el driver):**

- **INF y paquete:** clase de dispositivo, seguridad declarada, servicio que crea.
- **Cadenas SDDL** en el binario o en el INF, y llamadas a `WdfDeviceInitAssignSDDLString`, `WdfDeviceInitAssignName`, `WdfDeviceCreateSymbolicLink` o `WdfDeviceCreateDeviceInterface`.
- **Configuración de colas:** dónde se asigna `EvtIoDeviceControl` y con qué modo de despacho.
- **Códigos IOCTL:** constantes del `switch`, desglosadas en `DeviceType`, función, método y acceso. Prestá atención a `METHOD_NEITHER` y a `FILE_ANY_ACCESS`.
- **Validaciones:** si cada rama compara longitudes antes de pedir buffers y si usa un `MinimumRequiredSize` razonable.

**Dinámico (solo en la VM de pruebas, con el debugger de kernel de la 6.3):**

- Extensiones de WDF (`wdfkd.dll`): `!wdfldr` para ver la versión del framework cargada y `!wdflogdump` para leer el **In-flight Recorder** (IFR), un registro circular que WDF mantiene por driver con el progreso de IRPs y requests.
- Breakpoint en tu `EvtIoDeviceControl` para comparar longitudes y código recibidos con lo que envió la app.
- Driver Verifier y WDF Verifier sobre **tu** driver, en la VM, para detectar usos incorrectos de buffers o de IRQL.
- Desde user mode: el `GetLastError` de `DeviceIoControl` y `lpBytesReturned` para cada caso de la tabla.

## Práctica controlada

1. Partí de una muestra KMDF de Microsoft/plantilla WDK y documentá el WDK/SDK, Visual Studio, arquitectura y build de Windows usados; solo completá versiones después de verificarlas localmente.
2. Implementá el contrato fijo de consulta y las comprobaciones de longitud/código; revisá SDDL, exposición del dispositivo y configuración INF con la lista de seguridad de Microsoft. Elegí los bits Access del código y justificalos.
3. Compilá y analizá el paquete con la lista de **puntos de observación estática**. La carga es opcional y solo en VM compatible con firma de prueba siguiendo WDK actual; no uses comandos de relajación en el host.
4. Si cargaste el driver, la app cliente prueba todos los casos de la tabla: respuesta correcta, buffer de salida corto, entrada no vacía, código no admitido y handle sin derecho de lectura. Resultado esperado: respuesta fija o error limpio; nunca acceso genérico a memoria.
5. Desinstalá el paquete propio con el procedimiento documentado para esa VM, confirmá que ya no está cargado/registrado y revertí el snapshot.

**Alternativa sin carga:** si no compilaste o no podés cargar el driver en una VM compatible, hacé solo análisis estático del código fuente y del binario compilado (o de una muestra KMDF de Microsoft): recorré los siete pasos del recorrido señalando en qué línea ocurre cada uno, completá la tabla de controles y marcá cada caso de la tabla de pruebas como “esperado según el código, no ejecutado”.

## Entregable

Contrato IOCTL con el desglose del código, diagrama del recorrido, modelo de amenaza, SDDL y exposición del dispositivo, tabla de casos válidos/negativos (indicando cuáles se ejecutaron), log de build y verificación de limpieza/snapshot. Si no se cargó, marcá el ejercicio como revisión estática.

## Repaso

?? ¿Por qué el IOCTL devuelve una estructura fija?
!! Reduce superficie y permite validar longitudes y contenido de forma acotada.

?? ¿Qué riesgo resuelve una SDDL restrictiva?
!! Limita qué identidades pueden abrir el dispositivo; no reemplaza la validación dentro del driver.

?? ¿Qué controla el campo Access de un código IOCTL y quién lo aplica?
!! Qué derechos debe tener el handle para enviar ese código. Lo aplica el I/O manager antes de crear el IRP: si no se cumple, la solicitud no llega al driver.

?? Con `METHOD_BUFFERED`, ¿por qué el driver debe leer la entrada antes de escribir la salida?
!! Porque entrada y salida comparten un único buffer de sistema; escribir la salida primero puede pisar la entrada.

?? ¿Qué hace `WdfRequestRetrieveOutputBuffer` si el buffer es menor que `MinimumRequiredSize`?
!! Devuelve `STATUS_BUFFER_TOO_SMALL` y no entrega el buffer.

?? Con `METHOD_OUT_DIRECT`, ¿dónde está el buffer de salida desde el punto de vista del driver?
!! En un MDL (`Irp->MdlAddress`) que describe las páginas bloqueadas del buffer de la app; en KMDF se obtiene con `WdfRequestRetrieveOutputBuffer` o `WdfRequestRetrieveOutputWdmMdl`.

?? ¿Por qué un IOCTL `METHOD_BUFFERED` puede tener los mismos riesgos que uno `METHOD_NEITHER`?
!! Si la estructura de entrada trae punteros embebidos: esas direcciones son de usuario y el I/O manager no las valida.

?? ¿Por qué se rechaza un IOCTL desconocido?
!! Porque una solicitud no definida no debe llegar a una operación implícita o permisiva.

?? No pudiste cargar el driver en la VM. ¿Qué entregás?
!! Una revisión estática: el recorrido señalado en el código, la tabla de controles y los casos marcados como esperados y no ejecutados.

:::{nota} Puerta optativa
Podés explicar el flujo KMDF desde `DeviceIoControl` hasta la finalización, desglosar un código IOCTL, distinguir las cuatro capas de control de acceso, señalar puntos de observación estática y dinámica, y demostrar (o justificar estáticamente) validación de buffers/códigos y respuesta sin datos no inicializados.
:::

:::{nota} Lo que queda fuera
Escribir drivers con direct I/O o `METHOD_NEITHER`, DMA, la gestión de MDL propios y la firma de producción no se desarrollan. La revisión de `METHOD_NEITHER`, colas, cancelación y PnP/power sigue en la [6.4](6-04-revision-driver.html), como lectura de flujo. El laboratorio no demuestra que un driver real sea seguro: solo practica un contrato mínimo.
:::

## Fuentes

- Microsoft Learn, modelo y recorrido: [Differences between WDM and WDF](https://learn.microsoft.com/en-us/windows-hardware/drivers/wdf/differences-between-wdm-and-kmdf), [Creating Framework Request Objects](https://learn.microsoft.com/en-us/windows-hardware/drivers/wdf/framework-request-objects), [Dispatching Methods for I/O Requests](https://learn.microsoft.com/en-us/windows-hardware/drivers/wdf/dispatching-methods-for-i-o-requests), [IOCTL callback](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdfio/nc-wdfio-evt_wdf_io_queue_io_device_control), [WdfRequestRetrieveOutputBuffer](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdfrequest/nf-wdfrequest-wdfrequestretrieveoutputbuffer), [WdfRequestCompleteWithInformation](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdfrequest/nf-wdfrequest-wdfrequestcompletewithinformation).
- Microsoft Learn, códigos y acceso: [Defining I/O Control Codes](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/defining-i-o-control-codes), [Buffer Descriptions for I/O Control Codes](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/buffer-descriptions-for-i-o-control-codes), [Methods for Accessing Data Buffers](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/methods-for-accessing-data-buffers), [Using Direct I/O](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/using-direct-i-o), [Accessing Data Buffers in WDF Drivers](https://learn.microsoft.com/en-us/windows-hardware/drivers/wdf/accessing-data-buffers-in-wdf-drivers), [KMDF device access control](https://learn.microsoft.com/en-us/windows-hardware/drivers/wdf/controlling-device-access-in-kmdf-drivers), [WdfDeviceInitAssignSDDLString](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdfdevice/nf-wdfdevice-wdfdeviceinitassignsddlstring), [IoValidateDeviceIoControlAccess](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-iovalidatedeviceiocontrolaccess), [Driver security checklist](https://learn.microsoft.com/en-us/windows-hardware/drivers/driversecurity/driver-security-checklist).
- Microsoft Learn, observación y firma: [Using the Framework's Event Logger (IFR)](https://learn.microsoft.com/en-us/windows-hardware/drivers/wdf/using-the-framework-s-event-logger), [Wdfkd.dll extensions](https://learn.microsoft.com/en-us/windows-hardware/drivers/debugger/kernel-mode-driver-framework-extensions--wdfkd-dll-), [Driver Verifier](https://learn.microsoft.com/en-us/windows-hardware/drivers/devtest/driver-verifier), [Test signing](https://learn.microsoft.com/en-us/windows-hardware/drivers/install/test-signing).

:::{nota} Etiquetas
**Observado en CLS:** ninguno específico. **Conocimiento externo:** WDF, KMDF, recorrido de IOCTL, buffers y MDL por método, controles de acceso, herramientas de observación y firma. **Ejemplo ilustrativo:** contrato BlocLab, cálculo del código y tabla de casos (no compilados ni ejecutados en esta edición). **Laboratorio verificado:** no; requiere toolchain/VM y revisión de seguridad. La alternativa de análisis estático no requiere cargar nada.
:::
