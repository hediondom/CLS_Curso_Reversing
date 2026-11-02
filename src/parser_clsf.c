// Archivo: plantillas_codigo/parser_clsf.c
// Compilar (MSVC) : cl /Zi /O1 parser_clsf.c /Fe:parser_clsf.exe
// Compilar (MinGW): gcc -O1 -g parser_clsf.c -o parser_clsf.exe
// Generar muestra : parser_clsf.exe --gen muestra_A.clsf
// Analizar muestra: parser_clsf.exe muestra_A.clsf
#include <stdio.h>
#include <stdint.h>
#include <string.h>

#pragma pack(push, 1)
typedef struct {
    uint8_t  magic[4];   // +0x00: "CLSF" (43 4C 53 46)
    uint8_t  version;    // +0x04: 1
    uint8_t  flags;      // +0x05: 0
    uint16_t hdr_len;    // +0x06: 12 (0x000C LE)
    uint16_t body_len;   // +0x08: longitud del cuerpo (LE)
    uint16_t seq_id;     // +0x0A: campo variable / secuencia (0x002A = 42 LE)
} CabeceraCLSF;          // Total cabecera: 12 bytes
#pragma pack(pop)

int main(int argc, char** argv) {
    if (argc == 3 && strcmp(argv[1], "--gen") == 0) {
        CabeceraCLSF h = {{'C','L','S','F'}, 1, 0, 12, 5, 42};
        FILE* f = fopen(argv[2], "wb");
        if (!f) return 1;
        fwrite(&h, sizeof(h), 1, f);
        fwrite("HELLO", 1, 5, f);
        fclose(f);
        puts("Muestra CLSF de 17 bytes generada.");
        return 0;
    }
    if (argc < 2) { puts("Uso: parser_clsf [--gen salida.clsf | entrada.clsf]"); return 1; }
    FILE* f = fopen(argv[1], "rb");
    if (!f) return 2;
    uint8_t buf[256] = {0};
    size_t n = fread(buf, 1, sizeof(buf), f);
    fclose(f);
    if (n < sizeof(CabeceraCLSF)) { puts("Error: archivo truncado"); return 3; }
    const CabeceraCLSF* h = (const CabeceraCLSF*)buf;
    if (memcmp(h->magic, "CLSF", 4) != 0) { puts("Error: magic invalido"); return 4; }
    if (h->version != 1)                  { puts("Error: version no soportada"); return 5; }
    if (h->hdr_len != 12)                 { puts("Error: hdr_len != 12"); return 6; }
    if ((size_t)h->hdr_len + h->body_len > n) { puts("Error: body_len excede archivo"); return 7; }
    printf("CLSF OK | ver=%u flags=0x%02X seq=%u body(%u)=\"%.*s\"\n",
           h->version, h->flags, h->seq_id, h->body_len, h->body_len, (const char*)(buf + h->hdr_len));
    return 0;
}
