# ==============================================================================
# Plantilla 19 · Auditoría Forense de Procesos AppContainer y LPAC en PowerShell
# Obra: Reversing en Windows — Tomo III (Módulo 2)
#
# Objetivo:
#   Identificar procesos en ejecución que residan en contenedores de aplicación,
#   determinar si operan en modo LPAC (Less Privileged AppContainer) decodificando
#   sus Capability SIDs (S-1-15-3-*) y analizando su superficie de aislamiento.
#
# Requisitos:
#   Ejecutar en PowerShell (Consola x64 con privilegios estándar o de Administrador).
# ==============================================================================

Set-StrictMode -Version Latest
$ErrorActionPreference = "Continue"

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "[*] Plantilla 19 · Auditoría de Contenedores AppContainer y LPAC en Windows" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan

# Definición de P/Invoke para interactuar directamente con la API de Seguridad de Windows
$TypeDef = @"
using System;
using System.Runtime.InteropServices;
using System.Security.Principal;

public class NativeTokenAudit {
    [DllImport("advapi32.dll", SetLastError = true)]
    public static extern bool OpenProcessToken(IntPtr ProcessHandle, uint DesiredAccess, out IntPtr TokenHandle);

    [DllImport("advapi32.dll", SetLastError = true)]
    public static extern bool GetTokenInformation(IntPtr TokenHandle, int TokenInformationClass, IntPtr TokenInformation, uint TokenInformationLength, out uint ReturnLength);

    [DllImport("advapi32.dll", SetLastError = true, CharSet = CharSet.Auto)]
    public static extern bool ConvertSidToStringSid(IntPtr pSid, out IntPtr ptrSidString);

    [DllImport("kernel32.dll", SetLastError = true)]
    public static extern bool CloseHandle(IntPtr hObject);

    [DllImport("kernel32.dll")]
    public static extern IntPtr LocalFree(IntPtr hMem);

    public const uint TOKEN_QUERY = 0x0008;

    // TOKEN_INFORMATION_CLASS
    public const int TokenIsAppContainer = 29;
    public const int TokenCapabilities    = 30;
    public const int TokenAppContainerSid = 31;
    public const int TokenGroups          = 2;

    [StructLayout(LayoutKind.Sequential)]
    public struct SID_AND_ATTRIBUTES {
        public IntPtr Sid;
        public uint Attributes;
    }

    [StructLayout(LayoutKind.Sequential)]
    public struct TOKEN_GROUPS {
        public uint GroupCount;
        // seguido de un arreglo de SID_AND_ATTRIBUTES
    }
}
"@

Add-Type -TypeDefinition $TypeDef -ErrorAction SilentlyContinue

# Tabla de nombres conocidos de Capability SIDs
$KnownCapabilities = @{
    "S-1-15-3-1" = "internetClient (Conexión saliente a Internet)"
    "S-1-15-3-2" = "internetClientServer (Servidor/Saliente Internet)"
    "S-1-15-3-3" = "privateNetworkClientServer (Intranet corporativa)"
    "S-1-15-3-4" = "picturesLibrary (Acceso a Fotos/Imágenes)"
    "S-1-15-3-5" = "videosLibrary (Acceso a Videos)"
    "S-1-15-3-6" = "musicLibrary (Acceso a Música)"
    "S-1-15-3-7" = "documentsLibrary (Acceso a Documentos)"
    "S-1-15-3-8" = "enterpriseAuthentication (Credenciales de dominio)"
}

$LPAC_SID = "S-1-15-2-2" # ALL RESTRICTED APPLICATION PACKAGES
$APPCONTAINER_GENERIC_SID = "S-1-15-2-1" # ALL APPLICATION PACKAGES

function Convert-IntPtrToSidString([IntPtr]$pSid) {
    if ($pSid -eq [IntPtr]::Zero) { return $null }
    $pStr = [IntPtr]::Zero
    if ([NativeTokenAudit]::ConvertSidToStringSid($pSid, [ref]$pStr)) {
        $sidStr = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($pStr)
        [NativeTokenAudit]::LocalFree($pStr) | Out-Null
        return $sidStr
    }
    return $null
}

Write-Host "[*] Escaneando procesos activos en el sistema..." -ForegroundColor Yellow

$Processes = Get-Process
$FoundCount = 0

foreach ($p in $Processes) {
    $hToken = [IntPtr]::Zero
    $isOpen = $false
    try {
        $isOpen = [NativeTokenAudit]::OpenProcessToken($p.Handle, [NativeTokenAudit]::TOKEN_QUERY, [ref]$hToken)
    } catch {
        continue
    }

    if (-not $isOpen -or $hToken -eq [IntPtr]::Zero) { continue }

    # 1. Verificar si el token tiene TokenIsAppContainer activo (clase 29)
    $retLen = 0
    $pIsAppContainer = [System.Runtime.InteropServices.Marshal]::AllocHGlobal(4)
    $isAppContainer = $false

    if ([NativeTokenAudit]::GetTokenInformation($hToken, [NativeTokenAudit]::TokenIsAppContainer, $pIsAppContainer, 4, [ref]$retLen)) {
        $val = [System.Runtime.InteropServices.Marshal]::ReadInt32($pIsAppContainer)
        if ($val -ne 0) { $isAppContainer = $true }
    }
    [System.Runtime.InteropServices.Marshal]::FreeHGlobal($pIsAppContainer)

    if (-not $isAppContainer) {
        [NativeTokenAudit]::CloseHandle($hToken) | Out-Null
        continue
    }

    $FoundCount++
    Write-Host "`n--------------------------------------------------------------------------------" -ForegroundColor Green
    Write-Host "[+] Proceso en Contenedor Detectado: PID=$($p.Id) | Nombre=$($p.ProcessName)" -ForegroundColor Green

    # 2. Obtener el Package SID (clase 31)
    $retLen = 0
    [NativeTokenAudit]::GetTokenInformation($hToken, [NativeTokenAudit]::TokenAppContainerSid, [IntPtr]::Zero, 0, [ref]$retLen) | Out-Null
    if ($retLen -gt 0) {
        $buf = [System.Runtime.InteropServices.Marshal]::AllocHGlobal([int]$retLen)
        if ([NativeTokenAudit]::GetTokenInformation($hToken, [NativeTokenAudit]::TokenAppContainerSid, $buf, $retLen, [ref]$retLen)) {
            $pSid = [System.Runtime.InteropServices.Marshal]::ReadIntPtr($buf)
            $pkgSidStr = Convert-IntPtrToSidString $pSid
            Write-Host "    Package SID : $pkgSidStr" -ForegroundColor White
        }
        [System.Runtime.InteropServices.Marshal]::FreeHGlobal($buf)
    }

    # 3. Evaluar grupos para determinar si es LPAC (presencia de S-1-15-2-2)
    $retLen = 0
    $isLPAC = $false
    [NativeTokenAudit]::GetTokenInformation($hToken, [NativeTokenAudit]::TokenGroups, [IntPtr]::Zero, 0, [ref]$retLen) | Out-Null
    if ($retLen -gt 0) {
        $buf = [System.Runtime.InteropServices.Marshal]::AllocHGlobal([int]$retLen)
        if ([NativeTokenAudit]::GetTokenInformation($hToken, [NativeTokenAudit]::TokenGroups, $buf, $retLen, [ref]$retLen)) {
            $groupCount = [System.Runtime.InteropServices.Marshal]::ReadInt32($buf)
            $offset = [IntPtr]::Size # saltar groupCount
            for ($i = 0; $i -lt $groupCount; $i++) {
                $sidPtr = [System.Runtime.InteropServices.Marshal]::ReadIntPtr([IntPtr]($buf.ToInt64() + $offset))
                $sidStr = Convert-IntPtrToSidString $sidPtr
                if ($sidStr -eq $LPAC_SID) {
                    $isLPAC = $true
                }
                $offset += ([IntPtr]::Size * 2) # tamaño de SID_AND_ATTRIBUTES en x64 = 16 bytes
            }
        }
        [System.Runtime.InteropServices.Marshal]::FreeHGlobal($buf)
    }

    if ($isLPAC) {
        Write-Host "    Clasificación: LPAC (Less Privileged AppContainer) [S-1-15-2-2 ACTIVO]" -ForegroundColor Magenta
    } else {
        Write-Host "    Clasificación: AppContainer Estándar [S-1-15-2-1 ACTIVO]" -ForegroundColor Cyan
    }

    # 4. Enumerar Capability SIDs (clase 30)
    $retLen = 0
    [NativeTokenAudit]::GetTokenInformation($hToken, [NativeTokenAudit]::TokenCapabilities, [IntPtr]::Zero, 0, [ref]$retLen) | Out-Null
    if ($retLen -gt 0) {
        $buf = [System.Runtime.InteropServices.Marshal]::AllocHGlobal([int]$retLen)
        if ([NativeTokenAudit]::GetTokenInformation($hToken, [NativeTokenAudit]::TokenCapabilities, $buf, $retLen, [ref]$retLen)) {
            $capCount = [System.Runtime.InteropServices.Marshal]::ReadInt32($buf)
            Write-Host "    Capacidades Asignadas ($capCount SIDs detectados):" -ForegroundColor Yellow
            $offset = [IntPtr]::Size
            for ($i = 0; $i -lt $capCount; $i++) {
                $sidPtr = [System.Runtime.InteropServices.Marshal]::ReadIntPtr([IntPtr]($buf.ToInt64() + $offset))
                $sidStr = Convert-IntPtrToSidString $sidPtr
                if ($KnownCapabilities.ContainsKey($sidStr)) {
                    Write-Host "      [-] $sidStr : $($KnownCapabilities[$sidStr])" -ForegroundColor Gray
                } else {
                    Write-Host "      [-] $sidStr : (Capacidad personalizada de aplicación)" -ForegroundColor DarkGray
                }
                $offset += ([IntPtr]::Size * 2)
            }
        }
        [System.Runtime.InteropServices.Marshal]::FreeHGlobal($buf)
    }

    [NativeTokenAudit]::CloseHandle($hToken) | Out-Null
}

Write-Host "`n================================================================================" -ForegroundColor Cyan
Write-Host "[+] Auditoría concluida. Total de procesos en sandbox auditados: $FoundCount" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
