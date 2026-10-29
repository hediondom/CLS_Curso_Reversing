---
title: "2.14 · PE fino: los directorios que cuentan la historia"
description: "Más allá de cabeceras e imports: Rich header, recursos, delay-load, TLS, unwind/.pdata, debug/PDB, Load Config, resolución dinámica de APIs y la capa nativa (ntdll y syscalls), y qué le dicen al que analiza."
etapa: "Etapa 2 · Windows intermedio"
---

# PE fino: los directorios que cuentan la historia

:::{nota} Objetivo de la lección
Leer los **directorios del PE** que la lección 1.4 solo nombra, y entender qué pista da cada uno **antes** de llegar al entry point. **Prerrequisitos:** [El formato PE](01-pe.html) (1.4), [TLS](02-tls.html) (2.11), [huella de compilador](02-huella-compilador.html) (2.13).
:::

En [1.4](01-pe.html) viste la cabecera, las secciones, los imports y la IAT. Acá vamos a los **otros `DataDirectory`**, que muchas veces resuelven el análisis sin ejecutar nada. Todo esto se lee con **PE-bear**, **CFF Explorer** o el navegador de IDA; el recorrido VA↔RVA↔offset es el del capítulo 05 ({{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_05 Virtual Adress, RVA, Offsets y Desplazamientos_05 Virtual Adress, RVA, Offsets y Desplazamientos.txt|Reversing desde cero, cap. 05}}). El contenido de esta lección es **conocimiento externo** salvo donde se cite.

## Rich header

Entre el `DOS stub` y la cabecera PE, los linkers de Microsoft dejan el **Rich header**: una lista cifrada (XOR con una clave que está ahí mismo) de qué herramientas y versiones tocaron el binario (`@comp.id`). Qué te dice:

- Es casi una **firma de MSVC**: si está, se armó con el toolchain de Microsoft; su **ausencia sugiere** otro compilador (MinGW u otro) o que lo removieron, pero **no lo prueba** (ver [2.13](02-huella-compilador.html)).
- Las versiones ayudan a **datar** el binario y a agrupar muestras de la misma máquina de compilación.

## Recursos (`.rsrc`)

El **directorio de recursos** guarda íconos, menús, *dialogs*, *string tables*, *version info* y, a veces, **blobs** (otro ejecutable, una config, una clave). Qué mirar:

- *Version info*: nombre de producto, compañía, versión. Pistas de origen (y, en malware, mentiras).
- *Dialogs* y *string tables*: los textos de la interfaz, que te llevan a la lógica (como las strings del `.rdata`).
- Un recurso **grande o de tipo raro** (RCDATA) suele ser un payload embebido: a mirar con cuidado.

## Imports diferidos (*delay-load*)

Además de la tabla de imports normal, el PE puede tener un directorio de **delay-load**: DLLs que **no** se cargan al inicio sino la **primera vez que se usan**. Consecuencia para el análisis: una dependencia puede **no aparecer** en la lista de imports "a primera vista" y cargarse recién en runtime vía `__delayLoadHelper2`. Si buscás una API y no está en los imports normales, revisá delay-load.

## Excepciones y unwind (`.pdata`)

En x64, el manejo de excepciones **no** vive en el stack como el SEH de 32 bits: está en tablas `.pdata`/`.xdata` (ver la [rama de vulnerabilidades](05-vulnerabilidades.html), cap. 36). Para el análisis, esas tablas sirven para:

- **Delimitar funciones** aunque no haya símbolos (cada entrada cubre un rango de código).
- Entender el prólogo/epílogo (qué registros se salvan), útil al reconstruir marcos.

## Debug directory y PDB

El **directorio de debug** puede traer la **ruta del `.pdb`** (p. ej. `D:\proyectos\cosa\Release\cosa.pdb`) y un GUID/age para emparejar símbolos. Qué te da:

- La **ruta** filtra información: nombre de proyecto, usuario, estructura de carpetas del que lo compiló.
- El GUID/age permite **cargar los símbolos** correctos (si los tenés o están en un symbol server), lo que vuelve legible un binario (como el caso con `.pdb` de la [serie de estructuras del Curso IDA](../ida_tutes/27.html)).

## Load Config

El **`Load Config` directory** declara mitigaciones y metadatos que el loader usa:

- Puntero al **`security cookie`** (el `/GS` que viste en [vulnerabilidades](05-vulnerabilidades.html)).
- Tabla **SEH segura** (SafeSEH) en 32 bits.
- Tablas de **CFG** (`GuardCFFunctionTable`): los destinos válidos de llamadas indirectas.

Leerlo te dice **qué defensas tiene** el binario sin ejecutarlo, y complementa la tabla de mitigaciones de la rama de vulnerabilidades.

## Cuando los imports no cuentan todo: resolución dinámica de APIs

La tabla de imports solo lista lo que el programa enlazó **al compilar**. Un programa puede obtener la dirección de cualquier función **en ejecución**, y entonces esa API no aparece en los imports. Es una de las primeras cosas que se encuentran al analizar binarios reales, y hay tres formas típicas, de más visible a menos visible (**conocimiento externo** salvo lo citado):

1. **`LoadLibrary` + `GetProcAddress`.** El programa carga la DLL y pide la dirección por nombre. Señales: los dos imports, cadenas con nombres de API (`"VirtualAlloc"`, `"MessageBoxW"`) y, después, una llamada **indirecta** a través de un registro o una variable (`call rax`, `call [rbp-18h]`). La propia documentación de Microsoft usa este mecanismo para funciones sin biblioteca de importación, como las de `ntdll`.
2. **Recorrer el PEB y la tabla de exports.** Sin llamar a ninguna API: el código lee el PEB (`gs:[60h]` en x64, `fs:[30h]` en x86), sigue `Ldr` hasta la lista `InMemoryOrderModuleList` —una lista doblemente enlazada de entradas con la base y el nombre de cada módulo cargado— y, en el módulo elegido, recorre el **directorio de exports** del PE (nombres, ordinales y direcciones) hasta encontrar la función. Señales: accesos a esos offsets fijos, un bucle que compara nombres de módulo y otro que recorre `AddressOfNames`.
3. **Hashing de nombres de API.** Igual que el anterior, pero en vez de comparar el nombre con una cadena, calcula un **hash** de cada nombre exportado y lo compara con una **constante**. No queda ninguna cadena con el nombre de la API en el binario. Señales: un bucle corto que recorre los bytes de un nombre con rotaciones, `xor` o sumas, seguido de un `cmp` contra un valor de 32 bits. Como la misma función de hash produce la misma constante para el mismo nombre, esas constantes se pueden buscar en bases públicas de hashes conocidos para nombrar la API.

Qué registrar en el análisis: qué APIs resuelve dinámicamente (con evidencia: cadena, constante o traza), **dónde** guarda las direcciones (una tabla propia funciona como una IAT paralela) y desde dónde se llaman. En dinámico, un breakpoint en `GetProcAddress` o en el retorno del resolvedor te da la lista real.

Un detalle de lectura relacionado: en binarios modernos vas a ver imports de nombres como `api-ms-win-core-…`. Son **API sets**: nombres de **contratos**, no archivos; el cargador los resuelve contra la DLL que implementa cada función en esa versión de Windows, y puede no existir ningún archivo con ese nombre.

## Firma Authenticode: integridad y procedencia

Un PE puede incluir una firma **Authenticode** en la tabla de certificados del directorio de datos; también puede tener firma de catálogo. La firma permite comprobar integridad según las reglas de hash de PE y validar la cadena del certificado, pero **no prueba que el programa sea benigno** ni que su editor sea confiable para cualquier uso. Una firma ausente tampoco demuestra intención maliciosa. La entrada de la tabla de certificados es una excepción importante al modelo general de directorios: su ubicación se expresa como **offset de archivo**, no como RVA.

Al revisar un binario, registrá el resultado de verificación, el sujeto del certificado, la cadena y el sello de tiempo cuando estén disponibles. Interpretá todo como evidencia de identidad e integridad, no como veredicto de seguridad.

## Resolución efectiva de DLL

La IAT dice qué módulos y funciones necesita el binario; **no siempre revela qué archivo concreto se cargó**. Si el nombre no especifica ruta, la ubicación efectiva depende del orden de búsqueda de Windows y del contexto: directorio de la aplicación, módulos ya cargados, Known DLLs, API sets, redirecciones y configuración del proceso. Por eso, al analizar un problema de carga, distinguí el nombre importado de la ruta observada en ejecución. En programas propios, usar rutas explícitas y las opciones seguras del cargador reduce ambigüedades; en reversing, documentá la ruta efectiva y el contexto, sin inferirla solo del nombre de la DLL.

### Aplicaciones empaquetadas, manifiestos y búsqueda segura

No hay un único orden que puedas aplicar sin identificar el tipo de aplicación y la forma de carga. En apps de escritorio sin paquete, las redirecciones side-by-side declaradas por manifiestos pueden intervenir. En apps empaquetadas participa el **package dependency graph**, cuyas dependencias se buscan según el manifiesto del paquete. También importan la lista de módulos ya cargados, Known DLLs, API sets, redirecciones y si el programa pidió una ruta completa o usó flags de búsqueda.

Para analizarlo, registra si el ejecutable está empaquetado, qué manifiesto y flags de carga observas, el nombre solicitado y el **path real** de la imagen cargada. Confírmalo en un proceso propio con debugger o Process Monitor; no infieras el archivo final por el nombre del import. En software propio, preferí rutas explícitas o LoadLibraryEx con flags de búsqueda seguros y dependencias conocidas.

## La capa nativa: de kernel32 a ntdll y la llamada al sistema

Una llamada documentada de Win32 no es la última parada. En los sistemas actuales, buena parte de la implementación de las funciones de `kernel32.dll` vive en `kernelbase.dll` (conocimiento externo), y casi todo lo que necesita al kernel termina en una función **nativa** de `ntdll.dll` con prefijo `Nt` o `Zw`, que hace la **llamada al sistema** y entra en kernel mode. Microsoft documenta que, llamadas desde user mode, las versiones `Nt` y `Zw` se comportan igual, y que la API nativa es en gran parte interna: funciones como `NtQueryInformationProcess` “pueden cambiar o no estar disponibles” en versiones futuras.

Cómo se ve al analizar:

- En una pila de llamadas, el último frame de user mode suele ser `ntdll!NtAlgo`, no la API que llamó el programa. Para entender una operación de archivo, por ejemplo, la cadena típica es `CreateFileW` → (kernelbase) → `NtCreateFile` → kernel.
- Un *stub* de `ntdll` en x64 es corto: carga el número de servicio en `EAX` y ejecuta `syscall`. Ese número **cambia entre builds** de Windows.
- **Llamadas al sistema directas.** Si encontrás una instrucción `syscall` (o `sysenter`/`int 2Eh` en x86) **dentro del código del propio programa**, fuera de `ntdll`, el programa está saltándose la capa de user mode: no pasa por las funciones de `ntdll` donde un depurador, una herramienta de monitoreo o un producto de seguridad suelen observar. Como los números cambian por build, ese código o los tiene fijos (y queda atado a una versión) o los lee de `ntdll` en ejecución. Es una señal de anti-análisis o evasión para **documentar**, no algo para replicar.

## Ejemplo ilustrativo: un resolvedor sin cadenas

*(Listado **ilustrativo** de x64, construido para mostrar el patrón; los offsets siguen las estructuras documentadas `PEB`, `PEB_LDR_DATA` y `LDR_DATA_TABLE_ENTRY`; la constante de hash es inventada.)*

```asm
mov   rax, gs:[60h]          ; PEB
mov   rax, [rax+18h]         ; PEB->Ldr
mov   rsi, [rax+20h]         ; Ldr->InMemoryOrderModuleList.Flink
siguiente_modulo:
mov   rdi, [rsi+20h]         ; DllBase (offset relativo a InMemoryOrderLinks)
; ... ubicar el directorio de exports de ese módulo ...
siguiente_nombre:
xor   edx, edx               ; hash = 0
hash_loop:
movzx eax, byte ptr [rcx]    ; siguiente carácter del nombre exportado
test  al, al
jz    comparar
ror   edx, 0Dh               ; rotar ...
add   edx, eax               ; ... y sumar: una función de hash simple
inc   rcx
jmp   hash_loop
comparar:
cmp   edx, 1A2B3C4Dh         ; ¿es el hash de la API buscada? (valor ilustrativo)
jne   siguiente_nombre
```

Lectura: no hay `GetProcAddress` ni cadenas con nombres de API; la pista son `gs:[60h]`, la cadena de offsets hacia la lista de módulos, el bucle de hash y la constante. En el informe se anota “resolución dinámica por hash; API identificada como X porque la constante coincide con el hash de su nombre con esta función”, con la evidencia de esa coincidencia.

## Ejemplo paso a paso: un `Load Config` y un debug directory reales de leer

*(Ejemplo **ilustrativo**: valores construidos; mostrá los campos, no las direcciones exactas.)*

Compilado con `/GS /guard:cf`, PE-bear muestra:

```text
Load Config Directory
  Size                         0x0118
  SecurityCookie               0x0040B120   → hay /GS (stack canary)
  SEHandlerTable               0x00000000   → x64: SEH va por .pdata, no acá
  GuardCFCheckFunctionPointer  0x0040B008
  GuardCFFunctionTable         0x0040A800
  GuardFlags                   0x00010500   → CFG activo (INSTRUMENTED)

Debug Directory  (type = CODEVIEW / RSDS)
  PDB: D:\dev\miapp\x64\Release\miapp.pdb
  GUID: 7F3A... age 1
```

Sin ejecutar nada ya sabés: tiene **/GS** y **CFG**, es **x64** (SEH por tablas), y el `.pdb` filtra la ruta de compilación (`D:\dev\miapp\...`: usuario, proyecto, configuración Release). Ese GUID + age es lo que usarías para cargar los símbolos correctos.

## Práctica

En tu VM, con un **binario propio** (compilá con /GS /guard:cf en MSVC) y PE-bear:

1. Encontrá el **Rich header** y confirma qué sugiere al compararlo con una compilación propia de MinGW.
2. Abrí el directorio de **recursos** y ubicá version info y, si pusiste uno, un RCDATA.
3. Mirá **Load Config**: ¿apunta a un security cookie? ¿Hay tabla CFG?
4. Mirá el **debug directory**: ¿quedó la ruta del PDB? Anotá qué revela de tu entorno.
5. En un programa propio, obtené una API con LoadLibraryW + GetProcAddress y confirma por qué no figura como import estático.
6. En el depurador, seguí una llamada de tu programa hasta ntdll y registra lo que puedes concluir del stub en tu build, sin generalizar números de servicio entre versiones.
7. Con Get-AuthenticodeSignature (PowerShell) o signtool verify /pa (Windows SDK), registra el estado de firma y los datos del firmante; anota que una firma válida no demuestra que el programa sea benigno.
8. En una aplicación propia, identifica si está empaquetada y qué manifiesto/flags de carga aplican; compara el nombre solicitado de una DLL con la ruta realmente observada en el proceso.

## Preguntas de repaso

?? ¿Qué te dice la presencia (o ausencia) del Rich header?
!! Que el binario se armó (o no) con el toolchain de **MSVC**; además sus `@comp.id` ayudan a datar y agrupar. Su ausencia sugiere MinGW u otro compilador.

?? Buscás una API en los imports y no está, pero sabés que el programa la usa. ¿Dónde más mirás?
!! En los **imports diferidos** (delay-load): esa DLL se carga la primera vez que se usa, vía `__delayLoadHelper2`, y no aparece en la tabla de imports normal.

?? ¿Para qué sirve `.pdata` al analizar un x64 sin símbolos?
!! Para **delimitar funciones** (cada entrada cubre un rango) y entender el prólogo/epílogo; en x64 el unwind vive ahí, no en el stack.

?? ¿Qué información sensible puede filtrar el debug directory?
!! La **ruta del `.pdb`**: nombre de proyecto, usuario y estructura de carpetas del que compiló; y el GUID/age para emparejar símbolos.

?? Un programa usa una API que no figura en sus imports ni en sus cadenas. ¿Qué buscás?
!! Resolución dinámica por **hash**: acceso al PEB (`gs:[60h]`/`fs:[30h]`), recorrido de la lista de módulos y de los exports, un bucle que calcula un hash y un `cmp` contra una constante.

?? ¿Qué es un import `api-ms-win-core-…`?
!! Un **API set**: el nombre de un contrato que el cargador resuelve contra la DLL que lo implementa; puede no existir un archivo con ese nombre.

?? ¿Por qué una instrucción `syscall` en el código del propio programa es una señal a documentar?
!! Porque el programa entra al kernel sin pasar por `ntdll`, donde suelen observar depuradores y herramientas; además los números de servicio cambian entre builds.

?? ¿Qué defensas podés leer en Load Config sin ejecutar el binario?
!! El **security cookie** (`/GS`), la tabla **SafeSEH** (32 bits) y las tablas de **CFG** (destinos válidos de llamadas indirectas).

:::{nota} Puerta de salida
Podés: (1) ubicar y explicar Rich header, recursos, delay-load, `.pdata`, debug/PDB y Load Config y firma Authenticode; (además) explicar por qué la IAT no determina por sí sola la ruta efectiva de una DLL; (2) decir qué pista da cada uno antes del entry point; (3) deducir compilador y defensas de un binario solo leyendo sus directorios; (4) reconocer resolución dinámica de APIs (por nombre, por recorrido del PEB y por hash); (5) ubicar la capa nativa (`ntdll`, `Nt*`, `syscall`) en una pila de llamadas y reconocer una llamada al sistema directa.
:::

:::{nota} Lo que queda fuera
Escribir resolvedores o llamadas al sistema propias, las tablas de números de servicio por versión, el formato completo de `LDR_DATA_TABLE_ENTRY` (la mayoría de sus campos son reservados) y las técnicas para ocultar imports en sí no se desarrollan: la lección enseña a reconocerlas.
:::

## Fuentes de esta lección

- Microsoft Learn: [Understanding executable file signing](https://learn.microsoft.com/en-us/windows/win32/secbp/understanding-pe-signatures), [Dynamic-link library search order](https://learn.microsoft.com/en-us/windows/win32/dlls/dynamic-link-library-search-order), [Dynamic-link library security](https://learn.microsoft.com/en-us/windows/win32/dlls/dynamic-link-library-security).

- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_05 Virtual Adress, RVA, Offsets y Desplazamientos_05 Virtual Adress, RVA, Offsets y Desplazamientos.txt|Reversing desde cero, cap. 05}} — VA, RVA y offsets: cómo se navega dentro del PE.
- [El formato PE](01-pe.html) (1.4) — base: cabeceras, secciones, imports e IAT, sobre la que se apoya esta lección.
- [Curso IDA · tutes 25–28](../ida_tutes/27.html) — uso de `.pdb`/símbolos para volver legible un binario.
- Microsoft Learn: [PE Format](https://learn.microsoft.com/en-us/windows/win32/debug/pe-format), [GetProcAddress](https://learn.microsoft.com/en-us/windows/win32/api/libloaderapi/nf-libloaderapi-getprocaddress), [LoadLibraryW](https://learn.microsoft.com/en-us/windows/win32/api/libloaderapi/nf-libloaderapi-loadlibraryw), [PEB](https://learn.microsoft.com/en-us/windows/win32/api/winternl/ns-winternl-peb), [PEB_LDR_DATA](https://learn.microsoft.com/en-us/windows/win32/api/winternl/ns-winternl-peb_ldr_data), [Windows API sets](https://learn.microsoft.com/en-us/windows/win32/apiindex/windows-apisets), [Using Nt and Zw versions of the native system services](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/using-nt-and-zw-versions-of-the-native-system-services-routines), [NtQueryInformationProcess](https://learn.microsoft.com/en-us/windows/win32/api/winternl/nf-winternl-ntqueryinformationprocess).

:::{nota} Capas de esta lección
**Contenido observado en CLS:** el recorrido VA/RVA/offset del capítulo 05, la base de PE de 1.4 y el uso de símbolos del Curso IDA. **Conocimiento externo:** Rich header, directorio de recursos, delay-load, `.pdata`/unwind, debug/PDB, Load Config, resolución dinámica de APIs (incluido el hashing), API sets, Authenticode, búsqueda de DLL en apps empaquetadas y no empaquetadas, resolución efectiva de DLL y la capa nativa. **Ejemplo ilustrativo:** el resolvedor por hash (constante inventada). **Recomendación editorial:** leer los directorios antes del entry point y la práctica con binario propio.
:::
