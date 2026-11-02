---
title: "2.17 · Packers didácticos: UPX, stub, OEP, dump e IAT"
description: "Señales genéricas de empaquetado; cómo se ve un ejecutable comprimido con UPX, cómo llegar al OEP (también en x64), dumpear, reconstruir la IAT y por qué un dump falla — sobre binarios propios, con upx -d como red de seguridad."
etapa: "Etapa 2 · Windows avanzado (2C)"
---

# Packers didácticos: UPX, stub, OEP, dump e IAT

:::{nota} Objetivo de la lección
Entender qué hace un **packer** y recorrer el desempaquetado **didáctico** de UPX: reconocer el stub, llegar al **OEP**, **dumpear** el proceso y reconstruir la **IAT**. **Prerrequisitos:** PE, secciones e IAT (1.4), PE fino (2.14), debugger (2.6).
:::

:::{peligro} Solo UPX didáctico, sobre binarios propios
Esta lección usa **UPX** —un compresor **abierto y reversible**— sobre **programas propios**. UPX trae su propio `upx -d` que descomprime, así que siempre tenés una red de seguridad. **No** se cubre el desempaquetado de **protectores comerciales** (Themida, ACProtect, ASProtect, VMProtect…): eso queda fuera del recorrido, como la Etapa 5 excluida. El objetivo es **entender el mecanismo**, no vulnerar protecciones de terceros.
:::

## Qué hace un packer

Un packer toma tu `.exe`, **comprime** (o cifra) el código original y le pone adelante un **stub**: un pequeño programa que, al ejecutarse, **descomprime** el original en memoria y le salta. En disco ves poco; el código real aparece recién en runtime. Señales de UPX en el PE (lo viste en [1.4](01-pe.html) y [2.14](02-pe-fino.html)):

- Secciones llamadas **`UPX0`** (vacía en disco, grande en memoria: ahí se descomprime) y **`UPX1`** (el stub + datos comprimidos).
- **Pocos imports** (el stub resuelve el resto en runtime).
- El **entry point** cae en `UPX1`, no en el código original.

El **OEP** (*Original Entry Point*) es la dirección donde empezaba tu programa antes de empacar. Desempaquetar didácticamente es: **llegar al OEP**, **dumpear** la memoria ya descomprimida y **reconstruir la IAT** para que el dump vuelva a ser un `.exe` que corre.

## El método (sobre un binario propio)

El capítulo 13 lo plantea como práctica de unpacking **simple**: los ejemplos no tienen IAT redirection ni stolen bytes/code, y su anti-debug es tan básico que alcanza el comando `hide` de x64dbg ({{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_13 Unpacking 2 - OEP_13 Unpacking 2 - OEP.txt|Reversing desde cero, cap. 13}}).

1. **Reconocé el packer.** Secciones `UPX0`/`UPX1`, entry en `UPX1`.
2. **Llegá al OEP.** El stub termina restaurando registros y **saltando** al OEP. En UPX el patrón clásico es un `popad` seguido de un salto lejano (`jmp`) a una dirección en la zona que estaba vacía (`UPX0`). Un breakpoint de hardware sobre el stack o seguir hasta ese `jmp` te deja en el OEP.
3. **Dumpeá** el proceso cuando estás en el OEP (con Scylla, o el script que muestra el curso).
4. **Reconstruí la IAT.** El tute 15 del Curso IDA sigue justo acá: después del OEP, **dumpear y reconstruir la IAT** para que el ejecutable vuelva a resolver sus imports ({{src:CLS_Guia/_trabajo/extraido_ida/15-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|Curso IDA, tute 15}}).
5. **Comprobá con `upx -d`.** Como es UPX, descomprimí el mismo binario con `upx -d` y comparás tu dump con el original: así validás que llegaste bien.

## Ejemplo paso a paso: el salto al OEP

*(Ejemplo **ilustrativo** y **de 32 bits (PE32)**: `popad`/`pushad` existen solo en x86, así que este patrón es el de un UPX sobre un binario de 32 bits; en x64 el stub se ve distinto. Direcciones construidas para mostrar el patrón.)*

```asm
; ...final del stub de UPX, en la sección UPX1...
0045A1F0  popad                      ; restaura los registros que guardó al inicio (pushad)
0045A1F1  jmp     0x00401000         ; salto lejano a UPX0 → ese es el OEP
;--- en 0x00401000 ya estás en el código ORIGINAL ---
00401000  push    ebp
00401001  mov     ebp, esp           ; prólogo típico del main
```

El `popad` + `jmp` fuera de `UPX1` (hacia la zona `UPX0`, antes vacía) es la firma de "acá terminó de descomprimir y salta a tu programa". Parás en `0x00401000`, dumpeás y reconstruís la IAT.

## Y en 64 bits, ¿dónde está el `popad`?

**No existe a nivel de arquitectura x86-64.** En modo largo (*Long Mode* de 64 bits), los opcodes de 32 bits `0x60` (`pushad`) y `0x61` (`popad`) fueron invalidados por Intel y AMD; si la CPU intenta ejecutarlos en x64, genera de inmediato una excepción por opcode no válido (`#UD` - *Invalid Opcode Exception*). Además, en x64 existen 16 registros de propósito general (`RAX`..`R15`) en lugar de 8, por lo que el stub de UPX para x64 debe guardar y restaurar los registros explícitamente mediante instrucciones `push` y `pop` individuales de 64 bits.

### Anatomía del Stub de Descompresión UPX en x64 (Entrada y Cola)

Al iniciarse el binario empacado, el entry point en la sección `UPX1` salva el contexto en la pila con una secuencia de `push rax`, `push rcx`, ..., `push r15`. Al terminar de descomprimir el código original sobre la sección `UPX0` (que inicialmente estaba vacía y asignada con permisos de escritura), el stub ejecuta el desenrollado inverso y emite el salto de cola (*Tail Jump*) hacia el **OEP**:

```asm
; =========================================================================
; Final del stub de descompresión en UPX x64 (al final de la sección UPX1)
; =========================================================================
00007FF780021A40  41 5F               pop     r15
00007FF780021A42  41 5E               pop     r14
00007FF780021A44  41 5D               pop     r13
00007FF780021A46  41 5C               pop     r12
00007FF780021A48  41 5B               pop     r11
00007FF780021A4A  41 5A               pop     r10
00007FF780021A4C  41 59               pop     r9
00007FF780021A4E  41 58               pop     r8
00007FF780021A50  5F                  pop     rdi
00007FF780021A51  5E                  pop     rsi
00007FF780021A52  5D                  pop     rbp
00007FF780021A53  48 83 C4 08         add     rsp, 8     ; descarta el slot alineado de RSP salvado
00007FF780021A57  5B                  pop     rbx
00007FF780021A58  5A                  pop     rdx
00007FF780021A59  59                  pop     rcx
00007FF780021A5A  58                  pop     rax
00007FF780021A5B  E9 A0 F5 FD FF      jmp     00007FF780001000  ; ¡Tail Jump inter-sección hacia UPX0!

; =========================================================================
; En 0x00007FF780001000: Código ORIGINAL x64 completamente desempacado (OEP)
; =========================================================================
00007FF780001000  48 83 EC 28         sub     rsp, 28h   ; Prólogo típico x64 (reserva 32 bytes de shadow space)
00007FF780001004  E8 57 02 00 00      call    00007FF780001260
```

### Cómo cazar el OEP en x64 sin depender de una instrucción fija

Dado que cualquier empaquetador moderno puede alterar el orden de los registros o intercalar instrucciones basura (*junk code*) antes del salto final, el método riguroso en ingeniería inversa se basa en la transición de memoria $W \oplus X$ (escribir y luego ejecutar en otra sección):

1. **Método x64dbg (Memory Breakpoint on Execution):**
   - Abrí el binario x64 en `x64dbg`.
   - Presioná `Alt+M` para abrir la pestaña del mapa de memoria (*Memory Map*).
   - Localizá la sección **`UPX0`** (habitualmente la primera sección con memoria asignada en `ImageBase + 0x1000`).
   - Hacé clic derecho sobre la cabecera o primera página de `UPX0` $	o$ **Breakpoint de memoria** $	o$ **Ejecutar (F2)**.
   - Presioná `F9` (*Run*). El desempaquetador escribe a toda velocidad en `UPX0` sin detenerse (los accesos de escritura no activan un breakpoint de ejecución).
   - En el instante exacto en que la CPU ejecuta el `jmp 0x00007FF780001000`, salta el breakpoint: el registro `RIP` apunta a la primera instrucción del código original (**OEP**).
   - En ese punto abrís **Scylla** (`Plugins` $	o$ `Scylla`), hacés clic en `IAT Autosearch` $	o$ `Get Imports` $	o$ `Dump Process` y finalmente `Fix Dump` sobre el archivo guardado.

2. **Método WinDbg (Hardware Execution Breakpoint):**
```text
$$ Localizar la ImageBase y la RVA de la primera sección (UPX0)
lm m target64
!dh target64 -f
$$ Supongamos ImageBase = 0x00007ff7`80000000 y RVA de UPX0 = 0x1000:
ba e 1 target64+0x1000
g
$$ El debugger se detendrá en el hardware breakpoint en el primer ciclo de reloj ejecutado en UPX0:
r rip
u rip L5
```

## Señales genéricas de empaquetado

UPX se reconoce por el nombre de sus secciones, pero un packer cualquiera deja otras huellas que se pueden combinar (**conocimiento externo**; los permisos y constantes están en la documentación de Microsoft):

| Señal | Dónde se ve | Por qué sugiere empaquetado |
|---|---|---|
| **Entropía alta** de una sección (cerca de 8 bits por byte) | PE-bear, Detect It Easy o un script | Los datos comprimidos o cifrados parecen aleatorios; el código normal tiene entropía bastante menor |
| Tamaño **en disco** chico y tamaño **virtual** grande | Tabla de secciones | La sección se llena en memoria al descomprimir |
| Sección **escribible y ejecutable** a la vez | Flags de la sección (`MEM_WRITE` + `MEM_EXECUTE`) | El stub escribe código y después lo ejecuta en el mismo lugar |
| Pocos imports, con `LoadLibrary`/`GetProcAddress` | Tabla de imports | Los demás se resuelven en ejecución ([2.14](02-pe-fino.html)) |
| Entry point fuera de la primera sección de código | Cabecera opcional | El primer código que corre es el stub |
| En ejecución: `VirtualAlloc`/`VirtualProtect` que dejan memoria ejecutable, escritura en ella y salto | Breakpoints en esas APIs | Es el desempaquetado en vivo |

Ninguna alcanza sola: un instalador con datos comprimidos tiene entropía alta sin ser un packer, y un programa legítimo puede cambiar permisos de memoria. Como con la huella de compilador ([2.13](02-huella-compilador.html)), se suman señales.

*(Ejemplo **ilustrativo**: cálculo de entropía de Shannon de un bloque de bytes, para entender qué muestran las herramientas.)*

```python
import math
from collections import Counter

def entropia(datos: bytes) -> float:
    # bits por byte: 0 si todos los bytes son iguales, 8 si son uniformes
    if not datos:
        return 0.0
    n = len(datos)
    return -sum(c / n * math.log2(c / n) for c in Counter(datos).values())
```

## Por qué un dump puede no funcionar

Llegar al OEP y dumpear no garantiza un ejecutable que corra. Las causas típicas, de la más común a la menos (**conocimiento externo**):

- **IAT sin reconstruir:** el dump tiene en la IAT direcciones absolutas de esta ejecución, no una tabla de imports que el loader pueda resolver.
- **Cabeceras de secciones sin ajustar:** en memoria cada sección está en su dirección virtual; si el dumper no reescribe los offsets en disco para que coincidan, el archivo queda desalineado.
- **Base distinta:** si el proceso cargó en otra base por ASLR y el dump no conserva o ajusta las relocalizaciones, las direcciones absolutas del código no coinciden.
- **Estado ya modificado:** si dumpeás después del OEP, las variables globales ya pueden tener valores de esta ejecución.
- **Código que corre antes:** TLS callbacks ([2.11](02-tls.html)) o anti-dump ([2.15](02-anti-analisis.html)).

Para **analizar** no siempre hace falta que el dump corra: abierto en IDA o Ghidra, con la base correcta, ya muestra el código descomprimido. Que corra es la prueba de que reconstruiste bien, no un requisito para leerlo.

:::{aviso} El dump de Scylla crashea al ejecutarlo: es el ASLR, no la IAT
Al volcar un proceso que cargó con **ASLR activo**, las direcciones absolutas ya quedaron reubicadas a la base de *esa* ejecución, pero el dump conserva el flag `DYNAMIC_BASE (0x0040)` y Windows intenta re-reubicarlo con una `.reloc` ya consumida → `0xC0000005` al hacer doble clic. No reconstruiste mal la IAT: es el ASLR. Solución: en Scylla activá **Update header ImageBase** (que el `ImageBase` del dump sea la base real del volcado) y en PE-bear **desmarcá Dynamic Base** (o poné `Relocations stripped 0x0001` en File Header). Así el loader lo carga exactamente en la base para la que quedaron fijadas sus direcciones.
:::

## Práctica

En tu VM, con un **programa propio** (necesitás UPX, gratis y open source; versiones de referencia: UPX 4.x, x64dbg, Scylla):

1. Compilá un `hola.exe` propio **de 32 bits (x86)** —para que valga el patrón `popad` de arriba— y guardá su hash.
2. Comprimilo: `upx hola.exe`. Mirá en PE-bear las secciones `UPX0`/`UPX1` y cómo cambió el entry point y los imports.
3. En x64dbg (x32dbg), llegá al OEP siguiendo el `popad`/`jmp`. Anotá el OEP como **RVA** (dirección − base de imagen), no como VA absoluta.
4. Dumpeá y reconstruí la IAT (Scylla).
5. **Validá**: `upx -d hola.exe` recupera el original; comparalo con tu dump por **RVA del OEP y comportamiento** (no por la VA absoluta, que puede diferir según dónde cargue). ¿Coinciden el punto de entrada y los imports resueltos?
6. Repetí con un `hola.exe` propio **de 64 bits**: llegá al OEP con un breakpoint de memoria en ejecución sobre la región de `UPX0` y anotá qué instrucción del stub hizo el salto.
7. Calculá la entropía de cada sección del original y del comprimido (con una herramienta o con la función de arriba) y armá una tabla con las señales genéricas que muestra cada uno.

## Preguntas de repaso

?? ¿Qué son las secciones `UPX0` y `UPX1`?
!! `UPX1` trae el **stub** y los datos comprimidos; `UPX0` está **vacía en disco** pero reservada en memoria: ahí el stub **descomprime** el código original. El entry point apunta a `UPX1`.

?? ¿Qué es el OEP y por qué lo buscás?
!! El *Original Entry Point*: la dirección donde arrancaba tu programa antes de empacar. Al llegar ahí, el código ya está **descomprimido** en memoria, listo para dumpear.

?? ¿Cuál es el patrón clásico para detectar el salto al OEP en UPX?
!! Un **`popad`** (restaura los registros que guardó el `pushad` inicial del stub) seguido de un **`jmp` lejano** que sale de `UPX1` hacia la zona `UPX0`. Ese salto cae en el OEP.

?? ¿Por qué hay que reconstruir la IAT después de dumpear?
!! Porque el stub resolvió los imports en runtime; el dump "crudo" no tiene una tabla de imports válida. Reconstruir la IAT (p. ej. con Scylla) hace que el `.exe` recuperado vuelva a resolver sus funciones.

?? En x64 no hay `popad`. ¿Cómo llegás al OEP de un UPX de 64 bits?
!! Buscando el salto a la región que estaba vacía, o con un breakpoint de memoria en ejecución sobre esa región: se dispara en la primera instrucción ejecutada ahí, que es el OEP. Ese método no depende del packer.

?? ¿Por qué la entropía alta sola no prueba que un binario esté empaquetado?
!! Porque cualquier dato comprimido o cifrado la tiene (un instalador con recursos comprimidos, por ejemplo). Se combina con otras señales: tamaños en disco y virtual, secciones escribibles y ejecutables, pocos imports, entry point en el stub.

?? Llegaste al OEP y dumpeaste, pero el dump no arranca. ¿Qué revisás primero?
!! La IAT (¿se reconstruyó?), las cabeceras de secciones (¿coinciden offsets en disco y virtuales?) y la base (¿se conservaron las relocalizaciones?). Para leer el código no hace falta que arranque.

?? ¿Por qué UPX es seguro para practicar y un protector comercial no entra en esta guía?
!! UPX es **abierto y reversible** (`upx -d` deshace el empaquetado), y se practica sobre **binarios propios**. Desempaquetar protectores comerciales apunta a vulnerar software de terceros: queda fuera del marco educativo/defensivo.

:::{nota} Puerta de salida
Podés: (1) reconocer un binario UPX por sus secciones/entry/imports; (2) explicar qué es el OEP; (3) llegar al OEP por el patrón `popad`/`jmp` y dumpear; (4) decir por qué hay que reconstruir la IAT; (5) validar tu resultado con `upx -d`; (6) llegar al OEP de un UPX de 64 bits sin el patrón `popad`; (7) reconocer un posible empaquetado por señales genéricas y explicar por qué una sola no alcanza; (8) diagnosticar por qué un dump no corre.
:::

::: {nota} Dónde sigue esto (Bloque 2E) y límite del curso
El reconocimiento de protectores multicapa se amplía en **2.27 · Protectores comerciales y packers multicapa**, y la detección genérica del OEP mediante la regla $W \oplus X$ (página escrita y luego ejecutada) se practica con DynamoRIO/Pin en **2.29** y con Frida Stalker en **2.30**. Por el límite ético del curso, no se desempaquetan protectores comerciales sobre software ajeno.
:::

## Fuentes de esta lección

- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_13 Unpacking 2 - OEP_13 Unpacking 2 - OEP.txt|Reversing desde cero, cap. 13}} — unpacking simple: llegar al OEP y dumpear; ejemplos sin IAT redirection/stolen; anti-debug básico (`hide`).
- {{src:CLS_Guia/_trabajo/extraido_ida/15-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|Curso IDA, tute 15}} — dumpeado y reconstrucción de la IAT después del OEP.
- [Curso IDA · tutes 14–18](../ida_tutes/14.html) — serie de unpacking didáctico (UPX, ASPack) con IDA y Scylla.
- Video «10 Unpacking 1 - UPX» del tronco del curso → [índice de videos](../videos.html).
- Conocimiento externo: [UPX](https://upx.github.io/) (proyecto oficial); Microsoft Learn: [PE Format](https://learn.microsoft.com/en-us/windows/win32/debug/pe-format) (flags de sección), [VirtualProtect](https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-virtualprotect) y [Memory Protection Constants](https://learn.microsoft.com/en-us/windows/win32/memory/memory-protection-constants).

:::{nota} Capas de esta lección
**Núcleo conceptual:** el método de OEP del capítulo 13 y la reconstrucción de IAT del tute 15. **Conocimiento externo:** las secciones `UPX0`/`UPX1`, el patrón `popad`/`jmp`, el método por breakpoint de memoria en x64, las señales genéricas (entropía, permisos, tamaños), las causas de un dump fallido y `upx -d`. **Recomendación editorial:** el marco de solo-UPX-didáctico-sobre-binarios-propios y los ejemplos ilustrativos (listado del stub y función de entropía; no hay un laboratorio compilado con hashes reales en esta edición).
:::
