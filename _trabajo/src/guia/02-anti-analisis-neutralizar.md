---
title: "2.28 · Neutralizar anti-análisis en laboratorio: del reconocimiento a poder analizar"
description: "Aplicar contramedidas controladas (parches, ScyllaHide, hooks de Frida) sobre binarios propios o malware en VM descartable para poder analizar, entendiendo que neutralizar un chequeo puede disparar el payload."
etapa: "Etapa 2 · Desofuscación avanzada (2E)"
---

# Neutralizar anti-análisis en laboratorio

:::{nota} Objetivo de la lección
Pasar de **reconocer** un chequeo anti-análisis (lo que viste en 2.15) a **neutralizarlo de forma controlada** para poder analizar: parches, plugins de ocultación y *hooks*, sobre **binarios propios** o malware en **VM descartable**. **Prerrequisitos:** taxonomía anti-análisis ([2.15](02-anti-analisis.html)), scripting de debugger ([2.21](02-scripting-debugger.html)), debugger ([2.6](02-debugger.html)) y el laboratorio de [malware dinámico defensivo (2.22)](02-opt-malware-dinamico.html).
:::

:::{peligro} Riesgo: neutralizar un chequeo puede ejecutar el payload
Muchos binarios maliciosos **esconden su comportamiento detrás del anti-análisis**: si hacés que crean que nadie los observa, **corren su carga real**. Hacé esto solo en una **VM descartable con snapshot**, sin red o con red controlada, tal como se define en [4.4 Dinámico seguro](04-dinamico-seguro.html). Para **aprender la técnica**, usá binarios propios con chequeos que escribís vos.
:::

## Por qué, a veces, hay que neutralizar

En 2.15 aprendiste a **detectar** que un binario se defiende. Pero para analizarlo en dinámico a veces necesitás que **no aborte**: un programa que llama a `IsDebuggerPresent` y sale si estás enganchado no se deja estudiar bajo debugger. Neutralizar el chequeo —hacer que devuelva «no hay debugger»— te deja seguir. La regla de oro: **neutralizás para observar, no para romper protecciones de software ajeno**.

## Chequeos y su contramedida

| Chequeo (2.15) | Dónde mira | Contramedida en lab |
|---|---|---|
| `IsDebuggerPresent` | PEB `BeingDebugged` (byte en PEB+2) | Hook que devuelve 0; o poner a 0 el byte del PEB |
| `CheckRemoteDebuggerPresent` / `NtQueryInformationProcess(ProcessDebugPort)` | *debug port* del proceso | Forzar el resultado a «sin debugger» (ScyllaHide) |
| `NtGlobalFlag` / *heap* `ForceFlags` | Flags que cambian bajo debugger | Normalizar los flags al valor «sin debugger» |
| Tiempos (`rdtsc`, `QueryPerformanceCounter`, `GetTickCount`) | Mide cuánto tardó entre dos puntos | Acortar el delta (hook que devuelve tiempos cercanos) |
| Anti-VM (`cpuid` bit de hipervisor, artefactos) | Detecta que corre en VM | Ocultar artefactos de la VM; parchear el chequeo |
| *Hardware breakpoints* (DR0–DR3) | Lee el contexto de depuración | Usar bp de software; limpiar DRx vía hook |

:::{aviso} Un VEH que lee DR0–DR3 te delata al poner un breakpoint de hardware
En x64, un truco frecuente es registrar un *vectored exception handler* (`AddVectoredExceptionHandler`) que, ante cualquier excepción, inspecciona `ContextRecord->Dr0..Dr3`: si alguno es distinto de cero, hay un breakpoint de hardware y el binario aborta. Un bp de hardware tuyo en x64dbg cae en la trampa. Para neutralizarlo en lab: enganchá `NtGetContextThread` (o el VEH registrado) con Frida y **forzá `Dr0..Dr3 = 0`** en el `CONTEXT` antes de que el código los evalúe. Alternativa: usá solo breakpoints de software en ese tramo.
:::

## Herramientas

- **ScyllaHide / TitanHide:** plugins (de x64dbg el primero; driver el segundo) que **ocultan el debugger** interceptando las APIs y estructuras de arriba. Es el camino rápido para «hacer invisible» el debugger sin parchear a mano.
- **Frida:** *hooks* en runtime para reemplazar el valor que devuelve una API concreta (fino y reproducible).
- **Parche estático** en x64dbg: cuando el chequeo está en el propio binario propio (p. ej. forzar el salto), con *Patch* → *Apply patches*. Igual que en 2.10, **no a ciegas**.

## Ejemplo paso a paso: neutralizar tres chequeos propios con Frida

*(Ejemplo **ilustrativo**: script sobre un binario propio con chequeos que escribiste vos, en VM.)*

```javascript
// ocultar.js — en VM, sobre binario PROPIO. frida -f .\propio.exe -l ocultar.js
const k32 = Process.getModuleByName('kernel32.dll');
const ntdll = Process.getModuleByName('ntdll.dll');

// 1) IsDebuggerPresent -> siempre 0
Interceptor.replace(
  k32.getExportByName('IsDebuggerPresent'),
  new NativeCallback(() => 0, 'int', []));

// 2) limpiar PEB.BeingDebugged (+0x02) y PEB.NtGlobalFlag (+0xBC en x64 / +0x68 en x86).
//    En Frida no hay un objeto 'gs'; se obtiene el PEB llamando a ntdll!RtlGetCurrentPeb.
const RtlGetCurrentPeb = new NativeFunction(
  ntdll.getExportByName('RtlGetCurrentPeb'), 'pointer', []);
const peb = RtlGetCurrentPeb();
peb.add(0x02).writeU8(0);                                   // BeingDebugged = 0
const offNtGlobalFlag = (Process.pointerSize === 8) ? 0xBC : 0x68;
peb.add(offNtGlobalFlag).writeU32(0);                       // NtGlobalFlag = 0

// 3) chequeo de tiempo: devolver un delta chico y estable
let ticks = 100000;
Interceptor.replace(
  k32.getExportByName('GetTickCount64'),
  new NativeCallback(() => { ticks += 10; return uint64(ticks); }, 'uint64', []));

console.log('[*] PEB limpiado en ' + peb + '; hooks anti-debug activos.');
```

Con estos tres *hooks*, tu binario de práctica —que sin esto salía con «debugger detectado»— sigue hasta el **flujo protegido** y podés analizarlo. En un debugger, **ScyllaHide** hace lo equivalente con un par de clics. Lo importante es entender **qué** estás falseando y **por qué**, para no engañarte a vos mismo sobre lo que hace el binario.

## Práctica

En tu VM, con un **binario propio**:

1. Compilá un programa con tres chequeos (`IsDebuggerPresent`, lectura de `BeingDebugged` en el PEB y un chequeo de tiempo con `rdtsc`) que imprima «protegido» solo si ninguno detecta nada.
2. Verificá que bajo debugger **detecta** y sale.
3. Neutralizalos con ScyllaHide o con un script de Frida y confirmá que ahora llega a «protegido».
4. Escribí dos renglones sobre por qué este mismo procedimiento, aplicado a malware, se hace **solo en VM descartable**.

## Preguntas de repaso

?? ¿Cuál es el riesgo específico de neutralizar anti-análisis en malware?
!! Que el binario **esconde su payload detrás del chequeo**: al hacerle creer que no lo observan, **ejecuta su carga real**. Por eso se hace solo en VM descartable con snapshot y red controlada (4.4).

?? ¿Qué mira `IsDebuggerPresent` y cómo se neutraliza?
!! Lee el byte **`BeingDebugged` del PEB** (PEB+2). Se neutraliza con un *hook* que devuelve 0, o poniendo a 0 ese byte del PEB; ScyllaHide lo hace automáticamente.

?? ¿Por qué un chequeo de tiempo detecta al analista?
!! Porque entre dos puntos mide un **delta** (con `rdtsc`/`QueryPerformanceCounter`); bajo debugger o con breakpoints, el tiempo se dispara. Se neutraliza **achicando el delta** que devuelve el contador.

?? ¿Qué hace ScyllaHide que te ahorra parchear a mano?
!! Intercepta las APIs y estructuras del PEB que usan los chequeos (`IsDebuggerPresent`, `NtQueryInformationProcess`, `NtGlobalFlag`, etc.) y les devuelve valores de «sin debugger», **ocultando el debugger** de forma centralizada.

?? ¿Por qué «no parchear a ciegas» sigue valiendo acá?
!! Porque falsear un valor sin entenderlo puede ocultarte el comportamiento real o romper la lógica. Primero entendés qué chequea y qué estás cambiando; recién después neutralizás, y solo lo necesario.

:::{nota} Puerta de salida
Podés: (1) explicar por qué neutralizar un chequeo puede disparar el payload y qué recaudos exige; (2) relacionar cada chequeo de 2.15 con su contramedida; (3) ocultar el debugger con ScyllaHide o un hook de Frida sobre un binario propio; (4) justificar por qué se hace solo en VM descartable.
:::

## Fuentes de esta lección

- [github.com/x64dbg/ScyllaHide](https://github.com/x64dbg/ScyllaHide) — ocultación de debugger (PEB, APIs, NtGlobalFlag) (conocimiento externo).
- [frida.re/docs](https://frida.re/docs/) — `Interceptor.replace`/`attach` para falsear el resultado de una API.
- [github.com/LordNoteworthy/al-khaser](https://github.com/LordNoteworthy/al-khaser) — catálogo de chequeos anti-análisis para generar binarios propios de práctica.
- [2.15 Anti-análisis](02-anti-analisis.html) (reconocer) y [4.4 Dinámico seguro](04-dinamico-seguro.html) (la VM descartable).

:::{nota} Capas de esta lección
**Núcleo conceptual:** los chequeos y el encuadre de reconocimiento de 2.15; el dinámico seguro de la Etapa 4. **Conocimiento externo (agregado por esta edición):** las contramedidas concretas, ScyllaHide/TitanHide y los hooks de Frida. **Recomendación editorial:** ejemplos y práctica ilustrativos, sobre binarios propios y malware solo en VM descartable.
:::
