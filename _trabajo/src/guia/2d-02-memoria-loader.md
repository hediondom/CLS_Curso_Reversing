---
title: "2D.2 · Memoria y loader: PEB/TEB, VAD e image mapping"
description: "Cómo Windows mapea y describe la memoria de un proceso: PEB/TEB, la lista del loader, las VAD del kernel y el mapeo de imágenes/secciones. Rama optativa 2D."
etapa: "Etapa 2 · 2D · Windows internals (optativa)"
---

# Memoria y loader: PEB/TEB, VAD e image mapping

:::{aviso} Rama optativa 2D
Lección de la [rama optativa 2D](../2d.html). Profundiza en cómo se **describe** la memoria del proceso; no repite el formato PE ([1.4](01-pe.html)) ni el PE fino ([2.14](02-pe-fino.html)), se apoya en ellos.
:::

:::{nota} Propósito
Saber de dónde sale la información de memoria de un proceso: el **PEB/TEB** (en user-mode), la **lista del loader** (módulos cargados) y las **VAD** (cómo el kernel describe cada región), y cómo se **mapea** una imagen. Para orientarte en un dump o en vivo sin perderte, y reconocer el contexto WOW64.
:::

**Prerrequisitos**

- *Obligatorios:* memoria y stack ([1.2](01-memoria.html)), formato PE ([1.4](01-pe.html)).
- *Recomendados:* PE fino ([2.14](02-pe-fino.html)), TLS ([2.11](02-tls.html)), WinDbg ([2.19](02-windbg-heap.html)).

## PEB y TEB

El **PEB** (*Process Environment Block*) y el **TEB** (*Thread Environment Block*) son estructuras en **user-mode** que describen el proceso y cada hilo. Ya tocaste el PEB en [anti-análisis](02-anti-analisis.html) (el campo `BeingDebugged`). Para memoria/loader, lo valioso del PEB:

- **`Ldr`** → tres listas doblemente enlazadas de **módulos cargados** (por orden de carga, de memoria y de inicialización): base, tamaño y nombre de cada DLL. Es de donde sale la lista de módulos que ves en el debugger.
- **`ProcessParameters`** → línea de comandos, directorio actual, variables de entorno: contexto de ejecución, útil en análisis.

El TEB guarda, entre otras cosas, el puntero a la cadena **SEH** en 32 bits (`FS:[0]`) y el TLS por hilo (lo viste en [2.11](02-tls.html)).

## WOW64: proceso x86 en Windows de 64 bits

**WOW64** permite ejecutar aplicaciones x86 en Windows x64; también hay variantes para ejecutar aplicaciones x86 y ARM de 32 bits en Windows ARM64. Para reversing importa porque el proceso conserva una vista de 32 bits, mientras el sistema operativo y algunas herramientas pueden mostrar el contexto nativo de 64 bits. Un proceso x86 no puede cargar una DLL x64 para ejecutarla, ni a la inversa; la comunicación entre ambos mundos requiere una frontera explícita, por ejemplo IPC o ciertos mecanismos de interoperabilidad.

Al comparar un proceso WOW64, anotá siempre la arquitectura del proceso y la del sistema. La redirección de archivos y Registro puede hacer que una ruta aparente no sea la que finalmente se consulta; no confundas esa redirección con una diferencia en el binario. En depuración, confirmá qué contexto de registros y qué vista de módulos estás examinando antes de interpretar direcciones o stacks. La práctica de esta lección sigue siendo de lectura: identificar arquitectura, módulos y regiones sin cambiar redirecciones del sistema.

### Cruce de llamadas entre x86 y el sistema nativo

En Windows x64, WOW64 no convierte cada instrucción x86 a x64. El proceso usa su ntdll x86; cuando llega a una llamada de servicio, una secuencia de transición en user mode permite que WOW64 la intercepte. La transición entra en modo nativo, donde las thunks de Wow64.dll adaptan argumentos de 32 a 64 bits y encaminan la llamada al servicio nativo. Por eso una pila puede alternar contexto x86 y nativo, y una vista x86 del depurador no siempre muestra toda la transición.

Con WinDbg nativo y la extensión wow64exts, !wow64exts.sw cambia entre los contextos x86 y nativo, !wow64exts.k muestra una pila combinada y !wow64exts.info resume datos de PEB/TEB de WOW64. La implementación interna puede variar por arquitectura y build; estos comandos sirven para observarla, no son un contrato de aplicación.

## La lista del loader

El **loader** de ntdll mantiene esas listas (`PEB_LDR_DATA` → `LDR_DATA_TABLE_ENTRY`). Que estén en listas enlazadas tiene una consecuencia para el análisis: un módulo se puede **desenlazar** de ellas para "esconderlo" de herramientas que solo recorren la lista. Por eso, al buscar módulos ocultos, se compara la lista del loader con lo que dicen las **VAD** del kernel. (Reconocer esto es defensivo; no se enseña a ocultar nada.)

## VAD: cómo el kernel describe la memoria

Las **VAD** (*Virtual Address Descriptors*) son un árbol que el kernel mantiene por proceso: cada nodo describe un **rango** de direcciones virtuales (privado o mapeado, permisos, a qué archivo/sección corresponde). En WinDbg, **`!vadump`** lista las regiones de un proceso en user mode. La extensión `!vad` ofrece detalles de nodos VAD en depuración de kernel y requiere los argumentos/contexto adecuados; no es un sustituto directo de `!vadump`. Sirven para:

- Ver **qué es** cada región: imagen mapeada (`Image`), archivo mapeado (`Mapped`), o memoria privada (`Private`, típico del heap/stack).
- **Cruzar** con la lista del loader: si una VAD de tipo `Image` no aparece en la lista del loader, es **algo a investigar** —puede tener explicaciones legítimas—, no una prueba de que haya un módulo oculto.

## Image mapping y secciones

Un `.exe`/`.dll` no se "copia" a memoria: se **mapea** vía un objeto **sección** (*section*/*file mapping*). Las páginas de código **suelen** ser de solo-lectura/ejecución y **compartidas** entre procesos (varias instancias comparten la misma imagen física); las de datos usan **copy-on-write** (se duplican al primer escribir). Ojo: los permisos exactos **dependen de las características de cada sección** del PE (una sección puede ser escribible) y pueden variar, así que no asumas "todo el código es RO". El loader aplica las **relocalizaciones** solo si la imagen no cargó en su base preferida (ASLR), y resuelve los imports (lo viste en PE/IAT, [1.4](01-pe.html)).

## Ejemplo trabajado

*(Ejemplo **ilustrativo**: salida resumida de WinDbg; valores construidos.)*

```text
0:000> lm                      (módulos cargados — fuente confiable para la lista)
    start    end      module
    00400000 0040c000 prog
    77000000 77180000 ntdll
    75d00000 75e00000 KERNEL32

0:000> !peb                    (extracto; la salida varía según versión/sesión)
    ProcessParameters.CommandLine: "prog.exe" --modo test

0:000> !vadump                 (extracto de regiones)
    BaseAddress  RegionSize  Protect         Type
    00400000     0000c000    EXECUTE_READ    Image    (prog.exe)
    00030000     00002000    READWRITE       Private  (heap/stack)
    00140000     00002000    READONLY        Mapped   (archivo de datos)
```

Lectura: `lm` da la lista de módulos; `prog.exe` aparece además como región `Image` en `!vadump`, el heap/stack es `Private` READWRITE y hay un archivo `Mapped` READONLY. La `CommandLine` del `!peb` da el contexto (ese comando puede variar según la versión de Windows y el tipo de sesión). Todo esto orienta un dump sin suponer.

## Práctica segura

En tu VM, con WinDbg sobre un **proceso propio**:

1. Con `lm` listá los **módulos cargados**; con `!peb` mirá la **CommandLine** (su salida varía según versión/sesión, por eso los módulos salen de `lm`).
2. `!vadump`: identificá una región `Image`, una `Private` y, si hay, una `Mapped`. Decí qué es cada una.
3. Elegí una DLL de `lm` y confirmá que tiene una región `Image` en su base en `!vadump` (la coherencia módulos↔VAD).
4. Anotá base y tamaño de tu `.exe` y compará con lo que dice el PE en disco ([2.14](02-pe-fino.html)).
5. En un proceso x86 bajo WOW64, alterná el contexto con !wow64exts.sw y observá la pila combinada con !wow64exts.k; registra qué frames son x86 y cuáles nativos.

## Entregable

Un mapa breve del proceso: lista de 3–5 módulos (base), 3 regiones de VAD clasificadas (Image/Private/Mapped) y la línea de comandos. Con una frase sobre la coherencia loader↔VAD.

## Preguntas de repaso

?? ¿Qué guarda el campo `Ldr` del PEB y por qué importa?
!! Las **listas de módulos cargados** (base, tamaño, nombre). Importa porque es la fuente de la lista de DLLs del proceso; y porque un módulo puede desenlazarse de ahí para esconderse, lo que se detecta cruzando con las VAD.

?? ¿Qué describe una VAD?
?? ¿Qué precaución tomás al analizar un proceso WOW64?
!! Anoto por separado la arquitectura del proceso y la del sistema, confirmo el contexto de registros y módulos, y tengo en cuenta la redirección de archivos/Registro. Un proceso de 32 bits no puede cargar una DLL de 64 bits para ejecutarla.

!! Un **rango** de direcciones virtuales del proceso: su tipo (Image/Mapped/Private), permisos y a qué archivo/sección corresponde. El kernel las mantiene en un árbol por proceso; `!vadump` sirve para listar regiones en user mode y `!vad` para inspección detallada en el contexto de depuración de kernel.

?? ¿Cómo se investiga un posible módulo que no está en la lista del loader?
!! Comparando los módulos (`lm` / lista del loader) con las **regiones `Image`** (`!vadump` / VAD del kernel): una imagen mapeada que no figure en la lista es **algo a investigar** (puede tener causas legítimas), no una prueba de ocultamiento. Es reconocimiento defensivo, no ocultar nada.

?? ¿Por qué el código de una DLL se comparte entre procesos y los datos no?
!! Porque el ejecutable se **mapea** como una imagen respaldada por una sección. Las páginas pueden compartirse mientras coinciden con el archivo; los permisos y el comportamiento ante escrituras dependen de cada sección. En una vista *copy-on-write*, la página modificada se vuelve privada para ese proceso. No todas las imágenes tienen permisos idénticos; verificá la región concreta con `!vadump`.

?? ¿Cuándo aplica el loader las relocalizaciones?
!! Solo si la imagen **no** cargó en su base preferida (por ASLR u ocupación): entonces ajusta las direcciones absolutas con la tabla de relocalización.

:::{nota} Puerta de salida (optativa)
Podés: (1) listar módulos con `lm` y leer la CommandLine con `!peb`; (2) clasificar regiones con `!vadump` (Image/Private/Mapped); (3) explicar la coherencia módulos↔VAD y qué amerita investigar; (4) explicar image mapping, código compartido y copy-on-write, y por qué los permisos de sección pueden variar; (5) describir qué cambia al analizar un proceso WOW64 y no confundir la vista x86 con la nativa.
:::

## Fuentes

- Microsoft Learn: [Debugging WOW64](https://learn.microsoft.com/en-us/windows/win32/winprog64/debugging-wow64), [File System Redirector](https://learn.microsoft.com/en-us/windows/win32/winprog64/file-system-redirector).

- Microsoft Learn: [Running 32-bit Applications (WOW64)](https://learn.microsoft.com/en-us/windows/win32/winprog64/running-32-bit-applications), [WOW64 Implementation Details](https://learn.microsoft.com/en-us/windows/desktop/WinProg64/wow64-implementation-details).

- **Conocimiento externo** (páginas concretas): [PEB (winternl)](https://learn.microsoft.com/en-us/windows/win32/api/winternl/ns-winternl-peb), [`lm` (list modules)](https://learn.microsoft.com/en-us/windows-hardware/drivers/debuggercmds/lm--list-loaded-modules-), [`!vadump`](https://learn.microsoft.com/en-us/windows-hardware/drivers/debuggercmds/-vadump) y el [formato PE (características de sección)](https://learn.microsoft.com/en-us/windows/win32/debug/pe-format). *Windows Internals* como referencia general. No se citan versiones ni valores reales.
- **Tie con CLS:** el PEB (`BeingDebugged`) en [2.15](02-anti-analisis.html); PE, IAT y relocalizaciones en [1.4](01-pe.html) y [2.14](02-pe-fino.html); TLS/SEH en [2.11](02-tls.html).

:::{nota} Etiquetas
**Observado en CLS:** PEB y PE/loader de 1.4, 2.11, 2.14, 2.15 (referencia). **Conocimiento externo:** VAD, listas del loader, image mapping/COW, redirección y transición WOW64. **Ejemplo ilustrativo:** las salidas de `lm`, `!peb` y `!vadump`. **Laboratorio verificado:** ninguno en esta edición; la práctica se hace sobre procesos propios en tu VM.
:::
