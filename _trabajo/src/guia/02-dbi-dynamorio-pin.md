---
title: "2.29 · Instrumentación binaria dinámica: DynamoRIO y Pin"
description: "Escribir herramientas de DBI (Pin, DynamoRIO) que cuentan instrucciones, miden cobertura y detectan código auto-modificado para desempaquetado genérico, y cómo se integran con la cobertura y el fuzzing."
etapa: "Etapa 2 · Desofuscación avanzada (2E)"
---

# Instrumentación binaria dinámica: DynamoRIO y Pin

:::{nota} Objetivo de la lección
Entender qué es la **DBI** (instrumentación binaria dinámica) y usarla para **contar instrucciones**, **medir cobertura** y **detectar código auto-modificado** (desempaquetado genérico), sobre binarios propios. **Prerrequisitos:** scripting de debugger ([2.21](02-scripting-debugger.html)) y packers didácticos ([2.17](02-packers.html)).
:::

Esto es **análisis dinámico instrumentado** sobre programas propios o crackmes. El malware, si se instrumenta, va en **VM descartable** ([4.4](04-dinamico-seguro.html)).

## Qué es la DBI

Una herramienta de DBI (**conocimiento externo**) toma el proceso mientras corre, **re-compila su código en bloques** (JIT) justo antes de ejecutarlos e **inserta tu código** en los puntos que elijas: antes de cada instrucción, al entrar a una función, cuando se escribe memoria. A diferencia de un debugger (que para en breakpoints), la DBI observa **todo** a escala de instrucción y es **mucho más rápida**, porque no hay *trap* por instrucción. El precio: tu código corre dentro del mismo proceso, así que hay que cuidar la *transparencia* (no alterar el comportamiento observado).

## Los dos frameworks

| Framework | Cómo se programa | Herramientas que ya trae |
|---|---|---|
| **Intel Pin** | *pintools* en C++; registrás *callbacks* por instrucción, *trace*, rutina o imagen (`INS_AddInstrumentFunction`, `TRACE_`, `IMG_`) | Ejemplos: `inscount`, `pinatrace`, `itrace` |
| **DynamoRIO** | *clients* en C; API de eventos (`dr_register_bb_event`) | **`drcov`** (cobertura), **`drltrace`** (llamadas a librería), `drcachesim` |

Para empezar no hace falta escribir un *client*: `drcov` y `drltrace` de DynamoRIO resuelven el 80% de los casos de reversing sin compilar nada.

## Para qué sirve en reversing

- **Cobertura:** qué bloques se ejecutaron con una entrada dada. Se vuelca con `drcov` y se colorea en IDA/Ghidra/Binary Ninja con **Lighthouse**: ves «por dónde pasó» el programa.
- **Fuzzing dirigido:** esa misma cobertura es la señal que usan los fuzzers ([2.24](02-opt-fuzzing.html)) para saber si una entrada llegó a código nuevo.
- **Desempaquetado genérico:** un packer **escribe** una página y luego **ejecuta** desde ella. Una herramienta DBI que marca las páginas escritas y avisa cuando se ejecuta una de ellas encuentra el **OEP** sin conocer el packer (regla W⊕X).
- **Conteo y perfil:** cuántas instrucciones corre una rutina (útil para hallar la función «cara», p. ej. la de descifrado).

:::{nota} Cobertura ≠ traza: elegí según el objetivo
Son dos niveles de detalle distintos. La **cobertura** (`drcov`) registra *qué bloques básicos* se ejecutaron —basta para colorear en Lighthouse y comparar caminos, y es barata—. La **traza de instrucciones** registra *cada instrucción con los valores de los registros* (p. ej. `pinatrace` de Pin, o `drcachesim`/`drtrace` de DynamoRIO): es mucho más pesada, pero es la que necesitás para **reconstruir un algoritmo** —seguir cómo se transforma un dato paso a paso, como una rutina de descifrado—. Regla: para «¿por dónde pasó?» usá cobertura; para «¿qué le hizo al dato?» usá traza.
:::

## Ejemplo paso a paso: cobertura con drcov y OEP por W⊕X

*(Ejemplo **ilustrativo**: comandos típicos sobre un binario propio; no un volcado verificado.)*

```text
# 1) cobertura de un binario PROPIO con DynamoRIO (no hay que compilar nada)
drrun -t drcov -- .\crackme_propio.exe entrada1
#   -> genera  drcov.crackme_propio.exe.<pid>.0000.proc.log
#   abrilo en Lighthouse (IDA/Ghidra) para colorear los bloques ejecutados

# 2) contar instrucciones con un pintool de ejemplo de Intel Pin
pin -t inscount0.dll -- .\crackme_propio.exe
#   -> Count 1234567   (cuántas instrucciones corrió)
```

```text
// idea de un client/pintool de "unpacking genérico" (resumen conceptual)
//  - marcar cada página donde el programa ESCRIBE
//  - en cada bloque a ejecutar, si su página fue escrita antes -> candidato a OEP
on_memory_write(addr):      paginas_escritas.add(page_of(addr))
on_basic_block(bb):         if page_of(bb) in paginas_escritas:
                                print("posible OEP:", bb); dump_module()
```

La cobertura de `drcov` + Lighthouse te muestra **qué caminos tomó** cada entrada (comparás dos corridas y ves la rama que cambió). El esquema W⊕X encuentra el OEP de un UPX propio **sin** saber que era UPX: es el mismo OEP que en 2.17 buscabas a mano, ahora detectado por la regla «se ejecutó una página que antes se escribió».

## Práctica

En tu VM, con binarios **propios**:

1. Sacá la cobertura con `drcov` de tu crackme para dos entradas distintas y coloreala en Lighthouse; identificá la rama que separa «bien» de «mal».
2. Contá las instrucciones con un pintool de ejemplo (`inscount`) y encontrá la rutina que más ejecuta (candidata a descifrado/bucle).
3. Sobre tu «hola mundo» empaquetado con UPX (de 2.17), explicá cómo la regla W⊕X marcaría el OEP.
4. Escribí dos diferencias prácticas entre instrumentar con DBI y depurar con breakpoints.

## Preguntas de repaso

?? ¿En qué se diferencia la DBI de un debugger?
!! La DBI **re-compila el código (JIT) e inserta tu código** en cada punto de interés, observando a escala de instrucción y **mucho más rápido** (sin *trap* por instrucción). El debugger para en breakpoints puntuales.

?? ¿Qué herramienta de DynamoRIO usás para cobertura y con qué la visualizás?
!! **`drcov`** genera el archivo de cobertura; **Lighthouse** lo colorea sobre IDA/Ghidra/Binary Ninja para ver qué bloques se ejecutaron.

?? ¿Cómo encuentra la DBI un OEP sin conocer el packer?
!! Con la regla **W⊕X**: marca las páginas donde el programa **escribe** y avisa cuando se **ejecuta** una de ellas. Ese salto a código recién escrito es el candidato a OEP, sea cual sea el packer.

?? ¿Qué relación hay entre cobertura y fuzzing?
!! La cobertura (qué bloques nuevos tocó una entrada) es la **señal** que guía al fuzzer (2.24): si una entrada llega a código nuevo, vale la pena mutarla. La DBI puede proveer esa cobertura.

?? ¿Por qué importa la «transparencia» en DBI?
!! Porque tu código corre **dentro del mismo proceso**: si altera tiempos, memoria o APIs observables, el binario puede comportarse distinto (o detectarte). Hay que medir sin cambiar lo que se mide.

:::{nota} Puerta de salida
Podés: (1) explicar qué hace la DBI y en qué se diferencia de un debugger; (2) sacar cobertura con `drcov` y leerla en Lighthouse; (3) contar instrucciones con un pintool; (4) describir el desempaquetado genérico por W⊕X.
:::

## Fuentes de esta lección

- [Intel Pin · Pin User Guide](https://software.intel.com/sites/landingpage/pintool/docs/) — `INS_AddInstrumentFunction`, granularidades y pintools de ejemplo (conocimiento externo).
- [dynamorio.org](https://dynamorio.org/) — API de clients y herramientas `drcov`/`drltrace`/`drcachesim`.
- [github.com/gaasedelen/lighthouse](https://github.com/gaasedelen/lighthouse) — visualizar cobertura en IDA/Ghidra/Binary Ninja.
- [2.17 Packers](02-packers.html) (OEP a mano) y [2.24 Fuzzing](02-opt-fuzzing.html) (la cobertura como señal).

:::{nota} Capas de esta lección
**Núcleo conceptual:** el OEP/dump de 2.17 como problema que la DBI automatiza. **Conocimiento externo (agregado por esta edición):** Pin, DynamoRIO, `drcov`/Lighthouse y la regla W⊕X. **Recomendación editorial:** ejemplos y práctica ilustrativos, sobre binarios propios.
:::
