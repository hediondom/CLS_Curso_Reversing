# CLS — Curso de Reversing
### Paquete de Estudio Autónomo y Referencia Defensiva en Español

**Edición 5 · Revisión 5.4 (Estándar Industrial Consolidado)** (30 de octubre de 2026)  
Basado y ampliado a partir del proyecto educativo CLS.

---

## 🚀 Inicio Rápido (Navegación Web Offline)

Para estudiar desde el navegador, abrí **`00_EMPEZAR_AQUI.html`** o **`index.html`** en cualquier navegador web.  
Funciona 100% sin conexión a internet y da acceso a:
- Portada, metodología de estudio y recorrido por etapas.
- Buscador temático offline (`buscar.html`).
- 46 lecciones base + 13 lecciones avanzadas de Kernel (Rama 2D) y extensión Hyper-V.
- 69 tutoriales ilustrados de IDA Pro (`ida_tutes/`).
- Fichas de herramientas, glosario técnico y preguntas/respuestas de autoevaluación.

---

## 📚 Materiales Impresos y Formato PDF (Revisión 5.4)

El material está optimizado para lectura digital e impresión profesional en gráfica (formato A4, márgenes simétricos para anillado o encuadernación rústica pegada al lomo, control estricto de orfandad, paridad para doble faz y contraste optimizado):

| Archivo PDF | Páginas / Hojas | Contenido y Propósito |
| :--- | :---: | :--- |
| **`CLS_Tomo_1_Tronco_y_Apoyo.pdf`** | **338 págs.**<br>(169 hojas doble faz) | **Tomo I — Tronco Principal y Apoyo (Consolidado 10/10):** Recorrido troncal completo (Etapas 0 a 5: Fundamentos x86/x64, PE y DLLs, Desensamblado con IDA/Ghidra, x64dbg táctico con doble breakpoint `$ptr`, Reversing de Go y Rust con Niche Optimization, Indirect Syscalls y Call Stack Spoofing, Inyección en memoria, Criptografía híbrida y discrepancia de Endianness en CNG vs. CryptoAPI con script Python, C++ profundo con VTables, WinDbg/Heap, .NET, Triage de 5 pasos), 3 Casos de Estudio transversales, Fichas de Recursos, Glosario y Repaso Q&A. |
| **`CLS_Tomo_2_Kernel_e_Internals.pdf`** | **120 págs.**<br>(60 hojas doble faz) | **Tomo II — Ramas Especializadas (Kernel e Internals):** Portada, Rama Optativa 2D completa (Arquitectura interna de Windows, Objetos, Procesos, COM/DCOM, RPC, WMI, IPC, SEH/VEH, ETW y Extensión Hyper-V) y Etapa 6 completa (Drivers WDF/KMDF, IOCTLs, Depuración de Kernel con WinDbg/KDNET y Minifiltros). |
| **`CLS_Separata_Escritorio.pdf`** | **14 págs.**<br>(7 hojas doble faz) | **Separata de Escritorio (Cheat-Sheets de Consulta):** Cuadernillo para tener junto al teclado. Incluye: Árbol de Triage Defensivo (1 pág.), Anatomía y Mapa del Formato PE x86/x64, Atajos/Comandos de WinDbg, x64dbg, GDB, IDA Pro y Ghidra, Tabla de Registro de Decisiones y Plantilla de Informe Técnico Forense. |
| **`CLS_Curso_Reversing_v5.4_Ampliada.pdf`**<br>*(o `CLS_Curso_Reversing.pdf`)* | **454 págs.**<br>(227 hojas doble faz) | **Edición Completa Consolidada:** Todo el material del curso en un solo volumen integrado con índice general unificado. |

### 🖨️ Recomendaciones para la Gráfica / Imprenta:
- **Interiores Tomo I y II:** Papel obra / chambril de **90 g/m²** (u 80 g/m² estándar). El gramaje de 90 g/m² garantiza máxima opacidad para evitar que trasluzcan los bloques oscuros de código y tablas en la impresión doble faz.
- **Separata de Escritorio:** Papel obra de **90 g/m²** o papel ilustración mate / obra grueso de **120–150 g/m²** para mayor rigidez y durabilidad durante el uso diario.
- **Tapas y Contratapas:** Cartulina o ilustración de **250–300 g/m²** con laminado mate/brillante (encuadernación rústica pegada al lomo o anillado ring-wire).

---

## 🌟 Novedades Incorporadas en la Versión 5.4 (Estándar Industrial)

En respuesta a la auditoría técnica experta, la Revisión 5.4 integró las siguientes precisiones de bajo nivel:

1. **Evolución de Evasión: Indirect Syscalls, Call Stack Unwinding y Call Stack Spoofing (Lección 2.15, págs. 162–163):**
   - Justificación de por qué las *Direct Syscalls* fallan ante defensas modernas: Telemetría de Kernel (ETWti / *Microsoft-Windows-Threat-Intelligence*) e *Instrumentation Callbacks* que detectan si el `RIP` proviene de memoria privada o `.text` local.
   - Implementación de **Indirect Syscalls**: salto (`jmp`) a la instrucción `syscall; ret` legítima dentro de `ntdll.dll` para legitimar el `RIP`.
   - Inspección del *Call Stack Walking* mediante tablas `.pdata`/`UNWIND_INFO` y necesidad defensiva de comprender el *Call Stack Spoofing*.
   - Nota sobre *Tartarus' Gate* (hooks desplazados al byte `+3`).
2. **La Trampa del Endianness en CNG vs. CryptoAPI y Script de Conversión en Python (Lección 4.2, págs. 250–251):**
   - Cuadro comparativo de *magic bytes* en CNG (`BCRYPT_RSAPUBLIC_MAGIC = "RSA1"`, `BCRYPT_ECCPUBLIC_MAGIC = "ECK1"` / `"ECS1"` para curvas P-256).
   - Detalle crítico de orden de bytes: **CryptoAPI clásica almacena el módulo en Little-Endian, mientras que CNG lo hace en Big-Endian**.
   - Script funcional de 10 líneas en Python (`PyCryptodome`) para reconstruir una clave pública `.pem` a partir de volcados de memoria invirtiendo el *endianness*.
   - Reconocimiento visual del OID de RSA en estructuras ASN.1 DER (`30 82 .. 30 0D 06 09 2A 86 48 86 F7 0D 01 01 01`).
3. **Doble Breakpoint en x64dbg para Funciones In-Place y Niche Optimization en Rust (Lecciones 2.6 y 2.13, págs. 102–103 y 142):**
   - Técnica de doble breakpoint encadenado con variable de usuario en x64dbg para rutinas `void decodificar(char* buf)`: `$ptr = rcx` en el prólogo y log `{utf8@$ptr}` en el `ret`, sorteando la sobreescritura de registros volátiles.
   - Recomendación de plugins tácticos: **ScyllaHide**, **xAnalyzer** y **OllyDumpEx**.
   - *Niche Optimization* en Rust: supresión del byte discriminante `tag` en tipos que garantizan no-nulidad (`Option<&T>`, `Option<Box<T>>`, `Option<NonZeroU32>`), traduciéndose en desensamblado como una simple comprobación de puntero nulo (`test rax, rax ; jz es_none`).

---

## 📌 Estado de la Versión

- **Edición:** 5
- **Revisión:** 5.4 (Estándar Industrial Consolidado)
- **Fecha:** 30 de octubre de 2026
- **Estado de Compilación:** Aprobado (0 problemas de paginación, 0 destinos TOC rotos en los 4 volúmenes).
