---
title: "6.4 · Revisión defensiva de un driver"
description: "Auditar device names, IOCTLs, ACL/SDDL, validación de entradas, METHOD_NEITHER y punteros de usuario, propiedad y cancelación de solicitudes en un driver propio o didáctico."
etapa: "Etapa 6 · Kernel y drivers (rama optativa)"
---

# Revisión defensiva de un driver

:::{aviso} Sin explotación
Esta revisión busca defectos de diseño y evidencia para corregirlos. No pruebes IOCTLs contra drivers de terceros ni intentes conseguir acceso privilegiado. Los patrones de riesgo de esta lección se usan para **leer** código y binarios propios o didácticos, no para construir pruebas contra un kernel cargado.
:::

:::{nota} Propósito
Reconstruir la superficie de acceso de un driver desde nombre/interfaz y permisos hasta cada IOCTL y su validación, y leer el ciclo de vida de una solicitud (colas, propiedad, cancelación) para encontrar rutas donde la validación o la finalización fallan.
:::

**Prerrequisitos**

- *Obligatorios:* [6.1 modelo E/S](6-01-arquitectura-kernel.html), [6.2 KMDF](6-02-kmdf-ioctl.html), [2D.1 objetos/ACL](2d-01-objetos.html).
- *Recomendados:* [2D.2 memoria](2d-02-memoria-loader.html), [2D.11 excepciones](2d-11-excepciones.html), seguridad de [6.6](6-06-mitigaciones.html).

## Lista de lectura

1. ¿El driver crea un nombre de dispositivo solo cuando hace falta? ¿La interfaz usa ACL/SDDL limitada?
2. ¿Qué IOCTLs exporta, con qué **método** y qué permisos de acceso exige cada uno?
3. ¿Valida tamaño, versión, enum, flags, longitud de salida y estado antes de operar?
4. ¿Evita punteros del usuario, direcciones físicas, handles sin validar y salida no inicializada? Si usa `METHOD_NEITHER` o punteros embebidos, ¿aplica el patrón de la sección siguiente?
5. ¿Completa solicitudes en todas las rutas, una sola vez, y sincroniza estado compartido?
6. Si retiene solicitudes, ¿las marca como cancelables o comprueba la cancelación?

La **superficie de ataque** es el conjunto de entradas accesibles y efectos asociados; una interfaz amplia aumenta revisión necesaria, pero no basta para afirmar vulnerabilidad.

## Patrón de revisión: `METHOD_NEITHER` y punteros de usuario

Con `METHOD_NEITHER`, el I/O manager entrega al driver las **direcciones de usuario** originales (`Type3InputBuffer`, `UserBuffer`) sin validarlas ni bloquearlas (ver la tabla de métodos en la [6.2](6-02-kmdf-ioctl.html)). Lo mismo pasa con un **puntero embebido** dentro de una estructura que llegó por `METHOD_BUFFERED`: el buffer es de sistema, pero el puntero que trae adentro sigue siendo de usuario. Que un driver use cualquiera de los dos no es un defecto en sí, pero marca código que hay que leer con este patrón.

**Dónde aparece.** En el código: el bit de método `3` en las definiciones `CTL_CODE` (`METHOD_NEITHER`), accesos a `Type3InputBuffer` o `UserBuffer`, o en KMDF un `EvtIoInCallerContext` con `WdfRequestRetrieveUnsafeUserInputBuffer`/`…OutputBuffer`. En un binario: las mismas constantes en el `switch` del código de control (los dos bits bajos en `11`) y lecturas de esos campos del IRP o llamadas a esas funciones.

**Por qué `ProbeForRead` no alcanza por sí solo.** `ProbeForRead`/`ProbeForWrite` comprueban que el rango esté en la parte de usuario del espacio de direcciones y alineado, **en ese momento**. Microsoft documenta además que:

- con `Length = 0` no comprueba nada;
- deben llamarse dentro de `try/except`;
- **todo acceso posterior** también debe estar protegido, porque otro hilo de la aplicación puede liberar, sustituir o cambiar la protección del rango en cualquier momento, incluso durante o después del sondeo;
- el contenido puede cambiar mientras el driver lo usa.

Es decir: el sondeo valida una **dirección**, no una **decisión** basada en el contenido.

**Preguntas de revisión** (sobre código propio o didáctico):

| Pregunta | Qué buscar | Señal de riesgo |
|---|---|---|
| ¿Distingue llamadas desde user mode y kernel mode? | Uso de `RequestorMode` antes de sondear | Sondeo incondicional o ausencia de distinción |
| ¿La longitud sondeada es la que después se usa? | Misma variable para sondear y copiar; cálculo de tamaños sin desbordamiento | Sondeo con un tamaño y copia con otro, o multiplicaciones sin control |
| ¿Cada acceso al buffer de usuario está dentro de `try/except`? | Bloques de excepción alrededor de **todas** las lecturas y escrituras | Solo el sondeo protegido |
| ¿Captura los datos una sola vez? | Copia a un buffer del kernel y validación sobre la copia | Validar un campo en memoria de usuario y volver a leerlo para usarlo (doble lectura) |
| ¿Se usa el buffer fuera del hilo que llamó? | Bloqueo (`WdfRequestProbeAndLockUserBufferForRead`/`…ForWrite` o MDL propio) antes de encolar | Dirección de usuario guardada y usada desde otra cola, un DPC o un hilo del sistema |
| ¿Hacen falta estos punteros? | Diseño alternativo con offsets relativos o buffers de longitud variable | Punteros embebidos en una interfaz que podría ser `METHOD_BUFFERED` puro |

Lectura **ilustrativa** de un fragmento hipotético, para practicar el patrón (no es código de un driver real ni una receta):

```text
// handler hipotético, METHOD_NEITHER
p = Type3InputBuffer
ProbeForRead(p, sizeof(REQ), 4)        // dentro de try/except: OK
if (p->Len > MAX) fail                  // valida en memoria de usuario...
memcpy(local, p->Data, p->Len)          // ...y vuelve a leer Len: doble lectura
                                        // memcpy fuera del try/except: acceso sin protección
```

Hallazgos que debería registrar el informe: la validación y el uso leen `Len` dos veces de memoria de usuario; la copia no está protegida por el manejador de excepciones. Corrección propuesta: capturar la estructura completa en un buffer del kernel dentro de `try/except`, validar la copia y usar solo la copia; o rediseñar el IOCTL como `METHOD_BUFFERED` sin punteros.

## Leer el flujo de una solicitud: colas, propiedad y cancelación

Muchos defectos no están en la validación sino en **quién es dueño** de la solicitud y **cuántas veces** se completa. En WDF el modelo es explícito:

- **Propiedad.** Mientras la solicitud está en una cola, es del **framework**. Cuando la entrega a un callback, pasa a ser del **driver**, que debe hacer exactamente una de estas cosas: completarla, reencolarla, reenviarla a un destino de E/S o cancelarla. Después de eso ya no la posee y no puede tocarla (ni sus buffers).
- **Colas y despacho.** Cada cola tiene un modo de despacho (secuencial, paralelo o manual) y unos callbacks registrados; `WdfDeviceConfigureRequestDispatching` puede desviar tipos de solicitud a colas distintas. Al revisar, armá una tabla cola → modo → callbacks → tipos de solicitud.
- **Cancelación.** Si la operación se cancela, el framework cancela con `STATUS_CANCELLED` las solicitudes que **todavía no entregó** al driver. Una vez entregada, solo el driver puede cancelarla, y para enterarse debe haberla marcado con `WdfRequestMarkCancelable`/`…Ex` (registrando `EvtRequestCancel`) o consultar `WdfRequestIsCanceled` mientras la posee. Si la reencola en una cola con `EvtIoCanceledOnQueue`, el framework llama a ese callback en lugar de cancelarla, y el driver debe completarla.

Ejemplo de lectura **ilustrativo** de una solicitud retenida (no corresponde al driver de 6.2, que completa en el acto):

```text
EvtIoDeviceControl(R)          // el driver ahora posee R
  WdfRequestMarkCancelableEx(R, EvtCancel)
  guarda R en la lista "pendientes"      // espera un evento del dispositivo
--- más tarde, una de dos rutas ---
(a) llega el evento:  WdfRequestUnmarkCancelable(R) -> completa R con STATUS_SUCCESS
(b) la app cancela:   EvtCancel(R) -> quita R de la lista -> completa R con STATUS_CANCELLED
```

Preguntas de revisión: ¿hay alguna ruta en la que **ambas** ramas completen la misma solicitud? ¿Se respeta el resultado de `WdfRequestUnmarkCancelable` antes de completar? ¿La lista de pendientes está protegida contra acceso concurrente? ¿Una solicitud retenida mucho tiempo **sin** marcarse cancelable puede dejar colgado al proceso que la envió? Microsoft dedica una página a sincronizar cancelación y finalización; si el código no la sigue, es un hallazgo a documentar con archivo y línea.

:::{nota} Recuadro conceptual: PnP y energía
Un driver de función KMDF suele registrar callbacks de PnP y energía: `EvtDevicePrepareHardware`/`EvtDeviceReleaseHardware` (recursos del hardware) y `EvtDeviceD0Entry`/`EvtDeviceD0Exit` (entrada y salida del estado de trabajo D0). Las colas **administradas por energía** solo entregan solicitudes cuando el dispositivo está en D0; si no lo está, las solicitudes esperan. En la revisión basta con saber dos cosas: si la cola de IOCTL es administrada por energía (lo que explica solicitudes que “no avanzan”) y si algún callback de energía libera estado que un callback de E/S todavía puede usar. El dispositivo software de la 6.2 apenas usa esta maquinaria; el diseño de PnP/energía queda fuera del curso.
:::

## Ejemplo trabajado

*(Checklist ilustrativo para el driver de 6.2.)*

```text
Device interface: acceso solo a Administrators/SYSTEM
IOCTL 0x80006000 (BLOCLAB_QUERY_VERSION, contrato ilustrativo de 6.2)
  METHOD_BUFFERED, FILE_READ_DATA -> input=0, output=12
  sin punteros embebidos; no hay METHOD_NEITHER
Otras solicitudes: rechazadas con STATUS_INVALID_DEVICE_REQUEST
Buffer: longitud comprobada; respuesta inicializada por completo
Cola: una cola por defecto; la solicitud se completa en el mismo callback
Cancelación: no aplica (no se retienen solicitudes)
Conclusión: diseño acotado en el fragmento revisado; falta validar build/configuración INF
```

El código `0x80006000` sale del contrato **ilustrativo** de la 6.2; en un driver real se toma de su header, no se supone.

> **Ampliación editorial basada en fuentes externas — Resolución de la tabla `WdfFunctions` (`WDFFUNCTIONS`) en drivers KMDF sin símbolos en IDA y Ghidra**
>
> Al analizar estáticamente un driver KMDF sin archivo `.pdb`, las llamadas a la API del framework (`WdfDriverCreate`, `WdfDeviceCreate`, `WdfIoQueueCreate`, `WdfRequestRetrieveInputBuffer`, etc.) **no aparecen en la tabla de importaciones (IAT)** (*Microsoft Learn: KMDF Driver Entry and Binding / `wdffuncenum.h` del WDK*) (**Hecho confirmado**):
>
> 1. **Mecanismo de enlace dinámico de KMDF:**
>    El binario solo importa `WdfVersionBind` desde `WdfLdr.sys`. Durante el arranque, el stub del compilador llena una estructura `WDF_BIND_INFO` que contiene la versión del framework (p. ej. `1.15` o `1.33`) y un puntero a un puntero global en `.data`: `WdfFunctions` (de tipo `const WDFFUNCTIONS*`), junto con `WdfDriverGlobals` (`PWDF_DRIVER_GLOBALS`).
>
> 2. **Patrón en ensamblador x64:**
>    Toda llamada a una función `Wdf*` se compila como una llamada indirecta indexada sobre esa tabla global, pasando siempre `WdfDriverGlobals` como primer argumento oculto en `RCX` (lo que desplaza un lugar todos los argumentos documentados de la función):
>    ```nasm
>    ; Llamada en código C: WdfIoQueueCreate(device, &q, WDF_NO_OBJECT_ATTRIBUTES, WDF_NO_HANDLE);
>    mov     rax, cs:WdfFunctions_01015   ; Carga la base de la tabla de punteros KMDF
>    mov     rcx, cs:WdfDriverGlobals     ; 1.er arg oculto (RCX): PWDF_DRIVER_GLOBALS
>    mov     rdx, rbx                     ; 2.º arg (RDX): WDFDEVICE Device
>    lea     r8, [rsp+40h]                ; 3.er arg (R8) : PWDF_IO_QUEUE_CONFIG Config (+0x28 = EvtIoDeviceControl)
>    xor     r9d, r9d                     ; 4.º arg (R9) : WDF_NO_OBJECT_ATTRIBUTES
>    mov     qword ptr [rsp+20h], 0       ; 5.º arg (stack): Queue (NULL)
>    call    qword ptr [rax+4C0h]         ; Offset +0x4C0 (índice 152 * 8) = pfnWdfIoQueueCreate
>    ```
>
> 3. **Tabla de offsets de funciones críticas en `WDFFUNCTIONS` (`wdffuncenum.h`, KMDF 1.15–1.33):**
>
> | Función KMDF (`WDFFUNCENUM`) | Índice decimal (`TableIndex`) | Offset en x64 (`Índice * 8`) | Offset en x86 (`Índice * 4`) | Qué recibe en `RDX` / `R8` (x64, tras `DriverGlobals` en `RCX`) |
> | :--- | :--- | :--- | :--- | :--- |
> | `WdfDeviceInitAssignName` | `29` | `+0x0E8` | `+0x074` | `RDX` = `DeviceInit`, `R8` = `PCUNICODE_STRING` (`\Device\...`) |
> | `WdfDeviceInitAssignSDDLString` | `31` | `+0x0F8` | `+0x07C` | `RDX` = `DeviceInit`, `R8` = `PCUNICODE_STRING` (cadena SDDL) |
> | `WdfDeviceCreate` | `45` | `+0x168` | `+0x0B4` | `RDX` = `&DeviceInit`, `R8` = `Attributes`, `R9` = `&Device` |
> | `WdfDeviceCreateSymbolicLink` | `46` | `+0x170` | `+0x0B8` | `RDX` = `Device`, `R8` = `PCUNICODE_STRING` (`\DosDevices\...`) |
> | `WdfDeviceCreateDeviceInterface` | `47` | `+0x178` | `+0x0BC` | `RDX` = `Device`, `R8` = `const GUID* InterfaceClassGUID` |
> | `WdfDriverCreate` | `118` | `+0x3B0` | `+0x1D8` | `RDX` = `DriverObject`, `R8` = `RegistryPath`, `R9` = `Attributes`, `[rsp+20h]` = `WDF_DRIVER_CONFIG*` |
> | `WdfIoQueueCreate` | `152` | `+0x4C0` | `+0x260` | `RDX` = `Device`, `R8` = `WDF_IO_QUEUE_CONFIG*` (`+0x28` = `EvtIoDeviceControl`) |
> | `WdfRequestComplete` | `263` | `+0x838` | `+0x41C` | `RDX` = `Request`, `R8D` = `NTSTATUS` |
> | `WdfRequestCompleteWithInformation` | `265` | `+0x848` | `+0x424` | `RDX` = `Request`, `R8D` = `NTSTATUS`, `R9` = `ULONG_PTR Information` |
> | `WdfRequestRetrieveInputBuffer` | `275` | `+0x898` | `+0x44C` | `RDX` = `Request`, `R8` = `MinimumRequiredSize`, `R9` = `&Buffer` |
> | `WdfRequestRetrieveOutputBuffer` | `276` | `+0x8A0` | `+0x450` | `RDX` = `Request`, `R8` = `MinimumRequiredSize`, `R9` = `&Buffer` |
>
> 4. **Tipado rápido en IDA 9.0+ y Ghidra:**
>    Si asignás el tipo `WDFFUNCTIONS*` a la variable global `WdfFunctions` (o importás `wdf.h` / `wdffuncenum.h`), el decompilador convierte instantáneamente `(*(void (**)(...))(WdfFunctions + 0x4C0))(...)` en `WdfFunctions->pfnWdfIoQueueCreate(...)`.

## Práctica

Revisá el source de tu driver o una muestra didáctica de Microsoft:

1. Enumerá device interfaces, SDDL, definiciones de IOCTL (con método y acceso) y callbacks.
2. Trazá un IOCTL desde la entrada hasta la finalización.
3. Si hay `METHOD_NEITHER` o punteros embebidos, completá la tabla de preguntas del patrón para cada uno. Si no hay, decilo explícitamente.
4. Armá la tabla de colas (modo, callbacks, tipos de solicitud) y, para cada solicitud que el driver retenga, dibujá las rutas de finalización y de cancelación.
5. Verificá casos límite por pruebas unitarias en user mode, sin fuzzing contra un kernel cargado.

## Entregable

Tabla entrada–control–validación–resultado; tabla de colas y rutas de finalización/cancelación; hallazgos con archivo/línea, severidad razonada y corrección propuesta. No publiques el driver o detalles sensibles sin autorización.

## Repaso

?? ¿Una DACL fuerte vuelve seguro un IOCTL?
!! No. Reduce quién puede llamarlo, pero el callback debe validar toda entrada y salida.

?? ¿Por qué limitar IOCTLs?
!! Cada operación exportada amplía lo que un cliente puede pedir y debe tener contrato y permisos explícitos.

?? ¿Qué implica “superficie de ataque”?
!! Entradas y operaciones accesibles desde una frontera; es una guía de revisión, no un veredicto.

?? ¿Por qué `ProbeForRead` no vuelve seguro todo acceso posterior?
!! Porque solo comprueba rango y alineación en ese momento (y nada si la longitud es 0); otro hilo puede cambiar el contenido o la protección después. Cada acceso posterior debe estar protegido y los datos deben capturarse una vez.

?? ¿Qué es una doble lectura en este contexto?
!! Validar un valor en memoria de usuario y volver a leerlo para usarlo: entre las dos lecturas el valor puede cambiar.

?? ¿Cuándo deja el driver de poseer una solicitud WDF?
!! Cuando la completa, la reencola, la reenvía o la cancela; desde ese momento no puede acceder a ella ni a sus buffers.

?? ¿Quién cancela una solicitud que todavía está en una cola del driver?
!! El framework, con `STATUS_CANCELLED`, sin entregarla. Una vez entregada, solo el driver puede cancelarla.

?? Una solicitud de IOCTL “queda colgada” y el dispositivo está en un estado de bajo consumo. ¿Qué revisás?
!! Si la cola es administrada por energía: esas colas solo entregan solicitudes en D0.

:::{nota} Puerta optativa
Podés rastrear una operación desde la interfaz hasta su callback y demostrar permisos, validación de longitudes y tratamiento de errores; aplicar el patrón de revisión a `METHOD_NEITHER` y punteros embebidos; y leer las rutas de propiedad, finalización y cancelación de una solicitud.
:::

---

## 6.4.b — Fuzzing de IOCTLs en Kernel

La superficie de ataque primaria y más crítica de cualquier controlador de dispositivo en Windows reside en su interfaz de control de E/S: los códigos **`IOCTL`** despachados a través del manejador `IRP_MJ_DEVICE_CONTROL` (`EvtIoDeviceControl` en KMDF). Mientras que el fuzzing en espacio de usuario (Lección 2.24) prueba parsers de archivos, el **Kernel Fuzzing** somete al controlador a combinaciones anómalas de códigos de control, tamaños de buffer incongruentes y punteros no válidos para descubrir fallos de validación antes de que causen una vulnerabilidad en producción.

### Arquitectura del Harness de Fuzzing en Modo Usuario
A diferencia de un ejecutable clásico que lee de `stdin` o de un archivo, un fuzzer de kernel ejecuta un **harness en espacio de usuario** que interactúa directamente con el objeto de dispositivo del driver:
1. **Apertura del Dispositivo:** Obtiene un handle con `CreateFileW(L"\\.\MiDriver", GENERIC_READ | GENERIC_WRITE, ...)` utilizando el enlace simbólico (*Symbolic Link*) expuesto por el driver.
2. **Bucle de Mutación de IOCTLs:** Genera o permuta códigos `CTL_CODE` iterando a través de:
   - *DeviceType:* Códigos estándar o reservados (`0x8000`..`0xFFFF`).
   - *Function:* Rango de índices de función del driver (`0x800`..`0xFFF`).
   - *Method:* `METHOD_BUFFERED` (`0`), `METHOD_IN_DIRECT` (`1`), `METHOD_OUT_DIRECT` (`2`), `METHOD_NEITHER` (`3`).
3. **Manejo Estricto de Excepciones:** Como el envío de punteros inválidos hacia un driver con `METHOD_NEITHER` puede provocar un fallo en el propio llamador si no se captura, el harness encapsula `DeviceIoControl` dentro de un bloque `__try / __except`.

### Esqueleto de Código C: Harness de Fuzzing de IOCTLs
```c
// Archivo: plantillas_codigo/ioctl_fuzzer_harness.c
// Compilar con MSVC x64: cl /Zi /O2 ioctl_fuzzer_harness.c /Fe:IoctlFuzzer.exe

#include <windows.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define MAX_PAYLOAD_SIZE 4096

// Generador de payloads mutados con patrones límite
void GenerarPayloadMutado(BYTE* buffer, DWORD size) {
    static const DWORD patrones[] = { 0x00000000, 0xFFFFFFFF, 0x7FFFFFFF, 0x80000000, 0x41414141 };
    for (DWORD i = 0; i < size; i++) {
        buffer[i] = (BYTE)(rand() % 256);
    }
    // Sobrescribir los primeros 4 bytes con valores límite enteros
    if (size >= 4) {
        *(DWORD*)buffer = patrones[rand() % 5];
    }
}

int main(int argc, char* argv[]) {
    LPCWSTR deviceName = L"\\.\BlocLabDevice";
    HANDLE hDevice = CreateFileW(deviceName, GENERIC_READ | GENERIC_WRITE, 0, NULL, OPEN_EXISTING, 0, NULL);
    if (hDevice == INVALID_HANDLE_VALUE) {
        printf("[-] Error abriendo dispositivo %ls (Error: %lu)\n", deviceName, GetLastError());
        return 1;
    }

    printf("[+] Iniciando fuzzing de IOCTLs sobre %ls...\n", deviceName);
    srand((unsigned int)time(NULL));

    BYTE inBuffer[MAX_PAYLOAD_SIZE];
    BYTE outBuffer[MAX_PAYLOAD_SIZE];
    DWORD bytesReturned = 0;

    // Rango típico de IOCTLs definidos por el desarrollador (0x800 a 0x8FF)
    for (DWORD func = 0x800; func < 0x850; func++) {
        // Probar los 4 métodos de transferencia I/O
        for (DWORD method = 0; method < 4; method++) {
            DWORD ioctl = CTL_CODE(FILE_DEVICE_UNKNOWN, func, method, FILE_ANY_ACCESS);

            for (int iter = 0; iter < 100; iter++) {
                DWORD inSize = rand() % MAX_PAYLOAD_SIZE;
                DWORD outSize = rand() % MAX_PAYLOAD_SIZE;
                GenerarPayloadMutado(inBuffer, inSize);

                __try {
                    // Envío del IOCTL fuzzeado al driver de kernel
                    DeviceIoControl(
                        hDevice,
                        ioctl,
                        inBuffer,
                        inSize,
                        outBuffer,
                        outSize,
                        &bytesReturned,
                        NULL
                    );
                }
                __except (EXCEPTION_EXECUTE_HANDLER) {
                    // Capturar excepciones generadas en usermode si el driver usa METHOD_NEITHER
                    printf("[!] Excepción en usermode con IOCTL 0x%08X (InSize: %lu)\n", ioctl, inSize);
                }
            }
        }
    }

    CloseHandle(hDevice);
    printf("[+] Campaña de fuzzing de IOCTLs finalizada.\n");
    return 0;
}
```

### Instrumentación Guiada y Captura de Crashes con KDNET
Para que el fuzzing sea eficiente y no un mero bombardeo a ciegas:
1. **Instrumentación (Intel PT / DynamoRIO):** Herramientas avanzadas como **WinAFL** (modo `-m` para targeting de módulos) o **kAFL / syzkaller** utilizan trazas de hardware de **Intel PT (Processor Trace)** para guiar la mutación hacia bloques básicos no explorados del driver en kernel.
2. **Detección y Captura de Crashes vía KDNET:**
   - La VM de pruebas se ejecuta con depuración de kernel activa mediante KDNET conectada a una máquina anfitriona con WinDbg.
   - Cuando el fuzzer desencadena una corrupción de memoria en el driver, el sistema no se reinicia a ciegas; WinDbg captura de inmediato el **Bugcheck**:
     * **`0x50` (`PAGE_FAULT_IN_NONPAGED_AREA`):** El driver desreferenció un puntero inválido proveniente de `inBuffer` sin validación previa.
     * **`0xD1` (`DRIVER_IRQL_NOT_LESS_OR_EQUAL`):** El driver intentó acceder a memoria paginada mientras se ejecutaba a `DISPATCH_LEVEL`.
     * **`0x7E` (`SYSTEM_THREAD_EXCEPTION_NOT_HANDLED`):** Excepción no capturada por un bloque `__try / __except` en el driver.
   - En WinDbg, el comando `!analyze -v` desglosa el call stack exacto y señala la instrucción culpable en el desensamblado del `.sys`.


## Fuentes

- Microsoft Learn: [Driver security checklist](https://learn.microsoft.com/en-us/windows-hardware/drivers/driversecurity/driver-security-checklist), [Controlling device access in KMDF](https://learn.microsoft.com/en-us/windows-hardware/drivers/wdf/controlling-device-access-in-kmdf-drivers), [Using I/O control codes](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/defining-i-o-control-codes).
- Microsoft Learn, memoria de usuario: [Methods for Accessing Data Buffers](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/methods-for-accessing-data-buffers), [Using Neither Buffered Nor Direct I/O](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/using-neither-buffered-nor-direct-i-o), [Errors in Referencing User-Space Addresses](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/errors-in-referencing-user-space-addresses), [ProbeForRead](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-probeforread), [Handling Exceptions](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/handling-exceptions), [Accessing Data Buffers in WDF Drivers](https://learn.microsoft.com/en-us/windows-hardware/drivers/wdf/accessing-data-buffers-in-wdf-drivers).
- Microsoft Learn, colas y cancelación: [Request Ownership](https://learn.microsoft.com/en-us/windows-hardware/drivers/wdf/request-ownership), [Configuring Dispatch Mode for an I/O Queue](https://learn.microsoft.com/en-us/windows-hardware/drivers/wdf/configuring-dispatch-mode-for-an-i-o-queue), [Canceling I/O Requests](https://learn.microsoft.com/en-us/windows-hardware/drivers/wdf/canceling-i-o-requests), [Synchronizing Cancel and Completion Code](https://learn.microsoft.com/en-us/windows-hardware/drivers/wdf/synchronizing-cancel-and-completion-code).
- Microsoft Learn, PnP y energía: [Supporting PnP and Power Management in Function Drivers](https://learn.microsoft.com/en-us/windows-hardware/drivers/wdf/supporting-pnp-and-power-management-in-function-drivers), [Power Management for I/O Queues](https://learn.microsoft.com/en-us/windows-hardware/drivers/wdf/power-management-for-i-o-queues).

:::{nota} Etiquetas
**Núcleo conceptual:** superficie/mitigaciones de user mode. **Conocimiento externo:** seguridad de drivers, métodos de buffer, sondeo de memoria de usuario, propiedad y cancelación de solicitudes WDF, PnP/energía (recuadro). **Ejemplo ilustrativo:** checklist, fragmento `METHOD_NEITHER` y flujo de cancelación hipotéticos. **Laboratorio verificado:** no; revisión de código fuente.
:::
