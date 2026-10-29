---
title: "Etapa 1 · Bits, bytes, hexadecimal y números con signo"
description: "La aritmética mínima para leer un debugger: binario, hexadecimal, complemento a dos, little-endian y tamaños."
etapa: "Etapa 1 · Fundamentos"
---

# Bits, bytes, hexadecimal y números con signo

:::{nota} Objetivo de la lección
Al terminar vas a poder convertir entre binario, hexadecimal y decimal sin calculadora, interpretar un valor de 32 bits como positivo o negativo según el contexto, y leer los bytes de un número en memoria sin confundir el orden. También vas a poder verificar una dirección virtual contra el archivo en disco.
:::

**Prerrequisitos:** Etapa 0 (laboratorio y bitácora). **Duración sugerida:** 4 a 5 horas, con ejercicios. Estimación aproximada de esta guía.

## Por qué esto no es un trámite

Cuando abrís un programa en un debugger ves tres columnas: direcciones, bytes y una versión legible de esos bytes. Todo está en hexadecimal. Si no podés pasar de `FB` a `251` ni entender por qué `FFFFFFFF` a veces es `-1`, cada pantalla se vuelve un jeroglífico y terminás copiando pasos sin entender.

La buena noticia: el reversing cotidiano usa muy pocos conceptos numéricos, y son los mismos siempre. Esta lección los junta.

## Bit, byte y nibble

Un **bit** es la unidad mínima: vale 0 o 1. Un **byte** son 8 bits. Un **nibble** son 4 bits, que es exactamente lo que representa un dígito hexadecimal.

Por eso hexadecimal y binario se llevan tan bien: cada dígito hexadecimal equivale a cuatro bits.

| Hex | Binario | Decimal |
|---|---|---|
| 0 | 0000 | 0 |
| 1 | 0001 | 1 |
| 2 | 0010 | 2 |
| 4 | 0100 | 4 |
| 8 | 1000 | 8 |
| A | 1010 | 10 |
| F | 1111 | 15 |

Para leer un byte en hexadecimal, separá los dos dígitos y convertí cada uno por separado:

```text
0x8F  ->  8 = 1000     F = 1111   ->  1000 1111  ->  128 + 8 + 4 + 2 + 1 = 143
0xFB  ->  F = 1111     B = 1011   ->  1111 1011  ->  128+64+32+16+8+2+1 = 251
```

El método mental que usa Solid en el capítulo 01 es asignar a cada bit su potencia de dos, de derecha a izquierda: 1, 2, 4, 8, 16, 32, 64, 128. Para representar 10, prendés 8 y 2:

```text
bit:     7   6   5   4   3   2   1   0
valor: 128  64  32  16   8   4   2   1
10  ->   0   0   0   0   1   0   1   0     = 0x0A
```

Esto aparece explicado en el capítulo 01 ({{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_01 x64dbg primeros pasos_01 x64dbg primeros pasos.txt|Reversing desde cero, cap. 01}}, 00:19:00–00:22:00).

:::{aviso} El audio se equivoca en una palabra
En el capítulo 01, alrededor de 00:22:33, la transcripción dice que "el byte más significativo es el de la derecha". La idea que quiere transmitir es correcta —en memoria, el byte **menos** significativo va primero— pero la palabra está invertida. Quedate con la regla de abajo, no con la frase del audio.
:::

:::{nota} En el Curso IDA: convertir bases sin calculadora
El Curso IDA aprovecha la **barra de Python** que IDA trae en la parte de abajo para pasar de una base a otra al instante: `hex(143)` devuelve `0x8f`, `bin(10)` te da `0b1010`, `0x8f` tipeado solo te lo muestra en decimal. Si esa barra no aparece, es que falta el soporte de Python de IDA (reinstalarlo lo soluciona) ([Curso IDA · tute 2, Sistemas de numeración](../ida_tutes/2.html)).
:::

## Little-endian: cómo se guarda un número en memoria

x86 y x64 son **little-endian**: el byte menos significativo (el de menor peso) se guarda en la dirección más baja. Si en memoria ves estos cuatro bytes:

```text
dirección:  1000  1001  1002  1003
contenido:    0D    0C    0B    0A
```

el valor de 32 bits es `0x0A0B0C0D`, no `0x0D0C0B0A`. Para leerlo, das vuelta los bytes.

La confusión típica es Mirar la columna de bytes del debugger y creer que ya es el número. No: es la representación **en memoria**. Los registros, en cambio, te muestran el valor ya interpretado.

El capítulo 01 lo explica con un ejemplo de cuatro bytes `41 42 43 44` y aclara que en memoria se leen al revés (00:22:33–00:23:30). El capítulo 02 lo vuelve a mostrar al mover un valor desde una dirección a `EAX`: los bytes `36 00 00 38` en memoria se convierten en `0x38000036` en el registro ({{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_02 Instrucciones 1_02 Instrucciones 1.txt|Reversing desde cero, cap. 02}}, 00:07:12–00:07:50).

## Números con signo: complemento a dos

Un mismo patrón de bits puede interpretarse de dos maneras. `0xFB` es 251 si el dato es **sin signo** y −5 si es **con signo**. El procesador no guarda el signo en un bit aparte: usa una convención llamada **complemento a dos**.

La regla práctica:

- Si el bit más alto es 0, el número es positivo y vale lo mismo que en sin signo.
- Si el bit más alto es 1, el número es negativo. Para saber cuánto vale, invertí todos los bits y sumá 1 (o restá el valor a 2^n).

Ejemplo con 8 bits:

```text
 5  = 0000 0101
-5  = 1111 1010 + 1 = 1111 1011 = 0xFB
```

Comprobación: `0xFB` = 251. Y 256 − 251 = 5, así que representa −5. La relación es `valor_con_signo = valor_sin_signo − 2^8`.

Los rangos que hay que saber de memoria:

| Tamaño | Nombre | Bits | Sin signo | Con signo |
|---|---|---|---|---|
| 1 byte | BYTE | 8 | 0 a 255 | −128 a 127 |
| 2 bytes | WORD | 16 | 0 a 65.535 | −32.768 a 32.767 |
| 4 bytes | DWORD | 32 | 0 a 4.294.967.295 | −2.147.483.648 a 2.147.483.647 |
| 8 bytes | QWORD | 64 | 0 a 18.446.744.073.709.551.615 | −9.223.372.036.854.775.808 a 9.223.372.036.854.775.807 |

Por eso `0xFFFFFFFF` es 4.294.967.295 sin signo y −1 con signo. Y `0x7FFFFFFF` es el máximo positivo de 32 bits: 2.147.483.647.

El capítulo 03 explica la idea de dividir el rango en dos mitades, una positiva y otra negativa ({{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_03 Registros, Flags y Números_03 Registros, Flags y Números.txt|Reversing desde cero, cap. 03}}, 00:14:46–00:17:10). El audio se enreda al pasar de DWORD a WORD y dice un rango que no corresponde; la tabla de arriba es la que vale.

:::{aviso} El tamaño importa: una suma que "se da vuelta"
Si un programa acumula valores en un registro de **un byte**, al pasar de `0xFF` el resultado se envuelve: `0xFF + 2 = 0x01`, porque solo se guarda la parte baja. Lo mismo vale para `WORD` o `DWORD` en su tope. Es un detalle que cambia por completo lo que compara una función. El capítulo 34 lo usa: un programa suma los caracteres que ingresás en un byte, y una suma que pasa de `0xFF` deja un valor chico (por ejemplo `0x149` guarda `0x49`). Cuando leas una comparación, fijate **qué tamaño** tiene el acumulador ({{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_34 Reverseando sin símbolos_34 Reverseando sin símbolos.txt|Reversing desde cero, cap. 34}}).
:::

## Ejemplo paso a paso: de una dirección virtual al offset del archivo

Este es el cálculo que más vas a repetir cuando pases de un debugger a un editor hexadecimal o a un desensamblador. El capítulo 05 lo hace con un ejecutable concreto ({{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_05 Virtual Adress, RVA, Offsets y Desplazamientos_05 Virtual Adress, RVA, Offsets y Desplazamientos.txt|Reversing desde cero, cap. 05}}, 00:00:40–00:04:20).

Datos del ejemplo:

- Image Base: `0x6D0000`
- Dirección virtual (VA) de la instrucción: `0x6D1372`
- Tamaño reservado para el header en memoria: `0x1000`
- `PointerToRawData` de la sección `.text`: `0x400`

**Paso 1.** Calculá la RVA (Relative Virtual Address), que es la distancia desde la base:

```text
RVA = VA - Image Base
    = 0x6D1372 - 0x6D0000
    = 0x1372
```

**Paso 2.** Restá el espacio que el header ocupa en memoria (`0x1000`) y sumá el offset real donde empieza `.text` en el archivo (`0x400`):

```text
File Offset = RVA - 0x1000 + 0x400
            = 0x1372 - 0x1000 + 0x400
            = 0x372 + 0x400
            = 0x772
```

**Paso 3.** Verificá en el archivo. En el offset `0x772` del `.exe` deberían estar los bytes `E8 C4 03 00 00`, los mismos que muestra el debugger en esa dirección. El capítulo 05 lo comprueba con un editor hexadecimal (00:03:41–00:04:30).

:::{nota} Por qué se resta 0x1000 y no el tamaño real del header
El cargador de Windows alinea el header a `0x1000` en memoria, aunque el header real sea más chico (en el ejemplo, `.text` empieza en el archivo en `0x400`). Por eso la fórmula usa la diferencia entre la alineación de memoria y el offset real de la sección. Cada sección tiene su propio `PointerToRawData`; no uses `0x400` para `.rdata` ni para `.data`.
:::

## Ejemplo paso a paso: a dónde salta un `call` directo

En un `call` directo, el opcode `E8` va seguido de un desplazamiento de 4 bytes. La dirección destino se calcula sumando al desplazamiento la dirección de la **instrucción siguiente** (no la del `call`).

En el capítulo 05, el `call` está en `0x6D1372`, mide 5 bytes y su desplazamiento es `0x3C4`:

```text
destino = VA_del_call + tamaño_del_call + desplazamiento
        = 0x6D1372 + 5 + 0x3C4
        = 0x6D1377 + 0x3C4
        = 0x6D173B
```

El debugger muestra `0x6D173B` como destino. Si el salto fuera hacia atrás, el desplazamiento sería negativo y se rellenaría con `FF` a la izquierda antes de sumar (cap. 05, 00:09:00–00:12:00).

## Práctica

1. Convertí a hexadecimal: 42, 200, 255, 1024, 4096.
2. Convertí a decimal: `0x2A`, `0xC8`, `0xFF`, `0x400`, `0x1000`.
3. ¿Qué valor con signo representa `0xFFFFFFFB` en 32 bits? ¿Y sin signo?
4. Escribí los bytes que ocupa `0x11223344` en memoria little-endian.
5. Con Image Base `0x400000`, VA `0x401040`, header `0x1000` y `.text` en `0x400`, calculá el file offset.
6. Un `call` en `0x401000` tiene desplazamiento `0x20`. ¿A qué dirección salta? (Ojo con el tamaño de la instrucción.)
7. Abrí PowerShell y comprobá tus conversiones:

```powershell
'{0:X}' -f 42          # 2A
'{0:X8}' -f 4294967295 # FFFFFFFF
[Convert]::ToInt32('FFFFFFFB',16)  # -5
```

## Preguntas de repaso

**1. ¿Cuántos bits hay en un byte y cuántos dígitos hexadecimales lo representan?**
Ocho bits y dos dígitos hexadecimales, porque cada dígito representa cuatro bits.

**2. ¿Por qué `0xFB` puede ser 251 o −5?**
Porque el patrón de bits es el mismo. El tipo del dato y la instrucción que lo usa deciden si se interpreta con signo o sin signo.

**3. ¿Qué significa little-endian?**
Que el byte menos significativo se almacena en la dirección más baja. Para leer un valor de memoria hay que invertir el orden de los bytes.

**4. ¿La dirección que muestra el debugger es la misma que la del archivo en disco?**
No. La del debugger es una dirección virtual; la del archivo es un offset. Se relacionan con la fórmula `offset = RVA − alineación_del_header + PointerToRawData`.

**5. ¿Por qué el destino de un `call` se calcula desde la instrucción siguiente?**
Porque el desplazamiento se mide desde el final de la instrucción actual, que es donde el procesador ya actualizó `EIP`/`RIP`. Sumar el tamaño de la instrucción es parte del cálculo.

## Antes de avanzar

Tenés que poder, sin mirar la tabla:

- Pasar un byte de hexadecimal a binario y a decimal.
- Explicar complemento a dos con el ejemplo de `0xFB`.
- Escribir `0x0A0B0C0D` como bytes en memoria.
- Calcular un file offset a partir de una VA y un `call` directo a partir de su desplazamiento.

:::{nota} Puerta de salida de la Etapa 1 · bloque 1
Si los ejercicios 3 a 6 te salen con seguridad, seguí con memoria y procesos. Si no, repetilos con lápiz y papel antes de abrir un debugger: la pantalla no perdona la aritmética floja.
:::

## Fuentes de esta lección

- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_01 x64dbg primeros pasos_01 x64dbg primeros pasos.txt|Reversing desde cero, cap. 01}} — bits, bytes, little-endian, tamaños (00:18:00–00:24:00).
- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_02 Instrucciones 1_02 Instrucciones 1.txt|Reversing desde cero, cap. 02}} — lectura de un valor desde memoria (00:07:00–00:08:00).
- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_03 Registros, Flags y Números_03 Registros, Flags y Números.txt|Reversing desde cero, cap. 03}} — números con signo (00:14:46–00:17:10).
- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_05 Virtual Adress, RVA, Offsets y Desplazamientos_05 Virtual Adress, RVA, Offsets y Desplazamientos.txt|Reversing desde cero, cap. 05}} — VA, RVA, file offset y desplazamientos (00:00:40–00:12:00).
- [Curso IDA · tute 2, Sistemas de numeración](../ida_tutes/2.html) — binario/decimal/hexadecimal y la barra de Python de IDA para convertir bases.

:::{nota} Capas de esta lección
**Contenido observado en CLS:** el ejemplo numérico de la VA `0x6D1372`, la fórmula del offset y el cálculo del `call` a `0x6D173B`. **Conocimiento externo:** complemento a dos, rangos y aritmética hexadecimal. **Recomendación editorial:** el orden de los ejercicios y la advertencia sobre las imprecisiones del audio.
:::

