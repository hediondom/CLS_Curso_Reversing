# Entregable 3 — Nueva Versión Mejorada de la Guía (Suplemento e Integración Intacta)

**Versión:** Edición 5 — Revisión Ampliada 5.1 (29 de octubre de 2026).  
**Regla Editorial Principal aplicada:** El 100 % del contenido de CLS (texto, ejemplos, tablas, estructura, glosario y apéndices) se conserva **exactamente como está**, sin reescribir, resumir, corregir en silencio ni eliminar ni un solo carácter. Cada precisión sobre el material original va en una **Nota editorial separada** y cada adición técnica está marcada explícitamente como **«Ampliación editorial basada en fuentes externas»**, diferenciando entre *Hecho confirmado*, *Recomendación editorial* e *Inferencia*, con citas verificables enlazadas al Entregable 5.

---

## 3.1 Declaración de Preservación Literal y Limitaciones de Formato

1. **Archivos originales intactos:** El archivo `CLS_Curso_Reversing.pdf` (403 páginas, 4.477.417 bytes, SHA-256 verificado en el Entregable 6), así como todos los archivos `.md`, `.html`, `.csv` y `.py` existentes en `CLS_Guia/`, permanecen sin ninguna modificación.
2. **Qué partes se preservaron literalmente:** El 100 % del texto de las 403 páginas del curso se conserva carácter por carácter tanto en el PDF original como en la nueva edición generada en archivos separados (`CLS_Curso_Reversing_v5.1_Ampliada.html` y `CLS_Curso_Reversing_v5.1_Ampliada.pdf`).
3. **Qué partes del PDF original presentaron limitaciones de formato físico y cómo se resolvieron sin alterar el texto:**
   - **Página 266 (Lección 6.2):** La quinta columna de la tabla *«Qué recibe el driver según el método del IOCTL»* quedó truncada físicamente por el borde derecho de la página A4 al imprimirse con `overflow-x: auto`. En el Módulo 14 de este documento se reproduce primero el fragmento original y a continuación se presenta la tabla íntegra en una **Nota editorial y Ampliación editorial basada en fuentes externas**. Además, en el nuevo PDF separado (`CLS_Curso_Reversing_v5.1_Ampliada.pdf`), se ajustó únicamente la hoja de estilo de impresión (`.print-sec .tabla { overflow-x: visible; }`) para que la tabla original completa sea 100 % legible en A4 sin cambiar una sola letra de su contenido.
   - **Páginas 214 y 215 (Lección 4.5):** Los dos bloques delimitados con `~~~text` colapsaron en una sola línea en el PDF original porque el parser `build.py` solo procesaba `` ``` ``. En el Módulo 11 se conserva el texto original y se añade en Nota Editorial el bloque tabulado con sus saltos de línea.
   - **Página 302 (Lección 2D.2):** La respuesta a *«¿Qué describe una VAD?»* quedó desplazada con `!!` debajo de la pregunta de WOW64. En el Módulo 15 se preserva el original y se añade la Nota Editorial con ambas preguntas y respuestas correctamente apareadas.

---

## 3.2 Módulos de Ampliación y Notas Editoriales por Capítulo

---

### MÓDULO DE INSERCIÓN 1 — Apertura / Mapa del Curso y Etapa 4 (Páginas 4, 10, 203 y 402)

#### Texto original preservado (CLS, Págs. 4, 10 y 203)
> **Página 4 (`00_EMPEZAR_AQUI.html`):** `| 4 | Práctica guiada | 14–18 h | Análisis completo + informe reproducible |`  
> **Página 10 (`guia/index.html`):** `| 4 | Práctica guiada | 14 a 18 horas | 4 |`  
> **Página 203 (`guia/etapa-4.html`):** `Prerrequisitos: Etapas 0 a 3. Duración estimada: 19 a 25 horas. Es una estimación de esta guía, derivada de la suma de las lecciones; no es una duración declarada por CLS.`

#### Nota editorial separada (Sincronización de carga horaria de Etapa 4 y secuencia de rutas optativas 2C)
> **[Nota editorial — Consistencia interna de tablas y secuencia sugerida]**
> 1. **Carga horaria y conteo de lecciones de la Etapa 4:** Existe una discrepancia aritmética interna entre las tablas resumen de las páginas 4, 10 y 402 (que conservaron el valor previo de `14–18 h` y `4` lecciones) y la portada de la Etapa 4 en la página 203 (`19 a 25 horas` y `5` lecciones). Al sumar las duraciones sugeridas en el encabezado de cada una de las cinco lecciones que integran la Etapa 4 —`4.1` (6 h), `4.5` (6 h), `4.2` (3 h), `4.3` (3 h) y `4.4` (3 h)—, el total directo es de **21 horas** distribuidas en **5 lecciones**, lo que confirma que el rango actualizado es **19 a 25 horas** *(Hecho confirmado sobre el propio corpus, [Ref-Interna])*.
> 2. **Orden de estudio recomendado para las rutas optativas `2.22`, `2.23` y `2.24`:** Aunque las lecciones `2.22` (Malware dinámico), `2.23` (Shellcode, red y C2) y `2.24` (Fuzzing y simbólico) están ubicadas al final del bloque 2C, sus propios encabezados declaran como prerrequisitos las lecciones `4.1`, `4.2`, `4.4` y `5.1`. **Recomendación editorial:** cursar primero el recorrido obligatorio `0–4` y la lección `5.1` antes de abordar las prácticas optativas `2.22–2.24`, sin necesidad de alterar la numeración del curso.

---

### MÓDULO DE INSERCIÓN 2 — Lección 2.6: Breakpoints Condicionales sobre Mensajes en x86 vs. x64 (Página 90)

#### Texto original preservado (CLS, Pág. 90)
> 2. **Breakpoint condicional sobre el mensaje.** Poné un breakpoint donde la función carga el mensaje en un registro y condicionalo a ese mensaje. Podés además loguear los dos argumentos leyéndolos del stack:
> ```text
> log:     "msg={2}  id={3}"      ; con getdword(sp+8) y getdword(sp+C)
> breakif: getdword(sp+8) == 0x111 && getdword(sp+0xC) == 0x13A
> ```

#### Nota editorial y Ampliación editorial basada en fuentes externas (Lección 2.6, Pág. 90)
> **[Nota editorial — Alcance arquitectónico de la expresión `getdword(sp+8)`]**
> La expresión `getdword(sp+8) == 0x111 && getdword(sp+0xC) == 0x13A` del capítulo 28 está pensada para un binario de **32 bits (x86)** en el prólogo de `WindowProc(HWND hWnd, UINT uMsg, WPARAM wParam, LPARAM lParam)`, donde la convención `__stdcall` ubica `[esp+0]` = dirección de retorno, `[esp+4]` = `hWnd`, `[esp+8]` = `uMsg` y `[esp+0xC]` = `wParam`. Además, en el mensaje `WM_COMMAND` (`0x0111`), el identificador del control (*Control ID*) viaja en los 16 bits bajos (`LOWORD(wParam)`), mientras que los 16 bits altos (`HIWORD(wParam)`) contienen el código de notificación (p. ej., `BN_CLICKED = 0`, `EN_CHANGE = 0x0300`). Si el código de notificación no es cero, comparar los 32 bits completos de `wParam` contra `0x13A` no detendrá el debugger.
>
> **[Ampliación editorial basada en fuentes externas — Condiciones para `WndProc` en x64 y función `arg.get()` en x64dbg]**
> De acuerdo con la especificación oficial de `WindowProc` y `WM_COMMAND` en Microsoft Learn *(Hecho confirmado, [Ref-1, Ref-2])* y la documentación de funciones de expresión de x64dbg *(Hecho confirmado, [Ref-3])*:
>
> 1. **En binarios de 64 bits (x64):** Según la ABI x64 de Windows (vista en la lección 2.5), los cuatro argumentos de `WindowProc` llegan en registros: `RCX` = `hWnd`, `RDX` = `uMsg`, `R8` = `wParam` y `R9` = `lParam` [Ref-1]. Por lo tanto, al poner el breakpoint en la primera instrucción del `WndProc` o `DialogProc` en `x64dbg` (64 bits), la condición y el log correctos son:
> ```text
> Condición (breakif): rdx == 0x111 && (r8 & 0xFFFF) == 0x13A
> Texto de Log (log):  "WM_COMMAND: notif={r8>>16} id={r8&0xFFFF} hwnd={rcx}"
> ```
> 2. **Expresión independiente de arquitectura en x64dbg (`arg.get`):** x64dbg incluye la función de expresión `arg.get(índice)` (basada en 0), que en la entrada de una función lee automáticamente `[esp + 4*(índice+1)]` en x86 y `rcx`/`rdx`/`r8`/`r9` en x64 *(Hecho confirmado, [Ref-3])*:
> ```text
> Condición universal (x86 y x64) en la entrada de WndProc:
> breakif: arg.get(1) == 0x111 && (arg.get(2) & 0xFFFF) == 0x13A
> log:     "uMsg={arg.get(1)} control_id={arg.get(2)&0xFFFF}"
> ```
> *(Recomendación editorial: aplicar siempre la máscara `& 0xFFFF` sobre `wParam` al filtrar `WM_COMMAND` para aislar el `Control ID` sin depender de que el código de notificación sea `0` [Ref-2]).*

---

### MÓDULO DE INSERCIÓN 3 — Lección 2.10: Cómo Distinguir en Triage Estático un Aplanamiento de Flujo (CFF) frente a una Máquina Virtual de Bytecode (VM) (Página 119)

#### Texto original preservado (CLS, Pág. 119)
> **Lo que queda fuera**  
> La ofuscación por **máquina virtual** (el código se traduce a un bytecode propio que interpreta un "procesador" embebido), las expresiones mixtas booleano-aritméticas y la desofuscación automática por ejecución simbólica. Se mencionan para reconocerlas por nombre; analizarlas exige herramientas y tiempo que exceden esta etapa, y en protectores comerciales entran en el límite del curso (no desempacar protectores comerciales).

#### Ampliación editorial basada en fuentes externas (Lección 2.10, Pág. 119)
> **[Ampliación editorial basada en fuentes externas — Criterio de triage para diferenciar CFF de una Máquina Virtual de bytecode (VM)]**
> Aunque la reconstrucción de una máquina virtual de protección excede el alcance del curso, durante el inventario estático (Etapa 4) tanto el **aplanamiento del flujo de control (CFF)** como un **intérprete de bytecode (VM)** se presentan en el grafo de IDA o Ghidra como un gran bucle con un despachador (`switch`) central y decenas de bloques que vuelven a él *(Hecho confirmado, [Ref-4, Ref-5])*. Distinguirlos en los primeros cinco minutos evita invertir horas en la estrategia equivocada:
>
> | Criterio Observable en IDA / Ghidra | Aplanamiento del Flujo de Control (CFF) | Ofuscación por Máquina Virtual (VM de bytecode) |
> |---|---|---|
> | **Qué contienen los casos del `switch`** | **Lógica real de la función original:** llamadas a APIs de Windows, acceso a variables locales y globales del negocio y comparaciones propias del algoritmo [Ref-4]. | **Micro-operaciones genéricas (*handlers* de CPU virtual):** bloques pequeños que suman dos valores de una pila virtual (`vADD`), copian entre un banco de registros virtuales y memoria (`vMOV`), o aplican `NOR`/`NAND` sin llamadas directas a la lógica del negocio [Ref-5]. |
> | **Cómo se elige el siguiente bloque** | Cada bloque asigna una **constante fija** a una variable de estado local (p. ej. `mov dword ptr [rbp-8], 0x3A1F2041`) y salta de vuelta al encabezado del `switch` [Ref-4]. | Un registro físico actúa como **Puntero de Instrucción Virtual (`VIP` / `VPC`)** que avanza leyendo bytes de un arreglo de datos (`lodsb` o `movzx eax, byte ptr [rsi] ; inc rsi`) y salta mediante una tabla de punteros a handlers (`jmp qword ptr [rbx + rax*8]`) —el ciclo *fetch-decode-dispatch* [Ref-5]. |
> | **Presencia de una pila virtual (`VSP`)** | No hay pila virtual: la función usa únicamente el stack nativo (`RSP`/`RBP`) del procesador [Ref-4]. | Otro registro (p. ej. `RDI` o `R12`) funciona como puntero de pila virtual (`VSP`), subiendo y bajando sobre un buffer propio en cada handler [Ref-5]. |
> | **Reutilización entre funciones** | Cada función aplanada posee su propio `switch` y sus propios bloques básicos [Ref-4]. | Múltiples funciones protegidas comienzan con un `push <offset_bytecode> ; jmp VM_Entry`, compartiendo el mismo bucle intérprete [Ref-5]. |
> | **Acción recomendada en el informe (Etapa 4)** | Documentar «función ofuscada por *Control-Flow Flattening* con variable de estado en `[rbp-X]`» y armar la tabla `estado -> bloque -> estado siguiente` si la función es acotada *(Recomendación editorial)*. | Documentar «función virtualizada; entrada al despachador en `0x...`, registro `VIP` en `...` y tabla de handlers en `0x...`», observar entradas/salidas en las fronteras de llamada a APIs del sistema y **no** intentar reconstruir el bytecode a mano si excede el alcance autorizado *(Recomendación editorial, [Ref-5])*. |

---

### MÓDULO DE INSERCIÓN 4 — Lección 2.12: Reconstrucción Estática de `AFX_MSGMAP` y `AFX_MSGMAP_ENTRY` en MFC (Página 126)

#### Texto original preservado (CLS, Pág. 125)
> MFC asocia cada mensaje/control a una función con un **message map**, una tabla que el compilador arma a partir de macros del estilo `BEGIN_MESSAGE_MAP` / `ON_BN_CLICKED` / `END_MESSAGE_MAP`. En el binario queda como un arreglo de entradas **`AFX_MSGMAP_ENTRY`**, y cada entrada tiene más que "ID y puntero": `nMessage` (el mensaje, p. ej. `WM_COMMAND`), `nCode` (código de notificación), `nID` y `nLastID` (rango de IDs de control), `nSig` (la firma de la función) y **`pfn`** (el puntero al handler).

#### Ampliación editorial basada en fuentes externas (Lección 2.12, Pág. 126)
> **[Ampliación editorial basada en fuentes externas — Definición en C y offsets de `AFX_MSGMAP` y `AFX_MSGMAP_ENTRY` para análisis estático]**
> Cuando analizás un binario MFC en estático (sin ejecutarlo) o cuando fue compilado con **enlace estático de MFC** (donde no aparece `mfc140u.dll` en la IAT), podés importar las estructuras oficiales declaradas en el encabezado `<afxwin.h>` de Microsoft Visual C++ directamente en IDA (*Local Types → Insert*) o Ghidra (*Parse C Source*) *(Hecho confirmado, [Ref-6])*:
>
> ```c
> // Definición compatible con <afxwin.h> (MSVC x86 y x64)
> struct AFX_MSGMAP_ENTRY {
>     unsigned int nMessage;   // +0x00 (4B): Mensaje de Windows (p. ej. 0x0111 = WM_COMMAND)
>     unsigned int nCode;      // +0x04 (4B): Código de notificación (p. ej. 0 = BN_CLICKED)
>     unsigned int nID;        // +0x08 (4B): Control ID inicial (p. ej. 0x3E8 = 1000)
>     unsigned int nLastID;    // +0x0C (4B): Control ID final (igual a nID salvo en ON_COMMAND_RANGE)
>     uintptr_t    nSig;       // +0x10 (4B en x86 / 8B en x64): Descriptor de prototipo (AfxSig_*; 0 = fin)
>     void*        pfn;        // +0x14 en x86 (4B) / +0x18 en x64 (8B): Puntero al método handler
> };
>
> struct AFX_MSGMAP {
>     const void* pfnGetBaseMap;                // +0x00: Puntero a GetThisMessageMap de la clase base (o base directa)
>     const struct AFX_MSGMAP_ENTRY* lpEntries; // +0x04 (x86) / +0x08 (x64): Arreglo terminado en {0,0,0,0,0,0}
> };
> ```
>
> **Geometría exacta en memoria *(Hecho confirmado, [Ref-6])*:**
> - **En 32 bits (x86):** Cada `AFX_MSGMAP_ENTRY` ocupa **24 bytes (`0x18`)** (seis campos de 4 bytes). El puntero al handler `pfn` está en `+0x14`.
> - **En 64 bits (x64):** Cada `AFX_MSGMAP_ENTRY` ocupa **32 bytes (`0x20`)** (cuatro `unsigned int` de 4 bytes = 16 bytes, seguidos de `nSig` de 8 bytes en `+0x10` y `pfn` de 8 bytes en `+0x18`).
> - **Centinela de cierre (`END_MESSAGE_MAP`):** El arreglo `lpEntries` termina siempre con una entrada nula `{0, 0, 0, 0, AfxSig_end (0), NULL}` [Ref-6].
> - **Cómo encontrar la tabla estáticamente desde la vtable *(Recomendación editorial)*:** En cualquier clase derivada de `CCmdTarget` / `CWnd` / `CDialog`, uno de los primeros métodos virtuales de su vtable es `GetMessageMap()`, cuya implementación consta de solo dos instrucciones: `lea rax, [rip + MiDialog_messageMap] ; ret` (o `mov eax, offset MiDialog_messageMap ; ret` en x86). Siguiendo el segundo puntero (`lpEntries`) de esa estructura `AFX_MSGMAP` se accede directamente al arreglo de eventos del diálogo.

---

### MÓDULO DE INSERCIÓN 5 — Lección 2.13: Fuentes Verificadas y Layout Interno para Delphi (Páginas 130, 132 y 402)

#### Texto original preservado (CLS, Págs. 130 y 132)
> **Página 130:**  
> - **Formularios como recursos.** Los formularios (`TForm`) se guardan como recursos `RCDATA` que empiezan con la firma `TPF0`; ahí están los nombres de los controles y los **nombres de los manejadores de eventos** (por ejemplo `Button1Click`), que te llevan directo a la lógica.  
> - **Convención `register`.** En Delphi de 32 bits la convención por defecto pasa los tres primeros argumentos en `EAX`, `EDX` y `ECX`, no en el stack: un método recibe `Self` en `EAX`. Si leés el listado esperando `stdcall`, los argumentos "desaparecen".  
> - **Cadenas con cabecera.** Los `string` largos de Delphi guardan contador de referencias y longitud **antes** del primer carácter, así que el puntero apunta al texto pero hay datos en offsets negativos.  
>
> **Página 132:**  
> - Delphi: la convención `register`, la firma `TPF0` de los formularios y la cabecera de los `string` son conocimiento externo sin enlace verificado en esta revisión (la documentación de Embarcadero no respondió durante la verificación).

#### Nota editorial y Ampliación editorial basada en fuentes externas (Lección 2.13, Pág. 132 y Fuentes §10.4, Pág. 402)
> **[Nota editorial — Cierre del pendiente de verificación documental de Delphi]**
> Se dejan verificadas contra la documentación oficial primaria de Embarcadero RAD Studio (DocWiki) las tres afirmaciones de la página 130 que habían quedado pendientes de enlace en la revisión del 28/10/2026.
>
> **[Ampliación editorial basada en fuentes externas — ABI `register`, estructura `StrRec` en offsets negativos y recursos `TPF0` en Delphi]**
> 1. **Convención de llamada `register` en x86 vs. ABI en x64 *(Hecho confirmado, [Ref-7])*:**
>    - En **Delphi de 32 bits (`DCC32`)**, la convención por defecto es `register`: los primeros hasta tres parámetros ordinales, punteros o referencias que quepan en 32 bits se evalúan de izquierda a derecha y se pasan en **`EAX` (1.º)**, **`EDX` (2.º)** y **`ECX` (3.º)**. Si hay un 4.º parámetro o más, se apilan en el stack **de izquierda a derecha** (orden *Pascal*, opuesto al orden derecha-a-izquierda de `cdecl`/`stdcall`), y la función llamada limpia el stack al retornar (`ret N`). En métodos de instancia, `Self` (el equivalente a `this`) viaja siempre en `EAX`, por lo que los dos primeros argumentos visibles del método van en `EDX` y `ECX`. En constructores y destructores, `DL` actúa como bandera implícita de asignación/liberación de memoria [Ref-7].
>    - En **Delphi de 64 bits para Windows (`DCC64`)**, Embarcadero unificó todas las convenciones (`register`, `stdcall`, `cdecl`, `pascal`) en la **ABI x64 estándar de Microsoft** (`RCX`, `RDX`, `R8`, `R9` + 32 bytes de *shadow space*; `Self` llega en `RCX`) [Ref-7].
> 2. **Layout en memoria de `AnsiString` y `UnicodeString` (Delphi 2009 y posteriores) *(Hecho confirmado, [Ref-8])*:**
>    Una variable `string` no nula apunta directamente al primer carácter (`offset 0`), pero el bloque en memoria tiene una cabecera `StrRec` de **12 bytes en desplazamientos negativos**:
>    ```text
>    Offset desde el puntero | Tamaño  | Campo      | Descripción (Embarcadero Internal Data Formats)
>    ------------------------+---------+------------+------------------------------------------------------------
>    [ptr - 0x0C] (-12)      | 2 bytes | codePage   | Página de códigos (p. ej. 1200 = UTF-16LE, 1252 = Windows-1252)
>    [ptr - 0x0A] (-10)      | 2 bytes | elemSize   | Bytes por elemento (1 en AnsiString, 2 en UnicodeString)
>    [ptr - 0x08] (-8)       | 4 bytes | refCnt     | Contador de referencias (-1 = literal constante en solo lectura)
>    [ptr - 0x04] (-4)       | 4 bytes | length     | Longitud de la cadena en caracteres (32 bits con signo)
>    [ptr + 0x00] (0)        | N bytes | caracteres | Caracteres seguidos de terminador nulo (#0)
>    ```
>    *(En versiones anteriores a Delphi 2009 —Delphi 2 a 2007—, la cabecera de `AnsiString` medía solo 8 bytes: `[ptr - 8]` = `refCnt` y `[ptr - 4]` = `length` [Ref-8]. En ambos casos, ver en el desensamblado `mov eax, [eax - 4]` tras comprobar `test eax, eax` es la lectura directa de `Length(s)`).*
> 3. **Formularios DFM binarios y firma `TPF0` *(Hecho confirmado, [Ref-9])*:**
>    Al compilar un formulario `.dfm` en modo binario (a través de `TestStreamFormat` / `WriteResourceHeader` de `System.Classes`), la sección `.rsrc` almacena bajo `RT_RCDATA` un flujo que comienza con los 4 bytes mágicos `54 50 46 30` (ASCII `"TPF0"`), donde quedan asociados cada control visual (p. ej. `Button1: TButton`) y el nombre de su evento publicado (`OnClick = Button1Click`), resoluble contra la tabla de métodos publicados de la RTTI de la clase [Ref-9].

---

### MÓDULO DE INSERCIÓN 6 — Lección 2.14: Tabla Completa de Offsets de `PEB_LDR_DATA` y `LDR_DATA_TABLE_ENTRY` en x86 y x64 (Página 136)

#### Texto original preservado (CLS, Pág. 136)
> ```asm
> mov   rax, gs:[60h]          ; PEB
> mov   rax, [rax+18h]         ; PEB->Ldr
> mov   rsi, [rax+20h]         ; Ldr->InMemoryOrderModuleList.Flink
> siguiente_modulo:
> mov   rdi, [rsi+20h]         ; DllBase (offset relativo a InMemoryOrderLinks)
> ```

#### Nota editorial y Ampliación editorial basada en fuentes externas (Lección 2.14, Pág. 136)
> **[Nota editorial — Por qué `[rsi+20h]` es `DllBase` cuando se entra por `InMemoryOrderModuleList`]**
> El listado de la página 136 es exacto en x64, pero para que el lector pueda aplicar el principio de `CONTAINING_RECORD` visto en la lección 2.7 (pág. 99) a cualquier binario x86 o x64 —incluso cuando el código recorre `InLoadOrderModuleList` o `InInitializationOrderModuleList`—, es necesario explicitar la posición de los tres enlaces `LIST_ENTRY` dentro de `PEB_LDR_DATA` y `LDR_DATA_TABLE_ENTRY`.
>
> **[Ampliación editorial basada en fuentes externas — Geometría de `PEB`, `PEB_LDR_DATA` y `LDR_DATA_TABLE_ENTRY` en x86 y x64]**
> Según las declaraciones del Windows SDK en `<winternl.h>` y el símbolo público `ntdll!_LDR_DATA_TABLE_ENTRY` *(Hecho confirmado, [Ref-10, Ref-11, Ref-12])*:
>
> Cuando una rutina lee `Ldr->InMemoryOrderModuleList.Flink` (`[rax+0x20]` en x64 o `[eax+0x14]` en x86), el puntero obtenido en `rsi` **no apunta al byte `+0x00` de `LDR_DATA_TABLE_ENTRY`**, sino al miembro `InMemoryOrderLinks` embebido en `+0x10` (x64) o `+0x08` (x86). Por eso todos los desplazamientos posteriores desde `rsi` llevan restado ese offset base:
>
> | Estructura / Campo | Offset en x86 (32 bits) | Offset en x64 (64 bits) | Offset relativo desde `InMemoryOrderLinks` (x86 / x64) |
> |---|---|---|---|
> | **Puntero al `PEB` desde segmento** | `fs:[0x30]` | `gs:[0x60]` | — |
> | **`PEB.Ldr` (`PEB_LDR_DATA*`)** | `PEB + 0x0C` | `PEB + 0x18` | — |
> | `Ldr->InLoadOrderModuleList` | `Ldr + 0x0C` | `Ldr + 0x10` | — |
> | `Ldr->InMemoryOrderModuleList` | `Ldr + 0x14` | `Ldr + 0x20` | — |
> | `Ldr->InInitializationOrderModuleList` | `Ldr + 0x1C` | `Ldr + 0x30` | — |
> | **`LDR_DATA_TABLE_ENTRY`** | | | |
> | `InLoadOrderLinks` (`LIST_ENTRY`) | `+0x00` | `+0x00` | `-0x08` (x86) / `-0x10` (x64) |
> | `InMemoryOrderLinks` (`LIST_ENTRY`) | `+0x08` | `+0x10` | `0x00` / `0x00` *(aquí apunta `rsi` en el ejemplo)* |
> | `InInitializationOrderLinks` (`LIST_ENTRY`) | `+0x10` | `+0x20` | `+0x08` (x86) / `+0x10` (x64) |
> | **`DllBase` (`PVOID`)** | **`+0x18`** | **`+0x30`** | **`+0x10` (x86) / `+0x20` (x64)** |
> | `EntryPoint` (`PVOID`) | `+0x1C` | `+0x38` | `+0x14` (x86) / `+0x28` (x64) |
> | `SizeOfImage` (`ULONG`) | `+0x20` | `+0x40` | `+0x18` (x86) / `+0x30` (x64) |
> | `FullDllName` (`UNICODE_STRING`) | `+0x24` (`Buf` en `+0x28`) | `+0x48` (`Buf` en `+0x50`) | `+0x1C` (x86) / `+0x38` (x64) |
> | `BaseDllName` (`UNICODE_STRING`) | `+0x2C` (`Buf` en `+0x30`) | `+0x58` (`Buf` en `+0x60`) | `+0x24` (x86) / `+0x48` (x64) |
>
> **Regla rápida de reconocimiento *(Recomendación editorial)*:**
> - En **x64**, si después de cargar `Flink` ves `mov rdi, [rsi+30h]`, el código entró por `InLoadOrderModuleList` (`0x30 - 0x00`); si ves `mov rdi, [rsi+20h]` (como en el listado de esta página), entró por `InMemoryOrderModuleList` (`0x30 - 0x10`); y si ves `mov rdi, [rsi+10h]`, entró por `InInitializationOrderModuleList` (`0x30 - 0x20`).
> - En **x86 (32 bits)**, los tres desplazamientos equivalentes hacia `DllBase` son `[esi+18h]`, `[esi+10h]` y `[esi+08h]` respectivamente [Ref-11, Ref-12].

---

### MÓDULO DE INSERCIÓN 7 — Lección 2.15: Offsets de `NtGlobalFlag` (x86/x64) y Clases `0x1E` / `0x1F` de `NtQueryInformationProcess` (Página 142)

#### Texto original preservado (CLS, Págs. 140 y 141)
> **Página 140:** `| Anti-debug | Detectar que hay un debugger y cambiar de comportamiento o cerrarse | IsDebuggerPresent, PEB.BeingDebugged, NtGlobalFlag, flags del heap, NtQueryInformationProcess... |`  
> **Página 141:** **`NtQueryInformationProcess` con `ProcessDebugPort`.** Es una función de `ntdll` (la capa nativa de 2.14); Microsoft la documenta como interna y sujeta a cambios, y no tiene biblioteca de importación, así que el programa suele obtenerla con `GetProcAddress`. Con la clase `ProcessDebugPort` (valor 7) devuelve un número de puerto: **distinto de cero** indica que el proceso corre bajo un debugger de modo usuario.

#### Ampliación editorial basada en fuentes externas (Lección 2.15, Pág. 142)
> **[Ampliación editorial basada en fuentes externas — `PEB.NtGlobalFlag` en x86 vs. x64 y clases `0x1E` / `0x1F` de `NtQueryInformationProcess`]**
> Para completar las firmas de detección en el listado estático mencionadas en la tabla de la página 140 y en la lección 2.6 *(Hecho confirmado, [Ref-10, Ref-13, Ref-14])*:
>
> 1. **`PEB.NtGlobalFlag` (valor `0x70`) en 32 y 64 bits:**
>    Cuando un proceso se inicia bajo un depurador, el sistema activa por defecto tres indicadores de validación del heap en `NtGlobalFlag`: `FLG_HEAP_ENABLE_TAIL_CHECK (0x10) | FLG_HEAP_ENABLE_FREE_CHECK (0x20) | FLG_HEAP_VALIDATE_PARAMETERS (0x40) = 0x70` [Ref-14]. El desplazamiento del campo dentro del `PEB` cambia según la arquitectura:
>    - **En x86 (32 bits):** `fs:[30h]` $\to$ **`[peb + 0x68]`**.
>    - **En x64 (64 bits):** `gs:[60h]` $\to$ **`[peb + 0xBC]`** (en un proceso de 32 bits corriendo bajo WOW64, su PEB de 64 bits también lo expone en `+0xBC`).
>    ```asm
>    ; Firma típica en x64:
>    mov   rax, gs:[60h]
>    mov   eax, dword ptr [rax+0BCh]   ; PEB.NtGlobalFlag en x64 (+0x68 en x86)
>    and   eax, 70h
>    cmp   eax, 70h
>    je    detectado
>    ```
> 2. **Otras dos clases frecuentes de `NtQueryInformationProcess` junto a `ProcessDebugPort (7)` *(Hecho confirmado, [Ref-13, Ref-15])*:**
>    - **`ProcessDebugObjectHandle` (`0x1E` = 30):** Consulta el handle del objeto kernel `DEBUG_OBJECT` asociado al proceso. Si no hay debugger adjunto, la llamada **no** devuelve `STATUS_SUCCESS`, sino el código `NTSTATUS` **`0xC0000353` (`STATUS_PORT_NOT_SET`)**. Ver en el listado `mov edx, 1Eh` antes de llamar a `NtQueryInformationProcess` y una comparación posterior de `EAX` contra `0xC0000353` identifica este chequeo sin ambigüedad.
>    - **`ProcessDebugFlags` (`0x1F` = 31):** Consulta el campo `NoDebugInherit` del proceso en el kernel. Devuelve un `ULONG` con **lógica invertida**: vale **`0`** si el proceso está siendo depurado y **`1`** si no hay debugger presente.

---

### MÓDULO DE INSERCIÓN 8 — Lección 2.17: El Método del Breakpoint de Hardware en el Stack («ESP Trick») Paso a Paso (Página 152)

#### Texto original preservado (CLS, Pág. 151)
> 2. **Llegá al OEP.** El stub termina restaurando registros y **saltando** al OEP. En UPX el patrón clásico es un `popad` seguido de un salto lejano (`jmp`) a una dirección en la zona que estaba vacía (`UPX0`). Un breakpoint de hardware sobre el stack o seguir hasta ese `jmp` te deja en el OEP.

#### Ampliación editorial basada en fuentes externas (Lección 2.17, Pág. 152)
> **[Ampliación editorial basada en fuentes externas — Fundamento y procedimiento del breakpoint de hardware en el stack («ESP/RSP trick»)]**
> El paso 2 menciona «un breakpoint de hardware sobre el stack». Esta técnica clásica —conocida en la bibliografía como *the ESP trick* *(Hecho confirmado, [Ref-15, Cap. 18; Ref-16])*— combina la estructura LIFO de la pila (Lección 1.2) con los registros de depuración `DR0`–`DR3` (Lección 2.6):
>
> - **Por qué funciona:** Cuando el cargador entrega el control al *stub* de un packer como UPX, su primera acción es guardar en la pila los registros iniciales del hilo (por ejemplo, `pushad` en x86 guarda 8 registros = 32 bytes y resta `0x20` a `ESP`). Mientras el stub descomprime las secciones y resuelve imports, todas sus operaciones de pila ocurren en direcciones **inferiores** a ese `ESP` inicial. Recién cuando el stub termina todo su trabajo y ejecuta `popad` (o la secuencia de `pop` finales en x64) para restaurar el estado previo antes de saltar al OEP, el procesador **lee** por primera vez esos 4 u 8 bytes guardados al comienzo [Ref-15].
> - **Cómo aplicarlo paso a paso en x64dbg sobre un binario propio comprimido con UPX *(Recomendación editorial)*:**
>   1. Abrí el binario empaquetado en x64dbg y asegurate de estar detenido en el *Entry Point* del stub (donde está el `pushad` inicial en x86 o los `push` de preservación en x64).
>   2. Presioná **`F8` (Step Over) una sola vez** para que se ejecute el `pushad` y los registros queden guardados en el stack.
>   3. En el panel de registros (derecha), hacé clic derecho sobre el valor actual de **`ESP`** (o `RSP`) $\to$ ***Follow in Dump***.
>   4. En el panel *Dump* (abajo a la izquierda), seleccioná los primeros 4 bytes (el tope actual de la pila), hacé clic derecho $\to$ ***Breakpoint* $\to$ *Hardware, Access* $\to$ *Dword***.
>   5. Presioná **`F9` (Run)**. El programa descomprimirá todo a máxima velocidad y el procesador disparará la excepción de depuración (`DR0`) exactamente una instrucción después del `popad`: estarás parado sobre el `jmp OEP`, a un solo `F8` del punto de entrada original [Ref-15, Ref-16].

---

### MÓDULO DE INSERCIÓN 9 — Lección 2.18: Tablas Comprimidas de `__CxxFrameHandler4` en MSVC Moderno (Página 158)

#### Texto original preservado (CLS, Pág. 158)
> - **x64:** no hay registro en tiempo de ejecución. La entrada de la función en `.pdata` apunta a su información de desenrollado en `.xdata`, que nombra el handler de C++ (`__CxxFrameHandler3`, o `__CxxFrameHandler4` en versiones recientes de MSVC) y sus tablas. El cuerpo del `catch` suele compilarse como un **funclet** separado.

#### Ampliación editorial basada en fuentes externas (Lección 2.18, Pág. 158)
> **[Ampliación editorial basada en fuentes externas — Diferencia entre `__CxxFrameHandler3` y `__CxxFrameHandler4` (FH4) en MSVC x64]**
> Desde Visual Studio 2019 versión 16.3 en adelante (incluido Visual Studio 2022), el compilador MSVC x64 activa por defecto la opción `/d2FH4`, que reemplaza `__CxxFrameHandler3` por **`__CxxFrameHandler4`** para reducir entre un 30 % y un 60 % el tamaño de los metadatos de excepciones en `.xdata` *(Hecho confirmado, [Ref-17])*:
>
> - **En `__CxxFrameHandler3`:** El campo `ExceptionData` al final de `UNWIND_INFO` contiene la RVA de una estructura `FuncInfo` de tamaño fijo que comienza siempre con la constante mágica de 32 bits **`0x19930520`** (`magicNumber` + versión), seguida de conteos y RVAs de 32 bits hacia `UnwindMap` (destructores automáticos), `TryBlockMap` (bloques `try` y su lista `HandlerMap` de bloques `catch`) e `IpToStateMap` [Ref-17].
> - **En `__CxxFrameHandler4` (`FuncInfo4`):** Ya **no existe la constante `0x19930520`** ni campos de ancho fijo de 32 bits. La estructura comienza con un único byte de cabecera (`FuncInfoHeader`: bits `isCatch`, `isSeparated`, `bbt`, `hasUnwindMap`, `hasTryBlockMap`, `isNoExcept`) y codifica los desplazamientos y conteos subsiguientes mediante **enteros sin signo de longitud variable** (de 1 a 4 bytes, según los bits bajos del primer byte) [Ref-17].
> - **Qué tener en cuenta en la práctica de esta lección *(Recomendación editorial)*:** Si compilás tu programa propio en Visual Studio 2022 en x64, vas a ver `__CxxFrameHandler4` en los imports de `vcruntime140_1.dll`. IDA y Ghidra modernos parsean `FuncInfo4` automáticamente y etiquetan los *funclets* de `catch`; si en algún ejercicio querés observar la tabla clásica `FuncInfo` sin comprimir (`0x19930520`), podés compilar pasando `/d2FH4-` en la línea de comandos de `cl.exe` [Ref-17].

---

### MÓDULO DE INSERCIÓN 10 — Lección 2.19: Cómo Distinguir el *NT Heap* Clásico del *Segment Heap* en WinDbg (Página 166)

#### Texto original preservado (CLS, Pág. 165)
> - **LFH** (*Low Fragmentation Heap*): Windows agrupa las alocaciones chicas en *buckets*. El Curso IDA dedica una parte a distinguir si una alocación cae en el **LFH o en el heap estándar**, porque cambia cómo se ven los bloques (Curso IDA, tute 48). En WinDbg lo mirás con `!heap`.

#### Ampliación editorial basada en fuentes externas (Lección 2.19, Pág. 166)
> **[Ampliación editorial basada en fuentes externas — *NT Heap* (`0xEEFFEEFF`) vs. *Segment Heap* (`0xDDEEDDEE`) en Windows 10/11]**
> En Windows 10 y Windows 11 coexisten dos arquitecturas de heap en modo usuario administradas por `ntdll.dll` *(Hecho confirmado, [Ref-18, Ref-19])*:
>
> 1. **NT Heap (heap tradicional):** Es el administrador por defecto para la mayoría de los ejecutables Win32 clásicos (y el que muestran los tutes 44 y 48 del Curso IDA), compuesto por el *Back-End Allocator* y el *Low Fragmentation Heap (LFH)*. En memoria, la firma interna de su cabecera `_HEAP` es **`0xEEFFEEFF`**.
> 2. **Segment Heap:** Es el administrador moderno usado por procesos de sistema, servicios, aplicaciones empaquetadas (MSIX/UWP) y cualquier ejecutable Win32 que declare `<segmentHeap>true</segmentHeap>` en su manifiesto de aplicación (o se configure por `IFEO`) [Ref-18]. Divide las asignaciones en cuatro niveles (*Low Fragmentation Heap*, *Variable Size (VS) Subsegment*, *Backend Segment* y *Large Blocks*) y su estructura `_SEGMENT_HEAP` lleva la firma **`0xDDEEDDEE`**.
> 3. **Cómo identificarlos en WinDbg *(Hecho confirmado, [Ref-19])*:**
>    - Al ejecutar `!heap` sin argumentos, la columna `Type` (en versiones recientes de WinDbg) indica explícitamente `NT Heap` o `Segment Heap` para cada handle listado.
>    - Cuando activás **Full Page Heap** con `gflags /p /enable prog.exe /full` (como en la práctica de esta lección), el verificador intercepta las reservas antes del backend y encamina las asignaciones hacia `_DPH_HEAP_ROOT`, por lo que **`!heap -p -a <dirección>` funciona de la misma manera** para localizar el stack de reserva y la página de guardia [Ref-19].

---

### MÓDULO DE INSERCIÓN 11 — Lección 3.1: Cómo Distinguir *Single-File Deployment* (`apphost` bundle) y *ReadyToRun* (R2R) frente a *Native AOT* en .NET Moderno (Página 193)

#### Texto original preservado (CLS, Pág. 193)
> **Excepciones al modelo IL/JIT: Native AOT y C++/CLI**  
> El recorrido IL → JIT describe el caso común, no todos los ejecutables relacionados con .NET. **Native AOT** compila IL a código nativo durante la publicación y no usa JIT al arrancar; el resultado es específico de una plataforma y puede ser más difícil de decompilar como IL. En reversing, primero identificá si hay cabecera CLR y metadatos suficientes; no asumas que todo binario hecho con .NET conserva el mismo contenido administrado.

#### Ampliación editorial basada en fuentes externas (Lección 3.1, Pág. 193)
> **[Ampliación editorial basada en fuentes externas — Cuatro formatos de publicación en .NET 6/8/9+ y cómo no confundir *Single-File* con *Native AOT*]**
> Al analizar un ejecutable moderno de .NET en Windows, encontrarse con un `.exe` nativo que no tiene cabecera CLR (`IMAGE_DIRECTORY_ENTRY_COM_DESCRIPTOR` en cero) **no significa automáticamente que sea Native AOT**. Desde .NET Core 3.1 y .NET 5/6/8/9 existen cuatro variantes de empaquetado bien diferenciadas en la documentación oficial de Microsoft *(Hecho confirmado, [Ref-20, Ref-21])*:
>
> | Variante de publicación .NET | ¿Qué es el `.exe` en PE-bear? | ¿Conserva IL y metadatos completos? | Señal diagnóstica y cómo abrirlo |
> |---|---|---|---|
> | **1. Dependiente del framework / por defecto (`dotnet build`)** | Un **`apphost.exe` nativo chico** (~150 KB) acompañado en la misma carpeta por `MiApp.dll` (que sí tiene cabecera CLR). | **Sí**, íntegros dentro de `MiApp.dll`. | Abrir `MiApp.dll` (no el `.exe`) en ILSpy o dnSpyEx [Ref-20]. |
> | **2. Single-File Deployment (`/p:PublishSingleFile=true`)** | Un **`apphost.exe` nativo grande** (sin cabecera CLR propia) que lleva concatenados en su interior un archivo **Bundle** con `MiApp.dll` y las demás DLLs administradas [Ref-20]. | **Sí**, las DLLs con su IL y metadatos viajan enteras dentro del bundle. | Contiene la firma de 32 bytes del `.NET Single-File Bundle` (asociada a la cadena `".net bundle"` / `hostfxr`). **ILSpy 8.x/9.x** abre el `.exe` directamente y despliega el árbol de DLLs embebidas sin necesidad de considerar el binario como Native AOT [Ref-20]. |
> | **3. ReadyToRun (`R2R`, `/p:PublishReadyToRun=true`)** | Un ensamblado PE con **cabecera CLR** cuyo directorio `ManagedNativeHeader` apunta a una cabecera **`READYTORUN_HEADER`** (firma mágica `0x00525452` = `"RTR\0"`) [Ref-21]. | **Sí** (conserva el IL y los metadatos originales junto con código nativo precompilado para acelerar el arranque) [Ref-21]. | Se decompila normalmente como C# en ILSpy porque el IL sigue presente como respaldo para el JIT [Ref-21]. |
> | **4. Native AOT (`/p:PublishAot=true`)** | Un **PE 100 % nativo** compilado con el compilador AOT (`ilc`), sin JIT, sin IL y sin bundle de DLLs [Ref-20]. | **No hay IL** (solo código máquina x64 y estructuras de runtime / RTTI mínima de tipos reflejados). | Se analiza con **IDA o Ghidra** como binario nativo, apoyándose en las cadenas y tablas del runtime embebido. |

---

### MÓDULO DE INSERCIÓN 12 — Lección 4.5: Formato Tabulado del Ejemplo `CLSF` y del Diagrama de Estados TCP (Páginas 214 y 215)

#### Texto original preservado (CLS, Págs. 214 y 215)
> **Página 214:** `~~~text Offset Bytes Lectura provisional 00 43 4C 53 46 firma ASCII «CLSF» 04 01 versión candidata = 1 05 00 flags candidatos = 0 06 0C 00 tamaño de cabecera candidato = 12 (LE) 08 05 00 tamaño de cuerpo candidato = 5 (LE) 0A 2A 00 campo variable = 42 (LE) 0C 48 45 4C 4C 4F cuerpo ASCII «HELLO» ~~~`  
> **Página 215:** `~~~text DESCONECTADO --conectar--> ESPERA_SALUDO ESPERA_SALUDO --saludo válido--> LISTO LISTO --petición--> ESPERA_RESPUESTA ESPERA_RESPUESTA --respuesta/error--> LISTO cualquier estado --cierre--> DESCONECTADO ~~~`

#### Nota editorial separada (Restitución visual de los dos bloques preformateados de la Lección 4.5)
> **[Nota editorial — Presentación en bloque de los esquemas de las páginas 214 y 215]**
> Debido al uso de delimitadores `~~~text` en el archivo fuente, ambos esquemas se imprimieron en una sola línea corrida en el PDF original. Se reproducen a continuación con sus saltos de línea y alineación originales intactos para facilitar su lectura:
>
> **1. Mapa de bytes del formato sintético `CLSF` (Página 214):**
> ```text
> Offset  Bytes                                      Lectura provisional
> 00      43 4C 53 46                                 firma ASCII «CLSF»
> 04      01                                          versión candidata = 1
> 05      00                                          flags candidatos = 0
> 06      0C 00                                       tamaño de cabecera candidato = 12 (LE)
> 08      05 00                                       tamaño de cuerpo candidato = 5 (LE)
> 0A      2A 00                                       campo variable = 42 (LE)
> 0C      48 45 4C 4C 4F                              cuerpo ASCII «HELLO»
> ```
>
> **2. Máquina de estados del protocolo de ejemplo (Página 215):**
> ```text
> DESCONECTADO --conectar--> ESPERA_SALUDO
> ESPERA_SALUDO --saludo válido--> LISTO
> LISTO --petición--> ESPERA_RESPUESTA
> ESPERA_RESPUESTA --respuesta/error--> LISTO
> cualquier estado --cierre--> DESCONECTADO
> ```

---

### MÓDULO DE INSERCIÓN 13 — Lección 4.2: Reconocimiento de ChaCha20 / Salsa20 por sus Constantes y Estructura ARX (Página 218)

#### Texto original preservado (CLS, Pág. 218)
> | Algoritmo | Qué buscar |
> |---|---|
> | **AES (Rijndael)** | La S-box, que empieza `63 7C 77 7B F2 6B 6F C5 30 01 67 2B …`; o las T-tables |
> | **MD5** | Init `67452301 EFCDAB89 98BADCFE 10325476`; tabla de senos `D76AA478 …` |
> | **SHA-1** | Init `67452301 EFCDAB89 98BADCFE 10325476 C3D2E1F0` |
> | **SHA-256** | Init `6A09E667 BB67AE85 3C6EF372 …`; constantes `428A2F98 71374491 …` |
> | **RC4** | Un arreglo de **256 bytes** inicializado `0,1,2,…,255` y un bucle de *swaps* (KSA/PRGA) |
> | **TEA / XTEA** | La constante *delta* `0x9E3779B9` (número áureo) |
> | **CRC32** | El polinomio `0xEDB88320` o una tabla de 256 entradas de 32 bits |
> | **DES** | Tablas de permutación fijas (IP, S-boxes) |

#### Ampliación editorial basada en fuentes externas (Lección 4.2, Pág. 218)
> **[Ampliación editorial basada en fuentes externas — Reconocimiento de ChaCha20 / Salsa20 y Poly1305 en binarios modernos]**
> Además de los ocho algoritmos de la tabla original, en software actual de Windows (bibliotecas TLS, herramientas de red y malware contemporáneo) el cifrado de flujo **ChaCha20** (especificado en IETF RFC 8439) ha desplazado en gran medida a RC4 porque no requiere tablas S-box en memoria y es inmune a ataques de caché *(Hecho confirmado, [Ref-22])*:
>
> | Algoritmo | Constante / Firma Inmediata en el Binario | Estructura en el Desensamblado |
> |---|---|---|
> | **ChaCha20 / Salsa20** (clave de 256 bits) | Cadena ASCII de 16 bytes **`"expand 32-byte k"`** o sus cuatro `DWORD` en little-endian: **`0x61707865`**, **`0x3320646e`**, **`0x79622d32`**, **`0x6b206574`** [Ref-22]. | Estado de **16 palabras de 32 bits (64 bytes)**: palabras `0..3` = constante `"expand 32-byte k"`, palabras `4..11` = clave de 32 bytes, palabra `12` = contador de bloque, palabras `13..15` = *nonce* de 12 bytes (en RFC 8439). Bucle de **20 rondas** (10 iteraciones de doble ronda) que usa únicamente operaciones **ARX** (`ADD`, `XOR` y rotaciones `ROL` de **16, 12, 8 y 7 bits** en el *quarter-round* de ChaCha20; o **7, 9, 13 y 18 bits** en Salsa20) [Ref-22]. |
> | **ChaCha20 / Salsa20** (clave de 128 bits) | Cadena ASCII de 16 bytes **`"expand 16-byte k"`** (`0x61707865`, `0x3120646e`, `0x79622d36`, `0x6b206574`). | Mismo bucle ARX, repitiendo los 16 bytes de clave en las palabras `4..7` y `8..11`. |
>
> **Pista de lectura rápida *(Recomendación editorial)*:** Si el compilador inlinó las constantes como inmediatos en lugar de una cadena en `.rdata`, buscá `0x61707865` junto con un bloque de instrucciones sin tablas que encadena `add`, `xor` y rotaciones de `16`, `12`, `8` y `7` bits: esa tétrada de conteos de rotación identifica el *quarter-round* de ChaCha20 aunque hayan cambiado la constante `"expand 32-byte k"` para ocultar la firma [Ref-22].

---

### MÓDULO DE INSERCIÓN 14 — Lección 5.3: Migración de IDAPython en IDA 8.4 / 9.0+ (`ida_typeinf` en lugar de `ida_struct` e `ida_enum`) (Página 250)

#### Texto original preservado (CLS, Págs. 247 y 250)
> **Página 247:** `La mayoría de los scripts viejos de internet fallan no porque estén mal, sino porque los nombres cambiaron (PatchByte → patch_byte, etc.). El cap. 25 recomienda la página oficial "Porting from IDA 6.x to 7.4", que lista el nombre viejo y el nuevo de cada función.`  
> **Página 250:** `El cap. 22b, para imprimir los mensajes de Windows por nombre en vez de por número, agrega una enumeración en Local Types y la consulta desde el script con get_enum("nombre") (devuelve el id de la enumeración) y la función que, dado ese id y un valor como cpu.edx, devuelve el nombre (WM_COMMAND, etc.).`

#### Ampliación editorial basada en fuentes externas (Lección 5.3, Pág. 250)
> **[Ampliación editorial basada en fuentes externas — Cambios de API en IDA 9.0+: eliminación de `ida_struct` / `ida_enum` y uso de `ida_typeinf`]**
> Así como en IDA 7.4 se renombraron las funciones de `camelCase` a `snake_case`, en **IDA 9.0** Hex-Rays realizó el segundo gran cambio histórico de IDAPython: **eliminó los módulos `ida_struct` e `ida_enum`** (y las funciones asociadas de `idc` como `get_enum`, `get_enum_member_by_name`, `add_struc`, etc.), unificando todas las estructuras y enumeraciones dentro del sistema de tipos **`ida_typeinf` (`tinfo_t`)** *(Hecho confirmado, [Ref-23])*.
>
> Si ejecutás los ejemplos de los capítulos 22b, 25, 27b y 32 en **IDA 9.0+**:
> - **Siguen funcionando sin cambios:** `idautils.Functions()`, `idautils.Segments()`, `idautils.Heads()`, `idc.get_func_name()`, `idc.set_name()`, `idc.patch_bytes()`, `idc.get_original_byte()`, `idaapi.FlowChart()` e `ida_search.find_text()` (en IDA 9 también disponible vía `ida_bytes.find_bytes` para patrones binarios) [Ref-23].
> - **Cambian a `ida_typeinf` (`tinfo_t`):** Todas las consultas y creaciones de **enumeraciones** (cap. 22b) y **estructuras**.
>
> **Equivalencia funcional para el ejemplo de enumeraciones del capítulo 22b en IDA 9.0+ *(Hecho confirmado, [Ref-23])*:**
> ```python
> # En IDA 7.x / 8.x (cap. 22b):
> # eid = idc.get_enum("MACRO_WM")
> # bmask = idc.DEFMASK
> # cid = idc.get_enum_member(eid, valor, 0, bmask)
> # nombre = idc.get_enum_member_name(cid)
>
> # En IDA 9.0+ usando ida_typeinf.tinfo_t:
> import ida_typeinf
>
> def nombre_miembro_enum(nombre_enum: str, valor: int) -> str | None:
>     tif = ida_typeinf.tinfo_t()
>     if not tif.get_named_type(None, nombre_enum) or not tif.is_enum():
>         return None
>     ed = ida_typeinf.enum_type_data_t()
>     if not tif.get_enum_details(ed):
>         return None
>     for m in ed:
>         if m.value == valor:
>             return m.name
>     return None
>
> # Ejemplo de uso en breakpoint o consola:
> print(nombre_miembro_enum("MACRO_WM", 0x0111))  # -> "WM_COMMAND"
> ```

---

### MÓDULO DE INSERCIÓN 15 — Lección 6.2: Reconstrucción Íntegra de la Tabla de Métodos IOCTL Truncada en la Página 266

#### Texto original preservado (CLS, Pág. 266)
*(En el PDF original de 403 páginas, la quinta columna de esta tabla quedó cortada físicamente en el borde derecho de la página 266; el texto completo existente en la fuente `_trabajo/src/guia/6-02-kmdf-ioctl.md` se reproduce a continuación carácter por carácter):*

| Método | Primer buffer (entrada) | Segundo buffer (salida) | Qué hizo el I/O manager antes | Cómo lo obtiene un driver KMDF |
|---|---|---|---|---|
| `METHOD_BUFFERED` | `Irp->AssociatedIrp.SystemBuffer` | El **mismo** `SystemBuffer` | Reservó un buffer de sistema del tamaño mayor y copió la entrada; al completar copia `Information` bytes a la app. | `WdfRequestRetrieveInputBuffer` y `WdfRequestRetrieveOutputBuffer` (mismo buffer de sistema). |
| `METHOD_IN_DIRECT` / `METHOD_OUT_DIRECT` | `SystemBuffer` (copia, `InputBufferLength`) | Un **MDL** en `Irp->MdlAddress` que describe las páginas del buffer de la app (`OutputBufferLength`) | Verificó el acceso al segundo buffer y bloqueó sus páginas. `IN_DIRECT` asegura acceso de lectura (datos hacia el driver); `OUT_DIRECT`, de escritura (datos hacia la app). | Primer buffer como en buffered; el segundo, con `WdfRequestRetrieveOutputBuffer` (dirección de sistema) o `WdfRequestRetrieveOutputWdmMdl` (el MDL). |
| `METHOD_NEITHER` | `Parameters.DeviceIoControl.Type3InputBuffer`: dirección **de usuario** | `Irp->UserBuffer`: dirección **de usuario** | **Nada**: no copia, no valida, no bloquea. | Solo en `EvtIoInCallerContext` (contexto del hilo llamador): `WdfRequestRetrieveUnsafeUserInputBuffer`/`…OutputBuffer` y luego `WdfRequestProbeAndLockUserBufferForRead`/`…ForWrite`, antes de devolver la solicitud a una cola. |

#### Nota editorial y Ampliación editorial basada en fuentes externas (Lección 6.2, Pág. 266)
> **[Nota editorial — Restitución de la quinta columna truncada en la página 266 del PDF original]**
> En `CLS_Curso_Reversing.pdf` (pág. 266), la quinta columna (*«Cómo lo obtiene un driver KMDF»*) fue recortada por el margen derecho al renderizarse con `overflow-x: auto`, dejando visibles solo las iniciales (`C`, `W`/`b`, `P`/`W`/`d`/`W`, `So`/`h`/`W`/`Ou`/`W`/`Fo`/`co`) y dos íconos de barra de desplazamiento. Arriba queda restituida literalmente desde la fuente original de CLS y en la nueva copia `CLS_Curso_Reversing_v5.1_Ampliada.pdf` se corrigió el estilo de impresión para que la tabla completa entre en el ancho de página A4.
>
> **[Ampliación editorial basada en fuentes externas — Prototipos y verificación en KMDF al revisar las funciones de la 5.ª columna]**
> Al auditar un driver KMDF en IDA o Ghidra (Lecciones 6.2 y 6.4), las llamadas de la quinta columna se traducen a entradas de la tabla de punteros `WdfFunctions` (resueltas por el plugin `wdfkd` o el cargador de tipos WDF) *(Hecho confirmado, [Ref-24, Ref-25])*:
>
> 1. **`WdfRequestRetrieveInputBuffer(Request, MinimumRequiredLength, &Buffer, &Length)` y `WdfRequestRetrieveOutputBuffer(Request, MinimumRequiredSize, &Buffer, &Length)`:**
>    - Si el buffer provisto por el usuario es menor que `MinimumRequiredLength` / `MinimumRequiredSize`, KMDF devuelve inmediatamente **`STATUS_BUFFER_TOO_SMALL` (`0xC0000023`)** y pone `Buffer = NULL` [Ref-24].
>    - **Punto crítico de auditoría defensiva (Lección 6.4):** Si el desarrollador pasa `MinimumRequiredSize = 0` (o `1`) y luego escribe `sizeof(MI_ESTRUCTURA)` sin comprobar `Length`, produce un desborde de pool en `SystemBuffer`. Al analizar el desensamblado, verificá siempre el **segundo argumento (`RDX` en x64)** de `WdfRequestRetrieveInputBuffer` / `WdfRequestRetrieveOutputBuffer` [Ref-24].
> 2. **Por qué `METHOD_NEITHER` exige `EvtIoInCallerContext` en KMDF:**
>    - Como las colas WDF (`WDFQUEUE`) pueden despachar solicitudes de manera diferida en un hilo arbitrario y a `DISPATCH_LEVEL`, cuando corre `EvtIoDeviceControl` ya no está garantizado que el espacio de direcciones virtuales del proceso llamador siga activo. Por eso Microsoft exige que las direcciones crudas de usuario (`Type3InputBuffer` y `UserBuffer`) se intercepten antes de encolar, dentro del callback `EvtIoInCallerContext`, llamando allí a `WdfRequestRetrieveUnsafeUserInputBuffer` seguido de `WdfRequestProbeAndLockUserBufferForRead` (que valida el rango de modo usuario, bloquea las páginas a `PASSIVE_LEVEL` y crea un objeto `WDFMEMORY` seguro para el resto del driver) *(Hecho confirmado, [Ref-25])*.

---

### MÓDULO DE INSERCIÓN 16 — Lección 2D.2: Corrección del Orden de las Preguntas de Repaso sobre VAD y WOW64 (Página 302)

#### Texto original preservado (CLS, Pág. 302)
> `?? ¿Qué describe una VAD?`  
> `?? ¿Qué precaución tomás al analizar un proceso WOW64?`  
> `!! Anoto por separado la arquitectura del proceso y la del sistema, confirmo el contexto de registros y módulos, y tengo en cuenta la redirección de archivos/Registro. Un proceso de 32 bits no puede cargar una DLL de 64 bits para ejecutarla.`  
> `!! Un rango de direcciones virtuales del proceso: su tipo (Image/Mapped/Private), permisos y a qué archivo/sección corresponde. El kernel las mantiene en un árbol por proceso; !vadump sirve para listar regiones en user mode y !vad para inspección detallada en el contexto de depuración de kernel.`

#### Nota editorial separada (Restitución del apareamiento Pregunta–Respuesta en la Página 302)
> **[Nota editorial — Correspondencia de las dos preguntas de repaso de la página 302]**
> En la página 302 del PDF original, la pregunta *«¿Qué describe una VAD?»* quedó sin cuerpo desplegable porque la línea siguiente fue otra pregunta (`??`), y su respuesta apareció al final de la respuesta de WOW64 precedida por los signos literales `!!`. El par ordenado con el texto original exacto es:
>
> - **Pregunta 2:** *¿Qué describe una VAD?*  
>   **Respuesta:** Un **rango** de direcciones virtuales del proceso: su tipo (`Image`/`Mapped`/`Private`), permisos y a qué archivo/sección corresponde. El kernel las mantiene en un árbol por proceso; `!vadump` sirve para listar regiones en user mode y `!vad` para inspección detallada en el contexto de depuración de kernel.
> - **Pregunta 3:** *¿Qué precaución tomás al analizar un proceso WOW64?*  
>   **Respuesta:** Anoto por separado la arquitectura del proceso y la del sistema, confirmo el contexto de registros y módulos, y tengo en cuenta la redirección de archivos/Registro. Un proceso de 32 bits no puede cargar una DLL de 64 bits para ejecutarla.

---

### MÓDULO DE INSERCIÓN 17 — Glosario: Términos Nuevos de las Ampliaciones Editoriales (Página 385)

> **[Ampliación editorial basada en fuentes externas — Adiciones al Glosario para consulta rápida]**
> Se agregan como suplemento al Glosario original (págs. 375–385) los seis términos introducidos en las ampliaciones de esta revisión:
>
> | Término | Explicación (Ampliación editorial basada en fuentes externas) |
> |---|---|
> | **`arg.get(n)` (x64dbg)** | Función de expresión de x64dbg que devuelve el argumento `n` (basado en 0) en la entrada de una función según la convención de la arquitectura (`[esp+4*(n+1)]` en x86; `RCX`, `RDX`, `R8`, `R9` en x64) [Ref-3]. Ver Módulo 2 (Lección 2.6). |
> | **ChaCha20** | Cifrado de flujo moderno (RFC 8439) basado en operaciones ARX (`ADD`, `ROTATE`, `XOR`) sobre un estado de 16 palabras de 32 bits; se identifica por la constante ASCII `"expand 32-byte k"` (`0x61707865...`) [Ref-22]. Ver Módulo 13 (Lección 4.2). |
> | **`__CxxFrameHandler4` (FH4)** | Manejador de excepciones C++ por defecto en MSVC x64 desde VS 2019 16.3+; comprime las tablas de `.xdata` en `FuncInfo4` con enteros de longitud variable y sin el número mágico `0x19930520` [Ref-17]. Ver Módulo 9 (Lección 2.18). |
> | **`ida_typeinf` (`tinfo_t`)** | Módulo del sistema de tipos de IDAPython que en IDA 9.0+ reemplazó por completo a los antiguos módulos `ida_struct` e `ida_enum` para manipular estructuras y enumeraciones [Ref-23]. Ver Módulo 14 (Lección 5.3). |
> | **ReadyToRun (R2R) / Single-File (.NET)** | Formatos de publicación de .NET moderno: *Single-File* empaqueta las DLLs de IL dentro de un `apphost.exe` nativo, mientras que *R2R* incluye código nativo precompilado (`READYTORUN_HEADER`, `"RTR\0"`) junto con el IL original [Ref-20, Ref-21]. Ver Módulo 11 (Lección 3.1). |
> | **Segment Heap** | Administrador de heap moderno de Windows 10/11 (firma `0xDDEEDDEE`) usado por servicios del sistema y aplicaciones con manifiesto `SegmentHeap`, en contraste con el *NT Heap* clásico (`0xEEFFEEFF`) [Ref-18, Ref-19]. Ver Módulo 10 (Lección 2.19). |
