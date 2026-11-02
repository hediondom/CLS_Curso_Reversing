/* minifilter_obcallback_min.c — Driver de laboratorio con Minifiltro de FS y Callbacks de Objetos
 * Muestra el registro defensivo de FltRegisterFilter y ObRegisterCallbacks sobre PsProcessType (Lección 6.7)
 * Compilación: Visual Studio x64 WDK Environment
 */

#include <fltKernel.h>
#include <dontuse.h>
#include <suppress.h>

#define DRIVER_PREFIX "MiniFltOb: "

// Prototipos de Minifiltro
FLT_PREOP_CALLBACK_STATUS MiniFltPreCreate(
    _Inout_ PFLT_CALLBACK_DATA Data,
    _In_ PCFLT_RELATED_OBJECTS FltObjects,
    _Flt_CompletionContext_Outptr_ PVOID *CompletionContext
);

FLT_POSTOP_CALLBACK_STATUS MiniFltPostCreate(
    _Inout_ PFLT_CALLBACK_DATA Data,
    _In_ PCFLT_RELATED_OBJECTS FltObjects,
    _In_opt_ PVOID CompletionContext,
    _In_ FLT_POST_OPERATION_FLAGS Flags
);

NTSTATUS MiniFltUnload(_In_ FLT_FILTER_UNLOAD_FLAGS Flags);

// Tabla de operaciones interceptadas por el minifiltro
CONST FLT_OPERATION_REGISTRATION Callbacks[] = {
    { IRP_MJ_CREATE,
      0,
      MiniFltPreCreate,
      MiniFltPostCreate },
    { IRP_MJ_OPERATION_END }
};

// Registro del Minifiltro
CONST FLT_REGISTRATION FilterRegistration = {
    sizeof(FLT_REGISTRATION),         // Size
    FLT_REGISTRATION_VERSION,         // Version
    0,                                // Flags
    NULL,                             // ContextRegistration
    Callbacks,                        // OperationRegistration
    MiniFltUnload,                    // FilterUnload
    NULL,                             // InstanceSetup
    NULL,                             // InstanceQueryTeardown
    NULL,                             // InstanceTeardownStart
    NULL,                             // InstanceTeardownComplete
    NULL, NULL, NULL                  // GenerateFileName / Normalize / Ktm
};

PFLT_FILTER gFilterHandle = NULL;
PVOID gObRegistrationHandle = NULL;

// Callback de objetos: ObRegisterCallbacks sobre PsProcessType
OB_PREOP_CALLBACK_STATUS ObPreProcessCallback(
    PVOID RegistrationContext,
    POB_PRE_OPERATION_INFORMATION PreInfo
) {
    UNREFERENCED_PARAMETER(RegistrationContext);
    
    // Inspeccionar proceso objetivo
    PEPROCESS TargetProcess = (PEPROCESS)PreInfo->Object;
    UNREFERENCED_PARAMETER(TargetProcess);

    // En un sensor defensivo: auditar o despojar permisos peligrosos (PROCESS_VM_WRITE, PROCESS_VM_READ)
    if (PreInfo->Operation == OB_OPERATION_HANDLE_CREATE) {
        // PreInfo->Parameters->CreateHandleInformation.DesiredAccess &= ~PROCESS_VM_WRITE;
    }
    return OB_PREOP_SUCCESS;
}

NTSTATUS DriverEntry(_In_ PDRIVER_OBJECT DriverObject, _In_ PUNICODE_STRING RegistryPath) {
    UNREFERENCED_PARAMETER(RegistryPath);
    NTSTATUS status;

    KdPrint((DRIVER_PREFIX "Iniciando DriverEntry...\n"));

    // 1. Registro del Minifiltro de Sistema de Archivos
    status = FltRegisterFilter(DriverObject, &FilterRegistration, &gFilterHandle);
    if (!NT_SUCCESS(status)) {
        KdPrint((DRIVER_PREFIX "Error en FltRegisterFilter (0x%08X)\n", status));
        return status;
    }

    status = FltStartFiltering(gFilterHandle);
    if (!NT_SUCCESS(status)) {
        FltUnregisterFilter(gFilterHandle);
        return status;
    }
    KdPrint((DRIVER_PREFIX "Minifiltro registrado exitosamente.\n"));

    // 2. Registro de Callbacks de Objetos de Proceso (ObRegisterCallbacks)
    OB_CALLBACK_REGISTRATION obRegistration = { 0 };
    OB_OPERATION_REGISTRATION opRegistration = { 0 };

    opRegistration.ObjectType = PsProcessType;
    opRegistration.Operations = OB_OPERATION_HANDLE_CREATE | OB_OPERATION_HANDLE_DUPLICATE;
    opRegistration.PreOperation = ObPreProcessCallback;
    opRegistration.PostOperation = NULL;

    UNICODE_STRING altitude;
    RtlInitUnicodeString(&altitude, L"321000");

    obRegistration.Version = OB_FLT_REGISTRATION_VERSION;
    obRegistration.OperationRegistrationCount = 1;
    obRegistration.Altitude = altitude;
    obRegistration.RegistrationContext = NULL;
    obRegistration.OperationRegistration = &opRegistration;

    status = ObRegisterCallbacks(&obRegistration, &gObRegistrationHandle);
    if (!NT_SUCCESS(status)) {
        KdPrint((DRIVER_PREFIX "Aviso: ObRegisterCallbacks devolvio 0x%08X (requiere /INTEGRITYCHECK)\n", status));
        // No abortamos DriverEntry en entorno didactico si falla firma
    } else {
        KdPrint((DRIVER_PREFIX "ObRegisterCallbacks instalado en altitude 321000.\n"));
    }

    return STATUS_SUCCESS;
}

NTSTATUS MiniFltUnload(_In_ FLT_FILTER_UNLOAD_FLAGS Flags) {
    UNREFERENCED_PARAMETER(Flags);
    KdPrint((DRIVER_PREFIX "Descargando driver...\n"));

    if (gObRegistrationHandle) {
        ObUnRegisterCallbacks(gObRegistrationHandle);
        gObRegistrationHandle = NULL;
    }

    if (gFilterHandle) {
        FltUnregisterFilter(gFilterHandle);
        gFilterHandle = NULL;
    }

    return STATUS_SUCCESS;
}

FLT_PREOP_CALLBACK_STATUS MiniFltPreCreate(
    _Inout_ PFLT_CALLBACK_DATA Data,
    _In_ PCFLT_RELATED_OBJECTS FltObjects,
    _Flt_CompletionContext_Outptr_ PVOID *CompletionContext
) {
    UNREFERENCED_PARAMETER(Data);
    UNREFERENCED_PARAMETER(FltObjects);
    UNREFERENCED_PARAMETER(CompletionContext);

    // Inspección de apertura de archivos (IRP_MJ_CREATE)
    return FLT_PREOP_SUCCESS_WITH_CALLBACK;
}

FLT_POSTOP_CALLBACK_STATUS MiniFltPostCreate(
    _Inout_ PFLT_CALLBACK_DATA Data,
    _In_ PCFLT_RELATED_OBJECTS FltObjects,
    _In_opt_ PVOID CompletionContext,
    _In_ FLT_POST_OPERATION_FLAGS Flags
) {
    UNREFERENCED_PARAMETER(Data);
    UNREFERENCED_PARAMETER(FltObjects);
    UNREFERENCED_PARAMETER(CompletionContext);
    UNREFERENCED_PARAMETER(Flags);

    return FLT_POSTOP_FINISHED_PROCESSING;
}
