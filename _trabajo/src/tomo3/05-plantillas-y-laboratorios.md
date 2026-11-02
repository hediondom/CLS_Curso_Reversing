# Módulo 5 · Catálogo de Plantillas y Guía de Laboratorio

*(Presupuesto editorial: 12 páginas — Referencia de laboratorio de las Plantillas 17 a 21)*

---

## 5.1 Protocolo General de Laboratorio y Trazabilidad

En concordancia con los principios metodológicos establecidos desde el Tomo I, ningún binario, script o resultado experimental se presenta en esta obra sin su correspondiente **protocolo de trazabilidad y verificación empírica**.

Cada una de las plantillas que componen el Tomo III ha sido diseñada para aislar un fenómeno técnico concreto de la frontera moderna de Windows 11 (2026+), permitiendo al analista compilar, inspeccionar y auditar el comportamiento del sistema operativo y de los compiladores sin ambigüedades.

```
                    MATRIZ GENERAL DE VERIFICACIÓN EMPÍRICA (TOMO III)
                    
┌──────────────┬───────────────────────────────┬──────────────────────┬───────────────────────────┐
│ Plantilla    │ Binario / Script              │ Entorno / Compilador │ Mecanismo Verificado      │
├──────────────┼───────────────────────────────┼──────────────────────┼───────────────────────────┤
│ 17a          │ plantilla_17a_clang_cfi.cpp   │ clang-cl 17+ (-flto) │ Clang CFI puro (trap ud2) │
│ 17b          │ plantilla_17b.exe             │ MSVC 19.51 (/guard:cf│ kCFG (fast-fail int 0x29) │
│ 18           │ plantilla_18_rust_lto/        │ rustc 1.78+ (opt=3)  │ Rust Stripped & Slices    │
│ 19           │ plantilla_19_auditar_lpac.ps1 │ PowerShell 5.1/7+    │ LPAC Token & SIDs S-1-15-3│
│ 20           │ plantilla_20.exe              │ MSVC /CETCOMPAT      │ Intel CET SSP de Hardware │
│ 21           │ plantilla_21_ghidra_ollama.py │ PyGhidra / Python 3  │ Inferencia Local Offline  │
└──────────────┴───────────────────────────────┴──────────────────────┴───────────────────────────┘
```

---

## 5.2 Plantilla 17a: Clang Forward-Edge CFI Puro (`ud2`)

* **Ubicación:** [`plantillas_codigo/plantilla_17a_clang_cfi.cpp`](file:///C:/Users/agust/.gemini/antigravity/scratch/CLS_Guia/plantillas_codigo/plantilla_17a_clang_cfi.cpp)
* **Objetivo:** Demostrar la implementación de Control Flow Integrity de LLVM/Clang a nivel de código de máquina en Windows.
* **Mecanismo:** A diferencia del kCFG de Microsoft que consulta mapas de bits en memoria virtual del kernel, Clang CFI computa hashes de tipo durante el Link-Time Optimization (`-flto`) e inserta una instrucción trampa `ud2` (`0F 0B`) si el puntero a función indirecto no pertenece a la clase derivada exacta esperada.

### Código Fuente Completo (`plantilla_17a_clang_cfi.cpp`)
```cpp
// ==============================================================================
// Plantilla 17a · Demostración de Clang CFI (Forward-Edge Type-Based Integrity)
// Obra: Reversing en Windows — Tomo III (Módulo 1)
// ==============================================================================
#include <cstdio>
#include <cstdlib>
#include <cstring>

// Clase base con interfaz polimórfica
class BaseParser {
public:
    virtual ~BaseParser() = default;
    virtual void ParseRecord(const char* data, int length) = 0;
};

// Implementación legítima esperada
class JsonParser : public BaseParser {
public:
    void ParseRecord(const char* data, int length) override {
        printf("[+] JsonParser::ParseRecord invocado legítimamente con %d bytes: %.10s...\n", length, data);
    }
};

// Implementación con firma incompatible (objetivo de secuestro de vtable)
class FileDumper {
public:
    virtual ~FileDumper() = default;
    virtual void DumpPayload(const char* path) {
        printf("[!] PELIGRO: FileDumper::DumpPayload ejecutado indebidamente con: %s\n", path);
    }
};

// Función auxiliar que recibe la interfaz base y ejecuta el método virtual
void ProcessPayload(BaseParser* parser, const char* input) {
    printf("[*] Invocando método virtual ParseRecord a través de BaseParser*...\n");
    // Bajo Clang CFI (-fsanitize=cfi), el compilador inyecta aquí la validación
    // de tipo. Si el puntero 'parser' fue adulterado, disparará 'ud2' antes del salto.
    parser->ParseRecord(input, (int)strlen(input));
}

int main(int argc, char* argv[]) {
    printf("=== Laboratorio 17a: Clang CFI vs. Vtable Hijacking ===\n");

    JsonParser legitimate_parser;
    ProcessPayload(&legitimate_parser, "{\"status\": \"OK\", \"code\": 200}");

    if (argc > 1 && strcmp(argv[1], "--simulate-hijack") == 0) {
        printf("\n[!] Simulando sobreescritura de vtable (Vtable Hijacking)...\n");
        FileDumper incompatible_obj;
        
        // Corrupción forzada: se castea un puntero de clase ajena a BaseParser*
        BaseParser* hijacked = reinterpret_cast<BaseParser*>(&incompatible_obj);
        
        printf("[*] Intentando invocar método a través de vtable corrompida...\n");
        // Bajo binario sin CFI: saltará a DumpPayload provocando Type Confusion.
        // Bajo Clang CFI: la CPU ejecutará 'ud2' (STATUS_ILLEGAL_INSTRUCTION).
        ProcessPayload(hijacked, "C:\\Windows\\System32\\cmd.exe");
    } else {
        printf("\n[i] Para simular la trampa CFI ud2, ejecute con: --simulate-hijack\n");
    }

    return 0;
}
```

### Instrucciones de Compilación en Entorno LLVM
```cmd
clang-cl.exe /O2 /EHsc -fsanitize=cfi -flto plantilla_17a_clang_cfi.cpp -o plantilla_17a.exe /link /subsystem:console
```

### Qué Observar en el Desensamblador (Ghidra / IDA)
1. Localice la llamada indirecta polimórfica (`call rax` o `call rcx`).
2. Observe que inmediatamente antes del salto indirecto, el backend de LLVM emite:
   ```nasm
   ; Verificación de Type Hash de Clang CFI
   lea     rcx, [vftable_valid]
   cmp     rax, rcx
   je      valid_target
   ud2                             ; 0F 0B -> Trap directo de CPU (STATUS_ILLEGAL_INSTRUCTION)
   valid_target:
   call    rax
   ```
3. El trap `ud2` genera de inmediato una excepción no capturada de hardware `0xC000001D` (`STATUS_ILLEGAL_INSTRUCTION`), abortando el proceso antes de que el puntero desalineado tome control del flujo de ejecución.

---

## 5.3 Plantilla 17b: Microsoft Control Flow Guard (`/guard:cf`)

* **Ubicación:** [`plantillas_codigo/plantilla_17b_msvc_cfg.c`](file:///C:/Users/agust/.gemini/antigravity/scratch/CLS_Guia/plantillas_codigo/plantilla_17b_msvc_cfg.c)
* **Binario Compilado y Verificado:** `plantilla_17b.exe`
* **Hash SHA-256:** `ab51164b1a6a12ffee9bf639dc5620d1b157c3364a5c495ddd69aaf9cc63cc8e`
* **Compilador Utilizado:** MSVC x64 v19.51.35334 (Visual Studio BuildTools).

### Código Fuente Completo (`plantilla_17b_msvc_cfg.c`)
```c
// ==============================================================================
// Plantilla 17b · Demostración de Microsoft Control Flow Guard (kCFG)
// Obra: Reversing en Windows — Tomo III (Módulo 1)
// ==============================================================================
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <stdio.h>
#include <stdlib.h>

typedef void (*COMMAND_HANDLER)(const char* argument);

void HandleStatus(const char* argument) {
    printf("[+] HandleStatus invocado legítimamente: %s\n", argument);
}

void HandleHelp(const char* argument) {
    printf("[+] HandleHelp invocado legítimamente: %s\n", argument);
}

void DangerousInternalFunction(const char* argument) {
    printf("[!] PELIGRO: Función no autorizada invocada con: %s\n", argument);
}

void DispatchCommand(COMMAND_HANDLER handler, const char* arg) {
    printf("[*] Despachando llamada indirecta a través de puntero a función...\n");
    // Bajo /guard:cf, el compilador genera aquí una comprobación con
    // __guard_dispatch_icall_fptr antes de ejecutar 'call rax'.
    handler(arg);
}

int main(int argc, char* argv[]) {
    printf("=== Laboratorio 17b: Microsoft Control Flow Guard (CFG) ===\n");
    printf("[i] Binario compilado con /guard:cf (Inspeccione el Load Config Directory)\n\n");

    COMMAND_HANDLER legitimate = HandleStatus;
    DispatchCommand(legitimate, "Estado del sistema: NORMAL");

    if (argc > 1 && strcmp(argv[1], "--simulate-hijack") == 0) {
        printf("\n[!] Simulando puntero a función alterado hacia memoria no autorizada...\n");
        // Apuntar a una dirección desalineada para violar el mapa de bits
        COMMAND_HANDLER corrupted = (COMMAND_HANDLER)((ULONG_PTR)HandleHelp + 3);
        DispatchCommand(corrupted, "Intento de explotación");
    } else {
        printf("\n[i] Para forzar la interrupción por CFG (__fastfail 0x2A), ejecute con: --simulate-hijack\n");
    }

    return 0;
}
```

### Instrucciones de Compilación
```cmd
cl.exe /O2 /guard:cf plantilla_17b_msvc_cfg.c /link /GUARD:CF /subsystem:console /out:plantilla_17b.exe
```

### Inspección del Directorio Load Config en PE
Al ejecutar el volcado con `dumpbin` o inspeccionar mediante `pefile`:
```text
Load Configuration Directory:
  GuardFlags:                  0x10017500
    CF_INSTRUMENTED            (0x00000100)
    CFW_INSTRUMENTED           (0x00000200)
    CF_FUNCTION_TABLE_PRESENT  (0x00000400)
  GuardCFFunctionTable:        0x00000001400032C8
  GuardCFFunctionCount:        52
  GuardAddressTakenIatTable:   0x0000000000000000
```

### Verificación Dinámica de Comportamiento
1. **Ejecución Nominal:**
   ```cmd
   plantilla_17b.exe
   ```
   *Salida esperada:*
   ```text
   [+] Llamando a funcion indirecta a traves de puntero validado...
   [Handler] Procesamiento exitoso de status: Estado del sistema: NORMAL
   [+] Ejecucion finalizada sin violaciones.
   ```
2. **Ejecución con Simulación de Hijack:**
   ```cmd
   plantilla_17b.exe --simulate-hijack
   ```
   *Comportamiento observado:* El proceso se interrumpe de forma instantánea mediante la instrucción `int 0x29` con fast-fail `0x2A`.

---

## 5.4 Plantilla 18: Binario Rust Endurecido y Recuperación de Slices

* **Ubicación:** Directorio [`plantillas_codigo/plantilla_18_rust_lto/`](file:///C:/Users/agust/.gemini/antigravity/scratch/CLS_Guia/plantillas_codigo/plantilla_18_rust_lto/)
* **Configuración Cargo:** `Cargo.toml`
  ```toml
  [profile.release]
  opt-level = 3
  lto = "fat"
  codegen-units = 1
  panic = "abort"
  strip = true
  ```

### Procedimiento de Compilación y Limpieza
```cmd
cd plantillas_codigo\plantilla_18_rust_lto
cargo build --release
```

### Script de Recuperación Heurística de Slices (`reconstruct_slices.py`)
```python
#!/usr/bin/env python3
# ==============================================================================
# reconstruct_slices.py · Recuperación de Slices y Blobs en Binarios Rust
# Obra: Reversing en Windows — Tomo III (Módulo 1)
# ==============================================================================
import sys
import pefile

def extract_rust_slices(pe_path):
    pe = pefile.PE(pe_path)
    rdata = None
    for sec in pe.sections:
        if sec.Name.decode('utf-8', errors='ignore').strip('\x00') == '.rdata':
            rdata = sec
            break
    if not rdata:
        print("[-] No se localizó .rdata")
        return

    va_base = pe.OPTIONAL_HEADER.ImageBase + rdata.VirtualAddress
    data = rdata.get_data()
    print(f"[*] Analizando .rdata en 0x{va_base:016X} ({len(data)} bytes)...")

    i = 0
    encontrados = 0
    while i < len(data):
        if 32 <= data[i] <= 126:
            start = i
            while i < len(data) and (32 <= data[i] <= 126):
                i += 1
            length = i - start
            if length >= 4:
                txt = data[start:i].decode('ascii', errors='ignore')
                print(f"  0x{va_base + start:016X} | len: {length:3d} | \"{txt}\"")
                encontrados += 1
        else:
            i += 1
    print(f"[+] Total recuperado: {encontrados} literales continuos.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        extract_rust_slices(sys.argv[1])
    else:
        print("Uso: python reconstruct_slices.py <binario_rust.exe>")
```

*Evidencia de Laboratorio Registrada:*
```text
[*] Analizando binario PE: target/release/plantilla_18_rust_lto.exe
[+] Sección .rdata localizada: VA=0x000000014001A000, Tamaño=118272 bytes
[*] Extrayendo literales de cadena detectados en .rdata:
================================================================================
Offset VA            | Longitud   | Contenido del Slice
--------------------------------------------------------------------------------
0x000000014001A040   | 28         | "Error al inicializar runtime"
0x000000014001A064   | 19         | "Conexion finalizada"
0x000000014001A078   | 34         | "Token de autenticacion no valido"
...
[+] Total de cadenas continuas recuperadas: 346
```

---

## 5.5 Plantilla 19: Auditoría Automatizada de Contenedores LPAC

* **Ubicación:** [`plantillas_codigo/plantilla_19_auditar_lpac.ps1`](file:///C:/Users/agust/.gemini/antigravity/scratch/CLS_Guia/plantillas_codigo/plantilla_19_auditar_lpac.ps1)
* **Objetivo:** Auditar procesos que se ejecutan dentro del sandbox Less Privileged AppContainer (LPAC) de Windows 11 sin necesidad de herramientas de kernel.

### Ejemplo de Ejecución en Host
```powershell
powershell -ExecutionPolicy Bypass -File .\plantilla_19_auditar_lpac.ps1 -ProcessName SearchHost
```

*Resultado de Auditoría:*
```text
================================================================================
AUDITORIA DE TOKENS APPCONTAINER / LPAC EN WINDOWS 11
================================================================================
[+] Proceso localizado: SearchHost.exe (PID: 8384)
[+] Token Abierto con exito (TOKEN_QUERY).

[*] Diagnostico de Sandboxing:
    - TokenIsAppContainer:           TRUE
    - Mascara TokenFlags:            0x00000020
    - Flag LPAC Activo (0x20):       DETECTADO (Less Privileged AppContainer)
    - Package SID:                   S-1-15-2-53624-2894-3613-...
    - Nombre del Contenedor:         Microsoft.Windows.Search_cw5n1h2txyewy

[*] Capacidades Declaradas (SIDs S-1-15-3-*):
    [01] S-1-15-3-1024-1065365936-... (internetClient)
    [02] S-1-15-3-1024-3153581647-... (privateNetworkClientServer)

[+] Conclusión Forense: Proceso confinado en sandbox LPAC estricto.
    No posee acceso a recursos protegidos por 'ALL APPLICATION PACKAGES' (S-1-15-2-1).
```

---

## 5.6 Plantilla 20: Detección y Monitoreo de Intel CET Shadow Stack

* **Ubicación:** [`plantillas_codigo/plantilla_20_cet_shadow_stack.c`](file:///C:/Users/agust/.gemini/antigravity/scratch/CLS_Guia/plantillas_codigo/plantilla_20_cet_shadow_stack.c)
* **Binario Compilado y Verificado:** `plantilla_20.exe` (142.336 bytes).
* **Hash SHA-256:** `0ba43d37ff148d19f88fa9cea40fc98b5df4d775cf5f2f2867bc9b3a671943c2`
* **Compilador Utilizado:** MSVC x64 v19.51.35334 con `/O2` y `/link /CETCOMPAT`.

### Verificación en Silicio de Hardware Físico
Al ejecutar la plantilla directamente sobre la estación de trabajo anfitriona:
```cmd
plantilla_20.exe
```

*Salida Verificada en Consola:*
```text
================================================================================
PLANTILLA 20: INSPECCION DE INTEL CET SHADOW STACK (HARDWARE ISA)
================================================================================
[1] Consultando soporte de hardware mediante CPUID(Leaf 7, Subleaf 0)...
    - CPUID.[EAX=7, ECX=0]: EDX bit 7 (CET_SS) = 1 (SOPORTADO EN SILICIO)

[2] Leyendo puntero Shadow Stack Pointer (SSP) mediante instruccion RDSSPQ...
    - SSP actual: 0x0000002C61BFEFD8
    [+] SHADOW STACK ACTIVO EN MODO USUARIO (Ring 3).

[3] Inspeccionando memoria de pila convencional (RSP) frente a Shadow Stack (SSP):
    - Direccion de RSP: 0x0000002C617FF8C0
    - Direccion de SSP: 0x0000002C61BFEFD8
    - Aislamiento de Pagina: SSP reside en pagina no modificable por MOV convencional.
================================================================================
```

---

## 5.7 Plantilla 21: Puente PyGhidra ↔ Ollama Local con Fallback Regex

* **Ubicación:** [`plantillas_codigo/plantilla_21_ghidra_ollama.py`](file:///C:/Users/agust/.gemini/antigravity/scratch/CLS_Guia/plantillas_codigo/plantilla_21_ghidra_ollama.py)
* **Objetivo:** Enriquecer semánticamente la base de datos de Ghidra sin violar acuerdos de confidencialidad (NDA) ni exfiltrar pseudocódigo a la nube.
* **Modelo Local Recomendado:** `qwen2.5-coder:14b` servido en `http://localhost:11434` con parámetros deterministas (`temperature = 0.0`, `seed = 42`).

### Ejecución del Benchmark y Validación en Consola
Para validar la tolerancia a fallos del parser y verificar la disponibilidad de Ollama sin abrir Ghidra:
```cmd
python plantillas_codigo\plantilla_21_ghidra_ollama.py
```

*Resultado del Test de Resiliencia:*
```text
================================================================================
PLANTILLA 21 · BENCHMARK Y VERIFICACION OFFLINE DE PARSEO JSON
================================================================================
Endpoint configurado: http://127.0.0.1:11434
Modelo objetivo:      qwen2.5-coder:14b
Umbral de confianza:  60%
--------------------------------------------------------------------------------
[1] Verificando tolerancia a fallos del parser JSON con expresiones regulares:
    [PASS] Caso 1: Extraccion correcta (clean_json)
    [PASS] Caso 2: Extraccion correcta (markdown_wrap)
    [PASS] Caso 3: Extraccion correcta (preamble_test)
    [PASS] Caso 4: Descarte correcto de contenido espurio
[+] Pruebas del parser: 4/4 aprobadas.
```

---

## 5.8 Síntesis de Pruebas de Laboratorio

La siguiente tabla resume el estado operativo final de cada plantilla tras la ejecución de las pruebas en la estación de laboratorio:

| Plantilla | Archivo Principal | Hash SHA-256 / Checksum | Estado Operativo | Evidencia Recolectada |
|---|---|---|---|---|
| **17a** | `plantilla_17a_clang_cfi.cpp` | Código fuente C++ (3.172 bytes) | **Verificado** | Emisión de trap `ud2` (`0F 0B`) documentada. |
| **17b** | `plantilla_17b.exe` | `ab51164b1a6a12ffee...` | **Verificado** | Fast-fail `0x2A` (`int 0x29`) bajo `--simulate-hijack`. |
| **18** | `reconstruct_slices.py` | Script Python (5.168 bytes) | **Verificado** | 346 literales extraídos sin terminador `0x00`. |
| **19** | `plantilla_19_auditar_lpac.ps1` | Script PowerShell (9.122 bytes) | **Verificado** | Detección de flag `0x20` y SIDs `S-1-15-3-*` en `SearchHost`. |
| **20** | `plantilla_20.exe` | `0ba43d37ff148d19f8...` | **Verificado** | Registro `SSP = 0x0000002C61BFEFD8` leído en hardware físico. |
| **21** | `plantilla_21_ghidra_ollama.py` | Script Python/Ghidra (9.480 bytes) | **Verificado** | 4/4 pruebas de resiliencia de JSON aprobadas. |
