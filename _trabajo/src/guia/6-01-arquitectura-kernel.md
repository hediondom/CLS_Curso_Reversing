---
title: "6.1 · Arquitectura del kernel y modelo de E/S"
description: "Ubicar user/kernel mode, IRQL, contexto de hilo, objetos de dispositivo y pilas, IRP y stack locations, pool, DPC, sincronización y bugchecks antes de tocar un driver."
etapa: "Etapa 6 · Kernel y drivers (rama optativa)"
---

# Arquitectura del kernel y modelo de E/S

:::{peligro} Rama optativa de alto impacto
Todo el bloque requiere VM descartable con snapshot. Un error en kernel puede colgar o detener el invitado; nunca pruebes un driver en el host ni en un equipo de uso diario.
:::

:::{nota} Propósito
Construir el mapa mental de la ruta de una solicitud desde user mode al driver y reconocer qué estado/memoria es válido según IRQL. Al terminar deberías poder mirar una rutina de un driver y decir **a qué IRQL** corre, **en el contexto de qué hilo**, **qué memoria** puede tocar y **qué** podría hacer que el sistema se detenga.
:::

**Prerrequisitos**

- *Obligatorios para Etapa 6:* C básico, assembly, memoria/stack, sincronización elemental, WinDbg y [2D.1 objetos/tokens](2d-01-objetos.html), [2D.2 memoria/loader](2d-02-memoria-loader.html), [2D.11 excepciones/debugging](2d-11-excepciones.html).
- *Recomendados:* [2C WinDbg/heap](02-windbg-heap.html) y fundamentos de kernel; no exige COM, Scheduler ni toda 2D.

## Mapa del kernel

Las aplicaciones corren en **user mode** con privilegios limitados; el kernel y drivers operan en **kernel mode**, donde un fallo puede afectar al sistema entero. El **I/O Manager** traduce solicitudes en IRP y las dirige por una pila de drivers. El **IRQL** limita qué rutinas/operaciones son válidas en cada contexto; a IRQL elevado no se puede asumir que una operación bloqueante o memoria paginable sea segura.

El **pool** es memoria del kernel con políticas de paginación/NX. La sincronización protege estado compartido entre CPU, callbacks e interrupciones. Un **bugcheck** detiene Windows al detectar una condición grave; el dump y stack ayudan a atribuirla, aunque el driver señalado puede no ser el origen.

## IRQL: qué se puede hacer en cada nivel

El IRQL al que corre una rutina determina qué funciones de soporte puede llamar. Los niveles que más vas a ver, de menor a mayor:

| IRQL | Qué rutinas típicas corren ahí | Qué se puede y qué no |
|---|---|---|
| `PASSIVE_LEVEL` | `DriverEntry`, `AddDevice`, `Unload`, la mayoría de las rutinas de despacho, hilos del driver, callbacks de *worker threads* | Hay contexto de hilo; se puede esperar y el código/datos pueden ser paginables |
| `APC_LEVEL` | Algunas rutinas de despacho | Igual que `PASSIVE_LEVEL`, salvo que no se reciben APC; el código puede ser paginable |
| `DISPATCH_LEVEL` | `StartIo`, DPC (`DpcForIsr`, `CustomDpc`), timers, rutinas de completion de drivers de nivel superior, `Cancel` con el spin lock tomado | **No** se puede esperar un objeto con intervalo no nulo; **no** se puede tocar memoria paginable; los spin locks suben a este nivel |
| DIRQL | Rutina de interrupción (ISR), `SynchCritSection` | Lo mínimo indispensable; se difiere el resto a un DPC |

Dos reglas documentadas que explican muchos bugchecks: una rutina por encima de `APC_LEVEL` no puede asignar ni acceder a pool paginado (un fallo de página ahí es fatal), y esperar con intervalo no nulo a `DISPATCH_LEVEL` o más también es fatal. Cuanto más alto el IRQL, más corta debe ser la rutina.

## Contexto de hilo

La mayoría de las rutinas de un driver corren en un **contexto de hilo arbitrario**: el del hilo que estaba ejecutándose cuando se las llamó, que puede no tener nada que ver con la aplicación que pidió la operación. Solo los drivers de más alto nivel (por ejemplo, la parte de un sistema de archivos que atiende la llamada) corren en el contexto del hilo que hizo la solicitud. Consecuencias:

- Una dirección de **user mode** solo tiene sentido en el contexto del proceso que la pasó; por eso los métodos de buffer de [6.2](6-02-kmdf-ioctl.html) y el patrón de `METHOD_NEITHER` de [6.4](6-04-revision-driver.html).
- El estado de cada dispositivo se guarda en la **extensión del dispositivo** (en KMDF, en el contexto del objeto), no en variables del hilo.

## Objetos de dispositivo, pilas y stack locations

Cada dispositivo se representa con una **pila de objetos de dispositivo**: el **PDO** que crea el driver de bus, el **FDO** del driver de función y, opcionalmente, **filtros** por encima o por debajo. Un IRP entra por arriba y baja por la pila; cada driver tiene en el IRP su propia **I/O stack location** con los parámetros que le corresponden (código de función, longitudes, código de IOCTL). Al completarse, el IRP sube y los drivers que registraron rutinas de *completion* las ejecutan, normalmente a IRQL elevado. El resultado viaja en `IoStatus.Status` y la cantidad de bytes en `IoStatus.Information`.

En KMDF todo esto existe igual, pero el framework lo encapsula en objetos request, colas y callbacks (6.2).

## Pool y NX

El pool **no paginado** se puede usar a cualquier IRQL, pero es un recurso escaso; el **paginado** solo por debajo de `DISPATCH_LEVEL`. Desde Windows 8, la documentación pide asignar la memoria no paginada desde el pool **no ejecutable** (`NonPagedPoolNx`) y usar el pool ejecutable solo cuando haga falta ejecutar código ahí. En un análisis, una asignación de pool ejecutable en un driver moderno es algo a explicar; con integridad de memoria (HVCI, ver [6.6](6-06-mitigaciones.html)) las asignaciones de kernel están más restringidas.

## Ejemplo trabajado

*(Diagrama conceptual.)*

```text
app: DeviceIoControl
  -> I/O Manager crea IRP
  -> pila: filtro -> function driver -> bus
  -> completion/status vuelve al cliente
```

En KMDF, el framework recibe/organiza IRP y llama a callbacks del driver. En WDM, el código trabaja más directamente con dispatch routines e IRPs. No deduzcas que una app se comunica con hardware solo por llamar `DeviceIoControl`: puede ser un dispositivo software.

Lectura de un bugcheck **ilustrativo** con los conceptos de esta lección (no es un dump real):

```text
Bug check 0xD1 DRIVER_IRQL_NOT_LESS_OR_EQUAL
  Arg1: dirección referenciada
  Arg2: 2              ; IRQL en ese momento = DISPATCH_LEVEL
  Arg3: 0              ; operación de lectura
  Arg4: dirección de la instrucción que leyó
```

Interpretación prudente: a `DISPATCH_LEVEL` se leyó una dirección paginable o inválida. Microsoft lista como causas típicas código o datos paginables usados a ese IRQL (por ejemplo, una función marcada paginable que corre con un spin lock tomado), un puntero inválido o liberado, o una llamada a un driver que ya se descargó. El IRQL no suele ser el problema en sí: lo es la memoria accedida. La 6.3 muestra cómo seguir cada parámetro.

## Práctica de lectura

Usá un diagrama/documentación de un driver propio o una muestra WDK ya compilada. Identificá user/kernel mode, entrada IRP, callback, cola, IRQL declarado y finalización. No cargues ni modifiques drivers en esta lección.

1. Para cada callback de la muestra, anotá a qué IRQL puede llamarse según la documentación.
2. Marcá cada asignación de memoria como paginada, no paginada o no paginada NX, y verificá que las que se usan a `DISPATCH_LEVEL` no sean paginadas.
3. Señalá dónde el driver depende del contexto del hilo llamador, si lo hace.

## Entregable

Diagrama de la ruta de una solicitud (con pila de dispositivos y stack locations), tabla callback–IRQL–memoria usada, glosario IRP/IRQL/pool/DPC/bugcheck y dos condiciones que podrían invalidar una rutina en IRQL elevado.

## Repaso

?? ¿Qué transporta un IRP?
!! Una solicitud de E/S y su estado/resultado a través de la pila de drivers.

?? ¿Por qué importa IRQL?
!! Restringe qué operaciones y memoria son válidas en el contexto actual.

?? ¿Qué no puede hacer una rutina a `DISPATCH_LEVEL`?
!! Esperar con intervalo no nulo ni acceder a memoria paginable; un fallo de página ahí es fatal.

?? ¿Qué significa que un driver corre en contexto de hilo arbitrario?
!! Que el hilo actual puede no ser el que pidió la operación; las direcciones de user mode del solicitante no son válidas en general.

?? ¿Qué es una I/O stack location?
!! La parte del IRP con los parámetros para un driver concreto de la pila.

?? ¿Por qué se prefiere `NonPagedPoolNx`?
!! Porque es pool no paginado no ejecutable; el ejecutable solo se usa si hace falta ejecutar código en esa memoria.

?? ¿Un bugcheck identifica siempre al culpable?
!! No necesariamente; muestra dónde se detectó el problema. El análisis debe reconstruir el estado y las llamadas previas.

:::{nota} Puerta optativa
Podés explicar la ruta user mode → I/O Manager → pila de dispositivos → driver, decir a qué IRQL corre un callback y qué memoria puede usar, y leer los parámetros de un 0xD1 sin atribuirle una causa única.
:::

:::{nota} Lo que queda fuera
El scheduler, APC en detalle, la arquitectura de la memoria virtual del kernel, PnP y energía (ver el recuadro de 6.4), DMA e interrupciones de hardware no se desarrollan.
:::

## Fuentes

- Microsoft Learn: [Overview of the Windows I/O Model](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/overview-of-the-windows-i-o-model), [IRQL](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/managing-hardware-priorities), [POOL_TYPE (pool paginado, no paginado y NX)](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/ne-wdm-_pool_type), [Synchronization](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/synchronization-techniques).
- Microsoft Learn, contexto y pilas: [Driver Thread Context](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/driver-thread-context), [Introduction to Device Objects](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/introduction-to-device-objects), [Device nodes and device stacks](https://learn.microsoft.com/en-us/windows-hardware/drivers/gettingstarted/device-nodes-and-device-stacks), [I/O Stack Locations](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/i-o-stack-locations), [Introduction to DPC Objects](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/introduction-to-dpc-objects), [Introduction to Spin Locks](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/introduction-to-spin-locks), [No-Execute Nonpaged Pool](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/no-execute-nonpaged-pool), [Bug Check 0xD1](https://learn.microsoft.com/en-us/windows-hardware/drivers/debugger/bug-check-0xd1--driver-irql-not-less-or-equal).
- **CLS:** stack/memoria [1.2](01-memoria.html); fundamentos user-mode en [2D.1](2d-01-objetos.html).

:::{nota} Etiquetas
**Observado en CLS:** conceptos de memoria y procesos. **Conocimiento externo:** arquitectura del kernel/driver, IRQL, contexto de hilo, pilas de dispositivos y pool. **Ejemplo ilustrativo:** diagrama IRP y lectura de 0xD1. **Laboratorio verificado:** no; lectura conceptual.
:::
