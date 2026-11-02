// ==============================================================================
// Plantilla 17a · Demostración de Clang CFI (Forward-Edge Type-Based Integrity)
// Obra: Reversing en Windows — Tomo III (Módulo 1)
//
// Invocación recomendada (LLVM 17+ en Windows con lld-link):
//   clang-cl -O2 -flto=thin -fsanitize=cfi -fuse-ld=lld-link plantilla_17a_clang_cfi.cpp -o plantilla_17a.exe
//
// Invocación alternativa en WSL2 / Linux (si el target msvc carece de lld-link):
//   clang++ -O2 -flto -fsanitize=cfi -fvisibility=hidden plantilla_17a_clang_cfi.cpp -o plantilla_17a_elf
//
// Mecánica en Desensamblador:
//   Previo al 'call [rax + offset]', Clang inserta una comprobación de tipo
//   cargando el Type Hash en [Target - 4]. Si no coincide -> trampa 'ud2' (0F 0B).
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

// Implementación con firma incompatible o clase ajena (objetivo de secuestro de vtable)
class FileDumper {
public:
    virtual ~FileDumper() = default;
    virtual void DumpPayload(const char* path) {
        printf("[!] PELIGRO: FileDumper::DumpPayload ejecutado indebidamente con argumento: %s\n", path);
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
