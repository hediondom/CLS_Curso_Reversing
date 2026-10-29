---
title: "Etapa 4 · Práctica guiada"
description: "Analizar programas propios con método, reconstruir un formato o protocolo desde muestras, contener la ejecución y escribir un informe reproducible."
etapa: "Etapa 4 · Práctica guiada"
---

# Etapa 4 · Práctica guiada

:::{nota} Objetivo medible
Analizar programas propios con método, reconstruir un formato o protocolo desde muestras, contener la ejecución y escribir un informe reproducible.
:::

**Prerrequisitos:** Etapas 0 a 3.  
**Duración estimada:** 19 a 25 horas. Es una estimación de esta guía, derivada de la suma de las lecciones; no es una duración declarada por CLS.

## Lecciones

| # | Lección | Qué aprendés |
|---|---|---|
| 4.1 | [Método de análisis: de la pregunta al hallazgo](04-metodo.html) | Ciclo de cinco pasos, hipótesis y confirmación. |
| 4.5 | [Reconstruir formatos y protocolos propios](04-formatos-protocolos.html) | Deducir campos, longitudes, framing, estados y transformaciones a partir de muestras controladas. |
| 4.2 | [Reconocer criptografía y encoding en un binario](04-cripto.html) | XOR, base64, constantes de AES/MD5/RC4 y CryptoAPI/CNG. |
| 4.3 | [El informe reproducible](04-informe.html) | Estructura, evidencia, límites y divulgación. |
| 4.4 | [Análisis dinámico seguro: cuándo ejecutar y cuándo no](04-dinamico-seguro.html) | Matriz de decisión, contención y respuesta. |

## Recursos de CLS para esta etapa

- [Reversing desde cero (ejercicios 1 y 2)](../fichas/reversing-desde-cero.html)
- [Inventario y estados de cuarentena](../fichas/inventario-limpio.html)

## Evaluación de salida

- Analizar un programa propio de punta a punta sin mirar el fuente.
- Reconstruir desde muestras propias un formato binario o un framing simple, justificando campos, longitudes y estados.
- Confirmar una condición con breakpoints y valores concretos.
- Escribir un informe con hash, entorno, evidencia y límites.
- Explicar por qué el caso Shelter no es una práctica de principiante.

:::{practica} Entregable de la etapa
Un archivo en tu bitácora con: lecciones completadas, ejercicios resueltos, dudas abiertas y evidencia (capturas, valores, hashes). Sin evidencia no se considera aprobada.
:::

## Errores frecuentes

- Parchear antes de entender.
- Ejecutar una muestra dudosa en el host.
- Escribir conclusiones sin evidencia.

## Qué no entra en esta etapa

Los temas que no tienen material revisado o que exceden el marco se listan en [Kernel y otros territorios](05-fuera-de-alcance.html). No los uses como atajo: cada rama tiene prerrequisitos.

:::nota Volver
[Mapa del curso](index.html) · [Inicio](../00_EMPEZAR_AQUI.html)
:::
