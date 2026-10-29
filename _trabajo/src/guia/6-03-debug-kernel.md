---
title: "6.3 · Debugging de kernel y bugchecks"
description: "Preparar un objetivo VM de pruebas, cargar únicamente el driver didáctico propio y leer stacks, dumps y bugchecks con WinDbg (símbolos, tipos de dump, parámetros, objetos de driver e IRP); Driver Verifier con rollback."
etapa: "Etapa 6 · Kernel y drivers (rama optativa)"
---

# Debugging de kernel y bugchecks

:::{peligro} Driver Verifier puede detener la VM
Microsoft advierte que Driver Verifier puede generar bugchecks. Usalo solo sobre el driver didáctico propio en una VM descartable, con snapshot previo y método de recuperación probado. No verifiques todos los drivers del host.
:::

:::{nota} Propósito
Separar depuración user-mode de kernel, obtener un stack reproducible de un driver propio y explicar qué evidencia aporta un dump. Al terminar deberías poder recorrer un bugcheck con un método fijo —código, parámetros, contexto, stack, módulo, memoria— y escribir una conclusión que diga qué está probado y qué no.
:::

**Prerrequisitos**

- *Obligatorios:* [6.1](6-01-arquitectura-kernel.html), driver propio revisado de [6.2](6-02-kmdf-ioctl.html), WinDbg y [2D.11 excepciones](2d-11-excepciones.html).
- *Recomendados:* 2C WinDbg/heap; test-target VM configurada según WDK vigente.

## Flujo de depuración

WinDbg puede depurar el kernel local o un equipo de prueba conectado. En la VM, símbolos correspondientes al build permiten resolver funciones y tipos; sin ellos, direcciones/nombres pueden quedar incompletos. Ante bugcheck, guarda código, parámetros, dump y estado del snapshot. `!analyze -v` es un punto de partida, no una conclusión automática.

Driver Verifier comprueba reglas de drivers y puede provocar deliberadamente un bugcheck al detectar violaciones. Configurá solo el driver objetivo de prueba a través de su UI/documentación, mantén el rollback disponible y apágalo/revierte la VM al finalizar según el procedimiento Microsoft aplicable.

## Símbolos

Sin símbolos correctos, el stack muestra direcciones o nombres aproximados y cualquier conclusión se debilita. La ruta de símbolos combina el servidor público de Microsoft (para el sistema) y la carpeta con el PDB **de tu build** del driver. Después de cambiarla se recargan con `.reload`. Anotá en el informe qué símbolos estaban disponibles; un frame que dice `BlocLab+0x1a2b` en lugar de un nombre de función es un límite, no un dato.

## Qué contiene un dump y qué no

Windows ofrece cinco configuraciones de volcado de kernel, que difieren sobre todo en tamaño:

| Tipo | Qué guarda | Para qué alcanza |
|---|---|---|
| Completo | Toda la memoria física, incluida parte de user mode | El análisis más amplio; es el más grande |
| Activo | Similar al completo para la mayoría de los fines, algo más chico | Casi todo lo del completo |
| De kernel | Memoria del kernel; en general omite user mode | Stacks, objetos y pool del kernel |
| Automático | Igual que el de kernel, con más flexibilidad en el archivo de paginación | Ídem kernel |
| Pequeño (minidump) | 64 KB | Código, parámetros, stack básico y lista de módulos |

Microsoft aclara que ningún dump da tanta información como depurar en vivo: es una **foto** de un instante. Si el dump es pequeño, declarar que no se pudo inspeccionar memoria que no está incluida.

## Lectura guiada de un bugcheck

Un orden de trabajo que evita saltar a conclusiones:

| Paso | Comando | Qué responde | Límite |
|---|---|---|---|
| 1. Código y parámetros | `.bugcheck`, `!analyze -v` | Qué condición detectó el sistema y con qué argumentos | El “módulo sospechoso” es una heurística |
| 2. Significado de los parámetros | Página del código en la referencia de bugchecks | Qué representa cada argumento para **ese** código | Cada código tiene su propia tabla |
| 3. Contexto | `.trap` (si hay trap frame) o `.cxr` | Registros y stack en el punto del fallo | No siempre hay trap frame |
| 4. Stack | `k`, `kv` | Ruta de llamadas | Depende de símbolos |
| 5. Instrucción y memoria | `ln`, `u` sobre la dirección; `!pool`, `!address`, `!pte` sobre la memoria referenciada | Qué función accedió a qué y si era pool paginado | Interpretación técnica, no causa raíz automática |
| 6. IRQL y módulos | `!irql`, `lm t n` | Nivel en el momento y versiones de los módulos | `!irql` refleja lo guardado por el depurador |
| 7. Objetos del driver | `!drvobj`, `!devobj`, `!irp`; `!wdfkd.*` en KMDF (6.2) | Qué dispositivo y qué solicitud estaban en curso | Requiere saber qué objeto mirar |

Para un 0xD1, por ejemplo, la documentación indica usar `ln` con el cuarto parámetro para ver la función que hizo el acceso, `!pool` sobre el primero para saber si era pool paginado y `dx KiBugCheckDriver` para leer el nombre del driver que el sistema registró como responsable. También advierte que, en la mayoría de los casos de ese código, el problema no es el IRQL sino la memoria accedida.

## Ejemplo trabajado

*(Esquema ficticio, no dump real.)*

```text
Bugcheck observado: DRIVER_VERIFIER_DETECTED_VIOLATION
!analyze -v: módulo sospechoso = BlocLab.sys
stack: nt!Verifier -> Wdf01000!callback -> BlocLab!EvtIoDeviceControl
Conclusión: revisar la longitud del buffer en el callback; confirmar parámetros y código fuente
```

El módulo señalado es evidencia para investigar; comprueba stack, parámetros, build/símbolos y si el driver estaba realmente activo en esa solicitud.

Informe de ese caso, separando observación de inferencia (ilustrativo):

| Afirmación | Tipo | Evidencia |
|---|---|---|
| Driver Verifier detectó una violación | Observación | Código de bugcheck y parámetros |
| La violación ocurrió durante `EvtIoDeviceControl` de BlocLab | Observación con símbolos | Stack con PDB del build propio |
| La solicitud en curso era el IOCTL `0x80006000` | Observación | `!wdfkd`/`!irp` sobre la solicitud del frame |
| La causa es una validación de longitud ausente | Inferencia | Coincide con el parámetro y el código fuente; falta reproducir |
| Ningún otro driver intervino | No determinado | El dump pequeño no incluye toda la memoria |

## Práctica

En VM con snapshot, conecta el debugger a un target de prueba ya configurado y carga solo el driver propio permitido. Captura una solicitud válida, inspecciona lista de módulos/stack y unload. Driver Verifier es opcional y solo si el docente confirma el rollback; no provoques un fallo deliberado ni fuerces un bugcheck. Si aparece uno, conserva el dump, analiza offline y revierte.

1. Configurá la ruta de símbolos con el PDB de tu build y verificá con `lm` que el driver propio tiene símbolos.
2. Con el target vivo, ubicá tu driver con `!drvobj` y su dispositivo con `!devobj`; si estás en el callback, seguí la solicitud con `!wdfkd` o `!irp`.
3. Si tenés un dump (propio o de un ejercicio provisto), recorré la tabla de lectura guiada paso por paso y completá la tabla de afirmaciones.

## Entregable

Registro de build/VM, símbolos, tipo de dump, comandos de inspección usados, stack, tabla de afirmaciones (observación/inferencia/no determinado) y evidencia de que driver/verifier ya no están activos o snapshot revertido.

## Repaso

?? ¿`!analyze -v` da siempre la causa raíz?
!! No. Resume el bugcheck y pistas; hay que correlacionar parámetros, stack, símbolos y estado.

?? ¿Por qué no usar Driver Verifier sobre el host?
!! Puede causar bugchecks y afectar estabilidad; se limita a un target de pruebas recuperable.

?? ¿Qué no podés esperar de un minidump?
!! La memoria completa: tiene 64 KB; alcanza para código, parámetros y stack básico, no para inspeccionar estructuras grandes.

?? ¿Para qué sirve `.trap` o `.cxr` antes de `k`?
!! Para poner el contexto en el punto del fallo, de modo que el stack corresponda a ese momento.

?? En un 0xD1, ¿qué parámetro llevás a `ln` y cuál a `!pool`?
!! El cuarto (dirección de la instrucción) a `ln`, para ver la función; el primero (memoria referenciada) a `!pool`, para ver si era pool paginado.

?? Un frame dice `BlocLab+0x1a2b`. ¿Qué te falta?
!! Símbolos correctos del build; sin ellos, el nombre de la función es una suposición.

:::{nota} Puerta optativa
Podés capturar un stack/dump del driver propio, configurar y declarar símbolos, recorrer un bugcheck con el orden código–parámetros–contexto–stack–memoria–objetos, explicar límites del tipo de dump y salir del ejercicio con target restaurado.
:::

:::{nota} Lo que queda fuera
La configuración del enlace de depuración de kernel paso a paso (se sigue la documentación del WDK vigente), el análisis de hangs y deadlocks, la depuración de hipervisor y el análisis de dumps de terceros no se desarrollan.
:::

## Fuentes

- Microsoft Learn: [Setting up kernel-mode debugging](https://learn.microsoft.com/en-us/windows-hardware/drivers/debugger/setting-up-kernel-mode-debugging-in-windbg--cdb--or-ntsd), [Live kernel-mode debugging using WinDbg](https://learn.microsoft.com/en-us/windows-hardware/drivers/debugger/performing-kernel-mode-debugging-using-windbg), [Driver Verifier](https://learn.microsoft.com/en-us/windows-hardware/drivers/devtest/driver-verifier), [Bug check analysis](https://learn.microsoft.com/en-us/windows-hardware/drivers/debugger/bug-check-code-reference2).
- Microsoft Learn, lectura: [Symbol path](https://learn.microsoft.com/en-us/windows-hardware/drivers/debugger/symbol-path), [Varieties of Kernel-Mode Dump Files](https://learn.microsoft.com/en-us/windows-hardware/drivers/debugger/varieties-of-kernel-mode-dump-files), [!analyze](https://learn.microsoft.com/en-us/windows-hardware/drivers/debuggercmds/-analyze), [.bugcheck](https://learn.microsoft.com/en-us/windows-hardware/drivers/debuggercmds/-bugcheck--display-bug-check-data-), [!drvobj](https://learn.microsoft.com/en-us/windows-hardware/drivers/debuggercmds/-drvobj), [!devobj](https://learn.microsoft.com/en-us/windows-hardware/drivers/debuggercmds/-devobj), [!irp](https://learn.microsoft.com/en-us/windows-hardware/drivers/debuggercmds/-irp), [Bug Check 0xD1](https://learn.microsoft.com/en-us/windows-hardware/drivers/debugger/bug-check-0xd1--driver-irql-not-less-or-equal), [Wdfkd.dll extensions](https://learn.microsoft.com/en-us/windows-hardware/drivers/debugger/kernel-mode-driver-framework-extensions--wdfkd-dll-).

:::{nota} Etiquetas
**Observado en CLS:** WinDbg de user mode. **Conocimiento externo:** depuración kernel, símbolos, tipos de dump, lectura de bugchecks y verifier. **Ejemplo ilustrativo:** bugcheck e informe ficticios. **Laboratorio verificado:** no; el target de kernel no se probó.
:::
