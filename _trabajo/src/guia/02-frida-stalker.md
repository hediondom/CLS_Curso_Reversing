---
title: "2.30 · Frida avanzado: Stalker y tracing de código"
description: "Usar Stalker de Frida para trazar instrucciones y bloques, medir cobertura (frida-drcov) y detectar código generado en runtime, y cuándo conviene frente a la DBI nativa."
etapa: "Etapa 2 · Desofuscación avanzada (2E)"
---

# Frida avanzado: Stalker y tracing de código

:::{nota} Objetivo de la lección
Dar el salto de los *hooks* puntuales (que ya usaste) al **tracing de todo un hilo** con **Stalker**: seguir instrucciones y bloques, medir **cobertura** y detectar **código generado en runtime**. Saber cuándo conviene Stalker y cuándo la DBI nativa. **Prerrequisitos:** scripting de debugger y Frida básico ([2.21](02-scripting-debugger.html)) y DBI ([2.29](02-dbi-dynamorio-pin.html)).
:::

Análisis dinámico sobre binarios propios o crackmes; el malware se instrumenta solo en **VM descartable** ([4.4](04-dinamico-seguro.html)).

## De los hooks al tracing

En 2.21 usaste `Interceptor` para engancharte a una función concreta (entrar, leer argumentos, salir). Eso es puntual. **Stalker** es otra cosa: es el motor de *tracing* de Frida que **sigue el flujo completo** de un hilo, reescribiendo el código **bloque por bloque** a medida que se ejecuta e informándote de cada bloque, llamada o retorno (**conocimiento externo**). Es la versión «scriptable en JavaScript» de lo que viste con Pin/DynamoRIO.

## Qué te da Stalker

- **Eventos:** `exec` (cada instrucción), `block`/`compile` (cada bloque básico), `call` y `ret`. Elegís la granularidad según cuánto *overhead* tolerás.
- **`transform`:** podés **reescribir** el flujo mientras se traza (insertar *callouts*, saltar, instrumentar). Es el gancho más potente.
- **Cobertura:** con **`frida-drcov`** generás un archivo de cobertura **compatible con Lighthouse** (el mismo visor de 2.29).
- **Código en runtime:** como Stalker ve el código *cuando se va a ejecutar*, detecta bloques en regiones recién escritas (útil para OEP y descifrado en memoria).

## Stalker vs DBI nativa (2.29)

| | Frida Stalker | Pin / DynamoRIO |
|---|---|---|
| Se programa en | JavaScript (rápido de iterar) | C/C++ (compilar el tool) |
| Plataformas | Windows, Linux, macOS, Android, iOS | sobre todo desktop x86/x64 (+ ARM en DynamoRIO) |
| *Overhead* / transparencia | Mayor *overhead*; menos transparente | Más rápido y maduro para trazas largas |
| Fuerte en | enganchar APIs + trazar en el mismo script | trazas masivas, cobertura a gran escala |

Regla práctica: si ya estás en Frida haciendo *hooks* y querés cobertura o una traza acotada, usá Stalker. Si necesitás trazar millones de instrucciones o integrarte con un fuzzer nativo, andá a Pin/DynamoRIO.

## Ejemplo paso a paso: trazar los bloques de un hilo

*(Ejemplo **ilustrativo**: script sobre un binario propio en VM; `frida -f .\propio.exe -l stalker.js`.)*

```javascript
// stalker.js — trazar SOLO dentro de la función objetivo (frida -f .\propio.exe -l stalker.js)
// Clave: activá Stalker al ENTRAR a la función y detenelo al salir. Si hacés follow/unfollow
// en la carga del script, Stalker corre y se apaga antes de que el hilo llegue a main -> imprime 0.
const objetivo = DebugSymbol.fromName('validar').address;  // o Module.getBaseAddress('propio.exe').add(0x1000)
let total = 0;

Interceptor.attach(objetivo, {
  onEnter() {
    this.tid = this.threadId;
    Stalker.follow(this.tid, {
      events: { compile: true },        // un evento por bloque básico compilado
      onReceive(raw) {
        // annotate:false devuelve pares limpios [inicio, fin] (sin el tag 'compile')
        const bloques = Stalker.parse(raw, { annotate: false, stringify: false });
        total += bloques.length;
        for (const [ini, fin] of bloques) {
          // ini/fin son NativePointer reales del bloque básico compilado
        }
      }
    });
  },
  onLeave() {
    Stalker.unfollow(this.tid);
    Stalker.flush();
    console.log('[*] bloques ejecutados dentro de validar:', total);
  }
});
```

Con `compile: true` recibís un evento por **bloque básico** (barato): es la **cobertura**. Con `exec: true` tendrías uno por **instrucción** (caro, pero fino): es la **traza** que sirve para reconstruir un algoritmo (la misma distinción cobertura/traza de [2.29](02-dbi-dynamorio-pin.html)). Para cobertura real no reinventes el parser: `frida-drcov` ya emite el formato de Lighthouse. Para ver la transición **stub → OEP** en un packer propio, marcás las regiones que se escriben y avisás cuando Stalker compila un bloque dentro de una de ellas: ahí saltó al código desempaquetado.

## Práctica

En tu VM, con binarios **propios**:

1. Seguí con Stalker el hilo principal de tu crackme y contá los bloques de una corrida «clave correcta» vs «incorrecta»; ¿qué bloque aparece solo en una?
2. Generá cobertura con `frida-drcov` y abrila en Lighthouse; comparala con la que sacaste con `drcov` nativo en 2.29.
3. Sobre tu binario empaquetado con UPX, detectá con Stalker el salto a una región recién escrita (OEP).
4. Anotá dos casos en los que preferirías Pin/DynamoRIO antes que Stalker.

## Preguntas de repaso

?? ¿Qué diferencia a `Interceptor` de `Stalker`?
!! `Interceptor` engancha funciones **puntuales**; `Stalker` **traza el flujo completo** de un hilo, bloque por bloque, informando cada instrucción/bloque/llamada/retorno.

?? ¿Por qué elegirías `compile`/`block` en vez de `exec`?
!! Porque `exec` emite un evento **por instrucción** (mucho *overhead*), mientras que `compile`/`block` emiten uno **por bloque básico**: suficiente para cobertura y mucho más barato.

?? ¿Cómo detecta Stalker código generado en runtime?
!! Porque ve el código **justo cuando se va a ejecutar**: si un bloque cae en una región que se **escribió antes**, es código nuevo (descifrado o desempaquetado), candidato a OEP.

?? ¿Qué ventaja da que la cobertura sea formato Lighthouse?
!! Que la **visualizás igual** que la de `drcov` nativo (2.29), coloreando los bloques en IDA/Ghidra. Podés comparar trazas de Stalker y de Pin/DynamoRIO con el mismo visor.

?? ¿Cuándo preferís Pin/DynamoRIO a Stalker?
!! Para **trazas muy largas** (millones de instrucciones), cuando importa el *overhead*/transparencia, o para integrarte con un fuzzer nativo. Stalker gana cuando ya estás en Frida y querés iterar rápido en JavaScript.

:::{nota} Puerta de salida
Podés: (1) explicar la diferencia entre hook puntual y tracing; (2) seguir un hilo con Stalker y elegir granularidad; (3) sacar cobertura con `frida-drcov` y leerla en Lighthouse; (4) detectar el salto al OEP por bloques en regiones recién escritas, y decidir entre Stalker y DBI nativa.
:::

## Fuentes de esta lección

- [frida.re/docs/stalker](https://frida.re/docs/stalker/) — `Stalker.follow`, eventos, `transform` (conocimiento externo).
- [frida-drcov (Lighthouse)](https://github.com/gaasedelen/lighthouse) — emitir cobertura en formato Lighthouse.
- [2.21 Scripting](02-scripting-debugger.html) (Frida básico) y [2.29 DBI](02-dbi-dynamorio-pin.html) (la comparación con Pin/DynamoRIO).

:::{nota} Capas de esta lección
**Contenido observado en CLS:** la automatización dinámica de 2.21 como base. **Conocimiento externo (agregado por esta edición):** Stalker, sus eventos y `transform`, y la cobertura con frida-drcov. **Recomendación editorial:** ejemplos y práctica ilustrativos, sobre binarios propios.
:::
