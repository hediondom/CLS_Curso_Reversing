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
- 46 lecciones base + 13 lecciones avanzadas de Kernel (Rama 2D) y extensión Hyper-V.
- 69 tutoriales ilustrados de IDA Pro (`ida_tutes/`).
- 7 plantillas de código listas para compilar (`src/`).
- Fichas de herramientas, glosario técnico y preguntas/respuestas de autoevaluación.

---

## 📚 Materiales Impresos y Formato PDF (Revisión 5.4)

El material está optimizado para lectura digital e impresión profesional en gráfica (formato A4, márgenes simétricos para anillado o encuadernación rústica pegada al lomo, control estricto de orfandad, paridad para doble faz y contraste optimizado).

### 🖨️ Cuadernillos de Impresión Recomendados (Distribución Práctica)

Para facilitar la manipulación física y el uso diario en el escritorio, la obra se distribuye en 4 cuadernillos independientes de lomo equilibrado:

| Archivo PDF | Páginas | Hojas (doble faz) | Encuadernación / Contenido |
| :--- | :---: | :---: | :--- |
| **`Tomo_1_Parte_A_pags_1-172.pdf`** | **172 págs.** | **86 hojas** | **Tomo I · Parte A:** Fundamentos de arquitectura x86/x64, ciclo de vida del PE y DLLs, desensamblado estático (IDA Pro / Ghidra), depuración dinámica táctica con x64dbg (breakpoints `$ptr`), y análisis de anti-análisis y packers (Etapas 0 a 2C).<br>*(Anillado metálico Ring Wire / espiral o binder con tapa dura/polipropileno)*. |
| **`Tomo_1_Parte_B_pags_173-380.pdf`** | **208 págs.** | **104 hojas** | **Tomo I · Parte B:** C++ moderno en bajo nivel (vtables, RTTI, SSO, Smart Pointers, `std::function`), WinDbg y análisis de Heap, .NET/CLR, Criptografía híbrida (CryptoAPI vs. CNG con discrepancia de endianness), Metodología de Triage de 5 pasos, Bloque 2E avanzado (angr/Z3, VM bytecode, protectores multicapa, Go/Rust a bajo nivel, VB6 p-code), Casos prácticos y Material de Apoyo (Glosario, Q&A, Fichas de recursos).<br>*(Anillado metálico Ring Wire / espiral o binder con tapa dura/polipropileno)*. |
| **`Tomo_2_Kernel_e_Internals.pdf`** | **132 págs.** | **66 hojas** | **Tomo II · Ramas Especializadas:** Rama Optativa 2D completa (Internals de Windows, Objetos del Kernel, Procesos, COM/DCOM, RPC, WMI, IPC, SEH/VEH, ETW y Extensión Hyper-V) y Etapa 6 completa (Arquitectura de Drivers WDF/KMDF, tabla `WdfFunctions`, despacho de IOCTLs, depuración de Kernel con WinDbg/KDNET y Minifiltros de sistema de archivos).<br>*(Anillado metálico Ring Wire / espiral o binder con tapa dura/polipropileno)*. |
| **`Separata_Escritorio.pdf`** | **18 págs.** | **9 hojas** | **Separata de Escritorio (Cheat Sheets y Referencia Rápida):** Cuadernillo de consulta rápida junto al teclado. Contiene: Árbol de Triage Defensivo de 1 pág., Mapa y Anatomía del Formato PE x86/x64, Atajos y comandos de WinDbg, x64dbg, GDB, IDA Pro y Ghidra, Hojas 1 a 5 de tablas de bajo nivel (C++, WinDbg, evasión, criptografía, drivers) y Plantilla Forense.<br>*(Anillado metálico Ring Wire / espiral o binder con tapa dura/polipropileno)*. |

### 📑 Volúmenes Consolidados Integrales (Lectura Digital / Tablet)

| Archivo PDF | Páginas | Hojas (doble faz) | Contenido y Propósito |
| :--- | :---: | :---: | :--- |
| **`Tomo_1_Tronco_y_Apoyo.pdf`** | **380 págs.** | **190 hojas** | **Tomo I Íntegro:** Recorrido troncal completo (Etapas 0 a 5, Bloque 2E, Casos de Estudio, Fichas, Glosario y Repaso) en un solo archivo unificado con índice general consolidado. |
| **`Curso_Reversing_Windows.pdf`** | **530 págs.** | **265 hojas** | **Edición Completa Unificada:** Todo el material de la obra (Tomo I + Tomo II + Separata) integrado en un único volumen con índice temático unificado. |

### 🖨️ Recomendaciones para la Gráfica / Imprenta:
- **Papel de Interiores:** Papel obra de **80 g/m²** (estándar óptimo de imprenta) o chambril/obra de **90 g/m²** para máxima opacidad frente a bloques oscuros de desensamblado.
- **Encuadernación:** Anillado metálico Ring Wire / espiral o binder con tapa dura/polipropileno en los 4 cuadernillos.
- **Formato y escala:** A4 (210 &times; 297 mm), impresión al 100 % de escala (tamaño real, sin reescalar márgenes) a doble faz sobre el borde largo.
- **Ficha de orden de imprenta:** Se incluye la orden formal lista para entregar a la gráfica en **`orden_impresion.pdf`** y **`orden_impresion.png`** (generada a partir de `orden_impresion.html`).

---

## 🌟 Novedades Técnicas Incorporadas en la Versión 5.4 (Estándar Industrial)

En respuesta a la auditoría técnica experta y a los estándares contemporáneos de análisis de software en Windows, la Revisión 5.4 integró las siguientes precisiones de bajo nivel:

1. **Evolución de Evasión: Indirect Syscalls, Call Stack Walking y Call Stack Spoofing (Lección 2.15):**
   - Justificación de por qué las *Direct Syscalls* fallan ante telemetría de kernel moderna: ETWti (*Microsoft-Windows-Threat-Intelligence*) e *Instrumentation Callbacks* que comprueban si el `RIP` proviene de memoria privada o `.text` legítima.
   - Implementación táctica de **Indirect Syscalls**: salto (`jmp`) a la instrucción `syscall; ret` legítima dentro de `ntdll.dll` para legitimar el puntero de instrucción.
   - Verificación estática y dinámica de Call Stack Spoofing mediante tablas `.pdata`/`UNWIND_INFO`: validación del byte previo `ReturnAddress - N` frente a opcodes de llamada válidos (`CALL rel32` / `CALL r/m64`).
   - Detección de *Tartarus' Gate* (resolución de SSN cuando los stubs tienen ganchos desplazados al byte `+3`).

2. **La Trampa del Endianness en CNG vs. CryptoAPI y Script de Reconstrucción en Python (Lección 4.2):**
   - Cuadro comparativo de *magic bytes* en CNG (`BCRYPT_RSAPUBLIC_MAGIC = "RSA1"`, `BCRYPT_ECCPUBLIC_MAGIC = "ECK1"` / `"ECS1"` para curvas P-256).
   - Detalle de bajo nivel: **CryptoAPI clásica almacena el módulo en Little-Endian, mientras que CNG lo hace en Big-Endian**.
   - Script funcional de conversión en Python (`PyCryptodome`) para reconstruir claves públicas `.pem` a partir de volcados de memoria invirtiendo el *endianness*.
   - Reconocimiento visual del OID de RSA en estructuras ASN.1 DER (`30 82 .. 30 0D 06 09 2A 86 48 86 F7 0D 01 01 01`).

3. **Doble Breakpoint en x64dbg para Funciones In-Place y Niche Optimization en Rust (Lecciones 2.6 y 2.13):**
   - Técnica de doble breakpoint encadenado con variable de usuario en x64dbg para rutinas `void decodificar(char* buf)`: `$ptr = rcx` en el prólogo y registro `{utf8@$ptr}` en el `ret`, sorteando la sobreescritura de registros volátiles.
   - Recomendación de plugins tácticos esenciales: **ScyllaHide**, **xAnalyzer** y **OllyDumpEx**.
   - *Niche Optimization* en Rust: supresión del byte discriminante `tag` en tipos que garantizan no-nulidad (`Option<&T>`, `Option<Box<T>>`, `Option<NonZeroU32>`), traduciéndose en desensamblado como una simple comprobación de puntero nulo (`test rax, rax ; jz es_none`).

4. **Ampliaciones de Arquitectura en Drivers, C++ Moderno y Servicios Windows:**
   - **Resolución de la tabla `WdfFunctions` en KMDF sin símbolos (Lección 6.4):** Localización estática y dinámica de índices y offsets para `WdfDriverCreate` (+0x3B0), `WdfIoQueueCreate` (+0x4C0), `WdfDeviceCreate` e inspección de `EvtIoDeviceControl` (+0x28).
   - **Anatomía de `DllMain`, Loader Lock y DLL Sideloading (Lección 2.14):** Invocación bajo `LdrpCallInitRoutine`, riesgos de interbloqueo (*deadlock*) con `LoadLibrary`/`CoInitializeEx`, breakpoints en el EntryPoint de la DLL y análisis de entradas *Export Forwarding* en `.edata`.
   - **Estructuras Modernas de C++ en MSVC x64 (Lección 2.18):** Patrones de desensamblado para `std::unique_ptr` (8 bytes), `std::shared_ptr` (16 bytes con bloque de control `_Ref_count_base`) y `std::function` (64 bytes con Small Functor Optimization y tabla `_Impl_base`).
   - **Desofuscación Dinámica en .NET y Carga Reflexiva (Lección 3.2):** Intercepción de `Assembly.Load(byte[])` en memoria a través de `amsi.dll!AmsiScanBuffer` o `clrjit.dll!compileMethod`.
   - **Plantilla de Laboratorio: Servicio Windows Mínimo (`svclab_min.c`):** Implementación completa de `ServiceMain`, `RegisterServiceCtrlHandler`, reporte de estados ante el SCM y depuración con WinDbg / x64dbg.

---

## 📌 Estado de la Versión

- **Edición:** 5
- **Revisión:** 5.4 (Estándar Industrial Consolidado)
- **Fecha:** 30 de octubre de 2026
- **Estado de Compilación:** Aprobado (0 problemas de paginación, 0 destinos TOC rotos en todos los volúmenes, paridad par garantizada para doble faz).
