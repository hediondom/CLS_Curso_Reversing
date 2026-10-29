---
title: "Etapa 3 · Leer IL y comparar fuente, IL y decompilación"
description: "Un método propio paso a paso: qué hace cada instrucción IL, cómo se ve la pila de evaluación y qué reconstruye el decompilador."
etapa: "Etapa 3 · .NET como primera victoria"
---

# Leer IL y comparar fuente, IL y decompilación

:::{nota} Objetivo de la lección
Al terminar vas a poder leer el IL de un método sencillo, seguir la pila de evaluación instrucción por instrucción y comparar tres vistas del mismo código: la fuente que escribiste, el IL que generó el compilador y lo que reconstruye el decompilador.
:::

**Prerrequisitos:** runtime y ensamblados .NET. **Duración sugerida:** 4 horas. Estimación aproximada.

## IL es una máquina de pila

A diferencia del assembly x86, que usa registros, el IL es una **máquina de pila**: las instrucciones empujan valores a una pila de evaluación y las operaciones los sacan, calculan y empujan el resultado.

```text
ldarg.0        -> push a
ldarg.1        -> push b
add            -> pop b, pop a, push (a+b)
```

Eso hace que el IL sea más fácil de leer que el assembly nativo: no hay que seguir registros, solo la pila. El precio es que hay muchas instrucciones `ld*`/`st*`.

## El método de ejemplo

Escribí este método en una clase de consola:

```csharp
static bool Check(int a, int b)
{
    if (a > 50 || b < 50)
        return false;
    return (a + b) * 4 == 480;
}
```

Compilalo en **Debug** (sin optimizaciones) y abrilo en ILSpy. El IL va a ser parecido a este (los offsets exactos cambian según el compilador y la versión):

```il
.method private hidebysig static bool Check(int32 a, int32 b) cil managed
{
    .maxstack 2

    ldarg.0
    ldc.i4.s 50
    cgt
    brtrue.s L_false

    ldarg.1
    ldc.i4.s 50
    clt
    brtrue.s L_false

    ldarg.0
    ldarg.1
    add
    ldc.i4.2
    shl
    ldc.i4 480
    ceq
    ret

L_false:
    ldc.i4.0
    ret
}
```

## Lectura línea por línea

| IL | Qué hace | Pila después |
|---|---|---|
| `ldarg.0` | Empuja el primer argumento (`a`) | `[a]` |
| `ldc.i4.s 50` | Empuja la constante 50 | `[a, 50]` |
| `cgt` | Compara: ¿`a > 50`? Empuja 1 o 0 | `[a>50]` |
| `brtrue.s L_false` | Si el tope es distinto de 0, salta a `L_false` | `[]` |
| `ldarg.1` | Empuja `b` | `[b]` |
| `ldc.i4.s 50` | Empuja 50 | `[b, 50]` |
| `clt` | ¿`b < 50`? Empuja 1 o 0 | `[b<50]` |
| `brtrue.s L_false` | Si es verdadero, salta a `L_false` | `[]` |
| `ldarg.0` | Empuja `a` | `[a]` |
| `ldarg.1` | Empuja `b` | `[a, b]` |
| `add` | Suma | `[a+b]` |
| `ldc.i4.2` | Empuja 2 | `[a+b, 2]` |
| `shl` | Desplaza a la izquierda 2 bits (×4) | `[(a+b)*4]` |
| `ldc.i4 480` | Empuja 480 | `[(a+b)*4, 480]` |
| `ceq` | ¿Son iguales? Empuja 1 o 0 | `[resultado]` |
| `ret` | Devuelve el tope | `[]` |
| `L_false: ldc.i4.0` | Empuja 0 (false) | `[0]` |
| `ret` | Devuelve 0 | `[]` |

**Comprobación con `a = 40`, `b = 80`:**

1. `40 > 50` → 0. No salta.
2. `80 < 50` → 0. No salta.
3. `40 + 80 = 120`.
4. `120 << 2 = 480`.
5. `480 == 480` → 1 (`true`).

El método devuelve `true`. Con `a = 60`, el primer `cgt` da 1 y salta a `L_false`: devuelve `false` sin evaluar el resto.

:::{nota} `cgt`, `clt`, `ceq`
Son las comparaciones de IL: *compare greater than*, *compare less than*, *compare equal*. Empujan 1 si la condición se cumple y 0 si no. No modifican flags como `CMP`; el resultado es un valor en la pila.
:::

## Las tres vistas del mismo método

**Fuente (lo que escribiste):**

```csharp
if (a > 50 || b < 50)
    return false;
return (a + b) * 4 == 480;
```

**IL (lo que generó el compilador):** el listado de arriba, con `brtrue` y una etiqueta `L_false`.

**Decompilación (lo que reconstruye ILSpy):**

```csharp
private static bool Check(int a, int b)
{
    if (a <= 50 && b >= 50)
    {
        return (a + b) * 4 == 480;
    }
    return false;
}
```

Las tres son equivalentes, pero **no son iguales**. El decompilador invirtió la condición (`a > 50 || b < 50` se convirtió en `a <= 50 && b >= 50` por De Morgan), movió el `return false` al final y agregó llaves. Eso es normal: reconstruye una lógica equivalente, no el texto original.

Cuando analices un binario ajeno, no esperes "el código fuente". Esperá **una versión legible y equivalente**, que puede diferir en estilo, nombres y estructura.

## Metadatos: dónde están los nombres

En ILSpy, además del código, podés ver:

- **Assembly**: nombre, versión, cultura, referencias (`System.Runtime`, `System.Console`).
- **Namespace** y **Type**: `HolaNet.Program`.
- **Method**: nombre, firma, atributos (`private`, `static`).
- **Tokens**: identificadores numéricos que el runtime usa para referenciar tipos y métodos (por ejemplo, un `MethodDef` con su token). No los necesitás para leer, pero explican por qué el decompilador puede reconstruir las referencias.

Si el binario está ofuscado, los nombres pueden ser `\u0001`, `A`, `B`, `method_0`. La estructura sigue ahí; lo que se pierde es la legibilidad.

## Debug vs Release

Compilá el mismo método en Release y compará:

- En Debug, las variables locales y los puntos de secuencia están pensados para depurar; el IL es más "literal".
- En Release, el compilador puede inline-ar métodos chicos, reordenar, eliminar variables y simplificar condiciones.
- Las líneas y nombres de variables locales pueden desaparecer si no hay PDB.

Para aprender, usá Debug. Para analizar un binario real, asumí Release y no te sorprendas si el decompilador muestra un código más raro.

## Ofuscación: qué cambia y qué no

| Técnica | Qué hace | Cómo se reconoce |
|---|---|---|
| Renombrado | Cambia nombres por símbolos ilegibles | `\u0001`, `A`, `method_0` |
| Cifrado de strings | Guarda las cadenas cifradas y las descifra en runtime | Strings ausentes o ilegibles; llamadas a un método de descifrado |
| Flujo falso | Agrega saltos y bloques que nunca se ejecutan | Grafos con muchos bloques muertos |
| State machine | Convierte métodos en una máquina de estados | `switch` sobre un estado, `MoveNext` |

El decompilador sigue siendo útil, pero hay que **verificar**. Una condición reconstruida puede ser incorrecta si el flujo está ofuscado. La regla es la misma que en nativo: contrastar estático con dinámico, sobre un programa propio o autorizado.

## Práctica

1. Compilá el método `Check` en Debug y en Release. Pegá las dos versiones de IL y marcá tres diferencias.
2. Escribí un método con un `for` que sume 1..10. Encontrá en el IL el salto que vuelve al inicio del bucle.
3. Escribí una propiedad `public int Edad { get; set; }` y buscá el getter y el setter en ILSpy. ¿Qué métodos genera el compilador?
4. Escribí un método `async` que espere un segundo e imprima algo. Buscá la máquina de estados que genera el compilador. No hace falta entenderla entera: identificá `MoveNext`.
5. Compará la decompilación con tu fuente. Marcá al menos una diferencia de estilo y explicá por qué es equivalente.
6. Escribí en tu bitácora: qué método analizaste, qué IL te sorprendió y qué parte no entendés todavía.

## Preguntas de repaso

**1. ¿IL usa registros?**
No. Es una máquina de pila: las instrucciones empujan y sacan valores de una pila de evaluación.

**2. ¿Qué hace `cgt`?**
Compara los dos valores del tope: empuja 1 si el primero es mayor que el segundo, 0 si no.

**3. ¿Por qué el decompilador muestra una condición distinta de la fuente?**
Porque reconstruye una lógica equivalente a partir del IL. Puede aplicar De Morgan, reordenar retornos o simplificar expresiones.

**4. ¿Qué se pierde en Release?**
Variables locales, líneas y algunas simplificaciones que el compilador aplica. Los nombres de tipos y métodos se conservan, salvo ofuscación.

**5. ¿Qué hace `shl` en el IL?**
Desplaza a la izquierda la cantidad de bits indicada. `shl 2` equivale a multiplicar por 4.

**6. ¿La ofuscación impide analizar un binario .NET?**
No. Lo hace más difícil. El IL y los metadatos siguen ahí; hay que verificar la reconstrucción con ejecución controlada.

## Antes de avanzar

Tenés que poder:

- Leer un método IL de 20 instrucciones y decir qué devuelve.
- Seguir la pila de evaluación con un valor concreto.
- Comparar fuente, IL y decompilación y explicar una diferencia.
- Reconocer señales de ofuscación.

:::{nota} Puerta de salida de la Etapa 3
Si podés compilar tu propio método, leer su IL y explicar qué hace el decompilador, terminaste .NET. La Etapa 4 es el método de análisis completo, con informe.
:::

## Fuentes de esta lección

- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Videos y material adicional Ingenieria Inversa/Videos_Video38_Video38.txt|Videos y material adicional, Video 38}} — MSIL y por qué el código intermedio requiere otras herramientas.
- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Videos y material adicional Ingenieria Inversa/Videos_Video40_Video40.txt|Videos y material adicional, Video 40}} — .NET Reflector y reconstrucción de un formulario VB.NET.
- {{src:CLS_resultados_intermedios/teorias_numeradas_por_etapa.csv|teorias_numeradas_por_etapa.csv}} — títulos .NET/dnSpy **pendientes de revisar**.

:::{nota} Capas de esta lección
**Contenido observado en CLS:** el video 38 (MSIL) y el video 40 (decompilación VB.NET). **Conocimiento externo:** conjunto de instrucciones IL, pila de evaluación y comportamiento de los decompiladores. **Recomendación editorial:** el método `Check`, la tabla línea por línea y los ejercicios.
:::
