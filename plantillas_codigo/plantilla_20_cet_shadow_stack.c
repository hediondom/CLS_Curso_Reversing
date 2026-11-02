// ==============================================================================
// Plantilla 20 · Demostración de Intel CET (Shadow Stack) y Opcodes de Control
// Obra: Reversing en Windows — Tomo III (Módulo 3)
//
// Invocación MSVC x64:
//   cl /W4 /O2 plantilla_20_cet_shadow_stack.c /link /CETCOMPAT /out:plantilla_20.exe
//
// Requisitos de Ejecución:
//   CPU Intel Core 11.ª gen+ / AMD Zen 3+ (o VM con vCET activado en Hyper-V / VMware).
//   En CPUs sin soporte CET por hardware, la instrucción _rdsspq() retorna 0 y el
//   sistema opera en modo de compatibilidad sin disparar la excepción #CP.
//
// Mecánica en Desensamblador:
//   1. Opcode RDSSP (F3 0F 1E C8) lee el registro de pila sombra de la CPU.
//   2. La instrucción RET compara atómicamente [RSP] == [SSP].
//   3. Si [RSP] fue sobreescrito -> Trampa #CP (STATUS_CONTROL_PROTECTION_EXCEPTION 0xC00006A6)
//      o Fast-Fail de usuario (STATUS_STACK_BUFFER_OVERRUN 0xC0000409 subcódigo 0x2A).
// ==============================================================================

#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <stdio.h>
#include <stdlib.h>
#include <immintrin.h>

// Definición de códigos canónicos
#ifndef STATUS_CONTROL_PROTECTION_EXCEPTION
#define STATUS_CONTROL_PROTECTION_EXCEPTION ((DWORD)0xC00006A6L)
#endif

#ifndef FAST_FAIL_CONTROL_PROTECTION_USER
#define FAST_FAIL_CONTROL_PROTECTION_USER 42 // 0x2A
#endif

// Función auxiliar que intenta leer el Shadow Stack Pointer (SSP)
// Utiliza la instrucción nativa RDSSPQ (en x64) provista por immintrin.h
ULONG_PTR ReadShadowStackPointer(void) {
    ULONG_PTR ssp_val = 0;
#if defined(_M_X64)
    __try {
        // En CPUs x64 compatibles con CET, _rdsspq() emite el opcode 'rdsspq rax'
        ssp_val = (ULONG_PTR)_rdsspq();
    } __except (EXCEPTION_EXECUTE_HANDLER) {
        ssp_val = 0;
    }
#endif
    return ssp_val;
}

// Función objetivo donde se simula una sobreescritura de stack
__declspec(noinline) void TargetVulnerableFunction(int simulate_tamper) {
    volatile ULONG_PTR local_var = 0x1122334455667788ULL;
    printf("[*] Dentro de TargetVulnerableFunction (RSP local=%p)...\n", (void*)&local_var);

    ULONG_PTR current_ssp = ReadShadowStackPointer();
    printf("    Puntero de Pila Sombra (SSP actual) = 0x%016llX\n", (unsigned long long)current_ssp);

    if (current_ssp == 0) {
        printf("    [i] NOTA: SSP reporta 0. La CPU actual no tiene CET activo o vCET está deshabilitado.\n");
    } else {
        printf("    [+] Intel CET SHADOW STACK ACTIVO POR HARDWARE en esta CPU.\n");
    }

    if (simulate_tamper) {
        printf("\n[!] SIMULANDO ATAQUE ROP: Corrompiendo la dirección de retorno en [RSP]...\n");
        // En una arquitectura x64 típica, la dirección de retorno se encuentra
        // en el stack inmediatamente después de las variables locales y el marco guardado.
        volatile ULONG_PTR* stack_frame = (volatile ULONG_PTR*)&local_var;
        
        // Alterar deliberadamente el valor en stack para provocar discrepancia con [SSP]
        stack_frame[2] ^= 0xDEADBEEF00000000ULL;

        printf("[!] Pila convencional modificada. Al ejecutar la instrucción RET:\n");
        printf("    - Si CET está ACTIVO: la CPU detecta [RSP] != [SSP] y aborta con #CP.\n");
        printf("    - Si CET está APAGADO: la CPU saltará a la dirección corrupta y crasheará con 0xC0000005.\n");
    }
}

int main(int argc, char* argv[]) {
    printf("==============================================================================\n");
    printf("[*] Plantilla 20 · Laboratorio de Intel CET y Pila Sombra (Shadow Stack)\n");
    printf("==============================================================================\n");

    int do_tamper = (argc > 1 && strcmp(argv[1], "--tamper") == 0);

    TargetVulnerableFunction(do_tamper);

    printf("\n[+] Retorno exitoso de TargetVulnerableFunction: Ejecución normal completada.\n");
    if (!do_tamper) {
        printf("[i] Para simular la detección de violación de Shadow Stack, ejecute con: --tamper\n");
    }

    return 0;
}
