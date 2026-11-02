/* evasion_peb_syscall_lab.c — Laboratorio defensivo de resolución por PEB, Indirect Syscalls y VEH (Lecciones 2.14, 2.15)
 * Compilación x64:
 *   cl /W4 /Ox evasion_peb_syscall_lab.c /link /subsystem:console
 */

#include <windows.h>
#include <winternl.h>
#include <stdio.h>
#include <stdint.h>

// Definición de hash ROR13 para resolución sin cadenas ASCII en .rdata
static uint32_t HashRor13A(const char* str) {
    uint32_t hash = 0;
    while (*str) {
        hash = (hash >> 13) | (hash << (32 - 13));
        hash += (uint32_t)(*str++);
    }
    return hash;
}

// 1. Resolución de módulos y funciones vía recorrido de gs:[0x60] (PEB->Ldr)
static HMODULE ObtenerModuloPorHash(uint32_t hashModuloEsperado) {
    // Leer PEB en x64 mediante segmento GS
    PPEB pPeb = (PPEB)__readgsqword(0x60);
    PPEB_LDR_DATA pLdr = pPeb->Ldr;
    PLIST_ENTRY pHead = &pLdr->InMemoryOrderModuleList;
    PLIST_ENTRY pCurr = pHead->Flink;

    while (pCurr != pHead) {
        PLDR_DATA_TABLE_ENTRY pEntry = CONTAINING_RECORD(pCurr, LDR_DATA_TABLE_ENTRY, InMemoryOrderLinks);
        if (pEntry->BaseDllName.Buffer) {
            // Calcular hash en mayúsculas del nombre
            uint32_t h = 0;
            for (USHORT i = 0; i < pEntry->BaseDllName.Length / sizeof(WCHAR); i++) {
                WCHAR wc = pEntry->BaseDllName.Buffer[i];
                if (wc >= L'a' && wc <= L'z') wc -= (L'a' - L'A');
                h = (h >> 13) | (h << (32 - 13));
                h += (uint32_t)wc;
            }
            if (h == hashModuloEsperado) {
                return (HMODULE)pEntry->DllBase;
            }
        }
        pCurr = pCurr->Flink;
    }
    return NULL;
}

static PVOID ObtenerExportPorHash(HMODULE hMod, uint32_t hashExportEsperado) {
    PIMAGE_DOS_HEADER dos = (PIMAGE_DOS_HEADER)hMod;
    PIMAGE_NT_HEADERS nt = (PIMAGE_NT_HEADERS)((PBYTE)hMod + dos->e_lfanew);
    DWORD rvaExp = nt->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_EXPORT].VirtualAddress;
    if (!rvaExp) return NULL;

    PIMAGE_EXPORT_DIRECTORY exp = (PIMAGE_EXPORT_DIRECTORY)((PBYTE)hMod + rvaExp);
    PDWORD names = (PDWORD)((PBYTE)hMod + exp->AddressOfNames);
    PWORD ordinals = (PWORD)((PBYTE)hMod + exp->AddressOfNameOrdinals);
    PDWORD funcs = (PDWORD)((PBYTE)hMod + exp->AddressOfFunctions);

    for (DWORD i = 0; i < exp->NumberOfNames; i++) {
        const char* name = (const char*)((PBYTE)hMod + names[i]);
        if (HashRor13A(name) == hashExportEsperado) {
            WORD ord = ordinals[i];
            return (PVOID)((PBYTE)hMod + funcs[ord]);
        }
    }
    return NULL;
}

// 2. Manejador VEH para detectar anomalías de depuración por registros de hardware (Dr0..Dr3)
static LONG WINAPI ManejadorVehDefensivo(PEXCEPTION_POINTERS pExceptionInfo) {
    PCONTEXT ctx = pExceptionInfo->ContextRecord;
    
    // Inspección de registros de depuración del procesador
    if (ctx->Dr0 || ctx->Dr1 || ctx->Dr2 || ctx->Dr3) {
        printf("[!] VEH Alerta: Hardware Breakpoint detectado en Dr0..Dr3!\n");
        printf("    Dr0=%p Dr1=%p Dr2=%p Dr3=%p | Dr7=%p\n",
               (void*)ctx->Dr0, (void*)ctx->Dr1, (void*)ctx->Dr2, (void*)ctx->Dr3, (void*)ctx->Dr7);
        // Limpieza de registros para continuar ejecución limpia
        ctx->Dr0 = ctx->Dr1 = ctx->Dr2 = ctx->Dr3 = ctx->Dr7 = 0;
        return EXCEPTION_CONTINUE_EXECUTION;
    }
    return EXCEPTION_CONTINUE_SEARCH;
}

int main(void) {
    printf("=================================================================\n");
    printf("[*] Laboratorio Defensivo de Evasión, PEB y Call Stack Walking\n");
    printf("=================================================================\n");

    // 1. Instalar VEH para inspeccionar registros de depuración
    PVOID hVeh = AddVectoredExceptionHandler(1, ManejadorVehDefensivo);
    printf("[+] Vectored Exception Handler (VEH) registrado en: %p\n", hVeh);

    // 2. Hash ROR13 de "NTDLL.DLL" y "NTALLOCATEVIRTUALMEMORY"
    // HASH("NTDLL.DLL") en WCHAR mayúscula
    const uint32_t HASH_NTDLL = 0x6E2BCA17; 
    // HASH("NtAllocateVirtualMemory")
    const uint32_t HASH_NTALLOC = 0xE0762FEB;

    HMODULE hNtdll = GetModuleHandleW(L"ntdll.dll");
    printf("[+] ntdll.dll localizado en memoria en: %p\n", (void*)hNtdll);

    PVOID pfnNtAlloc = ObtenerExportPorHash(hNtdll, HASH_NTALLOC);
    printf("[+] Export NtAllocateVirtualMemory resuelto por ROR13: %p\n", pfnNtAlloc);

    if (pfnNtAlloc) {
        // Analizar el prólogo del stub en ntdll.dll
        PBYTE pBytes = (PBYTE)pfnNtAlloc;
        printf("[*] Prólogo del stub en ntdll: %02X %02X %02X %02X (esperado: 4C 8B D1 B8 = mov r10, rcx; mov eax, SSN)\n",
               pBytes[0], pBytes[1], pBytes[2], pBytes[3]);
        
        DWORD ssn = *(PDWORD)(pBytes + 4);
        printf("[+] System Service Number (SSN) extraído dinámicamente: 0x%04X\n", ssn);

        // Buscar el gadget syscall; ret (0F 05 C3) legítimo dentro de ntdll
        PBYTE pSyscallRet = NULL;
        for (DWORD i = 0; i < 32; i++) {
            if (pBytes[i] == 0x0F && pBytes[i+1] == 0x05 && pBytes[i+2] == 0xC3) {
                pSyscallRet = pBytes + i;
                break;
            }
        }
        if (pSyscallRet) {
            printf("[+] Gadget legítimo (syscall; ret) en ntdll: %p (Ideal para Indirect Syscall)\n", (void*)pSyscallRet);
            printf("[*] Ventaja defensiva de auditoría: Al validar UNWIND_INFO (.pdata), el RIP de la llamada\n");
            printf("    apunta a ntdll.dll en lugar de memoria privada no respaldada por imagen.\n");
        }
    }

    if (hVeh) RemoveVectoredExceptionHandler(hVeh);
    printf("[+] Fin del laboratorio de evasión y verificación de PEB.\n");
    return 0;
}
