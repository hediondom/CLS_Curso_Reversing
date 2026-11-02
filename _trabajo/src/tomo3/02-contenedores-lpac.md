# Módulo 2 · Contenedores, Aislamiento Moderno (LPAC, MSIX) y la Frontera WSL2
*(Presupuesto editorial: 20 páginas — Prerrequisito: Tomo I, Lección 2.35, págs. 259–260 y Tomo II, Anexo Hyper-V, págs. 158–159)*

---

## 2.1 Anatomía de Contenedores de Aplicaciones: AppContainer frente a LPAC

En la Lección 2.35 de Tomo I (págs. 259–260) se introdujo el concepto de proceso en sandbox bajo el modelo UWP (Universal Windows Platform) y el flag `TokenIsAppContainer` en el objeto de token primario. Sin embargo, para auditar la seguridad de aplicaciones modernas empaquetadas (MSIX) y software altamente restringido (como los procesos de renderizado de Microsoft Edge, visores de documentos de Office y plugins de terceros), el reverser debe dominar la distinción operativa entre un **AppContainer estándar** y un **Less Privileged AppContainer (LPAC)**.

### El Modelo de Seguridad de Paquetes MSIX
Una aplicación moderna empaquetada no se instala copiando archivos a granel en `Program Files`; reside en directorios de solo lectura protegidos (`C:\Program Files\WindowsApps\...`) y su ejecución está confinada por un perfil de seguridad derivado de su manifiesto (`AppxManifest.xml`):

```
                       ARQUITECTURA DE TOKENS EN CONTENEDORES MSIX
                       
  [ Token Primario del Usuario ] (SID: S-1-5-21-...)
              │
              ├──> [ Atributo TokenIsAppContainer = 1 ]
              │
              ├──> [ Package SID ] (S-1-15-2-X-Y-Z...) ───────> Identifica a la aplicación concreta
              │
              ├──> [ Capability SIDs ] (S-1-15-3-X-Y-Z...) ───> Permisos explícitos (Cámara, Red...)
              │
              └──> [ Tipo de Sandbox ]:
                     ├── Estándar : Miembro implícito de ALL APPLICATION PACKAGES (S-1-15-2-1)
                     └── LPAC     : Miembro restringido a ALL RESTRICTED APPLICATION PACKAGES (S-1-15-2-2)
```

### Derivación Criptográfica de SIDs de Paquete y Capacidades
A diferencia de los SIDs convencionales de Windows (donde las subautoridades se generan aleatoriamente en el SAM local o Active Directory), **los SIDs de AppContainer se derivan determinísticamente mediante hashing criptográfico**:

1. **Package SID (`S-1-15-2-*`):**
   * Se calcula aplicando `SHA-256` sobre el *Package Family Name* (ej. `Microsoft.Windows.Search_cw5n1h2txyewy`).
   * Los primeros 128 bits del hash SHA-256 se dividen en 4 bloques de 32 bits (little-endian), los cuales componen las 4 subautoridades del SID:
     $$S\text{-}1\text{-}15\text{-}2\text{-}A\text{-}B\text{-}C\text{-}D$$
   * Esto garantiza que cualquier proceso que se ejecute bajo el mismo paquete comparta exactamente el mismo Package SID en cualquier instalación de Windows 11 en el mundo.

2. **Capability SID (`S-1-15-3-*`):**
   * Se deriva de forma análoga mediante `SHA-256` sobre el nombre canónico de la capacidad declarada en el manifiesto (o sobre un identificador de GUID para capacidades personalizadas):
     $$S\text{-}1\text{-}15\text{-}3\text{-}1024\text{-}A\text{-}B\text{-}C\text{-}D$$

---

### La Diferencia Fundamental: `ALL APPLICATION PACKAGES` vs. `ALL RESTRICTED APPLICATION PACKAGES`

La barrera de contención en Windows se basa en el descriptor de seguridad (DACL) de los objetos del kernel (archivos, claves de Registro, named pipes, mutexes, secciones de memoria compartida):

1. **AppContainer Convencional:**
   * Cuando el kernel crea el token de un AppContainer estándar, inyecta automáticamente el SID bien conocido **`ALL APPLICATION PACKAGES` (`S-1-15-2-1`)**.
   * La inmensa mayoría de las DLLs del sistema en `C:\Windows\System32`, las fuentes tipográficas y los recursos comunes de Windows tienen DACLs que conceden `GENERIC_READ` o `GENERIC_EXECUTE` a `S-1-15-2-1`.
   * Por tanto, un AppContainer estándar puede cargar bibliotecas del sistema, leer claves públicas del Registro en `HKLM\Software` y comunicarse con endpoints IPC locales que acepten conexiones de aplicaciones UWP genéricas.

2. **Less Privileged AppContainer (LPAC):**
   * Introducido para mitigar vulnerabilidades donde un atacante comprometía un renderizador de navegador y utilizaba APIs locales del sistema operativo para escalar privilegios.
   * En un proceso LPAC, el kernel **remueve** el SID `ALL APPLICATION PACKAGES` (`S-1-15-2-1`) y lo sustituye por el SID restringido **`ALL RESTRICTED APPLICATION PACKAGES` (`S-1-15-2-2`)**.
   * **Consecuencia demoledora:** Un proceso LPAC **no puede leer prácticamente nada del sistema de archivos ni del Registro**, a menos que el objeto específico haya sido dotado explícitamente de una ACE que incluya a `S-1-15-2-2` o a su *Package SID* específico.
   * Incluso para cargar `ntdll.dll` o `kernel32.dll`, Windows 10/11 debió modificar los descriptores de seguridad predeterminados del sistema operativo para permitir que las bibliotecas esenciales otorguen lectura a `ALL RESTRICTED APPLICATION PACKAGES`.

### Los SIDs de Capacidad (*Capability SIDs*: `S-1-15-3-*`)
Cualquier recurso sensible que exceda el aislamiento absoluto requiere la asignación de un SID de capacidad en el manifiesto. Estos SIDs pertenecen a la rama `S-1-15-3`:

| Capacidad en Manifiesto | Nombre Canónico de Windows | Representación de SID / Rango | Propósito Operativo |
|---|---|---|---|
| `internetClient` | Acceso a redes públicas / Internet | `S-1-15-3-1` | Tráfico saliente WinSock / WinHTTP hacia Internet. |
| `internetClientServer` | Servidor en redes públicas | `S-1-15-3-2` | Permite escuchar en sockets entrantes (`bind/listen`). |
| `privateNetworkClientServer` | Redes locales / Intranet corporativa | `S-1-15-3-3` | Acceso a subredes privadas locales y RPC LAN. |
| `picturesLibrary` | Acceso a la carpeta Imágenes | `S-1-15-3-4` | Lectura/escritura en `%USERPROFILE%\Pictures`. |
| `videosLibrary` | Acceso a la carpeta Videos | `S-1-15-3-5` | Lectura/escritura en `%USERPROFILE%\Videos`. |
| `musicLibrary` | Acceso a la carpeta Música | `S-1-15-3-6` | Lectura/escritura en `%USERPROFILE%\Music`. |
| `documentsLibrary` | Acceso a Documentos | `S-1-15-3-7` | Lectura/escritura restringida a documentos. |
| `enterpriseAuthentication` | Autenticación Kerberos/NTLM | `S-1-15-3-8` | Uso de credenciales corporativas SSO. |
| *(Capacidades Personalizadas)* | Definidas por proveedores de software | `S-1-15-3-1024-X-Y-Z...` | Brokers de runtime específicos de la app. |

**Impacto en Reversing de Vulnerabilidades (Escape de Sandbox):**  
Si un analista audita un proceso en sandbox y detecta que este carece del SID `S-1-15-3-1` (`internetClient`), sabe de antemano que cualquier llamada a `connect()` de WinSock o llamadas a `WinHttpConnect` colapsarán a nivel de kernel en el filtro de red WFP con `WSAEACCES` (`10013`), independientemente del código desensamblado. Por el contrario, si un componente no interactivo posee indebidamente `S-1-15-3-3`, el proceso tiene superficie de ataque para interactuar con servicios RPC locales en la red corporativa.

---

## 2.2 Auditoría Forense y de Seguridad en Laboratorio: WinDbg y `AccessChk`

Para auditar un contenedor de aplicación en ejecución no basta con inspeccionar el explorador de procesos convencional. Es necesario auditar las estructuras internas del token a nivel de kernel y contrastar las DACLs a nivel de usuario.

### A. Inspección en Modo Kernel con WinDbg KDNET
Como se estudió en la Lección 2D.1 (Tomo II, pág. 64–68), el token de acceso reside en `nt!_EPROCESS->Token`. Al depurar un sistema con un proceso AppContainer/LPAC activo:

```windbg
$$ 1. Localizar el EPROCESS del proceso en sandbox (ej. SearchHost.exe)
kd> !process 0 0 SearchHost.exe
PROCESS ffffb801a2b40080
    SessionId: 1  Cid: 20c0    Peb: 0000003b8001a000
    Image: SearchHost.exe

$$ 2. Obtener la dirección del token despojando los bits inferiores de conteo rápido (_EX_FAST_REF)
kd> !token poi(ffffb801a2b40080 + @@(#FIELD_OFFSET(nt!_EPROCESS, Token))) & ~0xf
_TOKEN 0xffffb801a3518060
TS:               20c0
User:             S-1-5-21-2856281729-338294711-2098412-1001
Package:          S-1-15-2-53624-2894-3613-2819-3341
AppContainer SID: S-1-15-2-53624-2894-3613-...
TokenFlags:       0x000020a0   <-- NOTAR: Bit 0x20 activo = LPAC habilitado
Restricted SIDs:  Presentes

$$ 3. Volcar los Capability SIDs asignados en el token
kd> dt nt!_TOKEN 0xffffb801a3518060 Capabilities
   +0x0a8 Capabilities : Ptr64 _SID_AND_ATTRIBUTES
   +0x0b0 CapabilityCount : 0x4

kd> dx -r2 ((nt!_SID_AND_ATTRIBUTES*)0xffffb801a3518060->Capabilities)[0..3]
    [0] : Sid: S-1-15-3-1 (internetClient)
    [1] : Sid: S-1-15-3-2 (internetClientServer)
    [2] : Sid: S-1-15-3-1024-4053... (Custom Runtime Broker SID)
    [3] : Sid: S-1-15-3-1024-8842... (Audio Capture Capability)
```

**Verificación del Bit LPAC:**  
El campo `TokenFlags` (o el atributo de seguridad en `SecurityAttributes`) expone el bit **`0x00000020`** (`TOKEN_IS_LESS_RESTRICTED` / LPAC indicator). Si este bit está encendido, el kernel bloquea el acceso a cualquier descriptor que no conceda permisos a `S-1-15-2-2`.

---

### B. Auditoría en User-Mode con `AccessChk` (Sysinternals)

En modo usuario, sin necesidad de un depurador de kernel, la herramienta `accesschk.exe` de Sysinternals combinada con la bandera `-p` permite inspeccionar qué procesos tienen acceso efectivo a qué recursos del sistema:

```cmd
:: 1. Consultar los permisos de un proceso LPAC sobre una carpeta del sistema
accesschk.exe -p 8384 "C:\Windows\System32"

:: 2. Consultar qué named pipes puede abrir el contenedor (clave para explotación de IPC)
accesschk.exe -p 8384 \pipe\*

:: 3. Verificar si el proceso puede escribir en algún directorio de usuario
accesschk.exe -p 8384 -w -s "C:\Users\Public"
```

#### Análisis de Salida Típica de Named Pipes en LPAC:
```text
C:\Tools> accesschk.exe -p 8384 \pipe\*

Accesschk v6.15 - Reports effective permissions on objects
Copyright (C) 2006-2022 Mark Russinovich
Sysinternals - www.sysinternals.com

  \\.\Pipe\InitShutdown
        R NT AUTHORITY\SYSTEM
  \\.\Pipe\lsass
        R NT AUTHORITY\SYSTEM
  \\.\Pipe\SearchHost_ComLink
        RW S-1-15-2-53624-2894-... (Package SID)
  \\.\Pipe\W32SVC
        * Access Denied (Bloqueado por falta de S-1-15-2-2)
```

Si la salida de `accesschk` revela que un proceso LPAC tiene acceso `FILE_ALL_ACCESS` o `FILE_WRITE_DATA` sobre un named pipe administrado por un servicio del sistema (`NT AUTHORITY\SYSTEM`), el analista ha localizado un **vector crítico de fuga de sandbox (Sandbox Escape)**: el contenedor puede enviar comandos maliciosos al servicio privilegiado mediante llamadas de IPC.

---

### C. La Plantilla 19 (`plantilla_19_auditar_lpac.ps1`)

El repositorio incluye el script reproducible [`plantillas_codigo/plantilla_19_auditar_lpac.ps1`](file:///C:/Users/agust/.gemini/antigravity/scratch/CLS_Guia/plantillas_codigo/plantilla_19_auditar_lpac.ps1), el cual automatiza este análisis:
1. Enumera todos los procesos en ejecución y consulta sus tokens mediante P/Invoke a `OpenProcessToken` y `GetTokenInformation`.
2. Evalúa si `TokenIsAppContainer` es verdadero.
3. Decodifica los SIDs de paquete y lista todas las capacidades `S-1-15-3-*` activas.
4. Determina si el proceso corre en modo LPAC evaluando la presencia del bit `0x20` en `TokenFlags`.
5. Mide la superficie de ataque analizando el acceso a los named pipes del sistema.

---

## 2.3 WSL2 como Frontera Híbrida de Interoperabilidad (Windows $\leftrightarrow$ Linux)

### Aclaración de Alcance Metodológico
Siguiendo las restricciones de límites declaradas en la Sección 1.A del Tomo III:
> *Este apartado **no realiza ingeniería inversa de las llamadas internas del kernel de Linux** (`vmlinux` en ext4.vhdx) ni enseña a programar módulos `.ko`. Su propósito exclusivo es analizar **la frontera de comunicación e intercambio (IPC) entre el espacio de usuario de Windows y el subsistema virtualizado**, dotando al analista de herramientas para interceptar tráfico híbrido y llamadas remotas entre ambos mundos.*

### La Arquitectura de Micro-VM sobre Hyper-V
A diferencia de WSL1 (que implementaba un emulador de llamadas de sistema en modo kernel gobernado por `lxcore.sys` y `lxss.sys`), WSL2 corre un kernel Linux real optimizado dentro de una **máquina virtual liviana (*Utility VM*) administrada por Hyper-V**.

```
                   FRONTERA DE INTEROPERABILIDAD HÍBRIDA EN WSL2
                   
   [ ESPACIO WINDOWS (Host) ]                     [ ESPACIO LINUX (WSL2 Guest) ]
  ┌─────────────────────────────┐                ┌─────────────────────────────┐
  │ Proceso PE x64 (App.exe)    │                │ Proceso ELF x64 (daemon)    │
  └──────────────┬──────────────┘                └──────────────┬──────────────┘
                 │                                              │
                 ├── Sockets de Dominio Unix (AF_UNIX) ─────────┤
                 │   (afunix.sys en Windows ↔ AF_UNIX nativo)   │
                 │                                              │
                 ├── Named Pipes Compartidos ───────────────────┤
                 │   (\\.\pipe\wsl\... vía VMBus)               │
                 │                                              │
                 └── Protocolo WSLg (Wayland / RDP Rail) ───────┘
                     (Renderizado gráfico acelerado por GPU)
```

### Mecanismos de Intercambio y Superficie de Reversing

#### 1. Sockets de Dominio Unix Nativos (`AF_UNIX`)
Desde Windows 10 Build 17063, el kernel de Windows incorpora el controlador **`afunix.sys`**, permitiendo que procesos Win32 convencionales creen sockets de tipo `AF_UNIX` (`AF_UNIX = 1` en `winsock2.h`).
* **Cómo opera el puente:** Un archivo de socket Unix creado en el sistema de archivos de Windows (ej. `C:\Users\...\wsl_comm.sock`) es reconocido simultáneamente por el cliente en Windows y por el proceso en Linux montado bajo `/mnt/c/...`.
* **Reversing:** El analista que investiga una aplicación híbrida de Windows no debe buscar conexiones TCP locales (`127.0.0.1`) con `netstat`. Debe buscar llamadas a `socket(AF_UNIX, SOCK_STREAM, 0)` en el desensamblador de Windows, y rastrear la ruta del archivo de socket pasado en la estructura `sockaddr_un`.

```c
// Estructura sockaddr_un en Windows (afunix.h)
struct sockaddr_un {
    ADDRESS_FAMILY sun_family; // AF_UNIX (1)
    char sun_path[108];        // Ruta en disco: "C:\\temp\\wsl.sock" o "\\0abstract_socket"
};
```

#### 2. Named Pipes de WSL (`\\.\pipe\wsl\...`)
El servicio `wslservice.exe` en Windows expone una serie de tuberías con nombre en el espacio de nombres `\\.\pipe\`:
* `\\.\pipe\wsl\client`: Control de ciclo de vida del contenedor.
* `\\.\pipe\wsl\stdout` / `stderr`: Redirección de streams de consola.
* `\\.\pipe\wsl\g` (WSLg): Canal de comunicación para la extensión gráfica.

Un analista de malware o de herramientas defensivas puede interceptar este tráfico utilizando utilidades como `Pipe Mon` o creando un proxy de named pipes que clone el stream para auditar los comandos pasados al intérprete de Linux.

#### 3. El Canal WSLg y Aceleración Gráfica (vGPU)
WSLg ejecuta un compositor Wayland (Weston) en una partición de sistema aislada dentro de Linux. Para desplegar ventanas en el escritorio de Windows:
* Transmite las primitivas de renderizado a través de un canal RDP local optimizado mediante memoria compartida (*shared memory rails*).
* La aceleración de hardware utiliza el controlador **`dxgkrnl.sys`** en Windows proyectado hacia Linux a través del bus virtual **VMBus** mediante `/dev/dxg`.
* Cuando una aplicación híbrida falla o tiene problemas de rendimiento gráfico, el reverser debe auditar las llamadas IOCTL hacia `\\.\Device\Dxgk` en el anfitrión de Windows para verificar si el buffer de textura cruzó la frontera de la micro-VM.

---

## 2.4 Resumen de Prácticas del Módulo 2

Para afianzar los conceptos desarrollados en este módulo:
* [`plantillas_codigo/plantilla_19_auditar_lpac.ps1`](file:///C:/Users/agust/.gemini/antigravity/scratch/CLS_Guia/plantillas_codigo/plantilla_19_auditar_lpac.ps1): Script de auditoría de tokens AppContainer / LPAC sobre procesos en vivo en Windows 11.
* Práctica con `accesschk.exe`: Auditoría de Named Pipes contra procesos en sandbox LPAC para detección de posibles vectores de escape.
