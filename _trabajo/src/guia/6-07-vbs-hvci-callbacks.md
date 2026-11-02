---
title: "6.7 · Seguridad Profunda en Kernel x64: VBS/HVCI (VTL1), Callbacks (ETWti, Registro, InstrumentationCallback) y Mecánicas BYOVD"
description: "Arquitectura interna de VBS y Secure Kernel (VTL0/VTL1), Credential Guard y trustlets IUM, validación NtCreateSection->VtlCall, auditoría de telemetría de kernel en WinDbg, BYOVD con PiDDBCacheTable y condiciones de carrera Double Fetch en MDLs."
etapa: "Etapa 6 · Kernel y drivers en Windows (rama optativa)"
---

# Seguridad Profunda en Kernel x64: VBS/HVCI (VTL1), Callbacks y Mecánicas BYOVD

:::{nota} Propósito
Esta lección profundiza la arquitectura de seguridad del Kernel en Windows 11 contemporáneo, eliminando la frontera de lo que antes se consideraba "fuera de alcance". Aquí se estudian los mecanismos internos que rigen la protección por hipervisor (**VBS / HVCI**), el aislamiento de **Credential Guard con trustlets IUM**, el flujo exacto de validación de imágenes (`NtCreateSection` $\to$ `VtlCall`), las estructuras en memoria que sustentan los vectores de notificación y telemetría de kernel (**PspCreateProcessNotifyRoutine**, **ObRegisterCallbacks**, **ETWti**, **CmCallbackListHead**, **InstrumentationCallback**), el vector **BYOVD** con inspección de **PiDDBCacheTable**, y el análisis forense de fallos por **Double Fetch** en controladores **KMDF**.
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

### Credential Guard, LSAISO y Trustlets en Modo de Usuario Aislado (IUM)
En sistemas convencionales sin VBS, el proceso `lsass.exe` almacenaba hashes NTLM, credenciales en claro y tickets Kerberos directamente en su propio espacio de direcciones en modo usuario (VTL 0), haciéndolos vulnerables a lecturas de memoria con herramientas como Mimikatz si el atacante obtenía privilegios de `SeDebugPrivilege` o ejecutaba un driver en modo kernel.

Bajo **Credential Guard**:
1. El kernel crea un proceso especial en **Modo de Usuario Aislado (IUM - Isolated User Mode)** que reside dentro de **VTL 1**: **`lsaiso.exe`** (*LSA Isolated*).
2. El proceso `lsass.exe` en VTL 0 pasa a funcionar como un mero intermediario de RPC/ALPC: no contiene claves criptográficas ni hashes en claro.
3. Cada vez que se requiere autenticar un usuario o firmar un ticket Kerberos, `lsass.exe` envía una solicitud a través de llamadas ALPC canalizadas mediante una transición `VtlCall` hacia `lsaiso.exe` en VTL 1.
4. El Secure Kernel en VTL 1 procesa la operación criptográfica usando claves protegidas por hardware (TPM) y devuelve únicamente el resultado de la autenticación a VTL 0.
5. Las tablas de páginas de VTL 1 no están mapeadas en el espacio de direcciones de VTL 0: ni siquiera un driver en modo kernel ejecutándose con máximos privilegios en VTL 0 puede leer la memoria de `lsaiso.exe`.

### Flujo de Validación de Imágenes: `NtCreateSection` $\to$ `VtlCall` $\to$ `skci.dll`
Cuando se carga un binario ejecutable o controlador en el sistema:
1. El llamador invoca `NtCreateSection` con la bandera `SEC_IMAGE`.
2. El gestor de memoria (`nt!MiCreateSection`) analiza las cabeceras PE y transfiere la validación de firma a la biblioteca de integridad de código del kernel (`ci.dll!CiValidateImageHeader`).
3. Si la política de HVCI está activa, `ci.dll` no toma la decisión de ejecución de manera local en VTL 0: emite una transición de hipervisor **`VtlCall`** hacia **`skci.dll`** (*Secure Kernel Code Integrity*) en VTL 1.
4. `skci.dll` valida los certificados digitales, la cadena de confianza y las reglas WDAC (*Windows Defender Application Control*), computando los hashes criptográficos de cada página física.
5. Si la validación es exitosa, el Secure Kernel programa las tablas de páginas SLAT/EPT del hipervisor marcando las páginas físicas correspondientes como ejecutables de solo lectura ($R \oplus X$). Si la validación fracasa, VTL 1 retorna un estado de error (`STATUS_IMAGE_CERT_REVOKED` o `STATUS_INVALID_IMAGE_HASH`) y `NtCreateSection` es abortada inmediatamente.

#### Código C: Gatillo de Mapeo con Validación Criptográfica en Kernel
```c
// Invocación nativa para mapear una imagen PE sujeta a verificación de HVCI
HANDLE hFile = NULL, hSection = NULL;
OBJECT_ATTRIBUTES objAttr;
IO_STATUS_BLOCK ioStatus;
UNICODE_STRING uPath;

RtlInitUnicodeString(&uPath, L"\\??\\C:\\drivers\\vulnerable_or_untrusted.sys");
InitializeObjectAttributes(&objAttr, &uPath, OBJ_CASE_INSENSITIVE, NULL, NULL);

NtOpenFile(&hFile, FILE_EXECUTE | SYNCHRONIZE, &objAttr, &ioStatus, 
           FILE_SHARE_READ, FILE_NON_DIRECTORY_FILE | FILE_SYNCHRONOUS_IO_NONALERT);

// Al invocar NtCreateSection con SEC_IMAGE (0x01000000), ntoskrnl transfiere el control a CI / VTL1
NTSTATUS status = NtCreateSection(
    &hSection,
    SECTION_ALL_ACCESS,
    NULL,
    NULL,
    PAGE_EXECUTE,
    SEC_IMAGE,   // 0x01000000: Gatillo de verificación de firma y validación SLAT/EPT
    hFile
);
// Si HVCI rechaza la firma en VTL1, status retornará STATUS_INVALID_IMAGE_HASH (0xC0000428)
```

#### Receta WinDbg para Rastrear el Pipeline `NtCreateSection` $\to$ `VtlCall`
```text
$$ 1. Breakpoint en la entrada de creación de sección y análisis PE
bp nt!NtCreateSection "r @rcx; gc"
bp nt!MiCreateSection

$$ 2. Breakpoint en la biblioteca de integridad de código (VTL 0)
bp ci!CiValidateImageHeader "du poi(@rcx+0x30); gc"
bp ci!CiValidateImagePages

$$ 3. Breakpoint en la llamada de transición de hipervisor (VtlCall hacia Secure Kernel)
$$ (Nota técnica: En ci.dll, la rutina nativa que ensambla la transición VtlCall hacia VTL1 se denomina formalmente ci!IvtCallHypervisor)
bp ci!IvtCallHypervisor
$$ Al alcanzar ci!IvtCallHypervisor, examinar los argumentos de la llamada:
$$ RCX = Código de comando VTL1 (ej. 0x17 = SECURE_IMAGE_VALIDATE_PAGES)
$$ RDX = Puntero al bloque de contexto con las PFNs físicas a verificar
r rcx, rdx

$$ 4. Breakpoint en el Secure Kernel (VTL 1) (si el depurador está conectado a VTL1)
bp skci!SkciValidateImagePages
```

### kCFG (Kernel Control Flow Guard) Respaldado por VTL 1
En modo kernel, **kCFG** verifica cada llamada indirecta (`call rax`) comprobando si la dirección de destino está registrada en el bitmap de funciones válidas del kernel (`nt!guard_dispatch_icall`). Bajo VBS, el mapa de bits de CFG se almacena en memoria de solo lectura para VTL 0 y solo puede ser actualizado por el Secure Kernel en VTL 1.

---

## 2. Auditoría en Memoria de los Vectores de Telemetría y Notificación de Kernel

El reverser o analista defensivo debe dominar la inspección en **WinDbg** de los arreglos no exportados de notificación, registro y telemetría en memoria viva.

### A. Notificaciones de Creación de Procesos (`PspCreateProcessNotifyRoutine`)
Windows mantiene una tabla interna de 64 punteros de tipo `EX_FAST_REF` que registran los callbacks suscritos con `PsSetCreateProcessNotifyRoutineEx`:
- En x64, los 4 bits inferiores de cada entrada corresponden al conteo de referencias concurrentes.
- Para obtener la dirección del bloque de datos se aplica una máscara de bits: `Puntero & ~0x0F`.
- En el bloque resultante (`_EX_CALLBACK_ROUTINE_BLOCK`), el offset **`+0x08`** contiene el puntero a la función del driver.

```text
$$ Script WinDbg para auditar todos los slots de PspCreateProcessNotifyRoutine
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

### C. Callbacks de Registro: `nt!CmCallbackListHead` y `CmRegisterCallbackEx`
Los drivers de auditoría e integridad registran filtros de transacciones sobre el Registro mediante `CmRegisterCallbackEx`:
- Los callbacks activos se encadenan en la lista doblemente enlazada no exportada **`nt!CmCallbackListHead`**.
- Cada nodo corresponde a una estructura `_CM_CALLBACK_CONTEXT_BLOCK` donde el offset **`+0x28`** almacena el puntero `Function` (la rutina del driver) y **`+0x30`** contiene el puntero `Context`.

```text
$$ Recorrer en WinDbg todos los callbacks de registro registrados
!list -t nt!_CM_CALLBACK_CONTEXT_BLOCK.List -x "dps @$extret+0x28 L1" nt!CmCallbackListHead
```

### D. Sensor en Proceso: `KPROCESS->InstrumentationCallback`
Para evitar el monitoreo invasivo mediante inline hooking en modo usuario, Windows expone un mecanismo nativo de instrumentación en el despachador de syscalls:
- En la estructura `_KPROCESS` (`nt!_KPROCESS`), el campo **`InstrumentationCallback`** (offset **`+0x3D8`** en Windows 10 x64, **`+0x3E8`** en Windows 11 x64) almacena un puntero a una función en espacio de usuario.
- Se configura desde user mode mediante `NtSetInformationProcess` pasando la clase no documentada `ProcessInstrumentationCallback` (`0x28`).
- **Mecánica de intercepción:** Cuando este puntero está activo, cada vez que una llamada al sistema (`syscall`) o interrupción retorna desde el kernel al modo usuario, la CPU no regresa inmediatamente a la instrucción siguiente (`RIP`), sino que desvía la ejecución a la dirección configurada en `InstrumentationCallback`. Sensores defensivos y EDRs lo utilizan para inspeccionar el estado de los registros y el stack post-syscall.

#### Implementación en C: Registro de `InstrumentationCallback`
```c
#include <windows.h>
#include <stdio.h>

#define ProcessInstrumentationCallback 0x28

typedef struct _PROCESS_INSTRUMENTATION_CALLBACK_INFORMATION {
    ULONG Version;      // 0 en x64
    ULONG Reserved;     // 0
    PVOID Callback;     // Puntero a la rutina en espacio de usuario
} PROCESS_INSTRUMENTATION_CALLBACK_INFORMATION;

typedef NTSTATUS (NTAPI *pfnNtSetInformationProcess)(
    HANDLE ProcessHandle,
    ULONG ProcessInformationClass,
    PVOID ProcessInformation,
    ULONG ProcessInformationLength
);

// Stub en ensamblador que recibe el control tras cada syscall
extern void InstrumentationCallbackEntry(void);

void InstalarInstrumentationCallback(void) {
    pfnNtSetInformationProcess NtSetInformationProcess = 
        (pfnNtSetInformationProcess)GetProcAddress(GetModuleHandleA("ntdll.dll"), "NtSetInformationProcess");
    if (!NtSetInformationProcess) return;

    PROCESS_INSTRUMENTATION_CALLBACK_INFORMATION info;
    info.Version = 0;
    info.Reserved = 0;
    info.Callback = (PVOID)(ULONG_PTR)InstrumentationCallbackEntry;

    NTSTATUS status = NtSetInformationProcess(
        GetCurrentProcess(),
        ProcessInstrumentationCallback,
        &info,
        sizeof(info)
    );
    if (status == 0) {
        printf("[+] InstrumentationCallback registrado correctamente.\n");
    }
}
```

#### Stub en Ensamblador x64 (`instrumentation_entry.asm`)
Al regresar de la syscall, el kernel coloca la dirección de retorno original (`RIP` en modo usuario) en el registro **`R10`**, y las banderas en **`R11`**:
```asm
.code
PUBLIC InstrumentationCallbackEntry
EXTRN AuditarRetornoSyscall:PROC

InstrumentationCallbackEntry PROC
    ; Preservar el contexto volátil completo del hilo
    pushfq
    push    rax
    push    rcx
    push    rdx
    push    r8
    push    r9
    push    r10
    push    r11
    
    ; Invocar función C pasando R10 (RIP original de retorno) como 1er argumento (RCX)
    sub     rsp, 20h
    mov     rcx, r10
    call    AuditarRetornoSyscall
    add     rsp, 20h
    
    ; Restaurar contexto
    pop     r11
    pop     r10
    pop     r9
    pop     r8
    pop     rdx
    pop     rcx
    pop     rax
    popfq
    
    ; Saltar a la dirección de retorno original que el kernel dejó en R10
    jmp     r10
InstrumentationCallbackEntry ENDP
END
```

#### Script WinDbg: Auditoría de `InstrumentationCallback` en Todos los Procesos
Un analista forense o investigador de evasión puede inspeccionar qué procesos del sistema tienen activo un sensor `InstrumentationCallback`:
```text
$$ Script WinDbg: Recorrer todos los procesos y detectar callbacks activos
!for_each_process "r @$t0 = @#Process; .if (poi(@$t0+@@(#FIELD_OFFSET(nt!_KPROCESS, InstrumentationCallback))) != 0) { .printf \"PID %p (%s) -> InstrumentationCallback: %p\n\", poi(@$t0+@@(#FIELD_OFFSET(nt!_EPROCESS, UniqueProcessId))), poi(@$t0+@@(#FIELD_OFFSET(nt!_EPROCESS, ImageFileName))), poi(@$t0+@@(#FIELD_OFFSET(nt!_KPROCESS, InstrumentationCallback))) }"
```

### E. Proveedor de Telemetría de Kernel `ETWti` (*Microsoft-Windows-Threat-Intelligence*)
El subsistema ETWti alimenta a los EDRs con telemetría de bajo nivel:
- Su handle de registro global reside en `nt!EtwThreatIntProvRegHandle`.
- Apunta a una estructura `_ETW_REG_ENTRY`. En el offset **`+0x10`** reside el puntero a `_ETW_GUID_ENTRY`.
- Dentro de `_ETW_GUID_ENTRY`, el campo `ProviderEnableInfo` define si el proveedor está activo (`EnableMask != 0`) y a qué nivel de detalle registra eventos de kernel.

---

## 3. Mecánicas BYOVD (Bring Your Own Vulnerable Driver) y Detección Defensiva

El vector **BYOVD** (*Bring Your Own Vulnerable Driver*) es la técnica predilecta para eludir DSE (*Driver Signature Enforcement*) sin necesidad de vulnerar `ntoskrnl.exe`.

### Mecánica de Abuso de Drivers Legítimos Firmados
1. El atacante selecciona un driver legítimo antiguo firmado con un certificado comercial válido (utilidades de placa madre, herramientas de overclocking o versiones antiguas de antivirus).
2. El driver se carga en el sistema mediante la API legítima `NtLoadDriver` o a través del Service Control Manager (`CreateServiceW` / `StartServiceW`). Dado que la firma digital es válida y no ha sido explícitamente bloqueada por la lista de revocación de Windows (WDAC Blocklist), DSE permite su carga.
3. El proceso atacante abre un handle hacia el objeto dispositivo del driver y despacha códigos IOCTL vulnerables que exponen primitivas de lectura/escritura arbitraria de memoria física (`MmMapIoSpace`), manipulación de registros de control (desactivación del bit SMEP en `CR4`) o copia no validada de memoria (`RtlCopyMemory`).
4. Con estas primitivas, el atacante modifica en memoria viva las estructuras del kernel (desactiva callbacks de EDR en `PspCreateProcessNotifyRoutine`, neutraliza `ETWti` o altera el token de seguridad en `_EPROCESS`).

### Detección Defensiva: La Tabla de Caché `nt!PiDDBCacheTable`
Para llevar un registro forense de todos los controladores cargados, el kernel NT mantiene una tabla hash en memoria protegida por el recurso `nt!PiDDBLock`: **`nt!PiDDBCacheTable`**.

#### Estructura Interna de `_RTL_AVL_TABLE` (x64):
```text
dt nt!_RTL_AVL_TABLE
   +0x00 BalancedRoot          : _RTL_BALANCED_LINKS (Árbol balanceado AVL)
   +0x20 OrderedPointer        : Ptr64 Void
   +0x28 WhichOrderedElement   : Uint4
   +0x30 NumberGenericTableElements : Uint4 (Cantidad total de drivers cacheados)
   +0x38 DepthOfTree           : Uint4
   +0x40 RestartKey            : Ptr64 _RTL_BALANCED_LINKS
   +0x48 DeleteCount           : Uint4
   +0x50 CompareRoutine        : Ptr64
   +0x58 AllocateRoutine       : Ptr64
   +0x60 FreeRoutine           : Ptr64
   +0x68 TableContext          : Ptr64 Void
```

#### Estructura de Entrada `_PiDDBCacheEntry`:
Cada entrada dentro del árbol AVL contiene los metadatos de un controlador:
- **`+0x00` `List` (`_LIST_ENTRY`):** Enlace doble en la lista de entradas.
- **`+0x10` `DriverName` (`_UNICODE_STRING`):** Nombre del archivo del driver (ej. `RTCore64.sys`, `gdrv.sys`).
- **`+0x20` `TimeDateStamp` (`ULONG`):** Marca de tiempo de compilación del encabezado PE del driver.
- **`+0x24` `LoadStatus` (`NTSTATUS`):** Estado de carga del controlador (`STATUS_SUCCESS = 0x00000000`).

#### Técnicas de Evasión y Auditoría Forense:
- **Técnica de evasión:** Herramientas de carga clandestina intentan localizar la tabla `nt!PiDDBCacheTable`, adquirir `nt!PiDDBLock` mediante `ExAcquireResourceExclusiveLite` y desvincular el nodo del driver vulnerable llamando a **`RtlDeleteElementGenericTableAvl`** para no dejar rastro en la memoria del kernel.
- **Auditoría Forense en WinDbg:** Un analista de incidentes puede volcar la tabla para comprobar si un driver vulnerable fue cargado, incluso si el archivo ya fue eliminado del disco:
```text
$$ Localizar la tabla de caché de drivers y su lock en WinDbg
x nt!PiDDBCacheTable
x nt!PiDDBLock

$$ Inspeccionar las entradas del árbol AVL
dt nt!_RTL_AVL_TABLE poi(nt!PiDDBCacheTable)
dt nt!_PiDDBCacheEntry poi(poi(nt!PiDDBCacheTable) + 0x20)
```

---

## 4. Condiciones de Carrera y Reversing de MDLs en Drivers KMDF

En drivers reales el análisis de seguridad debe verificar el manejo de **MDLs (Memory Descriptor Lists)** y la sincronización asíncrona.

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

---

## 6.7.b — Detección de DKOM mediante Cross-View (VTL0 vs. VTL1 y PspCidTable)

Los atacantes avanzados y herramientas de evasión basadas en **BYOVD** (*Bring Your Own Vulnerable Driver*) intentan ocultar procesos maliciosos manipulando directamente las estructuras de datos del kernel (**DKOM - Direct Kernel Object Manipulation**). La técnica clásica consiste en desvincular el proceso de la lista doblemente enlazada `nt!_EPROCESS->ActiveProcessLinks`:

```text
[Proceso Legítimo A] <---> [Proceso Oculto X] <---> [Proceso Legítimo B]
                                   │
             (Atacante reasigna Flink y Blink con BYOVD)
                                   ▼
[Proceso Legítimo A] <-----------------------------> [Proceso Legítimo B]
```

Al desvincularse, el proceso `X` desaparece completamente de las herramientas de administración convencionales (`tasklist.exe`, `Process Explorer`, APIs `CreateToolhelp32Snapshot` y `EnumProcesses`), ya que todas ellas recorren la lista `ActiveProcessLinks` en VTL 0. Sin embargo, el hilo del proceso sigue ejecutándose porque el planificador de la CPU (*scheduler*) despacha hilos a través de `_ETHREAD` y de la tabla de identificadores globales.

### La Técnica Defensiva de Inspección Cruzada (*Cross-View Detection*)
La detección rigurosa de DKOM se basa en contrastar la vista estándar de VTL 0 contra fuentes inmutables o no enlazadas del sistema:

1. **Cruce contra `nt!PspCidTable`:**
   En Windows, cada identificador de proceso (PID) y de hilo (TID) se registra obligatoriamente en una tabla de handles interna no exportada del kernel: **`nt!PspCidTable`** (de tipo `_HANDLE_TABLE`).
   - `ActiveProcessLinks` es una lista meramente informativa para enumeración.
   - `PspCidTable` es la estructura que el kernel consulta cada vez que despacha una llamada o valida un handle de proceso. Si un atacante desvincula un proceso de `PspCidTable`, el sistema operativo entra inmediatamente en Bugcheck por inconsistencia de scheduler.
   - **Regla Cross-View:** Si un PID existe en `PspCidTable` pero no aparece al recorrer `ActiveProcessLinks`, **el proceso ha sido ocultado mediante DKOM**.

2. **Cruce VTL0 vs. VTL1 (Secure Kernel):**
   Bajo Virtualization-Based Security (VBS), el **Secure Kernel** (`securekernel.exe`) en VTL 1 mantiene su propio inventario de páginas físicas y contextos de ejecución respaldado por las tablas SLAT/EPT del hipervisor. Ningún driver en VTL 0 (incluso con privilegios de kernel absolutos) puede alterar la memoria de VTL 1. Los sensores defensivos de última generación consultan al hipervisor para comparar los contextos de ejecución activos contra la lista visible en VTL 0.

3. **Telemetría de Kernel `ETWti`:**
   El proveedor `Microsoft-Windows-Threat-Intelligence` emite eventos inmutables de creación de procesos (`PROCESS_CREATE`) generados en la ruta nativa `nt!PspInsertProcess`. Aunque el atacante desvincule el proceso a posteriori en memoria, la traza de auditoría de ETWti ya registró la creación con su PID legítimo.

### Script Conceptual de WinDbg para Detección Cross-View
El siguiente script en WinDbg compara los procesos enumerados por la lista circular contra los registros de la tabla de identificadores `PspCidTable`:

```text
$$ =========================================================================
$$ Detección Cross-View de Procesos Ocultos por DKOM en WinDbg
$$ =========================================================================

$$ 1. Recorrer la lista clásica ActiveProcessLinks (Vista VTL 0)
!process 0 0

$$ 2. Inspeccionar la tabla global de PIDs (PspCidTable)
r $t0 = poi(nt!PspCidTable)
.printf "[+] PspCidTable ubicada en %p\n", @$t0

$$ 3. Volcar los objetos de proceso referenciados por sus handles en PspCidTable
!handle 0 3 0 Process

$$ 4. Algoritmo de detección heurística en WinDbg:
$$ Para cada handle válido en PspCidTable, desreferenciar el puntero EPROCESS:
$$ Si EPROCESS->ActiveProcessLinks.Flink == &EPROCESS->ActiveProcessLinks
$$ o si Flink->Blink != EPROCESS, se delata una desvinculación maliciosa (DKOM).
!for_each_process "r @$t1 = @#Process; .if (poi(@$t1 + @@(#FIELD_OFFSET(nt!_EPROCESS, ActiveProcessLinks.Flink))) == (@$t1 + @@(#FIELD_OFFSET(nt!_EPROCESS, ActiveProcessLinks)))) { .printf \"[ALERTA DKOM] Proceso oculto detectado: PID %p (%s) en %p\n\", poi(@$t1 + @@(#FIELD_OFFSET(nt!_EPROCESS, UniqueProcessId))), poi(@$t1 + @@(#FIELD_OFFSET(nt!_EPROCESS, ImageFileName))), @$t1 }"
```


## 5. Laboratorio Verificado

1. Inspeccioná la plantilla `plantillas_codigo/minifilter_obcallback_min.c`. Observá cómo interactúan las estructuras de `FLT_REGISTRATION` y `OB_CALLBACK_REGISTRATION`.
2. En una sesión de depuración con WinDbg KDNET en tu VM de kernel, ejecutá el script de auditoría completa:
   ```text
   $$><plantillas_codigo\auditar_callbacks.wdbg
   ```
3. Verificá que la lista de callbacks enumera los drivers de tu entorno y localiza el módulo exacto que atiende la creación de procesos en tu sistema.
