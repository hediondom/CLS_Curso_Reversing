---
title: "Etapa 2 · IDA y el análisis estático"
description: "Navegar un binario sin ejecutarlo: strings, referencias, grafo, renombrado, rebase y decompilador."
etapa: "Etapa 2 · Introducción al reversing"
---

# IDA y el análisis estático

:::{nota} Objetivo de la lección
Al terminar vas a poder abrir un ejecutable en IDA (o Ghidra), encontrar una cadena, llegar al código que la usa, leer el grafo de una función, renombrar variables y comentar el flujo, y sincronizar direcciones con el debugger.
:::

**Prerrequisitos:** PE, instrucciones, flujo y llamadas. **Duración sugerida:** 5 horas. Estimación aproximada.

## Para qué sirve un desensamblador

Un debugger te muestra el programa **ejecutándose**. Un desensamblador te muestra el programa **completo, sin ejecutarlo**. Esa diferencia importa por tres razones:

1. Hay código que no podés ejecutar: malware, un binario de otra arquitectura, una función a la que no sabés cómo llegar.
2. Hay funciones que se llaman una vez cada mil ejecuciones y no querés esperar a que pasen.
3. El análisis estático te deja **leer todo** el código, no solo el camino que tomaste.

El capítulo 14 lo dice con un ejemplo claro: si estás analizando un virus, no lo corrés para ver qué hace; primero lo mirás estático. Y si estás buscando un bug en una función que no sabés cómo se alcanza, la podés analizar igual ({{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_14 Conociendo IDA_14 Conociendo IDA.txt|Reversing desde cero, cap. 14}}, 00:03:57–00:05:30).

## Abrir el archivo

1. **File → Open** y elegí el `.exe`.
2. IDA detecta el formato: `Portable executable for 80386 (PE)` indica un PE de 32 bits; si fuera de 64, lo diría.
3. En el diálogo de carga podés aceptar los valores por defecto. *Manual load* sirve si querés cargar secciones que IDA no trae por defecto (por ejemplo, el header).
4. Si el binario tiene símbolos PDB, IDA te los pide. Si no, cancelá: IDA hará su mejor esfuerzo.
5. Esperá a que termine el autoanálisis (el indicador deja de girar).

El capítulo 14 muestra este recorrido y aclara que la versión gratuita (IDA Free) tiene limitaciones: menos procesadores, un solo decompilador y, según la versión, solo IDC en lugar de Python (00:00:40–00:02:30).

El tutorial escrito de `descargas_sueltas` agrega un dato práctico: para saber si un PE es de 32 o 64 bits antes de abrirlo, mirá los bytes que siguen a la firma `PE`. En el documento, un binario de 64 bits muestra `PE..d†` y uno de 32 bits `PE..L`; la diferencia está en la cabecera opcional (PE32+ vs PE32) ({{src:descargas_sueltas/INTRODUCCIÓN AL REVERSING CON IDA PRO DESDE CERO.docx|Introducción al reversing con IDA Pro desde cero, 2016}}, sección "Lo primero es lo primero").

:::{aviso} Sobre las versiones
El curso usa IDA de 32 bits de una versión de escritorio. La interfaz cambió bastante en las versiones 8 y 9, y las capacidades de IDA Free también. Los conceptos —strings, xrefs, grafo, renombrado, rebase— se mantienen; los botones y atajos pueden variar. Si un atajo no funciona, buscalo en el menú.
:::

## Las ventanas que vas a usar

| Ventana | Cómo abrirla | Para qué |
|---|---|---|
| **IDA View** | `View → Open subviews → Disassembly` | Código desensamblado |
| **Hex View** | `View → Open subviews → Hex` | Bytes del archivo |
| **Strings** | `Shift+F12` | Cadenas del binario |
| **Imports** | `View → Open subviews → Imports` | Funciones que usa |
| **Exports** | `View → Open subviews → Exports` | Funciones que ofrece |
| **Functions** | `View → Open subviews → Functions` | Lista de funciones detectadas |
| **Names** | `View → Open subviews → Names` | Símbolos y etiquetas |
| **Structures** | `View → Open subviews → Structures` | Tipos y structs |
| **Graph** | `Espacio` sobre una función | Grafo de bloques |

## Ejemplo paso a paso: de una cadena al código

Este es el flujo que vas a repetir siempre. Lo hacemos con el programa de práctica del capítulo 15, que muestra el mensaje "el primer número debe ser menor a ese valor".

**Paso 1. Buscar la cadena.** `Shift+F12` abre la ventana de strings. Con `Ctrl+F` filtrás por texto. También podés usar `View → Open subviews → Strings`.

**Paso 2. Ir a la cadena.** Doble clic sobre ella: IDA te lleva a la sección `.rdata`, donde está almacenada.

**Paso 3. Ver quién la usa.** Con el cursor sobre la cadena, apretá `X` (*cross references*). IDA te muestra las instrucciones que la referencian. Elegí una y te lleva al código.

**Paso 4. Leer el grafo.** Apretá `Espacio` para ver los bloques. Cada bloque es una secuencia de instrucciones sin saltos internos; las flechas verdes/rojas son los caminos. En el capítulo 15, Ricardo pinta los bloques: verde para el camino bueno, salmón para el malo, celeste para el recorrido ({{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_15 Ejercicio 2 - Análisis estático_15 Ejercicio 2 - Análisis estático.txt|Reversing desde cero, cap. 15}}, 00:02:16–00:06:00).

**Paso 5. Renombrar y comentar.** `N` renombra una función, variable o etiqueta; `;` agrega un comentario; `Y` cambia el tipo. Renombrar `var_18` como `primer_valor` hace que todas las referencias se actualicen y el código se vuelva legible.

**Paso 6. Decompilar.** `F5` abre el decompilador (si la versión lo incluye). Te da una vista en C aproximada. No es el código original: es una reconstrucción. Sirve para entender la forma general, no para copiar y pegar.

## Sincronizar IDA con el debugger

Hay dos problemas clásicos:

1. **La base cambia.** IDA muestra la imagen en su `ImageBase` preferida (por ejemplo `0x400000`), pero el debugger la carga en otra dirección por ASLR. En el capítulo 14, IDA muestra `0x401040` y el debugger `0x410040`; la diferencia es la base.
2. **Las direcciones absolutas no coinciden.** Aunque rebasees, un byte puede estar en una sección con otra alineación.

Soluciones:

- **Rebasar IDA** a la base que ves en el debugger: `Edit → Segments → Rebase program`. En el capítulo 14, Ricardo rebasea de `0x400000` a `0x40000` para que coincida con el debugger (00:05:30–00:08:00).
- **Comparar por file offset.** En el debugger, `Ctrl+Shift+G` te da el offset de una instrucción; en IDA, `Jump → Jump to file offset` te lleva al mismo lugar. En el ejemplo, el offset `0x440` coincide en ambos (00:08:00–00:09:00).
- **Desactivar ASLR** en una copia del binario si necesitás direcciones estables (es lo que hace el capítulo 26b para trabajar cómodo). Es una modificación del archivo: hacela sobre una copia, nunca sobre el original.

## Buscar un valor inmediato y las constantes con nombre

A veces no tenés una cadena que te lleve al código, pero sí un número: el identificador de un botón, un código de error, un mensaje de Windows. IDA permite buscarlo.

- **Search → immediate value** (`search for immediate value`) encuentra todas las instrucciones donde aparece ese número. Si el botón "Check" tiene Control ID `0x7D0`, buscás `0x7D0` y IDA te lista cada lugar donde se usa; manteniendo `Shift` podés hacer doble clic para recorrerlos.
- **Constante con nombre** (tecla `M`, *standard symbolic constant*): sobre un número que es en realidad una constante de Windows, `M` te ofrece el nombre simbólico. Un `0x111` se vuelve `WM_COMMAND`; un `0x201`, `WM_LBUTTONDOWN`. Eso hace legible el `switch` que reparte los mensajes de una ventana.
- Si la opción `M` no aparece sobre un `case`, apretá `F5` (decompilador) y probá `M` ahí: suele reconocer la constante igual.

El capítulo 24b hace esto sobre un crackme propio: busca el Control ID con *search immediate value*, llega al `WinProc` y traduce los números de mensaje a `WM_COMMAND` y `WM_LBUTTONDOWN` con las constantes simbólicas ({{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_24b Apéndice teórico 4 - Proximity View_24b Apéndice teórico 4 - Proximity View.txt|Reversing desde cero, cap. 24b}}; transcripción .txt, sin marcas de tiempo).

## Proximity View: ver y buscar caminos entre funciones

El **Proximity View** (menú del grafo, tecla `-` para alejarte) muestra las funciones como un árbol de llamadas en vez de instrucciones. Por defecto muestra dos niveles: lo que la función llama y lo que la llama.

- Los nodos con "corona" son llamadas a la **IAT** (APIs importadas); si una llamada no continúa hacia abajo, es una API que se usa y vuelve (por ejemplo `MessageBox`).
- Doble clic en un nodo lo **centra** y expande dos niveles desde ahí; así seguís solo la rama que te interesa (por ejemplo, de `WinMain` a `WinProc`).
- Clic derecho → *Collapse children / parents* deja una función sola, para no llenar la pantalla.

Lo más útil es **buscar un camino**: con `Add node by name` agregás la función (o variable) destino, y con clic derecho → **Find path** IDA te dibuja la ruta estática que conecta dos funciones, si existe. Sirve cuando el programa es grande y querés saber "¿desde el inicio, cómo se llega hasta la función que muestra *Correcto*?". No siempre hay camino estático (a veces el flujo se arma en tiempo de ejecución), pero cuando lo hay, ahorra horas.

Esto lo muestra el capítulo 24b, que usa *Add node by name* + *Find path* para conectar el inicio del programa con una cadena de la sección de datos, y recomienda activar *use name for addresses* para que el grafo se lea ({{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_24b Apéndice teórico 4 - Proximity View_24b Apéndice teórico 4 - Proximity View.txt|Reversing desde cero, cap. 24b}}).

## Cuando no hay símbolos

Si el binario no trae símbolos, IDA muestra `sub_401000` en vez de `printf`. Peor aún: a veces las DLL están **embebidas** en el `.exe` (compilación estática), así que ni siquiera ves una llamada a una API conocida. Cómo reconocer una función igual:

1. **Por sus argumentos.** Una función con un solo argumento que siempre es una cadena, o con una cadena y después un número, tiene pinta de `printf`. Mirá todas sus referencias: si el patrón de argumentos se repite, confirma la hipótesis.
2. **Siguiendo a una API conocida.** Aunque la DLL esté embebida, `printf` termina llamando a `WriteConsole`. Con el Proximity View podés dejar la función sospechosa sola, agregar `WriteConsoleW` y buscar el camino: si llega, era una envoltura de `printf`.
3. **Confirmando en dinámico.** Si sospechás que una función sin argumentos es `getchar`, ejecutá: si se queda esperando una tecla, era `getchar`.
4. **Con Lumina** (solo IDA con licencia): el servidor compara las funciones con una base y les pone nombre. La versión gratuita o sin licencia no accede al servidor, así que no cuentes con eso.

El capítulo 34 ("Reverseando sin símbolos") usa estas tres primeras técnicas para identificar `printf`, `getchar` y `strcat` en un binario sin símbolos ({{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_34 Reverseando sin símbolos_34 Reverseando sin símbolos.txt|Reversing desde cero, cap. 34}}). El mismo capítulo resuelve además un keygen; esta guía toma solo las técnicas de **identificación de funciones**, no la generación de seriales.

## Reconstruir estructuras y vtables

Cuando una función usa `[reg+offset]` muchas veces sobre la misma base, lo más probable es que esté recorriendo una **estructura**. IDA deja trabajarlas aunque no haya símbolos:

- **Aplicar una estructura a un operando:** parado sobre el offset, apretá `T` (*structure offset*) y elegí la estructura; IDA te dice a qué campo corresponde (por ejemplo, `+0x58` → `F1`). A partir de ahí el listado se lee con nombres en vez de números.
- **Crear una estructura vacía y llenarla:** en la ventana *Structures*, `Insert` crea una estructura; con `D` agregás un campo; con clic derecho → *Array* (sin la tilde *create as array*) la agrandás hasta el tamaño que viste que reserva el programa (por ejemplo, si hace `new` de `0x3C`, creás una de `0x3C`). Después vas nombrando cada campo a medida que descubrís qué guarda (el retorno de `fopen` → `FILE*`, etc.).
- **Padding:** recordá que el tamaño puede incluir relleno por alineación (ver la lección de memoria); no asumas que los campos son contiguos sin huecos.

Para un **objeto de C++**, el primer campo (offset 0) suele ser el puntero a la **vtable**. El cap. 33 arma dos estructuras —una para el objeto y otra para la vtable con los punteros a los métodos virtuales (`suma`, `operator+`, `entrada`, `chequeo`)— y las aplica con `T`. Así, `mov edx, [obj]; call [edx+8]` se lee como "llamar al tercer método virtual".

:::{nota} Las llamadas virtuales no dejan xref directa
Un método virtual se llama a través de la vtable, así que `X` sobre la función solo muestra la referencia **desde la vtable**, no desde el `call`. El cap. 33 resuelve esto agregando una **referencia cruzada manual** (`View → Open subviews → Cross references → Add cross reference`) desde el sitio del `call` hacia el método. Conviene expresarla como **offset** del módulo (`modulo+0x92`) y no como dirección fija, para que ASLR no la rompa. Hecho esto, `X` y el Proximity View ya muestran de dónde viene la llamada.
:::

Dos atajos de navegación que ayudan con listados densos (cap. 20b): con un registro o campo resaltado, `Alt+↓` / `Alt+↑` salta entre sus apariciones; y en una lista de referencias o de strings, **`Shift`+doble clic** te lleva a cada una sin cerrar la ventana.

**Con símbolos es más directo (cap. 23).** Si el binario trae PDB, la estructura ya está definida en *Local Types* (después de sincronizarla con el IDB) y el **constructor** se reconoce por el patrón `Nombre::Nombre`. Aplicás la struct con `T` y cada `[reg+offset]` muestra su campo por nombre. Ojo con un caso frecuente: cuando un campo se pasa como **buffer** a una función (por ejemplo, el destino de `fread`), vas a ver `lea`/dirección `&campo`, no su contenido —es un puntero al campo, no su valor—. Reconocer las APIs por sus argumentos (`fopen` devuelve `FILE*`, `fread(buf,size,count,stream)`, `LoadLibrary`→`HMODULE`, `GetProcAddress(hmod,"printf")`) termina de dar sentido a la estructura ({{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_23 Ejercicio con Estructuras (con símbolos)_23 Ejercicio con Estructuras (con símbolos).txt|Reversing desde cero, cap. 23}}; transcripción .txt, sin marcas).

:::{nota} x64dbg también entiende estructuras
No es exclusivo de IDA. En x64dbg, la pestaña *Struct* permite **importar** una estructura con *parse header* (cargás un `.h` con su definición, bien formateado) y luego *Visit type* con el nombre del tipo y la dirección (por ejemplo, la que apunta a una `SYSTEMTIME` que llenó `GetSystemTime`). Es más áspero que en IDA, pero sirve para leer los campos en vivo mientras traceás (cap. 19).
:::

:::{nota} En el Curso IDA: una serie entera dedicada a estructuras (25–28)
El Curso IDA le dedica cuatro partes seguidas al tema. Lo más útil para practicar: el ejercicio `IDA_STRUCT.7z` (ejecutable `ConsoleApplication4.exe`) **viene con su `.pdb`**, pero el autor propone resolverlo **primero sin símbolos** —borrando o renombrando el `.pdb`— porque "es más complejo, pero es más real", y recién después comparar con los símbolos puestos. Es la mejor forma de ejercitar lo de arriba: armar la estructura a mano con `T`/`D` y nombrar campos, contra tenerla servida en *Local Types* ([Curso IDA · tutes 25–28, Estructuras](../ida_tutes/25.html)).
:::

## Patrones de datos más allá de una estructura

Una estructura sola es el caso fácil. En binarios reales vas a ver **colecciones** de estructuras, y cada una deja un patrón propio en el assembly (**conocimiento externo**, salvo lo citado):

- **Arreglo de estructuras.** El acceso a un elemento tiene la forma `base + índice × tamaño + campo`. Lo vas a ver como `imul rax, rcx, 18h` seguido de `[rbx+rax+8]`, o como un índice escalado `[rbx+rcx*8+10h]`. El multiplicador te da el **tamaño del elemento** y el desplazamiento final, el **campo**. Con eso creás la estructura del tamaño correcto y la aplicás como arreglo.
- **Lista enlazada simple.** Un bucle que hace `mov rbx, [rbx+8]` hasta que `rbx` vale cero: el `+8` es el campo *siguiente*. El resto de los accesos sobre `rbx` dentro del bucle son los campos del nodo.
- **Lista doblemente enlazada de Windows (`LIST_ENTRY`).** Windows usa una estructura con dos punteros, `Flink` (siguiente) y `Blink` (anterior), **embebida** dentro de cada elemento, y listas **circulares** con una cabecera. Dos consecuencias para leerla: el puntero apunta al campo `LIST_ENTRY`, no al comienzo del elemento, así que verás un `sub`/`lea` que **resta** el offset del campo para llegar al inicio (lo que en C hace la macro `CONTAINING_RECORD`); y el recorrido termina cuando se vuelve a la **cabecera**, no cuando aparece un `NULL`. Es la misma forma que tiene la lista de módulos del PEB de [2.14](02-pe-fino.html).
- **Árboles.** Nodos con dos punteros a hijos y una comparación que decide por cuál bajar; los contenedores ordenados de C++ (`std::map`) se ven así ([2.18](02-cpp-profundo.html)).

*(Ejemplo **ilustrativo**: recorrido de una lista circular de Windows en x64.)*

```asm
lea   rdi, [rcx+10h]        ; rdi = &cabecera (LIST_ENTRY dentro de un objeto)
mov   rbx, [rdi]            ; rbx = cabecera.Flink
bucle:
cmp   rbx, rdi              ; ¿volvimos a la cabecera? -> fin (lista circular)
je    fin
lea   rsi, [rbx-20h]        ; inicio del elemento = &entry - offset del campo (CONTAINING_RECORD)
mov   eax, [rsi+8]          ; un campo del elemento
mov   rbx, [rbx]            ; siguiente: entry.Flink
jmp   bucle
fin:
```

Lectura: el campo `LIST_ENTRY` está a `+0x20` dentro de cada elemento (por el `lea rsi, [rbx-20h]`), y el elemento tiene al menos un campo de 4 bytes en `+8`. Con esos dos datos creás la estructura del elemento y la de la cabecera.

## Cadenas: codificaciones y por qué no siempre aparecen

La ventana de strings es la puerta de entrada más rápida, pero solo muestra lo que el programa guarda **tal cual** en el archivo. Conviene saber qué se pierde:

- **ANSI frente a UTF-16.** Las funciones de Windows que manejan texto suelen tener una versión **A** (página de códigos, un byte por carácter) y una **W** (Unicode, en Windows UTF-16, dos bytes). En un volcado hexadecimal, un texto ASCII guardado como UTF-16LE se ve como `H.o.l.a.` con ceros intercalados. Si la búsqueda de cadenas está configurada solo para C/ANSI, esas cadenas **no aparecen**: en IDA se agregan los tipos Unicode desde la configuración de la ventana de strings; Ghidra los incluye en *Defined Strings*. Que el programa llame a `CreateFileW` en vez de `CreateFileA` ya te dice qué codificación buscar.
- **Cadenas con longitud.** Algunos lenguajes guardan cadenas como puntero + longitud, sin el `0` final (Go, Rust y otros; ver [2.13](02-huella-compilador.html)). El buscador de cadenas las puede mostrar pegadas unas con otras o cortadas.
- **Cadenas armadas en el stack.** El programa escribe el texto de a pedazos con instrucciones `mov` de inmediatos imprimibles (`mov dword ptr [rsp+20h], 6C6C6548h` = `"Hell"` en little-endian). No hay ninguna cadena en `.rdata`; la pista es una ráfaga de `mov` con constantes que, leídas como bytes, son caracteres.
- **Cadenas cifradas.** Se guardan transformadas y una rutina las descifra justo antes de usarlas (un bucle con `xor` es lo más simple; ver [2.10](02-ofuscacion.html)). Se recuperan siguiendo la rutina, ejecutando hasta después de que descifre o con herramientas que extraen cadenas armadas en el stack y decodificadas (por ejemplo, FLOSS de Mandiant, externa al curso).

Regla práctica: si un programa claramente muestra textos al usuario y la ventana de strings está casi vacía, alguna de estas cuatro situaciones está pasando, y eso ya es un dato del análisis.

## Estrategias de lectura

No leas una función de arriba a abajo sin plan. Algunas tácticas que funcionan:

1. **Empezá por las strings.** En programas con interfaz, los mensajes ("acceso denegado", "ingrese la clave") te llevan directo a la lógica.
2. **Buscá las APIs conocidas.** `GetWindowTextA`, `strcmp`, `MessageBoxA`, `CreateFileA` son pistas. En Imports tenés la lista.
3. **Seguí las referencias.** `X` sobre una función te dice desde dónde se llama. A veces el `main` es el nodo con más referencias.
4. **Nombrá mientras leés.** Un binario sin símbolos se vuelve legible cuando renombrás `sub_401000` como `check_password` y `var_8` como `largo`.
5. **Anotá las hipótesis.** Escribí "si el primer valor es <= 50, sigue por acá" y verificalo en el debugger.

El capítulo 15 usa exactamente este método: busca la cadena, llega al código, identifica el `printf`/`scanf`, renombra las variables, deduce las condiciones y las confirma ejecutando (00:06:00–00:19:00).

:::{nota} En el Curso IDA: el mismo método, dicho por Ricardo
El Curso IDA plantea este enfoque desde el arranque: cuando todavía no tenés práctica con el análisis estático, **comentá y renombrá lo poco que vas entendiendo** y resolvé el resto en el debugger; con práctica vas necesitando el debugger cada vez menos, hasta reversear casi sin ejecutar. Y algo clave para no agobiarte: **no se reversea el programa entero**, sino la o las funciones de la zona que necesitás para tu objetivo ([Curso IDA · tute 3, El loader](../ida_tutes/3.html) y [tute 8, Trabajar en el loader](../ida_tutes/8.html)).
:::

## IDA Free, Ghidra y alternativas

| Herramienta | Fortalezas | Límites |
|---|---|---|
| **IDA Free** | La misma base de IDA; buena para empezar | Menos procesadores, decompilador limitado, sin plugins de pago |
| **IDA Pro** | Estándar de la industria; decompilador maduro | Licencia cara |
| **Ghidra** | Gratis y open source; decompilador integrado; scripting en Java/Python | Interfaz más pesada; consume más recursos |
| **Binary Ninja** | Interfaz moderna; buena API | De pago |
| **radare2 / Cutter** | Gratis, scriptable, multiplataforma | Curva de aprendizaje alta |
| **x64dbg** | Debugger, no desensamblador estático | No reemplaza a IDA para análisis estático |

Para este curso, **IDA Free o Ghidra** son suficientes. El capítulo 14 recomienda IDA Free si no se tiene Pro; esta guía agrega Ghidra como alternativa gratuita y activa.

:::{peligro} Una recomendación del audio y del documento que no se copia
En el capítulo 14, el autor sugiere buscar una copia "por internet" de IDA Pro si no se puede pagar (00:01:00–00:02:00). El documento de `descargas_sueltas` va más lejos: indica buscar "IDA PRO 6.8 + HEXRAYS" en Google y usar la contraseña de `install_pass.txt`. Esta guía **no** reproduce esas instrucciones ni distribuye claves. Usá IDA Free, Ghidra o una licencia educativa.
:::

## Práctica

1. Abrí tu `check.exe` en IDA Free o Ghidra.
2. Buscá la cadena "Correcto" con `Shift+F12`, llegá al código con `X` y leé el grafo.
3. Renombrá la función `main` si no está nombrada, y las variables de los dos números.
4. Agregá comentarios en las dos comparaciones.
5. Si tu versión tiene decompilador, compará la vista `F5` con el assembly. Marcá tres diferencias.
6. Rebaseá IDA a la base que muestra x64dbg y comprobá que una dirección coincide. Si no coincide, usá el file offset.
7. Escribí en tu bitácora: qué string usaste, qué xref elegiste, qué función renombraste y qué hipótesis confirmaste.
8. Agregá a tu programa un mensaje con `MessageBoxW` y otro armado carácter por carácter en un arreglo local. Comprobá cuál aparece en la ventana de strings con la configuración por defecto, cuál solo al activar Unicode y cuál no aparece nunca.
9. Agregá un arreglo de estructuras y recorrelo en un bucle. En el listado, identificá el tamaño del elemento por el multiplicador y creá la estructura correspondiente.

## Preguntas de repaso

**1. ¿Cuál es la diferencia principal entre IDA y x64dbg?**
IDA es un desensamblador estático: analiza el archivo sin ejecutarlo. x64dbg es un debugger: ejecuta el programa y muestra su estado.

**2. ¿Para qué sirve `X` sobre una cadena?**
Para ver las referencias cruzadas: las instrucciones que usan esa cadena. Es el camino más rápido de la cadena al código.

**3. ¿Qué hace `N`?**
Renombra un símbolo (función, variable, etiqueta). Todas las referencias se actualizan.

**4. ¿Por qué las direcciones de IDA y del debugger no coinciden?**
Porque ASLR carga la imagen en una base distinta de la preferida. Se soluciona rebaseando o comparando por file offset.

**5. ¿El decompilador devuelve el código original?**
No. Reconstruye una aproximación en C a partir del assembly. Sirve para entender, no para copiar.

**6. ¿Qué mirada conviene primero, la estática o la dinámica?**
Depende. Para un programa con interfaz y strings claras, la estática orienta rápido. Para confirmar un valor concreto, la dinámica es más directa. Lo habitual es alternar.

**7. El programa muestra mensajes pero la ventana de strings está casi vacía. ¿Qué cuatro causas revisás?**
Cadenas UTF-16 no incluidas en la búsqueda, cadenas con longitud sin `0` final, cadenas armadas en el stack con `mov` de inmediatos y cadenas cifradas que se descifran en ejecución.

**8. Ves `[rbx+rcx*8+10h]` dentro de un bucle. ¿Qué te dice?**
Que probablemente es un arreglo de elementos de 8 bytes indexado por `rcx`, y que `+10h` es el desplazamiento del arreglo o de un campo respecto de la base.

**9. ¿Por qué en una lista `LIST_ENTRY` de Windows ves una resta antes de leer los campos?**
Porque el puntero apunta al campo `LIST_ENTRY` embebido, no al inicio del elemento; la resta del offset del campo recupera el inicio (lo que hace `CONTAINING_RECORD`).

## Antes de avanzar

Tenés que poder:

- Abrir un binario, buscar una cadena y llegar al código que la usa.
- Leer un grafo y distinguir el camino bueno del malo.
- Renombrar y comentar para que el listado se entienda.
- Sincronizar IDA con el debugger por rebase o por offset.
- Explicar por qué no usás una copia ilegal de IDA.
- Reconocer cadenas UTF-16, armadas en el stack o cifradas, y saber por qué no aparecen en la ventana de strings.
- Reconocer un arreglo de estructuras, una lista enlazada y una lista `LIST_ENTRY` por su patrón en el assembly.

:::{nota} Puerta de salida de la Etapa 2
Si podés analizar tu propio programa de punta a punta —estático y dinámico— y escribir un informe con las direcciones y los valores observados, terminaste la introducción al reversing. La Etapa 3 es una victoria rápida con .NET.
:::

## Fuentes de esta lección

- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_14 Conociendo IDA_14 Conociendo IDA.txt|Reversing desde cero, cap. 14}} — interfaz de IDA, rebase, file offset, símbolos, limitaciones de IDA Free.
- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_15 Ejercicio 2 - Análisis estático_15 Ejercicio 2 - Análisis estático.txt|Reversing desde cero, cap. 15}} — strings, xrefs, grafo, renombrado, decompilación y verificación dinámica.
- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_24b Apéndice teórico 4 - Proximity View_24b Apéndice teórico 4 - Proximity View.txt|Reversing desde cero, cap. 24b}} — Proximity View, Find Path, search immediate value, constantes simbólicas (`WM_*`) y decompilador para confirmar un `case`.
- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_34 Reverseando sin símbolos_34 Reverseando sin símbolos.txt|Reversing desde cero, cap. 34}} — identificar funciones sin símbolos por argumentos, por el camino a una API conocida y confirmando en dinámico (se omite la parte de keygen).
- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_20b Apéndice teórico 3 - Estructuras_20b Apéndice teórico 3 - Estructuras.txt|Reversing desde cero, cap. 20b}} — aplicar y reconstruir estructuras con `T`, y navegación con `Alt+↑/↓` y `Shift`+doble clic.
- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_33 C++ Clases_33 C++ Clases.txt|Reversing desde cero, cap. 33}} — objeto con vtable, reconstruir las dos estructuras y agregar cross-references manuales para las llamadas virtuales (se omite la parte de keygen).
- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_23 Ejercicio con Estructuras (con símbolos)_23 Ejercicio con Estructuras (con símbolos).txt|Reversing desde cero, cap. 23}} — estructura con símbolos, constructor `Nombre::Nombre`, `&campo` como buffer y reconocer `fopen`/`fread`/`LoadLibrary`/`GetProcAddress` (se omite la parte de keygen).
- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_19 Ejercicio 64 bits_19 Ejercicio 64 bits.txt|Reversing desde cero, cap. 19}} — importar y visitar estructuras (`SYSTEMTIME`) en x64dbg con parse header / visit type.
- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Videos y material adicional Ingenieria Inversa/Videos_Video33_Video33.txt|Videos y material adicional, Video 33}} — mapa de memoria y secciones como primer paso del análisis.
- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Videos y material adicional Ingenieria Inversa/Videos_Video39_Video39.txt|Videos y material adicional, Video 39}} — ExeInfoPE y detección de código nativo/empaquetado.
- [Curso IDA desde cero · 69 tutes ilustrados](../ida_tutes/1.html) — texto y 3.278 capturas extraídos e indexados por tema (índice en [ida-tutes](../ida-tutes.html)); el método de lectura estática —comentar, renombrar y reversear solo lo necesario— es de los tutes 3 y 8.
- [Curso IDA · tutes 25–28, Estructuras](../ida_tutes/25.html) — serie dedicada a estructuras en IDA; el ejercicio `IDA_STRUCT`/`ConsoleApplication4.exe` se resuelve primero sin símbolos (lo más real) y después con el `.pdb`.
- {{src:descargas_sueltas/INTRODUCCIÓN AL REVERSING CON IDA PRO DESDE CERO.docx|Introducción al reversing con IDA Pro desde cero (docx, 2016)}} — tutorial escrito de la parte 1: IDA vs OllyDbg, PE32/PE32+, proximity view, strings, imports, hex dump.
- Microsoft Learn (conocimiento externo): [Unicode in the Windows API](https://learn.microsoft.com/en-us/windows/win32/intl/unicode-in-the-windows-api), [Working with Strings](https://learn.microsoft.com/en-us/windows/win32/learnwin32/working-with-strings), [LIST_ENTRY](https://learn.microsoft.com/en-us/windows/win32/api/ntdef/ns-ntdef-list_entry), [Singly and doubly linked lists](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/singly-and-doubly-linked-lists). Herramienta externa: [FLOSS](https://github.com/mandiant/flare-floss).

:::{nota} Capas de esta lección
**Contenido observado en CLS:** el recorrido del capítulo 14, el ejemplo de `0x440`, las técnicas del capítulo 15 y la advertencia sobre IDA Free. **Conocimiento externo:** comparación con Ghidra y otras herramientas, atajos actuales, patrones de colecciones de datos (arreglos, listas, `LIST_ENTRY`, árboles) y codificaciones y formas de ocultar cadenas. **Ejemplo ilustrativo:** el recorrido de una lista circular. **Recomendación editorial:** la estrategia de lectura y el límite legal sobre copias de IDA Pro.
:::

