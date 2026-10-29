---
title: "2D.7 · COM: registro, activación y configuración"
description: "Seguir una activación COM de CLSID a interfaz: contexto, servidor in-proc o local, ThreadingModel, vistas de registro, AppID, typelib/IDL y COM sin registro, en modo de inspección."
etapa: "Etapa 2 · 2D · Windows internals (optativa)"
---

# COM: registro, activación y configuración

:::{aviso} Rama optativa 2D
El ejercicio inspecciona una clase propia o una instalación conocida. No cambia el registro de componentes ajenos, no ejecuta `DllRegisterServer`/`regsvr32` sobre binarios que no son tuyos y no configura activación automática.
:::

:::{nota} Propósito
Reconstruir cómo COM pasa de un CLSID a un servidor local o dentro del proceso y cómo usar metadatos para confirmar el contrato. El objetivo es poder responder, con evidencia, **qué archivo** atiende una clase, **en qué proceso y apartamento** corre y **por qué** fue ese y no otro.
:::

**Prerrequisitos**

- *Obligatorios:* [2D.3 Registro](2d-03-registro.html), [2D.6 COM](2d-06-com-interfaces.html).
- *Recomendados:* PE e imports ([1.4](01-pe.html)); ACL y token ([2D.1](2d-01-objetos.html)).

## El recorrido de una activación

La activación parte de una solicitud de clase y contexto. Con `CoCreateInstance(rclsid, pUnkOuter, dwClsContext, riid, ppv)` el cliente dice **qué clase** quiere, **qué tipos de servidor acepta** (`CLSCTX_INPROC_SERVER`, `CLSCTX_LOCAL_SERVER`, `CLSCTX_REMOTE_SERVER`, combinables) y **qué interfaz** espera recibir. Conceptualmente, la cadena es:

1. **CLSID + contexto de activación.** Si el hilo tiene un *activation context* activo (manifiesto), COM busca primero ahí qué DLL aloja el CLSID. Si no lo encuentra, usa el registro.
2. **Registro efectivo.** `HKEY_CLASSES_ROOT` es una vista combinada de `HKLM\Software\Classes` (máquina) y `HKCU\Software\Classes` (usuario); para una misma subclave, la entrada del usuario tiene prioridad. Además, la vista de 32 o 64 bits del proceso cambia qué subárbol se lee (ver más abajo).
3. **Servidor.** Según `dwClsContext` y lo registrado, COM elige un servidor en proceso (`InprocServer32`), uno local (`LocalServer32`, o un servicio vía `LocalService` del AppID) o uno remoto (2D.8).
4. **Class factory.** COM obtiene el *class object* de la clase: en una DLL, llamando a su export `DllGetClassObject`; en un EXE, esperando a que el servidor registre su class object al arrancar. Ese objeto implementa normalmente `IClassFactory`.
5. **Instancia e interfaz.** `IClassFactory::CreateInstance` crea el objeto y devuelve la interfaz pedida por `riid`. Si el servidor está en otro apartamento o proceso, el cliente recibe un **proxy** (2D.6).

`CoCreateInstance` equivale a `CoGetClassObject` + `IClassFactory::CreateInstance` + liberar la factory. En un binario podés ver cualquiera de las dos formas.

## `InprocServer32` y `LocalServer32`

| | `InprocServer32` | `LocalServer32` |
|---|---|---|
| Qué señala | Ruta de una **DLL** que se carga **en el proceso cliente**. | Línea de comando de un **EXE** que corre en **otro proceso**. |
| Cómo entrega la factory | Export `DllGetClassObject`. | El EXE registra su class object al arrancar; si no lo hace a tiempo (por defecto, 60 s), la activación expira. |
| Arquitectura | La DLL debe coincidir con la del cliente (un proceso x64 no carga una DLL x86). | Puede tener otra arquitectura; las llamadas viajan por proxy/stub. |
| Detalles útiles | Declara `ThreadingModel`. | COM agrega ` -Embedding` a la línea de comando. El valor `ServerExecutable` evita ambigüedad de ruta. Si el AppID define `LocalService`, se usa el servicio y `LocalServer32` se ignora. |
| Riesgo de lectura | Una ruta sin comillas o relativa es ambigua; verificá qué archivo se resolvería. | Igual; la documentación advierte sobre rutas sin comillas en `CreateProcess`. |

Una DLL también puede correr fuera de proceso dentro de un **surrogate** si su AppID define `DllSurrogate`. Por eso “es una DLL” no implica automáticamente “corre dentro del cliente”.

La ubicación por sí sola no determina si algo es confiable: verificá ruta, firma, propietario, permisos de la carpeta y compatibilidad de arquitectura.

## `ThreadingModel`: valores y límites

Solo aplica a servidores **en proceso**. Declara en qué apartamento (2D.6) puede vivir el objeto; COM lo usa para decidir dónde crearlo.

| Valor | Apartamento declarado | Si el cliente está en un apartamento incompatible |
|---|---|---|
| *(ausente)* | Solo el **STA principal** (el primero inicializado). | Se crea en el STA principal y el cliente recibe un proxy. |
| `Apartment` | STA. | Si el cliente está en la MTA, COM crea o usa un **host STA**; el cliente recibe un proxy. |
| `Both` | STA o MTA. | Se crea en el mismo apartamento del cliente. |
| `Free` | MTA. | Si el cliente es STA, se crea en la MTA (o en una *host MTA* creada por COM); proxy. |
| `Neutral` | Apartamento neutral. | Se crea en el apartamento neutral. |

Límites que conviene escribir en el informe:

- Es una **declaración del autor**, no una prueba: `Both` o `Free` no demuestran que el código sea seguro entre hilos.
- Debe ser el mismo valor para todos los objetos de ese servidor.
- Explica **por qué aparece un proxy** aun en una activación in-proc: no siempre hay un salto de proceso detrás.

## Registro por usuario, por máquina y vistas de 32/64 bits

- **Usuario vs. máquina.** Un CLSID puede estar en `HKCU\Software\Classes\CLSID`, en `HKLM\Software\Classes\CLSID` o en ambos. La vista `HKCR` da prioridad al usuario. La documentación aclara que, si una aplicación corre con derechos de administrador y UAC deshabilitado, el runtime COM ignora la configuración por usuario. Un proceso que atiende a clientes distintos del usuario interactivo (un servicio, por ejemplo) necesita abrir explícitamente la vista de ese usuario con `RegOpenUserClassesRoot`.
- **WOW64.** En Windows 7 y posteriores de 64 bits, `HKLM\Software\Classes\CLSID`, `HKCU\Software\Classes\CLSID` e `...\Interface` están **redirigidas**: un proceso de 32 bits ve otra copia (bajo `Wow6432Node`). En cambio `...\Classes\AppID` está **compartida**, y `Wow6432Node\Typelib` es un enlace a la clave compartida. Consecuencia: el mismo CLSID puede resolver a archivos distintos según la arquitectura del cliente.

Antes de afirmar “el CLSID no está registrado”, anotá **qué vista** consultaste (usuario/máquina, 32/64) y con qué herramienta. Regedit de 64 bits muestra `Wow6432Node` como una rama más; una API con `KEY_WOW64_32KEY` o `KEY_WOW64_64KEY` elige la vista explícitamente.

## AppID, TypeLib e IDL: qué prueba cada uno

| Metadato | Qué aporta | Qué **no** demuestra |
|---|---|---|
| **AppID** (`HKLM\Software\Classes\AppID\{GUID}`, enlazado desde el valor `AppID` del CLSID) | Configuración común de los objetos DCOM de un mismo ejecutable: `LaunchPermission`, `AccessPermission`, `RunAs`, `LocalService`, `DllSurrogate`, `AuthenticationLevel`, `RemoteServerName`, entre otros. | Que esos valores sean los efectivos: si el proceso llama a `CoInitializeSecurity`, sus parámetros reemplazan a los del registro (2D.8). Tampoco prueba que la clase se active remotamente. |
| **TypeLib** (`.tlb` o recurso dentro de la DLL; referenciada por `TypeLib` o por `tlbid`) | Descripción binaria de interfaces, métodos, parámetros y tipos; base del marshaling de automatización. | Que la implementación cumpla el contrato, que todos los métodos estén implementados o que no haya métodos no documentados. |
| **IDL** (fuente que MIDL compila a headers, typelib y código proxy/stub) | El contrato tal como lo escribió el autor: herencia, orden de métodos, atributos `[in]`/`[out]`. | Que el binario distribuido se haya compilado de **ese** IDL o de esa versión. |
| **`Interface\{IID}`** con `ProxyStubClsid32` | Qué proxy/stub se usa para marshalear ese IID. | Qué objeto implementa la interfaz. |

Regla práctica: los metadatos te dan **hipótesis de nombres y contratos**; la implementación y la ejecución en laboratorio las confirman o las refutan.

## Activación sin registro (registration-free COM)

Una aplicación puede declarar sus clases COM en un **manifiesto** en lugar del registro. En un manifiesto de ensamblado, el elemento `file` (la DLL) contiene uno o más `comClass` con atributos como `clsid`, `threadingModel`, `progid` y `tlbid`, y puede incluir `typelib` y `comInterfaceProxyStub`. Cuando el hilo tiene ese **contexto de activación** activo, `CoCreateInstance` y `CLSIDFromProgID` lo consultan **antes** que el registro; si el contexto no contiene la información, COM recurre al registro como siempre. Los contextos de activación son por hilo, y COM los propaga al hilo anfitrión al cargar la DLL.

Para el análisis, esto significa que **una búsqueda en el registro puede dar vacío y la activación igual funcionar**. Dónde mirar, en modo lectura:

- manifiesto de aplicación embebido como recurso del EXE o archivo `.manifest` junto al ejecutable;
- manifiestos de ensamblados privados (archivo junto a la DLL o recurso de la DLL);
- llamadas a las APIs de contextos de activación en el cliente.

## Ejemplo trabajado: observación frente a inferencia

*(Ejemplo **ilustrativo**: rutas ficticias de un componente propio; las cadenas entre llaves son marcadores didácticos, no GUID utilizables. No es salida de una VM.)*

```text
Cliente: BlocCliente.exe (PE32+, x64)
Llamada vista en el desensamblado:
  CoCreateInstance(CLSID {A...1}, NULL, CLSCTX_INPROC_SERVER|CLSCTX_LOCAL_SERVER, IID {D...4}, &p)

Vista 64 bits:
  HKCU\Software\Classes\CLSID\{A...1}   (no existe)
  HKLM\Software\Classes\CLSID\{A...1}
    AppID           {B...2}
    InprocServer32  (Default)       C:\CLS-Lab\x64\BlocCom.dll
                    ThreadingModel  Both
    TypeLib         {C...3}
HKLM\Software\Classes\AppID\{B...2}
    (sin LaunchPermission / AccessPermission / RunAs)
Vista 32 bits (Wow6432Node):
  HKLM\Software\Classes\Wow6432Node\CLSID\{A...1}
    LocalServer32   "C:\CLS-Lab\x86\BlocSrv.exe"
Manifiesto de BlocCliente.exe: sin comClass
```

| Afirmación | Tipo | Por qué |
|---|---|---|
| El cliente acepta servidor in-proc **o** local. | Observación | Flags de `dwClsContext` en el código. |
| En la vista de 64 bits, el CLSID resuelve a `BlocCom.dll` (x64). | Observación | Clave leída en esa vista. |
| No hay registro por usuario ni registro sin manifiesto que lo pise. | Observación | `HKCU` vacío y manifiesto sin `comClass`. |
| Un cliente **x86** del mismo CLSID terminaría en `BlocSrv.exe`, fuera de proceso. | Inferencia | Depende de la vista de 32 bits; habría que confirmarlo con un cliente x86. |
| Como el servidor x64 es `Both`, el objeto se crea en el apartamento del cliente y no hay proxy. | Inferencia | Se confirma resolviendo el módulo de la vtable (2D.6). |
| El AppID no define permisos propios, así que regirían los valores por defecto del equipo. | Inferencia con límite | Solo si el servidor no llama a `CoInitializeSecurity`; además, para una activación in-proc los permisos de lanzamiento no intervienen. |
| La typelib `{C...3}` describe `IID {D...4}`. | Hipótesis | Falta abrir la typelib y comparar; tampoco probaría la implementación. |

## Práctica: trazado de solo lectura

1. Elegí un componente propio ya registrado o una aplicación de laboratorio conocida.
2. Anotá la arquitectura del cliente y los flags `CLSCTX_*` que usa. Si no los ves, decilo.
3. Revisá si el cliente tiene manifiesto con `comClass` (recurso o archivo). Registrá el resultado aunque sea “no tiene”.
4. Seguí `CLSID → servidor → AppID → TypeLib` con Regedit en modo lectura, en la vista de **usuario y de máquina** y en la de **32 y 64 bits** que correspondan.
5. Anotá ruta, firma, arquitectura y `ThreadingModel` del servidor. No ejecutes un `DllRegisterServer` desconocido.
6. Clasificá cada dato como observación, inferencia o hipótesis, como en la tabla del ejemplo.
7. Si el componente de práctica no existe, analizá el ejemplo ilustrativo y declará que no verificaste activación en vivo.

## Entregable

Tabla de CLSID, contexto pedido, tipo de servidor, ruta, arquitectura, `ThreadingModel`, AppID y valores relevantes, typelib, vista de registro consultada, existencia de manifiesto y evidencias. Redactá anomalías como preguntas a investigar, no como diagnóstico automático.

## Repaso

?? ¿Qué diferencia hay entre `InprocServer32` y `LocalServer32`?
!! El primero apunta a un servidor DLL cargado en el proceso cliente (debe coincidir en arquitectura); el segundo, a un servidor ejecutable fuera del proceso, que puede tener otra arquitectura y se comunica por proxy/stub.

?? ¿Qué agrega `ThreadingModel`?
!! Declara el modelo de apartamento compatible para el servidor en proceso y determina dónde lo crea COM; no describe por sí solo toda la sincronización del código.

?? Un servidor in-proc tiene `ThreadingModel=Apartment` y el cliente está en la MTA. ¿Qué recibe el cliente?
!! Un proxy: COM crea el objeto en un host STA y marshalea las llamadas.

?? ¿Qué aporta AppID?
!! Agrupa opciones/configuración de uno o varios objetos distribuidos (permisos, identidad, surrogate, servicio) y permite relacionar la clase con ajustes DCOM. No garantiza que sean los valores efectivos si el proceso llama a `CoInitializeSecurity`.

?? ¿Un TLB demuestra el comportamiento interno?
!! No. Describe contratos y tipos; el comportamiento se confirma siguiendo la implementación.

?? Buscaste el CLSID en el registro y no aparece, pero la aplicación lo crea. ¿Qué dos explicaciones revisás primero?
!! Que estés mirando la vista equivocada (usuario/máquina o 32/64 bits) o que la clase se declare en un manifiesto y se resuelva por contexto de activación sin registro.

:::{nota} Puerta optativa
Podés seguir una activación desde CLSID hasta servidor y metadatos, distinguir servidor in-process/local, explicar el efecto de `ThreadingModel`, declarar la vista de registro consultada y reconocer cuándo el registro no alcanza por la existencia de un manifiesto.
:::

:::{nota} Lo que queda fuera
Monikers, ROT, servidores de servicio en detalle, catálogo COM+ y la creación de manifiestos o de registros propios no se desarrollan. La lección enseña a **leer** una configuración, no a registrar componentes.
:::

## Fuentes

- Microsoft Learn, activación: [CoCreateInstance](https://learn.microsoft.com/en-us/windows/win32/api/combaseapi/nf-combaseapi-cocreateinstance), [CoGetClassObject](https://learn.microsoft.com/en-us/windows/win32/api/combaseapi/nf-combaseapi-cogetclassobject), [IClassFactory](https://learn.microsoft.com/en-us/windows/win32/api/unknwn/nn-unknwn-iclassfactory), [DllGetClassObject](https://learn.microsoft.com/en-us/windows/win32/api/combaseapi/nf-combaseapi-dllgetclassobject), [COM Clients and Servers](https://learn.microsoft.com/en-us/windows/win32/com/com-clients-and-servers).
- Microsoft Learn, registro: [COM Registry Keys](https://learn.microsoft.com/en-us/windows/win32/com/com-registry-keys), [InprocServer32](https://learn.microsoft.com/en-us/windows/win32/com/inprocserver32), [LocalServer32](https://learn.microsoft.com/en-us/windows/win32/com/localserver32), [AppID Key](https://learn.microsoft.com/en-us/windows/win32/com/appid-key), [Interface Key](https://learn.microsoft.com/en-us/windows/win32/com/interface-key), [Merged View of HKEY_CLASSES_ROOT](https://learn.microsoft.com/en-us/windows/win32/sysinfo/merged-view-of-hkey-classes-root), [Registry Keys Affected by WOW64](https://learn.microsoft.com/en-us/windows/win32/winprog64/shared-registry-keys).
- Microsoft Learn, metadatos y sin registro: [Generating a type library with MIDL](https://learn.microsoft.com/en-us/windows/win32/midl/generating-a-type-library-with-midl-2), [Creating Registration-Free COM Objects](https://learn.microsoft.com/en-us/windows/win32/sbscs/creating-registration-free-com-objects), [Assembly Manifests](https://learn.microsoft.com/en-us/windows/win32/sbscs/assembly-manifests), [Activation Contexts](https://learn.microsoft.com/en-us/windows/win32/sbscs/activation-contexts).
- **CLS:** Registro/WOW64 en [2D.3](2d-03-registro.html); COM base en [2D.6](2d-06-com-interfaces.html).

:::{nota} Etiquetas
**Observado en CLS:** registro y permisos tratados en 2D.3. **Conocimiento externo:** activación, `ThreadingModel`, vistas de registro, metadatos y COM sin registro. **Ejemplo ilustrativo:** claves, rutas y conclusiones del componente ficticio. **Laboratorio verificado:** no.
:::
