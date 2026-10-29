---
title: "Etapa 2 · Flujo: comparar, saltar y repetir"
description: "Cómo se convierte un if, un while y un switch en comparaciones, saltos condicionales y tablas de salto."
etapa: "Etapa 2 · Introducción al reversing"
---

# Flujo: comparar, saltar y repetir

:::{nota} Objetivo de la lección
Al terminar vas a poder reconstruir un `if/else`, un bucle y un `switch` a partir de un listado de assembly, eligiendo el salto correcto según el dato sea con signo o sin signo.
:::

**Prerrequisitos:** instrucciones y flags. **Duración sugerida:** 4 horas. Estimación aproximada.

## La idea central

El procesador no tiene `if`. Tiene instrucciones que comparan y actualizan flags, y saltos que se toman o no según esos flags. Un `if` en C se convierte en:

```asm
cmp  eax, 4
jne  else_1      ; si no es igual, salta al else
; bloque del if
jmp  fin
else_1:
; bloque del else
fin:
```

Leer flujo es reconstruir ese patrón: **comparación → salto condicional → bloques → salto incondicional al final**.

## `CMP` y `TEST` en detalle

`CMP a, b` calcula `a - b` y descarta el resultado. Los flags quedan como si hubieras restado:

| Caso | `ZF` | `CF` | `SF` | `OF` |
|---|---|---|---|---|
| `a == b` | 1 | 0 | según resultado 0 | 0 |
| `a > b` (sin signo) | 0 | 0 | — | — |
| `a < b` (sin signo) | 0 | 1 | — | — |
| `a > b` (con signo) | 0 | — | 0 | 0 |
| `a < b` (con signo) | 0 | — | 1 | 0 |

`TEST a, b` hace `a AND b` y descarta el resultado. `TEST EAX, EAX` activa `ZF` si `EAX` es cero; es la forma estándar de preguntar "¿es nulo?".

El capítulo 09 lo muestra con `CMP EAX=4, EBX=4` (activa `ZF` y deja los registros intactos) y con `TEST EAX, EAX` seguido de `JZ` ({{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_09 Instrucciones 5_09 Instrucciones 5.txt|Reversing desde cero, cap. 09}}, 00:01:05–00:06:00 y 00:31:32–00:33:00).

## La tabla de saltos condicionales

| Instrucción | Salta si... | Uso típico |
|---|---|---|
| `JE` / `JZ` | `ZF = 1` | igual / cero |
| `JNE` / `JNZ` | `ZF = 0` | distinto / no cero |
| `JA` / `JNBE` | `CF = 0` y `ZF = 0` | mayor, **sin signo** |
| `JAE` / `JNB` / `JNC` | `CF = 0` | mayor o igual, sin signo |
| `JB` / `JNAE` / `JC` | `CF = 1` | menor, sin signo |
| `JBE` / `JNA` | `CF = 1` o `ZF = 1` | menor o igual, sin signo |
| `JG` / `JNLE` | `ZF = 0` y `SF = OF` | mayor, **con signo** |
| `JGE` / `JNL` | `SF = OF` | mayor o igual, con signo |
| `JL` / `JNGE` | `SF ≠ OF` | menor, con signo |
| `JLE` / `JNG` | `ZF = 1` o `SF ≠ OF` | menor o igual, con signo |
| `JS` / `JNS` | `SF = 1` / `SF = 0` | signo |
| `JO` / `JNO` | `OF = 1` / `OF = 0` | desborde con signo |

No hace falta memorizarla: alcanza con saber que **`J` + letra** indica la condición (`E` igual, `N` no, `A` arriba, `B` abajo, `G` mayor, `L` menor) y que las variantes `A/B` son sin signo y `G/L` con signo.

## Cómo se codifica un salto (y hasta dónde llega)

Hasta acá vimos *qué* hace cada salto; falta *cómo se escribe en bytes*, porque al parchear —o al leer un salto en el editor hexadecimal— trabajás con esos bytes. El **Curso IDA** lo muestra byte a byte sobre un `CRACKME` propio ([Curso IDA · tute 7, Control de flujo](../ida_tutes/7.html)):

- **Salto corto (`JMP SHORT`)** → opcode `EB` + **1 byte** de desplazamiento. El destino se calcula como **inicio de la instrucción + 2 + desplazamiento** (el 2 es el largo del salto corto). El alcance es chico: `0x7F` es el **máximo hacia adelante** y `0x80` el **máximo hacia atrás**.
- Un desplazamiento `FE` (−2) hace que el salto caiga **sobre sí mismo**: es el **loop infinito** clásico (`EB FE`).
- **Salto largo (`JMP`/`Jcc` near)** → opcode `E9` + un **dword** de desplazamiento, para alcanzar direcciones lejanas. La distancia se calcula como **destino − inicio − 5** (5 = largo del salto largo).

:::{nota} Probarlo sin romper la base de datos
El tute edita esos bytes con **Patch Byte** y **KeyPatch** dentro de IDA, y antes hace un **snapshot de la IDB** (*View → Database snapshot manager*) para volver atrás con *Restore* si el cambio rompe una función. Hacé lo mismo antes de experimentar: cambiás un `0x05` por `0x7F` o `0x80`, ves el efecto y, si algo se rompe, restaurás.
:::

## Ejemplo paso a paso: el mismo dato, dos interpretaciones

```asm
mov eax, 0xFFFFFFFF
cmp eax, 2
jg  mayor_firmado
ja  mayor_sin_signo
```

- `CMP` calcula `0xFFFFFFFF - 2`. Como número **sin signo**, `0xFFFFFFFF` es 4.294.967.295, mucho mayor que 2: `CF = 0`, `ZF = 0`, así que `JA` **salta**.
- Como número **con signo**, `0xFFFFFFFF` es −1, menor que 2: `SF = 1`, `OF = 0`, `SF ≠ OF`, así que `JG` **no salta**; el que saltaría es `JL`.

Es el ejemplo que usa el capítulo 09 (00:24:30–00:25:30). La lección: **el mismo `cmp` puede producir saltos opuestos según la instrucción que lo sigue**. Si el código usa `JA/JB`, el autor pensó el dato como sin signo; si usa `JG/JL`, como con signo. Ese detalle cambia por completo la reconstrucción de una comparación de contraseñas o de un índice.

## Bucles

### `while` / `for`

```c
while (i < 10) { ...; i++; }
```

Se compila a:

```asm
mov ecx, 0
loop_start:
cmp ecx, 10
jge loop_end      ; si ecx >= 10, salir
; cuerpo
inc ecx
jmp loop_start
loop_end:
```

El salto de salida es la **negación** de la condición: el cuerpo se ejecuta mientras se cumple, así que se sale cuando deja de cumplirse.

### `do/while`

La condición va al final, después del cuerpo. Se ejecuta al menos una vez.

### `LOOP`

`LOOP etiqueta` decrementa `ECX` y salta si `ECX ≠ 0`. Es una instrucción compacta pero más lenta que `dec ecx; jnz`. En el capítulo 12 se ve `LOOP` con `ECX` como contador (00:24:06).

### Bucles con cadenas

`REP MOVSB`, `REPE CMPSB` y `REPNE SCASB` repiten una operación mientras se cumple una condición y `ECX` no llegue a cero. Son bucles "de hardware" que el procesador ejecuta sin un `jmp` explícito.

## `switch`: la tabla de saltos

Un `switch` con casos consecutivos se compila a una **tabla de direcciones**:

```asm
cmp eax, 3
ja  default
jmp [tabla + eax*4]
```

La tabla contiene las direcciones de cada `case`; `jmp [tabla + eax*4]` salta a la que corresponde al índice. En el desensamblador se ve como un `jmp` con un operando indexado, seguido de una zona de datos con direcciones (a veces en `.rdata`).

Para reconstruirlo: identificá la comparación de rango (`cmp` + `ja default`), la tabla y el orden de las entradas. Si los casos no son consecutivos, el compilador puede usar una cadena de comparaciones en lugar de una tabla.

## Decisiones sin salto: `CMOVcc`

No toda decisión produce un salto. La familia `CMOVcc` (*conditional move*) **mueve un valor solo si se cumple una condición**, mirando los mismos flags que los `Jcc`. Por ejemplo, `CMOVZ eax, ebx` copia `EBX` en `EAX` únicamente si `ZF = 1`; si no, `EAX` queda como estaba.

```asm
cmp  byte ptr [esi], 0x41   ; ¿el primer carácter es 'A'?
mov  ecx, 0x31
cmovz esi_byte, ecx         ; si era 'A' (ZF=1), lo reemplaza por 0x31; si no, lo deja
```

La consecuencia para el reversing es importante: con `CMOVcc` **no hay dos bloques** (uno para el camino bueno y otro para el malo) ni un salto visible. La comparación y la elección ocurren en el mismo bloque, así que no hay un "salto para parchear" evidente. El capítulo 16 usa justamente esto para que un crackme no tenga bloques separados de "chico bueno" y "chico malo": decide con un `CMOVZ` y no con un `Jcc` ({{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_16 Ejercicio 3 - Análisis Dinámico y Estático_16 Ejercicio.txt|Reversing desde cero, cap. 16}}; transcripción .txt, sin marcas de tiempo).

Cuando no encuentres el salto que decide, buscá un `CMOVcc`, un `SETcc` (que deja 0 o 1 en un byte según la condición) o una operación aritmética que use el flag: la decisión puede estar ahí, sin bifurcación.

## Ejemplo integrador: el `if` del capítulo 15

El programa de práctica del capítulo 15 pide dos números y aplica:

```c
if (a > 50 || b < 50) { error; }
if ((a + b) * 4 == 480) { correcto; } else { incorrecto; }
```

En assembly, la primera condición se parte en dos comparaciones con saltos:

```asm
cmp eax, 50
jg  error          ; a > 50 -> error
cmp ebx, 50
jl  error          ; b < 50 -> error
```

La segunda usa una suma, un desplazamiento y una comparación:

```asm
add eax, ebx
shl eax, 2         ; (a+b) * 4
cmp eax, 480
jne incorrecto
```

El capítulo lo reconstruye leyendo los saltos y los comentarios que va agregando en IDA, y luego lo confirma en el debugger con `40` y `80` ({{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_15 Ejercicio 2 - Análisis estático_15 Ejercicio 2 - Análisis estático.txt|Reversing desde cero, cap. 15}}, 00:10:00–00:19:00).

:::{aviso} El error de leer el salto al revés
Un salto "hacia el bloque malo" no significa que la condición sea verdadera: puede ser la negación. Antes de escribir el `if`, preguntate **qué camino toma el programa cuando el salto se produce** y **qué camino cuando no**. El capítulo 09 insiste en esto al explicar cada `Jcc` por su condición (00:07:00–00:12:00).
:::

## Práctica

1. Traducí a C:

```asm
cmp eax, 10
jl  menor
mov ebx, 1
jmp fin
menor:
mov ebx, 0
fin:
```

2. Escribí en C un `for` que sume los números del 1 al 10 y compilalo con `-O0`. Identificá el contador, la comparación y el salto de salida.
3. ¿Qué diferencia hay entre `JA` y `JG`? Dame un ejemplo con `0xFFFFFFFF`.
4. Reconstruí un `switch` de tres casos a partir de una tabla de saltos inventada por vos. Dibujá la tabla y el `jmp` indexado.
5. En el programa del capítulo 15, cambiá `40 80` por `50 70`. ¿Sigue dando 480? ¿Qué condición falla?

## Preguntas de repaso

**1. ¿`CMP` modifica los operandos?**
No. Solo actualiza flags. Es una resta "de prueba".

**2. ¿Cómo se sale de un `while`?**
Con un salto condicional que se toma cuando la condición deja de cumplirse, o con un `jmp` al final si el cuerpo tiene un `break`.

**3. ¿Qué indica `JA` que no indica `JG`?**
`JA` compara sin signo; `JG`, con signo. Con `0xFFFFFFFF` y `2`, `JA` salta y `JG` no.

**4. ¿Cómo se reconoce una tabla de salto?**
Por un `jmp` con operando indexado (`[tabla + registro*4]`) y una zona de datos con direcciones consecutivas, generalmente precedida por una comparación de rango.

**5. ¿`LOOP` usa qué registro?**
`ECX`. Decrementa y salta si no llegó a cero.

## Antes de avanzar

Tenés que poder:

- Reconstruir un `if/else` a partir de `cmp` + `jcc` + `jmp`.
- Elegir `JA/JB` o `JG/JL` según el tipo del dato.
- Reconocer un bucle `while`, un `do/while` y un `for`.
- Explicar una tabla de saltos.

:::{nota} Puerta de salida
Si podés mirar un bloque con dos saltos y decir qué camino toma con un valor concreto, estás listo para las llamadas a funciones.
:::

## Fuentes de esta lección

- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_09 Instrucciones 5_09 Instrucciones 5.txt|Reversing desde cero, cap. 09}} — `CMP`, `TEST`, `JE/JNE/JA/JB/JG/JL`, `LEAVE`.
- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_16 Ejercicio 3 - Análisis Dinámico y Estático_16 Ejercicio.txt|Reversing desde cero, cap. 16}} — `CMOVcc`: decidir sin salto, un crackme sin bloques separados de bueno/malo.
- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_12 Practica de Instrucciones_12 Practica de Instrucciones.txt|Reversing desde cero, cap. 12}} — `LOOP` y comparaciones en un binario real.
- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_15 Ejercicio 2 - Análisis estático_15 Ejercicio 2 - Análisis estático.txt|Reversing desde cero, cap. 15}} — reconstrucción de condiciones.
- [Curso IDA · tute 7, Control de flujo](../ida_tutes/7.html) — codificación de los saltos (`EB`/`E9`), alcance ±`0x7F`/`0x80`, `EB FE` = loop infinito, y cómo parchearlos en IDA con snapshot de la IDB.
- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Videos y material adicional Ingenieria Inversa/Videos_Video29_Video29.txt|Videos y material adicional, Video 29}} — `IF/ELSE` compilado a `CMP` + saltos.
- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Videos y material adicional Ingenieria Inversa/Videos_Video30_Video30.txt|Videos y material adicional, Video 30}} — bucles y pila.

:::{nota} Capas de esta lección
**Contenido observado en CLS:** la tabla de saltos del capítulo 09, el ejemplo `0xFFFFFFFF` contra `2`, el `LOOP` del capítulo 12 y el `if` del capítulo 15. **Conocimiento externo:** la tabla completa de `Jcc` y el patrón de tabla de saltos. **Recomendación editorial:** los ejercicios y el ejemplo integrador.
:::
