---
title: "2D.12 · ETW y telemetría defensiva"
description: "Entender providers, controllers, consumers y sesiones ETW; tipos de proveedores, AutoLogger, filtros, eventos perdidos y canales del registro de eventos; registrar y revisar un evento de un programa propio."
etapa: "Etapa 2 · 2D · Windows internals (optativa)"
---

# ETW y telemetría defensiva

:::{aviso} Rama optativa 2D
El ejercicio registra solo eventos de un programa propio o un perfil de diagnóstico conocido. No inicia trazas de kernel amplias ni recopila datos personales. No se detienen, modifican ni crean sesiones del sistema o de productos de seguridad.
:::

:::{nota} Propósito
Comprender cómo se genera, habilita y consume telemetría ETW, y usar una traza delimitada para ordenar eventos de una ejecución benigna. Al terminar deberías poder decir, frente a una traza o a la **ausencia** de un evento, qué estaba habilitado, qué pudo perderse y qué no se puede concluir.
:::

**Prerrequisitos**

- *Obligatorios:* procesos/hilos ([1.3](01-procesos.html)); [WinDbg y TTD](02-windbg-heap.html).
- *Recomendados:* [2D.10 IPC](2d-10-ipc.html); conceptos de excepciones en [2D.11](2d-11-excepciones.html); registro de Windows ([2D.3](2d-03-registro.html)).

## Modelo ETW

ETW separa **provider** (emite eventos), **controller** (inicia sesión, habilita providers y define buffers/archivo) y **consumer** (procesa eventos en vivo o desde un ETL). Una aplicación puede cumplir más de un rol. Los eventos perdidos, buffers y privilegios de control son parte de la interpretación, no detalles secundarios.

Los providers pueden ser clásicos/MOF, WPP, manifest-based o TraceLogging; el formato determina cómo decodificar payloads. Una traza ETL puede incluir nombres de procesos, rutas y otros datos sensibles: almacénala de forma local, mínima y temporal.

ETW permite habilitar o deshabilitar providers **en caliente**, sin reiniciar el programa. Un provider registrado que nadie habilitó, en general, no emite eventos: por eso “el programa no generó nada” y “nadie estaba escuchando” se ven igual desde afuera.

## Tipos de providers y qué implican para decodificar

| Tipo | Cómo emite | Dónde está la información para decodificar | Sesiones que pueden habilitarlo a la vez |
|---|---|---|---|
| MOF (clásico) | `RegisterTraceGuids` / `TraceEvent` | Clases MOF | Una |
| WPP | `RegisterTraceGuids` / `TraceEvent` | Archivos TMF, normalmente dentro del PDB del binario | Una |
| Manifest-based | `EventRegister` / `EventWrite` | Manifiesto registrado en el sistema | Hasta ocho |
| TraceLogging | `TraceLoggingRegister` / `TraceLoggingWrite` | El propio evento (autodescriptivo) | Hasta ocho |

Consecuencia práctica: una traza de un provider WPP sin el PDB/TMF correcto muestra eventos que no se pueden interpretar; uno con manifiesto necesita que el manifiesto de **esa** versión esté disponible. Un payload no decodificado es un límite que se declara, no un dato a inventar.

## Sesiones, filtros y AutoLogger

Una **sesión** recibe eventos de los providers habilitados en ella y los entrega **en tiempo real** a un consumidor o los escribe en un archivo **ETL**. El controller define tamaño y cantidad de buffers y puede leer estadísticas de la sesión, incluidos **eventos y buffers perdidos**.

Al habilitar un provider se filtra por **nivel** (severidad) y por **keywords** (categorías): con `MatchAnyKeyword`, el provider escribe un evento si alguna de sus keywords coincide; `MatchAllKeyword` restringe más. También se pueden pedir datos extendidos, como el SID del usuario o una pila de llamadas. Por eso dos trazas “del mismo provider” pueden contener cosas muy distintas.

Las sesiones **AutoLogger** arrancan en el inicio del sistema, antes del inicio de sesión. Se configuran en `HKLM\SYSTEM\CurrentControlSet\Control\WMI\Autologger\<sesión>`, con una subclave por provider (su GUID) y valores como `Start`, `FileName`, `Enabled`, `EnableLevel` y `MatchAnyKeyword`; el valor `Status` guarda el código de error si la sesión no pudo arrancar. Para el análisis defensivo, esa clave es **configuración persistente**: se lee (2D.3) como cualquier otra, y una sesión que debería existir y no arrancó deja evidencia en `Status`.

## ETW y el Visor de eventos

El registro de eventos de Windows usa el mismo modelo: un evento definido en un manifiesto puede escribirse en un **canal** (de tipo Admin, Operational, Analytic o Debug) y, a la vez, ser recogido por hasta siete sesiones ETW más. Algunos canales, como los de traza o análisis, requieren habilitación explícita; por ejemplo, el canal *Trace* de WMI-Activity no está activo por defecto. Que un evento no aparezca en el Visor puede deberse a que su canal no estaba habilitado.

## Por qué faltan eventos

Microsoft enumera causas de eventos perdidos que conviene tener presentes al leer una traza:

- el evento completo supera 64 KB, o es más grande que el buffer de la sesión;
- en tiempo real, el consumidor no lee a tiempo o no está presente;
- al escribir a archivo, el disco no da abasto.

A eso se suman las causas de configuración: provider no habilitado, nivel o keywords que lo excluyen, sesión detenida o canal deshabilitado. Una **ausencia** de evento solo se interpreta después de descartar estas causas, y la detención inesperada de una sesión o la deshabilitación de un provider son, en sí mismas, hechos a documentar.

## Ejemplo trabajado

*(Tabla ilustrativa; no corresponde a una captura real.)*

| Tiempo | Provider | Evento | PID | Interpretación prudente |
|---|---|---|---:|---|
| t0 | BlocLab | Start | 4100 | comienza el programa propio |
| t1 | BlocLab | ReadConfig | 4100 | lee su configuración local |
| t2 | BlocLab | Exit | 4100 | termina con estado informado |

Un evento `ReadConfig` no demuestra qué contenido se leyó ni que haya habido acceso no autorizado; relacioná el provider, el manifiesto/metadata, PID y ventana temporal.

Ficha de la sesión que produjo esa tabla (ilustrativa):

| Campo | Valor | Por qué importa |
|---|---|---|
| Sesión | `BlocLab-Lab`, a archivo ETL, iniciada y detenida a mano | Delimita tiempo y alcance |
| Provider | BlocLab (TraceLogging) | Autodescriptivo: no necesita manifiesto para decodificar |
| Nivel y keywords | Informativo; todas las keywords | Lo que **no** aparece no fue filtrado por keywords |
| Eventos/buffers perdidos | 0 / 0 según la herramienta de captura | Sin pérdidas declaradas en esta ventana |
| Datos extendidos | Ninguno (sin SID ni pila) | La identidad sale del PID, no del evento |
| Retención | ETL borrado tras exportar la tabla | Minimiza datos sensibles |

## Práctica

1. Usá un provider documentado del programa propio o un perfil de WPR aprobado para la VM.
2. Antes de capturar, hacé un inventario **de solo lectura**: sesiones en ejecución (`logman query -ets`), providers registrados (`logman query providers`) y sesiones AutoLogger configuradas (leyendo la clave del registro). No detengas ni cambies ninguna.
3. Registra una ejecución corta y acotada; no uses sesión de kernel ni habilites providers ajenos que no necesitás. Anotá nivel y keywords.
4. Abrí el ETL en WPA/visor compatible, identifica provider, evento, timestamp, PID y pérdidas reportadas.
5. Detené la sesión desde la misma herramienta, comprueba que no siga activa y elimina el ETL después de guardar solo la evidencia anonimizada necesaria.

## Entregable

Cronología de 3–5 eventos, ficha de la sesión (configuración mínima, nivel, keywords, pérdidas, fuente de decodificación), inventario de solo lectura de sesiones/AutoLogger y constancia de detención/eliminación del trace.

## Repaso

?? ¿Qué rol cumple el controller?
!! Define y controla una sesión ETW, habilita providers y establece cómo registrar eventos.

?? ¿Qué diferencia provider y consumer?
!! El provider produce eventos; el consumer los lee e interpreta desde una sesión o archivo.

?? ¿Una traza sin eventos prueba que no ocurrió actividad?
!! No. El provider puede no estar habilitado, no emitir ese evento, perder datos o tener metadata no decodificada.

?? ¿Por qué una traza WPP puede ser ilegible?
!! Porque la información para decodificar está en archivos TMF, normalmente en el PDB del binario; sin ellos los eventos no se interpretan.

?? ¿Qué filtran el nivel y las keywords?
!! Qué eventos escribe el provider en esa sesión: el nivel por severidad y las keywords por categoría.

?? ¿Qué es una sesión AutoLogger y dónde se configura?
!! Una sesión que arranca en el inicio del sistema; se configura en `HKLM\SYSTEM\CurrentControlSet\Control\WMI\Autologger`, y `Status` guarda el error si no arrancó.

?? Un evento esperado no aparece en el Visor de eventos. ¿Qué revisás antes de concluir?
!! Si su canal estaba habilitado, si el provider estaba habilitado con nivel y keywords adecuados y si hubo eventos perdidos.

:::{nota} Puerta optativa
Podés explicar el ciclo provider–controller–consumer, los tipos de providers y su decodificación, el efecto de nivel y keywords, el papel de AutoLogger y de los canales, leer una traza pequeña y declarar pérdidas, huecos y sensibilidad de los datos.
:::

:::{nota} Lo que queda fuera
Escribir providers o manifiestos, la sesión de kernel (NT Kernel Logger) y sus flags, el análisis de rendimiento con WPA, el formato binario ETL y las técnicas de manipulación de ETW no se desarrollan. Detener o reconfigurar sesiones del sistema queda fuera del alcance.
:::

## Fuentes

- Microsoft Learn: [About Event Tracing](https://learn.microsoft.com/en-us/windows/win32/etw/about-event-tracing), [Controlling ETW sessions](https://learn.microsoft.com/en-us/windows/win32/etw/controlling-event-tracing-sessions), [Consuming Events](https://learn.microsoft.com/en-us/windows/win32/etw/consuming-events), [Windows Performance Recorder](https://learn.microsoft.com/en-us/windows-hardware/test/wpt/windows-performance-recorder).
- Microsoft Learn, sesiones y canales: [Event Tracing Sessions](https://learn.microsoft.com/en-us/windows/win32/etw/event-tracing-sessions), [Configuring and Starting an AutoLogger Session](https://learn.microsoft.com/en-us/windows/win32/etw/configuring-and-starting-an-autologger-session), [Defining Channels](https://learn.microsoft.com/en-us/windows/win32/wes/defining-channels), [TraceLogging](https://learn.microsoft.com/en-us/windows/win32/tracelogging/trace-logging-portal), [logman query](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/logman-query), [Tracing WMI Activity](https://learn.microsoft.com/en-us/windows/win32/wmisdk/tracing-wmi-activity).
- **CLS:** temporalidad/debugging en [2.19](02-windbg-heap.html).

:::{nota} Etiquetas
**Observado en CLS:** debugging y evidencia como método. **Conocimiento externo:** ETW, tipos de providers, sesiones, AutoLogger, canales y causas de pérdida. **Ejemplo ilustrativo:** cronología y ficha de sesión BlocLab. **Laboratorio verificado:** no; requiere herramientas de captura disponibles en la VM.
:::
