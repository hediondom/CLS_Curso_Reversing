// Archivo: plantillas_codigo/heap_bug.c
// Compilar v1 (vulnerable): cl /Zi /O1 heap_bug.c /Fe:heap_bug_v1.exe
// Compilar v2 (parcheada) : cl /Zi /O1 /DPARCHE_SEGURO heap_bug.c /Fe:heap_bug_v2.exe
// En la VM con Page Heap  : gflags /p /enable heap_bug_v1.exe /full
// Ejecutar en WinDbg      : heap_bug_v1.exe AAAAAAAAAAAAAAAAAAAA  --> !heap -p -a @rcx
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    char etiqueta[12];
    unsigned int estado;
} RegistroBloc; // sizeof(RegistroBloc) == 16 bytes exactos

int procesar_entrada(const char* entrada) {
    size_t len = strlen(entrada);
    RegistroBloc* reg = (RegistroBloc*)malloc(sizeof(RegistroBloc));
    if (!reg) return -1;
    reg->estado = 0xCAFE0001u;

#ifdef PARCHE_SEGURO
    // Version v2 corregida: valida el limite antes de copiar (Lecciones 2.20 y 5.2)
    if (len >= sizeof(reg->etiqueta)) {
        puts("Error: entrada excede el buffer de 12 bytes");
        free(reg);
        return 1;
    }
    memcpy(reg->etiqueta, entrada, len + 1);
#else
    // Version v1 con defecto didactico: copia hasta 20 bytes en un bloque de 16 bytes (Leccion 2.19)
    if (len > 20) len = 20;
    memcpy(reg->etiqueta, entrada, len);
    reg->etiqueta[11] = '\0';
#endif
    printf("Registro: %s | Estado: 0x%08X\n", reg->etiqueta, reg->estado);
    free(reg);
    return 0;
}

int main(int argc, char** argv) {
    const char* dato = (argc > 1) ? argv[1] : "BLOC_NORMAL";
    return procesar_entrada(dato);
}
