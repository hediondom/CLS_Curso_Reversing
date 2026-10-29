---
title: "Etapa 3 · .NET como primera victoria"
description: "Entender el runtime .NET, leer IL y comparar fuente, IL y decompilación en un programa propio."
etapa: "Etapa 3 · .NET como primera victoria"
---

# Etapa 3 · .NET como primera victoria

:::{nota} Objetivo medible
Entender el runtime .NET, leer IL y comparar fuente, IL y decompilación en un programa propio.
:::

**Prerrequisitos:** Etapa 2.  
**Duración estimada:** 7 a 10 horas. Es una estimación de esta guía, derivada de la suma de las lecciones; no es una duración declarada por CLS.

## Lecciones

| # | Lección | Qué aprendés |
|---|---|---|
| 3.1 | [.NET: runtime, ensamblados y metadatos](03-dotnet-runtime.html) | CLR, IL, JIT, ensamblado y decompiladores. |
| 3.2 | [Leer IL y comparar fuente, IL y decompilación](03-dotnet-il.html) | Pila de evaluación, opcodes y reconstrucción. |

## Recursos de CLS para esta etapa

- [Reversing desde cero (contexto de análisis)](../fichas/reversing-desde-cero.html)
- [Teorias_Numeradas (títulos .NET, pendiente)](../fichas/teorias-numeradas.html)

## Evaluación de salida

- Explicar C# → IL → JIT → CPU.
- Leer un método IL de 20 instrucciones y decir qué devuelve.
- Compilar Debug y Release y marcar tres diferencias.
- Reconocer señales de ofuscación.

:::{practica} Entregable de la etapa
Un archivo en tu bitácora con: lecciones completadas, ejercicios resueltos, dudas abiertas y evidencia (capturas, valores, hashes). Sin evidencia no se considera aprobada.
:::

## Errores frecuentes

- Creer que el decompilador devuelve el código fuente exacto.
- Asumir que .NET es inseguro por naturaleza.
- Analizar software comercial para saltar licencias.

## Qué no entra en esta etapa

Los temas que no tienen material revisado o que exceden el marco se listan en [Kernel y otros territorios](05-fuera-de-alcance.html). No los uses como atajo: cada rama tiene prerrequisitos.

:::nota Volver
[Mapa del curso](index.html) · [Inicio](../00_EMPEZAR_AQUI.html)
:::
