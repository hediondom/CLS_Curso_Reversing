---
title: "Etapa 2 · Cómo cambia el código con optimizaciones"
description: "Por qué un binario optimizado no se parece al código fuente: inlining, strength reduction, división por constante, vectorización y tail calls."
etapa: "Etapa 2 · Introducción al reversing"
---

# Cómo cambia el código con optimizaciones

:::{aviso} De dónde sale esta lección
Este tema **no está en el corpus CLS**: es **conocimiento externo** que agregamos para completar la guía. El curso de CLS usa ejemplos compilados en modo depuración (`-O0`/Debug), donde el assembly sigue de cerca al código fuente. Los binarios reales vienen optimizados (`-O2`/Release) y se ven muy distintos. Esta lección cubre ese salto, que es donde más se traba quien recién sale de los ejercicios.
:::

:::{nota} Objetivo de la lección
Al terminar vas a poder reconocer los patrones de optimización más comunes —inlining, *strength reduction*, división por constante, vectorización, *tail call*— y no confundirlos con "código raro" o con una protección.
:::

**Prerrequisitos:** instrucciones, flujo, llamadas (Etapa 2). **Duración sugerida:** 3 horas.

## El problema

En `-O0`, cada variable vive en el stack, cada operación es una instrucción y las funciones se llaman tal como las escribiste. En `-O2`, el compilador reescribe todo para que corra más rápido: mete funciones una dentro de otra, reemplaza multiplicaciones por sumas, borra código que "no hace falta" y reordena instrucciones. El resultado es correcto pero **no se parece** al fuente. Reconocer estos patrones es lo que separa leer un ejercicio de leer un programa real.

## Strength reduction: multiplicar sin `mul`

El compilador cambia operaciones caras por otras baratas. La más común: multiplicar por una constante usando `lea` y shifts.

```asm
; x * 2
add eax, eax            ; o:  shl eax, 1
; x * 8
shl eax, 3
; x * 5   ->  x + x*4
lea eax, [rax + rax*4]
; x * 9   ->  x + x*8
lea eax, [rax + rax*8]
```

Si ves un `lea` haciendo cuentas (no calculando una dirección), es casi seguro una multiplicación por constante disfrazada. `lea eax, [rax+rax*4]` es `x*5`, no "un acceso a memoria".

## División por constante: el número mágico

Dividir es carísimo, así que, en código optimizado, el compilador **casi nunca** usa `div` para dividir por una constante: lo habitual es que multiplique por un "número mágico" y desplace. Depende del compilador, la arquitectura y las opciones (sin optimizar, o con un divisor que no conoce en tiempo de compilación, sí vas a ver `div`/`idiv`).

```asm
; unsigned  x / 3
mov   eax, 0xAAAAAAAB     ; número mágico
mul   edx                 ; producto de 64 bits
shr   edx, 1              ; EDX = x / 3
```

Cuando veas una multiplicación por una constante aparentemente arbitraria (`0xAAAAAAAB`, `0x55555556`, `0xCCCCCCCD`…) seguida de un `shr`, es una **división por constante**, no un algoritmo secreto. Hay tablas y calculadoras para recuperar el divisor; lo importante es reconocer el patrón y no perder tiempo buscando sentido a la constante.

## Inlining: la función que desaparece

Con `-O2`, una función corta que llamás una vez puede **desaparecer**: el compilador copia su cuerpo donde se usaba (*inlining*). Entonces:

- No vas a encontrar un `call` a esa función.
- El código de la función aparece **mezclado** dentro de quien la llamaba.
- Varias funciones del fuente pueden colapsar en un solo bloque grande.

La consecuencia para el análisis: no asumas "una función del fuente = una función en el binario". Buscá el comportamiento, no el nombre.

## Vectorización: SSE donde esperabas un bucle

Un bucle que suma o copia un arreglo puede convertirse en instrucciones **packed** (`addps`, `movdqu`, `paddd`) que procesan varios elementos por vuelta. En vez de un bucle de 100 iteraciones de a 1, ves un bucle de 25 de a 4. Si un bucle "no tiene sentido" porque usa `xmm` y avanza de a 16 bytes, está vectorizado (ver la lección de punto flotante y SSE).

## Tail call: un `jmp` donde esperabas `call`

Si lo último que hace una función es llamar a otra y devolver su resultado, el compilador reemplaza `call f; ret` por un simple `jmp f` (*tail call*). Ahorra un marco de stack. El efecto al analizar: una función "termina" saltando a otra con `jmp`, sin `ret` propio. No es un salto sospechoso ni ofuscación: es una llamada final optimizada.

## Otros patrones frecuentes

| Patrón | Cómo se ve | Qué es |
|---|---|---|
| `xor eax, eax` | poner 0 | modismo para `eax = 0` |
| `test eax, eax` + `je` | en vez de `cmp eax, 0` | "¿es cero?" |
| `cmovcc` / `setcc` | decisión sin salto | el `if` se hizo sin bifurcar (ver lección de flujo) |
| `lea` con cuentas | aritmética | suma/multiplicación, no acceso a memoria |
| bloques reordenados | el camino "frío" (error) va al final | mejora la predicción de saltos |
| constantes plegadas | `mov eax, 480` donde el fuente decía `(a+b)*4` | *constant folding* en tiempo de compilación |

## Cómo convivir con esto

1. **Aprendé con `-O0`, analizá con `-O2`.** Compilá tu ejemplo en los dos modos y poné los listados lado a lado. Ver la misma lógica en ambas versiones entrena el ojo.
2. **Usá el decompilador.** Ghidra o Hex-Rays deshacen muchos de estos patrones: te muestran `x / 3` en vez del número mágico, y la función inlineada como una sola expresión. No es mágico, pero ahorra tiempo.
3. **Pensá en comportamiento, no en forma.** La pregunta no es "¿por qué hay un `lea` acá?", sino "¿qué valor queda en este registro al final?".

:::{practica} Práctica
1. Compilá una función `int f(int x){ return x*5 + x/3; }` con `-O0` y con `-O2`. Encontrá el `lea [rax+rax*4]` (el `*5`) y el número mágico (el `/3`).
2. Escribí dos funciones chicas donde una llame a la otra y compilá con `-O2`. ¿Desapareció la llamada (inlining)?
3. Hacé un bucle que sume un arreglo de 1000 `int` y compilá con `-O3 -mavx2`. ¿Ves registros `xmm`/`ymm` y avance de a varios elementos?
4. Abrí el `-O2` en Ghidra y compará el decompilado con tu fuente. ¿Recuperó la división por 3?
:::

## Preguntas de repaso

?? Ves `lea eax, [rax+rax*4]`. ¿Qué es?
!! Una multiplicación por 5 (`x + x*4`). `lea` se usa acá para aritmética, no para calcular una dirección.

?? Aparece `mov eax, 0xAAAAAAAB` seguido de `mul` y `shr`. ¿Qué está pasando?
!! Es una división por constante (por 3) implementada con un número mágico. El compilador evita `div`.

?? Una función termina con `jmp otra_funcion` en vez de `call` + `ret`. ¿Es sospechoso?
!! No. Es una *tail call*: la última acción era llamar y devolver, y el compilador la optimizó a un salto.

?? No encontrás el `call` a una función que sí está en el fuente. ¿Qué pudo pasar?
!! Inlining: el compilador copió su cuerpo dentro de quien la llamaba, así que no hay llamada separada.

## Antes de avanzar

Tenés que poder:

- Reconocer *strength reduction* (`lea`/shifts) y división por constante (número mágico).
- Explicar por qué una función del fuente puede no existir como función en el binario.
- Identificar un bucle vectorizado y una *tail call*.
- Usar un decompilador para deshacer estos patrones.

:::{nota} Puerta de salida
Si podés mirar un listado `-O2` y decir "esto es `x*5`, esto es `x/3`, esta función está inlineada" sin frustrarte, estás listo para binarios reales.
:::

## Fuentes de esta lección

- Agner Fog, *Optimizing subroutines in assembly language* y *Instruction tables* (patrones de código generado y costos).
- Documentación de **GCC** (`-O1/-O2/-O3`) y **LLVM/Clang** sobre pases de optimización.
- *Hacker's Delight* (Warren) para división por constantes y trucos aritméticos.

:::{nota} Capas de esta lección
**Conocimiento externo (agregado por esta edición):** todos los patrones de optimización. El corpus CLS usa binarios sin optimizar, así que este salto no estaba cubierto. **Recomendación editorial:** la estrategia "aprendé con Debug, analizá con Release" y los ejercicios.
:::
