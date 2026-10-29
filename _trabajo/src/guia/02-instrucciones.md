---
title: "Etapa 2 · Instrucciones: mover, calcular y manipular bits"
description: "El repertorio mínimo de instrucciones x86/x64, con ejemplos numéricos explicados paso a paso."
etapa: "Etapa 2 · Introducción al reversing"
---

# Instrucciones: mover, calcular y manipular bits

:::{nota} Objetivo de la lección
Al terminar vas a poder leer un bloque de instrucciones y decir qué valor queda en cada registro, distinguiendo transferencias, operaciones aritméticas, lógicas, desplazamientos y accesos a memoria.
:::

**Prerrequisitos:** registros y flags. **Duración sugerida:** 5 horas. Estimación aproximada.

## Cómo se lee una instrucción

Casi todas las instrucciones tienen la forma:

```asm
MNEMÓNICO destino, fuente
```

La operación se calcula con los dos operandos y el resultado se guarda en el **destino** (el primero). `mov eax, ebx` copia `EBX` en `EAX`; `add eax, ebx` suma y guarda en `EAX`.

Los corchetes significan "el contenido de esta dirección":

```asm
mov eax, 0x401000      ; EAX = el número 0x401000
mov eax, [0x401000]    ; EAX = lo que hay en la dirección 0x401000
```

Esa diferencia es la que separa un puntero de un valor. El capítulo 02 la explica al mover un valor desde memoria a `EAX`: los bytes `36 00 00 38` en la dirección se convierten en `0x38000036` en el registro ({{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_02 Instrucciones 1_02 Instrucciones 1.txt|Reversing desde cero, cap. 02}}, 00:07:00–00:08:00).

## Transferencias

### `MOV`

```asm
mov eax, 5          ; inmediato -> registro
mov eax, ebx        ; registro -> registro
mov eax, [0x403000] ; memoria -> registro
mov [0x403000], eax ; registro -> memoria
```

No modifica flags. No se puede `mov` de memoria a memoria: hay que pasar por un registro.

### `LEA`

`LEA` (*load effective address*) calcula una dirección y la guarda, **sin leer memoria**:

```asm
lea eax, [ebx + ecx*4 + 8]
```

Si `EBX = 0x1000` y `ECX = 2`, `EAX = 0x1000 + 8 + 8 = 0x1010`. No importa qué haya en `0x1010`: no se lee. Se usa para aritmética de punteros y, de paso, como una multiplicación rápida. El capítulo 12 lo muestra en la práctica ({{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_12 Practica de Instrucciones_12 Practica de Instrucciones.txt|Reversing desde cero, cap. 12}}, 00:08:07).

### `MOVSX` y `MOVZX`

Copian un valor más chico a un registro más grande, rellenando los bits altos:

```asm
; AX = 0x8384
movsx eax, ax   ; EAX = 0xFFFF8384  (rellena con el bit de signo)
movzx eax, ax   ; EAX = 0x00008384  (rellena con ceros)
```

`MOVSX` interpreta el origen como con signo; `MOVZX`, como sin signo. En el capítulo 12, `0x8384` es mayor que `0x7FFF`, así que como `WORD` con signo es negativo y `MOVSX` rellena con `FF` (00:07:21–00:08:00).

### `XCHG`

Intercambia los dos operandos. No hay destino ni fuente: los dos cambian.

```asm
; EAX = 0x20, EBX = 0x40
xchg eax, ebx
; EAX = 0x40, EBX = 0x20
```

:::{nota} En el Curso IDA: editar una instrucción (y qué pasa después)
El Curso IDA edita estas instrucciones desde **Edit → Patch Program → Assemble** sobre el crackme de Cruehead. Un detalle útil: si la instrucción nueva ocupa **menos** bytes que la vieja, el byte que sobra queda mostrado como **dato** (`db 0xC0`) y la función aparece "corrupta"; se lo reemplaza con un **`NOP`** (`0x90`, relleno que no hace nada) para que vuelva a verse como código. `LEA`, acá arriba, el curso la usa justamente para obtener la dirección de variables y argumentos ([Curso IDA · tute 4, Transferencia](../ida_tutes/4.html) y [tute 5, `LEA`](../ida_tutes/5.html)).
:::

## Aritmética

### `ADD` y `SUB`

```asm
add eax, ebx    ; EAX = EAX + EBX
sub eax, 4      ; EAX = EAX - 4
```

Actualizan `ZF`, `SF`, `CF` y `OF`. El capítulo 02 las practica con registros y memoria (00:10:00–00:18:00).

### `INC` y `DEC`

Suman o restan 1. Son más cortas que `add eax, 1` y **no modifican `CF`** (sí `ZF`, `SF`, `OF`). En el capítulo 06 se ve `INC EAX` con `EAX = 0xFFFFFFFF` (pasa a 0) y `DEC EAX` con `EAX = 1` (queda 0 y activa `ZF`) ({{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_06 Instrucciones 3_06 Instrucciones 3.txt|Reversing desde cero, cap. 06}}, 00:20:03–00:21:00).

### `MUL`, `IMUL`, `DIV`, `IDIV`

Ya las vimos en registros. Para 32 bits: `MUL` usa `EDX:EAX`; `DIV` divide `EDX:EAX`. `IMUL`/`IDIV` son las versiones con signo. En 64 bits, `RDX:RAX`.

## Lógica de bits

| Instrucción | Qué hace | Ejemplo (8 bits) |
|---|---|---|
| `AND` | 1 solo si ambos bits son 1 | `0x11 & 0x0F = 0x01` |
| `OR` | 1 si alguno es 1 | `0x11 OR 0x0F = 0x1F` |
| `XOR` | 1 si son distintos | `0x11 ^ 0x0F = 0x1E` |
| `NOT` | Invierte todos los bits | `~0x11 = 0xEE` (8 bits) o `0xFFFFFFEE` (32) |

El capítulo 08 las explica con tablas de verdad y las verifica en el debugger ({{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_08 Instrucciones 4_08 Instrucciones 4.txt|Reversing desde cero, cap. 08}}, 00:07:00–00:17:00).

`XOR EAX, EAX` es la forma idiomática de poner un registro en cero: ocupa 2 bytes y activa `ZF`. `MOV EAX, 0` ocupa 5 bytes y no toca flags. Esa diferencia de tamaño es la que hace que los compiladores prefieran `XOR`.

### Desplazamientos

```asm
shl eax, 1    ; desplaza 1 bit a la izquierda = multiplicar por 2
shr eax, 1    ; desplaza 1 bit a la derecha  = dividir por 2 (sin signo)
sar eax, 1    ; desplazamiento aritmético (conserva el signo)
rol eax, 4    ; rota a la izquierda: el bit que sale entra por la derecha
ror eax, 4    ; rota a la derecha
```

Con `EAX = 0x11`:

```text
shl eax, 2   -> 0x44     (0x11 * 4)
shr eax, 2   -> 0x04     (0x11 / 4, parte entera)
```

`SHL`/`SHR` **pierden** los bits que salen; `ROL`/`ROR` los reinyectan por el otro extremo. El capítulo 08 lo muestra con `0x11 << 2 = 0x44` y `0x44 >> 2 = 0x11` (00:24:33–00:28:11).

## Comparar sin restar: `CMP` y `TEST`

`CMP a, b` hace `a - b`, actualiza flags y **descarta el resultado**. `TEST a, b` hace `a AND b`, actualiza flags y también descarta el resultado.

```asm
cmp eax, 4      ; ¿EAX == 4?  -> ZF=1 si son iguales
test eax, eax   ; ¿EAX == 0?  -> ZF=1 si es cero
```

`TEST EAX, EAX` es la forma habitual de preguntar "¿este registro es cero?" sin modificar nada. El capítulo 09 lo explica y lo usa con `JZ` ({{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_09 Instrucciones 5_09 Instrucciones 5.txt|Reversing desde cero, cap. 09}}, 00:31:32–00:33:00).

## Pila y cadenas

```asm
push eax        ; ESP -= 4 ; [ESP] = EAX
pop  ebx        ; EBX = [ESP] ; ESP += 4
pushad          ; guarda EAX, ECX, EDX, EBX, ESP, EBP, ESI, EDI (32 bytes)
popad           ; los restaura
```

`PUSHAD`/`POPAD` se usan para preservar registros alrededor de una llamada. Dato fino: `POPAD` **no** restaura `ESP`, aunque `PUSHAD` lo haya guardado (cap. 12, 00:21:07).

Las instrucciones de cadena operan sobre `ESI` (origen) y `EDI` (destino):

```asm
rep movsb      ; copia ECX bytes de [ESI] a [EDI]
repe cmpsb     ; compara [ESI] y [EDI] mientras sean iguales
lodsb          ; AL = [ESI]; ESI++
stosb          ; [EDI] = AL; EDI++
repne scasb    ; busca AL en [EDI] mientras no lo encuentre
```

El capítulo 12 las recorre con un ejemplo concreto: `ESI` apunta a `"core"` (`0x402012`), `EDI` a `"core security"` (`0x402031`) y `REPNE SCASB` busca el byte `0x65` (`'e'`) (00:37:11–00:38:30).

## Ejemplo paso a paso: un bloque completo

```asm
mov  eax, 0x11
mov  ecx, 0x0F
xor  eax, ecx
and  eax, 0x1F
shl  eax, 2
mov  ebx, eax
sub  ebx, 0x44
```

| Paso | Instrucción | EAX | EBX | Flags relevantes |
|---|---|---|---|---|
| 1 | `mov eax, 0x11` | `0x11` | ? | sin cambio |
| 2 | `mov ecx, 0x0F` | `0x11` | ? | sin cambio |
| 3 | `xor eax, ecx` | `0x1E` | ? | `ZF=0`, `SF=0` |
| 4 | `and eax, 0x1F` | `0x1E` | ? | `ZF=0` |
| 5 | `shl eax, 2` | `0x78` | ? | `CF` = último bit que salió |
| 6 | `mov ebx, eax` | `0x78` | `0x78` | sin cambio |
| 7 | `sub ebx, 0x44` | `0x78` | `0x34` | `ZF=0`, `SF=0`, `CF=0` |

Comprobación: `0x11 ^ 0x0F = 0x1E`; `0x1E & 0x1F = 0x1E`; `0x1E << 2 = 0x78`; `0x78 - 0x44 = 0x34`. Todos los valores entran en 8 bits, así que no hay acarreo.

## Práctica

1. Ejecutá el bloque anterior en x64dbg y completá la tabla con los valores reales.
2. Cambiá `mov eax, 0x11` por `mov eax, 0xFFFFFFFF` y predecí qué pasa en cada paso.
3. Escribí una secuencia de tres instrucciones que deje `EAX = 0` sin usar `mov`.
4. ¿Qué diferencia hay entre `mov eax, [ebx]` y `lea eax, [ebx]`?
5. Traducí a assembly: `if (x == 0) return;` con `x` en `EAX`.
6. Explicá por qué `INC` no sirve para detectar acarreo sin signo.

## Preguntas de repaso

**1. ¿Qué significa que el resultado se guarda en el primer operando?**
Que en `add eax, ebx` el resultado queda en `EAX`, no en `EBX`. El segundo operando se lee pero no se modifica.

**2. ¿`LEA` lee memoria?**
No. Calcula la dirección efectiva de la expresión entre corchetes y la guarda. Es aritmética de punteros.

**3. ¿Qué hace `XOR EAX, EAX` y por qué se usa?**
Pone `EAX` en cero, ocupa menos bytes que `MOV EAX, 0` y actualiza flags. Es la forma idiomática de limpiar un registro.

**4. ¿Cuál es la diferencia entre `SHL` y `ROL`?**
`SHL` desplaza y descarta el bit que sale; `ROL` lo reinyecta por el otro extremo. `SHL` equivale a multiplicar por 2; `ROL` no es una multiplicación.

**5. ¿`CMP` guarda el resultado de la resta?**
No. Solo actualiza flags. Los operandos quedan intactos.

**6. ¿Por qué `TEST EAX, EAX` es útil?**
Porque activa `ZF` si `EAX` es cero, sin modificar el registro. Es la forma estándar de comprobar un valor nulo.

## Antes de avanzar

Tenés que poder:

- Leer un bloque de 10 instrucciones y calcular el valor final de los registros.
- Distinguir `mov` de `lea` y `mov` de `movsx`/`movzx`.
- Explicar qué flags cambian `add`, `sub`, `inc`, `and`, `shl` y `cmp`.
- Reconocer las instrucciones de cadena y su relación con `ESI`/`EDI`.

:::{nota} Puerta de salida
Si podés resolver el bloque del ejemplo sin ejecutarlo y después verificarlo en el debugger, estás listo para el flujo de control.
:::

## Fuentes de esta lección

- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_02 Instrucciones 1_02 Instrucciones 1.txt|Reversing desde cero, cap. 02}} — `MOV`, `XCHG`, `ADD`, `SUB`, memoria y corchetes.
- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_04 Instrucciones 2_04 Instrucciones 2.txt|Reversing desde cero, cap. 04}} — flags, `MUL` y `DIV`.
- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_06 Instrucciones 3_06 Instrucciones 3.txt|Reversing desde cero, cap. 06}} — `CALL`, `RET`, `JMP`, `PUSH`/`POP`, `INC`/`DEC`.
- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_08 Instrucciones 4_08 Instrucciones 4.txt|Reversing desde cero, cap. 08}} — lógicas y desplazamientos.
- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_09 Instrucciones 5_09 Instrucciones 5.txt|Reversing desde cero, cap. 09}} — `CMP`, `TEST`, `LEAVE`.
- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_12 Practica de Instrucciones_12 Practica de Instrucciones.txt|Reversing desde cero, cap. 12}} — práctica con `MOVSX`/`MOVZX`, `LEA`, `LOOP` y cadenas.
- [Curso IDA · tutes 4–6](../ida_tutes/4.html) — las mismas instrucciones en IDA: editar con *Assemble*, el byte sobrante como `db` y el relleno `NOP`; `LEA` para direcciones; regla de `ADD` (no se permiten dos operandos en memoria a la vez).

:::{nota} Capas de esta lección
**Contenido observado en CLS:** los valores de los ejemplos (`0x11`, `0x0F`, `0x44`, `0x8384`, `"core"`) y la secuencia de instrucciones de los capítulos 02 a 12. **Conocimiento externo:** la tabla de operaciones y la semántica precisa de cada flag. **Recomendación editorial:** el bloque integrador y los ejercicios.
:::
