---
title: "2.13 · Huella de compilador: saber con qué se hizo"
description: "Reconocer si un binario es MSVC, MinGW, Delphi, VB6, MFC, Go o Rust por sus imports, strings, runtime y estructuras — para leerlo con la estrategia correcta."
etapa: "Etapa 2 · Windows intermedio"
---

# Huella de compilador: saber con qué se hizo

:::{nota} Objetivo de la lección
Antes de leer una sola instrucción, saber **con qué compilador/runtime** se armó el binario, porque eso cambia todo: dónde está la lógica, cómo se ven las llamadas, qué estructuras esperar. **Prerrequisitos:** PE e imports (1.4), IDA (2.7), MFC (2.12).
:::

## Por qué mirar esto primero

El mismo programa en C se ve **distinto** según el compilador, y un programa de Delphi o Visual Basic no se parece en nada a uno de C. Identificar la huella te ahorra horas: te dice si vas a encontrar un `main` clásico, un runtime que rutea todo, p-code en vez de nativo, o una maraña de clases. Es lo primero que hace un analista con experiencia (**recomendación editorial**).

## Tabla de huellas

**Conocimiento externo** (pistas que se confirman en los imports, strings y secciones del PE):

| Compilador / runtime | Pistas típicas |
|---|---|
| **MSVC** (Visual C++) | **Rich header** en la cabecera (ver [2.14](02-pe-fino.html)); `__security_cookie`, `__scrt_common_main`, `__acrt_*`; ruta a un `.pdb`; runtime `vcruntime###.dll`/`ucrtbase.dll` |
| **MinGW/GCC** | `msvcrt.dll`, `__mingw_*`, `libgcc_s_*`, `___chkstk_ms`, sección `.eh_frame`; **sin** Rich header; strings de rutas tipo `/mingw/...` |
| **Delphi** | Strings `Sysutils`, `System`, `Classes`, `TForm`, `TObject`; símbolos con `@`; VMT (tabla de métodos) al inicio del objeto; secciones `.itext`/`.data` particulares |
| **Visual Basic 6** | Import de `MSVBVM60.DLL`; funciones `__vba*`; strings `Project1`/`Form1`; puede ser **p-code** (interpretado) o nativo |
| **MFC** (sobre MSVC) | `mfc###u.dll` (p. ej. `mfc140u.dll`), `AfxWinInit`/`AfxWinMain`, clases `CWnd`/`CDialog`/`CString`, message map (ver [2.12](02-mfc.html)) |
| **Go** | Binario grande y enlazado estáticamente, con pocos imports; cadena `Go build ID`; nombres de paquetes y funciones como `main.main`, `runtime.` o `fmt.` visibles aunque no haya símbolos de depuración; sección o datos con la tabla `pclntab` |
| **Rust** | Rutas de código fuente en mensajes de pánico (`src/main.rs`, `library/core/src/...`); símbolos con mangling `_ZN...E` (antiguo) o `_R...` (v0); mensajes como «called `Option::unwrap()` on a `None` value»; con el target `-msvc` puede traer **Rich header** del linker de Microsoft |

Regla práctica: **mirá primero los imports** (qué DLLs de runtime trae) y las **strings** (nombres de clases/módulos); con eso ya ubicás la familia.

## Dos casos que cambian la estrategia

- **VB6 p-code vs. nativo.** Si es p-code, el código "real" no es x86: es bytecode que interpreta `MSVBVM60.DLL`. Leer el x86 directo no sirve; hay que usar herramientas específicas de VB. Reconocerlo temprano evita perder tiempo.
- **Delphi.** Las APIs no se llaman como en C: el objeto trae su **VMT** al inicio y los métodos se resuelven por tabla. Esperar un `main` con `CreateWindow` directo te confunde.

En CLS esto está **como material, no como lección**: en `Teorias_Numeradas` hay **decenas de títulos de Delphi** y **varios de Visual Basic/VB6, p-code y Java** ([índice clasificado](../teorias.html)). Son conteos **por subcadena del título** (aproximados, sin abrir los contenedores): orientan para profundizar, no son prueba. El único runtime trabajado a fondo en el curso es **MSVC/C++** (y MFC en la [2.12](02-mfc.html), observado en el cap. 39: {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_39 TIPS 2 MFC_TIPS 2 MFC.txt|Reversing desde cero, cap. 39}}).

## Lenguajes que no se leen como C: Go, Rust y Delphi

Los tres producen código nativo x86/x64, así que IDA y Ghidra los abren sin problema. Lo que cambia es **qué esperar** del listado. Todo este apartado es **conocimiento externo** al material de CLS; lo citado viene de la documentación de cada lenguaje.

**Go.** Un "hola mundo" en Go pesa varios megabytes porque trae enlazado el runtime completo (planificador de goroutines, recolector de basura). Para leerlo:

- **Los nombres de funciones sobreviven.** El runtime de Go necesita una tabla que relaciona direcciones con funciones y líneas (`pclntab`) para armar trazas de pila, perfilar y recolectar basura, así que está en el binario aunque se hayan quitado los símbolos de depuración. Herramientas e IDA/Ghidra recientes la usan para recuperar nombres como `main.main` o `main.verificarClave`. Empezá por las funciones del paquete `main`: el resto suele ser runtime y biblioteca estándar.
- **Las cadenas no terminan en `0`.** Un `string` de Go es puntero + longitud; el compilador guarda muchas cadenas pegadas en una sola zona y el buscador de strings las muestra como un bloque largo. Para saber dónde termina una, buscá la longitud que se carga junto al puntero.
- **Convención propia.** Go no usa la convención x64 de Windows de [Llamadas y convenciones](02-llamadas.html) para sus funciones internas: tiene su propio ABI (en versiones recientes pasa argumentos en registros, en otro orden). Al comienzo de casi toda función vas a ver una **comprobación de pila** —una comparación del puntero de pila con un límite y un salto a `runtime.morestack`— que no es lógica del programa y se puede saltar con la vista.

**Rust.** También enlaza estáticamente su biblioteca estándar, pero suele usar el runtime de C de la plataforma.

- **Huella engañosa.** Con el target `x86_64-pc-windows-msvc` el binario lo enlaza el linker de Microsoft: puede tener Rich header e importar `vcruntime140.dll`. Ver esas pistas y concluir "C++ de MSVC" es el error típico; las rutas `.rs` y los mensajes de pánico lo desmienten.
- **Cadenas como puntero + longitud** (`&str`), igual que en Go: sin `0` final.
- **Nombres con mangling.** El esquema antiguo se parece al de C++ de Itanium (`_ZN...` con un hash al final) y el esquema **v0** empieza con `_R`; ambos se pueden demanglear con las herramientas de Rust.
- **Mucho código de comprobación.** Chequeos de límites de arreglos y desbordes que terminan en una función de pánico. Las ramas que van al pánico son el camino de error; la lógica está en el otro.

**Delphi** (amplía la fila de la tabla).

- **Formularios como recursos.** Los formularios (`TForm`) se guardan como recursos `RCDATA` que empiezan con la firma `TPF0`; ahí están los nombres de los controles y los **nombres de los manejadores de eventos** (por ejemplo `Button1Click`), que te llevan directo a la lógica.
- **Convención `register`.** En Delphi de 32 bits la convención por defecto pasa los tres primeros argumentos en `EAX`, `EDX` y `ECX`, no en el stack: un método recibe `Self` en `EAX`. Si leés el listado esperando `stdcall`, los argumentos "desaparecen".
- **Cadenas con cabecera.** Los `string` largos de Delphi guardan contador de referencias y longitud **antes** del primer carácter, así que el puntero apunta al texto pero hay datos en offsets negativos.
- **RTTI y VMT.** Los nombres de clases y la tabla de métodos virtuales permiten reconstruir jerarquías; existen herramientas específicas para Delphi que lo automatizan.

:::{aviso} Pistas, no pruebas
Una huella es un **indicio**, no un certificado. La **ausencia de Rich header** sugiere que no es MSVC, pero no **demuestra** MinGW (podría ser otro linker o estar removido). Y una app **MFC enlazada estáticamente** puede **no** importar `mfc###u.dll`. Confirmá siempre con varias señales juntas.
:::

## Ejemplo paso a paso: el mismo `hola.c`, dos compiladores

*(Ejemplo **ilustrativo**: imports representativos; varían según versión.)*

El mismo programa compilado en MSVC y en MinGW deja huellas distintas:

```text
MSVC (cl hola.c)                     MinGW (gcc hola.c)
──────────────────────────           ──────────────────────────
Rich header: presente                Rich header: AUSENTE
Imports:                             Imports:
  VCRUNTIME140.dll                     msvcrt.dll
    __C_specific_handler                 __getmainargs, __set_app_type
    memcpy, __current_exception          _onexit, __p__fmode
  api-ms-win-crt-stdio-l1-1-0.dll      KERNEL32.dll
    __stdio_common_vfprintf          Secciones: .text .data .rdata
  KERNEL32.dll                                   .eh_frame  ← GCC
Secciones: .text .rdata .data        Símbolos: __mingw_*, ___chkstk_ms
  (sin .eh_frame)
```

Con solo mirar imports y secciones ya decidís: Rich header + `api-ms-win-crt-*` + `__C_specific_handler` ⇒ **MSVC**; `msvcrt.dll` + `__mingw_*` + `.eh_frame` y sin Rich header ⇒ **MinGW** (recordá la salvedad de arriba: es indicio, no prueba).

## Práctica

En tu VM, con **programas propios**:

1. Compilá el **mismo** `hola.c` con **MSVC** (`cl`) y con **MinGW** (`gcc`). Abrí ambos en PE-bear/IDA.
2. Armá una tabla comparando: DLLs de runtime en imports, presencia de Rich header, strings de rutas, secciones (`.eh_frame` vs. no).
3. Si tenés cómo, compilá algo mínimo en **Delphi** o abrí un binario VB6 de práctica y buscá `MSVBVM60.DLL` o `TForm`/`TObject`.
4. Escribí en una línea, para cada binario, "esto es X porque veo Y".
5. Si tenés Go o Rust instalados, compilá un programa propio mínimo que compare una cadena ingresada con una fija. En el de Go, ubicá `main.main` y la comprobación de pila del inicio; en el de Rust, buscá las rutas `.rs` y mirá si hay Rich header. En ambos, encontrá la cadena fija y anotá dónde está su longitud.

:::{nota} Lo que queda fuera
Reconstruir tipos de Go (interfaces, *maps*, canales) o los genéricos y *traits* de Rust, analizar p-code de VB6 y usar herramientas específicas de Delphi. Esta lección enseña a **reconocer** el lenguaje y a no leerlo con expectativas de C; profundizar cada uno es un tema propio.
:::

## Preguntas de repaso

?? ¿Por qué conviene identificar el compilador antes de leer el código?
!! Porque determina **dónde está la lógica y cómo se ve**: un binario Delphi, uno VB6 p-code y uno MSVC se analizan de formas distintas. Saberlo evita buscar un `main` clásico donde no lo hay.

?? ¿Qué pista distingue MSVC de MinGW de un vistazo?
!! MSVC trae **Rich header** y runtime `vcruntime`/`ucrtbase` con `__security_cookie`; MinGW usa `msvcrt.dll`, símbolos `__mingw_*`, `.eh_frame` y **no** tiene Rich header.

?? Ves import de `MSVBVM60.DLL`. ¿Qué implica y qué riesgo hay?
!! Es **Visual Basic 6**. Riesgo: puede ser **p-code** (bytecode interpretado por esa DLL), así que leer el x86 directo no te muestra la lógica real; necesitás herramientas de VB.

?? ¿Cómo reconocés Delphi?
!! Strings como `Sysutils`/`System`/`Classes`/`TForm`/`TObject`, símbolos con `@` y la **VMT** al inicio de los objetos; las llamadas no se ven como en C.

?? Un binario tiene Rich header e importa `vcruntime140.dll`, pero aparecen rutas `src/main.rs`. ¿Qué es?
!! Probablemente **Rust** compilado con el target `-msvc`: el linker de Microsoft deja el Rich header y el runtime de C, pero las rutas `.rs` y los mensajes de pánico delatan el lenguaje. Es el ejemplo de por qué una sola pista no alcanza.

?? ¿Por qué en un binario de Go sin símbolos podés ver nombres como `main.main`?
!! Porque el runtime necesita la tabla `pclntab` (direcciones → funciones y líneas) para trazas de pila, perfilado y recolección de basura, y quitar los símbolos de depuración no la elimina.

?? En Delphi de 32 bits, ¿dónde llegan los primeros argumentos de un método?
!! En `EAX`, `EDX` y `ECX` (convención `register`); `Self` viene en `EAX`. Leerlo como `stdcall` hace que los argumentos parezcan faltar.

?? ¿Qué parte de esto está respaldada por material de CLS y qué es externo?
!! MFC está observado (cap. 39) y hay **títulos** de Delphi/VB/Java en `Teorias_Numeradas` (no leídos). La tabla de huellas de MSVC/MinGW/Delphi/VB6/Go/Rust y el apartado de lenguajes no-C son **conocimiento externo**.

:::{nota} Puerta de salida
Podés: (1) decir con qué compilador/runtime se hizo un binario y por qué; (2) distinguir MSVC de MinGW por imports/Rich header/secciones; (3) reconocer VB6 (y el riesgo de p-code) y Delphi; (4) justificar cada conclusión con una pista concreta del PE; (5) reconocer un binario de Go o de Rust y explicar qué cambia al leerlo (nombres recuperables, cadenas con longitud, comprobaciones del runtime).
:::

## Fuentes de esta lección

- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_39 TIPS 2 MFC_TIPS 2 MFC.txt|Reversing desde cero, cap. 39}} — MFC como capa sobre la API (huella de framework).
- [Teorias_Numeradas · clasificación](../teorias.html) — títulos de Delphi, Visual Basic/VB6, p-code y Java (conteo aproximado por subcadena del título); material para profundizar, no leído.
- Go (conocimiento externo): [paquete debug/gosym](https://pkg.go.dev/debug/gosym) y [diseño de la tabla de símbolos de Go 1.2](https://go.dev/s/go12symtab) — la tabla `pclntab` y por qué la necesita el runtime; [A Quick Guide to Go's Assembler](https://go.dev/doc/asm).
- Rust (conocimiento externo): [Symbol Mangling](https://doc.rust-lang.org/rustc/symbol-mangling/index.html) y [esquema v0](https://doc.rust-lang.org/rustc/symbol-mangling/v0.html); [tipo primitivo str](https://doc.rust-lang.org/std/primitive.str.html).
- Delphi: la convención `register`, la firma `TPF0` de los formularios y la cabecera de los `string` son conocimiento externo sin enlace verificado en esta revisión (la documentación de Embarcadero no respondió durante la verificación).

:::{nota} Capas de esta lección
**Contenido observado en CLS:** la huella de MFC del capítulo 39 y los conteos por título de `Teorias_Numeradas`. **Conocimiento externo:** la tabla de huellas (Rich header, `MSVBVM60.DLL`, VMT de Delphi, `.eh_frame` de MinGW, Go y Rust), el caso p-code y las particularidades de lectura de Go, Rust y Delphi. **Recomendación editorial:** mirar imports y strings primero y la práctica comparativa MSVC/MinGW.
:::
