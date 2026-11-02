/* rpc_com_server_lab.c — Servidor RPC local didáctico sobre ncalrpc con callback de seguridad (Lección 2D.10)
 * Compilación:
 *   midl /x64 rpc_com_server_lab.idl
 *   cl /W4 /Ox rpc_com_server_lab.c rpc_com_server_lab_s.c /link rpcrt4.lib
 */

#include <windows.h>
#include <stdio.h>
#include <rpc.h>
#include "rpc_com_server_lab.h"

#pragma comment(lib, "rpcrt4.lib")

// Implementación del Procedimiento 0 (índice 0 en DispatchTable)
unsigned long RpcObtenerVersion(void) {
    printf("[+] Servidor RPC: Llamada recibida en RpcObtenerVersion()\n");
    return 0x05040001; // Versión 5.4.1
}

// Implementación del Procedimiento 1 (índice 1 en DispatchTable)
unsigned long RpcValidarToken(const char* pszToken, unsigned long* pdwStatus) {
    printf("[+] Servidor RPC: Llamada recibida en RpcValidarToken()\n");
    printf("    Buffer recibido (decodificado vía NDR ProcFormatString): '%s'\n", pszToken ? pszToken : "(null)");
    
    if (pszToken && strcmp(pszToken, "SECRETO_LAB") == 0) {
        *pdwStatus = 1;
        return 0; // Exito
    }
    *pdwStatus = 0;
    return 0x5; // Access Denied
}

// Callback de seguridad RPC: valida cliente antes de despachar
RPC_STATUS CALLBACK RpcSecurityCallback(RPC_IF_HANDLE Interface, void* Context) {
    UNREFERENCED_PARAMETER(Interface);
    UNREFERENCED_PARAMETER(Context);
    
    // En un servidor seguro se evalúa el token del llamador (RpcImpersonateClient)
    printf("[*] RpcSecurityCallback ejecutado: permitiendo conexión local verificada.\n");
    return RPC_S_OK;
}

// Memoria para el stub MIDL
void __RPC_FAR* __RPC_USER midl_user_allocate(size_t len) {
    return malloc(len);
}

void __RPC_USER midl_user_free(void __RPC_FAR* ptr) {
    free(ptr);
}

int main(void) {
    RPC_STATUS status;
    RPC_WSTR pszProtocolSequence = (RPC_WSTR)L"ncalrpc";
    RPC_WSTR pszEndpoint = (RPC_WSTR)L"LabRpcDefensivoEndpoint";

    printf("=========================================================\n");
    printf("[*] Servidor RPC Didáctico para Auditoría de DispatchTable\n");
    printf("=========================================================\n");

    // 1. Usar protocolo local LPC (ncalrpc)
    status = RpcServerUseProtseqEpW(pszProtocolSequence, RPC_C_PROTSEQ_MAX_REQS_DEFAULT, pszEndpoint, NULL);
    if (status) {
        printf("[-] Error en RpcServerUseProtseqEp (0x%X)\n", status);
        return 1;
    }

    // 2. Registrar la interfaz generada por MIDL con callback de seguridad
    // Esta función inicializa RPC_SERVER_INTERFACE:
    // +0x04: UUID de la interfaz
    // +0x50: InterpreterInfo -> MIDL_SERVER_INFO (+0x08 DispatchTable, +0x10 ProcFormatString)
    status = RpcServerRegisterIf2(
        LabRpcDefensivo_v1_0_s_ifspec,
        NULL,
        NULL,
        RPC_IF_ALLOW_LOCAL_ONLY,
        RPC_C_LISTEN_MAX_CALLS_DEFAULT,
        (unsigned)-1,
        RpcSecurityCallback
    );

    if (status) {
        printf("[-] Error en RpcServerRegisterIf2 (0x%X)\n", status);
        return 1;
    }

    printf("[+] Servidor RPC escuchando en: ncalrpc:[%ws]\n", pszEndpoint);
    printf("[*] Para auditar en WinDbg o IDA:\n");
    printf("    1) Busca la estructura LabRpcDefensivo_v1_0_s_ifspec en .data\n");
    printf("    2) Inspecciona +0x50 (InterpreterInfo) -> DispatchTable (+0x08)\n");
    printf("    3) Observa ProcFormatString (+0x10) para decodificar los tipos NDR\n");
    printf("[*] Presiona Ctrl+C para detener el servidor.\n");

    status = RpcServerListen(1, RPC_C_LISTEN_MAX_CALLS_DEFAULT, FALSE);
    return 0;
}
