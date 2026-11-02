// ==============================================================================
// Plantilla 17b · Demostración de Microsoft Control Flow Guard (kCFG)
// Obra: Reversing en Windows — Tomo III (Módulo 1)
//
// Invocación MSVC x64:
//   cl /W4 /O2 /guard:cf plantilla_17b_msvc_cfg.c /link /guard:cf /out:plantilla_17b.exe
//
// Mecánica en Desensamblador:
//   Antes de cualquier llamada indirecta (*call_target)(...), el código invoca:
//   mov   rax, <dir_destino>
//   call  qword ptr [__guard_dispatch_icall_fptr] ; Valida RAX en bitmap del PE
//   call  rax                                     ; Salto real
// ==============================================================================

#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <stdio.h>
#include <stdlib.h>

// Tipo de puntero a función para la tabla de despacho
typedef void (*COMMAND_HANDLER)(const char* argument);

// Handler legítimo registrado en tiempo de compilación
void HandleStatus(const char* argument) {
    printf("[+] HandleStatus invocado legítimamente: %s\n", argument);
}

void HandleHelp(const char* argument) {
    printf("[+] HandleHelp invocado legítimamente: %s\n", argument);
}

// Función no registrada o ajena a la tabla
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
    printf("[i] Binario compilado con /guard:cf (Inspeccione el Load Config Directory en CFF Explorer)\n\n");

    // Invocación normal legítima
    COMMAND_HANDLER legitimate = HandleStatus;
    DispatchCommand(legitimate, "Estado del sistema: NORMAL");

    if (argc > 1 && strcmp(argv[1], "--simulate-hijack") == 0) {
        printf("\n[!] Simulando puntero a función alterado hacia memoria no autorizada...\n");
        // Apuntar a una dirección arbitraria o en medio de una función
        // En un binario con CFG activo, el kernel / ntdll detecta que el destino
        // no tiene el bit activo en el bitmap de CFG y ejecuta int 0x29 (0xC0000409).
        COMMAND_HANDLER corrupted = (COMMAND_HANDLER)((ULONG_PTR)HandleHelp + 3); // Destino desalineado
        DispatchCommand(corrupted, "Intento de explotación");
    } else {
        printf("\n[i] Para forzar la interrupción por CFG (__fastfail 0x2A), ejecute con: --simulate-hijack\n");
    }

    return 0;
}
