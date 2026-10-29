---
title: "Etapa 5 · Rama vulnerabilidades: entender el defecto, no armar un exploit"
description: "Desbordes de memoria, mitigaciones y divulgación responsable, practicando solo con programas propios."
etapa: "Etapa 5 · Ramas opcionales"
---

# Rama vulnerabilidades: entender el defecto, no armar un exploit

:::{nota} Objetivo de la lección
Al terminar vas a poder explicar cómo un desborde de buffer puede pisar el return address, qué mitigaciones lo frenan (canary, NX, ASLR) y cómo se documentan y corrigen varias familias de defectos, y cómo se divulga una vulnerabilidad de forma responsable.
:::

**Prerrequisitos:** etapas 0 a 4, stack y formato PE. **Duración sugerida:** 5 horas. Estimación aproximada.

## Alcance

Esta rama **no enseña a explotar sistemas ajenos**. Enseña a entender una clase de defecto, reconocerlo en código propio y explicar por qué las mitigaciones funcionan. Las prácticas se hacen con programas que escribís vos, en una VM local, sin red y sin datos reales.

En CLS hay carpetas de exploiting (`EXPLOITING`, `EXPLOITING Y REVERSING USANDO HERRAMIENTAS FREE`, `CURSO DE ARM EXPLOIT`) y material de "EXPLOIT" en `mega_OTROS`. Son **contenedores no revisados**; el mapa los ubica en la Etapa 5. Esta lección no los usa como fuente y no reproduce sus técnicas.

## El defecto: escribir más de lo que entra

```c
#include <string.h>
void copiar(char *entrada) {
    char buffer[16];
    strcpy(buffer, entrada);   // no verifica el tamaño
}
```

`buffer` tiene 16 bytes en el stack. Si `entrada` mide 20, `strcpy` escribe 4 bytes más allá del final. Esos bytes pisan lo que haya arriba en el stack: otras variables, el `EBP` guardado o el **return address**.

```text
stack de copiar():
+------------------+
| return address   |  <- si se pisa, el ret va a otra dirección
| EBP guardado     |
| buffer[16]       |  <- strcpy escribe acá y sigue
+------------------+
```

Si el atacante controla la entrada y el programa no valida, puede intentar que el return address apunte a código que él eligió. Ese es el núcleo del *stack buffer overflow* clásico.

:::{peligro} No es una receta
Esta explicación es conceptual. No incluye direcciones, offsets, shellcode ni pasos para lograr ejecución. Practicar eso contra sistemas ajenos es ilegal y está fuera del alcance del curso. El objetivo es reconocer el defecto y entender la mitigación.
:::

## Otras familias de defectos que conviene reconocer

El desbordamiento de buffer es solo una familia. En una revisión defensiva también conviene distinguir:

- **Desbordamiento o wraparound de enteros:** una longitud o un cálculo de tamaño se reduce o desborda antes de reservar/copiar memoria. Revisá límites, signo y operaciones de suma/multiplicación.
- **Lectura/escritura fuera de límites:** el índice o longitud excede el objeto. La escritura puede corromper memoria; la lectura puede exponer datos o fallar.
- **Use-after-free y double free:** se usa una referencia después de liberar el objeto, o se libera dos veces. Seguí el ciclo de vida y la propiedad de cada recurso.
- **Format string:** una entrada controlada se usa como formato; separá datos y cadena de formato.
- **Condiciones de carrera:** el estado cambia entre la comprobación y el uso; buscá sincronización y propiedad compartida.

La meta del curso es localizar la condición en código propio, reproducirla de forma inocua, explicar el impacto y corregir la causa. No se construyen payloads ni se convierten estos ejemplos en explotación.

## Mitigaciones

| Mitigación | Qué hace | Cómo se ve |
|---|---|---|
| **Stack canary** | Coloca un valor aleatorio antes del return address; si cambió, aborta | `__security_cookie`, `__stack_chk_fail` |
| **NX / DEP** | Marca el stack como no ejecutable | Página sin permiso `X` |
| **ASLR (`/DYNAMICBASE`)** | Aleatoriza la base de las imágenes | Direcciones distintas en cada ejecución |
| **SafeSEH / SEHOP** | Protege la cadena de manejadores SEH (32 bits) | Valida que el handler sea legítimo |
| **CFG (`/guard:cf`)** | Valida los destinos de llamadas indirectas | Chequeo antes de un `call` indirecto |
| **CET / Shadow Stack** | Protege la dirección de retorno por hardware | Aborta si el return address fue alterado |

El capítulo 15 muestra el **security cookie** de MSVC: el compilador guarda un valor calculado con XOR contra `RSP` y lo verifica antes de retornar. Si el buffer lo pisa, la verificación falla y el programa termina ({{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_15 Ejercicio 2 - Análisis estático_15 Ejercicio 2 - Análisis estático.txt|Reversing desde cero, cap. 15}}, 00:07:34–00:08:00).

ASLR se explica en el capítulo 26b: si la imagen se mueve, las direcciones absolutas dejan de ser predecibles ({{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_26b ASLR_26b ASLR.txt|Reversing desde cero, cap. 26b}}, 00:01:53–00:02:30).

## Excepciones y explotación: el caso histórico de SEH

En Windows de 32 bits, los manejadores de excepciones se encadenan en el stack y `FS:[0]` apunta al primero (cap. 16b, 00:02:29). Durante años, los desbordes de stack se usaron para sobrescribir esa cadena y redirigir el flujo cuando se producía una excepción.

En 64 bits, esa información se movió a tablas `.pdata`/`.rdata` y ya no está en el stack (cap. 36, 00:00:27). Es un ejemplo de cómo una mitigación cambia el panorama: el mismo defecto (escribir de más) tiene consecuencias distintas según el soporte de excepciones.

El capítulo 21 abre la estructura por dentro. En el prólogo de una función con `try/except`, el compilador arma en el stack un **registro de excepción** de cuatro campos: `next` (apunta al manejador anterior, el que estaba en `FS:[0]`), `exception handler` (la función de Windows que atiende la excepción), un puntero a una **scopetable** en `.data` y el `try level`. Luego instala el nuevo manejador con `mov fs:[0], &registro`, encadenándolo. La scopetable guarda los punteros a la **función filtro** y a la **función del `except`**; en compiladores modernos ese puntero va **XOR** con una cookie para que no se pueda falsificar trivialmente. Cuando ocurre la excepción, el handler desofusca la scopetable, llama primero al **filtro** —que inspecciona el código de la excepción vía `EXCEPTION_POINTERS → ExceptionRecord.ExceptionCode` (por ejemplo `0xC0000005` acceso inválido, `0xC0000094` división por cero, `0x80000003` breakpoint)— y, según devuelva 1 o 0, ejecuta o no el bloque `except` ({{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_21 Excepciones 2_21 Excepciones 2.txt|Reversing desde cero, cap. 21}}; transcripción .txt, sin marcas de tiempo).

Ese mismo `EXCEPTION_POINTERS` tiene un `ContextRecord` con los registros al momento de la excepción, incluidos `DR0`–`DR3`. Por eso un programa puede usar una excepción no solo para controlar el flujo, sino para **detectar breakpoints de hardware** (ver la lección del debugger). Entender la estructura sirve para análisis defensivo, no para construir un exploit.

Para el curso, lo relevante es entender **por qué** el diseño cambió y cómo se detecta, no cómo se explotaba.

## ROP en una frase

**ROP** (*Return-Oriented Programming*) encadena fragmentos de código existente ("gadgets") que terminan en `ret`, para hacer operaciones sin inyectar código nuevo. Funciona porque reutiliza bytes que ya están en la imagen ejecutable. **NX** no lo detiene y **ASLR** lo complica (no sabés dónde están los gadgets). La mitigación más **directa** contra las cadenas basadas en `ret` es **CET / shadow stack**, que protege la dirección de retorno por hardware. **CFG** apunta a otra cosa: valida los destinos de **llamadas indirectas** (más relevante para variantes tipo COP/JOP que para el ROP clásico de `ret`).

No vas a construir una cadena ROP en esta guía. Vas a entender por qué existen las mitigaciones y por qué "el stack no es ejecutable" no alcanza.

:::{nota} En el Curso IDA: las mitigaciones "en acción" (y qué cambió desde entonces)
Los tutes 29–48 del Curso IDA recorren estas mismas mitigaciones con ejemplos concretos: analizan un **CVE real por patch-diffing** (VLC, CVE-2008-4654; tutes 29–31), compilan un programa **con y sin DEP** (`SetProcessDEPPolicy`) para comparar (34–37), muestran el **canary** y el **SEH overwrite** (38–39) y el manejo de **heap/LFH** (41–48), todo con **WinDbg + IDA + Mona**.

Sirven en clave defensiva —entender el defecto y por qué cada mitigación lo frena—, pero **las recetas de explotación están datadas**: son de **Windows 7 / 32 bits (2016–2018)** y en Windows 10/11 x64 muchas ya no funcionan tal cual, porque se sumaron **CFG**, **CET/shadow stack**, **SEHOP** y un heap más endurecido (los propios tutes avisan que el "shellcode universal" puede no andar en Win10). Tomalos como **historia y concepto**, no como guía de explotación actual ([Curso IDA · tutes 29–48](../ida_tutes/29.html)).
:::

## Ejemplo paso a paso: ver la mitigación en tu programa

1. Compilá el programa del buffer **sin** canary (MSVC desactivando `/GS`):

```bat
cl /Od /GS- vuln.c
```

2. Ejecutalo con una entrada corta: funciona.
3. Ejecutalo con una entrada larga (por ejemplo, 40 caracteres) dentro de la VM: probablemente crashea. Anotá el mensaje.
4. Compilá **con** canary (`/GS`, que en MSVC está activo por defecto):

```bat
cl /Od /GS vuln.c
```

5. Repetí la entrada larga. Ahora el programa aborta con *buffer overrun detected* (MSVC llama a `__report_gsfailure`).
6. Mirá las mitigaciones de cada `.exe` con un visor de PE o con `dumpbin /headers /loadconfig vuln.exe` y compará (`/GS`, `/DYNAMICBASE`, `/NXCOMPAT`, `/guard:cf`).

**Qué observaste:** el canary convierte una escritura silenciosa en una detección. No arregla el defecto (el `strcpy` sigue sin validar), pero impide que el return address se use.

## Cómo se arregla el defecto

| Mal | Bien |
|---|---|
| `strcpy(buffer, entrada)` | `strncpy(buffer, entrada, sizeof(buffer)-1)` y terminador |
| `sprintf(buffer, ...)` | `snprintf(buffer, sizeof(buffer), ...)` |
| `gets(buffer)` | `fgets(buffer, sizeof(buffer), stdin)` |
| Confiar en el largo de la entrada | Validar antes de copiar |

La mitigación no reemplaza la corrección: un programa con canary y `strcpy` sigue teniendo un defecto. El canary solo hace más difícil aprovecharlo.

:::{nota} En el Curso IDA: decidir si algo es vulnerable, y leer un parche con un *differ*
El Curso IDA entra al tema de forma didáctica y **defensiva**: define qué es una vulnerabilidad y propone un ejercicio de *"¿vulnerable o no?"* donde tenés el **código fuente, el IDB y el ejecutable**, y lo analizás estáticamente en IDA antes de concluir. También presenta los ***differs***: herramientas que comparan **dos versiones consecutivas** de un programa y marcan qué funciones cambiaron —por ejemplo, para ver **qué arregló un parche de seguridad** (la base del análisis de parches / 1-day, en clave defensiva). Identificar el defecto no es construir el exploit ([Curso IDA · tute 20, Qué es una vulnerabilidad](../ida_tutes/20.html); [tute 21, ¿Vulnerable o no?](../ida_tutes/21.html); [tute 22, Differ](../ida_tutes/22.html)).
:::

## Divulgación responsable

Si encontrás una vulnerabilidad en un programa que tenés permiso de analizar:

1. Confirmá el impacto y la versión afectada.
2. Escribí un reporte privado con pasos mínimos de reproducción.
3. Contactá al proveedor y guardá la evidencia.
4. Acordá un plazo (por ejemplo, 90 días) antes de publicar.
5. No accedas a datos de terceros ni dejes el sistema en un estado inseguro.
6. Publicá solo cuando el proveedor haya tenido tiempo de corregir, o según el acuerdo.

## Práctica

1. Escribí `vuln.c` con un buffer de 16 bytes y `strcpy`.
2. Compilalo con y sin canary. Ejecutá entradas de 8, 16, 24 y 40 caracteres en la VM. Anotá qué pasa.
3. Mirá las mitigaciones de las dos versiones con `dumpbin /headers /loadconfig` o un visor de PE y explicá cada una.
4. Corregí el programa con una copia **acotada y con terminador explícito** (`strncpy` + poner el `\0` final, o `strcpy_s`) y verificá que la entrada larga ya no rompe.
5. Escribí un informe de dos páginas: defecto, impacto, mitigación, corrección y límites. Sin exploit.

## Preguntas de repaso

**1. ¿Qué es un desborde de buffer?**
Escribir más datos de los que entran en un buffer, pisando memoria adyacente.

**2. ¿Qué protege el stack canary?**
Detecta si se modificó el valor colocado antes del return address. Si cambió, aborta antes de retornar.

**3. ¿NX impide ejecutar código en el stack?**
Sí, marca las páginas del stack como no ejecutables. No impide el desborde ni la sobrescritura de punteros.

**4. ¿ASLR alcanza para proteger un programa?**
No. Complica la predicción de direcciones, pero un defecto sigue siendo explotable si se filtra una dirección o si el atacante puede reintentar.

**5. ¿Qué diferencia hay entre mitigar y corregir?**
Mitigar reduce el impacto; corregir elimina la causa. Un canary mitiga un `strcpy` inseguro; la corrección es usar una copia **acotada y bien terminada** —validar el tamaño y garantizar el `\0` final (p. ej. `strncpy` **más terminación explícita**, o `strcpy_s`/`strlcpy`)—. `strncpy` a secas no alcanza: puede dejar la cadena **sin terminador** y no valida que la entrada tenga sentido.

**6. ¿Qué se hace al encontrar una vulnerabilidad?**
Documentarla, reportarla en privado, no publicar el exploit y acordar un plazo de divulgación.

## Antes de avanzar

Tenés que poder:

- Explicar el defecto con el dibujo del stack.
- Nombrar cuatro mitigaciones y qué frena cada una.
- Compilar con y sin canary y observar la diferencia.
- Escribir un informe sin exploit.

:::{nota} Puerta de salida
Si podés explicar por qué el canary detecta el desborde y por qué no corrige el `strcpy`, la rama está aprobada. Si tu objetivo es "hacer que funcione el exploit", estás en el lugar equivocado.
:::

## Fuentes de esta lección

- MITRE CWE: [Out-of-bounds Write (CWE-787)](https://cwe.mitre.org/data/definitions/787.html), [Integer Overflow or Wraparound (CWE-190)](https://cwe.mitre.org/data/definitions/190.html), [Use After Free (CWE-416)](https://cwe.mitre.org/data/definitions/416.html).

- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_15 Ejercicio 2 - Análisis estático_15 Ejercicio 2 - Análisis estático.txt|Reversing desde cero, cap. 15}} — security cookie.
- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_16b Apéndice teórico 2 - Excepciones 1_16b Apéndice teórico 2 - Excepciones 1.txt|Reversing desde cero, cap. 16b}} — SEH en 32 bits.
- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_21 Excepciones 2_21 Excepciones 2.txt|Reversing desde cero, cap. 21}} — estructura SEH (registro, scopetable, filtro y handler), códigos de excepción y `ContextRecord` (se omite la parte de keygen).
- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_36 Excepciones en 64 bits_36 Excepciones en 64 bits.txt|Reversing desde cero, cap. 36}} — SEH basado en tablas en 64 bits.
- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_26b ASLR_26b ASLR.txt|Reversing desde cero, cap. 26b}} — ASLR.
- {{src:CLS_fuentes_externas/github/apuromafo_Crackslatinos/EXPLOITING|EXPLOITING (contenedor)}} — **pendiente de revisar**: no se extrajo ni se leyó.
- [Curso IDA · tutes 20–22](../ida_tutes/20.html) — qué es una vulnerabilidad, el ejercicio "¿vulnerable o no?" (fuente + IDB + binario) y los *differs* para leer qué cambió un parche (defensivo).
- [Curso IDA · tutes 29–48](../ida_tutes/29.html) — las mitigaciones en ejemplos (VLC/CVE-2008-4654, DEP, canary/SEH, heap) con WinDbg/IDA/Mona; recetas de Windows 7 / 32 bits, **históricas**: en Windows moderno cambian CFG, CET y SEHOP.

:::{nota} Capas de esta lección
**Contenido observado en CLS:** la cookie del capítulo 15, el SEH de los capítulos 16b y 36, y ASLR del 26b. **Conocimiento externo:** desbordes, overflow de enteros, acceso fuera de límites, use-after-free, double free, format string, carreras, mitigaciones, ROP y divulgación. **Recomendación editorial:** el ejemplo `vuln.c` y el límite explícito sobre exploits.
:::

