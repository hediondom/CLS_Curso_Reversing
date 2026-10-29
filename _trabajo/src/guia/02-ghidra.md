---
title: "2.16 · Ghidra (y Cutter): la alternativa libre, con práctica"
description: "Analizar el mismo binario que en IDA, pero en Ghidra: proyecto, autoanálisis, strings y referencias, tipos y estructuras, decompilador, scripting y modo headless — y Cutter/radare2 como opción."
etapa: "Etapa 2 · Windows intermedio"
---

# Ghidra (y Cutter): la alternativa libre, con práctica

:::{nota} Objetivo de la lección
Hacer en **Ghidra** el mismo recorrido que hiciste en IDA, para no depender de una sola herramienta: importar, dejar que autoanalice, seguir strings y referencias, corregir tipos, leer el decompilador y documentar. **Prerrequisitos:** [IDA y el análisis estático](02-ida.html) (2.7), estructuras (2.7).
:::

:::{aviso} Herramienta externa al corpus
El curso CLS enseña con IDA, OllyDbg y x64dbg; **Ghidra y radare2 no son material de CLS**, así que esta lección es **conocimiento externo**. En el corpus hay, sin revisar, una copia de **Ghidra 11.3.2** y una carpeta **RADARE** (en `CLS_fuentes_externas/links_chat` y `.../RADARE`); igual conviene **descargar Ghidra del sitio oficial** y verificar el hash antes de usarlo.
:::

## Por qué una segunda herramienta

Ghidra es gratis y open source (NSA), trae **decompilador** integrado y corre en cualquier sistema. Saber leer el mismo binario en IDA **y** en Ghidra te da dos ventajas: cuando una decompila mal una función, la otra suele aclararla; y no quedás atado a una licencia. Cutter (la GUI de **radare2**) es otra opción libre, más liviana.

## El recorrido equivalente al de IDA

1. **Proyecto e import.** Ghidra trabaja con un *project* que contiene uno o varios binarios. `File → Import File`, elegí el `.exe`; Ghidra detecta el formato PE y el procesador.
2. **Autoanálisis.** Al abrirlo por primera vez, ofrece correr los *analyzers*: dejalos con la opción por defecto la primera vez. Son el equivalente al análisis inicial de IDA (arma funciones, resuelve referencias, nombra imports).
3. **Navegación.** Las ventanas clave: **Symbol Tree** (funciones, imports, exports), **Defined Strings** (el equivalente a las strings de IDA), **Listing** (el desensamblado) y **Decompile** (el pseudo-C, como Hex-Rays).
4. **Seguir el hilo.** Doble clic en una string te lleva a su uso; clic derecho → **References → Show References to** es el `X` (xrefs) de IDA. Con eso llegás a la lógica igual que en 2.7.
5. **Corregir tipos.** En el decompilador, clic derecho → **Retype Variable** y **Rename Variable/Function**; para estructuras, el **Data Type Manager**. Es el `T`/renombrado de IDA: cada tipo que corregís hace el pseudo-C más legible.
6. **Documentar.** Comentarios (`;`), *bookmarks* y renombrado quedan en el proyecto. Exportá un resumen de hallazgos para tu informe (Etapa 4).

## Tipos y estructuras: donde Ghidra más mejora el pseudo-C

El decompilador es tan bueno como los tipos que le das. Tres herramientas cubren casi todo (**conocimiento externo**, guías de Ghidra):

- **Data Type Manager.** Ventana con los tipos del programa y los **archivos de tipos** (`.gdt`) que trae Ghidra; para un PE aplica automáticamente los de Windows, por eso `CreateFileW` ya aparece con sus parámetros. Ahí creás estructuras a mano (*New → Structure*) con los campos que dedujiste, como en [IDA y el análisis estático](02-ida.html).
- **Auto Create Structure.** En el decompilador, clic derecho sobre una variable que es un puntero → *Auto Create Structure*: Ghidra mira los accesos `[ptr+N]` de la función y arma una estructura con un campo por offset. Es un punto de partida, no el resultado: renombrá los campos y corregí tamaños cuando sepas qué son.
- **Parse C Source.** Si tenés el encabezado `.h` de tu propio programa (o la definición de una estructura documentada), *File → Parse C Source* lo convierte en tipos de Ghidra. Es lo que más rápido transforma un listado de `param_1 + 0x18` en `ctx->contador`.

Regla de trabajo: cada vez que el pseudo-C muestra aritmética de punteros sobre la misma variable, hay una estructura sin declarar.

## Scripting y modo headless

Ghidra expone toda su API para scripts en **Java** y **Python** (Jython en el *Script Manager* y, en versiones recientes, también CPython mediante PyGhidra). Es el equivalente a IDAPython de la [Etapa 5](05-automatizacion.html). Dentro de un script, `currentProgram` es el programa abierto y hay funciones de conveniencia de la API "plana" (*FlatProgramAPI*), como `getReferencesTo(direccion)`.

*(Ejemplo **ilustrativo**, no ejecutado en esta edición: listar las veinte funciones sin nombre más grandes, para decidir por dónde empezar.)*

```python
# Ghidra, Script Manager (Python): funciones FUN_ ordenadas por tamaño
fm = currentProgram.getFunctionManager()
sin_nombre = [f for f in fm.getFunctions(True) if f.getName().startswith("FUN_")]
sin_nombre.sort(key=lambda f: f.getBody().getNumAddresses(), reverse=True)
for f in sin_nombre[:20]:
    print(f.getEntryPoint(), f.getName(), f.getBody().getNumAddresses())
```

El **modo headless** corre el autoanálisis y los scripts sin interfaz, para procesar varios binarios en lote o repetir un análisis exactamente igual:

```text
analyzeHeadless C:\proyectos_ghidra LabCLS -import hola.exe -postScript listar_fun.py
```

Eso deja el resultado del script en la salida de consola y el binario analizado en el proyecto, que es evidencia reproducible.

## Version Tracking: llevar el trabajo de una versión a otra

Si ya renombraste y comentaste la versión 1 de un programa y aparece la versión 2, no hace falta empezar de cero. **Version Tracking** compara dos programas (origen y destino), busca funciones y datos que se corresponden con distintos **correlacionadores** (bytes idénticos, mismo código con otras direcciones, mismas referencias, mismos símbolos) y te deja **aceptar** cada coincidencia y **trasladar** al destino nombres, comentarios y tipos. Lo que queda sin correspondencia es justamente lo que cambió. Se usa a fondo en [2.20 Patch diffing](02-patch-diffing.html); acá alcanza con saber que existe.

## Ejemplo paso a paso: la misma función en IDA y en Ghidra

*(Ejemplo **ilustrativo**: pseudo-C representativo de los dos decompiladores.)*

La misma rutina de chequeo, decompilada por cada herramienta antes de renombrar:

```c
// IDA (Hex-Rays)                      // Ghidra
int sub_401050(char *a1) {             undefined4 FUN_00401050(char *param_1) {
  if ( strlen(a1) != 6 )                 size_t sVar1 = strlen(param_1);
    return 0;                            if (sVar1 != 6) return 0;
  return strcmp(a1, "s3cr3t") == 0;      iVar2 = strcmp(param_1,"s3cr3t");
}                                        return (uint)(iVar2 == 0);
                                       }
```

Dicen lo mismo con otra prosa: la longitud debe ser 6 y el texto `"s3cr3t"`. Dónde **conviene comparar**: a veces Ghidra resuelve mejor una `switch` o una estructura que Hex-Rays enreda (y al revés). Después de **renombrar** (`FUN_00401050` → `check`, `param_1` → `clave`) y **tipar**, el pseudo-C de Ghidra queda tan legible como el de IDA:

```c
bool check(char *clave) {
  if (strlen(clave) != 6) return false;
  return strcmp(clave, "s3cr3t") == 0;
}
```

## Práctica

En tu VM, con el **mismo crackme** que analizaste en IDA (ver [Banco de prácticas](../practicas.html)):

1. Importalo en un proyecto de Ghidra y corré el autoanálisis.
2. Encontrá la misma string clave que usaste en IDA y llegá, por referencias, a la función de decisión.
3. Leé la función en el **decompilador**; renombrá dos variables y confirmá que el pseudo-C mejora.
4. Compará lado a lado con la vista de IDA: ¿coincide el decompilado? ¿Alguna lo hace más claro?
5. (Opcional) Abrí el mismo binario en **Cutter** y repetí el paso 2.
6. Elegí una función de tu programa que reciba un puntero a estructura. Usá *Auto Create Structure*, renombrá los campos y compará el pseudo-C antes y después; si tenés el `.h`, importalo con *Parse C Source* y compará con la estructura automática.
7. Corré el script de ejemplo desde el *Script Manager* y después en modo headless sobre el mismo binario. Guardá la salida como evidencia.

## Preguntas de repaso

?? ¿Qué ventaja concreta da leer el mismo binario en IDA y en Ghidra?
!! Que cuando una **decompila mal** una función, la otra suele aclararla; además no dependés de una licencia. Son dos lecturas del mismo código.

?? ¿Cuál es el equivalente en Ghidra de las "strings" y de los "xrefs" de IDA?
!! **Defined Strings** para las cadenas y **References → Show References to** (clic derecho) para los xrefs.

?? ¿Qué hacés la primera vez que abrís un binario en Ghidra?
!! Dejar correr el **autoanálisis** con la opción por defecto: arma funciones, resuelve referencias y nombra imports, como el análisis inicial de IDA.

?? ¿Cómo mejorás el decompilado de una función?
!! **Renombrando** variables/funciones y **corrigiendo tipos** (Retype Variable, Data Type Manager); cada corrección hace el pseudo-C más legible, igual que `T`/rename en IDA.

?? ¿Qué hace *Auto Create Structure* y por qué no es el resultado final?
!! Crea una estructura con un campo por cada offset que la función usa sobre ese puntero. Es un borrador: no conoce los nombres ni el tamaño total, y puede faltarle campos que solo se usan en otras funciones.

?? ¿Para qué sirve el modo headless?
!! Para correr el autoanálisis y scripts sin interfaz: procesar varios binarios en lote o repetir el mismo análisis exactamente igual, lo que lo vuelve reproducible.

?? ¿Qué te ahorra Version Tracking cuando aparece una versión nueva del programa?
!! Rehacer el trabajo: encuentra las funciones correspondientes y traslada nombres, comentarios y tipos; lo que queda sin correspondencia es lo que cambió.

?? ¿Por qué conviene bajar Ghidra del sitio oficial aunque haya una copia en el corpus?
!! Porque la copia del corpus **no está revisada**; del sitio oficial, verificando el hash, tenés garantía de integridad. Es la misma precaución que con cualquier herramienta.

:::{nota} Puerta de salida
Podés: (1) importar y autoanalizar un binario en Ghidra; (2) llegar a la función de decisión por strings y referencias; (3) mejorar el decompilado renombrando y tipando; (4) comparar la lectura de IDA y Ghidra del mismo binario; (5) crear y aplicar una estructura con el Data Type Manager o *Auto Create Structure*; (6) correr un script propio desde el *Script Manager* y en modo headless. Con esto cerrás el bloque **2B · Windows intermedio**.
:::

:::{nota} Lo que queda fuera
Escribir analizadores o extensiones de Ghidra, el lenguaje de especificación de procesadores (SLEIGH), el trabajo colaborativo con Ghidra Server y la depuración integrada. Son temas de uso avanzado de la herramienta, no de método.
:::

## Fuentes de esta lección

- **Conocimiento externo:** Ghidra (proyecto NSA) y su decompilador; recorrido equivalente al de IDA. Guías oficiales: [Ghidra class · Beginner](https://ghidra.re/ghidra_docs/GhidraClass/Beginner/Introduction_to_Ghidra_Student_Guide.html) e [Intermediate](https://ghidra.re/ghidra_docs/GhidraClass/Intermediate/Intermediate_Ghidra_Student_Guide.html).
- En el corpus (sin revisar): copia de **Ghidra 11.3.2** y carpeta **RADARE** en `CLS_fuentes_externas`. No se usaron como fuente; se mencionan por completitud.
- [IDA y el análisis estático](02-ida.html) (2.7) — el recorrido que esta lección replica en otra herramienta.
- Ghidra (conocimiento externo): [Improving Disassembly and Decompilation](https://ghidra.re/ghidra_docs/GhidraClass/Advanced/improvingDisassemblyAndDecompilation.pdf) (presentación en PDF) (tipos y estructuras en el decompilador), [Version Tracking](https://ghidra.re/ghidra_docs/GhidraClass/Intermediate/VersionTracking.html) y [API de Ghidra](https://ghidra.re/ghidra_docs/api/) (`FlatProgramAPI`, `FunctionManager`).

:::{nota} Capas de esta lección
**Contenido observado en CLS:** solo la existencia de Ghidra 11.3.2 y la carpeta RADARE en el corpus (sin revisar). **Conocimiento externo:** todo el manejo de Ghidra/Cutter (tipos, scripting, headless, Version Tracking) y el paralelo con IDA. **Ejemplo ilustrativo:** el pseudo-C comparado, el script de funciones sin nombre y la línea de `analyzeHeadless` (no ejecutados en esta edición). **Recomendación editorial:** el recorrido paso a paso, la comparación lado a lado y la práctica con el mismo crackme.
:::
