---
title: "Etapa 2 · Registros, subregistros y flags"
description: "Los registros del procesador x86/x64, cómo se solapan y cómo los flags resumen el resultado de una operación."
etapa: "Etapa 2 · Introducción al reversing"
---

# Registros, subregistros y flags

:::{nota} Objetivo de la lección
Al terminar vas a poder nombrar los registros de propósito general y su función típica, descomponer un registro de 32 bits en sus partes de 16 y 8 bits, y explicar qué flag se activa en una suma o resta concreta.
:::

**Prerrequisitos:** Etapa 1 completa. **Duración sugerida:** 3 horas. Estimación aproximada.

## Qué es un registro

Un **registro** es una porción de memoria pequeña y muy rápida que está dentro del procesador. Se usa para operar con los datos que la CPU necesita en el momento. En 32 bits cada registro mide 4 bytes (32 bits); en 64 bits, 8 bytes (64 bits).

El capítulo 03 lo define así: "una porción de memoria pequeña, ultra rápida, que forma parte del procesador y que sirve para intercambiar datos" ({{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_03 Registros, Flags y Números_03 Registros, Flags y Números.txt|Reversing desde cero, cap. 03}}, 00:00:30).

## Los registros de propósito general

| Registro 32 | Registro 64 | Nombre | Uso típico |
|---|---|---|---|
| `EAX` | `RAX` | Acumulador | Resultado de funciones y operaciones |
| `EBX` | `RBX` | Base | Datos generales; a veces puntero a datos |
| `ECX` | `RCX` | Contador | Bucles, `rep`, shifts variables |
| `EDX` | `RDX` | Datos | Parte alta de multiplicaciones/divisiones; E/S |
| `ESI` | `RSI` | Source index | Origen en copias de memoria |
| `EDI` | `RDI` | Destination index | Destino en copias de memoria |
| `ESP` | `RSP` | Stack pointer | Cima del stack |
| `EBP` | `RBP` | Base pointer | Base del marco de la función |

Además, `EIP`/`RIP` es el **instruction pointer**: apunta a la instrucción que se va a ejecutar. No se modifica con `mov`; lo cambia el flujo (saltos, llamadas, retornos).

El capítulo 03 asigna funciones concretas: `EAX` guarda el resultado de las funciones, `ECX` actúa como contador en bucles y operaciones repetitivas, `ESI`/`EDI` se usan para copiar bloques de memoria, `ESP` apunta a la cima del stack y `EBP` a la base del marco (00:01:00–00:03:00). Son convenciones, no reglas absolutas: un compilador puede usar `EAX` para cualquier cosa.

## Subregistros: el mismo espacio, distintos tamaños

Un registro de 32 bits se puede leer como uno de 16 o como dos de 8. No son registros separados: son **ventanas** sobre el mismo espacio.

Para `EAX`:

```text
63                                 32 31              16 15       8 7        0
+------------------------------------+------------------+-----------+----------+
|              (solo en RAX)         |       EAX        |    AX     |          |
+------------------------------------+------------------+-----------+----------+
                                                          AH          AL
```

Ejemplo con `EAX = 0x008FFB18`:

| Vista | Valor | Tamaño |
|---|---|---|
| `EAX` | `0x008FFB18` | 32 bits |
| `AX` | `0xFB18` | 16 bits (los dos bytes bajos) |
| `AH` | `0xFB` | 8 bits (byte alto de `AX`) |
| `AL` | `0x18` | 8 bits (byte bajo de `AX`) |

Esto se aplica a `EAX`, `EBX`, `ECX` y `EDX`. `ESI`, `EDI`, `EBP` y `ESP` tienen versión de 16 bits (`SI`, `DI`, `BP`, `SP`) pero no se dividen en dos de 8. El capítulo 03 lo explica con este mismo ejemplo (00:04:30–00:09:00).

En 64 bits, `RAX` contiene a `EAX`, que contiene a `AX`, que contiene a `AL`/`AH`. Además hay ocho registros nuevos, `R8` a `R15`, con subregistros `R8D` (32), `R8W` (16) y `R8B` (8).

:::{aviso} Escribir en la parte baja no borra la alta (con matices)
En x86, escribir en `AL` no cambia el resto de `RAX`. Pero en x64, escribir en `EAX` **sí borra los 32 bits altos de `RAX`**. Es una diferencia que sorprende cuando comparás el código de 32 y 64 bits. Para el análisis inicial, alcanza con saber que los tamaños se solapan y que el debugger te muestra cada vista.
:::

## Flags: el resumen de la última operación

Los **flags** son bits de estado que se activan según el resultado de una operación. No son registros de datos: son banderas. Los cuatro que importan en el uso diario:

| Flag | Nombre | Se activa cuando... |
|---|---|---|
| `ZF` | Zero flag | El resultado es cero |
| `SF` | Sign flag | El resultado es negativo (bit más alto en 1) |
| `CF` | Carry flag | Hubo acarreo/desborde en una operación **sin signo** |
| `OF` | Overflow flag | Hubo desborde en una operación **con signo** |

Hay más (`PF` de paridad, `AF` auxiliar, `DF` de dirección), pero casi nunca los mirás al reversear.

### Ejemplo 1: `ZF`

```asm
mov eax, 3
sub eax, 3      ; resultado 0 -> ZF = 1
```

Si en cambio hacés `mov eax, 0`, el flag `ZF` **no** se activa: `mov` no es una operación aritmética y no actualiza los flags. El capítulo 04 lo muestra explícitamente ({{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_04 Instrucciones 2_04 Instrucciones 2.txt|Reversing desde cero, cap. 04}}, 00:00:30–00:02:00).

### Ejemplo 2: `CF`

```asm
mov eax, 0xFFFFFFFF   ; máximo sin signo
add eax, 5            ; resultado 4, con acarreo
```

El resultado "real" (4.294.967.300) no entra en 32 bits. El procesador guarda `4` y activa `CF`. Para valores sin signo, eso es un desborde (cap. 04, 00:05:00–00:06:00).

### Ejemplo 3: `OF` y `SF`

```asm
mov eax, 0x7FFFFFFF   ; máximo positivo con signo
add eax, 1            ; pasa a 0x80000000
```

El resultado cambió de positivo a negativo: para valores con signo es un desborde, así que se activa `OF`. Además, como el bit más alto quedó en 1, se activa `SF` (cap. 04, 00:07:30–00:09:00).

Lo importante: **el mismo resultado activa flags distintos según cómo lo interpretes**. `0x80000000` es un número enorme sin signo y un número negativo con signo. Los flags no deciden por vos; reflejan ambas lecturas.

## Multiplicación y división: registros dobles

`MUL` y `DIV` usan `EDX:EAX` como un registro de 64 bits:

- `MUL operando`: multiplica `EAX` por el operando y guarda el resultado en `EDX:EAX`.
- `DIV operando`: divide `EDX:EAX` por el operando; cociente en `EAX`, resto en `EDX`.

Ejemplo del capítulo 04: `EAX = 4`, `EBX = 2`, `MUL EBX` deja `EAX = 8` y `EDX = 0`. Si el resultado no entra en 32 bits, la parte alta aparece en `EDX` (00:13:00–00:17:00).

`IMUL`/`IDIV` son las versiones con signo. La mecánica es la misma; cambia la interpretación de los bits.

## Práctica

1. Completá la tabla para `EBX = 0x11223344`:

| Vista | Valor |
|---|---|
| `EBX` | |
| `BX` | |
| `BH` | |
| `BL` | |

2. ¿Qué flag se activa en cada caso?
   - `sub eax, eax`
   - `add eax, 1` con `EAX = 0xFFFFFFFF`
   - `add eax, 1` con `EAX = 0x7FFFFFFF`
   - `mov eax, 0`
3. Escribí en x64dbg `mov eax, 0x7FFFFFFF` y `add eax, 1`. Anotá `ZF`, `SF`, `CF` y `OF` antes y después.
4. Explicá por qué `mov` no cambia los flags y `add` sí.
5. ¿Qué registro usarías para contar las vueltas de un bucle? ¿Por qué no `ESP`?

## Preguntas de repaso

**1. ¿`AX` es un registro distinto de `EAX`?**
No. Es la parte baja de 16 bits de `EAX`. Escribir en `AX` modifica los dos bytes bajos de `EAX` y deja los altos intactos.

**2. ¿Qué diferencia hay entre `CF` y `OF`?**
`CF` indica desborde en una interpretación sin signo; `OF`, en una interpretación con signo. El mismo resultado puede activar uno, otro o ambos.

**3. ¿`EIP` se puede cambiar con `mov`?**
No directamente. Se cambia con instrucciones de control de flujo (`jmp`, `call`, `ret`, `jcc`) o con el debugger (por ejemplo, "set new origin here").

**4. ¿Para qué sirve `EDX` en una división?**
Para la parte alta del dividendo y para el resto. `DIV` divide `EDX:EAX` por el operando y deja el cociente en `EAX` y el resto en `EDX`.

**5. ¿Por qué `mov eax, 0` no activa `ZF`?**
Porque `mov` es una transferencia de datos, no una operación aritmética. Los flags se actualizan con instrucciones como `add`, `sub`, `cmp`, `test`, `and`, etc.

## Antes de avanzar

Tenés que poder:

- Nombrar los ocho registros de propósito general y su función típica.
- Descomponer `EAX` en `AX`, `AH` y `AL` con un ejemplo.
- Explicar `ZF`, `SF`, `CF` y `OF` con un caso cada uno.
- Decir qué registros usa `MUL`/`DIV` para el resultado.

:::{nota} Puerta de salida
Si podés predecir los flags de una operación antes de ejecutarla, estás listo para las instrucciones. Si no, practicá con la calculadora del debugger y papel.
:::

## Fuentes de esta lección

- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_03 Registros, Flags y Números_03 Registros, Flags y Números.txt|Reversing desde cero, cap. 03}} — registros, subregistros, flags y números con signo.
- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_04 Instrucciones 2_04 Instrucciones 2.txt|Reversing desde cero, cap. 04}} — ejemplos de `ZF`, `CF`, `OF`, `SF`, `MUL` y `DIV`.
- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Videos y material adicional Ingenieria Inversa/Videos_Video5_Video5.txt|Videos y material adicional, Video 5}} — registros de 32 bits y prefijo `E` en el curso de MASM32.

:::{nota} Capas de esta lección
**Contenido observado en CLS:** la definición de registro, el ejemplo `EAX = 0x008FFB18` y los ejemplos de flags de los capítulos 03 y 04. **Conocimiento externo:** la tabla de registros de 64 bits y la semántica exacta de `CF`/`OF`. **Recomendación editorial:** los ejercicios y la advertencia sobre el borrado de la parte alta en x64.
:::
