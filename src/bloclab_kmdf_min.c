// Archivo: plantillas_codigo/bloclab_kmdf_min.c
// Plantilla 6 (Tomo II, Lección 6.2): bloclab_kmdf_min.c
// Esqueleto mínimo KMDF para análisis estático en IDA/Ghidra y prueba en VM descartable.
// El SDDL restringe la apertura únicamente a SYSTEM y Administradores.
#include <ntddk.h>
#include <wdf.h>
#include <wdmsec.h>

#define IOCTL_BLOCLAB_QUERY_VERSION     CTL_CODE(0x8000, 0x800, METHOD_BUFFERED, FILE_READ_DATA) // 0x80006000

typedef struct _BLOCLAB_INFO {
    ULONG Size;
    ULONG Version;
    ULONG State;
} BLOCLAB_INFO, *PBLOCLAB_INFO;

EVT_WDF_DRIVER_DEVICE_ADD BlocLabEvtDeviceAdd;
EVT_WDF_IO_QUEUE_IO_DEVICE_CONTROL BlocLabEvtIoDeviceControl;

NTSTATUS DriverEntry(PDRIVER_OBJECT DriverObject, PUNICODE_STRING RegistryPath) {
    WDF_DRIVER_CONFIG config;
    WDF_DRIVER_CONFIG_INIT(&config, BlocLabEvtDeviceAdd); // +0x08 en x64 = EvtDriverDeviceAdd
    return WdfDriverCreate(DriverObject, RegistryPath, WDF_NO_OBJECT_ATTRIBUTES, &config, WDF_NO_HANDLE);
}

NTSTATUS BlocLabEvtDeviceAdd(WDFDRIVER Driver, PWDFDEVICE_INIT DeviceInit) {
    UNREFERENCED_PARAMETER(Driver);
    DECLARE_CONST_UNICODE_STRING(ntDeviceName, L"\Device\BlocLab");
    DECLARE_CONST_UNICODE_STRING(symbolicLink, L"\DosDevices\BlocLab");

    NTSTATUS status = WdfDeviceInitAssignName(DeviceInit, &ntDeviceName);
    if (!NT_SUCCESS(status)) return status;

    // Restringe apertura únicamente a SYSTEM y Administradores:
    status = WdfDeviceInitAssignSDDLString(DeviceInit, &SDDL_DEVOBJ_SYS_ALL_ADM_ALL);
    if (!NT_SUCCESS(status)) return status;

    WDFDEVICE device;
    status = WdfDeviceCreate(&DeviceInit, WDF_NO_OBJECT_ATTRIBUTES, &device);
    if (!NT_SUCCESS(status)) return status;

    status = WdfDeviceCreateSymbolicLink(device, &symbolicLink);
    if (!NT_SUCCESS(status)) return status;

    WDF_IO_QUEUE_CONFIG queueConfig;
    WDF_IO_QUEUE_CONFIG_INIT_DEFAULT_QUEUE(&queueConfig, WdfIoQueueDispatchSequential);
    queueConfig.EvtIoDeviceControl = BlocLabEvtIoDeviceControl; // +0x28 en x64

    return WdfIoQueueCreate(device, &queueConfig, WDF_NO_OBJECT_ATTRIBUTES, WDF_NO_HANDLE);
}

VOID BlocLabEvtIoDeviceControl(WDFQUEUE Queue, WDFREQUEST Request,
                               size_t OutputBufferLength, size_t InputBufferLength,
                               ULONG IoControlCode) {
    UNREFERENCED_PARAMETER(Queue);
    UNREFERENCED_PARAMETER(OutputBufferLength);

    if (IoControlCode != IOCTL_BLOCLAB_QUERY_VERSION) {
        WdfRequestComplete(Request, STATUS_INVALID_DEVICE_REQUEST);
        return;
    }
    if (InputBufferLength != 0) {
        WdfRequestComplete(Request, STATUS_INVALID_PARAMETER);
        return;
    }

    PBLOCLAB_INFO outBuf = NULL;
    // Valida automáticamente que OutputBufferLength >= sizeof(BLOCLAB_INFO) (12 bytes):
    NTSTATUS status = WdfRequestRetrieveOutputBuffer(Request, sizeof(BLOCLAB_INFO), (PVOID*)&outBuf, NULL);
    if (!NT_SUCCESS(status)) {
        WdfRequestComplete(Request, status); // Devuelve STATUS_BUFFER_TOO_SMALL
        return;
    }

    RtlZeroMemory(outBuf, sizeof(BLOCLAB_INFO));
    outBuf->Size    = sizeof(BLOCLAB_INFO);
    outBuf->Version = 1;
    outBuf->State   = 1; // READY
    WdfRequestCompleteWithInformation(Request, STATUS_SUCCESS, sizeof(BLOCLAB_INFO));
}
