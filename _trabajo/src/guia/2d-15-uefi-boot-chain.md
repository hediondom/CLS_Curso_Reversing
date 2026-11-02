---
title: "2D.15 · Reversing de Arranque Temprano, UEFI y Cadena de Carga (bootmgfw, winload, LOADER_PARAMETER_BLOCK)"
description: "Formato PE32+ de aplicaciones EFI, layout binario de EFI_SYSTEM_TABLE, cadena de inicialización de arranque (bootmgfw.efi, winload.efi, hvloader.efi), estructura LOADER_PARAMETER_BLOCK y análisis de bootkits en Ghidra/IDA."
etapa: "Etapa 2 · 2D · Windows internals (optativa)"
---

# Reversing de Arranque Temprano, UEFI y Cadena de Carga

:::{nota} Propósito y Alcance
El análisis del sistema operativo no comienza cuando el kernel ya está en ejecución. Para comprender las amenazas más persistentes (Bootkits UEFI, técnicas de desactivación temprana de DSE, y el despliegue del hipervisor VBS antes de `ntoskrnl.exe`), el analista de ingeniería inversa debe dominar el proceso de arranque temprano de Windows en plataformas de 64 bits con firmware **UEFI**. Esta lección disecciona la cadena de cargadores EFI, el layout de estructuras del firmware, el formato de los módulos DXE y la estructura de transición fundamental: el bloque **`LOADER_PARAMETER_BLOCK`**.
:::

---

## 1. El Formato PE32+ de las Aplicaciones EFI

Los archivos ejecutables del cargador de arranque de Windows (como `bootmgfw.efi`, `winload.efi` y `hvloader.efi`) no son formatos binarios propietarios exóticos: son archivos estándar **PE32+ (PE de 64 bits)** con características específicas en sus cabeceras:

1. **`Subsystem` en OptionalHeader:**
   - `IMAGE_SUBSYSTEM_EFI_APPLICATION` (`10` / `0x000A`): Aplicaciones que se ejecutan directamente bajo el entorno UEFI antes de que el sistema operativo tome el control.
   - `IMAGE_SUBSYSTEM_EFI_BOOT_SERVICE_DRIVER` (`11` / `0x000B`): Controladores DXE que extienden los servicios de arranque de la placa madre.
2. **Punto de Entrada EFI:**
   La función de inicio de un ejecutable EFI recibe siempre dos parámetros estandarizados en la convención x64 de Microsoft:
   ```c
   EFI_STATUS EFIAPI EfiMain(
       IN EFI_HANDLE ImageHandle,       // RCX: Handle del binario cargado en memoria
       IN EFI_SYSTEM_TABLE *SystemTable // RDX: Puntero a la tabla global de servicios UEFI
   );
   ```

### Layout Binario de `EFI_SYSTEM_TABLE` en x64
En un ejecutable UEFI desensamblado, toda interacción con memoria, consola y protocolos se realiza a través de la tabla `SystemTable` pasada en `RDX`. En arquitecturas de 64 bits, su disposición en memoria es fija:

| Offset (x64) | Campo | Tipo | Propósito |
| :--- | :--- | :--- | :--- |
| **`+0x00`** | `Hdr` | `EFI_TABLE_HEADER` | Cabecera estándar de 24 bytes (Firma mágica `0x5453595320494249` = `"IBI SYST"`, revisión, tamaño y CRC32). |
| **`+0x18`** | `FirmwareVendor` | `CHAR16*` | Puntero a cadena Unicode UTF-16 con el nombre del fabricante del BIOS/UEFI. |
| **`+0x20`** | `FirmwareRevision` | `UINT32` | Versión interna del firmware. |
| **`+0x24`** | `_Padding` | `UINT32` | Relleno de alineación a 8 bytes en arquitecturas de 64 bits. |
| **`+0x28`** | `ConsoleInHandle` | `EFI_HANDLE` | Handle del dispositivo de entrada estándar (teclado). |
| **`+0x30`** | `ConIn` | `EFI_SIMPLE_TEXT_INPUT_PROTOCOL*` | Puntero al protocolo de lectura de caracteres del teclado. |
| **`+0x38`** | `ConsoleOutHandle` | `EFI_HANDLE` | Handle de la salida de texto (pantalla). |
| **`+0x40`** | `ConOut` | `EFI_SIMPLE_TEXT_OUTPUT_PROTOCOL*` | Puntero al protocolo de impresión de texto en pantalla. |
| **`+0x48`** | `StandardErrorHandle`| `EFI_HANDLE` | Handle del dispositivo de error. |
| **`+0x50`** | `StdErr` | `EFI_SIMPLE_TEXT_OUTPUT_PROTOCOL*` | Puntero a la salida de errores en pantalla. |
| **`+0x58`** | `RuntimeServices` | `EFI_RUNTIME_SERVICES*` | Puntero a la tabla de servicios en tiempo de ejecución (`gRT`), que persisten tras arrancar el SO (variables NVRAM). |
| **`+0x60`** | `BootServices` | `EFI_BOOT_SERVICES*` | Puntero a la tabla de servicios de arranque (`gBS`), activa solo hasta que se invoca `ExitBootServices`. |

---

## 2. La Cadena de Carga de Windows en Sistemas x64 / UEFI

El proceso de arranque moderno desde el encendido de la máquina hasta la primera instrucción del kernel sigue una secuencia estricta de componentes encadenados y firmados bajo **Secure Boot**:

```text
[ Encendido / Reset ]
         │
         ▼
[ Firmware UEFI (SEC -> PEI -> DXE -> BDS) ]
         │ (Carga desde partición ESP FAT32: \EFI\Microsoft\Boot\bootmgfw.efi)
         ▼
[ Windows Boot Manager (bootmgfw.efi) ]
         │ 1. Parsea la base de datos BCD (\EFI\Microsoft\Boot\BCD)
         │ 2. Si BitLocker está activo: desbloquea la clave TPM mediante llamadas EFI
         │ 3. Carga y verifica la firma digital del cargador del SO
         ▼
[ Windows OS Loader (winload.efi) ]
         │ 1. Configura el mapa preliminar de tablas de páginas de 4 niveles (PML4)
         │ 2. Carga la colmena de registro SYSTEM (HKLM\SYSTEM) desde el disco
         │ 3. Carga ntoskrnl.exe, hal.dll y drivers con StartType = 0 (SERVICE_BOOT_START)
         │ 4. Si VBS está habilitado: invoca a hvloader.efi para iniciar Hyper-V
         │ 5. Llama a EFI_BOOT_SERVICES->ExitBootServices() (Termina el firmware)
         ▼
[ Kernel EntryPoint: ntoskrnl.exe!KiSystemStartup(LOADER_PARAMETER_BLOCK* pLpb) ]
```

---

## 3. La Estructura de Transición: `LOADER_PARAMETER_BLOCK`

Cuando `winload.efi` invoca la función de arranque del kernel (`nt!KiSystemStartup`), el hardware ya no tiene acceso a los servicios de UEFI (se ha llamado a `ExitBootServices`). La única vía por la cual el cargador transfiere información vital al kernel es mediante un puntero único pasado en el registro **`RCX`**: la estructura **`LOADER_PARAMETER_BLOCK`**.

### Offsets Críticos de `LOADER_PARAMETER_BLOCK` en x64:
- **`+0x010` `LoadOrderListHead` (`LIST_ENTRY`):** Lista doblemente enlazada de estructuras `KLDR_DATA_TABLE_ENTRY` que enumera todos los módulos y drivers cargados en memoria por `winload.efi` (incluyendo `ntoskrnl.exe`, `hal.dll`, `kd.dll` y drivers de arranque).
- **`+0x050` `MemoryDescriptorListHead` (`LIST_ENTRY`):** Mapa de memoria física del sistema clasificado por tipos (memoria utilizable, memoria reservada por firmware, memoria ACPI).
- **`+0x098` `Extension` (`Ptr64 _LOADER_PARAMETER_EXTENSION`):** Puntero a la extensión del bloque de arranque. En Windows 10/11 modernos, este campo contiene las estructuras de configuración de **VBS/HVCI**, el estado de inicialización de **Hyper-V** y los metadatos de integridad de código (*Code Integrity*).
- **`+0x0A0` `BootDriverListHead` (`LIST_ENTRY`):** Lista ordenada de controladores de arranque que deben ser inicializados por `IoInitSystem` antes de montar el sistema de archivos raíz.

### Inspección en WinDbg durante el Arranque Temprano
Si estás depurando una máquina virtual con WinDbg y configuras un breakpoint inicial (`sxe ibp` o `break` antes del kernel):
```text
$$ Inspeccionar el bloque de parámetros pasado a KiSystemStartup en RCX
dt nt!_LOADER_PARAMETER_BLOCK @rcx
$$ Volcar la lista de módulos cargados en el arranque
!list -t nt!_KLDR_DATA_TABLE_ENTRY.InLoadOrderLinks -x "dps @$extret+0x30 L2" (poi(@rcx+0x10))
```

---

## 4. Metodología de Análisis de Módulos EFI y Bootkits en IDA / Ghidra

Los bootkits modernos (como BlackLotus o Bootkm) buscan infectar la cadena de arranque antes de que `ntoskrnl.exe` active los mecanismos de protección de PatchGuard o las políticas de EDR.

### Pasos de Reversing para un Binario `.efi`:
1. **Carga en el Desensamblador:** Seleccionar el formato PE. En Ghidra o IDA Pro, utilizar los tipos de datos de UEFI (importando los headers de EDK2 o utilizando el plugin *EFISeek* / *Ghidra-EFI*).
2. **Localización de `SystemTable`:**
   En el prólogo de `EfiMain`, identificar la instrucción que salva el registro `RDX` en una variable global. Ese puntero es `gST` (`EFI_SYSTEM_TABLE`). En el offset **`+0x60`** de `gST` reside el puntero a `gBS` (`EFI_BOOT_SERVICES`).
3. **Identificación de Protocolos Hijackeados:**
   Los bootkits suelen instalar ganchos sobre funciones críticas de `EFI_BOOT_SERVICES` antes de que se cargue `winload.efi`:
   - Ganchos sobre **`LocateProtocol`** o **`OpenProtocol`**: interceptan la carga de protocolos para devolver punteros a rutinas modificadas.
   - Ganchos sobre **`ExitBootServices`**: capturan el momento exacto en que `winload.efi` va a transferir el control al kernel. En este punto, el bootkit parchea en memoria viva las rutinas de validación de firmas de `winload.efi` o inyecta código en `ntoskrnl!KiSystemStartup` para deshabilitar DSE antes de que el kernel arranque.
4. **Verificación Defensiva:** En sistemas corporativos, la integridad de esta cadena se audita mediante **Measured Boot** (el chip TPM registra los hashes SHA-256 de cada componente de arranque en los registros PCR 0 a 7, permitiendo a la red verificar remotamente que ningún binario EFI fue alterado).
