# Entregable 6 — Acta de Control Final y Verificación de Integridad

**Fecha de verificación:** 29 de octubre de 2026.  
**Objetivo del control:** Confirmar de manera auditable y reproducible que (1) ningún archivo original de CLS fue modificado ni sobrescrito, (2) el 100 % del texto, ejemplos y estructura de CLS permanece intacto en la versión ampliada, y (3) cada afirmación técnica nueva en los 17 módulos de ampliación cuenta con su cita cercana y enlaza con la fuente externa primaria que la respalda.

---

## 6.1 Verificación de Integridad de los Archivos Originales de CLS (No Sobrescritura)

El archivo original `CLS_Curso_Reversing.pdf` y su HTML imprimible base `_trabajo/print/CLS_Curso_Reversing_imprimible.html`, así como las 46 lecciones de `guia/*.html` y sus fuentes en `_trabajo/src/`, **no fueron alterados en ningún byte**:

| Archivo Original | Estado | Tamaño (bytes) | Fecha de última modificación | Hash SHA-256 Verificado |
|---|---|---:|---|---|
| `CLS_Curso_Reversing.pdf` | **Intacto (0 cambios)** | `4.477.417` | `28/10/2026 18:23` | `AD9DC0CFD1EF33454E57ECA9E920C1ECBE8D148443B90C545426B55492ECF18F` |
| `_trabajo/print/CLS_Curso_Reversing_imprimible.html` | **Intacto (0 cambios)** | `1.117.885` (1.103.007 chars UTF-8) | `28/10/2026 18:22` | Preservado bit a bit |
| `_trabajo/src/guia/*.md` (59 archivos) | **Intactos (0 cambios)** | — | `27–28/10/2026` | Preservados bit a bit |

---

## 6.2 Prueba Matemática de Preservación Literal del Texto de CLS en la Nueva Versión

En `CLS_Curso_Reversing_v5.1_Ampliada.html`:
- Longitud del documento original (`CLS_Curso_Reversing_imprimible.html`): **`1.103.007` caracteres**.
- Cantidad de bloques insertados (`<aside class="nota-ed">` y `<aside class="ampliacion-ext">`): **17 módulos** en las secciones correspondientes, más la regla CSS de impresión `.print-sec .tabla { overflow-x: visible !important; }`.
- Al retirar mediante expresión regular los bloques `<aside class="nota-ed">...</aside>`, `<aside class="ampliacion-ext">...</aside>` y el bloque `CSS_EXTRA` (junto con el salto de línea `\n` previo al cierre `</section>` de cada una de las 17 secciones intervenidas: $1.103.024 - 17 = 1.103.007$), el contenido resultante tiene **exactamente `1.103.007` caracteres y 0 diferencias carácter por carácter** respecto del documento original de CLS.

---

## 6.3 Auditoría Cruzada de Citas y Fuentes Externas (`[Ref-1]` a `[Ref-25]`)

Cada uno de los 17 módulos del **Entregable 3** (`ENTREGABLE_3_NUEVA_VERSION_AMPLIADA.md` y `CLS_Curso_Reversing_v5.1_Ampliada.html`) fue auditado para confirmar que:
1. Lleva la etiqueta explícita **«Nota editorial»** o **«Ampliación editorial basada en fuentes externas»**.
2. Distingue entre *Hecho confirmado*, *Recomendación editorial* e *Inferencia*.
3. Todas las citas `[Ref-1]` a `[Ref-25]` resuelven en el **Entregable 5** (`ENTREGABLE_5_BIBLIOGRAFIA_VERIFICABLE.md`) hacia documentación primaria verificable:

| Módulo (Entregable 3) | Lección y Páginas PDF | Citas Empleadas | Fuente Primaria Verificada en Entregable 5 | Estado |
|---|---|---|---|---|
| **Módulo 1** | Apertura y Etapa 4 (págs. 4, 10, 203, 402) | `[Ref-Interna]` | Coherencia interna de `CLS_Curso_Reversing.pdf` (suma de 21 h en 5 lecciones) | Verificado |
| **Módulo 2** | Lección 2.6 · Debugger (pág. 90) | `[Ref-1]`, `[Ref-2]`, `[Ref-3]` | Microsoft Learn (`WindowProc`, ABI x64, `WM_COMMAND`) y x64dbg Docs (`arg.get`) | Verificado |
| **Módulo 3** | Lección 2.10 · Ofuscación nativa (pág. 119) | `[Ref-4]`, `[Ref-5]` | Obfuscator-LLVM (Junod et al., SPRO '15) y Rolles (USENIX WOOT '09) | Verificado |
| **Módulo 4** | Lección 2.12 · MFC (pág. 126) | `[Ref-6]` | Microsoft Learn / MSVC `<afxwin.h>` (`AFX_MSGMAP_ENTRY`, `TN006`) | Verificado |
| **Módulo 5** | Lección 2.13 · Huella Delphi (págs. 130, 132, 402) | `[Ref-7]`, `[Ref-8]`, `[Ref-9]` | Embarcadero RAD Studio DocWiki (*Program Control*, *Internal Data Formats*, *Resource Files*) | Verificado |
| **Módulo 6** | Lección 2.14 · PE fino (pág. 136) | `[Ref-10]`, `[Ref-11]`, `[Ref-12]` | Microsoft Learn (`PEB`, `PEB_LDR_DATA` en `winternl.h`) y *Windows Internals 7th Ed.* | Verificado |
| **Módulo 7** | Lección 2.15 · Anti-análisis (pág. 142) | `[Ref-10]`, `[Ref-13]`, `[Ref-14]`, `[Ref-15]` | Microsoft Learn (`NtQueryInformationProcess`, `GFlags`) y *Practical Malware Analysis* Cap. 16 | Verificado |
| **Módulo 8** | Lección 2.17 · Packers didácticos (pág. 152) | `[Ref-15]`, `[Ref-16]` | *Practical Malware Analysis* Cap. 18 (*The ESP Trick*) e Intel SDM Vol. 3B §17.2 | Verificado |
| **Módulo 9** | Lección 2.18 · C++ profundo (pág. 158) | `[Ref-17]` | Microsoft C++ Team Blog / MSVC Docs (`__CxxFrameHandler4` / `/d2FH4`) | Verificado |
| **Módulo 10** | Lección 2.19 · WinDbg y heap (pág. 166) | `[Ref-18]`, `[Ref-19]` | Microsoft Learn (*Application Manifests `segmentHeap`* y *WinDbg `!heap`*) | Verificado |
| **Módulo 11** | Lección 3.1 · .NET runtime (pág. 193) | `[Ref-20]`, `[Ref-21]` | Microsoft Learn (*Single-file deployment* y *ReadyToRun R2R deployment*) | Verificado |
| **Módulo 12** | Lección 4.5 · Formatos y protocolos (págs. 214–215) | `[Ref-Interna]` | Fuente local `_trabajo/src/guia/04-formatos-protocolos.md` (bloques `~~~text`) | Verificado |
| **Módulo 13** | Lección 4.2 · Criptografía (pág. 218) | `[Ref-22]` | IETF RFC 8439 (*ChaCha20 and Poly1305 for IETF Protocols*, Secciones 2.1 y 2.3) | Verificado |
| **Módulo 14** | Lección 5.3 · IDAPython (pág. 250) | `[Ref-23]` | Hex-Rays Docs (*Porting from IDA 8.x to IDA 9.0 — `ida_typeinf`*) | Verificado |
| **Módulo 15** | Lección 6.2 · KMDF e IOCTL (pág. 266) | `[Ref-24]`, `[Ref-25]` | Microsoft Learn (`WdfRequestRetrieveOutputBuffer` y *Accessing Data Buffers in WDF Drivers*) | Verificado |
| **Módulo 16** | Lección 2D.2 · Memoria y loader (pág. 302) | `[Ref-Interna]` | Fuente local `_trabajo/src/guia/2d-02-memoria-loader.md` (líneas 100–104) | Verificado |
| **Módulo 17** | Glosario (pág. 385) | `[Ref-3]`, `[Ref-17]`–`[Ref-23]` | Consolidación de definiciones respaldadas en los módulos anteriores | Verificado |

---

## 6.4 Inventario de Archivos Nuevos Generados (Entregables 1 a 6)

Todos los archivos nuevos fueron creados en `d:\CLS_proyecto\CLS_Guia\` sin sobrescribir ningún archivo existente:

| Entregable | Archivo Generado | Tamaño (bytes) | Hash SHA-256 |
|---|---|---:|---|
| **Entregable 1** (Informe de revisión e inventario) | `ENTREGABLE_1_INFORME_REVISION_E_INVENTARIO.md` | `32.496` | `A967830E7A05A235FF12724449860E5708B44524298C6BF0DDEC3F757FD09656` |
| **Entregable 2** (Matriz priorizada de mejoras) | `ENTREGABLE_2_MATRIZ_DE_MEJORAS.md` | `15.729` | `2A1DBC858FA916AB39E8E207D4D9DC9B88A9E82AEAA692B849A05E38324F9633` |
| **Entregable 3** (Suplemento Markdown de los 17 módulos) | `ENTREGABLE_3_NUEVA_VERSION_AMPLIADA.md` | `38.610` | `B15FF1B413D5DB00FC7C4B11A268203C5F3BDC92A249C277FB97632E595E0087` |
| **Entregable 3** (Guía completa HTML unificada v5.1) | `CLS_Curso_Reversing_v5.1_Ampliada.html` | `1.145.895` | `7494731E03B2EF32018740D03BBBF350C4901867DE6EE825B85B7D9E950D615F` |
| **Entregable 4** (Lista de cambios y ubicaciones) | `ENTREGABLE_4_LISTA_DE_CAMBIOS.md` | `11.613` | `90F5CCBBEBF7C2FC6B37292D7229F8BBA12488297FBC587C8EEE212BD137C7E3` |
| **Entregable 5** (Bibliografía verificable con enlaces) | `ENTREGABLE_5_BIBLIOGRAFIA_VERIFICABLE.md` | `14.661` | `920D45818B2006E7D0411438F48F940B4CAD538C246DE9606640DC0F1EB6492C` |
| **Entregable 6** (Acta de control final) | `ENTREGABLE_6_CONTROL_FINAL.md` | *(este archivo)* | — |
