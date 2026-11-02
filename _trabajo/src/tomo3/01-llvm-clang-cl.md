# Módulo 1 · Compiladores No-MSVC en Windows: LLVM, Clang CFI y Rust Endurecido
*(Presupuesto editorial: 50 páginas — Prerrequisito: Tomo I, Lección 2.18, págs. 180–188 y Lección 2.32, págs. 243–247)*

---

## 1.1 Arquitectura del Backend LLVM en Windows (`clang-cl.exe`)

En los Tomos I y II de esta obra, el modelo de referencia para desarmar binarios nativos de Windows fue el compilador de Microsoft (`cl.exe`). Sin embargo, en el ecosistema moderno de Windows 11, una proporción masiva de software de alto rendimiento —incluyendo los navegadores web basados en Chromium (Google Chrome, Microsoft Edge), Firefox, motores de renderizado de videojuegos y herramientas de telemetría de seguridad— se compila utilizando el frontend **`clang-cl.exe`**.

### El Modelo Híbrido de `clang-cl`
`clang-cl` no es simplemente una versión de Clang portada a Windows. Es un controlador de compilador (*driver*) diseñado para aceptar las mismas banderas de línea de comandos que `cl.exe` (`/O2`, `/MD`, `/Zi`, `/guard:cf`), pero reemplazando el frontend y el backend clásicos de MSVC por la infraestructura de **LLVM**:

```
                              DIAGRAMA DE PIPELINE: CLANG-CL VS. MSVC
                              
   [ Código Fuente C/C++ ]
              │
              ├─── (cl.exe de MSVC) ──────> [ C1 / C2 Compiler Frontend ] ──> [ UTC / C2 CodeGen ] ──> [ link.exe ] ──> [ PE/COFF ]
              │                                                                 (MSVC Heuristics)
              │
              └─── (clang-cl de LLVM) ────> [ Clang AST / Clang Frontend ] ──> [ LLVM IR Optimization ]
                                                                                         │
                                                                           [ LLVM Target CodeGen (x86_64) ] ──> [ lld-link ] ──> [ PE/COFF ]
                                                                                 (LLVM Heuristics)
```

Para el analista de ingeniería inversa, aunque el binario resultante sea un archivo PE/COFF de 64 bits con dependencias en el CRT de Microsoft (`msvcrt.dll` o `vcruntime140.dll`), **el código de máquina generado responde a una filosofía de optimización enteramente distinta**:

1. **Orden de Asignación de Registros (*Register Allocation*):**
   * *MSVC:* Tiende a preservar religiosamente los registros no volátiles (`RBX`, `RBP`, `RSI`, `RDI`, `R12-R15`) empujándolos al stack en el prólogo sólo cuando agota los registros volátiles (`RCX`, `RDX`, `R8`, `R9`, `RAX`, `R10`, `R11`). En funciones cortas, suele reutilizar `RCX` y `RDX` agresivamente para variables locales.
   * *LLVM:* Emplea un algoritmo de asignación por coloreado de grafos basado en el algoritmo Chaitin-Briggs con ponderación de presión de registros (*Greedy Register Allocator*). Es muy común que Clang elija preservar un registro no volátil como `R14` o `RBX` incluso en funciones medianas si el análisis de liveness determina que ahorra un solo acceso a la pila durante un bucle crítico.
2. **Generación de Funciones Hoja (*Leaf Functions*):**
   * *MSVC:* Con frecuencia crea un marco de pila estándar (`sub rsp, 28h`) por motivos de consistencia de la *shadow store* de 32 bytes requerida por la convención x64 de Windows, aun cuando no llame a otras funciones.
   * *LLVM:* Optimiza agresivamente las funciones hoja. Si una función no invoca a ninguna otra, Clang elimina por completo la asignación de marco de pila, operando directamente con los parámetros en los registros de entrada y utilizando el espacio negativo de la pila o manteniendo `RSP` intacto.
3. **Fusión de Código Idéntico (*Identical Code Folding - ICF*):**
   * En conjunto con el enlazador `lld-link`, LLVM implementa un plegado de funciones idénticas mucho más agresivo que `link.exe /OPT:ICF`. Múltiples métodos de clases distintas o instanciaciones de plantillas (*templates*) que tengan la misma secuencia de instrucciones P-Code terminan colapsando en una única dirección de memoria, lo que genera referencias cruzadas (*xrefs*) aparentemente contradictorias en el desensamblador.

---

## 1.2 Heurísticas de Switch Lowering: Por Qué un `switch` de Clang No se Parece al de MSVC

Uno de los mayores puntos de fricción al descompilar binarios de `clang-cl` en IDA Pro o Ghidra reside en la traducción de sentencias condicionales múltiples (`switch/case`).

### El Enfoque Clásico de MSVC
Como se estudió en la Lección 2.18 (Tomo I, págs. 180–188), MSVC aborda un `switch` mediante dos estrategias predecibles:
* Si los casos son escasos o muy dispersos: una cascada de comparaciones lineales `cmp reg, val` seguida de saltos `je / jne`, o un árbol binario balanceado de comparaciones `cmp / jg / jl`.
* Si los casos son densos (ej. valores consecutivos de 0 a 15): una **tabla de saltos indexada** continua:
  ```assembly
  ; Patrón clásico de MSVC (Tomo I, pág. 182)
  cmp     eax, 0Fh
  ja      loc_default
  lea     rcx, cs:JumpTable
  movsxd  rax, dword ptr [rcx + rax*4]
  add     rax, rcx
  jmp     rax
  ```

### El Enfoque de LLVM: Bit Testing y Jump Table Clustering
LLVM no trata las tablas de saltos como una opción binaria (o árbol o tabla continua). En su lugar, el módulo `SwitchLowering` de LLVM aplica una combinación de **análisis de densidad de bits** y **agrupamiento por clústeres**:

#### A. Patrón de Bit Testing con `bt` / `bts`
Cuando los casos de un `switch` tienen valores dispersos pero están comprendidos dentro de un rango de 64 valores (o pueden mapearse a una máscara de 64 bits), Clang **no genera ninguna tabla de saltos ni saltos indirectos**. En su lugar, construye una máscara de bits constante en tiempo de compilación y ejecuta una única instrucción `bt` (Bit Test):

```assembly
; ==============================================================================
; Desensamblado de switch en binario clang-cl (LLVM Target)
; Código C: switch(cmd) { case 1: case 4: case 7: case 12: case 33: case 52: ... }
; ==============================================================================
mov     ecx, edx                ; edx = comando recibido (cmd)
sub     ecx, 1                  ; Normalizar el rango restando el caso mínimo (base 0)
cmp     ecx, 33h                ; ¿cmd - 1 > 51? (Rango total = 52 casos posibles)
ja      loc_default             ; Fuera del rango de 64 bits -> default directo

mov     rax, 00100000000010010000000000001001h ; Máscara constante de 64 bits (casos válidos)
bt      rax, rcx                ; Verificar si el bit correspondiente en RAX está encendido
jnc     loc_default             ; Si Carry Flag (CF) = 0, el caso no existe en el switch

; Si CF = 1, el valor es válido. Ahora ramifica mediante una mini-tabla o cálculo directo
```

**Impacto en Reversing:**  
Para el descompilador de Ghidra o IDA Pro, la instrucción `bt rax, rcx` con una constante hexadecimal de 64 bits suele desorientar el análisis del flujo de control. El descompilador puede emitir pseudocódigo críptico como:
```c
if (((1ULL << (cmd - 1)) & 0x10000000001001ULL) == 0) {
    goto loc_default;
}
```
El analista debe reconocer inmediatamente que esta construcción no es una manipulación criptográfica ni un hash de bits, sino un **filtro de selección de casos de switch generado por LLVM**.

#### B. Uso de Conteo de Ceros (`tzcnt` / `bsf`)
Cuando los casos tienen comportamientos uniformes que devuelven constantes o asignan identificadores internos, Clang suele combinar `bt` con `tzcnt` (*Count Trailing Zeros*):

```assembly
; Código emitido por Clang para mapear códigos dispersos a índices compactos (0, 1, 2...)
tzcnt   rax, rcx                ; Contar ceros antes del primer bit activo
mov     eax, dword ptr [HandlerTable + rax*4]
```

#### C. Agrupamiento por Clústeres (*Clustered Jump Tables*)
Si un `switch` contiene 40 casos, pero 20 de ellos están concentrados entre `100` y `120`, y otros 20 entre `5000` y `5020`, MSVC normalmente descartaría la tabla de saltos continua (porque requeriría una tabla de 5000 entradas llena de punteros al `default`) y caería en un árbol binario de 40 comparaciones.

Clang, por el contrario, divide el problema:
1. Emite una primera comparación para decidir a qué clúster pertenece el valor:
   `cmp eax, 2000; jge cluster_alto`.
2. Dentro de cada clúster, sustrae la base del grupo (`sub eax, 100` o `sub eax, 5000`) y ejecuta una **mini-tabla de saltos de solo 20 entradas**.
3. En el desensamblador, el analista observa múltiples instrucciones `jmp [rdata + offset]` dentro de una misma función, todas convergiendo en la misma lógica de salida.

---

## 1.3 Auto-Vectorización Agresiva en Lógica de Negocio y Parsers (AVX2 / SSE4.2)

Una de las marcas de identidad más profundas de LLVM en Windows es su motor de auto-vectorización (*Loop Vectorizer* y *SLP Vectorizer*). Mientras que `cl.exe` tradicionalmente requiere directivas explícitas (`#pragma loop(ivdep)`) o banderas agresivas (`/arch:AVX2`) para emitir instrucciones SIMD fuera de bibliotecas numéricas, **`clang-cl` vectoriza código de procesamiento de cadenas, buffers e I/O de manera predeterminada bajo `/O2`**.

### El Patrón de Búsqueda y Comparación Vectorizada
Considere un parser de texto trivial en C:
```c
// Búsqueda de fin de línea o terminador en un buffer HTTP
const char* find_delimiter(const char* buf, size_t max_len) {
    for (size_t i = 0; i < max_len; ++i) {
        if (buf[i] == '\n' || buf[i] == '\r' || buf[i] == '\0') {
            return &buf[i];
        }
    }
    return NULL;
}
```

En MSVC tradicional, este código compila a un bucle simple de lectura byte a byte (`movzx eax, byte ptr [rcx + rdx]`, seguido de 3 comparaciones y saltos).

En `clang-cl` con arquitectura AVX2 habilitada, el desensamblado se transforma radicalmente:

```assembly
; ==============================================================================
; Bucle Vectorizado por LLVM (AVX2) para Búsqueda de Caracteres
; ==============================================================================
vmovdqu     ymm0, ymmword ptr [rdata_nl_pattern]   ; ymm0 = broadcast de '\n' (32 copias)
vmovdqu     ymm1, ymmword ptr [rdata_cr_pattern]   ; ymm1 = broadcast de '\r' (32 copias)
vpxor       ymm2, ymm2, ymm2                       ; ymm2 = vector de ceros '\0'

loc_vector_loop:
vmovdqu     ymm3, ymmword ptr [rcx]                ; Cargar 32 bytes del buffer simultáneamente
vpcmpeqb    ymm4, ymm3, ymm0                       ; Comparar 32 bytes contra '\n' en paralelo
vpcmpeqb    ymm5, ymm3, ymm1                       ; Comparar 32 bytes contra '\r' en paralelo
vpcmpeqb    ymm6, ymm3, ymm2                       ; Comparar 32 bytes contra '\0' en paralelo

vpor        ymm4, ymm4, ymm5                       ; Unir resultados (OR lógico)
vpor        ymm4, ymm4, ymm6                       ; ymm4 tiene 0xFF en las posiciones coincidentes

vpmovmskb   eax, ymm4                              ; EXTRAER MÁSCARA: convierte los 32 bytes de ymm4
                                                   ; en una máscara de 32 bits en el registro EAX
test        eax, eax                               ; ¿Hubo alguna coincidencia en estos 32 bytes?
jnz         loc_match_found                        ; Si EAX != 0, encontramos al menos un delimitador

add         rcx, 20h                               ; Avanzar el puntero 32 bytes de una sola vez
sub         rdx, 20h
ja          loc_vector_loop

; Rutina de resolución del índice exacto:
loc_match_found:
tzcnt       eax, eax                               ; Contar ceros a la derecha en la máscara:
                                                   ; EAX contiene el índice exacto (0 a 31) del primer match
add         rax, rcx                               ; RAX = dirección exacta de memoria del delimitador
ret
```

### Cómo Interpretarlo en el Descompilador
Cuando Ghidra o IDA Pro se enfrentan a esta secuencia, suelen generar pseudocódigo plagado de tipos intrínsecos como:
```c
__m256i v3 = _mm256_loadu_si256((const __m256i *)buf);
int mask = _mm256_movemask_epi8(_mm256_or_si256(...));
```
**Estrategia para el Analista:**
1. No pierda tiempo intentando rastrear cada registro vectorial individualmente (`ymm0` a `ymm6`).
2. Busque inmediatamente la instrucción **`vpmovmskb eax, ymm`** o **`pmovmskb eax, xmm`**. Esa instrucción marca la frontera donde el dominio vectorial se condensa a un valor escalar estándar.
3. Observe la instrucción inmediatamente posterior a la máscara: si es un **`tzcnt eax, eax`** (o `bsf`), la función está buscando la **primera ocurrencia** de un byte específico dentro de un bloque de memoria de 16 o 32 bytes.
4. Puede renombrar la función completa como una rutina optimizada equivalente a `memchr` o `strpbrk`.

---

## 1.4 Clang Forward-Edge CFI frente a kCFG de Microsoft

Uno de los avances más críticos en mitigaciones de seguridad modernas es el blindaje de las transferencias de control indirectas hacia adelante (*Forward-Edge Control Flow Integrity*), diseñado para impedir que un atacante sobreescriba punteros a funciones o tablas virtuales (Vtables) para redirigir la ejecución hacia primitivas de ataque.

Existen dos filosofías radicalmente distintas para resolver este problema en Windows:

### A. El Modelo kCFG de Microsoft (Control Flow Guard)
Como se estudió en la Lección 5.2.b (Tomo I, págs. 332–335) y en la Lección 6.6 (Tomo II, pág. 47), el CFG de Microsoft se basa en una arquitectura cooperativa entre el compilador, el enlazador y el kernel de Windows:
1. En tiempo de compilación, `cl.exe /guard:cf` genera una lista con todas las direcciones que son destinos válidos de llamadas indirectas.
2. `link.exe /guard:cf` empaqueta esta lista en un **mapa de bits de direcciones válidas** dentro del directorio `IMAGE_DIRECTORY_ENTRY_LOAD_CONFIG` del archivo PE.
3. En ejecución, antes de cada llamada indirecta, el código invoca un puntero a función guardián provisto por `ntdll.dll` (en modo usuario) o por `ntoskrnl.exe` (en modo kernel):
   ```assembly
   ; Patrón de kCFG en MSVC (Plantilla 17b)
   mov     rax, qword ptr [rbx + 10h]               ; RAX = puntero a función indirecta
   mov     rcx, rbx                                ; RCX = argumento 'this'
   call    qword ptr [__guard_dispatch_icall_fptr] ; Valida RAX contra el mapa de bits del PE
   call    rax                                     ; Salto real sólo si es válido
   ```
4. **Debilidad de kCFG:** El mapa de bits es **grueso** (*coarse-grained*): cualquier función cuya dirección haya sido exportada o registrada como destino válido en cualquier parte del binario es considerada un destino legal, incluso si tiene una firma de parámetros completamente diferente.

### B. El Modelo Clang CFI (Forward-Edge Type-Based CFI)
Clang aborda el problema sin depender de mapas de bits en memoria ni de APIs del sistema operativo. Implementa un esquema de **Integridad Basada en Tipos de Grano Fino** (*Fine-Grained Type-Based CFI*), activado mediante `-fsanitize=cfi` y requiriendo Link-Time Optimization (`-flto`):

```
                   MECANISMO DE CHEQUEO INLINE DE CLANG CFI
                   
  [ Puntero a Función / Vtable ]
              │
              ├──> 1. Restar 4 o 8 bytes a la dirección destino: [Target - 4]
              ├──> 2. Cargar el prefijo de hash de tipo inyectado por LLVM
              ├──> 3. Comparar contra el Hash Canónico del Prototipo (cmp hash, CONST)
              │
              ├─── (Coincide: Firma Exacta) ────────> call Target  (Ejecución normal)
              │
              └─── (No Coincide: Type Mismatch) ───> ud2          (Undefined Instruction Trap)
```

#### Anatomía en el Desensamblador
En un binario compilado con `clang-cl` bajo Clang CFI, una llamada a un método virtual no salta a ningún despachador externo de Windows. En su lugar, el código inyecta una comprobación de tipo inmediata seguida de una trampa de CPU:

```assembly
; ==============================================================================
; Desensamblado de Clang CFI (Plantilla 17a)
; ==============================================================================
mov     rax, qword ptr [rcx]           ; RAX = vtable del objeto
mov     r10, qword ptr [rax + 08h]     ; R10 = puntero al método virtual a invocar

; Comprobación de integridad de firma de tipo previa a la llamada:
mov     eax, dword ptr [r10 - 04h]     ; Cargar el Type Hash inyectado antes del prólogo
cmp     eax, 0A3B5F19h                 ; ¿Coincide exactamente con el hash del prototipo?
jne     loc_cfi_trap                   ; Si difiere -> Trampa de terminación inmediata

call    r10                            ; Llamada segura: el destino tiene la firma exacta
...

loc_cfi_trap:
ud2                                    ; Opcode: 0F 0B -> STATUS_ILLEGAL_INSTRUCTION
```

### Tabla Comparativa: Clang CFI vs. MSVC kCFG

| Atributo Técnico | Clang Forward-Edge CFI (`-fsanitize=cfi`) | Microsoft Control Flow Guard (`/guard:cf`) |
|---|---|---|
| **Granularidad** | **Fina (*Fine-grained*):** Exige que el destino coincida en la firma estricta de tipos de la función. | **Gruesa (*Coarse-grained*):** Cualquier función marcada en el mapa de bits es válida. |
| **Dependencia del S.O.** | **Ninguna:** Todo el chequeo es código emitido por el compilador en el espacio del binario. | **Alta:** Depende del cargador de NT, de `ntdll!LdrpValidateUserCallTarget` o `guard_dispatch_icall`. |
| **Mecanismo de Parada** | Instrucción de máquina **`ud2`** (`0F 0B`), disparando `STATUS_ILLEGAL_INSTRUCTION`. | Invocación a `int 0x29` con fast-fail `FAST_FAIL_CONTROL_PROTECTION_USER`. |
| **Requisitos de Compilación**| Requiere **Link-Time Optimization (`-flto`)** y generación de código unificada en LLVM. | Funciona en compilación modular clásica módulo por módulo sin LTO estricto. |

---

## 1.5 Reversing de Binarios Rust Endurecidos (`lto = "fat"`, `panic = "abort"`, `strip = true`)

En la Lección 2.32 (Tomo I, págs. 243–247) se estudiaron las características básicas de los binarios de Rust en Windows: el esquema de nombres *mangling v0* y cómo las cadenas de pánico emitidas por `core::panicking::panic_fmt` permiten al reverser reconstruir los nombres de los archivos `.rs` y los números de línea originales.

Sin embargo, cuando un software escrito en Rust se compila con su perfil de producción endurecido al máximo, **todos esos oráculos semánticos desaparecen**.

### Configuración del Perfil Endurecido en `Cargo.toml`
```toml
[profile.release]
opt-level = 3           # Máxima optimización de velocidad
lto = "fat"             # Link-Time Optimization en todo el árbol de crates
codegen-units = 1       # Una sola unidad de generación (máximo inlining cruzado)
panic = "abort"         # Eliminar el sistema de desenrollado de excepciones (unwind)
strip = true            # Remover todos los símbolos, tablas de debug y metadatos
```

### El Impacto en la Estructura PE
1. **Desaparición de Tablas de Excepción en `.pdata`:**
   * Al configurar `panic = "abort"`, Rust no emite descriptores de excepción SEH para manejar pánicos recuperables con `std::panic::catch_unwind`.
   * En su lugar, cuando ocurre una violación de límites (*bounds check* fallido en un vector o array), el código no invoca a `core::panicking::panic_bounds_check` con cadenas descriptivas; simplemente ejecuta una trampa inmediata `ud2` o invoca `AbortProcess`.
   * El directorio de excepciones del PE se reduce al mínimo indispensable requerido por la ABI x64 de Windows para el desenrollado del sistema operativo.
2. **Eliminación Total de Rutas de Fuentes (`.rs`):**
   * El comando `strings` sobre el archivo binario final **no muestra una sola referencia a rutas de disco** (como `C:\Users\...\src\main.rs`), las cuales son típicas en binarios en modo debug o release estándar.
3. **Inlining Cruzado y Pérdida de Fronteras Modulares:**
   * Con `lto = "fat"` y `codegen-units = 1`, el compilador cruza los límites entre bibliotecas (*crates*). Funciones pertenecientes a crates externos de criptografía o parsing se fusionan en el interior de la función invocadora, eliminando las llamadas `call` intermedias que permitirían identificar una biblioteca de terceros por sus límites externos.

### La ABI de Rust y la Convención de Retorno Múltiple
A diferencia de C (donde la convención Microsoft x64 establece que un valor entero o puntero se retorna exclusivamente en `RAX`), **Rust no utiliza la ABI de C para sus funciones internas**.

Una de las construcciones más frecuentes en Rust es el tipo `Result<T, E>` o tuplas compuestas `(T, U)`:
```rust
// Función en Rust que retorna una tupla compuesta
fn parse_record(data: &[u8]) -> Result<(u64, u32), ErrorCode> { ... }
```

En el desensamblador de Ghidra o IDA Pro, esto se traduce en una convención de retorno distribuida a lo largo de múltiples registros:
* `RAX`: Contiene el primer campo del struct o el valor discriminante (`0` para `Ok`, `1` para `Err`).
* `RDX`: Contiene el valor principal `u64`.
* `R8D`: Contiene el valor secundario `u32`.
* `R9D`: Contiene el código de error en caso de fallo.

**Técnica de Reversing:**  
Si el analista intenta tipar la función en Ghidra como retornando un `uint64_t`, el descompilador considerará que las escrituras en `RDX` y `R8D` son operaciones huérfanas o efectos secundarios de registros no preservados. Para resolver esto:
1. Cree en Ghidra una estructura sintética que agrupe los retornos:
   ```c
   struct RustResult_Record {
       uint64_t discriminant;
       uint64_t field_0;
       uint32_t field_1;
   };
   ```
2. Modifique la firma de la función para retornar este struct por valor, obligando al motor de análisis a mapear los registros de salida coherentemente.

---

## 1.6 Reconstrucción de Slices (`&str`, `&[u8]`) y Blobs de Memoria sin Terminador Nulo

El choque metodológico más severo al analizar un binario de Rust frente a uno de C/C++ radica en cómo se almacenan y consumen las cadenas de texto y los arreglos contiguos en memoria.

### La Representación en Memoria de un Slice
En C clásico:
* Una cadena `"Hola Mundo"` se almacena en `.rdata` como una secuencia de bytes con un terminador nulo al final:
  `48 6F 6C 61 20 4D 75 6E 64 6F 00` (11 bytes en total).
* Las APIs como `strlen`, `strcpy` o `printf("%s")` confían ciegamente en el byte `0x00` final para detener la lectura.

En Rust:
* Un slice de cadena (`&str`) o de bytes (`&[u8]`) es un objeto gordo (*fat pointer*) compuesto por **dos palabras de 64 bits (16 bytes)**:
  1. `ptr`: Puntero a la dirección base del primer byte.
  2. `len`: Longitud exacta en bytes del segmento.
* **No existe ningún terminador nulo.**

```
                       ANATOMÍA DE SLICES EN RUST (.RDATA)
                       
  Sección .rdata (Blob monolítico continuo sin bytes 0x00):
  ┌────────────────────────────────────────────────────────────────────────┐
  │ GET /api/v1/statusPOST /auth/loginAuthorization: Bearer User-Agent:    │
  └────────────────────────────────────────────────────────────────────────┘
    ▲                 ▲                 ▲
    │                 │                 │
    │ Slice 1:        │ Slice 2:        │ Slice 3:
    │ ptr: .rdata+0   │ ptr: .rdata+18  │ ptr: .rdata+34
    │ len: 18         │ len: 16         │ len: 22
```

### El Efecto "Pared de Texto" en el Desensamblador
En el binario compilado:
1. El compilador empaqueta **todos los literales de cadena del programa en un único blob continuo** en la sección `.rdata`.
2. Las cadenas no tienen separadores nulos. Si un string dice `"GET /api/v1/status"` y el siguiente es `"POST /auth/login"`, en memoria aparecen contiguos: `GET /api/v1/statusPOST /auth/login`.
3. Si el reverser ejecuta la utilidad tradicional `strings.exe`, verá palabras fusionadas en bloques ininteligibles.
4. En el código ensamblador, las referencias se resuelven pasando el puntero base en un registro y la longitud en otro:
   ```assembly
   ; Referencia a Slice en código Rust x64
   lea     rcx, [rdata_monolithic_blob + 12h]    ; RCX = Puntero al inicio del texto
   mov     rdx, 10h                              ; RDX = Longitud exacta: 16 bytes
   call    procesar_token                        ; La función solo lee exactamente 16 bytes
   ```

### Script de Laboratorio: Reconstrucción Automatizada de Slices
Para resolver este problema de forma desatendida en Ghidra, la **Plantilla 18** incluye el script en Python [`reconstruct_slices.py`](file:///C:/Users/agust/.gemini/antigravity/scratch/CLS_Guia/plantillas_codigo/plantilla_18_rust_lto/reconstruct_slices.py), el cual automatiza el desempaquetado de cadenas:

1. **Algoritmo del Script:**
   * Escanea las instrucciones `lea reg1, [mem_rdata]` que apunten a secciones de solo lectura.
   * Verifica si la instrucción subsiguiente o adyacente es un `mov reg2, imm_val` donde `imm_val` sea un valor entero razonable de longitud ($1 \le \text{len} \le 1024$).
   * Extrae los bytes en el rango `[mem_rdata, mem_rdata + imm_val]`.
   * Si los bytes corresponden a texto ASCII/UTF-8 válido, invoca la API de Ghidra (`createAsciiString`) forzando la longitud exacta sin requerir terminador nulo, y asigna un comentario en el desensamblado con el texto recuperado.

---

## 1.7 Resumen de Prácticas del Módulo 1

Para afianzar los conceptos desarrollados en este módulo, el repositorio incluye los códigos fuentes de validación:
* [`plantillas_codigo/plantilla_17a_clang_cfi.cpp`](file:///C:/Users/agust/.gemini/antigravity/scratch/CLS_Guia/plantillas_codigo/plantilla_17a_clang_cfi.cpp): Demostración de Clang CFI con compilación modular en LLVM 17+ y captura de la instrucción `ud2`.
* [`plantillas_codigo/plantilla_17b_msvc_cfg.c`](file:///C:/Users/agust/.gemini/antigravity/scratch/CLS_Guia/plantillas_codigo/plantilla_17b_msvc_cfg.c): Demostración del modelo Control Flow Guard nativo de Microsoft con `cl.exe /guard:cf` y `guard_dispatch_icall`.
* [`plantillas_codigo/plantilla_18_rust_lto/`](file:///C:/Users/agust/.gemini/antigravity/scratch/CLS_Guia/plantillas_codigo/plantilla_18_rust_lto/): Proyecto Cargo con configuración release monolítica (`lto = "fat"`, `panic = "abort"`, `strip = true`) y el script Python de reconstrucción de slices para Ghidra.
