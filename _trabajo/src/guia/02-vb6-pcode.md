---
title: "2.33 · VB6 y p-code: nativo vs interpretado"
description: "Distinguir un ejecutable Visual Basic 6 nativo de uno en p-code, leer la VBHeader y las llamadas a MSVBVM60, y usar VB Decompiler / P32Dasm / WKTVBDE. Tecnología legada. Profundiza 2.13."
etapa: "Etapa 2 · Ampliación de 2.13 (Huella de compilador)"
---

# VB6 y p-code: nativo vs interpretado

:::{nota} Objetivo de la lección
Distinguir un ejecutable **Visual Basic 6 nativo** de uno en **p-code**, leer la **VBHeader** para orientarte, reconocer las llamadas al runtime `MSVBVM60` y saber qué herramienta usar en cada caso. **Prerrequisitos:** huella de compilador ([2.13](02-huella-compilador.html)).
:::

:::{aviso} Tecnología legada
VB6 es de ~1998 y está discontinuado, pero **sigue apareciendo**: malware viejo, crackmes de la escena y software heredado. Se incluye como contexto histórico, igual que OllyDbg y MASM32 en [2.9](02-herramientas.html).
:::

## Por qué VB6 es distinto

Un ejecutable VB6 no es C compilado: apoya casi todo en un **runtime**, `MSVBVM60.dll` (*Microsoft Visual Basic Virtual Machine*). Y puede estar compilado de dos maneras muy distintas —nativo o p-code—, que se analizan de forma diferente (**conocimiento externo**).

## La VBHeader: tu punto de entrada

El *entry point* de un VB6 es casi siempre el mismo *stub*: llama a `ThunRTMain` de `MSVBVM60` pasándole un puntero a la **VBHeader** (firma `VB5!`). Desde esa estructura se llega a:

- **`ProjectInfo`** — datos del proyecto y tabla de objetos.
- **`ObjectTable`** — los forms y clases, con sus controles y **eventos**.
- La info que te dice si hay **tablas de p-code** o código nativo por evento.

Encontrar la VBHeader es el «abrir la puerta»: a partir de ahí reconstruís la estructura del programa (qué forms, qué botones, qué maneja cada evento).

## Nativo vs p-code

| | VB6 nativo | VB6 p-code |
|---|---|---|
| Qué contiene | x86 real, con **muchísimas** llamadas a `MSVBVM60` | **Bytecode** interpretado por el motor dentro de `MSVBVM60` |
| En IDA/Ghidra | Se lee como x86 (plagado de *thunks* `__vba*`) | Ves el **intérprete**, no la lógica (como una VM, 2.26) |
| Herramienta | Desensamblador normal + VB Decompiler | VB Decompiler / P32Dasm; debug con **WKTVBDE** |

La clave: en **nativo**, la lógica está en el x86 (aunque enterrada entre llamadas al runtime); en **p-code**, el x86 que ves es el *intérprete* genérico y la lógica está en un bytecode —muy parecido conceptualmente a la virtualización de 2.26, pero **estándar y documentado** por la comunidad, no secreto—.

:::{aviso} Ante un p-code, IDA/Ghidra no alcanzan
Con un binario en p-code, un desensamblador clásico solo te muestra el **intérprete de VB** (código de `MSVBVM60`), no tu lógica. La única vía operativa es una herramienta especializada —**VB Decompiler**— que entiende el bytecode de VB y reconstruye el pseudocódigo y los formularios. No pierdas tiempo intentando leer la lógica en el listado x86: ahí no está.
:::

## Reconocer las llamadas del runtime

En VB6 nativo, los nombres `__vba*` son el mapa de la lógica (aunque no tengas símbolos propios):

- `__vbaStrCmp`, `__vbaStrComp` — comparación de strings (típico de un *check* de serial).
- `__vbaVarTstEq`, `__vbaVarTstNe` — comparación de `Variant`.
- `rtcMsgBox` — un `MsgBox` («clave correcta/incorrecta»).
- `__vbaStrCat`, `__vbaStrMove` — armado de strings.

## Ejemplo paso a paso: un check de serial en VB6 nativo

*(Ejemplo **ilustrativo**: patrón típico de un crackme VB6 propio/didáctico.)*

```asm
; en VB6 nativo, el "check" se delata por las llamadas al runtime
push   offset serial_ingresado
push   offset serial_esperado
call   __vbaStrCmp            ; compara los dos strings
test   eax, eax              ; 0 = iguales
jnz    short serial_malo
push   offset msg_ok
call   rtcMsgBox             ; "Correcto"
```

No hace falta entender todo el runtime: la secuencia **`__vbaStrCmp` → `test` → salto → `rtcMsgBox`** es la firma de un chequeo de serial. En p-code, en cambio, esto no se ve como x86: hay que abrirlo con **VB Decompiler**, que reconstruye los forms y el bytecode de cada evento, y para seguir la ejecución se usa **WKTVBDE**, un debugger específico de p-code.

## Práctica

En tu VM, con binarios **propios o crackmes didácticos**:

1. Tomá (o compilá, si tenés el IDE) un VB6 y clasificalo **nativo vs p-code** con DIE y con la VBHeader.
2. En uno nativo, ubicá la VBHeader desde el entry point y listá los forms/eventos.
3. Encontrá un chequeo con `__vbaStrCmp` + `rtcMsgBox` y explicá la lógica.
4. Abrí un p-code en VB Decompiler y describí por qué IDA no mostraba esa lógica.

## Preguntas de repaso

?? ¿Qué papel cumple `MSVBVM60.dll`?
!! Es el **runtime** de VB6: provee las funciones (`__vba*`, `rtc*`) y, en los binarios p-code, el **intérprete** que ejecuta el bytecode. Casi todo VB6 depende de él.

?? ¿Para qué buscás la VBHeader?
!! Es la estructura (firma `VB5!`) a la que apunta el stub de arranque; desde ella llegás a `ProjectInfo` y `ObjectTable` para reconstruir forms, controles y eventos, y ver si hay p-code.

?? ¿Cuál es la diferencia práctica entre nativo y p-code al analizar?
!! En **nativo** la lógica está en el x86 (entre llamadas `__vba*`) y se lee con un desensamblador normal. En **p-code** el x86 es el intérprete; la lógica está en bytecode y hay que usar VB Decompiler / WKTVBDE.

?? ¿Por qué el p-code se parece a la virtualización de 2.26?
!! Porque también hay un **intérprete** ejecutando un **bytecode** en vez de x86 directo. La diferencia: el p-code de VB6 es **estándar y documentado**, no un lenguaje secreto por binario.

?? ¿Qué secuencia delata un check de serial en VB6 nativo?
!! `__vbaStrCmp` (comparar) → `test`/salto → `rtcMsgBox` (mensaje). Reconocer esos nombres del runtime te da la lógica sin entender todo el motor.

:::{nota} Puerta de salida
Podés: (1) clasificar un VB6 como nativo o p-code; (2) ubicar la VBHeader y reconstruir forms/eventos; (3) leer un chequeo por las llamadas `__vba*`/`rtc*`; (4) explicar por qué el p-code necesita VB Decompiler/WKTVBDE y en qué se parece a una VM.
:::

## Fuentes de esta lección

- [vb-decompiler.org](https://www.vb-decompiler.org/) — reconstrucción de forms, nativo y p-code (conocimiento externo).
- [Detect It Easy](https://github.com/horsicq/Detect-It-Easy) — identifica VB6 y si es nativo o p-code.
- Formato **VBHeader**/`ProjectInfo`/`ObjectTable` — documentación de la comunidad de reversing de VB6 (P32Dasm, WKTVBDE).
- [2.13 Huella de compilador](02-huella-compilador.html) y [2.26 VM](02-ofuscacion-vm.html) (el paralelo intérprete/bytecode).

:::{nota} Capas de esta lección
**Contenido observado en CLS:** VB6 como una de las huellas de compilador de 2.13 y el contexto legado del material (VB en Teorias_Numeradas). **Conocimiento externo (agregado por esta edición):** VBHeader, nativo vs p-code, las llamadas del runtime y las herramientas. **Recomendación editorial:** ejemplos y práctica ilustrativos, sobre binarios propios/didácticos.
:::
