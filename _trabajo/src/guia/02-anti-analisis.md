---
title: "2.15 · Taxonomía anti-análisis: reconocer, no evadir"
description: "Clasificar las técnicas que un binario usa para estorbar el análisis — anti-debug, anti-VM, anti-disassembly, anti-dump —, reconocer sus firmas en el listado y documentarlas, en clave defensiva."
etapa: "Etapa 2 · Windows intermedio"
---

# Taxonomía anti-análisis: reconocer, no evadir

:::{nota} Objetivo de la lección
Tener un **mapa** de las técnicas que un binario usa para dificultar su análisis y saber **reconocerlas** cuando aparecen. **Prerrequisitos:** debugger (2.6), PE y TLS (1.4, 2.11), ofuscación (2.10).
:::

Esto es **reconocimiento defensivo**: clasificar y detectar estas técnicas para analizar mejor. No se enseña a **evadirlas** para proteger software comercial; la mayoría de los títulos de `Teorias_Numeradas` que las usan con ese fin quedan fuera del recorrido.

## Las cuatro familias

| Familia | Qué intenta | Ejemplos de señales |
|---|---|---|
| **Anti-debug** | Detectar que hay un debugger y cambiar de comportamiento o cerrarse | `IsDebuggerPresent`, `PEB.BeingDebugged`, `NtGlobalFlag`, flags del heap, `NtQueryInformationProcess`, chequeos de tiempo (`rdtsc`, `GetTickCount`), detección de breakpoints (`0xCC`, registros `DR`) |
| **Anti-VM / anti-sandbox** | Detectar que corre en una máquina virtual o sandbox | Claves de registro de VMware/VBox, direcciones MAC conocidas, drivers/dispositivos, pocos núcleos/poca RAM, nombres de usuario típicos de sandbox |
| **Anti-disassembly** | Confundir al desensamblador estático | Instrucciones solapadas, saltos al medio, `jmp` a registro, basura entre bloques (lo viste en [2.10](02-ofuscacion.html)) |
| **Anti-dump** | Dificultar volcar el proceso de memoria | Borrar la cabecera PE en memoria, `SizeOfImage` alterado, secciones sin permisos esperados |

## Qué muestra CLS

El capítulo 22 introduce anti-debug "desde lo más básico": qué es (técnicas para **detectar** un debugger y reaccionar), el comando **`hide`** de x64dbg para ocultarse, y cómo un programa detecta **breakpoints por software y por hardware** ({{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_22 Antidebug 1_22 Antidebug 1.txt|Reversing desde cero, cap. 22}}).

El capítulo 24 usa una **aplicación propia** que aplica varias técnicas a la vez: al ejecutarla suelta "no encontró debugger", pero si hay un IDA abierto —**aunque no cargue el programa**— lo detecta por el **nombre del proceso/ventana** y muestra "detected by IDA"; lo mismo con `x32dbg` ("detected by x32dbg"). Es el ejemplo perfecto de **detección por entorno**, no solo por breakpoint ({{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_24 Antidebug 2_24 Antidebug 2.txt|Reversing desde cero, cap. 24}}).

## Cómo detectarlas al analizar

- **Por imports/strings:** `IsDebuggerPresent`, `CheckRemoteDebuggerPresent`, `NtQueryInformationProcess`, nombres de procesos (`ida`, `x32dbg`, `ollydbg`), claves de VM.
- **Por comportamiento:** el programa "anda distinto" cuando lo abrís con un debugger o dentro de una VM. Ese cambio **es** la pista.
- **Dónde miran temprano:** acordate de los **TLS callbacks** ([2.11](02-tls.html)): un chequeo anti-debug puesto ahí corre antes de `main`.

Existen herramientas que **ocultan** el debugger (el comando `hide` de x64dbg, plugins tipo ScyllaHide). Se mencionan **solo para que las reconozcas** si aparecen; esquivar protecciones queda fuera del marco de esta lección, que es de **reconocimiento y documentación**.

## Ejemplo paso a paso: dos formas del mismo chequeo

*(Ejemplo **ilustrativo**: listado representativo de un anti-debug típico.)*

El mismo "¿me están debuggeando?" se ve de dos maneras:

```asm
; (a) por API — la más fácil de reconocer
call  IsDebuggerPresent          ; kernel32
test  eax, eax
jnz   detectado

; (b) a mano, leyendo el PEB (x64) — sin llamar a ninguna API
mov   rax, gs:[0x60]             ; RAX = puntero al PEB
movzx eax, byte ptr [rax+2]      ; PEB.BeingDebugged (offset 0x02)
test  al, al
jnz   detectado
```

La forma (a) la cazás en los imports (`IsDebuggerPresent`). La (b) **no usa imports**: la pista es el acceso a `gs:[0x60]` (en x86 sería `fs:[0x30]`) y el offset `+2`. Reconocer el patrón del PEB es lo que te permite detectar el anti-debug aunque no haya una API delatora. Lo documentás y seguís; no hace falta evadirlo para entenderlo.

## Más variantes del mismo chequeo

Las técnicas cambian de forma, pero cada una deja una **firma** reconocible. Estas tres aparecen a menudo (**conocimiento externo**; lo citado viene de la documentación de Microsoft):

**`CheckRemoteDebuggerPresent`.** Recibe un handle de proceso y un puntero a un `BOOL`, y escribe `TRUE` si ese proceso está siendo depurado. El "remote" del nombre no significa otra máquina: según Microsoft, el debugger está en **otro proceso**. La señal en el listado es el `call` y la lectura posterior de la variable, no el valor de retorno (que solo indica si la llamada funcionó).

**`NtQueryInformationProcess` con `ProcessDebugPort`.** Es una función de `ntdll` (la capa nativa de [2.14](02-pe-fino.html)); Microsoft la documenta como interna y sujeta a cambios, y no tiene biblioteca de importación, así que el programa suele obtenerla con `GetProcAddress`. Con la clase `ProcessDebugPort` (valor 7) devuelve un número de puerto: **distinto de cero** indica que el proceso corre bajo un debugger de modo usuario.

*(Ejemplo **ilustrativo**, x64: la consulta del puerto de depuración.)*

```asm
; rbx = GetProcAddress(GetModuleHandleW(L"ntdll.dll"), "NtQueryInformationProcess")
call  cs:GetCurrentProcess
mov   rcx, rax                    ; ProcessHandle
mov   edx, 7                      ; ProcessInformationClass = ProcessDebugPort
lea   r8, [rsp+30h]               ; &puerto (DWORD_PTR)
mov   r9d, 8                      ; tamaño del buffer
mov   qword ptr [rsp+20h], 0      ; ReturnLength = NULL
call  rbx
cmp   qword ptr [rsp+30h], 0      ; distinto de 0 -> hay debugger
jnz   detectado
```

Qué delata: la cadena `"NtQueryInformationProcess"` (o su hash, si la resolución está ofuscada), la constante `7` en `EDX` y la comparación del buffer contra cero.

**Chequeos de tiempo.** Dos lecturas de `rdtsc` (o de `GetTickCount`/`QueryPerformanceCounter`) alrededor de un fragmento corto y una comparación de la diferencia contra un umbral: si paso a paso tardó demasiado, "hay alguien mirando". La firma es el **par de lecturas** con una resta y un `cmp` contra una constante grande.

**Anti-VM por `CPUID`.** La instrucción `cpuid` con `EAX = 1` devuelve en el bit 31 de `ECX` el indicador de **hipervisor presente**; con `EAX = 0x40000000` un hipervisor devuelve su identificación en `EBX`, `ECX` y `EDX` (en el de Microsoft, los textos `"Micr"`, `"osof"`, `"t Hv"`). Ver `cpuid` seguido de `bt ecx, 31` o de comparaciones contra esas cadenas es una señal anti-VM. **Límite de la señal:** en un Windows con Hyper-V o seguridad basada en virtualización (VBS) activa, el propio sistema corre sobre un hipervisor, así que el bit también aparece en una máquina física. Un programa que lo usa como prueba de "estoy en una VM" se equivoca, y eso también se documenta.

## Cómo documentar lo que encontrás

Cada chequeo hallado se registra en una fila, con la misma disciplina de evidencia de la Etapa 4:

| Dirección / función | Técnica | Familia | Señal que la delata | Efecto observado | Cómo se confirmó |
|---|---|---|---|---|---|
| `0x140001120` (TLS) | `PEB.BeingDebugged` | Anti-debug | `gs:[60h]` + `[rax+2]` | Con debugger muestra "modo seguro" | Breakpoint en el `jnz`, `AL = 1` |
| `0x1400013A0` | `ProcessDebugPort` | Anti-debug | `GetProcAddress` + `edx = 7` | Igual que la anterior | Valor del buffer con y sin debugger |
| `0x140001500` | `CPUID` bit 31 | Anti-VM | `cpuid` + `bt ecx, 31` | Mensaje "entorno virtual" | Mismo resultado en VM y en host con VBS |

*(Filas **ilustrativas**: direcciones y efectos de un programa de práctica hipotético.)*

La columna "cómo se confirmó" es la que distingue una sospecha de un hallazgo: sin ella, la fila es una hipótesis.

## Práctica

En tu VM, con un **programa propio** (podés compilar uno que llame a `IsDebuggerPresent` y cambie un mensaje):

1. Hacé una tabla de tres columnas: técnica, familia, cómo la detectaste (import / string / comportamiento).
2. Ejecutá tu binario con y sin debugger y anotá la diferencia.
3. Poné el chequeo en un **TLS callback** y verificá que corre antes de `main`.
4. **Documentá** el cambio de comportamiento: qué muestra el programa con y sin debugger, y qué señal (import, string, lectura del PEB) lo delata. El objetivo es reconocer y dejar registrado, no evadir.
5. Agregá a tu programa `CheckRemoteDebuggerPresent` y la consulta de `ProcessDebugPort` (resolviendo `NtQueryInformationProcess` con `GetProcAddress`). Anotá el valor que devuelve cada una con y sin debugger.
6. Agregá la lectura de `CPUID` (bit 31 y, si está, la identificación del hipervisor) e imprimí el resultado en la VM. Escribí en la tabla de documentación por qué esa señal no prueba por sí sola que el equipo sea virtual.

## Preguntas de repaso

?? ¿Cuál es la diferencia entre anti-debug y anti-disassembly?
!! Anti-debug detecta/estorba la ejecución **dinámica** bajo un debugger; anti-disassembly confunde el análisis **estático** del desensamblador (instrucciones solapadas, saltos al medio). Son familias distintas.

?? En el cap. 24, ¿por qué el programa dice "detected by IDA" sin que IDA cargue el binario?
!! Porque detecta por **entorno**: busca el proceso/ventana de IDA abierto en el sistema, no necesita estar siendo debuggeado por él. Es detección por nombre de proceso.

?? Nombrá tres señales de anti-debug visibles sin ejecutar.
!! Imports/uso de `IsDebuggerPresent`, `CheckRemoteDebuggerPresent`, `NtQueryInformationProcess`; lectura de `PEB.BeingDebugged`/`NtGlobalFlag`; o strings con nombres de debuggers.

?? ¿Por qué conviene recordar los TLS callbacks acá?
!! Porque un chequeo anti-debug puesto en un callback corre **antes de `main`**: si solo mirás desde el entry point, ya decidió.

?? ¿Qué significa un `ProcessDebugPort` distinto de cero y por qué el programa suele obtener la función con `GetProcAddress`?
!! Que el proceso corre bajo un debugger de modo usuario. `NtQueryInformationProcess` es una función interna de `ntdll` sin biblioteca de importación, así que se resuelve en tiempo de ejecución; la cadena con su nombre (o su hash) es una pista.

?? ¿Por qué el bit de hipervisor de `CPUID` no prueba que el programa corre en una VM?
!! Porque un Windows con Hyper-V o VBS activo corre sobre un hipervisor aunque la máquina sea física, así que el bit también aparece ahí.

?? ¿Qué columna convierte una fila de la tabla de documentación en un hallazgo?
!! "Cómo se confirmó": el breakpoint, el valor leído o la comparación con y sin debugger. Sin ella, la fila es una hipótesis.

?? ¿Por qué el cambio de comportamiento con y sin debugger es, en sí, una pista?
!! Porque significa que el programa **chequea** su entorno: si hace algo distinto al correr bajo un debugger (o en una VM), tiene anti-análisis. Ese cambio te dice dónde buscar el chequeo, aunque no lo evites.

:::{nota} Puerta de salida
Podés: (1) clasificar una técnica en anti-debug/anti-VM/anti-disassembly/anti-dump; (2) detectar anti-debug por imports, strings y comportamiento; (3) explicar la detección por entorno del cap. 24; (4) relacionar un chequeo temprano con un TLS callback; (5) reconocer `CheckRemoteDebuggerPresent`, `ProcessDebugPort`, un chequeo de tiempo y un chequeo de `CPUID` por su firma en el listado; (6) registrar cada chequeo en una tabla con su confirmación.
:::

:::{nota} Lo que queda fuera
Cómo neutralizar estos chequeos, los anti-debug de modo kernel y los de protectores comerciales, y las técnicas basadas en excepciones o en manipular hilos (se mencionan como familia, sin detalle). La lección es un mapa para **reconocer y documentar**; no es un catálogo completo.
:::

## Fuentes de esta lección

- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_22 Antidebug 1_22 Antidebug 1.txt|Reversing desde cero, cap. 22}} — qué es anti-debug, `hide` de x64dbg, detección de breakpoints software y hardware.
- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_24 Antidebug 2_24 Antidebug 2.txt|Reversing desde cero, cap. 24}} — app propia con varias técnicas; detección por nombre de proceso ("detected by IDA/x32dbg").
- [Teorias_Numeradas · clasificación](../teorias.html) — títulos de anti-debug (material por título, no leído; muchos con fin de evasión comercial, fuera de alcance).
- Microsoft Learn (conocimiento externo): [IsDebuggerPresent](https://learn.microsoft.com/en-us/windows/win32/api/debugapi/nf-debugapi-isdebuggerpresent), [CheckRemoteDebuggerPresent](https://learn.microsoft.com/en-us/windows/win32/api/debugapi/nf-debugapi-checkremotedebuggerpresent), [NtQueryInformationProcess](https://learn.microsoft.com/en-us/windows/win32/api/winternl/nf-winternl-ntqueryinformationprocess) (clase `ProcessDebugPort`, función interna sin biblioteca de importación) y [Hypervisor Feature Discovery](https://learn.microsoft.com/en-us/virtualization/hyper-v-on-windows/tlfs/feature-discovery) (bit de hipervisor presente y hoja `0x40000000`).

:::{nota} Capas de esta lección
**Contenido observado en CLS:** el `hide` y la detección de breakpoints del capítulo 22 y la detección por entorno del 24. **Conocimiento externo:** la taxonomía de las cuatro familias y las señales concretas (PEB, NtGlobalFlag, `ProcessDebugPort`, chequeos de tiempo, `CPUID`, anti-VM, anti-dump). **Ejemplo ilustrativo:** los listados del PEB y de `ProcessDebugPort`, y las filas de la tabla de documentación. **Recomendación editorial:** el enfoque de reconocer y no evadir, la tabla de documentación y la práctica con binario propio.
:::
