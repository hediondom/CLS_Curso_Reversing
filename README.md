# Curso de Reversing e Ingeniería Inversa en Windows — Trilogía Completa

Guía profesional y exhaustiva de ingeniería inversa, reversing de binarios, seguridad interna del sistema operativo y análisis defensivo en sistemas Windows (x86, x64, ARM64EC, Kernel NT y arquitectura de virtualización). Diseñada para analistas de malware, investigadores de seguridad, auditores de código de bajo nivel y profesionales de ciberseguridad.

---

## 🧭 Estructura General de la Trilogía

La obra se organiza en **tres tomos complementarios**, una **separata de referencia rápida** para el escritorio y un **volumen maestro digital consolidado**:

1. **Tomo I · Tronco y Apoyo (Fundamentos a Especialización — 410 págs.):**
   - **Etapa 0:** Entorno de laboratorio aislado, herramientas y metodología segura.
   - **Etapa 1:** Fundamentos de bajo nivel, representación numérica, memoria, stack, ciclo de vida de procesos y formato PE.
   - **Etapa 2:** Dominio del desensamblado y depuración (IDA Pro, Ghidra, x64dbg, WinDbg), flujo de control, llamadas, optimizaciones del compilador, TLS callbacks, MFC, packers didácticos y taxonomía anti-análisis.
   - **Bloque 2E Avanzado:** C++ moderno (vtables, RTTI, smart pointers), WinDbg y heap, desvirtualización dinámica (Frida Stalker + Triton AST + Z3), procesador SLEIGH para Ghidra, reversing profundo de Go y Rust (layouts de slices y máquinas async), VB6/p-code, ARM64EC, WinRT y sandboxing AppContainer/LPAC.
   - **Etapa 3:** Reversing de aplicaciones .NET y CLR (CIL/MSIL, descompilación y ganchos JIT).
   - **Etapa 4:** Práctica guiada, reconocimiento de algoritmos criptográficos (CryptoAPI vs. CNG), formatos binarios y protocolos de red.
   - **Etapa 5:** Ramas profesionales: ingeniería inversa de malware, análisis de vulnerabilidades y automatización.
   - **Material de Apoyo:** Kit de 15 plantillas de código C/C++, 6 hojas de referencia rápida, glosario técnico y fuentes verificables.

2. **Tomo II · Kernel, Drivers e Internals (Modo Núcleo y Arquitectura Windows — 198 págs.):**
   - **Etapa 6 (Kernel y Drivers):** Arquitectura del kernel NT, modelo de paquetes I/O (IRP), driver propio KMDF con IOCTL inocuo, depuración con WinDbg (KDNET, bugchecks, Special Pool a nivel PTE), análisis defensivo de drivers, minifiltros del sistema de archivos (`FLTMGR`), mitigaciones del kernel, seguridad profunda (VBS, HVCI, trustlets IUM, callbacks `PspCreateProcessNotifyRoutine` y `ObRegisterCallbacks`, telemetría `ETWti`, *Double Fetch* en MDLs y mecánicas BYOVD con `PiDDBCacheTable`).
   - **Nuevas Lecciones de Modo Núcleo (Fase 2):**
     - **6.8:** *Windows Filtering Platform (WFP)*: capas ALE, arbitraje de red y callouts de inspección profunda (`FWPS_CALLOUT`, `classifyFn`, `netsh wfp`).
     - **6.9:** *kCFG a nivel ISA*: bitmap de control de flujo, indexación en VTL1 y contraste con Intel CET/IBT (`endbr64`).
     - **6.10:** *Fuzzing de Drivers en Modo Kernel*: decodificación de `CTL_CODE`, harness Win32/C++, triaje de bugcheck `0xD6` (*Driver Page Fault Beyond End of Allocation*) y arquitecturas de snapshot fuzzing (WTF y kAFL/Nyx).
   - **Rama 2D (Windows Internals y Virtualización):** Objetos y tokens de seguridad, loader de Windows, arquitectura del Registro, Servicios (SCM), Task Scheduler, COM/DCOM y RPC/NDR (`ProcFormatString`/`TypeFormatString`), WMI, IPC/ALPC, manejo de excepciones x64 (.pdata, SEH, VEH, slots `UNWIND_CODE`), subsistema gráfico `win32k` (`KeServiceDescriptorTableShadow`), cadena de arranque UEFI (`bootmgfw.efi`, `winload.efi`, `LOADER_PARAMETER_BLOCK`) y bootkits.
   - **Nuevas Lecciones de Internals (Fase 2):**
     - **2D.16:** *Hyper-V, Particiones y VMBus*: arquitectura hipervisor Type-1, partición raíz vs. invitadas, sintéticos VSC/VSP y canales VMBus.
     - **2D.17:** *Arquitectura Profunda de VBS, Secure Kernel y HVCI*: VTL0 frente a VTL1, llamada segura `VtlCall`, validación de integridad de código y aislamiento SLAT/EPT.
   - **Anexo A:** Fe de erratas técnica consolidada y fichas forenses de verificación.

3. **Tomo III · Paradigmas Modernos, Hardware ISA, Aislamiento e IA (52 págs.):**
   - **Módulo 1:** Paradigmas Modernos de Compilación: LLVM, Clang-cl vs. MSVC cl.exe, optimizaciones de Switch Lowering (LUTs vs. árboles binarios), auto-vectorización AVX2, Clang CFI (*Forward-Edge Control Flow Integrity*) frente a Microsoft kCFG, y reversing de Rust endurecido (`lto=fat`, `panic=abort`, `strip`, reconstrucción de `&str` y slices).
   - **Módulo 2:** Aislamiento por Contenedores: AppContainer vs. Less Privileged AppContainer (LPAC), auditoría forense de tokens (bit `0x20` en `TokenFlags`), SID `S-1-15-3-*`, MSIX y frontera de virtualización WSL2 (`AF_UNIX` y VMBus).
   - **Módulo 3:** Extensiones del Hardware ISA: Intel CET (*Control-flow Enforcement Technology*), Shadow Stack a nivel de microcódigo (`INCSSP`, `RDSSP`), contraste entre excepción `#CP` y fast-fail `0xC0000409`, detección de Call Stack Spoofing en la pila sombra, y binarios ARM64EC en el desensamblador.
   - **Módulo 4:** Reversing Aumentado por IA Local: Principio de soberanía y confidencialidad en ingeniería inversa, infraestructura offline con Ollama (DeepSeek-Coder, CodeLlama), integración con PyGhidra e IDA Pro, y principio de falsabilidad estricta ante alucinaciones.
   - **Módulo 5:** Catálogo de 5 plantillas C/Rust/Python de laboratorio y bitácora técnica de verificación editorial.

---

## 📚 Especificaciones de Impresión y Distribución Física

Todos los volúmenes están maquetados con **paridad par estricta** (número par de páginas, sin hojas impares ni páginas blancas descolocadas), márgenes simétricos optimizados para anillado metálico Ring Wire de paso 3:1 / 2:1 y tipografía de alto contraste con código en negro puro (`#111111` / `-webkit-text-fill-color: #111111`).

### 🖨️ Los 5 Volúmenes Físicos para Imprenta

Para evitar sobrecargar los lomos y asegurar un paso de hoja completamente fluido en anillado metálico, la obra física se distribuye en **5 cuadernillos independientes**:

| Volumen | Archivo PDF en el Repositorio / Pendrive | Páginas | Hojas (Doble Faz) | Encuadernación Recomendada |
| :--- | :--- | :---: | :---: | :--- |
| **1. Tomo I — Parte A** | `Tomo_1_Parte_A_pags_1-178.pdf` | **178 págs.** | **89 hojas** | Anillado metálico Ring Wire con tapa dura/polipropileno |
| **2. Tomo I — Parte B** | `Tomo_1_Parte_B_pags_179-410.pdf` | **232 págs.** | **116 hojas** | Anillado metálico Ring Wire con tapa dura/polipropileno |
| **3. Tomo II** | `Tomo_2_Kernel_e_Internals.pdf` | **198 págs.** | **99 hojas** | Anillado metálico Ring Wire con tapa dura/polipropileno |
| **4. Tomo III** | `Tomo_3_LLVM_Rust_Contenedores_IA.pdf` | **52 págs.** | **26 hojas** | Anillado metálico Ring Wire con tapa dura/polipropileno |
| **5. Separata de Escritorio** | `Separata_Escritorio.pdf` | **18 págs.** | **9 hojas** | Anillado fino o cuadernillo abrochado a caballete |
| **TOTAL FÍSICO** | **5 volúmenes encuadernados** | **678 págs.** | **339 hojas** | **100 % Paridad Par (Doble Faz)** |

### 📑 Volumen Maestro Digital Unificado (Lectura en Pantalla / Tablet)

| Archivo PDF | Páginas | Hojas equiv. | Propósito |
| :--- | :---: | :---: | :--- |
| **`CLS_Curso_Reversing.pdf`** | **660 págs.** | **330 hojas** | **Trilogía Maestra Consolidada:** Unifica los tres tomos en un solo archivo con navegación jerárquica por marcadores (*bookmarks*). Ideal para lectura en tablet, búsqueda global de texto y archivo bibliotecario. **(No requiere impresión física si se imprimen los 5 tomos desglosados)**. |
| **`Tomo_1_Tronco_y_Apoyo.pdf`** | **410 págs.** | **205 hojas** | Tomo I completo continuo de consulta técnica. |

### 📄 Parámetros Técnicos para el Taller de Imprenta
- **Papel:** Papel obra blanco de **80 g/m²** (estándar óptimo de lectura).
- **Formato y escala:** Hoja A4 (210 &times; 297 mm), impresión al **100 % de escala** (tamaño real, sin reducir ni ajustar márgenes al área imprimible).
- **Modo:** Doble faz (dúplex) sobre el **borde largo** (giro lateral / *duplex long-edge*).
- **Tapas:** Tapa transparente de polipropileno cristal al frente y contratapa opaca atrás.
- **Ficha técnica:** La orden formal para el operador de imprenta se encuentra en **`orden_impresion.pdf`**, **`orden_impresion.png`** y **`orden_impresion.html`**.

---

## 🧪 Laboratorios y Plantillas de Código (`plantillas_codigo/`)

El repositorio incluye un conjunto exhaustivo de plantillas educativas en C, C++, Rust, Python, SLEIGH y WinDbg listas para compilar y analizar:

1. **Evasión y Shellcode:** `evasion_peb_syscall_lab.c` (PEB walking con hash ROR13, indirect syscalls, VEH y hardware breakpoints Dr0..Dr3).
2. **RPC y Componentes:** `rpc_com_server_lab.c` y `rpc_com_server_lab.idl` (RPC sobre `ncalrpc` con security callback y formato NDR).
3. **Máquinas Virtuales y Desvirtualización:** `vm_mba_crackme.c` (máquina virtual con aritmética mixta MBA), `solve_vm_triton.py` (tracing dinámico con Frida y lifting a Triton AST) y `solve_minivm_z3.py` (resolución simbólica de bytecode con Z3).
4. **SLEIGH para Ghidra:** `sleigh_minivm/` (`minivm.ldefs`, `minivm.pspec`, `minivm.cspec`, `minivm.slaspec`).
5. **.NET e Intercepción JIT:** `dump_cil_jit.js` (script de Frida para volcado en vivo de métodos compilados por `clrjit.dll`).
6. **Binarios Go y Rust:** `gorust_targets/` (`target_go.go` y `target_rust.rs`) con scripts de compilación optimizada y stripping.
7. **Modo Núcleo y Minifiltros:** `minifilter_obcallback_min.c` (driver educativo para intercepción de procesos y filtrado de I/O) y `auditar_callbacks.wdbg` (script WinDbg para inspección de arrays de callbacks).
8. **Plantillas del Tomo III (`_trabajo/src/tomo3/plantillas/`):**
   - `plantilla_17a_clang_cfi.cpp`: Clang Forward-Edge CFI (`-fsanitize=cfi-icall`).
   - `plantilla_17b_msvc_kcfg.cpp`: Microsoft Control Flow Guard (`/guard:cf`).
   - `plantilla_18_rust_hardened.rs`: Rust con LTO fat, panic abort y disección de slices.
   - `plantilla_19_lpac_audit.c`: Creación de AppContainer con LPAC y auditoría de token.
   - `plantilla_20_cet_ssp.c`: Demostración de Shadow Stack Intel CET con opcodes `INCSSP`/`RDSSP`.
   - `ghidra_ai_analyst.py`: Script de asistencia con LLM local para PyGhidra.

---

## 🛠️ Herramientas de Compilación Automatizada

El proyecto cuenta con scripts en Python para la regeneración y verificación de la suite:

- `construir_tomo2.py`: Compila y pagina el Tomo II (198 págs.) a partir de sus fuentes HTML con tipografía canónica y alto contraste.
- `construir_tomo3.py`: Compila y valida el Tomo III (52 págs.) a partir de sus especificaciones técnicas y módulos Markdown.
- `generar_cls_curso_reversing.py`: Genera el archivo maestro unificado `CLS_Curso_Reversing.pdf` (660 págs.) concatenando los tomos con árboles de marcadores sincronizados.
- `generar_orden_impresion.py`: Renderiza `orden_impresion.html` a PDF y PNG mediante Chrome Headless.
- `sincronizar_y_limpiar.py`: Distribuye los binarios finales hacia el pendrive (`E:\`), el espejo local (`D:\Guia\CLS_Guia_Gemini`) y el directorio de artefactos, depurando copias obsoletas.

---

## 📌 Estado de la Obra

- **Edición:** Trilogía Completa (Tomos I, II y III)
- **Revisión:** 5.5 (Estándar Industrial y Editorial Consolidado)
- **Fecha:** Noviembre de 2026
- **Total Físico de Imprenta:** 678 páginas (339 hojas doble faz en 5 volúmenes)
- **Total Digital Maestro:** 660 páginas (330 hojas unificadas)
- **Estado de Auditoría:** 100 % aprobado (0 destinos rotos, 0 errores de maquetación, paridad par garantizada, alto contraste verificado).
