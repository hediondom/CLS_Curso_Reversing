---
title: "Etapa 1 · Memoria: stack, heap y marcos de función"
description: "Cómo se organiza la memoria de un proceso y por qué el stack explica casi todo lo que ves en un debugger."
etapa: "Etapa 1 · Fundamentos"
---

# Memoria: stack, heap y marcos de función

:::{nota} Objetivo de la lección
Al terminar vas a poder dibujar el stack de una función antes y después de un `call`, ubicar los argumentos, el return address, el `EBP` guardado y las variables locales, y explicar por qué en 64 bits los primeros argumentos no están en el stack.
:::

**Prerrequisitos:** números y little-endian (lección anterior). **Duración sugerida:** 4 horas. Estimación aproximada.

## Las cuatro zonas que importan

Un proceso ve un espacio de direcciones dividido en regiones. Para empezar alcanza con cuatro:

| Zona | Qué guarda | Crece hacia | Vida |
|---|---|---|---|
| **Código** (`.text`) | Instrucciones | — | Todo el proceso |
| **Datos** (`.data`, `.rdata`) | Variables globales, constantes, strings | — | Todo el proceso |
| **Heap** | Memoria pedida en tiempo de ejecución (`malloc`, `new`) | Direcciones altas | Hasta que la liberás |
| **Stack** | Argumentos, direcciones de retorno, variables locales | Direcciones bajas | Hasta que la función retorna |

El stack y el heap son distintos no solo por su ubicación: cambian por motivos distintos. El stack lo administra el procesador con `push`/`pop` y llamadas; el heap lo administra el runtime (la librería C, el recolector de basura, etc.). Esta lección se concentra en el stack porque es el que vas a ver todo el tiempo en un debugger.

## El stack es una pila LIFO

**LIFO** significa *last in, first out*: lo último que apilás es lo primero que sacás. En x86, el stack crece hacia direcciones **más bajas**. `ESP` (en 32 bits) o `RSP` (en 64) apunta siempre a la cima actual.

```asm
push eax      ; ESP = ESP - 4 ; [ESP] = EAX
pop  ebx      ; EBX = [ESP] ; ESP = ESP + 4
```

En 64 bits el decremento es de 8 bytes, salvo que empujes algo más chico.

## Ejemplo paso a paso: el stack de una función de 32 bits

Este ejemplo sale del capítulo 18, donde Ricardo compara una función basada en `EBP` con una basada en `ESP` usando un ejecutable de práctica ({{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_18 Funciones basadas en EBP vs basadas en ESP_18 Funciones basadas en EBP vs basadas en ESP.txt|Reversing desde cero, cap. 18}}, 00:02:40–00:08:30). La función `main` recibe tres argumentos: `argc`, `argv` y `envp`.

### Antes de llamar

La función que llama apila los argumentos **de derecha a izquierda**:

```asm
push envp
push argv
push argc
call main
```

El stack queda así (cada celda son 4 bytes; las direcciones bajas abajo):

```text
        +------------------+
esp --> | argc             |
        | argv             |
        | envp             |
        +------------------+
```

### El `call`

`call` hace dos cosas: empuja la dirección de retorno y salta. La dirección de retorno es la de la instrucción **siguiente** al `call`, para que `ret` sepa dónde volver.

```text
        +------------------+
        | argc             |
        | argv             |
        | envp             |
        | return address   |  <-- ESP
        +------------------+
```

En el ejemplo del video, la dirección de retorno es `0x011912EA` (cap. 18, 00:07:16).

### El prólogo

Casi todas las funciones de 32 bits empiezan igual:

```asm
push ebp          ; guarda el EBP de la función que llamó
mov  ebp, esp     ; fija un punto de referencia estable
sub  esp, 0x28    ; reserva espacio para variables locales
```

Después del prólogo, el stack tiene una forma reconocible:

```text
        +------------------+  <-- EBP + 0x10
        | envp (3.er arg)  |
        | argv (2.º arg)   |  <-- EBP + 0x0C
        | argc (1.er arg)  |  <-- EBP + 0x08
        | return address   |  <-- EBP + 0x04
        | EBP guardado     |  <-- [EBP]
        +------------------+
        | local [EBP-4]    |
        | local [EBP-8]    |  <-- espacio reservado por sub esp, 0x28
esp --> | ...              |
        +------------------+
```

**Cuidado con el orden:** los argumentos se apilan de derecha a izquierda, así que el primero de la función queda en la dirección más baja, justo arriba del return address. Por eso `[EBP+8]` es `argc`, `[EBP+0x0C]` es `argv` y `[EBP+0x10]` es `envp`. Lo importante no es memorizar los números de este ejemplo, sino el método: **contá desde `EBP` y verificá en el panel de stack**.

En el video, Ricardo muestra la correspondencia entre la vista estática del stack de IDA y la realidad del debugger: los tres `push`, el return address, el `push ebp`, el `mov ebp, esp` y el `sub esp, 0x28` aparecen en ese orden (cap. 18, 00:02:34–00:10:00).

### El epílogo

Al final, la función deshace lo que hizo:

```asm
mov esp, ebp      ; libera las variables locales
pop  ebp          ; recupera el EBP de la función que llamó
ret               ; saca el return address y vuelve
```

`leave` es una instrucción que hace las dos primeras operaciones juntas. Si ves `leave; ret`, es el mismo patrón.

:::{nota} Por qué `EBP` y no `ESP`
`ESP` cambia cada vez que la función empuja algo para llamar a otra función. Si las variables locales se referenciaran con `ESP`, cada `push` cambiaría sus direcciones. Por eso el prólogo copia `ESP` a `EBP` y usa `EBP` como referencia estable: `[EBP-4]`, `[EBP-8]`, etc. (cap. 18, 00:10:30–00:12:10).
:::

## 64 bits: los argumentos viajan en registros

En x64 cambia la convención. Los primeros cuatro argumentos enteros van en registros:

| Argumento | Registro |
|---|---|
| 1.º | `RCX` |
| 2.º | `RDX` |
| 3.º | `R8` |
| 4.º | `R9` |

Los demás van en el stack, y el llamador debe reservar **32 bytes de shadow space** (`0x20`) antes del `call`, aunque no use todos los registros. Por eso en el capítulo 18 se ve `sub rsp, 0x138` para las variables locales y referencias del tipo `[rsp+0x20]`, `[rsp+0x28]`, etc. (00:14:00–00:20:00).

En 64 bits es común que las funciones sean **basadas en RSP**: no hay `push rbp; mov rbp, rsp` porque `RSP` no cambia tanto (los argumentos no se apilan uno por uno). Las variables locales se referencian como `[rsp+0xNN]`, y el desensamblador suele mostrar el offset relativo al valor inicial de `RSP` para que no tengas que recalcular.

:::{aviso} El error de contar mal el shadow space
Cuando el quinto argumento va al stack, no va inmediatamente después del return address: va después de los 32 bytes reservados para los cuatro registros. Si ves `[rsp+0x28]` como primer argumento apilado, es porque `0x20` son los shadow slots y `0x28` el primer argumento real (cap. 18, 00:17:00–00:18:30).
:::

## Heap: la memoria que pedís vos

El heap se usa cuando el tamaño no se conoce en tiempo de compilación o cuando el dato tiene que sobrevivir a la función que lo creó. En C:

```c
char *buf = malloc(64);
if (buf == NULL) { /* error */ }
strcpy(buf, "hola");
free(buf);
```

En Python, `bytearray(64)` o una lista cumplen un rol parecido, pero el manejo lo hace el intérprete.

Tres diferencias prácticas con el stack:

1. **Vos administrás la vida** (en C). Si te olvidás de `free`, hay fuga de memoria; si liberás dos veces, corrupción.
2. **No tiene un orden LIFO.** Podés liberar en cualquier orden.
3. **Los errores son más silenciosos.** Un desborde de stack suele terminar en crash; un desborde de heap puede pasar desapercibido y explotar después.

## Estructuras y objetos en memoria

Una **estructura** (`struct`) es un dato compuesto: agrupa varios campos, que pueden ser de **distinto tipo**, uno detrás del otro. Es la diferencia con un array, que repite el mismo tipo. En memoria, una estructura es un bloque donde cada campo vive en un **offset fijo** desde el inicio.

Por eso, a bajo nivel, trabajar con una estructura casi siempre se ve igual: un registro tiene la **dirección base** de la estructura y las instrucciones le suman un offset para llegar a cada campo.

```asm
mov eax, [ebp-4]      ; EAX = dirección base de la estructura
mov ecx, [eax+0x58]   ; lee el campo que está en el offset 0x58
lea edx, [eax+4]      ; NO lee: deja en EDX un puntero al campo en +4
```

La distinción entre `mov ecx, [eax+0x58]` (leer el **valor** del campo) y `lea edx, [eax+4]` (calcular la **dirección** del campo, para pasarla como puntero) es la que más confunde al principio. Si no hay corchetes alrededor del resultado, es una dirección.

:::{aviso} El padding cambia los offsets
El tamaño de una estructura **no** es siempre la suma de sus campos. Por alineación, el compilador inserta bytes de relleno (*padding*). En 32 bits la alineación por defecto es 4, así que una estructura con un `DWORD` (4) y un `BYTE` (1) no mide 5 sino **8**: se agregan 3 bytes para que el tamaño sea múltiplo de 4. Si al leer un listado los offsets no cierran, sospechá del padding (cap. 20b).
:::

Un **objeto** de C++ es una estructura con un par de agregados. Cuando ves `new`, en el fondo se llama a `malloc` para reservar el tamaño de la clase (por ejemplo `0x3C` bytes) y después se llama al **constructor** para inicializar los campos. A los métodos, la instancia (el puntero `this`) se pasa normalmente en **ECX**; dentro del método, `[ecx+offset]` accede a cada campo.

Si la clase tiene **métodos virtuales**, el primer campo del objeto (offset 0) es un puntero a la **vtable**: una tabla de punteros a esos métodos. Por eso, al reversear, "levanta el primer campo y llama a `[campo+N]`" es la firma de una llamada a un método virtual. El cap. 33 lo muestra con una clase propia cuyo objeto empieza con el puntero a la vtable y cuyos cuatro métodos virtuales están en la tabla, en orden.

## Buffers, strings y el centinela

Un string en C es una secuencia de bytes terminada en `0x00`. `"Hola"` ocupa cinco bytes: `48 6F 6C 61 00`. Ese cero es el que permite a `strlen` saber dónde termina.

Cuando una función copia datos a un buffer sin verificar el tamaño, puede escribir más allá del final. Ese es el punto de partida de los desbordes de buffer, que en esta guía se estudian solo en programas propios y en la rama de vulnerabilidades. El capítulo 15 muestra un detalle defensivo relacionado: el **security cookie** que el compilador coloca en el stack y verifica antes de retornar, calculado con un XOR contra `RSP`, para detectar que alguien pisó el return address ({{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_15 Ejercicio 2 - Análisis estático_15 Ejercicio 2 - Análisis estático.txt|Reversing desde cero, cap. 15}}, 00:07:34–00:08:00).

## Práctica

1. Dibujá el stack de una función `int suma(int a, int b)` en 32 bits, desde el `push b` hasta el `ret`. Marcá `EBP`, `ESP`, argumentos, return address y variable local.
2. Escribí en C una función que reserve un buffer de 16 bytes en el stack y otra que use `malloc(16)`. Compilalas y mirá en x64dbg dónde queda cada buffer.
3. En el programa anterior, poné un breakpoint en la primera instrucción de la función y anotá `ESP` y `EBP`. Después del prólogo, volvé a anotarlos. ¿Cuánto cambió `ESP`?
4. Escribí el mismo programa para x64 y verificá en qué registros llegan `a` y `b`.
5. Explicá por qué `[ebp+8]` suele ser el primer argumento en 32 bits y por qué en 64 bits no lo es.

## Preguntas de repaso

**1. ¿Quién empuja el return address?**
La instrucción `call`, no la función llamada. `ret` lo consume.

**2. ¿Por qué el stack crece hacia abajo?**
Es una convención de la arquitectura x86: `push` decrementa el puntero y `pop` lo incrementa. Lo importante es que el modelo mental sea consistente, no la dirección física.

**3. ¿Qué guarda `push ebp` en el prólogo?**
El valor de `EBP` de la función que llamó, para poder restaurarlo al final y no romper las referencias de esa función.

**4. ¿Dónde están las variables locales?**
Entre `EBP` y `ESP`, en direcciones menores que `EBP` (`[EBP-4]`, `[EBP-8]`, etc.). El `sub esp, N` reserva ese espacio.

**5. ¿Los argumentos de una función de 64 bits siempre están en el stack?**
No. Los primeros cuatro enteros van en `RCX`, `RDX`, `R8` y `R9`; el resto va al stack después de 32 bytes de shadow space.

**6. ¿Qué diferencia hay entre un desborde de stack y uno de heap?**
El de stack suele pisar el return address y provocar un crash inmediato; el de heap corrompe estructuras internas y puede no manifestarse hasta mucho después.

## Antes de avanzar

Tenés que poder:

- Dibujar el stack de un `call` de 32 bits con argumentos, return address, `EBP` guardado y locales.
- Nombrar los registros de argumentos de x64 y explicar el shadow space.
- Explicar la diferencia entre stack y heap con un ejemplo de cada uno.
- Reconocer un prólogo y un epílogo en un listado de assembly.

:::{nota} Puerta de salida
Si podés explicar el stack sin mirar el dibujo, estás listo para verlo en vivo en el debugger. Si no, volvé al ejemplo del capítulo 18 y reconstruilo en papel.
:::

## Fuentes de esta lección

- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_18 Funciones basadas en EBP vs basadas en ESP_18 Funciones basadas en EBP vs basadas en ESP.txt|Reversing desde cero, cap. 18}} — stack de 32 y 64 bits, prólogo, epílogo, shadow space.
- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_15 Ejercicio 2 - Análisis estático_15 Ejercicio 2 - Análisis estático.txt|Reversing desde cero, cap. 15}} — security cookie y protección del return address.
- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_01 x64dbg primeros pasos_01 x64dbg primeros pasos.txt|Reversing desde cero, cap. 01}} — ventana de stack y mapa de memoria.
- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_20b Apéndice teórico 3 - Estructuras_20b Apéndice teórico 3 - Estructuras.txt|Reversing desde cero, cap. 20b}} — estructuras, acceso base+offset, stack vs heap y padding/alineación (transcripción .txt, sin marcas).
- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_33 C++ Clases_33 C++ Clases.txt|Reversing desde cero, cap. 33}} — objetos C++: `new`/`malloc`, constructor, `this` en ECX y puntero a la vtable en el offset 0 (transcripción .txt, sin marcas).

:::{nota} Capas de esta lección
**Contenido observado en CLS:** el ejemplo del capítulo 18 (argumentos, return address `0x011912EA`, `sub esp, 0x28`, shadow space), la cookie del capítulo 15, el padding del 20b y el objeto con vtable del 33. **Conocimiento externo:** layout general del espacio de direcciones, heap y strings en C. **Recomendación editorial:** los diagramas y ejercicios.
:::

