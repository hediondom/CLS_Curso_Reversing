# Fe de Erratas y Matriz de Trazabilidad Técnica — Tomo II (Fase 1 Consolidada)

**Proyecto:** Reversing en Windows — Edición Libre y Abierta  
**Volumen:** Tomo II («Kernel, Drivers e Internals»)  
**Alcance:** Fase 1 · Auditoría y Corrección de Erratas (E-01 a E-10) y Trazabilidad Cruzada con Tomo I  
**Estado de verificación:** Verificado contra el texto consolidado del Tomo II (`Tomo_2_Kernel_e_Internals.pdf`, 160 págs.), los archivos HTML de la Rama 2D (`2d-10` a `2d-15`) y las referencias cruzadas del Tomo I (`Tomo_1_Parte_A` y `Tomo_1_Parte_B`).  

> [!NOTE]
> **Política de Integridad Editorial de la Trilogía:**  
> Las referencias técnicas que involucran al Tomo I se registran exclusivamente en este documento para fines de fe de erratas y trazabilidad analítica sin reeditar el Tomo I, respetando rigurosamente la política de cobertura honesta declarada en el Tomo I (págs. 8–9) y en el Tomo II (págs. 62–63).

**Fuentes Primarias Consultadas:**
* Microsoft Learn: *NTSTATUS Values*, *Bug Check Code Reference*, *x64 Exception Handling*, *PE Format*, *dt (Display Type)*, *Control Flow Guard*.
* Cabeceras del Windows SDK / WDK: `ntstatus.h`, `winnt.h`, `wdffuncenum.h`, `ntddk.h`.
* Símbolos públicos oficiales de Microsoft (`ntoskrnl.pdb`) para Windows 10 22H2 (Build 19045), Windows 11 23H2 (Build 22631) y Windows 11 24H2 (Build 26100).
* Intel 64 and IA-32 Architectures Software Developer’s Manual: Vol. 2B (XOR opcodes `0x31 /r` y `0x33 /r`), Vol. 3A §6.15 (Interrupt 21 — `#CP`).

---

## 1. Tabla Consolidada de Erratas del Tomo II

| # | Archivo / Ubicación | Línea / Sección | Afirmación Actual / Estado Previo | Corrección Técnica Aplicada | Fuente Oficial |
|---|---|---|---|---|---|
| **E-01** | `guia/6-07-vbs-hvci-callbacks.html` (Tomo II, p. 52) y ref. cruzada Tomo I Lección 5.2.b (p. 333–334) | Sección 1 · kCFG Respaldado por VTL 1 (p. 52) / Tomo I p. 333 | En Tomo I (p. 333) se afirma que ante `#CP` Windows aborta con `0xC0000409`, y en 6.7 (p. 52) se describe kCFG sin precisar los códigos NTSTATUS de fallo. | `0xC0000409` es `STATUS_STACK_BUFFER_OVERRUN` (invocado vía `__fastfail` / `int 29h` con subcódigo en `RCX`, e.g. `0x0A` para CFG). La excepción de hardware `#CP` (vector 21 CET/Shadow Stack) asigna específicamente `0xC00006A6` (`STATUS_CONTROL_PROTECTION_EXCEPTION`) y bugcheck `0x139` param `0x39` o `0x7F` trampa `0x15`. Se agregó nota aclaratoria en 6.7. | Microsoft Learn: NTSTATUS Values; Windows SDK `ntstatus.h` y `winnt.h`; Intel SDM Vol. 3A §6.15. |
| **E-02** | `guia/2d-01-objetos.html` (Tomo II, p. 65) y cruce con Tomo I Hoja 6 (p. 382) | Recuadro *Los offsets de nt!_EPROCESS cambian entre builds* (p. 65) | Error tipográfico en tabla: `Token` indicaba `+0x488` en vez de `+0x4B8`; `MitigationFlags` indicaba `+0x458` en vez de `+0xA58`. No se advertía la reestructuración completa de `_EPROCESS` en Win11 24H2 GA (Build 26100). | Se corrigió `Token` a `+0x4B8` (19045/22631) y se incorporaron los esquemas duales de Windows 11 24H2 Build 26100 (GA: `UniqueProcessId` `+0x1D0`, `ActiveProcessLinks` `+0x1D8`, `Token` `+0x248`, `ImageFileName` `+0x338`, `Protection` `+0x5FA`, `MitigationFlags` `+0x750`; Pre-GA: `+0x440`, `+0x448`, `+0x4B8`, `+0x5A8`, `+0x8FA`, `+0xA58`). | Símbolos públicos `ntoskrnl.pdb` (Builds 19045, 22631, 26100); MS Learn: `dt` command. |
| **E-03** | `guia/6-07-vbs-hvci-callbacks.html` (Tomo II, p. 54, 56 y 60) | Sección 2.D · *Sensor en Proceso: KPROCESS->InstrumentationCallback* (p. 54–56) y Sección 6.7.b (p. 60) | 1) No precisaba builds ni cambio en Win11 24H2. 2) En scripts WinDbg usaba `poi(... ImageFileName)` con formato `%s`. | 1) Se asociaron offsets: `+0x3D8` (Win10 19045), `+0x3E8` (Win11 22621/22631), `+0x2C8` (Win11 26100). 2) Se quitó `poi()` sobre `ImageFileName` usando `%ma` ya que es un arreglo embebido `UCHAR[15]` (`+0x5A8` en 19045/22631, `+0x338` en 26100). | Símbolos públicos `ntoskrnl.pdb` (Builds 19045, 22631, 26100); Microsoft Learn: `.printf`. |
| **E-04** | `guia/6-07-vbs-hvci-callbacks.html` (Tomo II, p. 57–58) | Sección 3 · *Detección Defensiva: La Tabla de Caché nt!PiDDBCacheTable* (p. 57–58) | 1) Calificaba a `PiDDBCacheTable` como «tabla hash» en vez de árbol AVL. 2) Usaba sintaxis errónea `poi(nt!PiDDBCacheTable)` y tipo no exportado `_PiDDBCacheEntry`. | 1) Se precisó que es un árbol AVL genérico (`_RTL_AVL_TABLE`). 2) `PiDDBCacheTable` es la estructura misma (sin `poi()`). Cada nodo comienza con `_RTL_BALANCED_LINKS` (`0x20` bytes) seguido del payload (`LIST_ENTRY` en `+0x20`, `UNICODE_STRING DriverName` en `+0x30`, `TimeDateStamp` en `+0x40`). | Windows WDK `ntddk.h` (`RTL_AVL_TABLE`, `RTL_BALANCED_LINKS`); símbolos públicos `ntoskrnl.pdb`. |
| **E-05** | `guia/6-04-revision-driver.html` (Tomo II, p. 30) y `guia/6-07-vbs-hvci-callbacks.html` (Tomo II, p. 59) | Tabla de WDFFUNCTIONS (p. 30) y Sección 4 *Reenvío Asíncrono en KMDF* (p. 59) | 1) En 6.4 offsets de `WdfDriverCreate` y `WdfRequestRetrieveOutputBuffer`. 2) En 6.7 listado x64 cargaba `mov rcx, [rbx + 0x910]; call rcx`, pisando el primer argumento. | 1) Verificados y consolidados `+0x1D8` y `+0x8A0`. 2) En 6.7 se corrigió para pasar `PWDF_DRIVER_GLOBALS` en `RCX`, argumentos en `RDX`/`R8`/`R9`, e invocar vía `call qword ptr [rax + 910h]`. | WDK `wdffuncenum.h` (KMDF 1.15–1.33); MS Learn: `WdfRequestSetCompletionRoutine`. |
| **E-06** | `guia/2d-14-win32k-shadow.html` (Tomo II, p. 150–152) | Sección 2 · *Despacho por la Tabla Sombra y Conversión de Números de Servicio* | 1) Afirmaba que `KeServiceDescriptorTable` es una tabla global exportada en x64. 2) Ubicaba `Win32Thread` en `GS:[0x188]`. | 1) Se aclaró que en x64 ni la SSDT ni la Shadow SSDT se exportan en la EAT de `ntoskrnl.exe`. 2) Se precisó que `GS:[0x188]` es `CurrentThread` (`_KTHREAD`), y dentro de `_KTHREAD` el campo `Win32Thread` reside en `+0x1C8` (19045, 22631, 26100). | Símbolos públicos `ntoskrnl.pdb` (Builds 19045, 22631, 26100); MS Learn: x64 Architecture. |
| **E-07** | `guia/2d-15-uefi-boot-chain.html` (Tomo II, p. 156) | Sección 3 · *Offsets Críticos de LOADER_PARAMETER_BLOCK en x64* | Indicaba offsets heredados de Windows 7 (`+0x050` MemoryDescriptorListHead, `+0x098` Extension, `+0x0A0` BootDriverListHead). | Se actualizaron a los offsets modernos de Windows 10/11: `+0x010` LoadOrderListHead, `+0x020` MemoryDescriptorListHead, `+0x030` BootDriverListHead, y `+0x0F0` Extension (`_LOADER_PARAMETER_EXTENSION*`). | Símbolos públicos `ntoskrnl.pdb` (`dt nt!_LOADER_PARAMETER_BLOCK` en 19045, 22631, 26100). |
| **E-08** | `guia/2d-11-excepciones.html` (Tomo II, p. 133–137) | Blockquote *Call Stack Spoofing*, slots `UNWIND_CODE` y callout *Lo que queda fuera* | 1) Quedaron asteriscos `**` de Markdown en HTML. 2) Código `10 = UWOP_EPILOG`. 3) Callout afirmaba que `UNWIND_INFO` quedaba fuera. | 1) Reemplazados `**` por `<strong>`. 2) Se corrigió `6 = UWOP_EPILOG` (Windows 8.1+ / VS 2013) y `10 = UWOP_PUSH_MACHFRAME` (marco de interrupción/trampa). 3) Se ajustó el callout reflejando la cobertura de `UNWIND_INFO`. | Microsoft Learn: x64 Exception Handling — UNWIND_CODE; Windows SDK `winnt.h`. |
| **E-09** | `guia/2d-10-ipc.html` (p. 124–129) y `guia/2d-12-etw.html` (p. 142, 144) | Callouts *Puerta optativa* y *Lo que queda fuera* en 2D.10; listas partidas y opcodes en 2D.12 | 1) En 2D.10 callout contradecía cobertura de NDR y ALPC. 2) En 2D.12 listas partidas y discrepancia entre `31 C0 C3` y `33 C0 C3`. | 1) Se sincronizaron los callouts de 2D.10. 2) Se corrigió el anidamiento de listas en 2D.12 y se aclaró que `31 C0 C3` (GAS/NASM) y `33 C0 C3` (MSVC/MASM) son codificaciones válidas de `xor eax, eax; ret`. | Especificación HTML5; Intel SDM Vol. 2B (XOR opcodes `0x31` y `0x33`). |
| **E-10** | `guia/2d-13-integrador.html` (Tomo II, p. 148) y aperturas de Etapa 6 / Rama 2D | Tablas de lecciones de Etapa 6 (p. 3), listado 2D (p. 62) y enlaces de Fuentes | Enlace genérico a `04-informe.html` y desincronización de índices con lecciones avanzadas (6.7–6.10, 2D.14–2D.17). | Se incorporaron citas específicas a las lecciones 4.1 (Tomo I, p. 282) y 4.3 (Tomo I, p. 301) y enlaces completos a 2D.14 y 2D.15. | Índices generales del Tomo I (p. 2) y Tomo II (p. 2). |

---

## 2. Matriz de Trazabilidad Cruzada con Tomo I (Sin Modificación de Tomo I)

| Punto de Auditoría en Tomo I | Ubicación Física en Tomo I | Tratamiento Metodológico | Resolución en Tomo II y Errata |
|---|---|---|---|
| Excepción `#CP` reportada como `0xC0000409` | Tomo I, Lección 5.2.b (p. 333–334) | **Preservado inalterado.** Se respeta la p. 8–9 de Tomo I (obra publicada). | Errata **E-01** en `guia/6-07-vbs-hvci-callbacks.html` y Lección `6-09-kcfg-isa.html` aclaran la distinción formal entre `STATUS_STACK_BUFFER_OVERRUN` (`0xC0000409` vía fast-fail) y `STATUS_CONTROL_PROTECTION_EXCEPTION` (`0xC00006A6` vía `#CP` hardware). |
| Variación de offsets de `_EPROCESS` en Win11 24H2 | Tomo I, Hoja 6 de la Separata (p. 382) | **Preservado inalterado.** Las tablas históricas reflejan compilaciones pre-GA. | Errata **E-02** en `guia/2d-01-objetos.html` documenta la reorganización mayor de `nt!_EPROCESS` en Build 26100 GA (`UniqueProcessId` `+0x1D0`, `Token` `+0x248`). |
| Método de análisis e informe técnico | Tomo I, Lecciones 4.1 (p. 282) y 4.3 (p. 301) | **Referenciado como fundamento.** | Errata **E-10** en `guia/2d-13-integrador.html` formaliza los hipervínculos cruzados y números de página exactos hacia el Tomo I. |
| Syscalls y tablas de despacho SSDT | Tomo I, Lección 2.15 (p. 180–188) | **Ampliado hacia kernel-mode.** | Errata **E-06** en `guia/2d-14-win32k-shadow.html` vincula la SSDT user-mode con la Shadow SSDT gráfica de Ring 0. |

---

## 3. Estado de Cierre de Fase 1

Todas las 10 erratas han sido incorporadas y verificadas sintácticamente en los archivos fuente HTML de `guia/`. El Tomo II queda completamente consistente y libre de discordancias técnicas.
