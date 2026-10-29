---
title: "Etapa 5 · Kernel y otros territorios: qué queda fuera y por qué"
description: "Límites explícitos de esta edición: kernel, protección comercial y temas sin material revisado."
etapa: "Etapa 5 · Ramas opcionales"
---

# Kernel y otros territorios: qué queda fuera y por qué

:::{nota} Objetivo de la lección
Al terminar vas a poder explicar por qué el kernel, el desempaquetado de protectores comerciales, el exploiting contra terceros y **otras plataformas (Linux, macOS, Android, ARM)** no forman parte de esta edición, y qué prerequisites harían falta para abordarlos.
:::

:::{aviso} Esta edición es solo Windows
Por decisión de alcance, la guía cubre **únicamente binarios de Windows** (PE, x86/x64). El reversing de **Linux/ELF**, **macOS/Mach-O**, **Android (APK/DEX)** y arquitecturas como **ARM/AArch64** queda **fuera**. Los conceptos de base (números, memoria, stack, flujo, método) se trasladan a esas plataformas, pero su formato, convenciones y herramientas son otro mundo y merecen su propio material.
:::

**Prerrequisitos:** etapas 0 a 4. **Duración sugerida:** 30 minutos (lectura y reflexión).

## Una guía también se define por lo que no incluye

El corpus de CLS tiene material de kernel, protectores comerciales, exploiting y malware. No todo se convierte en lección. Algunos temas quedan fuera por tres razones:

1. **No hay material revisado.** Hay contenedores que no se abrieron; una mención no es contenido.
2. **El riesgo no es proporcional al beneficio para un principiante.** Enseñar a manipular kernel o protectores sin bases sólidas produce accidentes, no aprendizaje.
3. **El marco legal y ético.** Eludir protecciones de software comercial o atacar sistemas ajenos no es educativo.

## Kernel

Un módulo de kernel corre en el nivel más privilegiado del sistema. Un error ahí no crashea una aplicación: crashea la máquina, corrompe el sistema o abre una puerta que no se cierra con un reinicio.

Para abordar kernel con responsabilidad hacen falta, como mínimo:

- C y ensamblador con soltura.
- Entender la memoria virtual, la paginación y las estructuras del sistema operativo.
- Un laboratorio con snapshots y, preferentemente, hardware o VM descartable.
- Un objetivo defensivo claro: analizar un driver, entender una mitigación, revisar una vulnerabilidad con permiso.

En CLS no hay un curso de kernel leído. El mapa menciona material de exploiting y de drivers, pero no se verificó. Esta guía no lo convierte en una lección de principiante.

## Protectores comerciales

El desempaquetado de protectores como Themida, WinLicense o ACProtect aparece en el corpus (por ejemplo, el RAR de Themida + WinLicense y los capítulos de ACProtect). Es material avanzado y, en muchos casos, orientado a modificar software comercial.

Esta guía explica **qué es** un empacador, cómo se reconoce y por qué el código queda plano en memoria en algún momento. No enseña a desempaquetar protectores comerciales, no distribuye recetas y no propone esas tareas. El capítulo 35 (inline patching sobre ACProtect) se cita solo como evidencia de que la técnica existe; no se reproduce.

## Exploiting contra terceros

Los ejercicios de vulnerabilidades de esta guía se limitan a programas propios o laboratorios deliberadamente vulnerables, con permiso. No se enseña a atacar sistemas ajenos, a evadir defensas de terceros ni a mantener acceso.

Si tu objetivo es la seguridad ofensiva profesional, el camino incluye:

- Fundamentos de redes y sistemas.
- Programación y análisis de binarios.
- Laboratorios legales (por ejemplo, entornos de práctica diseñados para eso).
- Certificaciones y programas con alcance definido.
- Ética y divulgación responsable.

## Otros temas del corpus que quedan como referencia

| Tema | Estado en esta edición |
|---|---|
| Android (APK/DEX) | **Fuera de alcance**: edición solo Windows |
| Linux/ELF | **Fuera de alcance**: edición solo Windows |
| macOS/Mach-O | **Fuera de alcance**: edición solo Windows |
| ARM/AArch64 y otras arquitecturas | **Fuera de alcance**: edición solo Windows (x86/x64) |
| Malware | Triage estático defensivo de Windows; ejecución **fuera de alcance** |
| Vulnerabilidades | Concepto y mitigación en laboratorio propio; exploit **fuera de alcance** |
| Kernel/drivers (Windows) | Rama [optativa Etapa 6](etapa-6.html): drivers propios/didácticos en VM descartable; no rootkits, BYOVD, explotación ni evasión de mitigaciones |
| Protectores comerciales | **Fuera de alcance** por marco legal y ético |
| Automatización | Rama con IDAPython/Ghidra; capítulos CLS **pendientes** |

## Práctica

1. Elegí un tema de la tabla que te interese y escribí qué prerequisites te faltan.
2. Buscá en el corpus un recurso de ese tema y anotá si está leído o pendiente.
3. Escribí una regla personal: "no voy a analizar X hasta poder Y".
4. Revisá tu bitácora: ¿hay alguna práctica que hayas hecho sin permiso o sin aislamiento? Corregila.

## Preguntas de repaso

**1. ¿Por qué el kernel queda fuera?**
Por el nivel de privilegio, el riesgo de daño y la falta de material revisado y de prerequisites en esta edición.

**2. ¿Qué diferencia hay entre explicar un empacador y desempaquetar un protector comercial?**
Explicar es conceptual y defensivo; desempaquetar un protector comercial para modificar el programa queda fuera del marco legal y ético de esta guía.

**3. ¿Qué hace falta para practicar exploiting de forma responsable?**
Un laboratorio propio o autorizado, un objetivo definido, permisos y un plan de divulgación.

**4. ¿Una mención en el corpus alcanza para dar una lección?**
No. Una mención o un título no demuestran el contenido. Primero hay que leerlo y verificarlo.

## Antes de cerrar

Tenés que poder:

- Explicar por qué no todo el corpus se convierte en curso.
- Nombrar los prerequisites de kernel.
- Decir qué temas quedan como referencia y cuáles como pendientes.

:::{nota} Cierre del recorrido
Si llegaste hasta acá con las etapas 0 a 4 completas, tenés una base real de reversing. Las ramas son opcionales: elegí una, completá su práctica y documentala. No acumules temas: acumulá evidencia.
:::

## Fuentes de esta lección

- {{src:CLS_resultados_intermedios/mapa_carpetas_etapas.csv|mapa_carpetas_etapas.csv}} — asignación de temas y notas sobre kernel/exploiting.
- {{src:telegram/Themida + WinLicense 2.x (Unpacking).rar|Themida + WinLicense 2.x (Unpacking).rar}} — recurso **excluido** del recorrido base.
- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_35 Cómo parchear un programa empacado - In Line Patching_35 Cómo parchear un programa empacado - In Lin.txt|Reversing desde cero, cap. 35}} — evidencia de la técnica de inline patching; **no se reproduce**.
- {{src:CLS_Guia/FUENTES_Y_LIMITES.md|FUENTES_Y_LIMITES.md}} — criterios de exclusión de esta edición.

:::{nota} Capas de esta lección
**Contenido observado en CLS:** la existencia de los recursos y su clasificación en el mapa. **Conocimiento externo:** requisitos de kernel y explotación responsable. **Recomendación editorial:** los límites y la tabla de estado.
:::
