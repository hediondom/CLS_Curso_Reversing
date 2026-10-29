---
title: "Etapa 1 · C y Python mínimos para analizar"
description: "El subconjunto de C y Python que necesitás para escribir programas de práctica y herramientas pequeñas, con una advertencia sobre el material de CLS."
etapa: "Etapa 1 · Fundamentos"
---

# C y Python mínimos para analizar

:::{nota} Objetivo de la lección
Al terminar vas a poder leer y escribir programas chicos en C (variables, condiciones, bucles, funciones, punteros) y en Python (tipos, listas, funciones, archivos binarios), compilarlos, ejecutarlos en el laboratorio y usarlos como conejillos de indias para el debugger.
:::

**Prerrequisitos:** Etapa 0 y las lecciones anteriores de la Etapa 1. **Duración sugerida:** 6 a 8 horas. Estimación aproximada.

## Una advertencia honesta sobre el material de CLS

La carpeta `Python ISO video tutes` parece un curso de Python, pero **no lo es**. Las 55 transcripciones son un curso de **lógica y fundamentos de programación** dictado por Daniel Bermúdez, basado en pseudocódigo y con ejemplos en Basic, Pascal y C. En las transcripciones no hay una sola línea de Python ejecutable: ni `import`, ni `print(...)`, ni `raw_input`. El propio autor anuncia una segunda parte con Python "puro" que **no está en la carpeta**. El material cita Python 2.5.1 como versión vigente en abril de 2007 y usa `print hola` como sentencia, sintaxis que Python 3 ya no acepta.

Eso no lo vuelve inútil. Lo que sí enseña —algoritmos, secuencia, decisión, ciclos, arreglos, matrices y funciones— es exactamente el prerequisito mental para programar. Pero si venías a aprender Python con estos videos, no lo vas a lograr. Para Python moderno, esta guía usa conocimiento externo y prácticas propias, y lo marca como tal.

:::{aviso} Estado en el catálogo
El material está listado en {{src:CLS_resultados_intermedios/transcripciones/extraidos/Python ISO video tutes/Videotutoriales_QueesPython_QueesPython.txt|Python ISO video tutes}} y en {{src:CLS_resultados_intermedios/mapa_carpetas_etapas.csv|mapa_carpetas_etapas.csv}} como apoyo a la Etapa 1. La ficha completa, con lo que se leyó y lo que falta, está en {{src:CLS_Guia/fichas/python-iso.html|ficha de Python ISO}}.
:::

## Cómo aprender Python de verdad (recursos externos)

Como el corpus CLS no enseña Python moderno, esta guía completa el camino con **cursos y tutoriales externos**. No son material del grupo; son **recomendación editorial**, gratuitos o con parte gratuita, y actuales. Verificá siempre el enlace antes de usarlo.

| Recurso | Qué es | Para quién |
|---|---|---|
| **El Tutorial de Python (oficial)** — [docs.python.org/3/tutorial](https://docs.python.org/3/tutorial/) | La referencia gratuita y al día; Python 3 | Base sólida, consulta permanente |
| **Automate the Boring Stuff** (Al Sweigart) — [automatetheboringstuff.com](https://automatetheboringstuff.com/) | Libro gratuito online, muy práctico, pensado para Windows | Quien nunca programó y quiere resultados rápidos |
| **Real Python** — [realpython.com](https://realpython.com/) | Tutoriales por tema (archivos, bytes, struct, módulos) | Afianzar temas puntuales |
| **Python Crash Course** (Eric Matthes) | Libro de pago, proyecto guiado | Quien prefiere un recorrido ordenado |
| **freeCodeCamp — Python (YouTube)** | Curso en video gratuito | Quien aprende mejor mirando |

**La ruta mínima que necesitás para esta guía** (no hace falta dominar todo Python): tipos y variables → `str` vs `bytes` → listas y diccionarios → `if`/`for`/`while` → funciones y módulos (`import`) → leer y escribir archivos **binarios** → el módulo `struct` para desempaquetar enteros. Con eso ya podés escribir las herramientas que usa el resto del curso.

:::{nota} El puente con el curso de lógica de CLS
Lo que el "Python ISO" de CLS sí te deja —secuencia, decisión, ciclos, arreglos, funciones— es el prerrequisito mental. Si lo mirás, usalo para **la lógica**, y aprendé la **sintaxis de Python 3** con los recursos de arriba. Es la combinación que te lleva al siguiente tema: scripts que leen binarios.
:::

## El subconjunto de C que vas a leer en un debugger

No necesitás ser experto en C. Necesitás reconocer cinco construcciones:

1. **Variables y tipos:** `int`, `char`, `unsigned`, punteros (`int *p`).
2. **Condiciones:** `if`, `else`, `switch`.
3. **Bucles:** `for`, `while`.
4. **Funciones:** parámetros, valor de retorno, variables locales.
5. **Punteros y arrays:** `&x` (dirección de), `*p` (contenido de), `a[i]`.

### Ejemplo paso a paso: el programa del capítulo 15

El capítulo 15 analiza un crackme de práctica que pide dos números. La lógica que Ricardo deduce del listado es:

- el primer número tiene que ser **menor o igual** que `0x32` (50 decimal);
- el segundo tiene que ser **mayor o igual** que `0x32`;
- la suma de los dos, multiplicada por 4, tiene que dar `0x1E0` (480 decimal).

Un programa equivalente, escrito por vos, es este:

```c
#include <stdio.h>

int main(void) {
    int a, b;
    printf("Primer valor: ");
    if (scanf("%d", &a) != 1) return 1;
    printf("Segundo valor: ");
    if (scanf("%d", &b) != 1) return 1;

    if (a > 50 || b < 50) {
        puts("No cumple las condiciones");
        return 0;
    }
    if ((a + b) * 4 == 480) {
        puts("Correcto");
    } else {
        puts("Incorrecto");
    }
    return 0;
}
```

**Cómo se lee, línea por línea:**

- `int a, b;` reserva dos enteros en el stack.
- `scanf("%d", &a)` lee un decimal y lo guarda en la dirección de `a`. El `&` es la dirección; sin él, la función no podría modificar la variable.
- `a > 50 || b < 50` usa `||` (OR lógico): si cualquiera de las dos condiciones se cumple, rechaza.
- `(a + b) * 4 == 480` reproduce la comparación del binario. Con `a = 40` y `b = 80`, da `(120) * 4 = 480`, así que imprime `Correcto`.

**Compilación** (en el guest, con MinGW o Visual Studio):

```bash
gcc -O0 -g -o check.exe check.c
```

`-O0` desactiva optimizaciones para que el assembly sea fácil de seguir; `-g` agrega información de depuración. En Visual Studio, compilá en modo Debug.

**Qué mirar en el debugger:** el `if (a > 50 || b < 50)` se convierte en dos comparaciones y saltos; el `(a+b)*4` se convierte en un `add` seguido de un `shl eax, 2` (desplazar dos bits a la izquierda es multiplicar por 4). Eso conecta directo con la lección de instrucciones.

## El subconjunto de Python que vas a usar como herramienta

Python no compila a un `.exe` nativo (en el sentido clásico), así que no es el lenguaje que vas a ver en un debugger de Windows. Es la **navaja suiza** para procesar archivos, calcular hashes, parsear cabeceras y automatizar tareas.

### Ejemplo: leer los primeros bytes de un ejecutable

```python
from pathlib import Path

data = Path("check.exe").read_bytes()
print("Tamaño:", len(data))
print("Primeros dos bytes:", data[:2])          # b'MZ'
print("Primeros 16 bytes:", data[:16].hex(" "))
```

Salida esperada (los valores exactos dependen del compilador):

```text
Tamaño: 53248
Primeros dos bytes: b'MZ'
Primeros 16 bytes: 4d 5a 90 00 03 00 00 00 04 00 00 00 ff ff 00 00
```

`read_bytes()` devuelve un objeto `bytes`: una secuencia inmutable de valores entre 0 y 255. `data[:2]` toma los dos primeros; `.hex(" ")` los muestra en hexadecimal separados por espacios. No hace falta instalar nada.

### Ejemplo: calcular un SHA-256

```python
import hashlib
from pathlib import Path

datos = Path("check.exe").read_bytes()
print(hashlib.sha256(datos).hexdigest())
```

Ese hash es el mismo que devuelve `Get-FileHash` en PowerShell. Sirve para la bitácora de la Etapa 0.

### Ejemplo: desempaquetar un entero con `struct`

Los bytes sueltos no alcanzan: para leer una cabecera hay que interpretar grupos de bytes como números. Eso lo hace el módulo `struct`. En un PE, en el offset `0x3C` hay un entero de 4 bytes (little-endian) que apunta a dónde empieza la firma `PE\0\0`:

```python
import struct
from pathlib import Path

data = Path("check.exe").read_bytes()
(pe_off,) = struct.unpack_from("<I", data, 0x3C)   # "<I" = entero de 4 bytes, little-endian
print("La cabecera PE empieza en:", hex(pe_off))
print("Firma en ese offset:", data[pe_off:pe_off+4])  # b'PE\x00\x00'
```

`struct.unpack_from("<I", data, 0x3C)` lee 4 bytes desde el offset `0x3C` y los arma como un entero sin signo (`I`) en little-endian (`<`). Esto conecta directo con la lección de PE: lo que ahí leés a mano, acá lo automatizás.

### Ejemplo: el mismo cálculo del crackme, en Python

```python
a = int(input("Primer valor: "))
b = int(input("Segundo valor: "))
if a <= 50 and b >= 50 and (a + b) * 4 == 480:
    print("Correcto")
else:
    print("Incorrecto")
```

Compará las dos versiones: en C el `scanf` recibe una dirección; en Python `input()` devuelve un string y `int()` lo convierte. En C la condición se escribe con `||` y `&&`; en Python, con `or` y `and`. La lógica es la misma.

:::{nota} Python 2 vs Python 3
Si encontrás material viejo con `print "hola"` o `raw_input`, es Python 2. Hoy se usa Python 3: `print("hola")`, `input()`, divisiones con `/` que devuelven float y `//` para entero. El curso de CLS es de esa época; no copies esa sintaxis.
:::

## Hacia dónde sigue este camino

No hace falta parsear cada cabecera a mano con `struct`: hay librerías que ya lo hacen. El camino natural desde acá es:

1. **`pefile`** — lee cabeceras PE, secciones e imports de un ejecutable de Windows con unas pocas líneas.
2. **`capstone`** — desensambla bytes a instrucciones x86/x64 desde Python.
3. **IDAPython / Ghidra scripting** — automatizar el análisis dentro del desensamblador.

Esos tres se desarrollan, con ejemplos, en la rama de [automatización](05-automatizacion.html) de la Etapa 5. Lo de esta lección —`bytes`, `hex`, `struct`, archivos— es la base que te deja usarlos sin que sean magia.

## Práctica

1. Compilá el programa `check.c` y probalo con `40 80`, `50 50`, `51 80` y `40 79`. Anotá qué imprime cada caso.
2. Abrilo en x64dbg, poné un breakpoint en `main` y seguí con F8 hasta la comparación. Anotá en qué instrucción se convierte `(a+b)*4`.
3. Escribí un programa en C que pida una palabra y la compare con `"clase"` usando `strcmp`. Compilalo y encontralo en el debugger.
4. Escribí un script en Python que recorra una carpeta, calcule el SHA-256 de cada archivo y escriba un CSV con `ruta,hash`. Usalo sobre tu carpeta de prácticas.
5. Modificá el script para que lea la cabecera PE y muestre `ImageBase` y `AddressOfEntryPoint` (podés reutilizar el de la lección de PE). Usá `struct.unpack_from` sobre los offsets correctos.
6. Instalá `pefile` (`pip install pefile`) y obtené los mismos valores con la librería (`pe.OPTIONAL_HEADER.ImageBase`, `pe.OPTIONAL_HEADER.AddressOfEntryPoint`). Compará con tu versión a mano: ¿coinciden? Así ves qué te ahorra la librería.
7. Hacé el Tutorial oficial de Python (secciones 3 a 7) o los primeros capítulos de *Automate the Boring Stuff*, y rehacé el script del item 4 sin mirar el ejemplo.

## Preguntas de repaso

**1. ¿Por qué `scanf` necesita `&a` y `printf` no?**
Porque `scanf` tiene que **escribir** en la variable, y para eso necesita su dirección. `printf` solo lee el valor.

**2. ¿Qué diferencia hay entre `int` y `unsigned int`?**
El rango y la interpretación. `int` usa complemento a dos y incluye negativos; `unsigned int` solo representa valores no negativos y puede llegar al doble del máximo positivo.

**3. ¿Por qué `x << 2` equivale a multiplicar por 4?**
Porque cada desplazamiento a la izquierda multiplica por 2. Dos desplazamientos multiplican por 4. Es la operación que usa el compilador para optimizar multiplicaciones por potencias de dos.

**4. ¿Python sirve para analizar un `.exe`?**
Sí, como herramienta: leer bytes, parsear cabeceras, calcular hashes, automatizar. No es el lenguaje del binario que analizás, salvo que el programa esté hecho en Python y empaquetado con un generador de ejecutables.

**5. ¿El curso de Python de CLS enseña Python?**
No. Enseña lógica de programación con pseudocódigo y ejemplos en Basic, Pascal y C. Es útil como base, pero no reemplaza un curso de Python.

## Antes de avanzar

Tenés que poder:

- Leer un programa en C de 20 líneas y decir qué hace.
- Escribir, compilar y ejecutar un programa propio en C.
- Leer y escribir un archivo binario en Python y calcular su hash.
- Explicar por qué el material de Python de CLS no es un curso de Python.

:::{nota} Puerta de salida de la Etapa 1
Con esto terminás los fundamentos. Si podés escribir tus propios binarios, ya tenés con qué practicar todo lo que sigue sin depender de software ajeno.
:::

## Fuentes de esta lección

- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Python ISO video tutes/Videotutoriales_FundamentosdeProgramacion_FundamentosdeProgramacion.txt|Python ISO video tutes, Fundamentos de programación}} — qué es programar, intérprete vs compilador, `print` en Python 2.
- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Python ISO video tutes/Videotutoriales_QueesPython_QueesPython.txt|Python ISO video tutes, Qué es Python}} — presentación del curso y versión de la época.
- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Python ISO video tutes/Videotutoriales_Arreglos1_Arreglos1.txt|Python ISO video tutes, Arreglos}} — ejemplo del tipo de contenido real de la colección.
- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_15 Ejercicio 2 - Análisis estático_15 Ejercicio 2 - Análisis estático.txt|Reversing desde cero, cap. 15}} — lógica del programa de práctica y comparación con `0x32`/`0x1E0`.
- {{src:CLS_fuentes_externas/github/apuromafo_Crackslatinos/C Y REVERSING|C Y REVERSING (contenedor)}} — material de C del proyecto, **pendiente de revisar**: solo se verificó su existencia y sus dos archivos `.rar`.

:::{nota} Capas de esta lección
**Contenido observado en CLS:** la lógica del programa del capítulo 15 y el contenido real de las transcripciones de Python ISO. **Conocimiento externo:** sintaxis de C y Python 3, compilación, hash, `struct`, y los recursos de aprendizaje externos (Tutorial oficial, Automate the Boring Stuff, Real Python, etc.). **Recomendación editorial:** los programas de práctica, la corrección sobre el curso de Python de CLS y la ruta de Python hacia `pefile`/`capstone`.
:::
