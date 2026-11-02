---
title: "2.32 · Go y Rust en profundidad: recuperar tipos, nombres y estructuras"
description: "Recuperar nombres de función (gopclntab), tipos e interfaces en binarios Go, y desmanglar símbolos, trait objects y layouts en binarios Rust; reconocer cada runtime. Profundiza 2.13."
etapa: "Etapa 2 · Ampliación de 2.13 (Huella de compilador)"
---

# Go y Rust en profundidad

:::{nota} Objetivo de la lección
Ir más allá de «reconocer el compilador» (lo que viste en [2.13](02-huella-compilador.html)) y **recuperar la lógica** de un binario Go o Rust: nombres de función, tipos, interfaces/traits y cómo se ven sus estructuras en memoria. **Prerrequisitos:** huella de compilador ([2.13](02-huella-compilador.html)) y C++ profundo ([2.18](02-cpp-profundo.html), para vtables y layouts).
:::

Esto es una **ampliación profunda** de 2.13: ahí ya identificabas que un binario era Go o Rust; acá aprendés a leerlos.

## Por qué cuestan (y por qué hay esperanza)

Go y Rust producen binarios **estáticos y grandes**, con su propio *runtime* adentro y sin los símbolos «clásicos» de C. La buena noticia: ambos dejan **metadatos recuperables**. En Go son casi un regalo; en Rust hay que desmanglar y entender la monomorfización (**conocimiento externo**).

## Go: el runtime que se deja leer

- **`gopclntab` (pclntab):** una tabla que mapea direcciones a **nombres de función**, pensada para los *stack traces*. Aunque el binario esté «stripeado», esta tabla suele estar: recuperás casi todos los nombres. Es el primer paso siempre.
- **`moduledata`:** la estructura raíz del runtime; desde ahí se llega a la pclntab y a las tablas de tipos.
- **Tipos (`_type`/rtype):** Go guarda descriptores de tipo para reflexión; con ellos recuperás nombres de structs y campos.
- **Interfaces (`itab`):** una interfaz es un par `(itab, data)`; el `itab` tiene el tipo concreto y la **tabla de métodos**. Reconocer este par te dice qué método se llama en un despacho dinámico.
- **Strings:** `(puntero, longitud)`, **sin terminador NUL**. En el listado vas a ver una carga de puntero seguida de una longitud inmediata.
- **Convención de llamada:** hasta Go 1.16 los argumentos iban por **stack**; desde **Go 1.17** hay ABI por **registros** (amd64). Saber la versión cambia cómo leés los argumentos.

Herramienta clave: **GoReSym** (Mandiant) recupera pclntab, tipos y metadatos y los exporta para IDA/Ghidra.

## Rust: manglado, monomorfización y traits

- **Name mangling:** dos esquemas. El **legacy** (estilo Itanium, `_ZN...E` con longitudes y un hash) y el **v0** (`_R...`, RFC 2603). Se desmanglan con **`rustfilt`** (o el soporte de Ghidra/IDA).
- **Monomorfización:** los genéricos no existen en runtime: el compilador genera **una copia por cada tipo** usado. Por eso un `Vec<T>` aparece muchas veces, una por `T`: no te confundas creyendo que son funciones distintas.
- **Trait objects (`dyn Trait`):** un *fat pointer* = **puntero a datos + puntero a vtable**. La vtable trae *drop*, tamaño, alineación y los métodos. Es el despacho dinámico de Rust y se lee parecido a una vtable de C++ (2.18).
- **Strings y colecciones:** `&str` es `(ptr, len)` UTF-8; `String` es `(ptr, len, cap)`; `Vec<T>` igual. **Sin NUL**.
- **`Option`/`Result`:** con *niche optimization*, un `Option<&T>` no ocupa un byte extra: usa el valor `0` (puntero nulo) como `None`.
- **Los *panics* son oráculos:** en modo seguro, Rust inyecta antes de indexar un array/slice una llamada a `core::panicking::panic_bounds_check` (y a `panic_fmt`/`panic` en otros casos), muchas veces con el `file:line` del fuente embebido. Esas comprobaciones te **revelan la longitud esperada de los buffers** y marcan dónde empieza cada acceso a datos: un regalo para reconstruir estructuras.

## Cómo se ve cada cosa en memoria

| Concepto | Go | Rust |
|---|---|---|
| String | `(ptr, len)` sin NUL | `&str (ptr,len)` · `String (ptr,len,cap)` |
| Despacho dinámico | interfaz = `(itab, data)` | `dyn Trait` = `(data, vtable)` |
| Nombres recuperables | pclntab (casi siempre) | símbolos manglados → `rustfilt` |
| Genéricos | parcial (desde 1.18, por *shape*) | monomorfizados: una copia por tipo |

## Ejemplo paso a paso: recuperar nombres y un trait object

*(Ejemplo **ilustrativo**: comandos sobre binarios propios compilados por vos.)*

```text
# GO: recuperar nombres aunque esté "stripeado"
GoReSym.exe -t -p .\mi_programa_go.exe > go_meta.json
#   -> funciones (pclntab) + tipos; se importan en IDA/Ghidra

# RUST: desmanglar un símbolo
echo _ZN4core3fmt9Formatter3pad17h0123456789abcdefE | rustfilt
#   -> core::fmt::Formatter::pad
```

En Go, con los nombres de la pclntab cargados, el binario «stripeado» vuelve a tener etiquetas (`main.main`, `main.validar`…) y navegás como si tuviera símbolos. En Rust, al desmanglar ves el *path* real (`core::fmt::Formatter::pad`); y cuando encontrás un par **(puntero a datos, puntero a vtable)** pasándose junto, es un `dyn Trait`: la vtable te dice qué métodos hay.

## Práctica

En tu VM, con binarios **propios**:

1. Compilá un programa en Go, «stripealo» (`-ldflags "-s -w"`) y recuperá los nombres con GoReSym; confirmá que reaparecen `main.*`.
2. Identificá una **interfaz** en el Go: encontrá el par `(itab, data)` y el método que se llama.
3. Compilá un programa en Rust con un `dyn Trait`; desmanglá sus símbolos con `rustfilt` y ubicá la vtable del trait.
4. Mostrá en ambos cómo se ve un string (ptr+len, sin NUL) frente a un string C (con NUL) de 2.1.

## Preguntas de repaso

?? ¿Qué recuperás de la `gopclntab` y por qué es el primer paso en Go?
!! Los **nombres de función** (mapa dirección → nombre), pensados para *stack traces*. Suele estar aun en binarios «stripeados», así que recuperás casi todas las etiquetas y navegás como con símbolos.

?? ¿Qué es una interfaz de Go en memoria?
!! Un par `(itab, data)`: el `itab` tiene el **tipo concreto** y la **tabla de métodos**; `data` apunta al valor. Ese par te dice qué método resuelve un despacho dinámico.

?? ¿Por qué una misma función genérica de Rust aparece muchas veces?
!! Por la **monomorfización**: Rust genera una copia por cada tipo concreto con el que se instancia el genérico. No son funciones distintas, son instancias del mismo genérico.

?? ¿Cómo se ve un `dyn Trait` y a qué se parece?
!! A un **fat pointer**: puntero a datos + puntero a **vtable**. La vtable trae drop, tamaño, alineación y los métodos. Se lee parecido a una vtable de C++ (2.18).

?? ¿Qué dos esquemas de manglado tiene Rust y cómo los leés?
!! El **legacy** (`_ZN...E`, estilo Itanium con hash) y el **v0** (`_R...`, RFC 2603). Se desmanglan con **`rustfilt`** o el soporte del desensamblador.

:::{nota} Puerta de salida
Podés: (1) recuperar nombres de un Go «stripeado» con la pclntab; (2) leer una interfaz Go como par (itab, data); (3) desmanglar símbolos Rust y reconocer monomorfización; (4) identificar un `dyn Trait` por su vtable y describir el layout de strings en ambos.
:::

## Fuentes de esta lección

- [github.com/mandiant/GoReSym](https://github.com/mandiant/GoReSym) — recuperar pclntab, tipos y metadatos de Go (conocimiento externo).
- [go.dev · runtime/symtab.go](https://go.dev/src/runtime/symtab.go) — formato de la pclntab y moduledata.
- [RFC 2603 · Rust symbol mangling v0](https://rust-lang.github.io/rfcs/2603-rust-symbol-name-mangling-v0.html) y [rustfilt](https://github.com/luser/rustfilt).
- [2.13 Huella de compilador](02-huella-compilador.html) (identificación) y [2.18 C++ profundo](02-cpp-profundo.html) (vtables y layouts).

:::{nota} Capas de esta lección
**Núcleo conceptual:** la identificación de Go/Rust/Delphi incorporada a 2.13 en la revisión de esta edición. **Conocimiento externo (agregado por esta edición):** pclntab/itab, manglado v0, monomorfización, trait objects y layouts, con documentación primaria. **Recomendación editorial:** ejemplos y práctica ilustrativos, sobre binarios propios.
:::
