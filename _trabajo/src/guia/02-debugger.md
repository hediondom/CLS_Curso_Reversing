---
title: "Etapa 2 · El debugger: x64dbg de punta a punta"
description: "Navegar, ejecutar paso a paso, poner los tres tipos de breakpoint y leer el estado del programa sin perderte."
etapa: "Etapa 2 · Introducción al reversing"
---

# El debugger: x64dbg de punta a punta

:::{nota} Objetivo de la lección
Al terminar vas a poder abrir un programa propio en x64dbg, moverte por el código, ejecutar con F7/F8/F9, poner breakpoints por software, por hardware y de memoria, condicionarlos y dejar un registro de lo observado.
:::

**Prerrequisitos:** registros, instrucciones, flujo y llamadas. **Duración sugerida:** 5 horas. Estimación aproximada.

## Análisis dinámico y estático

Hay dos formas de mirar un programa:

- **Dinámico:** lo ejecutás dentro de un debugger y observás qué hace mientras corre. Te muestra la verdad de la ejecución, pero solo del camino que tomaste.
- **Estático:** lo analizás sin ejecutarlo, con un desensamblador como IDA o Ghidra. Te muestra todo el código, pero no los valores concretos.

El capítulo 11 lo plantea como una decisión de método: el dinámico es más visual y rápido para problemas chicos; el estático permite analizar funciones que no sabés cómo alcanzar y es obligatorio cuando no podés ejecutar ({{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_11 Ejercicio 1 - Análisis dinámico_11 Ejercicio 1 - Análisis dinámico.txt|Reversing desde cero, cap. 11}}, 00:00:05–00:01:00).

En la práctica se usan los dos: primero el estático para orientarte, después el dinámico para confirmar.

:::{nota} En el Curso IDA: IDA también debuggea, y se practica con crackmes propios
El Curso IDA refuerza esta misma combinación de estático y dinámico, pero sin salir de IDA: recordá que **IDA no solo desensambla, también soporta varios debuggers**, así que podés estudiar el loader y después ejecutar sobre el mismo programa sin cambiar de herramienta. Lo practica con crackmes chiquitos hechos por el propio autor (`HOLA_REVERSER.exe`, `TEST_REVERSER.exe`) ([Curso IDA · tute 10, Loader + debugger](../ida_tutes/10.html); prácticas en [tute 9](../ida_tutes/9.html) y [tute 12](../ida_tutes/12.html)).
:::

## La ventana de x64dbg

Al abrir un programa, x64dbg se detiene en el **entry point**: la primera instrucción que ejecuta el código del programa. No es necesariamente `main`; es el punto donde el cargador le pasa el control (cap. 01, 00:02:08).

Las pestañas principales:

| Pestaña | Qué muestra |
|---|---|
| **CPU** | Desensamblado, registros, flags, stack y dump |
| **Log** | Mensajes del debugger y de los breakpoints con log |
| **Notes** | Notas que escribís vos |
| **Breakpoints** | Lista de breakpoints con condición y estado |
| **Memory Map** | Regiones del espacio de direcciones |
| **Call Stack** | Cadena de llamadas actual |
| **SEH** | Cadena de manejadores de excepciones (32 bits) |
| **Symbols** | Módulos cargados y sus funciones |
| **Threads** | Hilos del proceso |
| **Handles** | Recursos abiertos |
| **Trace** | Resultado del trazado |
| **PE Viewer** | Cabecera PE del módulo (plugin) |

El capítulo 01 hace un recorrido por todas ellas y aclara que al principio no hace falta entenderlas todas (00:04:00–00:07:00).

## Ejecutar paso a paso

| Tecla | Acción | Qué hace |
|---|---|---|
| `F9` | Run | Ejecuta hasta el próximo breakpoint o hasta que el programa termine |
| `F8` | Step over | Ejecuta la instrucción; si es un `call`, ejecuta la función completa sin entrar |
| `F7` | Step into | Ejecuta la instrucción; si es un `call`, entra a la función |
| `F2` | Toggle breakpoint | Pone o saca un breakpoint por software |
| `Ctrl+F2` | Restart | Reinicia el proceso |
| `*` | Follow EIP/RIP | Vuelve a la instrucción actual |

La diferencia entre F7 y F8 es la más importante al empezar: con F8 pasás "por arriba" de una función; con F7 entrás. El capítulo 01 lo demuestra entrando a `main` con F7 y saliendo con F8 (00:15:16–00:20:00).

:::{nota} El "step over" no saltea la función
`F8` **ejecuta** la función completa, no la ignora. La diferencia es que no te detiene instrucción por instrucción dentro de ella. Si la función tiene efectos (escribe un archivo, muestra un mensaje), esos efectos ocurren igual.
:::

## Los tres tipos de breakpoint

### Por software

Es el clásico. El debugger reemplaza el primer byte de la instrucción por `0xCC` (la instrucción `INT3`). Cuando el procesador la ejecuta, genera una excepción que el debugger intercepta, muestra el estado y restaura el byte original.

- Se pone con `F2` o con doble clic en la columna de opcodes.
- No hay un límite práctico: podés poner todos los que quieras.
- Es fácil de detectar por un programa: si compara el byte en memoria con el del archivo, ve `0xCC` donde debería haber otra cosa.

### Por hardware

Usa los registros de depuración `DR0` a `DR3` del procesador. Hay **cuatro por hilo** (no por proceso: cada hilo tiene su propio contexto de CPU). En x64dbg se aplican al hilo actual, salvo que configures lo contrario.

- Se ponen con clic derecho → *Breakpoint* → *Set hardware on execution*.
- Se marcan con un punto rojo, no con la línea entera.
- No modifican el código, así que son más difíciles de detectar.
- También permiten *on access* (lectura/escritura) sobre 1, 2 o 4 bytes.

El capítulo 07 los muestra y aclara que el hardware "para una instrucción después" del acceso ({{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_07 Breakpoints_07 Breakpoints.txt|Reversing desde cero, cap. 07}}, 00:02:34–00:10:00). Es una imprecisión útil de conocer: el *debug exception* se genera después de ejecutar la instrucción que accedió a la dirección vigilada.

:::{aviso} Una corrección al audio
El capítulo 07 dice "cuatro por proceso" y "funcionan solamente en el thread principal". Lo correcto es que los registros `DR0`–`DR3` son parte del contexto de cada hilo, así que el límite es por hilo. En la práctica, x64dbg te muestra y aplica los breakpoints de hardware según el hilo que estés mirando. Si no te aparecen, revisá qué hilo está seleccionado.
:::

### De memoria

Vigila una región (no solo 1, 2 o 4 bytes) y se dispara cuando el programa la lee o la escribe. Internamente usa protecciones de página: el debugger marca la página como no accesible y recibe la excepción cuando alguien la toca.

- Se pone seleccionando un rango en el dump → clic derecho → *Breakpoint* → *Memory on access/read/write*.
- Opciones: *single shot* (se deshabilita después del primer impacto) o *restore on hit* (sigue activo).
- Es la herramienta para responder "¿quién lee este buffer?".

El capítulo 07 lo prueba con el buffer donde `GetDlgItemText` escribe el nombre: pone un breakpoint de memoria sobre los primeros bytes y el programa se detiene cuando los lee (00:10:00–00:14:00).

## Breakpoints condicionales y con log

Un breakpoint puede tener una **condición** y una **acción**:

- **Condición** (`breakif`): solo se detiene si se cumple. Ejemplo: `EAX == 8`.
- **Log**: escribe un texto en el panel Log cada vez que pasa, sin detenerse. Ejemplo: `valor de EAX = {EAX}`.

En el capítulo 07, Ricardo usa un breakpoint en una función que devuelve la longitud del texto ingresado. Primero lo configura para loguear `{EAX}` y ve `5` cuando escribe `"solid"`. Después le pone la condición `EAX == 8` y comprueba que solo se detiene cuando el nombre tiene 8 caracteres (00:15:00–00:20:00).

```text
breakif: EAX == 8
log:     "longitud = {EAX}"
```

Ese patrón —"no me interesa parar, me interesa saber qué valor toma"— es el que vas a usar para entender bucles y comparaciones sin detenerte cien veces.

## Etiquetas, comentarios y navegación

- **Etiqueta** (`:`): renombra una dirección para no perderte. En el capítulo 11, Ricardo etiqueta el bloque del mensaje "acceso denegado" como `chico_malo` y el otro como `chico_bueno`.
- **Comentario** (`;`): agrega una nota a una línea.
- **Follow in dump**: muestra en el panel de memoria el contenido de una dirección.
- **Follow in disassembler**: salta a la dirección apuntada.
- **Ctrl+G**: ir a una dirección o expresión.
- **Ctrl+Shift+G**: ir a un file offset (útil para comparar con el archivo).

Las etiquetas y comentarios no cambian el programa: son tu mapa de lectura. El capítulo 11 muestra cómo el análisis visual se apoya en ellas (00:02:16–00:06:00).

## Encontrar el código que maneja un botón o un mensaje

En un programa con ventana no hay un `main` lineal: Windows le **envía mensajes** (se hizo clic, se escribió en un campo, se apretó un botón) y el programa los atiende en una función despachadora. Encontrar esa función es el primer paso para analizar una interfaz.

Lo que hay que saber:

- La función despachadora es el **WinProc** (si la ventana se creó con `CreateWindow`) o la **Dialog procedure** (si se creó con `DialogBoxParam`). Las dos hacen lo mismo: reciben el mensaje y lo reparten con un `switch`.
- El **mensaje** es el **segundo argumento** de esa función. Un `WM_COMMAND` vale `0x111` y es el que se dispara, en general, al apretar un botón; un `WM_LBUTTONDOWN` vale `0x201`.
- El **Control ID** identifica qué botón se tocó. Se puede ver pasando el mouse por el control en una herramienta de inspección de ventanas.

Tres maneras de llegar al handler, de más simple a más robusta:

1. **Buscar el Control ID en estático.** Si el botón tiene ID `0x13A`, buscás ese inmediato en IDA (ver la lección de IDA) y caés dentro del `WinProc`. Falla cuando el ID es un número bajo y común (`1`, `5`, `10`): hay demasiadas ocurrencias.
2. **Breakpoint condicional sobre el mensaje.** Poné un breakpoint donde la función carga el mensaje en un registro y condicionalo a ese mensaje. Podés además loguear los dos argumentos leyéndolos del stack:

```text
log:     "msg={2}  id={3}"      ; con getdword(sp+8) y getdword(sp+C)
breakif: getdword(sp+8) == 0x111 && getdword(sp+0xC) == 0x13A
```

3. **Breakpoint en `SendMessage` + breakpoint de ejecución en el código.** Es el método genérico que sirve aunque no sepas nada del programa. En Windows, los mensajes llegan vía `SendMessageW`/`SendMessageA` de `user32.dll` (ahí el mensaje también es el segundo argumento). Poné un breakpoint ahí, condicionado a tu mensaje; cuando pare, poné un **breakpoint de hardware por ejecución sobre toda la sección de código del ejecutable** (su dirección de inicio y su tamaño, que ves en el *Memory Map* o en *Segments*). Al continuar, el programa se detiene en la primera instrucción **de tu código** que corre tras recibir el mensaje: esa es la entrada del WinProc. Después borrás ese breakpoint para seguir.

:::{nota} Cómo se registra el WinProc
Con `CreateWindow`, antes hay un `RegisterClassA` que recibe una estructura `WNDCLASS`; dentro de esa estructura está el puntero al WinProc. Con `DialogBoxParam`, el procedimiento se pasa directamente como uno de sus argumentos. Encontrar `RegisterClassA` o `DialogBoxParam` te lleva, por cualquiera de los dos caminos, a la función que maneja los mensajes.
:::

El capítulo 28 ("Mensajes de Windows") muestra las tres formas sobre varios crackmes propios, incluida la carga de los símbolos de `user32.dll` para poner el breakpoint en `SendMessageW` ({{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_28 Mensajes de Windows_28 Mensajes de Windows.txt|Reversing desde cero, cap. 28}}; transcripción .txt, sin marcas de tiempo). El capítulo 24b agrega que el `switch` de mensajes se lee mejor traduciendo los números a sus nombres `WM_*` con la tecla `M` en IDA.

## Parchear (solo programas propios)

x64dbg permite modificar instrucciones en memoria y guardar los cambios en un archivo:

1. Seleccioná la instrucción.
2. Clic derecho → *Binary* → *Fill with NOP* (o *Edit* para escribir bytes).
3. *Patches* → *Patch file* para guardar una copia con los cambios.

En el capítulo 11, Ricardo reemplaza un salto condicional por dos `NOP` y guarda una copia del programa que acepta cualquier clave (00:20:00–00:25:00). Es una demostración didáctica sobre un crackme de práctica.

:::{peligro} El límite legal y ético
Parchear un programa **no es una técnica neutral**. En esta guía se practica únicamente con programas propios, software abierto o crackmes diseñados para aprender, y se explica el efecto de un parche para entender el flujo. No se parchea software comercial para saltar licencias, DRM, autenticación ni controles de acceso. Si el programa no es tuyo o no tiene licencia para analizarlo, no lo toques.
:::

## Anti-debug: qué cambia cuando hay un debugger

Un programa puede detectar que está siendo depurado. Los chequeos más comunes en Windows de 32 bits:

| Chequeo | Dónde mira | Qué delata |
|---|---|---|
| `IsDebuggerPresent` | `PEB+2` | Byte en 1 si hay debugger |
| `NtGlobalFlag` | `PEB+0x68` | Flags de heap activados por el debugger |
| Lista de procesos | `CreateToolhelp32Snapshot` | Encuentra `x64dbg.exe`, `ida.exe`, etc. |
| `ParentPID` | PID del proceso padre | El padre no es `explorer.exe` |
| `CloseHandle` inválido | Excepción `0xC0000008` | Comportamiento distinto bajo debugger |
| `INT3` en memoria | Byte `0xCC` | Breakpoint por software |
| `ContextRecord` tras una excepción | `DR0`–`DR3` del contexto | Breakpoints de **hardware** |

El capítulo 21 muestra el último caso: un programa que provoca una excepción a propósito puede, en su manejador, leer el `ContextRecord` y mirar los registros de depuración `DR0`–`DR3`; si no están en cero, hay breakpoints de hardware puestos y el programa lo detecta ({{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_21 Excepciones 2_21 Excepciones 2.txt|Reversing desde cero, cap. 21}}; transcripción .txt, sin marcas de tiempo). Es un motivo para conocer cómo funcionan las excepciones (ver la rama de vulnerabilidades).

El capítulo 22 explica los dos primeros con el PEB y el comando `hide` de x64dbg ({{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_22 Antidebug 1_22 Antidebug 1.txt|Reversing desde cero, cap. 22}}, 00:02:35–00:07:00). El capítulo 24 muestra un crackme propio con cuatro chequeos y un mensaje que dice cuál lo detectó ({{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_24 Antidebug 2_24 Antidebug 2.txt|Reversing desde cero, cap. 24}}, 00:01:17–00:03:31).

Para esta guía, el objetivo es **entender** esos mecanismos y reconocerlos en un binario, no enseñar a evadirlos. Si un programa se cierra solo bajo el debugger, la pregunta correcta es "¿qué chequeo está fallando?", no "¿qué truco le aplico?".

## Práctica

1. Compilá tu programa `check.exe` (Etapa 1) y abrilo en x64dbg.
2. Recorré con F8 hasta `main`. Anotá `EIP`, `ESP` y `EBP`.
3. Poné un breakpoint por software en la comparación `(a+b)*4 == 480`, ejecutá con `40` y `80`, y verificá los valores en el stack.
4. Poné un breakpoint de hardware *on access* sobre la variable `b` y observá cuándo se lee.
5. Poné un breakpoint de memoria sobre el buffer de `scanf` y observá cuándo se escribe.
6. Agregá un breakpoint con log `{EAX}` en la comparación y ejecutá varias veces con valores distintos. Guardá el log.
7. Etiquetá el bloque "Correcto" y el bloque "Incorrecto". Sacá una captura para tu bitácora.

## Preguntas de repaso

**1. ¿Qué diferencia hay entre F7 y F8?**
F7 entra a las funciones; F8 las ejecuta sin detenerse dentro. Las dos ejecutan la instrucción actual.

**2. ¿Qué byte usa un breakpoint por software?**
`0xCC`, la instrucción `INT3`. El debugger lo restaura al detenerse.

**3. ¿Cuántos breakpoints de hardware hay y de quién son?**
Cuatro (`DR0`–`DR3`) por hilo. Se aplican al contexto del hilo; si no aparecen, revisá qué hilo está seleccionado.

**4. ¿Para qué sirve un breakpoint con `log` y `breakif 0`?**
Para registrar valores sin detener la ejecución. Es útil en bucles donde el programa pasa muchas veces.

**5. ¿Un breakpoint de memoria vigila bytes o páginas?**
Vigila un rango de bytes, pero internamente trabaja con protecciones de página. Por eso puede detenerse ante un acceso cercano al rango.

**6. ¿Qué es el entry point?**
La primera instrucción del código del programa, donde el cargador le pasa el control. No es necesariamente `main`.

## Antes de avanzar

Tenés que poder:

- Abrir un programa, moverte y reconocer las pestañas principales.
- Usar F7, F8 y F9 con intención.
- Poner los tres tipos de breakpoint y explicar en qué se diferencian.
- Configurar un breakpoint condicional con log.
- Guardar un parche en un programa propio y explicar por qué no lo harías en software ajeno.

:::{nota} Puerta de salida
Si podés responder "¿quién escribe este buffer?" con un breakpoint de memoria y "¿cuántas veces pasa por acá y con qué valor?" con uno condicional, ya usás el debugger como herramienta, no como curiosidad.
:::

## Fuentes de esta lección

- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_01 x64dbg primeros pasos_01 x64dbg primeros pasos.txt|Reversing desde cero, cap. 01}} — interfaz, ventanas, F7/F8/F9, entry point.
- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_07 Breakpoints_07 Breakpoints.txt|Reversing desde cero, cap. 07}} — breakpoints por software, hardware, memoria, condicionales y log.
- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_11 Ejercicio 1 - Análisis dinámico_11 Ejercicio 1 - Análisis dinámico.txt|Reversing desde cero, cap. 11}} — etiquetas, análisis visual y parcheo didáctico.
- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_22 Antidebug 1_22 Antidebug 1.txt|Reversing desde cero, cap. 22}} — PEB y detección de debugger.
- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_24 Antidebug 2_24 Antidebug 2.txt|Reversing desde cero, cap. 24}} — cuatro chequeos anti-debug en un crackme propio.
- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_28 Mensajes de Windows_28 Mensajes de Windows.txt|Reversing desde cero, cap. 28}} — WinProc y Dialog procedure, `WM_COMMAND`/Control ID, breakpoint condicional sobre el mensaje y el método `SendMessage` + breakpoint de ejecución en la sección de código.
- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_21 Excepciones 2_21 Excepciones 2.txt|Reversing desde cero, cap. 21}} — lectura de `DR0`–`DR3` desde el `ContextRecord` como detección de breakpoints de hardware.
- [Curso IDA · tutes 9, 10 y 12](../ida_tutes/10.html) — IDA como debugger (soporta varios) y práctica dinámica sobre crackmes propios (`HOLA_REVERSER`, `TEST_REVERSER`).

:::{nota} Capas de esta lección
**Contenido observado en CLS:** el recorrido de la interfaz del capítulo 01, los tres breakpoints del capítulo 07, el log `{EAX}` y las etiquetas del capítulo 11, y los chequeos de los capítulos 22 y 24. **Conocimiento externo:** el mecanismo `INT3`, los registros `DR` y las protecciones de página. **Recomendación editorial:** el límite sobre parcheo y la corrección sobre "cuatro por proceso".
:::

