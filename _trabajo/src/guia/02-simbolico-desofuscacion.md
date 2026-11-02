---
title: "2.25 · Ejecución simbólica y concólica: desofuscar con un solver"
description: "Usar ejecución simbólica y concólica (angr, Triton, Miasm, Z3) para recuperar condiciones y resolver ramas en binarios propios ofuscados, y entender por qué a veces no escala."
etapa: "Etapa 2 · Desofuscación avanzada (2E)"
---

# Ejecución simbólica y concólica: desofuscar con un solver

:::{nota} Objetivo de la lección
Entender qué es la **ejecución simbólica** y la **concólica**, y usarlas para recuperar las condiciones de un binario propio ofuscado (qué entrada lo lleva a una rama) y para **simplificar** expresiones enredadas. Saber **cuándo no sirve** y por qué. **Prerrequisitos:** fundamentos de simbólico ([2.24](02-opt-fuzzing.html)), ofuscación nativa ([2.10](02-ofuscacion.html)), instrucciones ([2.2](02-instrucciones.html)) y scripting ([2.21](02-scripting-debugger.html)). *Contexto recomendado:* método de análisis (4.1).
:::

Esto es **análisis**, no evasión: se usa el solver sobre **binarios propios o crackmes didácticos** para entender su lógica. No se producen cracks, keygens ni parches de software comercial.

## Qué es la ejecución simbólica

En la ejecución **concreta** (la de siempre), una variable tiene un valor: `eax = 0x41`. En la **simbólica**, la variable es una *incógnita* —la llamamos `x`— y el motor va anotando, instrucción por instrucción, **qué operaciones se le hicieron**. Cuando el programa llega a un salto condicional, en vez de tomar un camino, el motor guarda la **restricción** (*path constraint*) que haría cierto ese salto y puede explorar **los dos lados** (**conocimiento externo**).

Al final, cada camino es una lista de restricciones del estilo «`(x ^ 0x23) + 7 == 0x62`». Esa lista se le entrega a un **solver SMT** (típicamente **Z3**), que responde una de dos cosas: *insatisfacible* (ninguna entrada llega acá) o *satisfacible* y, de paso, **un valor concreto de `x`** que cumple. Ese valor es, muchas veces, la «clave» que buscabas: en vez de leer y revertir el algoritmo a mano, le preguntás al solver qué entrada produce el resultado.

## Por qué «concólica» (concrete + symbolic)

El simbólico puro se ahoga cuando el programa llama al sistema operativo, lee un archivo o depende del entorno: no todo se puede dejar como incógnita. La **ejecución concólica** mezcla las dos: mantiene simbólico **lo que te interesa** (la entrada del usuario) y **concretiza** el resto (una syscall devuelve un valor fijo, una librería se reemplaza por un modelo). Así el árbol de caminos no explota por cosas que no te importan. En la práctica, casi siempre vas a trabajar en modo concólico.

## Los tres motores que vas a encontrar

| Motor | Cómo trabaja | Cuándo elegirlo |
|---|---|---|
| **angr** (Python) | Levanta el binario a VEX IR y emula con estados simbólicos; `SimulationManager` gestiona los caminos | El más completo para «encontrá la entrada que llega acá»; mucho ejemplo de crackmes |
| **Triton** (C++/Python) | Construye el AST simbólico de cada instrucción x86/x64 y lo resuelve con Z3; se engancha a una traza | Cuando ya tenés una *traza* concreta y querés razonar sobre ella (ideal junto a DBI, 2.29) |
| **Miasm** (Python) | IR propio, ensambla/desensambla, emula y hace simbólico; buen *lifting* | Reconstrucción de flujo y desofuscación de rutinas puntuales |

Los tres apoyan abajo en un solver: **Z3** (de Microsoft Research) es el más usado. No hace falta escribir Z3 a mano para empezar —angr lo maneja por vos—, pero conviene entender que ahí abajo hay un demostrador de teoremas sobre *bitvectors*.

## El enemigo: explosión de caminos

Cada salto condicional **duplica** la cantidad de estados a seguir. Un bucle que corre 32 veces con una rama adentro son `2³²` caminos: inmanejable. La ofuscación **empeora** esto a propósito —el **aplanamiento de flujo** ([2.10](02-ofuscacion.html)) convierte un programa lineal en un *switch* gigante, y los **predicados opacos** agregan ramas falsas—. Mitigaciones:

- **Exploración dirigida:** decile al motor *adónde* querés llegar (`find=`) y *qué* evitar (`avoid=`), para que no explore todo.
- **Concretizar:** fijá la longitud de la entrada, modelá las syscalls, saltá funciones de librería con *SimProcedures*.
- **Veritesting / fusión de estados:** angr puede unir caminos equivalentes para no multiplicarlos.
- **Límites:** cota de pasos, de memoria y de tiempo; si no cierra, cambiá de técnica (trazá con DBI, 2.29, y pasale la traza a Triton).

## Simplificar expresiones y MBA

Una técnica de ofuscación frecuente es el **MBA** (*mixed boolean-arithmetic*): reemplazar `x + y` por una maraña equivalente de `and`, `or`, `xor` y sumas. El solver sirve para **probar que dos expresiones son iguales** y así deshacer la maraña. La identidad clásica:

```python
# Z3: demostrar que una expresión MBA es, en realidad, una suma
from z3 import BitVec, prove
x, y = BitVec("x", 32), BitVec("y", 32)
prove((x ^ y) + 2 * (x & y) == x + y)   # imprime: proved
```

Si `prove` dice *proved*, esa expresión complicada era `x + y` disfrazada. Lo mismo sirve para confirmar que un chequeo enrevesado equivale a un simple `cmp`.

## Ejemplo paso a paso: resolver un crackme propio con angr

*(Ejemplo **ilustrativo**: código de referencia sobre un binario propio; no es un volcado de una corrida verificada en esta edición.)*

Como el curso es **solo Windows**, no entramos por `stdin` ni leemos la salida con `posix.dumps` (eso es de binarios ELF/Linux; en un PE de MSVC devuelve vacío y `simgr.found` queda siempre `[]`). Arrancamos **directo en la función de validación** con `blank_state`, ponemos la entrada en memoria y dirigimos la búsqueda por **direcciones de bloque** (el que devuelve «correcto» vs. el que devuelve «incorrecto»):

```python
# resolver.py — crackme PROPIO, PE de Windows x64.
# Entra directo en validar(const char *clave), sin pasar por el CRT.
import angr, claripy

proj = angr.Project("./crackme_propio.exe", auto_load_libs=False)

ADDR_VALIDAR = 0x140001000   # prólogo de validar()
ADDR_EXITO   = 0x140001085   # bloque que devuelve 1 (Correcto)
ADDR_FALLO   = 0x140001090   # bloque que devuelve 0 (Incorrecto)
BUF_ADDR     = 0x140050000   # memoria escribible donde alojar la clave

clave = claripy.BVS("clave", 16 * 8)
estado = proj.factory.blank_state(addr=ADDR_VALIDAR)

# escribir el bitvector en memoria y apuntar RCX (1.er arg en Windows x64) al buffer
estado.memory.store(BUF_ADDR, clave)
estado.regs.rcx = BUF_ADDR

# 15 bytes ASCII imprimible + terminador nulo
for b in clave.chop(8)[:-1]:
    estado.solver.add(b >= 0x20, b <= 0x7e)
estado.solver.add(clave.chop(8)[-1] == 0x00)

simgr = proj.factory.simulation_manager(estado)
simgr.explore(find=ADDR_EXITO, avoid=ADDR_FALLO)

if simgr.found:
    s = simgr.found[0]
    print("clave:", s.solver.eval(clave, cast_to=bytes).rstrip(b"\x00").decode())
```

Qué hizo: arrancó el estado **en el prólogo de `validar()`** (con `blank_state`, no en el *entry point*, para no modelar el CRT), puso 16 bytes simbólicos en una dirección escribible y apuntó `RCX` ahí (primer argumento en la ABI de Windows x64), y dirigió la búsqueda a la **dirección** del bloque «correcto» evitando la del «incorrecto» (esas direcciones las sacás en IDA/Ghidra). Si **no** encuentra nada o tarda infinito, la lección está en el *porqué*: explosión de caminos, un bucle sin cota, o una comprobación que depende de algo que no modelaste.

:::{aviso} En Windows: no modeles el CRT, entrá por la función de validación
Alimentar la entrada por `stdin` en un `.exe` de MSVC arrastra a angr por el runtime de C (`ReadFile`, buffers de `conio`…) y dispara *timeouts* o explosión de caminos que no te interesan. Dos salidas: (1) pasá la entrada por `sys.argv[1]` en vez de stdin; (2) la del ejemplo de arriba —`blank_state(addr=…)` en el prólogo de la validación (no `entry_state`, que es para el *entry point*), con la entrada en memoria y `RCX` apuntándola—. Y nunca guíes `find`/`avoid` con `posix.dumps(1)`/`stdin`: eso lee el descriptor POSIX de Linux; en un PE de Windows la salida va por `WriteFile`/`ucrtbase`, así que dirigí por **direcciones de bloque**.
:::

## Práctica

En tu VM, con un **crackme propio** (compilá uno en C con una comprobación aritmética sobre la entrada):

1. Escribí la comprobación a propósito como una cuenta (p. ej. `(entrada[i] ^ 0x5A) + i == tabla[i]`) y compilalo.
2. Resolvelo con angr usando `find`/`avoid`; verificá que la clave que da el solver es aceptada por el programa real.
3. Agregá un bucle grande o una rama extra y observá cómo cambia el tiempo: explicá qué pasó con los caminos.
4. Tomá una línea con MBA (usá la identidad de arriba) y demostrá con Z3 a qué operación simple equivale.

## Preguntas de repaso

?? ¿Qué le pedís en el fondo a un solver SMT?
!! Que decida si un conjunto de restricciones sobre *bitvectors* es **satisfacible** y, si lo es, que te dé **un valor concreto** de las incógnitas que las cumple. Ese valor suele ser la entrada que buscabas.

?? ¿Por qué casi siempre se trabaja en modo concólico y no simbólico puro?
!! Porque dejar **todo** simbólico (syscalls, entorno, librerías) hace explotar el árbol de caminos. El concólico mantiene simbólica solo la entrada de interés y **concretiza** el resto, acotando el problema.

?? ¿Cómo empeora la ofuscación la ejecución simbólica?
!! El **aplanamiento de flujo** multiplica las ramas (un *switch* gigante) y los **predicados opacos** agregan caminos falsos. Más ramas = más estados = explosión de caminos. Por eso se usa exploración dirigida, fusión de estados y límites.

?? ¿Para qué sirve `prove` de Z3 frente a un MBA?
!! Para **demostrar que la expresión enrevesada es igual** a una operación simple (p. ej. que `(x^y)+2*(x&y)` es `x+y`). Así deshacés la maraña con una garantía matemática, no por inspección a ojo.

?? El motor no encuentra solución ni termina. ¿Qué revisás?
!! Si hay un **bucle sin cota**, si falta **concretizar** algo (longitud de entrada, una syscall), si conviene **dirigir** con `find`/`avoid`, o si el binario está virtualizado (2.26) y hay que trazarlo con DBI (2.29) antes.

:::{nota} Puerta de salida
Podés: (1) explicar qué es un estado simbólico y un *path constraint*; (2) resolver un crackme propio con angr dirigiendo la búsqueda; (3) nombrar dos causas de explosión de caminos y sus mitigaciones; (4) demostrar con Z3 que un MBA equivale a una operación simple.
:::

## Fuentes de esta lección

- [docs.angr.io](https://docs.angr.io/) — `SimulationManager`, `explore(find=, avoid=)`, *SimProcedures*, veritesting (conocimiento externo, documentación primaria).
- [triton-library.github.io](https://triton-library.github.io/) — AST simbólico por instrucción y resolución con Z3.
- [github.com/cea-sec/miasm](https://github.com/cea-sec/miasm) — IR, emulación y simbólico.
- [github.com/Z3Prover/z3](https://github.com/Z3Prover/z3) — el solver SMT; API de Python para *bitvectors*.
- [2.24 Fuzzing y simbólico](02-opt-fuzzing.html) — la introducción sobre la que se apoya esta lección.

:::{nota} Capas de esta lección
**Núcleo conceptual:** la ofuscación y el aplanamiento de flujo de los capítulos 26/30 (vistos en 2.10), como el problema que motiva el solver. **Conocimiento externo (agregado por esta edición):** ejecución simbólica/concólica, angr/Triton/Miasm/Z3, explosión de caminos y MBA. **Recomendación editorial:** los ejemplos y la práctica son ilustrativos; no hay laboratorio compilado con hashes en esta edición.
:::
