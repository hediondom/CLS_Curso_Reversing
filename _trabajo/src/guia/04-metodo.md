---
title: "Etapa 4 · Método de análisis: de la pregunta al hallazgo"
description: "Un procedimiento repetible para analizar un programa propio: hipótesis, estático, dinámico y conclusión; también aplicado a reconstruir un formato de archivo propio."
etapa: "Etapa 4 · Práctica guiada"
---

# Método de análisis: de la pregunta al hallazgo

:::{nota} Objetivo de la lección
Al terminar vas a poder analizar un programa de práctica con un método explícito: formular una pregunta, inspeccionar el binario, proponer una hipótesis, confirmarla con el debugger y escribir una conclusión que otra persona pueda reproducir.
:::

**Prerrequisitos:** etapas 0 a 3. **Duración sugerida:** 6 horas (4 para el ciclo con `check.exe` y 2 para el formato propio). Estimación aproximada.

## Por qué un método y no "ir probando"

Cuando empezás, el debugger invita a tocar botones: F8, F7, breakpoints, parches. Eso funciona para un programa de 20 líneas y fracasa con uno de 20.000. Un método te evita dos trampas:

1. **Perderte en el camino equivocado.** Sin una pregunta, cualquier instrucción parece interesante.
2. **Confundir correlación con explicación.** Ver que un salto se toma no significa entender por qué.

El capítulo 11 lo dice a su manera: primero buscás lo más fácil (las strings, los mensajes), y si no alcanza, cambiás de estrategia. El análisis visual es rápido, pero hay que saber qué se está buscando ({{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_11 Ejercicio 1 - Análisis dinámico_11 Ejercicio 1 - Análisis dinámico.txt|Reversing desde cero, cap. 11}}, 00:00:05–00:02:00).

## El ciclo de cinco pasos

```text
1. Pregunta     -> ¿qué quiero saber?
2. Inventario   -> ¿qué es este archivo?
3. Estático     -> ¿dónde está la lógica?
4. Hipótesis    -> ¿qué creo que hace y por qué?
5. Confirmación -> ¿cómo lo pruebo?
```

Después se escribe la conclusión y se anotan los límites. Si la confirmación falla, se vuelve al paso 3 con una hipótesis nueva. Ese ida y vuelta es el trabajo real.

## Paso 1: la pregunta

Una pregunta útil es específica y verificable. No es "¿qué hace este programa?", sino:

- ¿Qué condición tiene que cumplir la entrada para que muestre "Correcto"?
- ¿Qué compara exactamente la instrucción de la dirección `0x401234`?
- ¿De dónde sale el valor que se usa como índice?

Para el programa de práctica de esta lección, la pregunta es: **¿qué pares de números hacen que `check.exe` imprima "Correcto"?**

## Paso 2: inventario

Antes de abrir el debugger, respondé:

| Pregunta | Herramienta | Respuesta (ejemplo) |
|---|---|---|
| ¿Qué tipo de archivo es? | Visor de PE | PE32, ejecutable de consola |
| ¿Es nativo o .NET? | Detect It Easy | Nativo (C) |
| ¿Está empacado? | Secciones/imports | No: `.text` normal, imports de `msvcrt` |
| ¿Qué cadenas muestra? | `strings` o IDA | "Primer valor", "Segundo valor", "Correcto", "Incorrecto" |
| ¿Qué imports usa? | Visor de PE | `printf`, `scanf`, `puts` |
| ¿Tiene símbolos? | PDB | Sí, si lo compilaste en Debug |

Ese inventario ya te dice mucho: un programa de consola que usa `scanf` y `puts`, sin empaquetar, con cadenas claras. No hace falta empezar por el entry point.

## Paso 3: análisis estático

Abrí el binario en IDA Free o Ghidra y seguí las cadenas:

1. `Shift+F12`, buscá "Correcto".
2. `X` sobre la cadena para ver quién la usa.
3. Leé el bloque: vas a encontrar una comparación y dos caminos.
4. Renombrá: `check`, `primer_valor`, `segundo_valor`, `camino_ok`, `camino_error`.
5. Anotá la condición que deduce el grafo.

En el programa del capítulo 15, el análisis estático muestra:

- `scanf("%d", &a)` y `scanf("%d", &b)`;
- `if (a > 50 || b < 50) error;`
- `if ((a + b) * 4 == 480) correcto; else incorrecto;`

El capítulo 15 hace exactamente este recorrido, con `0x32` (50) y `0x1E0` (480), y lo confirma después en el debugger ({{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_15 Ejercicio 2 - Análisis estático_15 Ejercicio 2 - Análisis estático.txt|Reversing desde cero, cap. 15}}, 00:06:00–00:16:00).

## Paso 4: la hipótesis

Una hipótesis se escribe como una afirmación falsable:

> "El programa acepta cualquier par `(a, b)` con `a <= 50`, `b >= 50` y `(a + b) * 4 == 480`. Con `a = 40` y `b = 80` debería imprimir 'Correcto'; con `a = 40` y `b = 70` debería imprimir 'Incorrecto'."

Falsable significa que podés imaginar un resultado que la contradiga. "El programa compara números" no es falsable; "compara contra 50 y contra 480" sí.

## Paso 5: confirmación dinámica

Ahora sí, el debugger. El objetivo no es "ver qué pasa", sino **comprobar la hipótesis**.

### Preparación

1. Copiá el programa a la VM.
2. Abrilo en x64dbg.
3. Buscá la cadena "Correcto" y seguí la referencia hasta el bloque.
4. Etiquetá `camino_ok` y `camino_error`.
5. Poné un breakpoint en la comparación final (`cmp eax, 0x1E0`).

### Ejecución con `40` y `80`

1. `F9` para correr.
2. Ingresá `40` y `80`.
3. El programa se detiene en el breakpoint.
4. Mirá `EAX`: debería ser `0x1E0` (480).
5. Mirá `ZF`: debería ser 1.
6. `F8` para ejecutar el salto: no se toma el salto a `camino_error`.
7. `F9`: imprime "Correcto".

### Ejecución con `40` y `70`

1. Reiniciá (`Ctrl+F2`).
2. Ingresá `40` y `70`.
3. En el breakpoint, `EAX` debería ser `0x1B8` (440).
4. `ZF` = 0; el salto se toma; imprime "Incorrecto".

### Ejecución con `60` y `80`

1. Reiniciá.
2. Ingresá `60` y `80`.
3. El programa ni siquiera llega a la comparación final: falla la primera condición (`a > 50`).
4. Confirmá dónde se detiene y qué salto se toma.

:::{nota} Tu compilador puede generar otro código
Las direcciones y la forma exacta dependen del compilador, las optimizaciones y la arquitectura. Lo que no cambia es la **lógica**: dos comparaciones de rango, una suma, un desplazamiento y una comparación final. Si tu listado no coincide, buscá esas operaciones, no una dirección mágica.
:::

## Dos casos que afinan el método

El ciclo de arriba sirve para la mayoría de los programas, pero conviene conocer dos situaciones que lo ponen a prueba.

**La decisión no está donde la buscás (cap. 16).** Lo habitual es un bloque "bueno" y un bloque "malo" separados por un salto. Pero un programa puede imprimir el mensaje correcto o el incorrecto **desde el mismo bloque**, eligiendo con un `CMOVcc` (ver la lección de flujo) qué puntero de cadena usar. Entonces no hay un salto evidente para entender —ni para parchear—. La lección de método: si las cadenas de éxito y error están en el mismo bloque, buscá un movimiento condicional, no un `Jcc`. En ese mismo ejercicio aparece un `strlen` *inline* (un bucle que incrementa un puntero hasta el byte `0` y resta inicio de final) en vez de una llamada a la API: reconocer funciones estándar escritas a mano es parte del método ({{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_16 Ejercicio 3 - Análisis Dinámico y Estático_16 Ejercicio.txt|Reversing desde cero, cap. 16}}; transcripción .txt, sin marcas).

**Sin símbolos, igual se puede (cap. 20).** El capítulo 20 resuelve un crackme **sin PDB**, y es un buen modelo del ciclo: ejecutar y anotar las cadenas; abrir en IDA; buscar la cadena de error con `Shift+F12` y llegar al código con `X`; **pintar** el bloque malo (salmón), el bueno (verde) y el camino (celeste); como la función es chica, analizarla **desde el inicio** hasta la comparación; renombrar funciones y variables mientras se lee, poniendo `printf?` con signo de pregunta cuando no hay certeza; deducir el algoritmo (ahí, el serial es la suma de los caracteres del nombre) y confirmarlo en el debugger con *popups* de valores ({{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_20 Ejercicio 4 - Análisis Estático_20 Ejercicio 4 - Análisis Estático.txt|Reversing desde cero, cap. 20}}). Un detalle útil de ese capítulo: en 32 bits, **el primer argumento es el que está más cerca del `call`**; y sobre una variable del stack, `A` la convierte en array/define su tamaño y `H` muestra el valor en decimal.

:::{aviso} Cuando el resultado depende del tiempo o del entorno
A veces el valor correcto no es fijo: el capítulo 19 analiza un programa de 64 bits cuya clave se calcula a partir de `GetSystemTime` (depende del minuto actual). Entonces no se puede "ver el valor y volver a ingresarlo", porque para cuando lo tipeás ya cambió. Ahí la confirmación dinámica no alcanza por sí sola: hay que **entender el algoritmo** (o automatizarlo). Es un recordatorio de que estático y dinámico se complementan, y de que una sola corrida no demuestra el caso general ({{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_19 Ejercicio 64 bits_19 Ejercicio 64 bits.txt|Reversing desde cero, cap. 19}}).
:::

## Cuando la pregunta es un formato o un protocolo propio

Este apartado muestra la reconstrucción de **un archivo propio** dentro del ciclo general. La lección [4.5 · Reconstruir formatos y protocolos propios](04-formatos-protocolos.html) sistematiza el trabajo con muestras, framing, protocolos con estado y validación independiente.

Muchas preguntas reales no son "¿qué condición acepta?" sino "¿cómo es el archivo que guarda este programa?" o "¿qué significan los mensajes que manda?". El ciclo de cinco pasos sirve igual; cambian las herramientas de cada paso. Este apartado es **recomendación editorial** apoyada en **conocimiento externo**; el ejemplo es **ilustrativo** y supone un programa **propio** que guarda su configuración en un archivo binario.

**1. Pregunta.** Concreta: "¿qué campos tiene el archivo `.blc` y qué valida el programa al abrirlo?".

**2. Inventario.** Dos o tres archivos generados por el propio programa con datos distintos, y un volcado hexadecimal de cada uno. Las primeras cosas a buscar: bytes fijos al inicio (**número mágico**), números que coinciden con el tamaño del archivo o de un bloque (**campos de longitud**), texto legible (UTF-16 incluido, ver [IDA y el análisis estático](02-ida.html)) y zonas de alta entropía (posible compresión o cifrado, ver [criptografía y encoding](04-cripto.html)).

**3. Estático: encontrar el parser.** El código que lee el formato está detrás de las llamadas que traen los bytes: `ReadFile`, `fread`, `MapViewOfFile` para archivos; `recv`/`WSARecv` para red. Desde la xref, seguí el buffer: cada comparación contra una constante es una validación (el mágico, una versión) y cada lectura `[buffer+N]` con un tamaño fijo es un campo. Una lectura seguida de un salto que usa ese valor como cantidad o desplazamiento es un campo de longitud u offset.

**4. Hipótesis: la tabla de campos.** Escribí la estructura como tabla, con la evidencia de cada fila:

| Offset | Tamaño | Tipo | Significado (hipótesis) | Evidencia |
|---|---|---|---|---|
| `0x00` | 4 | bytes | Mágico `BLOC` | Comparado con `0x434F4C42` antes de seguir |
| `0x04` | 2 | uint16 LE | Versión | `cmp ax, 2` y rama de error "versión no soportada" |
| `0x06` | 2 | uint16 LE | Cantidad de registros | Controla el contador del bucle |
| `0x08` | 4 | uint32 LE | Checksum del resto | Comparado con el resultado de una función con tabla de 256 entradas (CRC32) |
| `0x0C` | variable | registros | Datos | Leídos de a `0x20` bytes dentro del bucle |

**5. Confirmación diferencial.** Con una **copia** del archivo, cambiá **un solo byte** por vez y observá: si cambiar la versión dispara el error de versión, la fila está confirmada; si cambiar un dato hace fallar el checksum, ya sabés que lo cubre. La prueba final es escribir un **lector independiente** (un script de Python con el módulo `struct`, o una descripción declarativa en un lenguaje como Kaitai Struct) que lea los tres archivos y dé los mismos valores que muestra el programa.

Cuidados: trabajá sobre copias; el programa puede reescribir o "reparar" el archivo al abrirlo. Para protocolos de red, el mismo método se aplica a capturas de tu propio cliente y servidor en la VM aislada, sin apuntar a servicios de terceros. Si un campo está cifrado o comprimido, la tabla lo dice así ("bloque cifrado, clave no recuperada") en lugar de inventarle estructura.

## Cómo se escribe la conclusión

Una conclusión útil tiene cuatro partes:

1. **Respuesta a la pregunta.** "El programa acepta pares con `a <= 50`, `b >= 50` y `(a+b)*4 == 480`."
2. **Evidencia.** "Breakpoint en `0x...`: con (40,80), `EAX=0x1E0`, `ZF=1`, imprime 'Correcto'; con (40,70), `EAX=0x1B8`, `ZF=0`, imprime 'Incorrecto'."
3. **Método.** "Análisis estático en IDA Free + confirmación en x64dbg; binario compilado con gcc -O0."
4. **Límites.** "No se probaron todos los pares; la conclusión vale para esta compilación."

Eso es un hallazgo reproducible. No es "lo crackeé": es "entendí la condición y la verifiqué".

## Errores frecuentes

| Error | Por qué pasa | Cómo evitarlo |
|---|---|---|
| Buscar solo strings | El programa puede no tener mensajes claros | Probá imports, xrefs y el entry point |
| Confundir dirección virtual con offset | ASLR y secciones | Usá RVA u offset, o rebaseá |
| Leer un salto al revés | `jne` salta cuando **no** son iguales | Preguntá qué camino toma el salto |
| Confundir signo | `JA` vs `JG` | Mirá el tipo del dato y la instrucción |
| Parchear como primera opción | Es más rápido que entender | Primero explicá; después decidí si hace falta |
| No anotar | Te olvidás de lo que probaste | Bitácora en el momento |

## Práctica

1. Analizá tu `check.exe` con el ciclo de cinco pasos. Escribí la pregunta, el inventario, la hipótesis y la confirmación.
2. Probá tres pares válidos y tres inválidos. Anotá los valores de `EAX` y `ZF` en cada caso.
3. Cambiá el programa: hacé que la condición sea `(a + b) * 2 == 240`. Recompilá y repetí el análisis sin mirar el código fuente. ¿Pudiste deducir la nueva constante?
4. Agregá una tercera condición (por ejemplo `a != b`) y analizala.
5. Escribí un párrafo de conclusión con las cuatro partes.
6. Escribí un programa propio que guarde tres o cuatro valores en un archivo binario con un mágico, una versión y un campo de longitud. Sin mirar el fuente, armá la tabla de campos con evidencia, confirmala cambiando un byte por vez sobre copias y escribí un lector en Python con `struct` que dé los mismos valores.

## Preguntas de repaso

**1. ¿Cuál es la diferencia entre una hipótesis y una observación?**
La hipótesis es una afirmación que hacés antes de confirmar; la observación es lo que el debugger te muestra. La hipótesis se contrasta con la observación.

**2. ¿Por qué conviene empezar por las strings?**
Porque en programas con interfaz o mensajes, las cadenas te llevan rápido a la lógica y a los bloques de éxito/error.

**3. ¿Qué hacés si la confirmación falla?**
Volvés al análisis estático con una hipótesis nueva. No parcheás para que "funcione": entendés por qué falló.

**4. ¿Por qué hay que anotar la compilación y las direcciones?**
Porque el mismo código compilado con otra versión u optimización puede generar otro listado. Sin esos datos, el informe no es reproducible.

**5. ¿Qué significa que un hallazgo sea reproducible?**
Que otra persona, con el mismo binario y el mismo método, puede obtener el mismo resultado.

**6. Querés entender el formato de archivo de un programa. ¿Dónde empezás a buscar el parser?**
En las xrefs a las APIs que traen los bytes (`ReadFile`, `fread`, `MapViewOfFile`; `recv` para red) y siguiendo el buffer: las comparaciones con constantes son validaciones y las lecturas a offsets fijos, campos.

**7. ¿Qué es una confirmación diferencial y por qué se hace sobre copias?**
Cambiar un solo byte por vez y observar qué validación falla o qué valor cambia. Se hace sobre copias porque el programa puede reescribir el archivo y porque el original es la referencia.

**8. ¿Cuándo das por confirmada la tabla de campos?**
Cuando un lector independiente (un script propio) lee varios archivos y obtiene los mismos valores que muestra el programa; lo que no se pudo explicar queda anotado como tal.

## Antes de avanzar

Tenés que poder:

- Formular una pregunta específica y una hipótesis falsable.
- Hacer el inventario de un binario antes de ejecutarlo.
- Confirmar una condición con un breakpoint y valores concretos.
- Escribir una conclusión con evidencia y límites.
- Reconstruir el formato de un archivo propio como tabla de campos con evidencia y confirmarlo con un lector independiente.

:::{nota} Puerta de salida
Si podés analizar un programa propio y explicar la condición sin mirar el fuente, aprobaste el método. La lección siguiente convierte ese trabajo en un informe.
:::

:::{nota} Lo que queda fuera
El objetivo es reconocer y documentar compresión, checksums, hashes, MAC y cifrado, no romper cifrado ni recuperar claves. Tampoco se reconstruyen protocolos de servicios de terceros. La lección [4.5](04-formatos-protocolos.html) enseña el procedimiento con formatos y comunicaciones de programas propios; el *fuzzing* guiado por formato se presenta en la optativa [2.24](02-opt-fuzzing.html).
:::

## Fuentes de esta lección

- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_11 Ejercicio 1 - Análisis dinámico_11 Ejercicio 1 - Análisis dinámico.txt|Reversing desde cero, cap. 11}} — análisis dinámico, strings, etiquetas y hipótesis.
- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_15 Ejercicio 2 - Análisis estático_15 Ejercicio 2 - Análisis estático.txt|Reversing desde cero, cap. 15}} — análisis estático, condiciones `0x32`/`0x1E0` y confirmación.
- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_16 Ejercicio 3 - Análisis Dinámico y Estático_16 Ejercicio.txt|Reversing desde cero, cap. 16}} — decisión con `CMOVcc` en el mismo bloque y `strlen` inline.
- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_19 Ejercicio 64 bits_19 Ejercicio 64 bits.txt|Reversing desde cero, cap. 19}} — clave dependiente del tiempo (`GetSystemTime`): por qué no se reproduce ingresando el mismo valor.
- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_20 Ejercicio 4 - Análisis Estático_20 Ejercicio 4 - Análisis Estático.txt|Reversing desde cero, cap. 20}} — modelo del ciclo sin símbolos: strings, xref, pintar, analizar desde el inicio, renombrar con `?`.
- {{src:CLS_Guia/plantilla_informe.md|plantilla_informe.md}} — plantilla base para el informe.
- Conocimiento externo: [struct — Interpret bytes as packed binary data](https://docs.python.org/3/library/struct.html) (documentación de Python) y [Kaitai Struct](https://kaitai.io/) (lenguaje declarativo para describir formatos binarios).

:::{nota} Capas de esta lección
**Contenido observado en CLS:** el método y los valores de los capítulos 11 y 15 (`0x32`, `0x1E0`, `40`/`80`), el caso `CMOVcc`/`strlen` inline del 16, el modelo sin símbolos del 20 y la clave por tiempo del 19. **Conocimiento externo:** ciclo hipótesis-confirmación, criterios de reproducibilidad y la reconstrucción de formatos (mágicos, campos de longitud, checksums). **Ejemplo ilustrativo:** el formato `.blc` y su tabla de campos. **Recomendación editorial:** el programa `check.exe`, la tabla de errores y la confirmación diferencial con lector independiente.
:::
