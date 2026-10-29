# Entregable 5 — Bibliografía Verificable con Enlaces

Esta bibliografía registra todas las fuentes públicas primarias (documentación oficial de fabricantes, estándares IETF, publicaciones académicas y libros técnicos de referencia) que respaldan las notas editoriales y las ampliaciones de la **Edición 5 — Revisión Ampliada 5.1**.

Para cada referencia se indica: identificador `[Ref-N]`, título, autor u organización, URL pública verificable, sección o apartado específico que respalda la afirmación técnica y fecha de consulta.

---

## 5.1 Fuentes Oficiales, Estándares y Documentación Primaria

- **[Ref-1]** **Microsoft Corporation (Microsoft Learn).** *`WindowProc` callback function (`winuser.h`) & x64 Calling Convention*.  
  - **URL:** https://learn.microsoft.com/en-us/windows/win32/api/winuser/nc-winuser-wndproc y https://learn.microsoft.com/en-us/cpp/build/x64-calling-convention  
  - **Apartado que respalda la ampliación:** Prototipo `(HWND hwnd, UINT uMsg, WPARAM wParam, LPARAM lParam)` y sección *Parameter Passing* (los primeros cuatro argumentos enteros o punteros se pasan en `RCX`, `RDX`, `R8` y `R9` de izquierda a derecha). Respalda el **Módulo 2 (Lección 2.6)**.  
  - **Fecha de consulta:** 29 de octubre de 2026.

- **[Ref-2]** **Microsoft Corporation (Microsoft Learn).** *`WM_COMMAND` message (Winuser.h)*.  
  - **URL:** https://learn.microsoft.com/en-us/windows/win32/menurc/wm-command  
  - **Apartado que respalda la ampliación:** Tabla de parámetros de `wParam`: *«The high-order word specifies the notification code if the message is from a control... The low-order word specifies the identifier of the menu item, control, or accelerator»* (`LOWORD(wParam)` = Control ID, `HIWORD(wParam)` = código de notificación). Respalda el **Módulo 2 (Lección 2.6)**.  
  - **Fecha de consulta:** 29 de octubre de 2026.

- **[Ref-3]** **x64dbg Project (Duncan Ogilvie / mrexodia et al.).** *x64dbg Documentation — Expressions & Expression Functions (`arg.get`)*.  
  - **URL:** https://help.x64dbg.com/en/latest/introduction/Expressions.html y https://help.x64dbg.com/en/latest/introduction/Formatting.html  
  - **Apartado que respalda la ampliación:** Sección *Arguments*: `arg.get(index)` obtiene el argumento `index` (basado en 0) según la convención de llamada de la arquitectura actual, y formato de cadenas de log `{expresión}`. Respalda el **Módulo 2 (Lección 2.6)** y el **Módulo 17 (Glosario)**.  
  - **Fecha de consulta:** 29 de octubre de 2026.

- **[Ref-4]** **Junod, P., Rinaldini, J., Wehrli, J., & Michielin, J. (HEIG-VD / Obfuscator-LLVM Project).** *Obfuscator-LLVM: Software Protection for the Masses — Control Flow Flattening*. En *Proceedings of the IEEE/ACM 1st International Workshop on Software Protection (SPRO '15)*, pp. 3–9, y Wiki técnica del proyecto.  
  - **URL:** https://github.com/obfuscator-llvm/obfuscator/wiki/Control-Flow-Flattening y https://doi.org/10.1109/SPRO.2015.10  
  - **Apartado que respalda la ampliación:** Descripción de la transformación de los bloques básicos de una función en casos de un único `switch` envuelto en un bucle infinito controlado por una variable de estado local que se actualiza al final de cada bloque. Respalda el **Módulo 3 (Lección 2.10)**.  
  - **Fecha de consulta:** 29 de octubre de 2026.

- **[Ref-5]** **Rolles, R.** *Unpacking Virtualization Obfuscators*. En *Proceedings of the 3rd USENIX Workshop on Offensive Technologies (WOOT '09)*, USENIX Association, Montreal, 2009.  
  - **URL:** https://www.usenix.org/legacy/events/woot09/tech/full_papers/rolles.pdf  
  - **Apartado que respalda la ampliación:** Secciones 2 (*Virtualization Obfuscation Architecture*) y 3 (*Reverse Engineering Virtualization Obfuscators*): arquitectura del intérprete de bytecode, registros de contexto virtual (`VIP`/`VPC` y `VSP`), bucle *fetch-decode-dispatch* y diferencias estructurales frente a ofuscadores de código nativo directo. Respalda el **Módulo 3 (Lección 2.10)**.  
  - **Fecha de consulta:** 29 de octubre de 2026.

- **[Ref-6]** **Microsoft Corporation (Microsoft Learn / Visual C++ MFC Reference).** *Message Map Macros (MFC), `TN006: Message Maps` y encabezado `<afxwin.h>` (`AFX_MSGMAP` y `AFX_MSGMAP_ENTRY`)*.  
  - **URL:** https://learn.microsoft.com/en-us/cpp/mfc/reference/message-map-macros-mfc y https://learn.microsoft.com/en-us/cpp/mfc/tn006-message-maps  
  - **Apartado que respalda la ampliación:** Estructura interna de los mapas de mensajes de MFC (`GetMessageMap`, estructura `AFX_MSGMAP` con puntero al mapa base y a `lpEntries`, campos `nMessage`, `nCode`, `nID`, `nLastID`, `nSig`, `pfn` de `AFX_MSGMAP_ENTRY` y centinela `AfxSig_end = 0`). Respalda el **Módulo 4 (Lección 2.12)**.  
  - **Fecha de consulta:** 29 de octubre de 2026.

- **[Ref-7]** **Embarcadero Technologies (RAD Studio DocWiki).** *Program Control (Delphi) — Calling Conventions (`register`, `pascal`, `cdecl`, `stdcall`, `safecall`) & 64-bit Windows Calling Convention*.  
  - **URL:** https://docwiki.embarcadero.com/RADStudio/en/Program_Control  
  - **Apartado que respalda la ampliación:** Subsecciones *Calling Conventions* y *Method Calls*: paso de los tres primeros parámetros en `EAX`, `EDX` y `ECX` en 32 bits, apilado de izquierda a derecha de los parámetros restantes, paso de `Self` en `EAX`, y adopción de la ABI x64 de Microsoft (`RCX`, `RDX`, `R8`, `R9`) en compilaciones de 64 bits. Respalda el **Módulo 5 (Lección 2.13)**.  
  - **Fecha de consulta:** 29 de octubre de 2026.

- **[Ref-8]** **Embarcadero Technologies (RAD Studio DocWiki).** *Internal Data Formats (Delphi) — Long String Types (`AnsiString` and `UnicodeString` Memory Layout / `StrRec`)*.  
  - **URL:** https://docwiki.embarcadero.com/RADStudio/en/Internal_Data_Formats_(Delphi)  
  - **Apartado que respalda la ampliación:** Sección *Long String Types*: tabla de desplazamientos negativos respecto del puntero de texto (`-12` página de códigos de 16 bits, `-10` tamaño de elemento en bytes de 16 bits, `-8` contador de referencias de 32 bits, `-4` longitud en caracteres de 32 bits y `0` cadena terminada en nulo). Respalda el **Módulo 5 (Lección 2.13)**.  
  - **Fecha de consulta:** 29 de octubre de 2026.

- **[Ref-9]** **Embarcadero Technologies (RAD Studio DocWiki).** *Using Resource Files (`DFM` Form Files, `RT_RCDATA`) & `System.Classes.TWriter` / `TestStreamFormat` (`TPF0` signature)*.  
  - **URL:** https://docwiki.embarcadero.com/RADStudio/en/Using_Resource_Files y https://docwiki.embarcadero.com/Libraries/en/System.Classes.TStream.ReadComponentRes  
  - **Apartado que respalda la ampliación:** Almacenamiento de formularios VCL/FMX compilados como recursos `RT_RCDATA` precedidos por la firma mágica de 4 bytes `"TPF0"` y enlace de propiedades de eventos (`OnClick`) con métodos publicados via RTTI. Respalda el **Módulo 5 (Lección 2.13)**.  
  - **Fecha de consulta:** 29 de octubre de 2026.

- **[Ref-10]** **Microsoft Corporation (Microsoft Learn).** *`PEB` structure (`winternl.h`)*.  
  - **URL:** https://learn.microsoft.com/en-us/windows/win32/api/winternl/ns-winternl-peb  
  - **Apartado que respalda la ampliación:** Definición oficial de `PEB` en x86 y x64: `BeingDebugged` en `+0x02`, `Ldr` (`PPEB_LDR_DATA`) en `+0x0C` (x86) y `+0x18` (x64). Respalda los **Módulos 6 y 7 (Lecciones 2.14 y 2.15)**.  
  - **Fecha de consulta:** 29 de octubre de 2026.

- **[Ref-11]** **Microsoft Corporation (Microsoft Learn).** *`PEB_LDR_DATA` structure (`winternl.h`)*.  
  - **URL:** https://learn.microsoft.com/en-us/windows/win32/api/winternl/ns-winternl-peb_ldr_data  
  - **Apartado que respalda la ampliación:** Definición de `PEB_LDR_DATA` y `LDR_DATA_TABLE_ENTRY`: ubicación de `InMemoryOrderModuleList` (`+0x14` en x86, `+0x20` en x64) y de `InMemoryOrderLinks` (`+0x08` en x86, `+0x10` en x64), `DllBase` (`+0x18` en x86, `+0x30` en x64) y `FullDllName` (`+0x24` en x86, `+0x48` en x64). Respalda el **Módulo 6 (Lección 2.14)**.  
  - **Fecha de consulta:** 29 de octubre de 2026.

- **[Ref-12]** **Yosifovich, P., Ionescu, A., Russinovich, M. E., & Solomon, D. A.** *Windows Internals, Part 1: System architecture, processes, threads, memory management, and more* (7th Edition). Microsoft Press, 2017.  
  - **URL de referencia editorial:** https://www.microsoftpressstore.com/store/windows-internals-part-1-system-architecture-processes-9780735684188  
  - **Apartado que respalda la ampliación:** Capítulo 3 (*Processes and Jobs — Process Environment Block*) y Capítulo 5 (*Memory Management — Virtual Address Descriptors & Heap Manager*): listas `InLoadOrderLinks`, `InMemoryOrderLinks` e `InInitializationOrderLinks` de `LDR_DATA_TABLE_ENTRY`, `NtGlobalFlag` y arquitectura del *Segment Heap*. Respalda los **Módulos 6, 7 y 10 (Lecciones 2.14, 2.15 y 2.19)**.  
  - **Fecha de consulta:** 29 de octubre de 2026.

- **[Ref-13]** **Microsoft Corporation (Microsoft Learn).** *`NtQueryInformationProcess` function (`winternl.h`)*.  
  - **URL:** https://learn.microsoft.com/en-us/windows/win32/api/winternl/nf-winternl-ntqueryinformationprocess  
  - **Apartado que respalda la ampliación:** Parámetro `ProcessInformationClass`: `ProcessDebugPort = 7` (devuelve `-1` / distinto de cero cuando el proceso se ejecuta bajo depurador de modo usuario), junto con las clases del subsistema de depuración `ProcessDebugObjectHandle` (`0x1E`, devuelve `STATUS_PORT_NOT_SET = 0xC0000353` si no existe objeto de depuración) y `ProcessDebugFlags` (`0x1F`). Respalda el **Módulo 7 (Lección 2.15)**.  
  - **Fecha de consulta:** 29 de octubre de 2026.

- **[Ref-14]** **Microsoft Corporation (Microsoft Learn).** *GFlags Flag Table*.  
  - **URL:** https://learn.microsoft.com/en-us/windows-hardware/drivers/debugger/gflags-flag-table  
  - **Apartado que respalda la ampliación:** Tabla de valores hexadecimales de `NtGlobalFlag`: `FLG_HEAP_ENABLE_TAIL_CHECK` (`0x10`), `FLG_HEAP_ENABLE_FREE_CHECK` (`0x20`) y `FLG_HEAP_VALIDATE_PARAMETERS` (`0x40`), cuya suma combinada es `0x70`. Respalda el **Módulo 7 (Lección 2.15)**.  
  - **Fecha de consulta:** 29 de octubre de 2026.

- **[Ref-15]** **Sikorski, M., & Honig, A.** *Practical Malware Analysis: The Hands-On Guide to Dissecting Malicious Software*. No Starch Press, San Francisco, 2012.  
  - **URL de referencia editorial:** https://nostarch.com/malware  
  - **Apartado que respalda la ampliación:** Capítulo 16 (*Anti-Debugging*: `NtGlobalFlag` en `+0x68` x86 / `+0xBC` x64 y clases `0x07`, `0x1E`, `0x1F` de `NtQueryInformationProcess`) y Capítulo 18 (*Packers and Unpacking — Section "The ESP Trick"*, pp. 388–390): uso de un breakpoint de hardware en acceso sobre `ESP` tras el `pushad` inicial del stub para detenerse en el `popad` previo al salto al OEP. Respalda los **Módulos 7 y 8 (Lecciones 2.15 y 2.17)**.  
  - **Fecha de consulta:** 29 de octubre de 2026.

- **[Ref-16]** **Intel Corporation.** *Intel® 64 and IA-32 Architectures Software Developer's Manual, Volume 3B: System Programming Guide, Part 2*.  
  - **URL:** https://www.intel.com/content/www/us/en/developer/articles/technical/intel-sdm.html  
  - **Apartado que respalda la ampliación:** Capítulo 18 / §17.2 (*Debug Registers `DR0`–`DR7`*): funcionamiento de los breakpoints de datos por hardware (*Data Read or Write*), que disparan una excepción `#DB` (*trap*, después de completarse la instrucción que leyó la dirección vigilada en la pila). Respalda el **Módulo 8 (Lección 2.17)**.  
  - **Fecha de consulta:** 29 de octubre de 2026.

- **[Ref-17]** **Modi, R. / Microsoft C++ Team (Microsoft Developer Blogs & MSVC Documentation).** *Making C++ Exception Handling Smaller on x64 (`__CxxFrameHandler4` / `/d2FH4`)*.  
  - **URL:** https://devblogs.microsoft.com/cppblog/making-cpp-exception-handling-smaller-x64/  
  - **Apartado que respalda la ampliación:** Secciones *Current x64 EH Metadata (`__CxxFrameHandler3`)* y *New Metadata Format (`__CxxFrameHandler4`)*: eliminación de los campos fijos de 32 bits (`magicNumber = 0x19930520`), introducción del byte `FuncInfoHeader` y compresión de enteros con longitud variable de 1 a 4 bytes en `.xdata`. Respalda el **Módulo 9 (Lección 2.18)** y el **Módulo 17 (Glosario)**.  
  - **Fecha de consulta:** 29 de octubre de 2026.

- **[Ref-18]** **Microsoft Corporation (Microsoft Learn).** *Application Manifests — `segmentHeap` element*.  
  - **URL:** https://learn.microsoft.com/en-us/windows/win32/sbscs/application-manifests#segmentHeap  
  - **Apartado que respalda la ampliación:** Especificación del elemento `<segmentHeap>` en Windows 10 (2004+) y Windows 11 para optar por la implementación del *Segment Heap* en lugar del *Legacy Heap (NT Heap)*. Respalda el **Módulo 10 (Lección 2.19)** y el **Módulo 17 (Glosario)**.  
  - **Fecha de consulta:** 29 de octubre de 2026.

- **[Ref-19]** **Microsoft Corporation (Microsoft Learn).** *`!heap` (WinDbg Debugger Command Reference)*.  
  - **URL:** https://learn.microsoft.com/en-us/windows-hardware/drivers/debuggercmds/-heap  
  - **Apartado que respalda la ampliación:** Uso de `!heap` sobre *NT Heap* y *Segment Heap*, y modificadores `-p -a <Address>` para inspeccionar bloques bajo *Page Heap* (`_DPH_HEAP_ROOT`). Respalda el **Módulo 10 (Lección 2.19)**.  
  - **Fecha de consulta:** 29 de octubre de 2026.

- **[Ref-20]** **Microsoft Corporation (Microsoft Learn).** *Single-file deployment and executable in .NET*.  
  - **URL:** https://learn.microsoft.com/en-us/dotnet/core/deploying/single-file/overview  
  - **Apartado que respalda la ampliación:** Estructura de un ejecutable *Single-File* (`PublishSingleFile`): un host nativo (`apphost`) que empaqueta los ensamblados `.dll` administrados de IL y metadatos, y tabla comparativa frente a `PublishAot` (*Native AOT*). Respalda el **Módulo 11 (Lección 3.1)** y el **Módulo 17 (Glosario)**.  
  - **Fecha de consulta:** 29 de octubre de 2026.

- **[Ref-21]** **Microsoft Corporation (Microsoft Learn).** *ReadyToRun (R2R) deployment overview*.  
  - **URL:** https://learn.microsoft.com/en-us/dotnet/core/deploying/ready-to-run  
  - **Apartado que respalda la ampliación:** Descripción de binarios *ReadyToRun* (`PublishReadyToRun`): coexistencia en el mismo archivo PE del código IL y metadatos originales junto con código nativo precompilado descripto por la cabecera `READYTORUN_HEADER` (`"RTR\0"`). Respalda el **Módulo 11 (Lección 3.1)** y el **Módulo 17 (Glosario)**.  
  - **Fecha de consulta:** 29 de octubre de 2026.

- **[Ref-22]** **Nir, Y., & Langley, A. (IETF).** *RFC 8439: ChaCha20 and Poly1305 for IETF Protocols*. Internet Engineering Task Force (IETF), junio de 2018.  
  - **URL:** https://www.rfc-editor.org/rfc/rfc8439  
  - **Apartado que respalda la ampliación:** Sección 2.1 (*The ChaCha20 Quarter Round*: operaciones `ADD`, `XOR` y rotaciones de `16`, `12`, `8` y `7` bits) y Sección 2.3 (*The ChaCha20 Block Function*): matriz inicial de 16 palabras de 32 bits cuyas primeras cuatro palabras son las constantes `0x61707865`, `0x3320646e`, `0x79622d32`, `0x6b206574` (ASCII `"expand 32-byte k"`), seguidas de 8 palabras de clave, 1 de contador y 3 de *nonce*, ejecutando 20 rondas (10 iteraciones de doble ronda). Respalda el **Módulo 13 (Lección 4.2)** y el **Módulo 17 (Glosario)**.  
  - **Fecha de consulta:** 29 de octubre de 2026.

- **[Ref-23]** **Hex-Rays SA.** *IDAPython documentation — Porting from IDA 8.x to IDA 9.0 (`ida_typeinf` replacing `ida_struct` and `ida_enum`)*.  
  - **URL:** https://docs.hex-rays.com/user-guide/idapython/idapython-porting-guide-ida-9 y https://python.docs.hex-rays.com/  
  - **Apartado que respalda la ampliación:** Guía oficial de migración a IDA 9.0: eliminación de los módulos `ida_struct` e `ida_enum` (y sus equivalentes en `idc`) y tabla de reemplazo mediante `ida_typeinf.tinfo_t`, `udt_type_data_t` y `enum_type_data_t`. Respalda el **Módulo 14 (Lección 5.3)** y el **Módulo 17 (Glosario)**.  
  - **Fecha de consulta:** 29 de octubre de 2026.

- **[Ref-24]** **Microsoft Corporation (Microsoft Learn).** *`WdfRequestRetrieveInputBuffer` and `WdfRequestRetrieveOutputBuffer` (`wdfrequest.h`)*.  
  - **URL:** https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdfrequest/nf-wdfrequest-wdfrequestretrieveinputbuffer y https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdfrequest/nf-wdfrequest-wdfrequestretrieveoutputbuffer  
  - **Apartado que respalda la ampliación:** Parámetro `MinimumRequiredSize` / `MinimumRequiredLength` y retorno de `STATUS_BUFFER_TOO_SMALL` cuando el buffer asociado a la solicitud es menor que el mínimo requerido. Respalda el **Módulo 15 (Lección 6.2)**.  
  - **Fecha de consulta:** 29 de octubre de 2026.

- **[Ref-25]** **Microsoft Corporation (Microsoft Learn).** *Accessing Data Buffers in WDF Drivers & Using Neither Buffered I/O Nor Direct I/O in KMDF (`EvtIoInCallerContext`, `WdfRequestRetrieveUnsafeUserInputBuffer`, `WdfRequestProbeAndLockUserBufferForRead`)*.  
  - **URL:** https://learn.microsoft.com/en-us/windows-hardware/drivers/wdf/accessing-data-buffers-in-wdf-drivers  
  - **Apartado que respalda la ampliación:** Tabla de métodos de acceso a buffers en KMDF (`METHOD_BUFFERED`, `METHOD_IN_DIRECT`/`METHOD_OUT_DIRECT` con `WdfRequestRetrieveOutputWdmMdl`, y `METHOD_NEITHER` exclusivamente desde `EvtIoInCallerContext` usando `WdfRequestRetrieveUnsafeUserInputBuffer`/`OutputBuffer` y `WdfRequestProbeAndLockUserBufferForRead`/`ForWrite`). Respalda íntegramente la reconstrucción de la 5.ª columna truncada en el **Módulo 15 (Lección 6.2)**.  
  - **Fecha de consulta:** 29 de octubre de 2026.

---

## 5.2 Referencia Interna del Corpus Auditado

- **[Ref-Interna]** **Proyecto CLS (`CLS_Guia`).** *`CLS_Curso_Reversing.pdf` (Edición 5, 28/10/2026, 403 páginas) y fuentes locales en `_trabajo/src/`, `FUENTES_Y_LIMITES.md`, `mapa_de_cobertura.csv` y `registro_de_cobertura.csv`*.  
  - **Ubicación local:** `d:\CLS_proyecto\CLS_Guia\CLS_Curso_Reversing.pdf`
