---
title: "Etapa 0 · Laboratorio y método seguro"
description: "Armar un entorno aislado, tomar snapshots, verificar hashes y registrar cada práctica con su alcance."
etapa: "Etapa 0 · Laboratorio y método seguro"
---

# Etapa 0 · Laboratorio y método seguro

:::{nota} Objetivo medible
Armar un entorno aislado, tomar snapshots, verificar hashes y registrar cada práctica con su alcance.
:::

**Prerrequisitos:** Ninguno.  
**Duración estimada:** 4 a 6 horas. Es una estimación de esta guía, derivada de la suma de las lecciones; no es una duración declarada por CLS.

## Lecciones

| # | Lección | Qué aprendés |
|---|---|---|
| 0.1 | [Un laboratorio que podés romper sin miedo](00-laboratorio.html) | VM, snapshots, red aislada, transferencia por ISO y hashes. |

## Recursos de CLS para esta etapa

- [Inventario limpio de CLS](../fichas/inventario-limpio.html)
- [Transcripciones de Telegram](../fichas/transcripciones-telegram.html)

## Evaluación de salida

- Mostrar una VM con snapshot limpia y red aislada.
- Transferir un archivo sin carpeta compartida y verificar su SHA-256 en host y guest.
- Escribir una bitácora con snapshot, programa, hash y observaciones.
- Explicar qué harías si el programa deja el sistema en un estado raro.

:::{practica} Entregable de la etapa
Un archivo en tu bitácora con: lecciones completadas, ejercicios resueltos, dudas abiertas y evidencia (capturas, valores, hashes). Sin evidencia no se considera aprobada.
:::

## Errores frecuentes

- Usar carpeta compartida "solo para pasar el archivo".
- Tomar la snapshot después de copiar la muestra.
- Confundir una snapshot con un backup de los archivos del host.

## Qué no entra en esta etapa

Los temas que no tienen material revisado o que exceden el marco se listan en [Kernel y otros territorios](05-fuera-de-alcance.html). No los uses como atajo: cada rama tiene prerrequisitos.

:::nota Volver
[Mapa del curso](index.html) · [Inicio](../00_EMPEZAR_AQUI.html)
:::
