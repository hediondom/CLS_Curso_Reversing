# Reversing en Windows — Edición Libre y Abierta
## Tomo III: LLVM, Rust, Contenedores y Reversing con IA Local
*(Revisión 5.4 / Trilogía Consolidada)*

---

### Ficha Técnica del Volumen

- **Título Oficial:** Reversing en Windows — Tomo III: LLVM, Rust, Contenedores y Reversing con IA Local.
- **Perfil Académico:** Reversers, analistas de malware y auditores de seguridad que hayan completado las Etapas 0 a 4 del Tomo I y la Etapa 6 / Rama 2D del Tomo II. No requiere experiencia previa con el compilador Clang ni con infraestructura de Machine Learning.
- **Carga Horaria Estimada:** 25 a 35 horas de lectura crítica + 15 a 20 horas de laboratorio práctico.
- **Presupuesto Editorial:** 52 páginas consolidadas (26 hojas físicas a doble faz para encuadernación Ring Wire 3:1 de 14.3 mm, volumen completo de cierre).
- **Paridad Par de Impresión:** Asegurada mediante Bitácora de Laboratorio y Colofón Editorial en la página de cierre.

---

### Puerta de Salida Declarada

> *«Al finalizar este volumen, podés reconocer patrones característicos de `clang-cl` (switch lowering por bits, presencia de instrucciones AVX2, comprobaciones de Clang CFI) y saber cuándo aplicar el modelo de MSVC en su lugar; auditar binarios de Rust stripped sin tablas de pánico; evaluar las restricciones reales de un contenedor LPAC en Windows 11; interpretar la protección de pila por hardware (Intel CET); y desplegar un pipeline local de Ghidra asistido por IA con métricas de acierto y tolerancia a fallos documentadas en laboratorio.»*

---

### Declaración de Alcance, Límites y Pendientes Heredados

#### Lo que este volumen NO cubre
1. **Reversing de ARM64 nativo puro:** El Módulo 3 se enfoca estrictamente en el modelo híbrido **ARM64EC** sobre Windows 11 (emulación, trampolines `$$h` y convivencia con código x64). Para reversing de ARM64 puro (Android/Linux/macOS), refiérase a bibliografía especializada de esa arquitectura.
2. **Espacio de kernel de Linux dentro de WSL2:** Se audita la frontera IPC de interoperabilidad desde Windows (sockets `AF_UNIX`, named pipes `\\.\pipe\wsl\` y VMBus de Hyper-V), no la ingeniería inversa del árbol de fuentes de Linux ni el desarrollo de drivers para WSL.
3. **Entrenamiento, fine-tuning o desarrollo CUDA de IA:** El Módulo 4 trata al LLM local como un motor de inferencia determinista gobernado por API REST para enriquecer el AST del descompilador. No es un manual de Machine Learning ni de computación tensorial.
4. **Sustitución del criterio analítico humano:** Ninguna sugerencia de renombrado o tipado generada por IA se acepta en el informe de auditoría sin la validación empírica de sus referencias cruzadas contra las APIs del sistema operativo.

#### Declaración de Pendientes Heredados (Coherencia con Tomo I, pág. 9)
En estricta observancia de la metodología declarada en la página 9 del Tomo I:
> *Los pendientes históricos documentados en la obra base (la lectura exhaustiva de todas las transcripciones y tutoriales de IDA indexados, así como los contenedores avanzados de exploiting de la Etapa 5) **continúan abiertos** y no forman parte del alcance del Tomo III. Se mantienen identificados en la bitácora general de la obra para su eventual abordaje en revisiones mayores o monografías complementarias.*

---

### Estado de Verificación de Laboratorio de las Plantillas 17 a 21

| Módulo / Laboratorio | Entregable | Estado Actual | Evidencia Requerida para Cerrar (Fase 3) |
|---|---|---|---|
| **Módulo 1 · Clang CFI** | `plantilla_17a` / `17b` | **Verificado** | Binario compilado con hash SHA-256 + captura del trap `ud2` en desensamblador + versión exacta de LLVM (17+). |
| **Módulo 1 · Rust LTO** | `plantilla_18` | **Verificado** | Binario stripped con hash SHA-256 + volcado de `strings` limpio (sin rutas `.rs`) + script de slices ejecutado con éxito. |
| **Módulo 2 · LPAC y MSIX** | `plantilla_19` | **Verificado** | Captura de `AccessChk.exe -p` + volcado WinDbg de `!token` exhibiendo bit LPAC `0x20` y SIDs `S-1-15-3-*` sobre una app real. |
| **Módulo 3 · Intel CET** | `plantilla_20` | **Verificado** | Traza de `!analyze -v` en CPU física o VM con vCET activo, documentando el `ExceptionCode` real (`0xC00006A6` vs `0xC0000409` subcódigo `0x2A`). |
| **Módulo 4 · PyGhidra ↔ Ollama**| `plantilla_21` | **Verificado** | Benchmark documentado sobre el set propio de 20 funciones con `qwen2.5-coder:14b`: $\ge 60\%$ acierto semántico, $\le 8$ s latencia y fallback regex probado. |

---

### Tabla de Concordancia Retrospectiva con Tomo I y Tomo II

| Sección en Tomo III | Requiere Repaso Previo de | Página Impresa en la Obra Existente |
|---|---|---|
| **§1.1 – 1.2** (`clang-cl` vs. MSVC y CFI) | Lección 2.18 (C++ profundo y desensamblado MSVC) | **Tomo I, págs. 180–188** |
| **§1.3 – 1.4** (Rust LTO y slices `ptr+len`) | Lección 2.32 (Go y Rust en profundidad) | **Tomo I, págs. 243–247** |
| **§2.1 – 2.2** (Contenedores LPAC y SIDs) | Lección 2.35 (AppContainer y tokens) | **Tomo I, págs. 259–260** |
| **§2.3** (Frontera WSL2 e IPC híbrido) | Lección 2D.16 (Hyper-V, particiones y VMBus) | **Tomo II, págs. 182–187** |
| **§3.1** (Intel CET a nivel de Opcode) | Lección 5.2.b (Vulnerabilidades y mitigaciones ROP) | **Tomo I, págs. 332–335** |
| **§3.2** (Detección de Stack Spoofing) | Lección 2D.11 (Excepciones, SEH y `UNWIND_CODE`) | **Tomo II, págs. 154–161** |
| **§3.3** (ARM64EC en el desensamblador) | Lección 2.35.b (Binarios Híbridos ARM64EC) | **Tomo I, págs. 263–264** |
| **§4.1 – 4.4** (IA Local soberana para Ghidra) | Lección 2.31 (Extensiones de Ghidra y PyGhidra) | **Tomo I, págs. 240–242** *(Contexto instrumental: 115–120)* |

> *Nota obligatoria de consulta:* Las páginas indicadas corresponden al **número impreso en el encabezado de cada hoja**, tanto en la edición consolidada de 410 páginas como en la edición dividida (donde la Parte B conserva la numeración continua de 173 a 410). Si utiliza un visor de PDF sobre el archivo dividido `Tomo_1_Parte_B_pags_173-410.pdf`, recuerde que la página impresa 180 corresponde a la página física 8 del visor.

---

### Hoja de Ruta de Transición y Estados del Proyecto

- **ESTADO 1: Especificación Técnica y Editorial:** `[CERRADO Y APROBADO]`.
- **ESTADO 2: Fase 2 de Redacción (Módulos 1 a 4):** `[COMPLETADO]`.
- **ESTADO 3: Fase 3 de Laboratorio (Hardware e IA Local):** `[VERIFICADO]`.
- **ESTADO 4: Publicación e Impresión Física (52 págs. par):** `[LISTO PARA IMPRENTA]`.
