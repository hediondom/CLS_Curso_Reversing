# Curso de Reversing e Ingeniería Inversa en Windows
### Paquete de Estudio Autónomo y Referencia Defensiva en Español

**Edición 5 · Revisión 5.4 (Estándar Industrial Consolidado)** (30 de octubre de 2026)  
Obra comunitaria, abierta e independiente para el estudio defensivo y riguroso de ingeniería inversa en plataformas Windows.

---

## 🚀 Inicio Rápido (Navegación Web Offline)

Para estudiar desde el navegador, abrí **`00_EMPEZAR_AQUI.html`** o **`index.html`** en cualquier navegador web.  
Funciona 100% sin conexión a internet y da acceso a:
- Portada, metodología de estudio y recorrido estructurado por etapas.
- Buscador temático offline (`buscar.html`).
- 48 lecciones base + 14 lecciones avanzadas de Kernel (Rama 2D y Etapa 6) y extensión Hyper-V.
- 69 tutoriales ilustrados de IDA Pro (`ida_tutes/`).
- Kit completo de plantillas C/C++ y scripts de laboratorio (`src/` y `plantillas_codigo/`).
- Fichas de herramientas, glosario técnico y preguntas/respuestas de autoevaluación.

---

## 📚 Materiales Impresos y Formato PDF (Revisión 5.4 Consolidada)

El material está optimizado para lectura digital e impresión profesional en gráfica (formato A4, márgenes simétricos para anillado o encuadernación rústica pegada al lomo, control estricto de orfandad, paridad para doble faz y contraste optimizado).

### 🖨️ Cuadernillos de Impresión Recomendados (Distribución Práctica)

Para facilitar la manipulación física y el uso diario en el escritorio, la obra se distribuye en 4 cuadernillos independientes de lomo equilibrado:

| Archivo PDF | Páginas | Hojas (doble faz) | Encuadernación / Contenido |
| :--- | :---: | :---: | :--- |
| **`Tomo_1_Parte_A_pags_1-172.pdf`** | **172 págs.** | **86 hojas** | **Tomo I · Parte A:** Fundamentos de arquitectura x86/x64, ciclo de vida del PE y DLLs (Loader Lock), desensamblado estático (IDA Pro / Ghidra), depuración dinámica táctica con x64dbg (breakpoints `$ptr`), y análisis de anti-análisis y packers (Etapas 0 a 2C).<br>*(Anillado metálico Ring Wire / espiral o binder con tapa dura/polipropileno)*. |
| **`Tomo_1_Parte_B_pags_173-388.pdf`** | **216 págs.** | **108 hojas** | **Tomo I · Parte B:** C++ moderno en bajo nivel (vtables, RTTI, SSO, Smart Pointers, `std::function`), WinDbg y análisis de Heap, .NET/CLR, Criptografía híbrida (CryptoAPI vs. CNG), Metodología de Triage de 5 pasos, Bloque 2E avanzado (angr/Z3, VM bytecode, protectores multicapa, Go y Rust con layouts de slices/async, VB6 p-code), **Lección 2.34** (desvirtualización y SLEIGH completo), **Lección 2.35** (ARM64EC, WinRT `IInspectable` y Native AOT con JIT Hooking), Casos prácticos y Apoyo (Glosario, Q&A, Fichas).<br>*(Anillado metálico Ring Wire / espiral o binder con tapa dura/polipropileno)*. |
| **`Tomo_2_Kernel_e_Internals.pdf`** | **136 págs.** | **68 hojas** | **Tomo II · Ramas Especializadas:** Rama Optativa 2D completa (Internals de Windows, Objetos, Procesos, COM/DCOM, RPC/NDR, WMI, IPC, SEH/VEH, ETW y Extensión Hyper-V) y Etapa 6 completa (Drivers WDF/KMDF, tabla `WdfFunctions`, despacho de IOCTLs, depuración KDNET, Minifiltros de sistema de archivos y **Lección 6.7** con VBS/HVCI en VTL1, auditoría de `PspCreateProcessNotifyRoutine`, `ObRegisterCallbacks`, `ETWti` y *Double Fetch* en MDLs).<br>*(Anillado metálico Ring Wire / espiral o binder con tapa dura/polipropileno)*. |
| **`Separata_Escritorio.pdf`** | **18 págs.** | **9 hojas** | **Separata de Escritorio (Cheat Sheets y Referencia Rápida):** Cuadernillo de consulta rápida junto al teclado. Contiene: Árbol de Triage Defensivo de 1 pág., Mapa y Anatomía del Formato PE x86/x64, Atajos y comandos de WinDbg, x64dbg, GDB, IDA Pro y Ghidra, Hojas 1 a 5 de tablas de bajo nivel (C++, WinDbg, evasión, criptografía, ARM64EC, VTL1, callbacks de kernel) y Plantilla Forense.<br>*(Anillado metálico Ring Wire / espiral o binder con tapa dura/polipropileno)*. |

### 📑 Volúmenes Consolidados Integrales (Lectura Digital / Tablet)

| Archivo PDF | Páginas | Hojas (doble faz) | Contenido y Propósito |
| :--- | :---: | :---: | :--- |
| **`Tomo_1_Tronco_y_Apoyo.pdf`** | **388 págs.** | **194 hojas** | **Tomo I Íntegro:** Recorrido troncal completo (Etapas 0 a 5, Bloque 2E completo con 2.34 y 2.35, Casos de Estudio, Fichas, Glosario y Repaso) en un solo archivo unificado con índice general consolidado. |
| **`Curso_Reversing_Windows.pdf`** | **522 págs.** | **261 hojas** | **Edición Completa Unificada:** Todo el material de la obra (Tomo I + Tomo II + Separata) integrado en un único volumen con índice temático unificado. |

### 🖨️ Recomendaciones para la Gráfica / Imprenta:
- **Papel de Interiores:** Papel obra de **80 g/m²** (estándar óptimo de imprenta) o chambril/obra de **90 g/m²** para máxima opacidad frente a bloques oscuros de desensamblado.
- **Encuadernación:** Anillado metálico Ring Wire / espiral o binder con tapa dura/polipropileno en los 4 cuadernillos.
- **Formato y escala:** A4 (210 &times; 297 mm), impresión al 100 % de escala (tamaño real, sin reescalar márgenes) a doble faz sobre el borde largo.
- **Ficha de orden de imprenta:** Se incluye la orden formal lista para entregar a la gráfica en **`orden_impresion.pdf`** y **`orden_impresion.png`** (generada a partir de `orden_impresion.html`).

---

## 🌟 Novedades Técnicas e Industriales Incorporadas

La presente edición integra las siguientes áreas avanzadas de ingeniería inversa y seguridad:

1. **Desvirtualización y Lifting Simbólico (Lección 2.34):**
   - Detección de *Indirect Threading* (`jmp qword ptr [r12 + rax*8]`) frente al switch tradicional.
   - Lifting simbólico con **Z3 / Python** (`solve_minivm_z3.py`) para colapsar expresiones *Mixed Boolean-Arithmetic* (MBA).
   - Especificación completa de procesador virtual en **SLEIGH** para Ghidra (`.ldefs`, `.pspec`, `.cspec`, `.slaspec`).

2. **Ecosistemas Modernos en Windows 11 (Lección 2.35):**
   - Binarios híbridos **ARM64EC**: `IMAGE_DYNAMIC_RELOCATION_ARM64EC`, thunks `$$h` y mapa de registros mapeados (`RCX..R9` &harr; `X0..X3`).
   - Reversing de **Windows Runtime (WinRT)**: interfaz `IInspectable` (+0x18, +0x20, +0x28), cabeceras `HSTRING` (24 bytes) y sandboxing con tokens AppContainer / LPAC.
   - Reversing de **.NET Native AOT** e intercepción de compilación por método en el JIT mediante ganchos en `clrjit.dll!CILJit::compileMethod` (`dump_cil_jit.js`).

3. **Seguridad Profunda en Modo Kernel (Lección 6.7):**
   - Arquitectura **VBS y Secure Kernel**: partición VTL0 (`ntoskrnl.exe`) vs. VTL1 (`securekernel.exe`), transiciones `VtlCall` / `VtlReturn`, kCFG en `nt!guard_dispatch_icall` y cumplimiento de $W \oplus X$ en kernel mediante SLAT / EPT.
   - Auditoría forense en WinDbg de vectores de notificación: arreglo `nt!PspCreateProcessNotifyRoutine` (`EX_FAST_REF`), callbacks de objetos `ObRegisterCallbacks` en `*PsProcessType`, y telemetría `ETWti` (`EtwThreatIntProvRegHandle`).
   - Vulnerabilidades de *Double Fetch* en buffers compartidos con `MmGetSystemAddressForMdlSafe`, y llamadas indirectas KMDF para I/O asíncrona (`WdfRequestSend` en +0x8E8 y `WdfRequestSetCompletionRoutine` en +0x910).

4. **Go y Rust en Profundidad (Lección 2.32):**
   - Layout en memoria de `slices` (24 bytes en x64), tablas `hmap`, llamadas a `runtime.newproc`, `chanrecv1` y despacho de `selectgo` en Go.
   - Vtables de `dyn Trait` (destructor, size, align, métodos) y desmantelamiento de máquinas de estado `async/await` (`Future::poll`) en Rust.

---

## 📌 Estado de la Versión

- **Edición:** 5
- **Revisión:** 5.4 (Estándar Industrial Consolidado)
- **Fecha:** 30 de octubre de 2026
- **Estado de Compilación:** Aprobado (0 problemas de paginación, 0 destinos TOC rotos en todos los volúmenes, paridad par garantizada para doble faz).
