---
title: "2.21 · Scripting de debugger: automatizar y dejar evidencia"
description: "Automatizar tareas repetidas en x64dbg (breakpoints, logs, trazas condicionales) y guardar evidencia; instrumentación dinámica con Frida; OllyDbg/OllyScript como legado a reconocer y adaptar."
etapa: "Etapa 2 · Windows avanzado (2C)"
---

# Scripting de debugger: automatizar y dejar evidencia

:::{nota} Objetivo de la lección
Dejar de repetir a mano la misma secuencia en el debugger: **automatizarla con un script** de x64dbg y que ese script **guarde evidencia** reproducible. Reconocer y adaptar un **OllyScript** antiguo. **Prerrequisitos:** debugger (2.6). *Contexto recomendado (no bloqueante):* método de análisis (4.1) y automatización con IDAPython (5.3) — útiles como referencia, pero 2C no exige haber hecho las etapas 4 o 5.
:::

## Por qué scriptear el debugger

Cuando una tarea se repite —poner el mismo breakpoint, leer el mismo registro, anotar el mismo valor en cada corrida— conviene **automatizarla**: es más rápido, no te equivocás y queda **reproducible** (cualquiera corre el script y obtiene lo mismo). Es el mismo espíritu que viste con **IDAPython** en la [automatización de la Etapa 5](05-automatizacion.html), pero del lado **dinámico**: en vez de recorrer el binario estático, manejás la ejecución.

## x64dbg: el lenguaje de scripts

x64dbg trae una pestaña **Script** con un lenguaje de comandos simple (**conocimiento externo**). Los que más vas a usar:

| Comando | Qué hace |
|---|---|
| `bp dir` / `bphws dir, "r"` | breakpoint de software / de hardware |
| `SetBreakpointLog dir, "..."` | texto que se escribe al log cuando se dispara ese bp |
| `SetBreakpointCondition dir, 0` | *break-condition* 0 = el bp **loggea pero no pausa** |
| `run` / `erun` | correr hasta el bp / correr pasando excepciones |
| `log "texto {reg}"` | escribir en el log (con formato de registros/memoria) |
| `$resultado = [rsp+8]` | variables del script, leer memoria |

El formato de `log` permite volcar memoria y registros: `{utf16@rcx}` imprime el string Unicode **cuya dirección está en `RCX`**. Ojo con los corchetes: `@rcx` usa el **valor del registro** como dirección; `@[rcx]` haría una **lectura de más** (tomaría lo que hay *en* `RCX` como dirección). Con un breakpoint que **loggea sin pausar** armás una **traza** automática.

## Ejemplo paso a paso: loggear cada archivo que abre el programa

*(Ejemplo **ilustrativo**: script de x64dbg para registrar llamadas y guardar evidencia.)*

```text
// script.txt — correr desde la pestaña Script de x64dbg
bp CreateFileW                                            // breakpoint en la API
SetBreakpointLog CreateFileW, "[CreateFileW] {utf16@rcx}" // qué loggear al dispararse
SetBreakpointCondition CreateFileW, 0                     // 0 = loggea pero NO pausa
run                                                       // una sola vez; todo queda en el log

// el log queda con algo como:
// [CreateFileW] C:\Users\...\config.ini
// [CreateFileW] C:\Users\...\datos.bin
```

Cada vez que el programa llama a `CreateFileW`, el breakpoint **loggea el nombre del archivo** (el primer argumento, en `RCX`) y **continúa solo**, porque la *break-condition* es 0. Esa es la forma recomendada: no metas `run` dentro de un comando de breakpoint (x64dbg lo desaconseja por inestable); dejá que el bp loggee y no pause. Al final copiás el **log** como evidencia (Etapa 4): un registro reproducible de qué archivos tocó, sin frenar a mano en cada llamada.

## Trazas condicionales: registrar cada instrucción que cumple algo

Un breakpoint con log te dice **cuándo** se llamó a algo. A veces la pregunta es otra: "¿por qué camino pasó entre este punto y aquel?" o "¿en qué instrucción `RAX` tomó este valor?". Para eso x64dbg tiene **trazas condicionales** (menú *Debug*: *Trace into until condition* / *Trace over until condition*): el debugger ejecuta paso a paso por vos y en cada instrucción evalúa expresiones (**conocimiento externo**, documentación de x64dbg):

| Campo | Qué hace | Valor por defecto |
|---|---|---|
| *Break condition* | Si da 1, la traza se detiene | `0` (no se detiene por condición) |
| *Log text* | Texto con formato que se escribe al log | vacío |
| *Log condition* | Si da 1, se escribe el *log text* | `1` (siempre) |
| *Command text* / *condition* | Comando que se ejecuta cuando la condición da 1 | la condición por defecto es la *break condition* |

El log de la traza se puede mandar a un archivo (desde el diálogo o con el comando `TraceSetLogFile`), y ese archivo es la evidencia.

*(Ejemplo **ilustrativo**, no ejecutado en esta edición: valores de los campos para una traza "trace over" desde el inicio de una función de verificación.)*

```text
Break condition:  cip == 0x140001290        // fin de la función: ahí se detiene
Log text:         {p:cip} {i:cip}  rax={rax}
Log condition:    1                         // loggear todas las instrucciones
```

El resultado es la lista de instrucciones **realmente ejecutadas**, con el valor de `RAX` en cada una. Comparar dos trazas (una con entrada válida y otra con inválida) muestra exactamente **dónde se separan los caminos**, que es el dato que buscabas en el método de la Etapa 4. Dos precauciones: una traza paso a paso es **mucho más lenta** que la ejecución normal, así que acotala entre dos direcciones y usá *trace over* para no meterte en las APIs; y el archivo crece rápido, así que logueá solo lo que vas a leer.

## Instrumentación dinámica: Frida

Un debugger detiene el proceso (o lo traza instrucción por instrucción). La **instrumentación dinámica** hace otra cosa: **inyecta código propio** en el proceso para que se ejecute al entrar y salir de las funciones que te interesan, sin pausar. **Frida** es la herramienta libre más difundida de este tipo (**conocimiento externo**): inyecta un motor de JavaScript en el proceso y te da una API para enganchar funciones.

La pieza central es `Interceptor.attach(target, callbacks)`: `target` es la dirección de la función y `callbacks` tiene `onEnter(args)`, que recibe los argumentos, y `onLeave(retval)`, que recibe el valor de retorno. La dirección de una función exportada se obtiene con `Process.getModuleByName(nombre).getExportByName(funcion)`.

*(Ejemplo **ilustrativo**, no ejecutado en esta edición: el mismo registro de `CreateFileW` del ejemplo de x64dbg, ahora con Frida.)*

```js
// agente.js: registrar qué archivos abre el programa y qué handle recibe
const f = Process.getModuleByName('kernel32.dll').getExportByName('CreateFileW');
Interceptor.attach(f, {
  onEnter(args) {
    this.nombre = args[0].readUtf16String();   // primer argumento: LPCWSTR
  },
  onLeave(retval) {
    console.log('[CreateFileW] ' + this.nombre + ' -> ' + retval);
  }
});
```

Se carga con la herramienta de línea de comandos de Frida al lanzar **tu programa** dentro de la VM. Comparado con el script de x64dbg, ganás el valor de retorno en la misma línea (`this` guarda datos entre `onEnter` y `onLeave`) y la posibilidad de procesar los datos en JavaScript; perdés la vista de registros y memoria que da el debugger.

| Herramienta | Cuándo conviene | Costo |
|---|---|---|
| Breakpoint con log (x64dbg) | Saber cuándo y con qué argumentos se llama a algo | Bajo; pausa interna en cada disparo |
| Traza condicional (x64dbg) | Ver el camino exacto entre dos puntos | Muy lento; acotarlo |
| Instrumentación (Frida) | Registrar entradas y salidas de muchas funciones, procesar datos al vuelo | Inyecta código: modifica el proceso |
| TTD ([2.19](02-windbg-heap.html)) | Grabar una ejecución y recorrerla hacia atrás | Archivos grandes; solo WinDbg |

:::{aviso} Instrumentar modifica el proceso
Frida inyecta una biblioteca y reescribe el inicio de las funciones enganchadas. Usala solo sobre **programas propios o didácticos, en la VM**. Un programa con controles anti-análisis ([2.15](02-anti-analisis.html)) puede notar la inyección y comportarse distinto, y eso es un dato para documentar, no algo para evadir. No la uses sobre software de terceros, juegos en línea ni procesos protegidos del sistema.
:::

## OllyDbg como legado

**OllyDbg** (el de los videos 23–40 del curso, ver [2.9 Herramientas](02-herramientas.html)) tiene su propio **OllyScript** (`.txt` con comandos como `bp`, `run`, `log`, `cmp`, `jne`). Es de 32 bits y está discontinuado, pero vas a **encontrar scripts viejos** de OllyScript en material de la escena. El objetivo acá no es escribir OllyScript nuevo, sino **reconocer** qué hace uno antiguo y, si hace falta, **adaptar** su lógica a x64dbg. En `Teorias_Numeradas` hay varios títulos sobre scripting de OllyDbg/x64dbg (material por título, no revisado; ver [índice](../teorias.html)).

## Práctica

En tu VM, con un **crackme propio o didáctico** (ver [Banco de prácticas](../practicas.html)):

1. Elegí una tarea repetitiva (p. ej. loggear cada `strcmp`/`CreateFileW`, o leer un registro en un punto).
2. Escribí un script de x64dbg que la haga sola y escriba al **log**.
3. Corré el script y **guardá el log** como evidencia.
4. Tomá un OllyScript viejo (si conseguís uno) y escribí en dos líneas qué hace y cómo se traduciría a x64dbg.
5. Sobre tu crackme propio, hacé una traza condicional *trace over* de la función de verificación con una entrada válida y otra inválida, mandando el log a archivo. Compará los dos archivos y señalá la primera instrucción donde se separan.
6. Si instalás Frida en la VM, registrá con un agente las llamadas a `CreateFileW` (o a la comparación de cadenas) de tu programa propio y compará la salida con la del script de x64dbg.

## Preguntas de repaso

?? ¿Por qué scriptear una tarea del debugger en vez de hacerla a mano?
!! Porque es más rápido, evita errores de repetición y queda **reproducible**: el script documenta exactamente qué se hizo y cualquiera obtiene el mismo resultado.

?? ¿Cómo hacés que un breakpoint loggee sin pausar la ejecución?
!! Le ponés un **texto de log** (`SetBreakpointLog`) y la **break-condition en 0** (`SetBreakpointCondition dir, 0`): el bp escribe al log cada vez que se dispara y continúa solo. Es lo recomendado; meter `run` dentro de un comando de breakpoint es inestable.

?? ¿Cómo loggeás el nombre de archivo en una llamada a `CreateFileW`?
!! Con el formato de memoria del log: el primer argumento (`RCX` en x64) tiene la **dirección** del nombre; `{utf16@rcx}` vuelca ese string Unicode al log. (Con `@[rcx]` harías una lectura de más.)

?? ¿Qué te da una traza condicional que no te da un breakpoint con log?
!! El **camino completo** de instrucciones ejecutadas entre dos puntos, con los valores que pidas en cada una. Comparando dos trazas ves dónde se separan los caminos. A cambio es muy lenta, por eso se acota.

?? En Frida, ¿para qué sirven `onEnter` y `onLeave`?
!! `onEnter(args)` corre al entrar a la función y recibe los argumentos; `onLeave(retval)` corre al salir y recibe el valor de retorno. Con `this` se guardan datos de la entrada para usarlos a la salida.

?? ¿Por qué instrumentar con Frida no es "solo mirar"?
!! Porque inyecta una biblioteca y modifica el inicio de las funciones enganchadas: el proceso cambia y un programa con controles anti-análisis puede notarlo. Por eso se usa sobre programas propios en la VM y se documenta.

?? ¿Qué relación tiene esto con IDAPython (5.3)?
!! Es la misma idea de **automatizar**, pero en dinámico: IDAPython recorre el binario estático; el script de x64dbg maneja la **ejecución** (breakpoints, registros, memoria en vivo).

?? ¿Qué hacés con un OllyScript antiguo?
!! Lo **reconocés y adaptás**: entendés su lógica (bp, run, comparaciones) y la traducís a x64dbg. No conviene escribir OllyScript nuevo (OllyDbg está discontinuado y es de 32 bits).

:::{nota} Puerta de salida
Podés: (1) escribir un script de x64dbg que automatice una tarea y escriba al log; (2) hacer que un breakpoint loggee sin pausar (log + break-condition 0); (3) guardar el log como evidencia reproducible; (4) reconocer un OllyScript y explicar cómo adaptarlo; (5) acotar una traza condicional y comparar dos trazas; (6) explicar qué hace un agente de Frida con `Interceptor.attach` y qué cambia en el proceso. **Con esto cerrás el núcleo del bloque 2C.**
:::

:::{nota} Lo que queda fuera
*Stalker* (el trazador de Frida) y la reescritura de funciones con `Interceptor.replace`, los marcos de instrumentación binaria como DynamoRIO o Intel Pin y el uso de Frida en Android o iOS. La lección enseña a registrar evidencia sin cambiar la lógica del programa.
:::

## Fuentes de esta lección

- [Automatización con IDAPython](05-automatizacion.html) (5.3) — el paralelo estático del scripting; misma idea de automatizar y reproducir.
- [Herramientas](02-herramientas.html) (2.9) — OllyDbg en su contexto histórico (videos 23–40).
- [Teorias_Numeradas](../teorias.html) — títulos sobre scripting de x64dbg/OllyDbg (material por título, no revisado).
- x64dbg (conocimiento externo): [Conditional Breakpoint](https://help.x64dbg.com/en/latest/introduction/ConditionalBreakpoint.html) y [Conditional Tracing](https://help.x64dbg.com/en/latest/introduction/ConditionalTracing.html) — campos de condición, log y comando; `TraceSetLogFile`.
- Frida (conocimiento externo): [documentación](https://frida.re/docs/home/) y [JavaScript API](https://frida.re/docs/javascript-api/) — `Interceptor.attach`, `onEnter`/`onLeave`, `Process.getModuleByName`, `getExportByName`, `readUtf16String`.

:::{nota} Capas de esta lección
**Contenido observado en CLS:** OllyDbg en los videos del curso y la automatización con IDAPython de la Etapa 5; títulos de scripting en `Teorias_Numeradas`. **Conocimiento externo:** el lenguaje de scripts de x64dbg (`SetBreakpointLog`, `SetBreakpointCondition`, `log`, formatos de memoria), las trazas condicionales, Frida y OllyScript. **Recomendación editorial:** los ejemplos ilustrativos (script, campos de traza, agente de Frida; ninguno ejecutado en esta edición), la tabla de herramientas y la práctica de guardar evidencia (sin laboratorio compilado con hashes en esta edición).
:::
