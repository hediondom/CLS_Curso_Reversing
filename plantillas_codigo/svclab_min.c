// Archivo: plantillas_codigo/svclab_min.c
// Práctica para Lección 2D.4 (Servicios: SCM, ciclo de vida, cuentas y auditoría)
// Compilar (MSVC) : cl /Zi /O1 /DUNICODE /D_UNICODE svclab_min.c advapi32.lib /Fe:SvcLab.exe
// Compilar (MinGW): gcc -O1 -g -municode svclab_min.c -ladvapi32 -o SvcLab.exe
// Probar en consola antes de registrar: SvcLab.exe --console
// Registrar en VM (cmd elevado):
//   sc.exe create ReversingLabSvc binPath= "C:\ReversingLab\SvcLab.exe" start= demand obj= "NT AUTHORITY\LocalService"
//   sc.exe start ReversingLabSvc
//   sc.exe query ReversingLabSvc
//   sc.exe stop ReversingLabSvc
//   sc.exe delete ReversingLabSvc

#include <windows.h>
#include <stdio.h>

#ifdef _MSC_VER
#pragma comment(lib, "advapi32.lib")
#endif

#define SVC_NAME L"ReversingLabSvc"

static SERVICE_STATUS        g_Status = {0};
static SERVICE_STATUS_HANDLE g_hStatus = NULL;
static HANDLE                g_hStopEvent = NULL;

static void ReportarEstado(DWORD dwCurrentState, DWORD dwWin32ExitCode, DWORD dwWaitHint) {
    static DWORD dwCheckPoint = 1;
    g_Status.dwServiceType      = SERVICE_WIN32_OWN_PROCESS;
    g_Status.dwCurrentState     = dwCurrentState;
    g_Status.dwWin32ExitCode    = dwWin32ExitCode;
    g_Status.dwWaitHint         = dwWaitHint;
    g_Status.dwControlsAccepted = (dwCurrentState == SERVICE_START_PENDING) ? 0 : (SERVICE_ACCEPT_STOP | SERVICE_ACCEPT_SHUTDOWN);
    g_Status.dwCheckPoint       = (dwCurrentState == SERVICE_RUNNING || dwCurrentState == SERVICE_STOPPED) ? 0 : dwCheckPoint++;
    if (g_hStatus) {
        SetServiceStatus(g_hStatus, &g_Status);
    }
}

static DWORD WINAPI SvcCtrlHandlerEx(DWORD dwControl, DWORD dwEventType, LPVOID lpEventData, LPVOID lpContext) {
    (void)dwEventType; (void)lpEventData; (void)lpContext;
    switch (dwControl) {
        case SERVICE_CONTROL_STOP:
        case SERVICE_CONTROL_SHUTDOWN:
            ReportarEstado(SERVICE_STOP_PENDING, NO_ERROR, 2000);
            if (g_hStopEvent) SetEvent(g_hStopEvent);
            return NO_ERROR;
        case SERVICE_CONTROL_INTERROGATE:
            return NO_ERROR;
        default:
            return ERROR_CALL_NOT_IMPLEMENTED;
    }
}

static VOID WINAPI SvcLabMain(DWORD dwArgc, LPWSTR* lpszArgv) {
    (void)dwArgc; (void)lpszArgv;
    g_hStatus = RegisterServiceCtrlHandlerExW(SVC_NAME, SvcCtrlHandlerEx, NULL);
    if (!g_hStatus) return;

    ReportarEstado(SERVICE_START_PENDING, NO_ERROR, 2000);
    g_hStopEvent = CreateEventW(NULL, TRUE, FALSE, NULL);
    if (!g_hStopEvent) {
        ReportarEstado(SERVICE_STOPPED, GetLastError(), 0);
        return;
    }

    ReportarEstado(SERVICE_RUNNING, NO_ERROR, 0);
    // Espera pasiva sin consumir CPU hasta que el SCM envíe SERVICE_CONTROL_STOP
    WaitForSingleObject(g_hStopEvent, INFINITE);

    CloseHandle(g_hStopEvent);
    g_hStopEvent = NULL;
    ReportarEstado(SERVICE_STOPPED, NO_ERROR, 0);
}

int wmain(int argc, wchar_t* argv[]) {
    if (argc > 1 && wcscmp(argv[1], L"--console") == 0) {
        wprintf(L"[SvcLab] Modo diagnóstico de consola OK. Para usar con el SCM, registralo con sc.exe create.
");
        return 0;
    }
    SERVICE_TABLE_ENTRYW DispatchTable[] = {
        { (LPWSTR)SVC_NAME, (LPSERVICE_MAIN_FUNCTIONW)SvcLabMain },
        { NULL, NULL }
    };
    if (!StartServiceCtrlDispatcherW(DispatchTable)) {
        DWORD err = GetLastError();
        if (err == ERROR_FAILED_SERVICE_CONTROLLER_CONNECT) {
            wprintf(L"Error 1063 (ERROR_FAILED_SERVICE_CONTROLLER_CONNECT): este binario es un servicio Win32.
"
                    L"Inicialo con 'sc.exe start ReversingLabSvc' o probalo con 'SvcLab.exe --console'.
");
        }
        return (int)err;
    }
    return 0;
}
