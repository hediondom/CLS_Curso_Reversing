# Curso de Reversing e Ingeniería Inversa en Windows

Guía completa y profesional de ingeniería inversa, reversing de binarios y seguridad interna en sistemas Windows (x86, x64, ARM64EC y Kernel NT). Diseñada para analistas de malware, auditores de seguridad defensiva, desarrolladores de software de bajo nivel e investigadores de vulnerabilidades.

---

## 🧭 Estructura General de la Obra

La obra está organizada en dos grandes ejes temáticos:
1. **Tronco Principal (Tomo I - Etapas 0 a 5):** Desde los fundamentos de representación numérica, arquitectura y ciclo de vida de procesos/PE, pasando por el dominio de desensambladores (IDA Pro, Ghidra) y debuggers (x64dbg, WinDbg), hasta técnicas avanzadas de desvirtualización, reversing de Go/Rust, WinRT, ARM64EC y análisis de malware/vulnerabilidades.
2. **Ramas Especializadas (Tomo II - Etapa 6 y Rama 2D):** Seguridad interna del sistema operativo en profundidad, cubriendo arquitectura de drivers KMDF/WDM, depuración de kernel con WinDbg, subsistema gráfico Win32k (`KeServiceDescriptorTableShadow`), cadena de arranque UEFI (`bootmgfw.efi`, `winload.efi`), VBS/HVCI en VTL1, auditoría de telemetría de kernel (`ETWti`), mecánicas BYOVD e internals del ejecutivo NT.

---

## 📚 Materiales Impresos y Formato PDF (Revisión 5.4 Consolidada)

El material está optimizado para lectura digital e impresión profesional en gráfica (formato A4, márgenes simétricos para anillado o encuadernación rústica pegada al lomo, control estricto de orfandad, paridad para doble faz y contraste optimizado).

### 🖨️ Cuadernillos de Impresión Recomendados (Distribución Práctica)

Para facilitar la manipulación física y el uso diario en el escritorio, la obra se distribuye en 4 cuadernillos independientes de lomo equilibrado:

| Archivo PDF | Páginas | Hojas (doble faz) | Encuadernación / Contenido |
| :--- | :---: | :---: | :--- |
| **`Tomo_1_Parte_A_pags_1-172.pdf`** | **172 págs.** | **86 hojas** | **Tomo I · Parte A:** Fundamentos de arquitectura x86/x64, ciclo de vida del PE y DLLs (Loader Lock), desensamblado estático (IDA Pro / Ghidra), depuración dinámica táctica con x64dbg (breakpoints `$ptr`), y análisis de anti-análisis y packers (Etapas 0 a 2C).<br>*(Anillado metálico Ring Wire / espiral o binder con tapa dura/polipropileno)*. |
| **`Tomo_1_Parte_B_pags_173-396.pdf`** | **224 págs.** | **112 hojas** | **Tomo I · Parte B:** C++ moderno en bajo nivel (vtables, RTTI, SSO, Smart Pointers, `std::function`), WinDbg y análisis de Heap, .NET/CLR, Criptografía híbrida (CryptoAPI vs. CNG), Metodología de Triage de 5 pasos, Bloque 2E avanzado (angr/Z3, VM bytecode, protectores multicapa, Go y Rust con layouts de slices/async, VB6 p-code), **Lección 2.34** (desvirtualización, pipeline Frida Stalker + Triton AST + Z3, y procesador SLEIGH completo), **Lección 2.35** (ARM64EC, WinRT `IInspectable`, sandboxing AppContainer/LPAC con SIDs de capacidades, y Native AOT con secciones `.managedcode`/`.hydrated` y JIT Hooking), Casos prácticos, Kit de 15 plantillas y Apoyo (Glosario, Q&A, Fichas).<br>*(Anillado metálico Ring Wire / espiral o binder con tapa dura/polipropileno)*. |
| **`Tomo_2_Kernel_e_Internals.pdf`** | **152 págs.** | **76 hojas** | **Tomo II · Ramas Especializadas:** Rama Optativa 2D completa (Internals de Windows, Objetos, Procesos, COM/DCOM, RPC/NDR con decodificación `ProcFormatString`/`TypeFormatString`, WMI, IPC, SEH/VEH/WER con slots `UNWIND_CODE`, ETW con sesión `NT Kernel Logger`, formato binario ETL y mitigación de ETW Patching, **Lección 2D.14** subsistema gráfico Win32k y `KeServiceDescriptorTableShadow`, **Lección 2D.15** arranque temprano, UEFI y bootkits con `LOADER_PARAMETER_BLOCK`, y Extensión Hyper-V) y Etapa 6 completa (Drivers WDF/KMDF, tabla `WdfFunctions`, despacho de IOCTLs, depuración KDNET, Minifiltros de sistema de archivos, y **Lección 6.7** con VBS/HVCI en VTL1, Credential Guard con trustlets IUM, validación `NtCreateSection` $\to$ `VtlCall`, callbacks de registro `CmCallbackListHead`, sensor `InstrumentationCallback`, auditoría de `PspCreateProcessNotifyRoutine`, `ObRegisterCallbacks`, `ETWti`, *Double Fetch* en MDLs y mecánicas BYOVD con `PiDDBCacheTable`).<br>*(Anillado metálico Ring Wire / espiral o binder con tapa dura/polipropileno)*. |
| **`Separata_Escritorio.pdf`** | **18 págs.** | **9 hojas** | **Separata de Escritorio (Cheat Sheets y Referencia Rápida):** Cuadernillo de consulta rápida junto al teclado. Contiene: Árbol de Triage Defensivo de 1 pág., Mapa y Anatomía del Formato PE x86/x64, Atajos y comandos de WinDbg, x64dbg, GDB, IDA Pro y Ghidra, Hojas 1 a 5 de tablas de bajo nivel (C++, WinDbg, evasión, criptografía, ARM64EC, VTL1, callbacks de kernel) y Plantilla Forense.<br>*(Anillado metálico Ring Wire / espiral o binder con tapa dura/polipropileno)*. |

### 📑 Volúmenes Consolidados Integrales (Lectura Digital / Tablet)

| Archivo PDF | Páginas | Hojas (doble faz) | Contenido y Propósito |
| :--- | :---: | :---: | :--- |
| **`Tomo_1_Tronco_y_Apoyo.pdf`** | **396 págs.** | **198 hojas** | **Tomo I Íntegro:** Recorrido troncal completo (Etapas 0 a 5, Bloque 2E completo con 2.34 y 2.35, Casos de Estudio, Fichas, Glosario y Repaso) en un solo archivo unificado con índice general consolidado. |
| **`Curso_Reversing_Windows.pdf`** | **546 págs.** | **273 hojas** | **Edición Completa Unificada:** Todo el material de la obra (Tomo I + Tomo II + Separata) integrado en un único volumen con índice temático unificado. |

### 🖨️ Recomendaciones para la Gráfica / Imprenta:
- **Papel de Interiores:** Papel obra de **80 g/m²** (estándar óptimo de imprenta) o chambril/obra de **90 g/m²** para máxima opacidad frente a bloques oscuros de desensamblado.
- **Encuadernación:** Anillado metálico Ring Wire / espiral o binder con tapa dura/polipropileno en los 4 cuadernillos.
- **Formato y escala:** A4 (210 &times; 297 mm), impresión al 100 % de escala (tamaño real, sin reescalar márgenes) a doble faz sobre el borde largo.
- **Ficha de orden de imprenta:** Se incluye la orden formal lista para entregar a la gráfica en **`orden_impresion.pdf`** y **`orden_impresion.png`** (generada a partir de `orden_impresion.html`).

---

## 🌟 Novedades Técnicas e Industriales Incorporadas

La presente edición integra las siguientes áreas avanzadas de ingeniería inversa y seguridad:

1. **Desvirtualización Dinámica y Lifting Simbólico (Lección 2.34):**
   - Pipeline dinámico de desofuscación: trazado de basic blocks con **Frida Stalker**, análisis dinámico de propagación de taint y lifting a AST simbólico con **Triton** (`solve_vm_triton.py`), y simplificación y resolución con **Z3** (`solve_minivm_z3.py`).
   - Detección de *Indirect Threading* (`jmp qword ptr [r12 + rax*8]`) frente al switch tradicional.
   - Especificación completa y funcional de procesador virtual en **SLEIGH** para Ghidra (`minivm.ldefs`, `minivm.pspec`, `minivm.cspec`, `minivm.slaspec`).

2. **Ecosistemas Modernos en Windows 11 (Lección 2.35):**
   - Binarios híbridos **ARM64EC**: `IMAGE_DYNAMIC_RELOCATION_ARM64EC`, thunks `$$h` y mapa de registros mapeados (`RCX..R9` &harr; `X0..X3`).
   - Reversing de **Windows Runtime (WinRT)**: interfaz `IInspectable` (+0x18, +0x20, +0x28), cadenas `HSTRING` (24 bytes) y metadatos ECMA-335 en `.winmd`.
   - Sandboxing con **AppContainer y LPAC**: anatomía del token (`TokenCapabilities`), tabla de SIDs de capacidades (`internetClient`, `privateNetworkClientServer`), y comandos de inspección en WinDbg y Process Hacker.
   - Reversing de **.NET Native AOT** e intercepción de compilación por método en el JIT mediante ganchos en `clrjit.dll!CILJit::compileMethod` (`dump_cil_jit.js`).

3. **Subsistema Gráfico en Modo Kernel (Lección 2D.14):**
   - Arquitectura y modularización de `win32kbase.sys` y `win32kfull.sys`.
   - Despacho de syscalls gráficas (`0x1000+`) mediante `KeServiceDescriptorTableShadow` (tabla de índice 1).
   - Inversión de control y superficie de vulnerabilidades de Use-After-Free con `KeUserModeCallback` (`user32!__ClientLoadLibrary`).
   - Mitigaciones modernas: **Win32k Lockdown** (`ProcessSystemCallDisablePolicy`).

4. **Arranque Temprano, UEFI y Bootkits (Lección 2D.15):**
   - Formato PE32+ de aplicaciones EFI (`IMAGE_SUBSYSTEM_EFI_APPLICATION`).
   - Cadena de arranque en Windows: `bootmgfw.efi` $\to$ `winload.efi` $\to$ `hvloader.efi` $\to$ `ntoskrnl.exe`.
   - Anatomía e inspección en WinDbg de la estructura `LOADER_PARAMETER_BLOCK` en `KiSystemStartup`.
   - Ingeniería inversa de drivers DXE y detección de persistencia previa al kernel (bootkits) en Ghidra e IDA Pro.

5. **Seguridad Profunda en Kernel, Telemetría y BYOVD (Lección 6.7):**
   - Arquitectura **VBS y Secure Kernel**: partición VTL0 (`ntoskrnl.exe`) vs. VTL1 (`securekernel.exe`), transiciones `VtlCall` / `VtlReturn`, kCFG en `nt!guard_dispatch_icall` y cumplimiento de $W \oplus X$ en kernel mediante SLAT / EPT.
   - Auditoría forense en WinDbg de vectores de notificación: arreglo `nt!PspCreateProcessNotifyRoutine` (`EX_FAST_REF`), callbacks de objetos `ObRegisterCallbacks` en `*PsProcessType`, y telemetría `ETWti` (`EtwThreatIntProvRegHandle`).
   - Vulnerabilidades de *Double Fetch* en buffers compartidos con `MmGetSystemAddressForMdlSafe`, y llamadas indirectas KMDF para I/O asíncrona (`WdfRequestSend` y `WdfRequestSetCompletionRoutine`).
   - **Mecánicas BYOVD (Bring Your Own Vulnerable Driver):** abuso de drivers vulnerables firmados para evadir DSE, manipulación de `MmMapIoSpace` / bit SMEP en CR4, y auditoría forense con `nt!PiDDBCacheTable`.

6. **Reconstrucción RPC/NDR y Desenrollado de Excepciones (Lecciones 2D.10 y 2D.11):**
   - Extracción y tipado de rutinas RPC a partir de `MIDL_SERVER_INFO+0x10` (`DispatchTable`), decodificación de `ProcFormatString` y `TypeFormatString`.
   - Decodificación estática del layout binario de `UNWIND_INFO` y slots `UNWIND_CODE` de 2 bytes (`CodeOffset`, `UnwindOp`, `OpInfo`) para auditar Call Stack Spoofing.

7. **Go y Rust en Profundidad (Lección 2.32):**
   - Layout en memoria de `slices` (24 bytes en x64), tablas `hmap`, llamadas a `runtime.newproc`, `chanrecv1` y despacho de `selectgo` en Go.
   - Vtables de `dyn Trait` (destructor, size, align, métodos) y desmantelamiento de máquinas de estado `async/await` (`Future::poll`) en Rust.

8. **Kit Completo de Laboratorios Prácticos (`plantillas_codigo/`):**
   - `gorust_targets/` (`target_go.go` y `target_rust.rs`) con instrucciones de build y stripping.
   - `rpc_com_server_lab.c` y `rpc_com_server_lab.idl` (RPC sobre `ncalrpc` con security callback).
   - `evasion_peb_syscall_lab.c` (PEB walking con hash ROR13, indirect syscalls, VEH y hardware breakpoints Dr0..Dr3).
   - `solve_vm_triton.py` (tracing dinámico con Frida + lifting AST y taint con Triton).
   - `solve_minivm_z3.py` (resolución simbólica de bytecode ofuscado con Z3).
   - `vm_mba_crackme.c` (máquina virtual de prueba con aritmética mixta MBA).
   - `sleigh_minivm/` (módulo de extensión de procesador virtual para Ghidra).
   - `dump_cil_jit.js` (script de Frida para intercepción en tiempo real de compilación CIL en JIT).
   - `minifilter_obcallback_min.c` (driver educativo para intercepción de procesos y filtrado de I/O).
   - `auditar_callbacks.wdbg` (script para volcado y análisis forense de callbacks de kernel en WinDbg).

---

## 📌 Estado de la Versión

- **Edición:** 5
- **Revisión:** 5.4 (Estándar Industrial Consolidado)
- **Fecha:** 30 de octubre de 2026
- **Estado de Compilación:** Aprobado (0 problemas de paginación, 0 destinos TOC rotos en todos los volúmenes, paridad par garantizada para doble faz).
