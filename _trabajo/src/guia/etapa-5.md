---
title: "Etapa 5 · Ramas opcionales"
description: "Elegir una especialización dentro de Windows, con prerrequisitos y práctica propia, sin convertir el corpus en una lista de tareas peligrosas."
etapa: "Etapa 5 · Ramas opcionales"
---

# Etapa 5 · Ramas opcionales

:::{nota} Objetivo medible
Elegir una especialización dentro de Windows, con prerrequisitos y práctica propia, sin convertir el corpus en una lista de tareas peligrosas.
:::

**Prerrequisitos:** Etapas 0 a 4 completas.  
**Duración estimada:** Variable: 5 a 10 horas por rama. Es una estimación de esta guía, derivada de la suma de las lecciones; no es una duración declarada por CLS.

## Lecciones

| # | Lección | Qué aprendés |
|---|---|---|
| 5.1 | [Rama malware: análisis defensivo sin ejecutar](05-malware.html) | Triage, IOCs, YARA y respuesta. |
| 5.2 | [Rama vulnerabilidades: entender el defecto](05-vulnerabilidades.html) | Desbordes, mitigaciones de Windows y divulgación. |
| 5.3 | [Rama automatización: scripts](05-automatizacion.html) | IDAPython, Ghidra, pefile y capstone. |
| 5.4 | [Kernel y otros territorios: qué queda fuera](05-fuera-de-alcance.html) | Límites explícitos, otras plataformas y prerequisites. |

## Recursos de CLS para esta etapa

- [2D · Windows internals (rama optativa)](../2d.html)
- [Etapa 6 · Kernel y drivers (rama optativa, requiere base técnica específica)](etapa-6.html)
- [Exploiting (contenedores pendientes)](../fichas/exploiting-contenedores.html)
- [Virus (excluido)](../fichas/malware-virus.html)
- [Themida (excluido)](../fichas/themida.html)

## Evaluación de salida

- Elegir una rama y completar su práctica con documentación.
- Explicar los prerrequisitos y los límites de esa rama.
- No ejecutar muestras ni usar técnicas de evasión fuera del marco.

:::{practica} Entregable de la etapa
Un archivo en tu bitácora con: lecciones completadas, ejercicios resueltos, dudas abiertas y evidencia (capturas, valores, hashes). Sin evidencia no se considera aprobada.
:::

## Errores frecuentes

- Saltar a exploiting sin dominar stack y mitigaciones.
- Ejecutar malware para "ver qué hace".
- Confundir un contenedor sin revisar con una fuente leída.

## Qué no entra en esta etapa

Los temas que no tienen material revisado o que exceden el marco se listan en [Kernel y otros territorios](05-fuera-de-alcance.html). No los uses como atajo: cada rama tiene prerrequisitos.

:::nota Volver
[Mapa del curso](index.html) · [Inicio](../00_EMPEZAR_AQUI.html)
:::
