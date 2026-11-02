// Archivo: plantillas_codigo/pipe_server_min.c
// Compilar (MSVC) : cl /Zi /O1 pipe_server_min.c /Fe:pipe_server_min.exe
// Compilar (MinGW): gcc -O1 -g pipe_server_min.c -o pipe_server_min.exe
// Probar en Python: open(r'\\.\pipe\BlocLabPipe', 'r+b', buffering=0)
#include <windows.h>
#include <stdio.h>
#include <string.h>

int main(void) {
    const wchar_t* nombre = L"\\\\.\\pipe\\BlocLabPipe";
    HANDLE hPipe = CreateNamedPipeW(
        nombre,
        PIPE_ACCESS_DUPLEX | FILE_FLAG_FIRST_PIPE_INSTANCE,
        PIPE_TYPE_MESSAGE | PIPE_READMODE_MESSAGE | PIPE_WAIT | PIPE_REJECT_REMOTE_CLIENTS,
        1, 256, 256, 0, NULL);
    if (hPipe == INVALID_HANDLE_VALUE) {
        printf("CreateNamedPipeW fallo (GLE=%lu)\n", GetLastError());
        return 1;
    }
    puts("[ESPERA_SALUDO] Escuchando en \\.\pipe\BlocLabPipe ...");
    if (ConnectNamedPipe(hPipe, NULL) || GetLastError() == ERROR_PIPE_CONNECTED) {
        char buf[128] = {0};
        DWORD leidos = 0, escritos = 0;
        if (ReadFile(hPipe, buf, sizeof(buf) - 1, &leidos, NULL) && leidos >= 4 && memcmp(buf, "CLSF", 4) == 0) {
            puts("[LISTO] Saludo CLSF valido recibido; enviando respuesta fija.");
            const char resp[] = "CLSF_ACK_V1_READY";
            WriteFile(hPipe, resp, (DWORD)strlen(resp), &escritos, NULL);
        } else {
            const char err[] = "CLSF_ERR_BAD_HELLO";
            WriteFile(hPipe, err, (DWORD)strlen(err), &escritos, NULL);
        }
        FlushFileBuffers(hPipe);
        DisconnectNamedPipe(hPipe);
    }
    CloseHandle(hPipe);
    return 0;
}
