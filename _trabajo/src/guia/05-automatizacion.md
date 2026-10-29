---
title: "Etapa 5 · Rama automatización: scripts para no repetir trabajo"
description: "IDAPython, Ghidra y Python standalone para renombrar, buscar patrones y extraer datos de un binario."
etapa: "Etapa 5 · Ramas opcionales"
---

# Rama automatización: scripts para no repetir trabajo

:::{nota} Objetivo de la lección
Al terminar vas a poder escribir un script corto que recorra funciones, busque una constante o liste imports, y decidir cuándo conviene automatizar y cuándo no.
:::

**Prerrequisitos:** etapas 0 a 4, IDA o Ghidra, Python básico. **Duración sugerida:** 4 horas. Estimación aproximada.

## Qué hay en CLS

El curso tiene cuatro capítulos de IDAPython, **leídos e integrados en esta edición**: 22b ("Empezando con IDAPython"), 25 ("Empezando con IDAPython" + guía del entorno), 27b ("Jugando con IDAPython") y 32 ("Un proyecto con IDAPython"). Más abajo, en «Lo que muestra el curso», están los ejemplos observados con su cita. Los ejemplos de esta sección inicial son editoriales (código propio) y los del curso los complementan con la API real.

:::{aviso} Sobre las versiones y la legalidad
Los capítulos usan IDA 7.5 con Python 3. Varios demuestran las técnicas sobre crackmes (incluido parcheo): esta guía toma la **mecánica de IDAPython** (recorrer, buscar, pintar, parchear, revertir) y la practica con **programas propios**, nunca para saltar protecciones de software ajeno.
:::

## Cuándo automatizar

Automatizá cuando:

- La tarea se repite muchas veces (renombrar 200 funciones, buscar una constante en todo el binario).
- La tarea es mecánica y propensa a errores (extraer imports, comparar listas).
- Querés que el análisis sea reproducible (un script se puede volver a correr).

No automaticés cuando:

- Todavía no entendés el problema. Primero hacelo a mano una vez.
- La tarea requiere juicio caso por caso. Un script que renombra "lo que parece" puede empeorar el análisis.
- El script va a modificar el binario sin backup.

## IDAPython: el modelo mental

IDA expone tres módulos principales:

| Módulo | Para qué |
|---|---|
| `idc` | Funciones clásicas: nombres, comentarios, bytes, instrucciones |
| `idautils` | Iteradores: funciones, segmentos, referencias, heads |
| `idaapi` | API de más bajo nivel: eventos, UI, tipos |
| `ida_bytes` | Acceso a bytes y flags |
| `ida_funcs` | Funciones y sus límites |

Un script típico recorre algo y hace una acción por elemento.

### Ejemplo 1: renombrar funciones sin nombre

```python
import idautils
import idc

for ea in idautils.Functions():
    nombre = idc.get_func_name(ea)
    if nombre.startswith("sub_"):
        idc.set_name(ea, f"func_{ea:X}", idc.SN_NOWARN)
```

**Qué hace:** recorre todas las funciones detectadas; si el nombre automático empieza con `sub_`, lo reemplaza por `func_<dirección>`. Es útil para tener nombres estables antes de renombrar a mano las funciones importantes.

### Ejemplo 2: buscar una constante en el código

```python
import idautils
import idc

OBJETIVO = 0x1E0

for seg in idautils.Segments():
    if idc.get_segm_name(seg) != ".text":
        continue
    for ea in idautils.Heads(idc.get_segm_start(seg), idc.get_segm_end(seg)):
        if idc.print_insn_mnem(ea) in ("cmp", "sub", "add"):
            for i in range(3):
                if idc.get_operand_value(ea, i) == OBJETIVO:
                    print(f"{ea:#x}: {idc.generate_disasm_line(ea, 0)}")
```

**Qué hace:** recorre las instrucciones de `.text`; si alguna usa la constante `0x1E0` como operando, imprime la dirección y el texto. En el programa del capítulo 15, esa constante es la que compara el resultado con 480.

:::{aviso} La API cambia entre versiones
`idc.get_operand_value`, `idc.print_insn_mnem` y `idautils.Heads` existen en IDA 7 y 8, pero algunos nombres cambiaron respecto de IDA 6. Si el script falla, revisá la versión y la documentación de IDAPython. La lógica —recorrer y comparar— se mantiene.
:::

### Ejemplo 3: listar imports

```python
import idautils
import idc

for i in range(idc.get_import_module_qty()):
    modulo = idc.get_import_module_name(i)
    print(f"[{modulo}]")
    def callback(ea, nombre, ordinal):
        print(f"  {ea:#x}  {nombre or ordinal}")
        return True
    idc.enum_import_names(i, callback)
```

**Qué hace:** recorre los módulos importados y, por cada uno, enumera sus funciones. Es el equivalente scripteado de la pestaña Imports.

## Lo que muestra el curso

Esta sección resume lo que hacen los cuatro capítulos de IDAPython, con la API real que usan.

### Montar el entorno y probar que anda

El cap. 22b instala **IPyIDA**, una consola de IPython dentro de IDA (se abre con `Shift`+`.`). Tiene autocompletado con `Tab`, historial (`%hist`) y reuso de resultados por número de línea (`_6`). Dos molestias que el propio video admite: hay que **importar las librerías a mano** la primera vez (`from idc import *`, `from idautils import *`, `from idaapi import *`) y la consola se cierra al depurar (se reabre con `Shift`+`.`).

El cap. 25 arma un entorno más cómodo: un archivo `exint.py` en `.ipython/profile_default/startup/` que carga las librerías solas (y agrega `exon`/`exof` para mostrar enteros en hexadecimal), y **Spyder conectado al kernel de IDA** (*Consoles → Connect to an existing kernel*, eligiendo el `kernel-NNNN.json` más nuevo). Así podés escribir scripts con autocompletado, ver la documentación con `Ctrl+I`, ejecutar una selección (*Run selection or current line*) y hacer doble clic en una dirección de la salida para saltar a ella en IDA.

Una prueba rápida de que las librerías están cargadas: `here()` devuelve la dirección donde está el cursor. Si da error, las librerías no se importaron (cap. 25).

:::{aviso} La API cambió de nombre entre versiones
La mayoría de los scripts viejos de internet fallan no porque estén mal, sino porque los nombres cambiaron (`PatchByte` → `patch_byte`, etc.). El cap. 25 recomienda la página oficial *"Porting from IDA 6.x to 7.4"*, que lista el nombre viejo y el nuevo de cada función. Si un script tira error por todos lados, es casi seguro esto.
:::

### Correr un script

Hay tres formas (caps. 22b y 25): cargar un `.py` con *File → Script file*; pegar código de IDAPython **dentro de un breakpoint** (en *Edit breakpoint*, cambiando el tipo a IDAPython) —ahí los registros se leen como `cpu.edx`, y si el código hace `return True` el programa para, lo que da un breakpoint condicional scripteado—; o, con Spyder conectado, ejecutar una selección del script.

### Recorrer las funciones

El cap. 25 recorre todas las funciones del binario:

```python
import idautils, idc

inicio = idc.get_inf_attr(idc.INF_MIN_EA)   # dirección mínima cargada
fin    = idc.get_inf_attr(idc.INF_MAX_EA)   # dirección máxima

for ea in idautils.Functions(inicio, fin):
    nombre = idc.get_func_name(ea)
    fin_f  = idc.find_func_end(ea)
    print(f"{ea:#x}  {fin_f:#x}  {nombre}")
```

`Functions()` devuelve un **generador** (para verlo entero, `list(idautils.Functions())`); `get_func_name(ea)` da el nombre de la función a la que pertenece una dirección (no hace falta la dirección exacta de inicio); `find_func_end(ea)` da el final (un byte más allá de la última instrucción).

### Recorrer el grafo de control y pintar bloques

El cap. 27b toma una función y recorre sus **bloques básicos**:

```python
import idaapi, idc

f = idaapi.get_func(idc.here())     # func_t de la función bajo el cursor
fc = idaapi.FlowChart(f)
for bloque in fc:
    print(f"{bloque.start_ea:#x} - {bloque.end_ea:#x}")
```

Cada bloque tiene `start_ea`, `end_ea`, `preds()` (bloques que llegan a él) y `succs()` (a los que salta). Para **pintar** el bloque donde está una dirección y sus predecesores de otro color:

```python
import idaapi, idautils, idc

addr = idc.here()
f = idaapi.get_func(addr)
for bloque in idaapi.FlowChart(f):
    if bloque.start_ea <= addr < bloque.end_ea:        # bloque que contiene addr
        for ea in idautils.Heads(bloque.start_ea, bloque.end_ea):
            idc.set_color(ea, idc.CIC_ITEM, 0x80FF80)  # verde (0xBBGGRR)
        for pred in bloque.preds():                    # puede haber varios
            for ea in idautils.Heads(pred.start_ea, pred.end_ea):
                idc.set_color(ea, idc.CIC_ITEM, 0x80FFFF)
```

Es una forma visual de ver de dónde viene el flujo. El color va en formato `0xBBGGRR`.

### Parchear con un script (solo programas propios)

El cap. 25 automatiza un parcheo sobre un crackme. Tomamos la **mecánica** (no el objetivo) para aplicarla a un programa propio en tu laboratorio:

```python
import idc

addr = idc.find_binary(idc.get_inf_attr(idc.INF_MIN_EA), idc.SEARCH_DOWN, "74 07")
if addr != idc.BADADDR:
    print("originales:", idc.get_bytes(addr, 2).hex(), "/ byte previo:", hex(idc.get_original_byte(addr)))
    idc.patch_bytes(addr, b"\x90\x90")   # en la base de datos
    # idc.revert_byte(addr)              # para deshacer
```

`patch_bytes` cambia bytes en la base de datos; `get_original_byte` devuelve el byte anterior al parche (lo mismo que *Patch program → original bytes* en el menú); `revert_byte` lo deshace. Para escribir los cambios al `.exe`, el cap. 25 usa `save_file`/*apply patches to input file*, calculando el **file offset** = dirección − base del código + `0x400` (header), como en la lección de números. **Antes de cualquier script que modifique la base de datos, tomá un snapshot** (*Database snapshot manager*).

### Buscar secuencias de instrucciones por patrón

El cap. 32 arma un buscador de instrucciones con `ida_search.find_text` + expresiones regulares. El truco es una función `replace()` que convierte una instrucción fácil de tipear en un patrón regex:

- el espacio simple → ` *` (cualquier cantidad de espacios, porque IDA alinea con varios);
- `R32` → `(e.x|e.i)` para cualquier registro de 32 bits;
- `const` → `[0-9a-fA-F]{2,8}h` para una constante hexadecimal;
- y **escapar** los caracteres especiales de regex que aparezcan en la instrucción (`[`, `]`, `+`, `*`, `-`) con `\`.

Dos límites que el capítulo señala: la búsqueda de texto de IDA es **de una sola línea** (no matchea una secuencia multilínea en una sola llamada; hay que buscar instrucción por instrucción, encadenando desde la dirección anterior), y `find_text` devuelve `BADADDR` (`0xFFFFFFFF`) cuando no encuentra. Para buscar una secuencia de tres instrucciones "cercanas", se busca la primera, y desde cada hallazgo se busca la siguiente verificando que la **distancia** no supere un límite. `idc.jumpto(ea)` mueve el cursor para mostrar el resultado en IDA.

### Traducir números a nombres con enumeraciones

El cap. 22b, para imprimir los mensajes de Windows por nombre en vez de por número, agrega una enumeración en *Local Types* y la consulta desde el script con `get_enum("nombre")` (devuelve el id de la enumeración) y la función que, dado ese id y un valor como `cpu.edx`, devuelve el nombre (`WM_COMMAND`, etc.). Es la forma scripteada de lo que la tecla `M` hace a mano en el listado.

## Ghidra y Python standalone

Si usás Ghidra, tenés scripting en Python (Jython) y Java. El modelo es parecido: recorrer funciones, leer instrucciones, renombrar.

Si no tenés IDA Pro, también podés automatizar **sin** desensamblador:

```python
import pefile

pe = pefile.PE("check.exe")
print("Entry point:", hex(pe.OPTIONAL_HEADER.AddressOfEntryPoint))
for entry in pe.DIRECTORY_ENTRY_IMPORT:
    print(entry.dll.decode())
    for imp in entry.imports:
        print("  ", imp.name)
```

`pefile` es una librería de Python para leer PE. No desensambla, pero sirve para inventarios, detección y reportes.

Para desensamblar desde Python, `capstone` permite decodificar bytes:

```python
from capstone import Cs, CS_ARCH_X86, CS_MODE_32

md = Cs(CS_ARCH_X86, CS_MODE_32)
codigo = bytes.fromhex("83F81E7410")
for ins in md.disasm(codigo, 0x401000):
    print(f"{ins.address:#x}: {ins.mnemonic} {ins.op_str}")
```

Salida esperada:

```text
0x401000: cmp eax, 0x1e
0x401003: je 0x401015
```

## El flujo de trabajo con scripts

```text
1. Hacer la tarea a mano una vez.
2. Detectar qué se repite.
3. Escribir el script mínimo.
4. Probarlo sobre una copia.
5. Revisar el resultado (no confiar ciegamente).
6. Guardar el script con el informe.
```

El paso 5 es el más importante. Un script que renombra mal contamina la base de datos y hace que el análisis sea peor que antes.

## Práctica

1. Compilá tu `check.exe` y abrilo en IDA.
2. Corré el script de renombrado y verificá que las funciones `sub_` cambiaron de nombre.
3. Corré el script de búsqueda de `0x1E0` y comprobá que encuentra la comparación.
4. Modificá la constante del programa a `0x1B8`, recompilá y volvé a correr el script.
5. Escribí un script que imprima todas las funciones cuyo nombre contenga "check" o "main".
6. Guardá los scripts en tu bitácora y anotá la versión de IDA.

## Preguntas de repaso

**1. ¿Cuándo conviene automatizar?**
Cuando la tarea es repetitiva, mecánica y verificable. Primero se hace a mano para entenderla.

**2. ¿Qué diferencia hay entre `idc`, `idautils` e `idaapi`?**
`idc` tiene funciones clásicas; `idautils` ofrece iteradores; `idaapi` es la API de bajo nivel y la interfaz.

**3. ¿IDAPython funciona en IDA Free?**
Depende de la versión. Históricamente IDA Free no incluía Python; las versiones recientes agregaron capacidades. Si no está, usá Ghidra o automatizá con `pefile`/`capstone`.

**4. ¿Por qué hay que revisar el resultado de un script?**
Porque un script no entiende el contexto: puede renombrar mal, buscar coincidencias falsas o modificar datos que no correspondían.

**5. ¿Qué hace `capstone`?**
Desensambla bytes a instrucciones desde Python, sin necesidad de IDA.

## Antes de avanzar

Tenés que poder:

- Escribir un script que recorra funciones y renombre.
- Buscar una constante en `.text`.
- Listar imports con IDAPython o `pefile`.
- Explicar por qué el resultado se revisa a mano.

:::{nota} Puerta de salida
Si el script te ahorra tiempo y el resultado es correcto, la rama está aprobada. Si el script produce nombres dudosos y no los revisás, no.
:::

## Fuentes de esta lección

- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_22b Apéndice teórico 3 - Empezando con IDAPython_22b Apéndice teórico 3 - Empezando con IDAPython.txt|Reversing desde cero, cap. 22b}} — IPyIDA, imports, correr código en un breakpoint (`cpu.edx`, `return True`) y enumeraciones (transcripción .txt, sin marcas).
- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_25 Empezando con IDAPython_25 Empezando con IDAPython.txt|Reversing desde cero, cap. 25}} — entorno (exint.py, Spyder+kernel), `here()`, porting de nombres, recorrer `Functions()` y parchear/revertir/guardar (transcripción .txt, sin marcas).
- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_27b Jugando con IDAPython_27b Jugando con IDAPython.txt|Reversing desde cero, cap. 27b}} — `get_func`, `FlowChart`, bloques básicos (`start_ea`/`end_ea`/`preds`) y pintar con `set_color` (transcripción .txt, sin marcas).
- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_32 Un proyecto con IDAPython_32 Un proyecto con IDAPython.txt|Reversing desde cero, cap. 32}} — búsqueda de instrucciones con `find_text` + regex, límite de una línea y búsqueda por distancia (transcripción .txt, sin marcas).
- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_15 Ejercicio 2 - Análisis estático_15 Ejercicio 2 - Análisis estático.txt|Reversing desde cero, cap. 15}} — constante `0x1E0` usada en el ejemplo de búsqueda editorial.

:::{nota} Capas de esta lección
**Contenido observado en CLS:** el entorno IPyIDA/Spyder, `here()`, el recorrido de funciones y del grafo, el parcheo scripteado, la búsqueda por regex y las enumeraciones (caps. 22b, 25, 27b, 32). **Conocimiento externo:** API de IDAPython moderna, Ghidra, `pefile` y `capstone`. **Recomendación editorial:** los tres primeros scripts de ejemplo, el flujo de trabajo y el encuadre de parchear solo programas propios.
:::
