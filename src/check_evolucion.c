// Archivo: plantillas_codigo/check_evolucion.c
// Compilar Principiante (MSVC): cl /Zi /Od check_evolucion.c /Fe:check_v1_O0.exe
// Compilar Optimizado   (MSVC): cl /Zi /O2 check_evolucion.c /Fe:check_v1_O2.exe
// Compilar Intermedio   (MSVC): cl /Zi /O1 /DMODO_INTERMEDIO check_evolucion.c /Fe:check_v2.exe
// Compilar en MinGW-w64 (GCC) : gcc -O0 -g check_evolucion.c -o check_v1_O0.exe
#include <windows.h>
#include <stdio.h>
#include <stdlib.h>

static int g_objetivo = 480; // 0x1E0 en condiciones normales

#ifdef MODO_INTERMEDIO
static void NTAPI tls_antidebug(PVOID h, DWORD reason, PVOID res) {
    (void)h; (void)res;
    if (reason == DLL_PROCESS_ATTACH && IsDebuggerPresent()) {
        g_objetivo = 999; // Desvia la constante antes de entrar a main (Lecciones 2.11 y 2.15)
    }
}
#ifdef _MSC_VER
#pragma comment(linker, "/INCLUDE:_tls_used")
#pragma section(".CRT$XLB", long, read)
__declspec(allocate(".CRT$XLB")) PIMAGE_TLS_CALLBACK p_tls = tls_antidebug;
#else
PIMAGE_TLS_CALLBACK p_tls __attribute__((used, section(".CRT$XLB"))) = tls_antidebug;
#endif
#endif

int validar_pares(int a, int b) {
    if (a > 50 || b < 50) return 0;
    return ((a + b) * 4) == g_objetivo;
}

int main(int argc, char** argv) {
    int a = (argc > 2) ? atoi(argv[1]) : 0;
    int b = (argc > 2) ? atoi(argv[2]) : 0;
    if (argc <= 2) {
        printf("Primer valor: ");  if (scanf("%d", &a) != 1) return 1;
        printf("Segundo valor: "); if (scanf("%d", &b) != 1) return 1;
    }
    if (validar_pares(a, b)) {
#ifdef MODO_INTERMEDIO
        // "Correcto" cifrado con XOR 0x5A (Lecciones 2.10 y 4.2)
        unsigned char enc[] = {0x19, 0x35, 0x28, 0x28, 0x3F, 0x39, 0x2E, 0x35, 0x00};
        for (int i = 0; enc[i] != 0; ++i) enc[i] ^= 0x5A;
        puts((const char*)enc);
#else
        puts("Correcto");
#endif
        return 0;
    }
    puts("Incorrecto");
    return 1;
}
