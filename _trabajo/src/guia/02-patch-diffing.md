---
title: "2.20 · Patch diffing y CVE: leer qué cambió"
description: "Comparar dos versiones de un binario con BinDiff, Diaphora o Ghidra Version Tracking para ver qué arregló un parche —primero en un programa propio, después un CVE público—, separar el ruido del cambio real y usar símbolos públicos, en clave defensiva."
etapa: "Etapa 2 · Windows avanzado (2C)"
---

# Patch diffing y CVE: leer qué cambió

:::{nota} Objetivo de la lección
Comparar **dos versiones** de un binario y entender **qué cambió un parche** y qué riesgo mitiga, sin convertirlo en una práctica de explotación. **Prerrequisitos:** IDA (2.7) y el differ mencionado en flujo (2.4). *Contexto recomendado (no bloqueante):* la rama de vulnerabilidades (5.2) — 2C es la continuación natural de 2B y no exige haber hecho la Etapa 5.
:::

## Qué es un differ

Un **differ** toma dos versiones consecutivas de un programa y **empareja** (matchea) sus funciones a pesar de los cambios, para mostrarte **cuáles cambiaron y dónde**. El tute 22 del Curso IDA lo define así y aclara el caso que nos importa: esos cambios pueden ser **un parche de seguridad** que corrige una vulnerabilidad ({{src:CLS_Guia/_trabajo/extraido_ida/22-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|Curso IDA, tute 22}}). Las herramientas estándar (**conocimiento externo**) son **BinDiff** y **Diaphora**: emparejan por estructura del grafo, hashes de instrucciones, llamadas y nombres, y te dan un porcentaje de similitud por función.

Por qué es **defensivo**: comparar la versión vulnerable con la parcheada te dice **qué chequeo agregaron**, es decir, cuál era el defecto. Es la base del análisis de **1-day** (entender una falla ya corregida) y de verificar que un parche realmente arregla lo que dice. Identificar el cambio **no** es construir el exploit.

## El flujo

1. **Conseguí las dos versiones** (antes y después del parche) de un binario que tengas derecho a analizar.
2. **Analizá cada una** en IDA/Ghidra y exportá para el differ.
3. **Corré el differ**: ordená por "más cambiadas / menos similares". Las funciones con 100% de match no te interesan; mirá las que bajaron.
4. **Leé el cambio**: casi siempre es un **chequeo agregado** (una comparación de tamaño, un `if` nuevo antes de un `memcpy`).
5. **Redactá** qué cambió y qué riesgo mitiga, para tu informe.

## El caso real del curso: VLC (CVE-2008-4654)

El Curso IDA toma un **CVE público** y lo trabaja como diff de **dos versiones consecutivas de VLC**, usando el número de CVE como guía de qué buscar ({{src:CLS_Guia/_trabajo/extraido_ida/30-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|Curso IDA, tute 30}}; explicación en el [tute 31](../ida_tutes/31.html)). El objetivo acá es **entender el defecto y el arreglo** (qué validación faltaba), no desarrollar un exploit; la [rama de vulnerabilidades](05-vulnerabilidades.html) ya enmarca esto en clave defensiva.

## Ejemplo paso a paso: una función antes y después del parche

*(Ejemplo **ilustrativo**: pseudo-C construido para mostrar qué resalta un differ.)*

BinDiff marca `leer_registro` con **82%** de similitud (bajó): algo cambió. Abrís las dos:

```c
// versión vulnerable                 // versión parcheada
int leer_registro(FILE *f) {          int leer_registro(FILE *f) {
  char buf[64];                         char buf[64];
  int n = leer_u16(f);                  int n = leer_u16(f);
                                        if (n > sizeof(buf))        // <-- chequeo AGREGADO
                                            return -1;
  fread(buf, 1, n, f);                  fread(buf, 1, n, f);
  ...                                   ...
}
```

El diff resalta el bloque nuevo: un `if (n > sizeof(buf)) return -1` antes del `fread`. Conclusión para el informe: **el defecto era un overflow de stack** (se leían `n` bytes controlados por el archivo en un buffer de 64 sin validar `n`); **el parche agrega la validación de tamaño**. Eso es todo lo que esta lección busca: leer el cambio, nombrar el riesgo.

## Cómo empareja un differ, y dónde se equivoca

Saber cómo trabaja la herramienta te dice cuándo creerle (**conocimiento externo**). **BinDiff** es hoy de código abierto y trabaja sobre exportaciones en formato **BinExport**, que se generan desde IDA, Binary Ninja o Ghidra; **Diaphora** corre como script dentro de IDA. Los dos siguen la misma lógica general:

1. Empiezan por las coincidencias **más seguras**: mismo nombre (si hay símbolos), mismos bytes o el mismo hash de instrucciones.
2. Siguen con atributos **estructurales**: cantidad de bloques y aristas del grafo, llamadas que hace y recibe la función, constantes y cadenas que usa.
3. **Propagan**: si `A` coincide con `A'`, las funciones que `A` llama probablemente coincidan con las que llama `A'`.

Cada par queda con una **similitud** (cuánto se parecen) y una **confianza** (qué tan seguro está el emparejamiento). Una similitud baja con confianza alta es lo que buscás: la misma función, cambiada. Donde se equivoca: funciones **chicas** y parecidas entre sí (envoltorios, *thunks*, métodos triviales) que se emparejan mal; funciones que el compilador **inlineó** en una versión y no en la otra, y que "desaparecen"; y código **reordenado** que cambia el grafo sin cambiar la lógica.

## Separar el ruido del parche

En un diff real, la mayoría de las funciones que cambiaron **no** son el parche. Fuentes típicas de ruido:

| Ruido | Cómo se ve | Cómo descartarlo |
|---|---|---|
| Otra versión del compilador o del enlazador | Cientos de funciones con cambios menores | El cambio está repartido en todo el binario, no concentrado |
| Otras opciones de optimización | Mismos bloques en otro orden, registros distintos | El grafo cambia pero las llamadas y constantes son las mismas |
| Direcciones y constantes de enlace | Solo cambian inmediatos que son direcciones | Ignorar diferencias en offsets a datos |
| Bibliotecas actualizadas | Cambios en funciones del runtime | Mirar primero el código propio del programa |

La señal del parche suele ser otra: **un bloque nuevo** con una comparación y una salida temprana, una llamada nueva a una función de validación o una API "segura" en lugar de la anterior (por ejemplo, una variante con tamaño explícito). Mirar también el **diff de imports** ayuda: una función nueva importada a veces nombra el arreglo.

## Símbolos públicos: nombres para los binarios de Windows

Para diffear binarios de Windows, Microsoft publica **símbolos públicos** en su servidor de símbolos: el debugger o la herramienta de análisis los descarga según la versión exacta del binario. Traen nombres de funciones y variables globales, no el código fuente ni los tipos privados. Con nombres en las dos versiones, el emparejamiento mejora mucho y el informe puede decir "cambió `FuncionX`" en lugar de "cambió `sub_180012340`". La ruta de símbolos que combina el servidor público de Microsoft con tus propios PDB se arma igual que en la depuración de kernel de [6.3](6-03-debug-kernel.html); IDA y Ghidra también pueden descargarlos.

## Ghidra Version Tracking como alternativa

**Version Tracking** de Ghidra ([2.16](02-ghidra.html)) hace un trabajo parecido con otro enfoque: corrés **correlacionadores** (bytes exactos, instrucciones exactas, mismas referencias a datos, mismos símbolos, y otros más permisivos), revisás las coincidencias propuestas, las **aceptás** y trasladás nombres y comentarios del origen al destino. Lo que queda sin aceptar es el candidato a cambio. Es más manual que BinDiff, pero todo queda dentro de un solo proyecto y no necesita IDA.

## Práctica

En tu VM:

1. Compilá un programa **propio** con un bug simple (un `fread`/`memcpy` sin validar tamaño). Guardá el binario **"v1"**.
2. Arreglalo (agregá la validación) y compilá **"v2"**.
3. Corré **BinDiff** o **Diaphora** entre v1 y v2; ordená por menor similitud.
4. Abrí la función que cambió y escribí dos líneas: **qué** cambió y **qué riesgo** mitiga.
5. Compilá una **v2b** con el mismo arreglo pero otra opción de optimización (por ejemplo `/O1` en lugar de `/O2`). Diffeá v1 contra v2b, contá cuántas funciones cambiaron y explicá cuáles son ruido y cuál es el parche.
6. Repetí el diff v1/v2 con **Version Tracking** de Ghidra y compará con el resultado de BinDiff o Diaphora: ¿encontraron la misma función?

## Preguntas de repaso

?? ¿Qué hace un differ y para qué sirve en defensa?
!! Empareja las funciones de **dos versiones** de un binario y marca las que cambiaron. En defensa sirve para ver **qué arregló un parche** (qué chequeo agregaron = cuál era el defecto): análisis de 1-day y verificación de parches.

?? Al correr BinDiff, ¿qué funciones mirás?
!! Las de **menor similitud** (las que cambiaron). Las que matchean al 100% no aportan; el parche está en las que bajaron.

?? En el ejemplo, ¿cuál era el defecto y cuál el arreglo?
!! El defecto: leer `n` bytes (controlados por el archivo) en un buffer de 64 **sin validar** `n` → overflow de stack. El arreglo: un `if (n > sizeof(buf)) return -1` antes del `fread`.

?? ¿Qué aporta el número de CVE al hacer el diff de VLC?
!! Es una **guía**: te dice qué clase de falla y en qué zona buscar, para no comparar a ciegas las dos versiones.

?? En un diff, ¿qué combinación de similitud y confianza buscás?
!! Similitud **baja** con confianza **alta**: el differ está seguro de que es la misma función y de que cambió. Similitud baja con confianza baja puede ser un mal emparejamiento.

?? Diffeaste dos versiones y cambiaron trescientas funciones. ¿Qué hacés?
!! Separar el ruido: cambios repartidos por todo el binario suelen ser otra versión del compilador u otras optimizaciones. Buscás el cambio concentrado: un bloque nuevo con comparación y salida temprana, una validación nueva o un import nuevo.

?? ¿Qué aportan los símbolos públicos de Microsoft al diffear binarios de Windows?
!! Nombres de funciones y variables globales en las dos versiones: mejoran el emparejamiento y permiten describir el cambio por nombre. No incluyen código fuente ni tipos privados.

?? ¿Dónde está el límite de esta lección?
!! En **leer el cambio y nombrar el riesgo**. Identificar el defecto no es construir el exploit; eso queda fuera (la guía es defensiva).

:::{nota} Puerta de salida
Podés: (1) explicar qué es un differ y por qué es defensivo; (2) correr BinDiff/Diaphora entre dos versiones propias y encontrar la función cambiada; (3) leer el chequeo agregado y nombrar el defecto que mitiga; (4) explicar el rol del CVE en el caso VLC; (5) explicar cómo empareja un differ y en qué casos se equivoca; (6) separar el ruido de compilación del cambio real; (7) usar símbolos públicos o Version Tracking para mejorar el diff.
:::

:::{nota} Lo que queda fuera
El diff de parches mensuales completos de Windows, la extracción de archivos de los paquetes de actualización, el diff de controladores de kernel y, por el marco del curso, cualquier paso desde "entendí el defecto" hacia "construí un exploit".
:::

## Fuentes de esta lección

- {{src:CLS_Guia/_trabajo/extraido_ida/22-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|Curso IDA, tute 22}} — qué es un differ; empareja funciones entre versiones; el caso del parche de seguridad.
- {{src:CLS_Guia/_trabajo/extraido_ida/30-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|Curso IDA, tute 30}} — VLC / CVE-2008-4654 como diff de dos versiones (explicación en el tute 31).
- [Rama vulnerabilidades](05-vulnerabilidades.html) (5.2) — el marco defensivo del defecto y las mitigaciones.
- Conocimiento externo: [BinDiff](https://github.com/google/bindiff) (código abierto; trabaja sobre BinExport desde IDA, Binary Ninja o Ghidra), [Diaphora](https://github.com/joxeankoret/diaphora), [Ghidra Version Tracking](https://ghidra.re/ghidra_docs/GhidraClass/Intermediate/VersionTracking.html) y Microsoft Learn: [Microsoft public symbols](https://learn.microsoft.com/en-us/windows-hardware/drivers/debugger/microsoft-public-symbols).

:::{nota} Capas de esta lección
**Contenido observado en CLS:** la definición de differ del capítulo 22 y el caso VLC/CVE de los tutes 30–31. **Conocimiento externo:** BinDiff, Diaphora y Version Tracking, cómo emparejan funciones, el ruido de compilación y los símbolos públicos de Microsoft. **Recomendación editorial:** el ejemplo ilustrativo, la tabla de ruido, el flujo de 1-day defensivo y la práctica con dos versiones propias (sin laboratorio compilado con hashes en esta edición).
:::
