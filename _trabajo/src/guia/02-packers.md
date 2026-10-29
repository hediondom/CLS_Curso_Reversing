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

No está: `pushad`/`popad` no existen en x64. El stub de un UPX de 64 bits guarda y restaura los registros que necesita con varios `push`/`pop` sueltos, y la firma del final cambia. Lo que **no** cambia es la idea: en algún momento el stub termina de escribir el código original y **salta a una dirección dentro de la región que estaba vacía**. Por eso el método general no busca una instrucción concreta, sino ese salto (**conocimiento externo**):

- **Por el destino:** ubicá en el *memory map* la región que corresponde a `UPX0` y buscá, cerca del final del stub, un `jmp` cuyo destino caiga ahí.
- **Por la ejecución:** poné un **breakpoint de memoria en ejecución** sobre esa región. No salta mientras el stub escribe en ella; salta cuando el procesador ejecuta la primera instrucción ahí, que es el OEP.

La segunda forma funciona igual en 32 y 64 bits, y es la que conviene entender, porque no depende del packer.

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

:::{nota} Lo que queda fuera
Packers con varias capas, código que se descifra por partes durante la ejecución, redirección de la IAT, *stolen bytes* y, por el límite del curso, todo protector comercial. La lección enseña el mecanismo con un compresor abierto y reversible.
:::

## Fuentes de esta lección

- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_13 Unpacking 2 - OEP_13 Unpacking 2 - OEP.txt|Reversing desde cero, cap. 13}} — unpacking simple: llegar al OEP y dumpear; ejemplos sin IAT redirection/stolen; anti-debug básico (`hide`).
- {{src:CLS_Guia/_trabajo/extraido_ida/15-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|Curso IDA, tute 15}} — dumpeado y reconstrucción de la IAT después del OEP.
- [Curso IDA · tutes 14–18](../ida_tutes/14.html) — serie de unpacking didáctico (UPX, ASPack) con IDA y Scylla.
- Video «10 Unpacking 1 - UPX» del tronco del curso → [índice de videos](../videos.html).
- Conocimiento externo: [UPX](https://upx.github.io/) (proyecto oficial); Microsoft Learn: [PE Format](https://learn.microsoft.com/en-us/windows/win32/debug/pe-format) (flags de sección), [VirtualProtect](https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-virtualprotect) y [Memory Protection Constants](https://learn.microsoft.com/en-us/windows/win32/memory/memory-protection-constants).

:::{nota} Capas de esta lección
**Contenido observado en CLS:** el método de OEP del capítulo 13 y la reconstrucción de IAT del tute 15. **Conocimiento externo:** las secciones `UPX0`/`UPX1`, el patrón `popad`/`jmp`, el método por breakpoint de memoria en x64, las señales genéricas (entropía, permisos, tamaños), las causas de un dump fallido y `upx -d`. **Recomendación editorial:** el marco de solo-UPX-didáctico-sobre-binarios-propios y los ejemplos ilustrativos (listado del stub y función de entropía; no hay un laboratorio compilado con hashes reales en esta edición).
:::
