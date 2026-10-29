---
title: "Etapa 2 · Punto flotante y SSE: los registros xmm"
description: "Cómo se ven las operaciones con float y double en x86/x64 de Windows, el FPU x87 histórico y las instrucciones SSE."
etapa: "Etapa 2 · Introducción al reversing"
---

# Punto flotante y SSE: los registros xmm

:::{aviso} De dónde sale esta lección
Este tema **no está en el corpus CLS**: es **conocimiento externo** que agregamos para completar la guía. El curso de CLS trabaja casi todo con enteros, así que el punto flotante quedaba sin cubrir. Lo incluimos porque aparece en cualquier binario de Windows real y, sin él, te trabás la primera vez que ves un registro `xmm`.
:::

:::{nota} Objetivo de la lección
Al terminar vas a poder reconocer una operación con `float`/`double` en un listado, leer las instrucciones SSE escalares más comunes (`movss`, `movsd`, `addsd`, `cvtsi2sd`, `ucomisd`) y entender por qué una comparación de flotantes se lee distinto de una de enteros.
:::

**Prerrequisitos:** instrucciones, flujo y registros (Etapa 2). **Duración sugerida:** 3 horas.

## Por qué vas a chocarte con esto

Apenas analices un binario que haga una cuenta con decimales —un precio, un porcentaje, una coordenada, un promedio— vas a ver registros `xmm0`, `xmm1`… e instrucciones terminadas en `ss`, `sd`, `ps` o `pd` que no estaban en la tabla de enteros. No es un tema avanzado: es el día a día de cualquier programa compilado hoy. Además, muchos `memcpy`/`memset` optimizados usan registros `xmm` para mover 16 bytes de una.

## Dos mundos: x87 y SSE

Hay dos formas de hacer punto flotante en x86, y conviene distinguirlas porque se ven muy distinto:

| | **x87 (FPU)** | **SSE / SSE2** |
|---|---|---|
| Época | Clásico; común en código de 32 bits | Estándar desde ~2003; **obligatorio en x64** |
| Registros | Pila `st(0)`…`st(7)` | `xmm0`…`xmm7` (32 bits) / `xmm0`…`xmm15` (64 bits) |
| Estilo | Basado en pila (como una calculadora RPN) | Basado en registros (como los enteros) |
| Instrucciones | `fld`, `fstp`, `faddp`, `fmul`, `fcomip` | `movss`, `movsd`, `addsd`, `mulsd`, `ucomisd` |

En 64 bits el compilador usa **casi siempre SSE**; vas a ver x87 sobre todo en binarios viejos de 32 bits.

## IEEE 754 en una cucharada

- Un **`float`** ocupa 4 bytes; un **`double`**, 8. No son enteros: tienen signo, exponente y mantisa.
- Por eso las constantes flotantes **no se ven como el número**. `1.0` en `double` es `0x3FF0000000000000`; `0.5` es `0x3FE0000000000000`. Suelen cargarse desde `.rdata`.
- Si en un `movsd xmm0, [0x...]` el valor cargado es `0x4059000000000000`, no es "un número raro": es `100.0` en `double`. Cualquier conversor IEEE 754 te lo traduce; no hace falta hacerlo a mano.

## Las instrucciones SSE que vas a ver

La clave está en el **sufijo**:

- `ss` = *scalar single* → un `float` (4 bytes).
- `sd` = *scalar double* → un `double` (8 bytes).
- `ps`/`pd` = *packed* → varios valores a la vez (vectorización; ver la lección de optimizaciones).

| Instrucción | Qué hace |
|---|---|
| `movss` / `movsd` | mueve un float / un double |
| `movaps` / `movups` | mueve 16 bytes (alineado / sin alinear) |
| `addsd`, `subsd`, `mulsd`, `divsd` | aritmética con double |
| `cvtsi2sd` | entero → double |
| `cvttsd2si` | double → entero (trunca) |
| `cvtss2sd` / `cvtsd2ss` | float ↔ double |
| `comiss` / `ucomisd` | **comparar** flotantes (actualiza EFLAGS) |
| `xorps xmm0, xmm0` | pone el registro en 0 (truco idiomático) |
| `pxor`, `andps`, `orps` | lógicas de 128 bits (a veces para el signo) |

:::{nota} `xorps xmm, xmm` no es "una lógica rara"
Igual que `xor eax, eax` pone `EAX` en cero, `xorps xmm0, xmm0` pone `xmm0` en cero. Es el modismo del compilador para inicializar un flotante en 0.0.
:::

## Ejemplo paso a paso: `double` en x64

```c
double promedio(double a, double b) {
    return (a + b) / 2.0;
}
```

En x64 de Windows, los `double` llegan en `xmm0` y `xmm1`, y el resultado vuelve en `xmm0`:

```asm
promedio:
    addsd   xmm0, xmm1              ; xmm0 = a + b
    movsd   xmm1, [rel dos]         ; xmm1 = 2.0  (0x4000000000000000)
    divsd   xmm0, xmm1              ; xmm0 = (a+b) / 2.0
    ret
dos: dq 0x4000000000000000          ; 2.0 en .rdata
```

Lo que tenés que reconocer: `xmm0`/`xmm1` traen los argumentos, `addsd` es la suma, la constante `2.0` se carga de datos y el resultado queda en `xmm0`. No hay `push`/`pop` de flotantes: viajan por registros `xmm`.

## Comparar flotantes es distinto

Una comparación de enteros usa `cmp` + `je/jg/jl`. Una de flotantes usa `ucomisd`/`comiss`, que actualiza `ZF`, `PF` y `CF` (no `SF`/`OF`), y después un salto **sin signo** (`ja`, `jae`, `jb`, `jbe`, `je`):

```asm
ucomisd xmm0, xmm1
jae     es_mayor_o_igual     ; usa CF/ZF, como una comparación sin signo
```

Además aparece el **flag de paridad (`PF`)**: se activa si alguno de los operandos es `NaN` (*not a number*). Por eso a veces ves un `jp`/`jnp` antes del salto real: el compilador está manejando el caso "no es un número". Si ves `ucomisd` seguido de `jp`, no te asustes: es el chequeo de NaN, no la condición principal.

## x87 en binarios viejos (lo mínimo)

En código de 32 bits podés encontrarte con la pila del FPU:

```asm
fld  qword [a]     ; empuja a en st(0)
fadd qword [b]     ; st(0) = a + b
fstp qword [res]   ; guarda st(0) en res y lo saca de la pila
```

Se lee como una calculadora de pila: `fld` empuja, las operaciones trabajan sobre `st(0)`, `fstp` guarda y saca. No necesitás dominarlo; alcanza con reconocer que **`f...` = punto flotante x87** y seguir el valor por la pila `st`.

:::{practica} Práctica
1. Compilá `promedio.c` con `gcc -O0` (x64) y mirá el listado: ubicá `xmm0`, `xmm1`, `addsd`, `divsd` y la constante `2.0` en `.rdata`.
2. Tomá la constante que carga tu binario y convertila con un conversor IEEE 754. ¿Coincide con `2.0`?
3. Agregá una comparación `if (a > b)` y mirá cómo aparece `ucomisd` + salto sin signo (y quizás un `jp`).
4. Compilá una versión de 32 bits con `-mfpmath=387` y compará: ahora deberías ver `fld`/`faddp` en vez de `xmm`.
:::

## Preguntas de repaso

?? ¿Qué significan los sufijos `ss`, `sd`, `ps` y `pd`?
!! `ss` = un `float` (scalar single); `sd` = un `double` (scalar double); `ps`/`pd` = varios valores a la vez (packed, vectorizado).

?? Ves `xorps xmm0, xmm0`. ¿Qué hace?
!! Pone `xmm0` en 0.0. Es el modismo para inicializar un flotante en cero, igual que `xor eax, eax` con enteros.

?? ¿Por qué después de `ucomisd` aparece a veces un `jp`?
!! Porque la comparación de flotantes activa el flag de paridad si hay un `NaN`. El `jp`/`jnp` maneja ese caso antes del salto principal.

?? Un `movsd xmm0, [rel k]` carga `0x3FF0000000000000`. ¿Qué número es?
!! `1.0` en `double`. Las constantes flotantes se ven como su codificación IEEE 754, no como el número decimal.

## Antes de avanzar

Tenés que poder:

- Reconocer una operación con `float`/`double` por los registros `xmm` y los sufijos `ss`/`sd`.
- Leer una comparación de flotantes (`ucomisd` + salto sin signo + chequeo de NaN).
- Traducir una constante IEEE 754 con una herramienta.
- Distinguir x87 (`f...`, pila `st`) de SSE (`xmm`).

:::{nota} Puerta de salida
Si podés leer `promedio` en assembly y explicar cómo viajan los argumentos y el resultado en `xmm`, ya no te va a frenar el punto flotante.
:::

## Fuentes de esta lección

- *Intel 64 and IA-32 Architectures Software Developer's Manual*, vol. 1 (FPU x87) y vol. 2 (instrucciones SSE/SSE2). Referencia primaria del repertorio de instrucciones.
- *Microsoft x64 calling convention*: paso de `float`/`double` en registros `xmm`.
- Estándar **IEEE 754** para la codificación de `float` y `double`.

:::{nota} Capas de esta lección
**Conocimiento externo (agregado por esta edición):** todo el contenido (x87, SSE, IEEE 754, convención de `xmm`). **No** proviene del corpus CLS, que trabaja con enteros. **Recomendación editorial:** los ejemplos `promedio` y la práctica con conversor IEEE 754.
:::
