---
title: "2.31 · Extensiones de Ghidra y SLEIGH"
description: "Escribir scripts y plugins de Ghidra (Jython, PyGhidra, Java), correr el analizador headless, usar P-Code y entender SLEIGH para modelar arquitecturas o bytecode propio."
etapa: "Etapa 2 · Desofuscación avanzada (2E)"
---

# Extensiones de Ghidra y SLEIGH

:::{nota} Objetivo de la lección
Automatizar Ghidra con **scripts** (descifrar strings, renombrar, resolver imports) y entender **P-Code** y **SLEIGH** lo suficiente para leer el IR y, si hace falta, **modelar un bytecode propio** (el de tu mini-VM de 2.26). **Prerrequisitos:** Ghidra/Cutter ([2.16](02-ghidra.html)) y C++ profundo ([2.18](02-cpp-profundo.html)).
:::

Ampliación de [2.16](02-ghidra.html): ahí recorriste Ghidra «a mano»; acá lo **programás**.

## Por qué extender Ghidra

Dos motivos (**conocimiento externo**): **automatizar** lo repetitivo (descifrar cientos de strings, renombrar por patrón, anotar structs) y **enseñarle algo que no sabe** (una arquitectura rara, un bytecode a medida). Lo primero son *scripts*; lo segundo es **SLEIGH**.

## Scripts: Jython, PyGhidra y Java

- **Jython (Python 2):** el scripting histórico, integrado en el *Script Manager*. Cómodo para tareas rápidas; el lenguaje es viejo.
- **PyGhidra (Python 3):** desde **Ghidra 11+** viene integrado y es el **estándar actual**: corre CPython 3 real contra la API, así que podés usar librerías de Python 3 dentro del script (`z3-solver` para resolver una condición, `requests`, `capstone`…). En versiones previas se lograba lo mismo con Ghidrathon. Jython queda para scripts viejos.
- **Java (GhidraScript):** la API nativa, la más completa y la de los *plugins*/analizadores.

Las piezas de la API que más vas a tocar: `FlatProgramAPI` (`getInstructionAt`, `getBytes`, `createFunction`, `setEOLComment`, `getSymbolAt`) y la interfaz de decompilado `DecompInterface` (pedir el C decompilado de una función desde el script).

## Headless: Ghidra sin interfaz

Para procesar muchos binarios o integrar en CI, `analyzeHeadless` corre el análisis y tus scripts **sin GUI**:

```text
analyzeHeadless C:\proyectos miProyecto ^
  -import .\muestra_propia.exe ^
  -postScript descifrar_strings.py ^
  -scriptPath .\scripts
```

## P-Code: el IR de Ghidra

Ghidra no razona sobre x86 directamente: traduce cada instrucción a **P-Code**, un lenguaje intermedio de operaciones chiquitas (`COPY`, `INT_ADD`, `LOAD`, `STORE`, `CBRANCH`…). Hay dos niveles: **raw** (crudo, 1 instrucción → varias ops) y **refined/high** (tras el análisis, el que alimenta el decompilador). Trabajar sobre P-Code te da análisis de flujo de datos **independiente de la arquitectura**: el mismo script sirve para x86 y para ARM.

## SLEIGH: enseñarle una arquitectura (o tu bytecode)

**SLEIGH** es el lenguaje con que Ghidra describe un procesador: un `.slaspec` (cómo se decodifican los bytes y qué P-Code produce cada instrucción), más `.pspec`/`.cspec`/`.ldefs` (registros, convención de llamada, variantes). Modelar una instrucción es decir tres cosas: **qué bits** la identifican, **cómo se muestra** (el *display*) y **qué hace** (su semántica en P-Code). Esto es lo que te deja **liftear el bytecode de tu mini-VM** (2.26) y que Ghidra lo decompile como si fuera código normal.

```text
# fragmento SLEIGH (ESQUEMÁTICO) para el OP_XOR de la mini-VM de 2.26
# opcode de 8 bits + inmediato de 8 bits; 'acc' es un registro virtual
define token instr (16) op=(8,15) imm=(0,7);
:XOR imm is op=0x02 & imm { acc = acc ^ imm; }     # semántica = P-Code
:ADD imm is op=0x03 & imm { acc = acc + imm; }
```

## Ejemplo paso a paso: descifrar strings con un script

*(Ejemplo **ilustrativo**: script Jython sobre un binario propio; Window → Script Manager.)*

```python
# descifrar_strings.py (Jython) — XOR 0x5A y dejar el claro como comentario
addr = toAddr(0x00403020)
n = 16
data = getBytes(addr, n)                      # byte[] (con signo)
claro = "".join(chr((b & 0xff) ^ 0x5A) for b in data)
setEOLComment(addr, "desc: " + claro)         # queda anotado en el listado
print("descifrado:", claro)
```

Qué hiciste: leíste 16 bytes, los pasaste por `XOR 0x5A` y dejaste el texto claro **anotado en el propio listado**, de forma reproducible. Escalado a un bucle sobre todas las referencias a la rutina de descifrado, resolvés cientos de strings en segundos —lo que a mano sería una tarde—.

## Práctica

En tu VM, sobre binarios **propios**:

1. Compilá un binario que guarde sus strings con `XOR 0x5A` y escribí un script Ghidra que las descifre y comente todas.
2. Corré ese mismo script en modo **headless** sobre dos binarios de una.
3. Pedí con `DecompInterface` el C decompilado de una función y guardalo a archivo.
4. Escribí (esquemático) las líneas SLEIGH de dos opcodes más de tu mini-VM (2.26) y explicá qué P-Code generarían.

## Preguntas de repaso

?? ¿Cuándo escribís un script y cuándo tocás SLEIGH?
!! **Script** para automatizar sobre una arquitectura que Ghidra **ya entiende** (descifrar, renombrar, anotar). **SLEIGH** cuando hay que **enseñarle una arquitectura o un bytecode nuevo** que no trae.

?? ¿Qué es P-Code y por qué conviene razonar sobre él?
!! Es el **IR** de Ghidra: cada instrucción se traduce a operaciones chicas (`INT_ADD`, `LOAD`…). Razonar sobre P-Code es **independiente de la arquitectura**: el mismo análisis vale para x86 y ARM.

?? ¿Qué tres cosas define una instrucción en SLEIGH?
!! **Qué bits** la identifican (el patrón del token), **cómo se muestra** (el display/mnemónico) y **qué hace** (su semántica expresada en P-Code).

?? ¿Para qué sirve `analyzeHeadless`?
!! Para correr el análisis y tus scripts **sin la GUI**: procesar lotes de binarios, integrar en CI o automatizar pipelines de triage.

?? ¿Cómo se conecta esta lección con la VM de 2.26?
!! Con SLEIGH podés **modelar el bytecode de tu mini-VM** para que Ghidra lo desensamble y decompile como código normal: es la vía de *lifting* para devirtualizar lo que vos mismo virtualizaste.

:::{nota} Puerta de salida
Podés: (1) escribir un script de Ghidra (Jython/PyGhidra) que descifre y anote; (2) correrlo en headless; (3) explicar qué es P-Code y sus niveles; (4) describir cómo SLEIGH modela una instrucción y para qué liftearías tu bytecode propio.
:::

## Fuentes de esta lección

- [ghidra.re · API (FlatProgramAPI, DecompInterface)](https://ghidra.re/ghidra_docs/api/) — scripting en Java/Jython (conocimiento externo).
- [SLEIGH language docs](https://htmlpreview.github.io/?https://github.com/NationalSecurityAgency/ghidra/blob/master/GhidraDocs/languages/html/sleigh.html) — tokens, display y semántica P-Code.
- [github.com/mandiant/Ghidrathon](https://github.com/mandiant/Ghidrathon) — Python 3 en Ghidra (alternativa a Jython).
- [2.16 Ghidra/Cutter](02-ghidra.html) (recorrido a mano) y [2.26 VM](02-ofuscacion-vm.html) (el bytecode que se liftea).

:::{nota} Capas de esta lección
**Núcleo conceptual:** el recorrido de Ghidra de 2.16 como base. **Conocimiento externo (agregado por esta edición):** la API de scripting, headless, P-Code y SLEIGH. **Recomendación editorial:** los ejemplos (incluida la línea SLEIGH, marcada como esquemática) y la práctica son ilustrativos.
:::
