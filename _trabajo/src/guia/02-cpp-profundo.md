---
title: "2.18 · C++ profundo: RTTI, vtables, STL y excepciones"
description: "Más allá de la vtable: RTTI, std::string con SSO, contenedores STL y el manejo de excepciones de C++ vistos en assembly y en el decompilador, con un ejemplo fijado a MSVC x64."
etapa: "Etapa 2 · Windows avanzado (2C)"
---

# C++ profundo: RTTI, vtables, STL y excepciones

:::{nota} Objetivo de la lección
Reconocer en un binario los rasgos de C++ que van más allá de una llamada virtual: **RTTI**, **`std::string`** (con su optimización SSO), **contenedores STL** y el **manejo de excepciones**. **Prerrequisitos:** estructuras y vtables en IDA (2.7), llamadas y marcos (2.5), PE fino (2.14).
:::

En [2.7](02-ida.html) ya reconstruiste una **vtable** y leíste una llamada virtual sobre un binario de **32 bits** (`call [edx+8]` = tercer método, porque cada puntero ocupa 4 bytes). El capítulo 33 del curso lo hace con un objeto propio: arma **dos estructuras** —el objeto y su vtable con los punteros a los métodos— y agrega cross-references manuales para las llamadas virtuales ({{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_33 C++ Clases_33 C++ Clases.txt|Reversing desde cero, cap. 33}}). Acá vamos a los otros cuatro rasgos. Lo que sigue es **conocimiento externo** salvo donde se cite.

:::{aviso} Arquitectura y compilador fijados
Toda esta lección, incluidos el ejemplo y la práctica, se fija a **MSVC x64** (Visual Studio 2022, biblioteca estándar de Microsoft). En x64 cada puntero y cada slot de vtable ocupa **8 bytes**, `this` llega en `RCX` y el RTTI usa **RVA** (desplazamientos de 32 bits desde la base de la imagen) en lugar de punteros absolutos. Cuando algo cambia en x86 se indica aparte. El layout de RTTI, de `std::string` y de los contenedores **no** es parte del estándar de C++: es un detalle de implementación de MSVC que puede variar entre versiones y entre Debug y Release. MinGW/GCC, Clang con libc++ o libstdc++ usan otros layouts y otro RTTI (Itanium ABI).
:::

## RTTI (Run-Time Type Information)

Cuando el programa usa `dynamic_cast` o `typeid` (y RTTI no está deshabilitado con `/GR-`), MSVC deja estructuras de **RTTI** colgando de la vtable: **justo antes** del primer método, en `vtable[-1]` (offset `-0x08` en x64, `-0x04` en x86), hay un puntero al *RTTI Complete Object Locator* (COL). El COL lleva al *TypeDescriptor*, que contiene el **nombre decorado** de la clase (por ejemplo, `.?AVMiClase@@`, que se desdecora a `class MiClase`), y a la jerarquía de clases base.

Diferencia importante entre arquitecturas: en **x86**, los campos del COL son punteros absolutos; en **x64**, son **RVA** de 32 bits que hay que sumar a la base de la imagen. Si sumás mal o tratás una RVA como puntero, el TypeDescriptor “no aparece”. Para el análisis, RTTI es un **regalo**: te da los nombres reales de las clases sin símbolos. IDA y Ghidra muestran la jerarquía si la reconocen.

## `std::string` y la optimización SSO

En MSVC x64 (Release), `std::string` ocupa **32 bytes**: una **unión de 16 bytes** que contiene o bien el **buffer interno** o bien un **puntero** al heap, seguida de **size** (8 bytes) y **capacity** (8 bytes). En x86 los dos contadores son de 4 bytes y el objeto ocupa 24. En Debug el objeto puede ser más grande por el soporte de depuración de iteradores: medilo con `sizeof` en tu build en lugar de suponerlo.

La clave para no confundirse es la **SSO** (*Small String Optimization*): si la cadena entra en 15 caracteres `char` (capacidad 15 más el terminador), se guarda **dentro** del objeto y no hay `new`; si es más larga, los primeros 8 bytes de la unión pasan a ser el puntero al heap. Síntoma en el reversing: para strings cortas no ves una asignación dinámica y el texto aparece **en el stack**, dentro del objeto. Para distinguir los dos casos, mirá `capacity`: si es mayor que 15, la unión contiene un puntero.

## Contenedores STL

- **`std::vector`**: tres punteros —`inicio`, `fin`, `fin_capacidad`— (24 bytes en x64 Release). El tamaño es `(fin - inicio) / sizeof(T)`; la capacidad, `(fin_capacidad - inicio) / sizeof(T)`. Un `push_back` que realoca mueve los tres.
- **`std::map`/`std::set`**: árbol rojo-negro; vas a ver nodos con punteros a padre/izquierda/derecha, un byte de color y un nodo cabecera.
- En el decompilador, estos patrones se ven como aritmética de punteros repetida sobre la misma base: candidatos a **aplicar una estructura** (como en 2.7).

## Excepciones de C++

Un `try/catch` de C++ sobre MSVC se apoya en el manejo de excepciones de Windows (lo viste en [vulnerabilidades](05-vulnerabilidades.html): SEH en 32 bits, tablas `.pdata`/`.xdata` en 64). Las señales cambian con la arquitectura:

- **x86:** la función registra un marco en la cadena SEH (`fs:[0]`) con un handler que termina en `__CxxFrameHandler3` (u otra variante según la versión).
- **x64:** no hay registro en tiempo de ejecución. La entrada de la función en `.pdata` apunta a su información de desenrollado en `.xdata`, que nombra el handler de C++ (`__CxxFrameHandler3`, o `__CxxFrameHandler4` en versiones recientes de MSVC) y sus tablas. El cuerpo del `catch` suele compilarse como un **funclet** separado.

En ambos casos, `throw` termina en `_CxxThrowException` con una estructura `ThrowInfo` que describe el tipo lanzado. No hace falta reconstruir todo: alcanza con **reconocer** que hay `try/catch` y dónde está el cuerpo del `catch`.

## Ejemplo paso a paso: vtable + RTTI (MSVC x64)

*(Ejemplo **ilustrativo**: las direcciones y las RVA están construidas con forma realista para una imagen x64 con base `0x140000000`; no son la salida de un binario compilado en esta edición.)*

```text
Base de la imagen: 0x0000000140000000

obj @ 0x000000D51C8FF8A0 (stack):
  +0x00  vptr -> 0x0000000140023A48            ; puntero a la vtable (8 bytes)

vtable @ 0x0000000140023A48:
  -0x08  0x00000001400289F0  -> RTTI Complete Object Locator   ; vtable[-1]
  +0x00  0x0000000140001200  -> MiClase::metodo1               ; slot 0
  +0x08  0x0000000140001250  -> MiClase::metodo2 (virtual)     ; slot 1
```

Siguiendo `vtable[-1]` hasta el nombre de la clase:

```text
Complete Object Locator @ 0x00000001400289F0 (campos de 4 bytes):
  +0x00  signature        = 1        ; 1 indica formato x64 con RVA
  +0x04  offset           = 0
  +0x08  cdOffset         = 0
  +0x0C  pTypeDescriptor  = 0x0002F0C8   (RVA)  -> 0x14002F0C8
  +0x10  pClassDescriptor = 0x00028A18   (RVA)
  +0x14  pSelf            = 0x000289F0   (RVA del propio COL)

TypeDescriptor @ 0x000000014002F0C8:
  +0x00  pVFTable (puntero a la vtable de type_info)
  +0x08  spare
  +0x10  ".?AVMiClase@@"   -> desdecorado: class MiClase
```

Y la llamada virtual que se lee con ese nombre:

```text
  mov  rcx, [rsp+30h]        ; rcx = this (obj)
  mov  rax, [rcx]            ; rax = vptr (0x0000000140023A48)
  call qword ptr [rax+8]     ; slot 1 = 0x08 / 8 -> MiClase::metodo2
```

Dos comprobaciones de coherencia que valen para cualquier binario x64: `pSelf` + base debe dar la dirección del propio COL (`0x140000000 + 0x289F0 = 0x1400289F0`), y `pTypeDescriptor` + base debe caer en una zona de datos donde aparezca una cadena que empiece con `.?AV` (clase) o `.?AU` (struct). Si alguna falla, estás leyendo otra cosa.

Con RTTI, `call [rax+8]` deja de ser "el slot 1" y pasa a ser `MiClase::metodo2`: el nombre te lo dio `vtable[-1]`.

**Variante x86 (solo para contraste):** con MSVC de 32 bits, el mismo objeto tendría el COL en `vtable[-1]` a `-0x04`, el COL usaría punteros absolutos (sin `pSelf`), `this` llegaría en `ECX` (`__thiscall`) y la llamada sería `mov eax,[ecx]` / `call dword ptr [eax+4]`, porque el slot 1 está a 4 bytes. No mezcles offsets de una arquitectura con la otra.

## Herencia múltiple y virtual en MSVC

Con herencia simple hay un vptr por objeto. Con **herencia múltiple** aparecen varios, y eso cambia tres lecturas.

**Varios vptr y varias vtables.** Para `class C : public A, public B` (con `A` y `B` polimórficas), el objeto `C` contiene un subobjeto `A` con su vptr al principio y un subobjeto `B` con **otro** vptr más adelante. `C` tiene entonces dos vtables (en símbolos de MSVC, `C::vftable{for A}` y `C::vftable{for B}`), y **cada una** tiene su propio Complete Object Locator en `vtable[-1]`. El campo `offset` del COL dice a qué distancia del comienzo del objeto completo está **ese** vptr: 0 para el de `A`, distinto de 0 para el de `B`. Así es como `dynamic_cast` y `typeid` encuentran el objeto completo desde cualquier subobjeto.

**Conversión de punteros.** Pasar de `C*` a `B*` **suma** un desplazamiento (`lea rdx, [rcx+10h]` o similar). Si en el binario ves que un puntero a objeto se ajusta con una constante antes de pasarlo, lo más probable es un cambio de base, no aritmética de datos.

**Thunks de ajuste.** Si `C` redefine un método virtual de `B`, la vtable de `B` dentro de `C` no puede apuntar directo a `C::metodo`, porque ese código espera un `this` de tipo `C*` y recibe un `B*`. MSVC pone en ese slot un **adjustor thunk** de dos instrucciones:

```text
; ilustrativo, MSVC x64: thunk en la vtable de B dentro de C
sub  rcx, 10h          ; vuelve de B* a C*
jmp  C::metodoDeB      ; salta a la implementación real
```

Cuando sigas un slot y caigas en un `sub rcx, N` seguido de un salto, no es ofuscación: es un ajuste de `this`, y el desplazamiento coincide con el `offset` del COL de esa vtable.

**Herencia virtual.** Con `class D : virtual public Base`, MSVC agrega un **vbptr** (*virtual base pointer*) que apunta a una **vbtable** con los desplazamientos hasta cada base virtual, porque su posición dentro del objeto completo depende de la clase más derivada. Lo vas a ver como una lectura indirecta antes de acceder a miembros de la base: cargar el vbptr, leer un desplazamiento de la vbtable y sumarlo. Con algunas combinaciones de constructores y funciones virtuales aparecen además campos `vtordisp` (controlados por la opción `/vd`). Para el análisis alcanza con reconocer el patrón; reconstruir el layout completo exige el tipo exacto.

Ejemplo de layout **ilustrativo** (x64, Release; los desplazamientos dependen de los miembros y la alineación reales):

```text
C @ obj:
  +0x00  vptr -> C::vftable{for A}   ; COL.offset = 0
  +0x08  int a  (+ relleno)
  +0x10  vptr -> C::vftable{for B}   ; COL.offset = 0x10
  +0x18  int b  (+ relleno)
  +0x20  int c
```

## Contraste: el ABI Itanium (GCC, Clang, MinGW)

Los binarios de GCC y Clang fuera de MSVC (incluido MinGW en Windows) siguen, en general, el **C++ ABI Itanium**. A pesar del nombre, es una especificación **genérica**: se escribió para Itanium, se apoya en el ABI de C de cada plataforma, y la propia especificación aclara que no es la definición autoritativa para ninguna plataforma en particular; cada plataforma puede adaptarla y documentar sus diferencias. Conviene separar dos partes.

**Vtables, RTTI y nombres (especificación principal).**

- El vptr apunta al **address point** de la vtable, que no es su comienzo: antes hay componentes en desplazamientos negativos. En 64 bits, `vptr[-1]` es el **puntero a typeinfo** y `vptr[-2]` es el **offset-to-top** (distancia desde ese vptr hasta el comienzo del objeto completo). Con bases virtuales hay además *vbase offsets* y *vcall offsets* más atrás.
- Un destructor virtual ocupa **dos** entradas consecutivas (destructor del objeto completo y destructor que además libera), a diferencia del único *scalar deleting destructor* de MSVC.
- Los nombres usan el *mangling* Itanium, que empieza con `_Z`: la vtable de `MiClase` es `_ZTV7MiClase`, su typeinfo `_ZTI7MiClase` y el nombre de tipo `_ZTS7MiClase` (cuyo texto es `7MiClase`). Si ves cadenas de este estilo y no `.?AV…@@`, cambiaste de ABI.
- En herencia múltiple también hay vtables secundarias y thunks de ajuste de `this`, con nombres propios del mangling.

**Excepciones (específico del destino).** El manejo de excepciones está en un documento aparte (ABI-EH): una capa C++ común (`__cxa_throw`, `__cxa_begin_catch` y una función *personality*) apoyada en el mecanismo de desenrollado **de la plataforma**. En sistemas ELF eso suele significar tablas DWARF en `.eh_frame` y datos específicos del lenguaje en `.gcc_except_table`. En Windows, según cómo se compiló el toolchain MinGW, puede usarse desenrollado SJLJ, DWARF o basado en las tablas SEH de Windows (`.pdata`/`.xdata`) con una personality de GCC. No supongas uno: identificalo por las secciones, los símbolos y las DLL de runtime que use el binario.

Señales rápidas para saber qué ABI tenés delante:

| Señal | MSVC | GCC/Clang (Itanium) |
|---|---|---|
| Nombre de vtable | `??_7MiClase@@6B@` | `_ZTV7MiClase` |
| RTTI en `vptr[-1]` | Puntero (x86) o puntero a COL con RVA (x64) | Puntero directo a typeinfo |
| Cadena de tipo | `.?AVMiClase@@` | `7MiClase` (en `_ZTS…`) |
| Excepciones | `__CxxFrameHandler*`, `_CxxThrowException` | `__cxa_throw`, `__gxx_personality_*` |

## Práctica

En tu VM, con un **programa propio** compilado con C++ (clases con métodos virtuales, un `std::vector`, un `std::string` corto y uno largo, y un `try/catch`):

1. Compilá con **MSVC x64** (p. ej. VS 2022, `/EHsc`) en **Debug** y en **Release** y compará. Anotá la versión exacta del compilador. Fijá el compilador: el layout de **RTTI** y la **SSO** de `std::string` son específicos de MSVC; con MinGW/Clang/libstdc++ los detalles cambian, así que el ejemplo solo es repetible con el mismo toolchain.
2. Encontrá la vtable de tu clase y, en `vtable[-1]` (`-0x08`), seguí el COL: sumá la RVA de `pTypeDescriptor` a la base de la imagen hasta llegar al nombre de la clase. Verificá `pSelf`.
3. Mirá un `std::string` corto (≤15) y uno largo: confirmá con `capacity` que el corto vive **en el objeto** (SSO) y el largo apunta al heap. Registrá `sizeof(std::string)` en Debug y en Release.
4. Ubicá el `try/catch`: en x64, buscá la entrada de la función en `.pdata`, su información de desenrollado y el handler de C++ que nombra; identificá el funclet del `catch`.
5. Agregá a tu programa una clase con **herencia múltiple** que redefina un método de la segunda base. Encontrá las dos vtables, compará el `offset` de sus COL y ubicá el adjustor thunk en la vtable de la segunda base.
6. Opcional, si tenés el toolchain instalado en la VM: compilá el mismo fuente con MinGW-w64 o Clang con libstdc++/libc++ y compará nombres de vtable, la posición del typeinfo y las funciones de excepciones con la tabla de señales. Anotá la versión exacta de cada compilador.

## Preguntas de repaso

?? ¿Dónde está el RTTI respecto de la vtable y para qué sirve al analizar?
!! En **`vtable[-1]`** (justo antes del primer método; `-0x08` en x64) hay un puntero al *Complete Object Locator*, que lleva al TypeDescriptor con el **nombre decorado de la clase**. Da los nombres reales sin símbolos.

?? En un binario MSVC x64, ¿por qué no podés tratar `pTypeDescriptor` del COL como un puntero?
!! Porque en x64 es una **RVA** de 32 bits: hay que sumarle la base de la imagen para obtener la dirección.

?? ¿Qué es la SSO de `std::string` y cómo cambia lo que ves?
!! *Small String Optimization*: las cadenas de hasta 15 `char` se guardan **dentro** del objeto (buffer interno), sin `new`. Para strings cortas no ves asignación dinámica y el texto aparece en el stack. Con `capacity` > 15, la unión contiene un puntero al heap.

?? ¿Cómo reconocés un `std::vector` en el binario?
!! Por **tres punteros** juntos (inicio, fin, fin de capacidad). El tamaño es `(fin - inicio) / sizeof(T)`; una realocación en `push_back` mueve los tres.

?? ¿Qué señal delata un `try/catch` de C++ en MSVC x64?
!! La información de desenrollado de la función (`.pdata`/`.xdata`) nombra un handler de C++ (`__CxxFrameHandler3` o `__CxxFrameHandler4`), con funclets para el `catch`; los `throw` llegan a `_CxxThrowException` con un `ThrowInfo`. En x86, en cambio, se ve el registro del marco en `fs:[0]`.

?? En una clase con herencia múltiple, un slot de vtable lleva a `sub rcx, 10h` y un `jmp`. ¿Qué es?
!! Un adjustor thunk: convierte el `this` del subobjeto base en el `this` del objeto completo antes de saltar a la implementación. El 0x10 debería coincidir con el `offset` del COL de esa vtable.

?? ¿Para qué sirve el campo `offset` del Complete Object Locator?
!! Indica a qué distancia del comienzo del objeto completo está el vptr de esa vtable; con herencia múltiple cada vtable tiene su COL y su offset.

?? En un binario GCC de 64 bits, ¿dónde está el typeinfo respecto del vptr y qué hay antes?
!! En `vptr[-1]` está el puntero a typeinfo y en `vptr[-2]` el offset-to-top; con bases virtuales hay más componentes en desplazamientos negativos.

?? ¿Por qué no basta con saber que un binario usa el ABI Itanium para saber cómo maneja excepciones?
!! Porque la especificación separa vtables y nombres del manejo de excepciones, que se apoya en el desenrollado de la plataforma: DWARF en ELF, y en MinGW puede ser SJLJ, DWARF o SEH según el toolchain.

?? Con RTTI, ¿en qué cambia leer `call [rax+8]` en x64?
!! Deja de ser "el slot 1" (`0x08 / 8`) y pasa a tener **nombre** (p. ej. `MiClase::metodo2`), porque `vtable[-1]` te dio la clase. El análisis se vuelve legible.

:::{nota} Puerta de salida
Podés: (1) seguir el RTTI desde `vtable[-1]` hasta el nombre de la clase en un binario x64, resolviendo las RVA; (2) distinguir un `std::string` con SSO de uno en heap; (3) reconocer un `std::vector` por sus tres punteros; (4) identificar un `try/catch` por su handler de C++; (5) decir qué offsets cambian entre x86 y x64; (6) reconocer varios vptr y adjustor thunks en herencia múltiple; (7) distinguir por sus señales un binario MSVC de uno con ABI Itanium.
:::

:::{nota} Lo que queda fuera
La reconstrucción completa de layouts con herencia virtual (vbtable, `vtordisp`), la jerarquía completa de `ClassHierarchyDescriptor`, `std::unordered_map`, `std::shared_ptr` y otros contenedores, las variantes del ABI Itanium por plataforma (por ejemplo ARM) y el formato de las tablas de excepciones de GCC no se desarrollan. Los layouts descritos para MSVC deben verificarse en cada versión, y los del ABI Itanium en cada plataforma y toolchain.
:::

## Fuentes de esta lección

- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_33 C++ Clases_33 C++ Clases.txt|Reversing desde cero, cap. 33}} — objeto con vtable, reconstruir las dos estructuras y cross-references manuales a los métodos virtuales.
- [Curso IDA · tutes 41–43](../ida_tutes/41.html) — strings en stack/heap, `new`/`malloc` y heap en IDA.
- [IDA y el análisis estático](02-ida.html) (2.7) — base de vtables y estructuras sobre la que se apoya esta lección.
- Microsoft Learn: [x64 calling convention](https://learn.microsoft.com/en-us/cpp/build/x64-calling-convention), [x64 exception handling](https://learn.microsoft.com/en-us/cpp/build/exception-handling-x64), [/GR (Enable Run-Time Type Information)](https://learn.microsoft.com/en-us/cpp/build/reference/gr-enable-run-time-type-information), [Multiple base classes](https://learn.microsoft.com/en-us/cpp/cpp/multiple-base-classes), [/vd (Disable Construction Displacements)](https://learn.microsoft.com/en-us/cpp/build/reference/vd-disable-construction-displacements). El layout interno del COL y de `std::string` no está documentado como contrato por Microsoft: se describe como conocimiento externo de reversing, igual que los adjustor thunks y la vbtable.
- [Itanium C++ ABI](https://itanium-cxx-abi.github.io/cxx-abi/abi.html) (vtables, RTTI y mangling) y [Itanium C++ ABI: Exception Handling](https://itanium-cxx-abi.github.io/cxx-abi/abi-eh.html).

:::{nota} Capas de esta lección
**Contenido observado en CLS:** la vtable y las dos estructuras del capítulo 33 (binario de 32 bits). **Conocimiento externo:** RTTI (`vtable[-1]`, Complete Object Locator con RVA en x64, TypeDescriptor), SSO de `std::string`, layout de los contenedores STL de MSVC handlers de excepciones de C++, herencia múltiple/virtual en MSVC y contraste con el ABI Itanium. **Recomendación editorial:** el ejemplo ilustrativo fijado a MSVC x64 y la práctica con binario propio (sin laboratorio compilado con hashes en esta edición).
:::
