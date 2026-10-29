---
title: "2.19 · WinDbg, TTD y heap"
description: "WinDbg de punta a punta, Time Travel Debugging para ir hacia atrás, y heap: Page Heap y LFH para encontrar corrupción en un programa propio."
etapa: "Etapa 2 · Windows avanzado (2C)"
---

# WinDbg, TTD y heap

:::{nota} Objetivo de la lección
Manejar **WinDbg** para lo que x64dbg no da cómodo: **time-travel** (ir hacia atrás) y **diagnóstico de heap**. Encontrar la causa de un error de memoria en un programa **propio**. **Prerrequisitos:** debugger (2.6), llamadas y pila (2.5), memoria (1.2).
:::

## WinDbg: por qué y lo mínimo

El Curso IDA integra **WinDbg con IDA**: lo instala y lo maneja desde la interfaz de IDA porque es "un gran debugger" aunque incómodo, casi todo por comandos ({{src:CLS_Guia/_trabajo/extraido_ida/32-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|Curso IDA, tute 32}}). Comandos que vas a usar siempre:

| Comando | Qué hace |
|---|---|
| `g` / `p` / `t` | correr / step over / step into |
| `bp dir` / `ba r4 dir` | breakpoint de software / de acceso (hardware) |
| `k` | call stack |
| `dt tipo dir` | volcar una estructura con sus campos |
| `!address dir` | a qué región pertenece una dirección |
| `!heap` | estado del heap (ver abajo) |

## TTD: grabar y rebobinar

**Time Travel Debugging** (TTD, de Microsoft; **conocimiento externo**, es posterior al material de CLS) graba **toda** la ejecución en un trace y después la reproducís **hacia adelante y hacia atrás**. Cambia el método: en vez de "¿quién va a escribir este valor?" y reiniciar mil veces, ponés un breakpoint de acceso y hacés **`g-`** (go back) hasta la escritura que lo rompió. Para "¿quién corrompió este buffer?", TTD es la herramienta: encontrás la dirección mala y **retrocedés** hasta la instrucción culpable.

## Heap: Page Heap y LFH

El heap es donde más cuesta ver la corrupción, porque el síntoma (un crash) aparece **lejos** de la causa. Dos ayudas:

- **Page Heap / Application Verifier** (se activan con `gflags`; **conocimiento externo**): ponen cada bloque al **final de una página**, con una página de guardia detrás. Así un overflow de heap **crashea en el acto**, en la instrucción que escribe de más, no páginas después. El modo *full* consume más memoria, pero te da el crash exacto.
- **LFH** (*Low Fragmentation Heap*): Windows agrupa las alocaciones chicas en *buckets*. El Curso IDA dedica una parte a distinguir si una alocación cae en el **LFH o en el heap estándar**, porque cambia cómo se ven los bloques ({{src:CLS_Guia/_trabajo/extraido_ida/48-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|Curso IDA, tute 48}}). En WinDbg lo mirás con `!heap`.

El tute 44 muestra justamente **qué info de heap se obtiene con WinDbg dentro de IDA** ({{src:CLS_Guia/_trabajo/extraido_ida/44-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|Curso IDA, tute 44}}).

:::{aviso} Heap spraying: solo como concepto
El *heap spraying* (rellenar el heap con muchas copias de un dato para que una dirección sea predecible) se explica **para reconocerlo en un informe** —qué dice y qué evidencia buscar—, no se practica su construcción. Esta lección es de **diagnóstico defensivo**.
:::

## Ejemplo paso a paso: cazar un overflow de heap con Page Heap + TTD

*(Ejemplo **ilustrativo**: salida construida para mostrar el flujo.)*

Programa propio que hace `memcpy` de 40 bytes en un buffer de 32 del heap. Con Page Heap activo (`gflags /p /enable prog.exe /full`), crashea **en el `memcpy`**:

```text
(1a2c.0b30): Access violation - code c0000005
prog!copiar+0x2e:
  mov byte ptr [eax], cl      ; escribe en la página de guardia → crash acá

0:000> !heap -p -a eax
    address 0019f000 found in _DPH_HEAP ... 32 bytes allocated
    stack:  prog!reservar+0x1c   ← dónde se pidió el bloque de 32

0:000> k                        ; cómo llegué
  prog!copiar+0x2e
  prog!procesar+0x51
  prog!main+0x22
```

Con TTD, si no tuvieras el crash exacto, pondrías `ba w1 <fin del buffer>` y harías `g-` hasta la escritura. En los dos casos llegás a `copiar+0x2e` y, por `!heap -p -a`, al bloque de 32 pedido en `reservar`: la causa, no solo el síntoma.

## Práctica

En tu VM, con un **programa propio** con un bug de heap (un `memcpy`/`strcpy` que escribe de más en un bloque del heap):

1. Reproducí el crash "normal": vas a ver que explota lejos de la causa.
2. Activá **Page Heap** (`gflags /p /enable prog.exe /full`) y volvé a correrlo: ahora crashea en la escritura culpable.
3. Con `!heap -p -a <dir>` encontrá dónde se pidió ese bloque y con `k` el camino.
4. (Si tenés TTD) grabá, poné `ba w` en el fin del buffer y `g-` hasta la escritura.
5. **Apagá Page Heap al terminar**: `gflags /p /disable prog.exe`. La configuración de GFlags **persiste en el registro** (`Image File Execution Options`); si no la sacás, el programa queda siempre con page heap (más lento y con más consumo). Verificá con `gflags /p` que no quede ninguno activo.

## Preguntas de repaso

?? ¿Qué problema del heap resuelve Page Heap?
!! Que el crash aparece **lejos** de la causa. Page Heap pone cada bloque pegado a una **página de guardia**, así un overflow crashea **en el acto**, en la instrucción que escribe de más.

?? ¿En qué cambia TTD el análisis de "¿quién escribió este valor?"
!! Deja **retroceder** (`g-`) en una ejecución grabada hasta la escritura culpable, sin reiniciar una y otra vez. Grabás una vez y navegás hacia adelante y atrás.

?? ¿Qué es el LFH y por qué importa?
!! El *Low Fragmentation Heap*: Windows agrupa alocaciones chicas en buckets. Importa porque un bloque en LFH se ve distinto de uno en el heap estándar, y eso cambia cómo interpretás la memoria.

?? ¿Qué te da `!heap -p -a <dir>` en WinDbg?
!! La información del bloque de heap que contiene esa dirección: tamaño y, con Page Heap, el **stack de dónde se alocó**. Te lleva del síntoma a dónde se pidió la memoria.

?? ¿Por qué el heap spraying está solo como concepto?
!! Porque esta lección es de **diagnóstico defensivo**: interesa reconocer de qué habla un informe y qué evidencia buscar, no construir la técnica.

:::{nota} Puerta de salida
Podés: (1) moverte en WinDbg con `g/p/t`, `bp/ba`, `k`, `dt`, `!heap`; (2) explicar qué resuelve Page Heap y usarlo para cazar un overflow de heap propio; (3) decir cómo TTD ayuda a ir a la causa; (4) distinguir LFH de heap estándar; (5) explicar qué es el heap spraying sin construirlo.
:::

## Fuentes de esta lección

- {{src:CLS_Guia/_trabajo/extraido_ida/32-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|Curso IDA, tute 32}} — WinDbg manejado desde IDA.
- {{src:CLS_Guia/_trabajo/extraido_ida/44-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|Curso IDA, tute 44}} — info de heap con WinDbg dentro de IDA.
- {{src:CLS_Guia/_trabajo/extraido_ida/48-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|Curso IDA, tute 48}} — alocación en LFH vs. heap estándar.

:::{nota} Capas de esta lección
**Contenido observado en CLS:** WinDbg+IDA (tute 32), heap con WinDbg (tute 44) y LFH (tute 48). **Conocimiento externo:** TTD, Page Heap/Application Verifier (`gflags`) y el concepto de heap spraying. **Recomendación editorial:** el ejemplo ilustrativo y la práctica con un bug de heap propio (sin laboratorio compilado con hashes en esta edición).
:::
