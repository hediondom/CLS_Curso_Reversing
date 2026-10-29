---
title: "Etapa 1 · Fundamentos"
description: "Leer un binario sencillo: números, memoria, procesos, formato PE y programas propios en C y Python."
etapa: "Etapa 1 · Fundamentos"
---

# Etapa 1 · Fundamentos

:::{nota} Objetivo medible
Leer un binario sencillo: números, memoria, procesos, formato PE y programas propios en C y Python.
:::

**Prerrequisitos:** Etapa 0.  
**Duración estimada:** 21 a 25 horas. Es una estimación de esta guía, derivada de la suma de las lecciones; no es una duración declarada por CLS.

## Lecciones

| # | Lección | Qué aprendés |
|---|---|---|
| 1.1 | [Bits, bytes, hexadecimal y números con signo](01-numeros.html) | Binario, hex, complemento a dos, little-endian y VA→offset. |
| 1.2 | [Memoria: stack, heap y marcos de función](01-memoria.html) | Stack, prólogo/epílogo, argumentos y shadow space en x64. |
| 1.3 | [Procesos, hilos y mapa de memoria](01-procesos.html) | Procesos, hilos, handles, mapa de memoria y permisos. |
| 1.4 | [El formato PE: cabeceras, secciones e imports](01-pe.html) | Cabecera PE, secciones, IAT y ASLR. |
| 1.5 | [C y Python mínimos para analizar](01-c-python.html) | Programas propios en C y herramientas en Python. |

## Recursos de CLS para esta etapa

- [Reversing desde cero (caps. 01–05)](../fichas/reversing-desde-cero.html)
- [Python ISO video tutes (lógica, no Python)](../fichas/python-iso.html)
- [Curso de MASM32 (Videos 1–22)](../fichas/masm32-cayetano.html)

## Evaluación de salida

- Convertir valores entre binario, hex y decimal sin calculadora.
- Dibujar el stack de una función de 32 bits y explicar el de 64 bits.
- Calcular un file offset a partir de una VA y verificarlo en el archivo.
- Compilar un programa propio en C y leer su hash y cabecera PE.

:::{practica} Entregable de la etapa
Un archivo en tu bitácora con: lecciones completadas, ejercicios resueltos, dudas abiertas y evidencia (capturas, valores, hashes). Sin evidencia no se considera aprobada.
:::

## Errores frecuentes

- Memorizar la tabla hexadecimal sin entender el valor posicional.
- Confundir dirección virtual con offset del archivo.
- Creer que el curso de Python de CLS enseña Python (enseña lógica).

## Qué no entra en esta etapa

Los temas que no tienen material revisado o que exceden el marco se listan en [Kernel y otros territorios](05-fuera-de-alcance.html). No los uses como atajo: cada rama tiene prerrequisitos.

:::nota Volver
[Mapa del curso](index.html) · [Inicio](../00_EMPEZAR_AQUI.html)
:::
