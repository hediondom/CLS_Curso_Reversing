---
title: "2D.11 · Excepciones de Windows y debugging"
description: "Leer SEH x86, unwind x64 y metadatos .pdata/.xdata; seguir el despacho de una excepción (depurador, VEH, handlers por marco, segunda oportunidad) y depurar una excepción controlada en un programa propio."
etapa: "Etapa 2 · 2D · Windows internals (optativa)"
---

# Excepciones de Windows y debugging

:::{aviso} Rama optativa 2D
La práctica usa una excepción esperada en un programa propio. No busca provocar corrupción ni explotar un fallo.
:::

:::{nota} Propósito
Entender cómo el depurador reconstruye el stack y cómo Windows transfiere el control cuando una función falla, distinguiendo el modelo histórico x86 del unwind x64. Al terminar deberías poder explicar **quién** vio una excepción, **en qué orden** y **por qué** una excepción de primera oportunidad no significa que el programa haya fallado.
:::

**Prerrequisitos**

- *Obligatorios:* stack y llamadas ([1.2](01-memoria.html), [2.5](02-llamadas.html)); [2D.2 memoria/loader](2d-02-memoria-loader.html).
- *Recomendados:* WinDbg/TTD ([2.19](02-windbg-heap.html)); C++ profundo ([2.18](02-cpp-profundo.html)); taxonomía anti-análisis ([2.15](02-anti-analisis.html)).

## Modelos

En x86, SEH usa registros/estructuras de excepción y el runtime del compilador puede agregar handlers de lenguaje; los detalles dependen del compilador y de mitigaciones como SafeSEH/SEHOP. En x64, el unwinder consulta metadatos de funciones: `.pdata` indexa entradas `RUNTIME_FUNCTION` y `.xdata` describe cómo deshacer prólogos y recuperar registros; algunas funciones hoja no requieren entrada.

WinDbg puede mostrar el evento de excepción, contexto y stack. En TTD, una traza de user mode permite avanzar o retroceder por esa ejecución, pero no reemplaza símbolos, documentación ni comprensión del estado. La salida cambia con arquitectura, build y símbolos disponibles.

## Qué guarda el sistema cuando ocurre una excepción

Cuando el procesador o el software genera una excepción, Windows guarda dos estructuras:

- el **registro de contexto** (`CONTEXT`): el estado de la máquina del hilo en ese momento, dependiente de la arquitectura;
- el **registro de excepción** (`EXCEPTION_RECORD`): el **código** de excepción, si es **continuable**, un puntero a otro registro (excepciones anidadas), la **dirección** donde ocurrió y un arreglo de **parámetros** adicionales.

Para el análisis, el par contexto + registro es la evidencia primaria: la dirección y el código dicen qué pasó; el contexto dice con qué registros. En WinDbg, `.exr` muestra un registro de excepción y `.ecxr` cambia el contexto al de la excepción guardada, para que `k` muestre el stack **de ese momento** y no el del depurador.

## Orden de despacho en user mode

Microsoft documenta este orden para buscar quién maneja una excepción de user mode:

1. **Depurador, primera oportunidad.** Si el proceso está siendo depurado, el sistema notifica al depurador.
2. **Vectored exception handlers (VEH).** Se registran con `AddVectoredExceptionHandler`, no dependen del marco de llamada, se aplican a todo el proceso y se llaman en el orden en que se agregaron, **después** de la primera oportunidad del depurador y **antes** de que comience el desenrollado.
3. **Handlers basados en marcos.** El sistema recorre los marcos del hilo desde el actual hacia atrás: en x86, la cadena SEH; en x64, la información de `.pdata`/`.xdata`. Aquí entran `__try/__except` y los handlers de lenguaje como el de C++.
4. **Depurador, segunda oportunidad.** Si nadie la manejó y hay depurador, se lo notifica de nuevo.
5. **Manejo por defecto.** Sin depurador o si este no la maneja, el sistema aplica la acción por defecto, que para la mayoría de las excepciones es terminar el proceso.

En kernel mode el sistema busca handlers en la pila del kernel; si no hay ninguno, el sistema se detiene (bugcheck, ver [6.3](6-03-debug-kernel.html)).

Un filtro de `__try/__except` decide con su valor de retorno si el bloque maneja la excepción, si se sigue buscando o si se continúa la ejecución. Cuando un handler acepta la excepción, el sistema **desenrolla** los marcos intermedios y ejecuta los bloques `__finally`/destructores que correspondan antes de llegar al handler.

## Primera y segunda oportunidad en el depurador

Para WinDbg, cada tipo de excepción tiene un **estado de corte**: cortar en la primera oportunidad (`sxe`), cortar solo en la segunda (`sxd`), solo informar (`sxn`) o ignorar (`sxi`). Por defecto, por ejemplo, una violación de acceso corta en la primera oportunidad, mientras que la excepción de C++ (`eh`) corta solo en la segunda. `.lastevent` muestra el último evento.

Consecuencias para leer evidencia:

- Una **excepción de primera oportunidad** es normal en muchos programas: excepciones C++ lanzadas y atrapadas, sondeos de memoria protegidos por `__try`, mecanismos de runtime. **No** significa un fallo.
- Una **segunda oportunidad** sí significa que nadie la manejó.
- Un **VEH** registrado por el programa ve todas las excepciones del proceso. Si al analizar un binario encontrás `AddVectoredExceptionHandler`, anotá qué hace el handler: puede ser diagnóstico legítimo (registro de fallos) o una técnica anti-depuración que usa excepciones a propósito (2.15). La llamada sola no decide cuál.

En binarios MSVC, las excepciones de C++ se lanzan como una excepción de Windows con un código propio del runtime (habitualmente `0xE06D7363`, conocimiento externo de reversing); reconocerlo evita confundir un `throw` controlado con un fallo.

## Ejemplo trabajado

*(Secuencia ilustrativa de un programa C++ propio que lanza y captura una excepción documentada.)*

```text
app!RunCase -> app!ParseOwnInput -> throw/catch controlado
WinDbg: evento de excepción -> handler del runtime -> app!RunCase
x64: .pdata señala RuntimeFunction; .xdata describe unwind del prólogo
```

Al recorrer el stack, identificá qué frames son la ruta de llamada y cuál maneja el evento. La mera presencia de `.pdata` no demuestra que una excepción haya ocurrido; es metadata disponible para unwind.

Cronología de lectura (ilustrativa) del mismo caso, en el orden en que aparece cada dato:

| Paso | Qué se ve | Herramienta | Interpretación prudente |
|---|---|---|---|
| 1 | Evento de primera oportunidad, código de excepción C++ | Mensaje de WinDbg / `.lastevent` | Se lanzó una excepción; todavía no se sabe si alguien la maneja |
| 2 | Registro de excepción con dirección dentro del runtime | `.exr -1` | El `throw` pasa por el runtime de C++ |
| 3 | Stack de la excepción hasta `app!ParseOwnInput` | `.ecxr` + `k` | Ruta de llamada al momento del `throw` |
| 4 | El programa continúa y no hay segunda oportunidad | Ejecución | Un `catch` la manejó |
| 5 | Ejecución reanudada en `app!RunCase` | Breakpoint en el `catch` | Coincide con el handler esperado |

## Práctica

1. Compilá o usá un programa propio mínimo que lance/capture una excepción prevista, sin leer datos externos.
2. En WinDbg, anotá arquitectura, evento, excepción y `k`/`kv` antes y después del handler. Usá `.exr -1` y `.ecxr` para leer el registro y el contexto de la excepción.
3. Cambiá **solo para tu sesión** el estado de corte de la excepción C++ (`sxe eh`) para verla en primera oportunidad, y comparalo con el comportamiento por defecto.
4. En x64, inspeccioná la entrada de función/unwind con símbolos y comandos documentados para tu build; en x86, describe el frame SEH observado sin modificar la cadena.
5. Opcional: agregá a tu programa un VEH que solo registre el código de excepción y verificá en qué momento se llama respecto del depurador y del `catch`.
6. Opcional: grabá el mismo caso de user mode con TTD y navega a la excepción. Guardá el trace solo mientras lo necesites y borrá la copia al finalizar.

## Entregable

Diagrama de control antes/después de la excepción, arquitectura, stack, handler y límites de símbolos; la cronología con primera/segunda oportunidad y, si lo hiciste, el momento en que actúa el VEH. Separá información observada de interpretación del compilador.

## Repaso

?? ¿Qué función cumplen `.pdata` y `.xdata` en x64?
!! `.pdata` localiza metadata de funciones; `.xdata` describe información de unwind/handlers necesaria para recuperar estado y recorrer el stack.

?? ¿x86 SEH y x64 unwind son el mismo mecanismo?
!! No. Tienen representación y reglas distintas; el compilador y las mitigaciones también afectan lo observable.

?? ¿Un frame de stack prueba que esa función lanzó la excepción?
!! No. Es una pista del camino actual; se confirma con instrucción, contexto y flujo de control.

?? ¿En qué orden se buscan handlers en user mode?
!! Depurador (primera oportunidad), handlers vectorizados, handlers basados en marcos, depurador (segunda oportunidad) y manejo por defecto.

?? ¿Una excepción de primera oportunidad indica que el programa falló?
!! No. Muchas se lanzan y se manejan normalmente; solo la segunda oportunidad indica que nadie la manejó.

?? ¿Para qué sirve `.ecxr`?
!! Pone el contexto del depurador en el registro de contexto de la excepción, para que el stack corresponda al momento del fallo.

?? Encontrás `AddVectoredExceptionHandler` en un binario. ¿Qué concluís?
!! Que el programa ve todas las excepciones del proceso antes que los handlers por marco. Hay que leer qué hace el handler: puede ser diagnóstico o anti-depuración.

:::{nota} Puerta optativa
Podés describir una excepción propia en WinDbg, leer registro y contexto, explicar el orden de despacho (incluidos VEH y primera/segunda oportunidad), leer el stack y explicar la diferencia general entre SEH x86 y unwind x64.
:::

:::{nota} Lo que queda fuera
El formato completo de `UNWIND_INFO`, los manejadores de lenguaje en detalle, SafeSEH/SEHOP y CFG por dentro, WER y la depuración post mortem configurada en el sistema no se desarrollan. No se cambia ninguna configuración global de depuración.
:::

## Fuentes

- Microsoft Learn: [x64 exception handling](https://learn.microsoft.com/en-us/cpp/build/exception-handling-x64), [Structured Exception Handling](https://learn.microsoft.com/en-us/windows/win32/debug/structured-exception-handling), [Debugging a user-mode process using WinDbg](https://learn.microsoft.com/en-us/windows-hardware/drivers/debugger/debugging-a-user-mode-process-using-windbg).
- Microsoft Learn, despacho y depurador: [Exception Dispatching](https://learn.microsoft.com/en-us/windows/win32/debug/exception-dispatching), [Vectored Exception Handling](https://learn.microsoft.com/en-us/windows/win32/debug/vectored-exception-handling), [try-except statement](https://learn.microsoft.com/en-us/cpp/cpp/try-except-statement), [Controlling Exceptions and Events](https://learn.microsoft.com/en-us/windows-hardware/drivers/debugger/controlling-exceptions-and-events), [.exr](https://learn.microsoft.com/en-us/windows-hardware/drivers/debuggercmds/-exr--display-exception-record-), [.ecxr](https://learn.microsoft.com/en-us/windows-hardware/drivers/debuggercmds/-ecxr--display-exception-context-record-).
- **CLS:** stack en [1.2](01-memoria.html), unwind C++ en [2.18](02-cpp-profundo.html), WinDbg en [2.19](02-windbg-heap.html), anti-análisis en [2.15](02-anti-analisis.html).

:::{nota} Etiquetas
**Observado en CLS:** excepciones y stack como conceptos generales. **Conocimiento externo:** SEH/unwind, despacho de excepciones, VEH y control de excepciones en WinDbg; el código de excepción C++ de MSVC como dato de reversing. **Ejemplo ilustrativo:** flujo y cronología de excepción. **Laboratorio verificado:** no.
:::
