---
title: "2.10 · Ofuscación nativa: leer lo que no quiere ser leído"
description: "Reconocer código ofuscado nativo —secciones invertidas, basura, saltos al medio, cadenas cifradas, flujo aplanado— y encontrar el bloque real sin parchear a ciegas."
etapa: "Etapa 2 · Windows intermedio"
---

# Ofuscación nativa: leer lo que no quiere ser leído

:::{nota} Objetivo de la lección
Reconocer las señales de que un binario nativo está **ofuscado** y tener un método para llegar al código real, sin romperlo. **Prerrequisitos:** PE y secciones (1.4), assembly y flujo (2.3–2.4), IDA y debugger (2.6–2.7).
:::

Esto es **reconocimiento defensivo**: entender cómo se ve el código ofuscado para poder analizarlo. No se enseña a ofuscar ni a desempaquetar protectores comerciales.

## Qué es la ofuscación nativa

Ofuscar es hacer que el programa **siga funcionando igual** pero sea difícil de leer para una persona y confuso para el desensamblador. A diferencia de un packer, el código puede estar a la vista: lo que cambia es la *forma*. Las técnicas típicas (**conocimiento externo**):

- **Secciones reordenadas o con nombres falsos**, y el *entry point* lejos de lo esperado.
- **Basura entre bloques**: bytes que no se ejecutan pero que el desensamblador intenta interpretar como instrucciones.
- **Saltos al medio de una instrucción**: un `jmp`/`jnz` cae a un byte que no es el inicio real, así el listado lineal muestra una instrucción que *no es* la que se ejecuta.
- **Código muerto y opaco**: `test ebp, ebp` seguido de `jnz` cuando `ebp` nunca es cero — un salto que *siempre* se toma, disfrazado de condicional.
- **Strings ocultas**: con un `00` adelante, armadas en el stack byte a byte, o cifradas y descifradas en runtime.

## Cómo se ve en CLS

El capítulo 26 analiza el ejercicio «choteado» y muestra el síntoma clásico: al abrirlo, **IDA lo muestra "todo roto"** y al forzarlo a función queda "todo feo"; en x64dbg tampoco se ve claro. Al mirar el *memory map* aparece la causa: **las secciones están cambiadas** —la primera sección está vacía y el código ejecutable recién está en la segunda—, y eso **engaña al desensamblador**. Con los símbolos cargados se empieza a navegar; sin ellos, la dificultad es la misma pero hay que apoyarse en la traza ({{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_26 Ofuscación 1_26 Ofuscación 1.txt|Reversing desde cero, cap. 26}}).

El capítulo 30 resuelve la segunda parte y agrega un paso de preparación muy útil para analizar: cargar **todas las secciones** en IDA y, para trabajar con direcciones estables, **poner a cero el `DLL characteristics`** (el bit de `DYNAMICBASE`/ASLR) con *Patch Program → Change byte* y *Apply patches to input file*, de modo que el módulo cargue siempre en su base (aquí `0x400000`) ({{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_30 Ofuscación 2_30 Ofuscación 2.txt|Reversing desde cero, cap. 30}}). Es un parche **sobre el crackme didáctico** del ejercicio (hecho para practicar), para poder estudiarlo con direcciones estables; no sobre software ajeno.

## El método: encontrar el bloque real

1. **Sospechá temprano.** Si IDA no arma funciones, si hay flechas que cruzan todo o si el *memory map* no coincide con lo que esperás, asumí ofuscación.
2. **Mirá las secciones primero** (memory map / segments): dónde está de verdad el código ejecutable y cuál es la base.
3. **Dejá las direcciones quietas**: en tu laboratorio, desactivá ASLR del ejecutable propio para que las direcciones no cambien entre corridas.
4. **Seguí la ejecución, no el listado.** Ante un salto sospechoso, poné un breakpoint y mirá a dónde salta *de verdad*; el desensamblado lineal puede estar mostrando bytes que no se ejecutan.
5. **No NOPees a ciegas.** Reemplazar bytes sin entender rompe el programa y borra la pista. Comentá y renombrá; parchá solo cuando sabés qué hace el byte.

## Ejemplo paso a paso: un salto al medio de una instrucción

*(Ejemplo **ilustrativo**: bytes construidos para mostrar la técnica, no un volcado de un binario puntual.)*

Supongamos estos bytes a partir de `0x401000`:

```text
401000:  B8 EB FE 90 90        ; así lo decodifica el desensamblador LINEAL
         mov eax, 0x9090FEEB

pero el código que viene antes hace:  jmp 0x401001  (salta UN byte adelante)

401001:  EB FE                 ; reinterpretado desde 0x401001
         jmp short 0x401001    ; EB = jmp corto, FE = -2  → salta a sí mismo
```

Qué pasó: el byte `B8` (opcode de `mov eax, imm32`) hizo que IDA se "comiera" los 4 bytes siguientes como el inmediato. Pero el flujo real nunca ejecuta el `B8`: entra en `0x401001`, donde `EB FE` es un `jmp` a sí mismo (lo que viste en [2.4](02-flujo.html): desplazamiento `FE` = −2 sobre el final de la instrucción). El listado lineal mostraba una instrucción que **no se ejecuta**; la real aparece solo si decodificás desde el offset correcto. Por eso se sigue la **ejecución** (poné un breakpoint en `0x401001`) y no el listado.

## Cadenas ocultas: cómo reconocer la rutina que las descifra

En [2.7](02-ida.html) viste por qué una cadena puede no aparecer en la ventana de strings. Cuando la causa es que está **cifrada**, el patrón en el código suele ser reconocible aunque el algoritmo cambie (**conocimiento externo**):

- un **bucle corto** que recorre un buffer con un índice o puntero que avanza de a uno (o de a dos, si es UTF-16);
- una **operación reversible** por byte: `xor` con una constante o con un byte de una clave que se repite (`índice mod largo`), o `add`/`sub`/`rol`;
- un **destino** que después se pasa a una API que espera texto (`CreateFileW`, `RegOpenKeyExW`, `MessageBoxW`, `LoadLibraryW`).

*(Ejemplo **ilustrativo**: descifrado con `xor` y clave de un byte, x64.)*

```asm
lea   rsi, [rip+datos_cifrados]   ; fuente en .rdata (bytes ilegibles)
lea   rdi, [rsp+40h]              ; destino en el stack
xor   ecx, ecx
bucle:
movzx eax, byte ptr [rsi+rcx]
xor   al, 5Ah                     ; clave de un byte
mov   [rdi+rcx], al
inc   rcx
cmp   rcx, 0Ch                    ; largo fijo: 12 bytes
jb    bucle
mov   byte ptr [rdi+rcx], 0       ; terminador
lea   rcx, [rsp+40h]
call  cs:LoadLibraryA             ; el texto descifrado es un nombre de DLL
```

Cómo se lee: el `xor al, 5Ah` dentro del bucle es la transformación; `0Ch` es el largo; el destino termina como argumento de `LoadLibraryA`, así que el texto es un nombre de módulo. Para recuperarlo hay dos caminos, y conviene hacer los dos: **dinámico**, con un breakpoint en la llamada a `LoadLibraryA` y leyendo `RCX`; **estático**, aplicando la misma operación a los 12 bytes con un script (en IDA, IDAPython; en Ghidra, un script de [2.16](02-ghidra.html)). Si coinciden, anotás la cadena en un comentario junto al bucle y renombrás el buffer.

Lo que **no** conviene: ejecutar el programa entero para "ver qué cadenas aparecen" si no sabés qué hace, ni copiar la rutina sin entender de dónde sale la clave (puede depender de un dato del entorno y dar otro resultado en otra máquina).

## Aplanamiento del flujo de control

Otra técnica frecuente en ofuscadores de código nativo es el **aplanamiento del flujo de control** (*control-flow flattening*): los bloques básicos de una función se sacan de su orden natural y se ponen **todos al mismo nivel**, dentro de un bucle infinito con un `switch` que elige qué bloque ejecutar según una **variable de estado**. Cada bloque, al terminar, escribe en esa variable el número del bloque siguiente (**conocimiento externo**; el ofuscador de investigación Obfuscator-LLVM lo describe así).

Cómo se ve en el grafo de IDA o Ghidra:

- un **despachador** central (comparaciones o una tabla de saltos sobre la misma variable) al que vuelven todos los bloques;
- muchos bloques "hermanos" sin relación aparente entre sí, todos con una flecha de vuelta al despachador;
- cada bloque termina con un `mov [var_estado], constante` (o con un cálculo que da una constante) antes de volver.

El método para leerlo no es mirar el grafo, que ya no dice nada, sino **reconstruir la secuencia**: para cada bloque, anotá qué valor de estado lo selecciona y qué valor deja al salir. Con esa tabla (estado → bloque → estado siguiente) se recupera el orden real. Los saltos condicionales originales aparecen como bloques que dejan **uno de dos valores** según una comparación. Hacerlo a mano sirve para funciones chicas; para funciones grandes existen complementos que lo automatizan, fuera del alcance de esta lección.

| Señal | Qué sospechar | Cómo confirmarlo |
|---|---|---|
| Todos los bloques vuelven a un mismo punto | Aplanamiento | Ubicar la variable que compara el despachador |
| `jnz` tras `test` con registro siempre no nulo | Predicado opaco | Seguir el valor del registro en el debugger |
| Bucle corto con `xor` sobre un buffer que va a una API | Cadena cifrada | Breakpoint en la API y leer el argumento |
| Ráfaga de `mov` con constantes imprimibles | Cadena armada en el stack | Leer las constantes como bytes en little-endian |
| El listado no arma funciones | Basura o saltos al medio | Seguir la ejecución, no el listado |

## Práctica

En tu VM, sobre un **ejercicio propio o un crackme didáctico** (hay varios en el [Banco de prácticas](../practicas.html)):

1. Abrilo en IDA y en x64dbg y anotá tres señales de que algo no se lee normal.
2. Mirá el *memory map*: ¿la sección de código es la primera? ¿La base es la esperada?
3. Encontrá un salto condicional que en realidad sea incondicional (p. ej. `test reg,reg` + `jnz` con el registro siempre distinto de cero) y explicá por qué.
4. Llegá al primer bloque "real" de lógica siguiendo la ejecución, no el listado.
5. En un programa **propio**, guardá un nombre de DLL cifrado con `xor` de un byte y descifralo antes de usarlo. Recuperalo de las dos formas (breakpoint en la API y script sobre los bytes) y compará.
6. Escribí a mano, en C, una función chica con un `if` y un bucle, y una segunda versión "aplanada" con `while (1) { switch (estado) { ... } }`. Compilá ambas y compará los grafos; armá la tabla estado → bloque → estado siguiente de la versión aplanada.

## Preguntas de repaso

?? ¿Por qué un listado lineal puede mostrar una instrucción que no es la que se ejecuta?
!! Porque un salto puede caer **al medio** de lo que el desensamblador tomó como una instrucción; a partir de ese offset los bytes se decodifican distinto. Lo que se ejecuta es la secuencia que sigue el flujo real, no la que el desensamblador alineó de arriba a abajo.

?? Viste `test ebp, ebp` seguido de `jnz`. ¿Por qué puede ser ofuscación?
!! Si en ese punto `ebp` nunca vale cero, `ZF` nunca se activa y el `jnz` **se toma siempre**: es un salto incondicional disfrazado de condicional, para que parezca que hay dos caminos cuando hay uno.

?? En el «choteado», ¿qué pista da el *memory map*?
!! Que las secciones están **reordenadas**: la primera está vacía y el código ejecutable está en la segunda. Eso explica por qué el desensamblador no arma bien las funciones.

?? ¿Por qué el capítulo 30 pone a cero el `DLL characteristics`?
!! Para **desactivar ASLR** del ejecutable y que cargue siempre en la misma base (`0x400000`), así las direcciones son estables mientras se lo analiza. Es un parche sobre un binario propio de práctica.

?? ¿Por qué "no NOPear a ciegas"?
!! Porque reemplazar bytes sin entenderlos rompe la lógica y borra la evidencia de qué hacía el código. Primero se entiende (comentando, trazando); recién después, si hace falta y es un binario propio, se parchea.

?? ¿Qué tres elementos delatan una rutina que descifra una cadena?
!! Un bucle corto sobre un buffer, una operación reversible por byte (`xor`, `add`, `rol`) y un destino que después se pasa a una API que espera texto.

?? ¿Por qué conviene recuperar una cadena cifrada de forma estática y dinámica?
!! Porque se controlan entre sí: si el script sobre los bytes y el argumento leído en el breakpoint coinciden, la lectura de la rutina es correcta; si no, la clave puede depender del entorno o la rutina tiene un paso que no viste.

?? En un grafo aplanado, ¿qué tabla reconstruís para recuperar el orden?
!! Estado → bloque → estado siguiente: qué valor de la variable selecciona cada bloque y qué valor deja al salir. Los bloques que dejan uno de dos valores según una comparación son los condicionales originales.

:::{nota} Puerta de salida
Podés: (1) nombrar tres señales de ofuscación en un binario; (2) explicar un salto al medio de una instrucción y un salto condicional que siempre se toma; (3) usar el *memory map* para ubicar el código real; (4) llegar al primer bloque de lógica siguiendo la ejecución; (5) reconocer una rutina de descifrado de cadenas y recuperar el texto de dos formas; (6) reconocer un despachador de flujo aplanado y reconstruir el orden de una función chica.
:::

:::{nota} Lo que queda fuera
La ofuscación por **máquina virtual** (el código se traduce a un bytecode propio que interpreta un "procesador" embebido), las expresiones mixtas booleano-aritméticas y la desofuscación automática por ejecución simbólica. Se mencionan para reconocerlas por nombre; analizarlas exige herramientas y tiempo que exceden esta etapa, y en protectores comerciales entran en el límite del curso (no desempacar protectores comerciales).
:::

## Fuentes de esta lección

- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_26 Ofuscación 1_26 Ofuscación 1.txt|Reversing desde cero, cap. 26}} — el «choteado» con símbolos: IDA/x64dbg confundidos, secciones invertidas en el memory map.
- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_30 Ofuscación 2_30 Ofuscación 2.txt|Reversing desde cero, cap. 30}} — cargar todas las secciones y poner a cero `DLL characteristics` (ASLR) para direcciones estables.
- [Curso IDA · tutes 14–18](../ida_tutes/14.html) — contexto de binarios que "no se leen de una".
- Conocimiento externo: [Obfuscator-LLVM, Control Flow Flattening](https://github.com/obfuscator-llvm/obfuscator/wiki/Control-Flow-Flattening) — descripción del aplanamiento con variable de estado y `switch`; [FLOSS](https://github.com/mandiant/flare-floss) — tipos de cadenas que extrae (estáticas, armadas en el stack, decodificadas).

:::{nota} Capas de esta lección
**Contenido observado en CLS:** el «choteado» de los capítulos 26 y 30, las secciones invertidas y el parche de `DLL characteristics`. **Conocimiento externo:** la taxonomía de técnicas (basura, saltos al medio, código opaco, strings ocultas), el patrón de las rutinas de descifrado y el aplanamiento del flujo de control. **Ejemplo ilustrativo:** los bytes del salto al medio y el bucle de descifrado con `xor`. **Recomendación editorial:** el método de cinco pasos, la regla de no NOPear a ciegas, la tabla de señales y la recuperación doble (estática y dinámica).
:::
