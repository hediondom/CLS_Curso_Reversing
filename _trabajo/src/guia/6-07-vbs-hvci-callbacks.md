---
title: "6.7 · Seguridad Profunda en Kernel x64: VBS/HVCI (VTL1), Callbacks (ETWti) y Condiciones de Carrera en MDLs"
description: "Arquitectura interna de VBS y Secure Kernel (VTL0/VTL1), kCFG, auditoría de vectores de telemetría de kernel en WinDbg y análisis de condiciones de carrera Double Fetch en MDLs."
etapa: "Etapa 6 · Kernel y drivers en Windows (rama optativa)"
---

# Seguridad Profunda en Kernel x64: VBS/HVCI (VTL1), Callbacks (ETWti) y Condiciones de Carrera en MDLs

:::{nota} Propósito
Esta lección profundiza la arquitectura de seguridad del Kernel en Windows 11 contemporáneo, eliminando la frontera de lo que antes se consideraba "fuera de alcance". Aquí se estudian los mecanismos internos que rigen la protección por hipervisor (**VBS / HVCI**), las estructuras exactas en memoria que sustentan los vectores de notificación y telemetría de kernel (**PspCreateProcessNotifyRoutine**, **ObRegisterCallbacks**, **ETWti**), y el análisis forense de fallos por **Double Fetch** y solicitudes asíncronas en controladores **KMDF**.
:::

---

## 1. Arquitectura Interna de VBS y Secure Kernel (VTL0 vs. VTL1)

Desde Windows 10 versión 1709 y por defecto en Windows 11, el modelo de seguridad del sistema operativo se basa en **Virtualization-Based Security (VBS)**. El hipervisor de Windows (Hyper-V) divide el hardware en dos mundos o **Virtual Trust Levels (VTL)**:

```text
+-------------------------------------------------------------------------------+
|                             HIPERVISOR (HYPER-V)                              |
+-------------------------------------------------------+-----------------------+
|                 VTL 0 (Mundo Normal)                  | VTL 1 (Mundo Seguro)  |
|                                                       |                       |
|  [ Modo Usuario ]         [ Modo Kernel ]             |   [ Isolated User ]   |
|  Procesos normales        ntoskrnl.exe                |   lsaiso.exe (CredGrd)|
|  (explorer.exe, etc.)     Drivers de terceros         |                       |
|                                                       |   [ Secure Kernel ]   |
|                                                       |   securekernel.exe    |
|                                                       |   skci.dll (Policy)   |
+-------------------------------------------------------+-----------------------+
|  SLAT / EPT (Tablas de Páginas de Segundo Nivel gobernadas solo por VTL1)    |
+-------------------------------------------------------------------------------+
```

### Transiciones de Privilegio: `VtlCall` y `VtlReturn`
- **`VTL 0`:** Contiene el kernel clásico (`ntoskrnl.exe`), drivers de terceros y aplicaciones de usuario.
- **`VTL 1`:** Contiene el **Secure Kernel** (`securekernel.exe`) y bibliotecas de integridad aisladas como `skci.dll`.
- Las comunicaciones entre mundos no ocurren mediante interrupciones de software clásicas, sino a través de la instrucción de hipervisor `vmcall` (en Intel) o `vmmcall` (en AMD), encapsulada en la función `VtlCall`. Cuando VTL 1 concluye la operación, devuelve el control a VTL 0 mediante `VtlReturn`.

### Integridad de Código por Hipervisor (HVCI) y $W \oplus X$
Bajo **HVCI (Hypervisor-Protected Code Integrity)**, las decisiones sobre qué páginas de memoria pueden ejecutarse en modo kernel se delegan a VTL 1. El hipervisor configura las tablas de páginas de segundo nivel (**SLAT / EPT**) de modo que ninguna página en VTL 0 pueda ser simultáneamente escribible y ejecutable ($W \oplus X$). Si un driver intenta asignar memoria en el pool ejecutable (`NonPagedPoolExecute`) o desproteger el bit de escritura de una página de código en `CR0`, el hipervisor intercepta el fallo de página anidado (*EPT Violation*) e interrumpe inmediatamente la ejecución antes de que el código no firmado pueda ejecutarse.

### kCFG (Kernel Control Flow Guard) Respaldado por VTL 1
En modo kernel, **kCFG** verifica cada llamada indirecta (`call rax`) comprobando si la dirección de destino está registrada en el bitmap de funciones válidas del kernel (`nt!guard_dispatch_icall`). Bajo VBS, el mapa de bits de CFG se almacena en memoria de solo lectura para VTL 0 y solo puede ser actualizado por el Secure Kernel en VTL 1.

---

## 2. Auditoría en Memoria de los Vectores de Telemetría de Kernel

Tanto para la ingeniería inversa de sensores EDR como para la investigación pericial de drivers comprometidos, el analista debe ser capaz de localizar e inspeccionar en **WinDbg** los arreglos de callbacks no exportados en memoria viva.

### A. Notificaciones de Creación de Procesos (`PspCreateProcessNotifyRoutine`)
Windows mantiene una tabla interna de 64 punteros de tipo `EX_FAST_REF` que registran los callbacks suscritos con `PsSetCreateProcessNotifyRoutineEx`:
- En x64, los 4 bits inferiores de cada entrada corresponden al conteo de referencias concurrentes.
- Para obtener la dirección del bloque de datos se aplica una máscara de bits: `Puntero & ~0x0F`.
- En el bloque resultante (`_EX_CALLBACK_ROUTINE_BLOCK`), el offset **`+0x08`** contiene el puntero a la función del driver.

**Comando WinDbg para auditar todos los slots:**
```text
r $t0 = nt!PspCreateProcessNotifyRoutine
.for (r $t1 = 0; @$t1 < 0x40; r $t1 = @$t1 + 1) {
    r $t2 = poi(@$t0 + @$t1 * 8) & 0xfffffffffffffff0
    .if (@$t2 != 0) {
        r $t3 = poi(@$t2 + 8)
        .printf "[Slot %02d] Callback en %p : ", @$t1, @$t3; ln @$t3
    }
}
```

### B. Callbacks de Objetos de Proceso (`ObRegisterCallbacks`)
Los drivers de seguridad registran rutinas `PreOperation` y `PostOperation` sobre objetos `PsProcessType` para despojar permisos peligrosos (como `PROCESS_VM_WRITE` o `PROCESS_VM_OPERATION`):
- En Windows 10 y 11 x64, la cabeza de lista `CallbackListHead` se ubica en el offset **`+0xC8`** de la estructura `_OBJECT_TYPE` apuntada por `*PsProcessType`.
- Cada elemento de la lista apunta a una estructura `OB_CALLBACK_CONTEXT_BLOCK` donde **`+0x28`** es el puntero `PreOperation` y **`+0x30`** es `PostOperation`.

### C. Proveedor de Telemetría de Kernel `ETWti` (*Microsoft-Windows-Threat-Intelligence*)
El subsistema ETWti es el canal que alimenta a los EDRs modernos con eventos de inyección de código, lectura de memoria y mapeo de hilos:
- Su handle de registro global está en `nt!EtwThreatIntProvRegHandle`.
- Apunta a una estructura `_ETW_REG_ENTRY`. En el offset **`+0x10`** reside el puntero a `_ETW_GUID_ENTRY`.
- Dentro de `_ETW_GUID_ENTRY`, el campo `ProviderEnableInfo` define si el proveedor está activo (`EnableMask != 0`) y a qué nivel de detalle registra eventos de kernel.

El script completo para auditar estos tres vectores de una sola vez se encuentra en `plantillas_codigo/auditar_callbacks.wdbg`.

---

## 3. Mecánicas BYOVD (Bring Your Own Vulnerable Driver) y Detección Defensiva

Una de las tácticas más críticas en el análisis de amenazas de bajo nivel es el vector **BYOVD** (*Bring Your Own Vulnerable Driver*).

### Por qué ocurre BYOVD
En sistemas Windows modernos de 64 bits con Secure Boot activo, el kernel exige que todo driver esté firmado digitalmente (*Driver Signature Enforcement - DSE*). Para eludir esta restricción sin explotar una vulnerabilidad en `ntoskrnl.exe`, los adversarios cargan legítimamente un **driver antiguo o comercial firmado por un fabricante legítimo** (fabricantes de placas madre, utilidades de diagnóstico, software antivirus antiguo o herramientas de overclocking) que contiene una vulnerabilidad de diseño:
- Primitivas de lectura y escritura física o virtual arbitraria (`MmMapIoSpace`, `ZwMapViewOfSection`).
- Despacho de IOCTLs que exponen instrucciones privilegiadas como `wrmsr` o lectura/escritura en puertos de E/S (`__inbyte`, `__outbyte`).
- Copia de memoria sin validación de buffers mediante `RtlCopyMemory`.

Una vez cargado el driver firmado con éxito bajo la política de DSE, el proceso en espacio de usuario envía IOCTLs hacia el driver vulnerable para alterar estructuras de seguridad del kernel (como el token del proceso en `EPROCESS->Token` para elevar privilegios a SYSTEM, desarmar los ganchos de EDR en `PspCreateProcessNotifyRoutine` o limpiar los registros de telemetría de `ETWti`).

### Detección Defensiva: La Tabla de Caché de Drivers `nt!PiDDBCacheTable`
Para mitigar la carga de drivers vulnerables conocidos, Microsoft implementa dos líneas de defensa:
1. **Microsoft Vulnerable Driver Blocklist (WDAC):** Una lista denegada de hashes SHA-256 de archivos y certificados de firma revocados que el kernel comprueba al invocar `NtLoadDriver`.
2. **Estructura Interna `nt!PiDDBCacheTable`:** El cargador de drivers de Windows mantiene una tabla hash interna en memoria protegida por el recurso `nt!PiDDBLock`. Cada vez que un driver `.sys` se carga en el sistema, Windows calcula un hash de su nombre y timestamp y lo inserta en `PiDDBCacheTable`.
   - **Técnica de evasión conocida:** Protectores o utilidades de carga ilícita intentan localizar `nt!PiDDBCacheTable` y eliminar su entrada (`RtlDeleteElementGenericTableAvl`) para borrar la evidencia de carga.
   - **Auditoría Defensiva en WinDbg:** Un analista de respuesta a incidentes (DFIR) o auditor de kernel puede examinar `PiDDBCacheTable` para verificar qué drivers fueron inicializados en el sistema, contrastando sus timestamps contra la lista oficial de drivers vulnerables conocidos:

```text
$$ Localizar la tabla de caché de drivers y su lock en WinDbg KDNET
x nt!PiDDBCacheTable
x nt!PiDDBLock

$$ Inspeccionar los primeros elementos de la tabla genérica AVL
dt nt!_RTL_AVL_TABLE poi(nt!PiDDBCacheTable)
```

---

## 4. Condiciones de Carrera y Reversing de MDLs en Drivers KMDF

En la Lección 6.4 se abordó la estructura de despacho de IOCTLs en KMDF. Sin embargo, en drivers reales el análisis de seguridad debe verificar el manejo de **MDLs (Memory Descriptor Lists)** y la sincronización asíncrona.

### El Peligro del *Double Fetch* en `METHOD_IN_DIRECT` / `METHOD_OUT_DIRECT`
Cuando un driver utiliza E/S directa (`METHOD_IN_DIRECT` o `METHOD_OUT_DIRECT`):
1. El I/O Manager bloquea las páginas físicas del buffer de usuario en memoria mediante una estructura MDL (`Irp->MdlAddress`).
2. El driver mapea esas páginas en el espacio virtual del sistema llamando a `MmGetSystemAddressForMdlSafe(Mdl, NormalPagePriority)`.
3. **La trampa de seguridad:** La memoria virtual devuelta por `MmGetSystemAddressForMdlSafe` comparte exactamente los mismos marcos de página física (PFNs) que el buffer en modo usuario. Si el driver lee un parámetro de tamaño o un puntero interno desde ese buffer dos veces (por ejemplo, una vez para validar y otra para copiar), un hilo atacante en espacio de usuario puede modificar el valor concurrentemente en la memoria compartida entre ambas lecturas (**Double Fetch**), desbordando buffers internos del kernel.

### Reenvío Asíncrono a I/O Targets en KMDF
En drivers KMDF desensamblados sin símbolos, las llamadas indirectas a través de la tabla `WdfFunctions` que gestionan solicitudes asíncronas se identifican por sus índices fijos:
- **`WdfRequestSend` (Índice 285 / Offset `+0x8E8`):** Reenvía un paquete de E/S a un dispositivo inferior o destino de E/S.
- **`WdfRequestSetCompletionRoutine` (Índice 290 / Offset `+0x910`):** Registra la rutina de finalización que se ejecutará cuando el dispositivo inferior complete la operación. En el desensamblado x64:

```nasm
; Registro de CompletionRoutine en KMDF (offset +0x910)
mov     rax, [rbx]                  ; RBX = Puntero a WdfFunctions
mov     r8, offset MiCompletionRoutine ; R8 = Puntero al callback
mov     rdx, r14                    ; RDX = WDFREQUEST
mov     rcx, [rbx + 0x910]          ; Índice 290 = WdfRequestSetCompletionRoutine
call    rcx                         ; Invocación indirecta
```

---

## 4. Laboratorio Verificado

1. Inspeccioná la plantilla `plantillas_codigo/minifilter_obcallback_min.c`. Observá cómo interactúan las estructuras de `FLT_REGISTRATION` y `OB_CALLBACK_REGISTRATION`.
2. En una sesión de depuración con WinDbg KDNET en tu VM de kernel, ejecutá:
   ```text
   $$><plantillas_codigo\auditar_callbacks.wdbg
   ```
3. Verificá que la lista de callbacks enumera los drivers de tu entorno y localiza el módulo exacto que atiende la creación de procesos en tu sistema.
