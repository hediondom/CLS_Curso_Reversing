# CLS — Curso de Reversing
### Paquete de Estudio Autónomo y Referencia Defensiva en Español

**Edición 5 · Revisión 5.2** (29 de octubre de 2026)  
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

## 📚 Materiales Impresos y Formato PDF (Revisión 5.2)

El material está optimizado para lectura digital e impresión profesional en gráfica (formato A4, márgenes simétricos para anillado/encuadernación, control de orfandad y contraste adaptado a doble faz):

| Archivo PDF | Páginas / Hojas | Contenido y Propósito |
| :--- | :---: | :--- |
| **`CLS_Tomo_1_Tronco_y_Apoyo.pdf`** | **314 págs.**<br>(157 hojas doble faz) | **Tomo I — Tronco y Apoyo:** Portada, Recorrido Troncal Completo (Etapas 0 a 6: Fundamentos x86/x64, Ensamblador, Análisis Estático y Dinámico, Criptografía, Desempaquetado, Formato PE), Casos de Estudio Transversales, Fichas de Recursos, Glosario y Repaso Q&A. |
| **`CLS_Tomo_2_Kernel_e_Internals.pdf`** | **120 págs.**<br>(60 hojas doble faz) | **Tomo II — Kernel e Internals:** Portada, Rama Optativa 2D completa (Arquitectura interna de Windows, Desarrollo de Drivers WDF/KMDF, Depuración de Kernel con WinDbg, Análisis de Crash Dumps y Extensión Hyper-V). |
| **`CLS_Separata_Escritorio.pdf`** | **14 págs.**<br>(7 hojas doble faz) | **Separata de Escritorio (Cheat-Sheets):** Cuadernillo de consulta rápida para tener junto al teclado. Incluye: Árbol de Triage Defensivo (1 pág.), Anatomía y Mapa del Formato PE x86/x64, Atajos/Comandos de WinDbg, x64dbg, GDB, IDA Pro y Ghidra, Tabla de Registro de Decisiones y Plantilla de Informe Técnico Forense. |
| **`CLS_Curso_Reversing_v5.2_Ampliada.pdf`**<br>*(o `CLS_Curso_Reversing.pdf`)* | **430 págs.**<br>(215 hojas doble faz) | **Edición Completa Consolidada:** Todo el material del curso en un solo volumen integrado con índice general unificado. |

### 🖨️ Recomendaciones para la Gráfica / Imprenta:
- **Interiores Tomo I y II:** Papel obra / chambril de **90 g/m²** (u 80 g/m² estándar). El gramaje de 90 g/m² garantiza máxima opacidad para evitar que trasluzcan los bloques oscuros de código y tablas en la impresión doble faz.
- **Separata de Escritorio:** Papel obra de **90 g/m²** o papel ilustración mate / obra grueso de **120–150 g/m²** para mayor rigidez y durabilidad durante el uso diario.
- **Tapas y Contratapas:** Cartulina o ilustración de **250–300 g/m²**, o tapas plásticas transparentes de polipropileno con encuadernación anillada (espiral o doble alambre / ring-wire).

---

## 🌟 Novedades Incorporadas en la Versión 5.2 (Mejoras de Alto Impacto)

La Revisión 5.2 consolida 6 bloques temáticos indispensables que cubren desde nivel principiante hasta avanzado:

1. **Árbol de Decisión / Triage Inicial (1 pág.):**  
   Flujo estandarizado y matriz heurística para clasificar binarios desconocidos en menos de 10 minutos (análisis de entropía, detección de empaque/protectores, verificación de firmas digitales y aislamiento dinámico en sandbox).
2. **Guía Visual y Estructural del Formato PE (Portable Executable):**  
   Diagrama arquitectónico ASCII y desglose de campos críticos de `IMAGE_DOS_HEADER`, `IMAGE_NT_HEADERS`, `IMAGE_OPTIONAL_HEADER`, `Data Directory`, tabla de secciones y directorios de importación/exportación (`IAT`/`EAT`).
3. **Laboratorio Aislado y Protocolo Anti-Evasión:**  
   Matriz técnica de contramedidas contra anti-debugging y anti-VM (`RDTSC`, `IsDebuggerPresent`, `BeingDebugged`, `NtGlobalFlag`, `CheckRemoteDebuggerPresent`, `Hardware Breakpoints`, artefactos de hipervisores VBox/VMware).
4. **Patrones de Compilador Moderno en x86/x64:**  
   Guía de desensamblado e ingeniería inversa para reconocer estructuras vs. arreglos, clases C++ con VTable y despacho polimórfico, plantillas (templates), inlining y tablas de salto de punteros a función.
5. **Casos de Estudio Transversales Guiados Paso a Paso:**  
   Tres escenarios prácticos de extremo a extremo con hipótesis, artefactos y lecciones aprendidas:
   - *Caso A (Principiante):* Binario crackme en C empaquetado con UPX modificado (reconstrucción manual del OEP y volcado de IAT).
   - *Caso B (Intermedio):* Loader de malware con inyección en proceso legítimo (`Process Injection`) y resolución dinámica de APIs por hash.
   - *Caso C (Avanzado):* Driver de Windows vulnerable a desbordamiento de búfer por IOCTL no saneado (análisis de crash dump en WinDbg).
6. **Metodología Forense y Plantilla de Informe Técnico:**  
   Estructura estandarizada y reproducible para redacción de informes técnicos y ejecutivos de análisis de software e incidentes de seguridad.

---

## 📂 Estructura del Repositorio

- `00_EMPEZAR_AQUI.html` / `index.html`: Portal principal interactivo y mapa del curso.
- `buscar.html`: Motor de búsqueda temático en texto completo para todo el curso.
- `guia/`: Lecciones troncales (Etapas 0 a 6) con teoría, ejemplos en ensamblador/C, ejercicios prácticos y puertas de salida.
- `2d.html` y `2d-hyperv.html`: Índice y módulos de la Rama 2D (Kernel e Internals).
- `ida_tutes/`: 69 tutoriales prácticos de IDA Pro:
  - 1 a 28: Acompañamiento directo a las lecciones del recorrido base.
  - 29 a 69: Referencia avanzada de decompilación, scripts y análisis especializado.
- `fichas/`: 20 fichas técnicas de herramientas (x64dbg, Ghidra, WinDbg, Process Hacker, PE-bear, YARA, etc.).
- `glosario.html`: Glosario terminológico con definiciones pedagógicas y ejemplos.
- `preguntas_y_respuestas.html`: Cuestionarios de autoevaluación por etapa con soluciones justificadas.
- `plantillas_codigo/`: Código fuente, esqueletos y plantillas para prácticas seguras.
- `plantilla_informe.md`: Plantilla editable para documentación forense.
- `ENTREGABLE_*.md`: Registros de auditoría, inventario, matriz de mejoras, lista de cambios y bibliografía académica verificable.
- `mapa_de_cobertura.csv`, `registro_de_cobertura.csv` y `seguimiento.csv`: Planillas de seguimiento y estado del corpus.

---

## 🛡️ Criterios Éticos y Legales

- **Finalidad Defensiva y Educativa:** Todo el contenido está diseñado con fines de formación en seguridad informática, análisis forense, ingeniería inversa de software propio o autorizado, y auditoría de vulnerabilidades.
- **Entorno Seguro:** Las prácticas se realizan sobre programas propios, proyectos de código abierto o crackmes educativos diseñados para aprendizaje.
- **Límites Claros:** No se enseña a vulnerar sistemas ajenos, eludir controles de licenciamiento comercial (DRM) ni violar accesos no autorizados.
- **Aislamiento:** Los ejercicios dinámicos y análisis de comportamiento deben ejecutarse siempre en máquinas virtuales aisladas sin conexión a redes de producción.

---

## 📌 Estado de la Versión

- **Edición:** 5
- **Revisión:** 5.2
- **Fecha:** 29 de octubre de 2026
- **Estado de Compilación:** Aprobado (0 problemas de paginación o saltos huérfanos).
