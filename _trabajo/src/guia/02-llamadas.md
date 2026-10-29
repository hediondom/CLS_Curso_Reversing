---
title: "Etapa 2 · Llamadas, convenciones y marcos de función"
description: "Qué hace CALL, cómo se pasan los argumentos en 32 y 64 bits y cómo reconocer la convención de una función."
etapa: "Etapa 2 · Introducción al reversing"
---

# Llamadas, convenciones y marcos de función

:::{nota} Objetivo de la lección
Al terminar vas a poder seguir un `call` hasta su destino, calcular la dirección de retorno, identificar los argumentos de una función en 32 y 64 bits y decir quién limpia el stack.
:::

**Prerrequisitos:** flujo, stack y registros. **Duración sugerida:** 4 horas. Estimación aproximada.

## `CALL` y `RET`

`call destino` hace dos cosas:

1. Empuja en el stack la dirección de la instrucción **siguiente** (el *return address*).
2. Salta a `destino`.

`ret` hace lo inverso: saca el return address del stack y salta ahí.

Ejemplo del capítulo 06: un `call` en `0x00401013` (5 bytes) deja `0x00401018` en el tope del stack; la rutina hace `nop; ret` y vuelve a `0x00401018` ({{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_06 Instrucciones 3_06 Instrucciones 3.txt|Reversing desde cero, cap. 06}}, 00:00:53–00:03:10).

```asm
0x401013: call 0x40102C     ; push 0x401018 ; jmp 0x40102C
0x401018: ...               ; acá vuelve
```

`ret n` (por ejemplo `ret 0x10`) hace lo mismo y además suma `n` a `ESP` después de sacar el return address. Se usa en la convención `stdcall` para que la función llamada limpie los argumentos. En el ejemplo del capítulo 06, `ret 0x10` mueve el stack `0x10 + 4 = 0x14` (00:08:38–00:09:30).

## `call` directo e indirecto

```asm
call 0x401000          ; directo: el destino está en el opcode (E8 + desplazamiento)
call dword ptr [0x403000]  ; indirecto: el destino está en la memoria (FF15)
```

El indirecto es el que se usa para llamar APIs a través de la IAT. En el capítulo 06, `call dword ptr [0x402018]` no salta a `0x402018` sino a lo que hay allí; el capítulo 05 lo muestra con una API de `kernel32` ({{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_05 Virtual Adress, RVA, Offsets y Desplazamientos_05 Virtual Adress, RVA, Offsets y Desplazamientos.txt|Reversing desde cero, cap. 05}}, 00:13:00–00:18:00).

## Convenciones de llamada

Una **convención de llamada** es el acuerdo sobre tres cosas: dónde van los argumentos, quién limpia el stack y qué registros se preservan.

### 32 bits

| Convención | Argumentos | Limpia el stack | Registros volátiles |
|---|---|---|---|
| `cdecl` | En el stack, de derecha a izquierda | El llamador | `EAX`, `ECX`, `EDX` |
| `stdcall` | En el stack, de derecha a izquierda | La función (`ret n`) | `EAX`, `ECX`, `EDX` |
| `fastcall` | `ECX`, `EDX` y el resto en el stack | La función | `EAX`, `ECX`, `EDX` |
| `thiscall` | `ECX` = `this`; resto en el stack | La función | `EAX`, `ECX`, `EDX` |

`cdecl` es la convención por defecto de C; por eso las funciones variádicas (`printf`) la usan: solo el llamador sabe cuántos argumentos pasó. `stdcall` es la de la API de Windows (`MessageBoxA`, `CreateThread`). `thiscall` es la de los métodos de clase en C++.

**Cómo reconocerlas en el listado:**

- Si después del `call` hay un `add esp, N`, es `cdecl`: el llamador limpia.
- Si la función termina en `ret N`, es `stdcall` o `fastcall`: la función limpia.
- Si el primer argumento llega en `ECX`, es `fastcall` o `thiscall`.

El video 28 del curso de OllyDbg muestra el mismo concepto con procedimientos propios: `CALL`/`RET`, variables locales y argumentos en la pila ({{src:CLS_resultados_intermedios/transcripciones/extraidos/Videos y material adicional Ingenieria Inversa/Videos_Video28_Video28.txt|Videos y material adicional, Video 28}}, 00:00:00–00:05:00).

### 64 bits

En x64 hay una sola convención para el código de Windows: los primeros cuatro argumentos enteros van en `RCX`, `RDX`, `R8` y `R9`; el resto, en el stack. El llamador reserva **32 bytes de shadow space** antes del `call` y limpia el stack después. Los registros `RAX`, `RCX`, `RDX`, `R8`–`R11` son volátiles; `RBX`, `RBP`, `RDI`, `RSI`, `R12`–`R15` se preservan.

El capítulo 18 lo muestra con `main`: los tres argumentos llegan en `RCX`, `RDX` y `R8`, y las variables locales se referencian como `[rsp+0xNN]` ({{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_18 Funciones basadas en EBP vs basadas en ESP_18 Funciones basadas en EBP vs basadas en ESP.txt|Reversing desde cero, cap. 18}}, 00:13:00–00:20:00).

:::{aviso} En 64 bits los argumentos no se cargan "en orden"
Como los argumentos no se apilan uno tras otro con `push`, el compilador puede setear los registros en **cualquier orden**: podés ver que carga `R8` y recién una línea más abajo `RCX`. No deduzcas el primer argumento por su posición en el listado; identificalo por el **registro** (`RCX`, `RDX`, `R8`, `R9`) y por el rol. El capítulo 19 lo muestra con `fgets(buffer, maxcount, stream)`: `RCX` es el buffer, `RDX` el máximo y `R8` el stream, aunque en el código `RCX` aparezca seteado después de `R8` ({{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_19 Ejercicio 64 bits_19 Ejercicio 64 bits.txt|Reversing desde cero, cap. 19}}; transcripción .txt, sin marcas de tiempo).
:::

### x64: el resto de la ABI

El cap. 18 muestra lo básico; la ABI de x64 de Windows tiene cuatro detalles más que conviene conocer (**conocimiento externo**; [convención x64 de Microsoft](https://learn.microsoft.com/en-us/cpp/build/x64-calling-convention?view=msvc-170)):

- **Alineación de la pila.** En el punto del `call`, `RSP` debe estar alineado a **16 bytes**. Como el `call` empuja 8 bytes (el return address), al entrar a la función `RSP` queda "desalineado en 8"; por eso los prólogos restan una cantidad que deja todo en múltiplo de 16 (y el **shadow space** de 32 bytes también respeta eso). Si ves un `sub rsp, 0x28` típico, es shadow space (0x20) + alineación.
- **Argumentos de punto flotante.** `float`/`double` van en **`XMM0`–`XMM3`** (misma posición que los enteros: el 1.º en `XMM0` o `RCX`, no ambos). `XMM0`–`XMM5` son **volátiles**; `XMM6`–`XMM15` se **preservan**.
- **Funciones variádicas.** En una variádica (`printf`), cada argumento flotante se pasa **a la vez** en el registro XMM y en el GPR entero correspondiente, y `AL` indica cuántos registros vectoriales se usaron. Por eso una variádica se ve distinta de una función normal con los mismos tipos.
- **Unwind / `.pdata`.** No hay cadena SEH en el stack como en 32 bits: la info de desenrollado (qué registros salva el prólogo, dónde está el handler) vive en tablas **`.pdata`/`.xdata`** (lo ves en [PE fino](02-pe-fino.html) 2.14). Sirve para **delimitar funciones** sin símbolos y para entender el prólogo/epílogo.

## Ejemplo paso a paso: `suma(a, b)` en 32 bits

```c
int suma(int a, int b) { return a + b; }
int main(void) { return suma(3, 4); }
```

Compilado con `cdecl`, la llamada se ve así:

```asm
push 4          ; segundo argumento
push 3          ; primer argumento
call suma
add  esp, 8     ; el llamador limpia los dos argumentos
```

Y la función:

```asm
suma:
push ebp
mov  ebp, esp
mov  eax, [ebp+8]    ; a
add  eax, [ebp+12]   ; b
pop  ebp
ret
```

**Recorrido del stack:**

```text
antes del call:      [esp] = 3, [esp+4] = 4
después del call:    [esp] = return address
                     [esp+4] = 3
                     [esp+8] = 4
después del prólogo: [ebp] = ebp viejo
                     [ebp+4] = return address
                     [ebp+8] = 3
                     [ebp+12] = 4
```

Si la función fuera `stdcall`, terminaría en `ret 8` y no habría `add esp, 8` después del `call`. Ese es el detalle que te dice quién limpia.

:::{nota} En el Curso IDA: leer una función basada en EBP (ejercicios IDA1/IDA2)
El Curso IDA trae dos ejercicios muy didácticos de funciones basadas en `EBP`: `IDA1.exe` e `IDA2.exe`. El método es el de siempre: se llega al `main` **por la string** ("You are a winner man je"), se usan los **xrefs** (`X`) para ver dónde se tocan las variables y se las **renombra** (en `IDA2` hay dos "cookies" que hay que comparar para caer en la zona del "chico bueno"). Un detalle real a tener en cuenta: `IDA1.exe` está compilado con **DevC++**, que arma las llamadas a las APIs de una forma distinta a la habitual y puede marear al principio ([Curso IDA · tute 23, IDA1.exe](../ida_tutes/23.html) y [tute 24, IDA2 (cookies)](../ida_tutes/24.html)).
:::

## Recursión

Una función recursiva se llama a sí misma. Cada llamada crea un **nuevo marco** en el stack, con sus propios argumentos y locales. Por eso una recursión sin caso base termina en *stack overflow*: el stack se agota.

```c
int fact(int n) { return n <= 1 ? 1 : n * fact(n - 1); }
```

En el debugger vas a ver el mismo `call` repetido con valores decrecientes de `n`, y el call stack creciendo hacia arriba. El panel **Call Stack** te muestra la cadena de marcos; es la forma más rápida de entender una recursión.

## Llamadas indirectas y funciones virtuales

```asm
call [eax]        ; llama a la función apuntada por EAX
call [eax+4]      ; llama a la segunda entrada de una tabla
```

En C++, un objeto con funciones virtuales guarda al principio un puntero a la **vtable**: una tabla de punteros a métodos. `call [eax+4]` puede ser "llamar al segundo método virtual del objeto apuntado por EAX". El capítulo 37 lo desarrolla con una clase de `0x58` bytes y una vtable de cuatro punteros ({{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_37 TIPS 1_TIPS 1.txt|Reversing desde cero, cap. 37}}, 00:07:38–00:10:48). Es un tema de la rama de C++; en el recorrido base alcanza con reconocer el patrón.

## Práctica

1. Compilá `suma.c` con `gcc -O0 -m32` (o Visual Studio en 32 bits) y mirá el listado en x64dbg. Identificá los `push`, el `call`, el `add esp` y el `ret`.
2. Hacé lo mismo con `__stdcall` (en GCC, `__attribute__((stdcall))`) y comprobá si aparece `ret 8`.
3. Compilá la versión de 64 bits y verificá en qué registros llegan `a` y `b`.
4. Escribí una función recursiva de factorial y mirá el Call Stack en el debugger con `n = 3`.
5. En el programa del capítulo 15, identificá si `printf`/`scanf` son `cdecl` o `stdcall` y justificá con el `add esp` posterior.

## Preguntas de repaso

**1. ¿Qué guarda `call` en el stack?**
La dirección de la instrucción siguiente al `call`, para que `ret` sepa dónde volver.

**2. ¿Quién limpia los argumentos en `cdecl`? ¿Y en `stdcall`?**
En `cdecl`, el llamador (con `add esp, N` después del `call`). En `stdcall`, la función llamada (con `ret N`).

**3. ¿Cómo se pasa `this` en un método de C++ de 32 bits?**
En `ECX`, según la convención `thiscall`.

**4. ¿Cuántos argumentos van en registros en x64?**
Los primeros cuatro enteros: `RCX`, `RDX`, `R8`, `R9`. El resto va al stack, después de 32 bytes de shadow space.

**5. ¿Por qué una recursión infinita produce un stack overflow?**
Porque cada llamada crea un marco nuevo y el stack tiene un tamaño limitado. Al agotarse, el sistema termina el proceso.

## Antes de avanzar

Tenés que poder:

- Calcular la dirección de retorno de un `call`.
- Distinguir `call` directo de indirecto.
- Reconocer `cdecl`, `stdcall` y la convención x64 en un listado.
- Dibujar el marco de una función con dos argumentos.

:::{nota} Puerta de salida
Si podés explicar quién limpia el stack mirando el `ret` o el `add esp`, estás listo para usar el debugger con criterio.
:::

## Fuentes de esta lección

- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_06 Instrucciones 3_06 Instrucciones 3.txt|Reversing desde cero, cap. 06}} — `CALL` directo/indirecto, `RET`, `RET n`.
- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_18 Funciones basadas en EBP vs basadas en ESP_18 Funciones basadas en EBP vs basadas en ESP.txt|Reversing desde cero, cap. 18}} — marcos, prólogo/epílogo, convención x64.
- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_19 Ejercicio 64 bits_19 Ejercicio 64 bits.txt|Reversing desde cero, cap. 19}} — argumentos x64 cargados fuera de orden; identificar por registro y rol (`fgets`).
- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Videos y material adicional Ingenieria Inversa/Videos_Video28_Video28.txt|Videos y material adicional, Video 28}} — procedimientos y variables locales en MASM32.
- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_37 TIPS 1_TIPS 1.txt|Reversing desde cero, cap. 37}} — vtables y llamadas virtuales.
- [Curso IDA · tutes 23 y 24](../ida_tutes/23.html) — funciones basadas en EBP (`IDA1.exe`/`IDA2.exe`), el quirk de DevC++ al llamar APIs y el método strings→`main`→xrefs→renombrar.

:::{nota} Capas de esta lección
**Contenido observado en CLS:** el ejemplo del `call` en `0x00401013`, `ret 0x10`, la convención x64 del capítulo 18 y la vtable del capítulo 37. **Conocimiento externo:** tabla de convenciones `cdecl`/`stdcall`/`fastcall`/`thiscall`. **Recomendación editorial:** el ejemplo `suma` y los ejercicios.
:::

