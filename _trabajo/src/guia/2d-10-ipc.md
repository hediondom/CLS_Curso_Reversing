---
title: "2D.10 · IPC en Windows: named pipes, RPC y ALPC"
description: "Distinguir mecanismos de comunicación entre procesos y revisar nombres, permisos, instancias, impersonación, endpoints y controles RPC sin explotación."
etapa: "Etapa 2 · 2D · Windows internals (optativa)"
---

# IPC en Windows: named pipes, RPC y ALPC

:::{aviso} Rama optativa 2D
Se analizan mecanismos en programas propios o didácticos. No se buscan endpoints de terceros para enviarles datos ni se enseña a abusarlos.
:::

:::{nota} Propósito
Reconocer IPC por evidencia estática/dinámica y explicar qué controles separan al cliente del servidor. Al terminar deberías poder decir, para un canal propio, **quién puede abrirlo**, **quién puede hacerse pasar por servidor**, **con qué identidad actúa** el servidor al atender y **qué valida** antes de procesar un mensaje.
:::

**Prerrequisitos**

- *Obligatorios:* procesos e hilos ([1.3](01-procesos.html)); objetos, handles, tokens y ACL ([2D.1](2d-01-objetos.html)).
- *Recomendados:* COM/RPC ([2D.6](2d-06-com-interfaces.html), [2D.8](2d-08-dcom-rpc.html)).

## Diferencias

- **Named pipe:** canal nombrado, local o de red según configuración; el nombre no es secreto. El servidor decide acceso con ACL y puede autenticar/impersonar clientes; revisá también framing, longitud y validación de mensajes.

Para reconstruir la estructura de los mensajes más allá del mecanismo IPC, seguí [4.5 · Reconstruir formatos y protocolos propios](../guia/04-formatos-protocolos.html).
- **RPC:** contrato de operaciones que puede comunicarse local o remotamente; el runtime gestiona transporte/marshalling según binding. Analizá interfaz, endpoint, identidad y autorización.
- **ALPC:** mecanismo local de bajo nivel usado por componentes de Windows. En reversing suele reconocerse por módulos, estructuras y trazas; la documentación pública del contrato es limitada y varía por versión. Se cubre conceptualmente, sin construir clientes de endpoints del sistema.

| | Named pipe | RPC | ALPC |
|---|---|---|---|
| Qué transporta | Bytes o mensajes | Llamadas a operaciones de una interfaz (IDL) | Mensajes locales del sistema |
| Dónde se ve | Nombre `\\.\pipe\…`, handles de tipo archivo | UUID y versión de interfaz, secuencia de protocolo, endpoint | Módulos y trazas; poca documentación pública |
| Control de acceso principal | Descriptor de seguridad del pipe | Autenticación + callback de seguridad + chequeos en cada operación | Interno del sistema |
| Lo que lees en un análisis | Creación, apertura, ACL, modo, impersonación | Registro de interfaz, flags, protocolos, autenticación | Que existe, quién lo usa y qué evento registra |

## Named pipes en detalle

**Nombres y alcance.** Un servidor crea `\\.\pipe\nombre` con `CreateNamedPipe`; el nombre no distingue mayúsculas y cualquiera que lo conozca puede **intentar** abrirlo. Un cliente de otro equipo puede llegar por la red con `\\servidor\pipe\nombre`, salvo que el servidor cree la instancia con `PIPE_REJECT_REMOTE_CLIENTS`, que rechaza automáticamente las conexiones remotas.

**Descriptor de seguridad.** Si el servidor pasa `NULL`, el pipe recibe un descriptor por defecto que, según la documentación, da control total a LocalSystem, a los administradores y al creador, y **lectura** a Everyone y a la cuenta anónima. Un servidor que atiende solo a su sesión puede restringir el acceso con el *logon SID*; Microsoft lo recomienda para impedir accesos desde otras sesiones o equipos.

**Quién puede ser servidor.** Para crear una instancia hace falta el derecho `FILE_CREATE_PIPE_INSTANCE` sobre el pipe. La documentación advierte que `FILE_GENERIC_WRITE` incluye ese derecho (comparte valor con `FILE_APPEND_DATA`), así que una ACL que da “escritura genérica” también deja **crear instancias**. Si el servidor real crea la primera con `FILE_FLAG_FIRST_PIPE_INSTANCE`, la llamada falla con `ERROR_ACCESS_DENIED` cuando el nombre ya existe: es la forma documentada de detectar que otro proceso ocupó el nombre antes.

**Modo.** Un pipe de tipo **mensaje** conserva los límites de cada escritura; uno de tipo **byte** no. El lado cliente arranca en modo byte aunque el servidor sea de mensajes. Para el análisis, esto define cómo hay que leer el protocolo: con mensajes, cada `WriteFile` es una unidad; con bytes, el protocolo necesita su propio *framing* (longitud, delimitador) y es ahí donde se validan tamaños.

**Impersonación.** El servidor puede llamar a `ImpersonateNamedPipeClient` para actuar con el token del cliente y volver a su propia identidad con `RevertToSelf`. Por defecto la impersonación es al nivel `SecurityImpersonation`, pero el **cliente** puede limitarla al abrir el pipe con `CreateFile` y la bandera `SECURITY_SQOS_PRESENT` (por ejemplo, a nivel identificación). Para el análisis importan tres preguntas: ¿el servidor impersona? ¿revierte en todas las rutas, incluidos los errores? ¿qué nivel pidió el cliente?

| Qué revisar en un pipe propio | Evidencia | Señal a explicar |
|---|---|---|
| Nombre y proceso creador | Handle en el proceso servidor, argumentos de `CreateNamedPipe` | Nombre predecible usado por un servicio privilegiado |
| Descriptor de seguridad | DACL pasada al crear (o `NULL`) | Descriptor por defecto o ACL con `FILE_GENERIC_WRITE` amplio |
| Primera instancia | `FILE_FLAG_FIRST_PIPE_INSTANCE` en la primera creación | Sin la bandera, otro proceso pudo ocupar el nombre antes |
| Clientes remotos | `PIPE_REJECT_REMOTE_CLIENTS` | Aceptación remota sin necesidad |
| Modo y framing | Tipo byte/mensaje, prefijo de longitud | Longitud leída del mensaje sin tope |
| Impersonación | `ImpersonateNamedPipeClient` / `RevertToSelf` | Rutas de error sin `RevertToSelf` |

## RPC en detalle

Una interfaz RPC se define en **IDL** con un UUID y una versión; MIDL genera los stubs de cliente y servidor. El servidor registra la interfaz y elige **secuencias de protocolo**: `ncalrpc` (local), `ncacn_np` (sobre named pipes) o `ncacn_ip_tcp` (TCP, normalmente con endpoint dinámico resuelto por el mapeador de 2D.8).

Tres lecturas de seguridad que Microsoft documenta y que cambian conclusiones:

- **Los endpoints no aíslan interfaces.** En un proceso con varios servidores RPC, *todas* las interfaces son invocables por *todos* los endpoints del proceso. Que tu componente registre solo `ncalrpc` no impide que lo llamen por un pipe o un socket que abrió otro componente del mismo proceso. Por eso un descriptor de seguridad sobre un endpoint no es un control efectivo; la recomendación es un **callback de seguridad** que verifique protocolo e identidad en cada llamada.
- **Registrar autenticación no la exige.** `RpcServerRegisterAuthInfo` agrega una **opción** de autenticación, no un requisito: un cliente no autenticado que podía conectarse sigue pudiendo, aunque luego fallen funciones como `RpcImpersonateClient`.
- **Flags de registro.** Con `RpcServerRegisterIf2`/`Ex`/`3`, `RPC_IF_ALLOW_LOCAL_ONLY` rechaza clientes remotos (con las excepciones que detalla la documentación para `ncacn_np`), y `RPC_IF_ALLOW_SECURE_ONLY` exige un nivel de autenticación mayor que *none*, **sin** garantizar que el usuario sea privilegiado: puede ser una cuenta de invitado.

Microsoft remarca que `ncalrpc` no es “seguro por ser local”: en un servidor de terminales, cientos de usuarios pueden llegar a un servicio local.

### Anatomía Interna de Stubs RPC y Decodificación de NDR (Format Strings)

Para el analista de ingeniería inversa que audita un binario sin símbolos ni archivos `.idl`, reconstruir la firma exacta de las funciones expuestas por un servidor RPC requiere inspeccionar las estructuras internas que MIDL compila en la sección `.data` o `.rdata`:

```text
RPC_SERVER_INTERFACE (puntero exportado o registrado con RpcServerRegisterIf2):
   +0x00: Length: 0x60 (96 bytes en x64)
   +0x04: InterfaceId.SyntaxGUID (UUID de 16 bytes de la interfaz)
   +0x14: InterfaceId.SyntaxVersion (Major/Minor version)
   +0x50: InterpreterInfo (Ptr64 a MIDL_SERVER_INFO)

MIDL_SERVER_INFO:
   +0x00: pStubDesc (Ptr64 a MIDL_STUB_DESC)
   +0x08: DispatchTable (Ptr64 a arreglo de punteros a funciones C del servidor)
   +0x10: ProcFormatString (Ptr64 a tabla de formatos de procedimiento NDR)
   +0x18: FmtStringOffset (Ptr64 a tabla de índices a ProcFormatString)
```

#### Decodificación de `ProcFormatString` y `TypeFormatString`
El compilador MIDL genera secuencias de bytes compactas que codifican los parámetros de cada método mediante la máquina de tipos de **NDR (Network Data Representation)**:
1. **Cabecera de Procedimiento:** En `ProcFormatString`, cada rutina arranca con una cabecera de 6 bytes en modo `-Oicf` que define el tamaño del marco en la pila (`stack_size`) y el número de parámetros.
2. **Descriptores de Parámetros (6 bytes por parámetro):**
   - **Flags de Dirección:** Los primeros 2 bytes indican si el parámetro es entrante o saliente (`0x0048` = `[in]`, `0x0158` = `[out]`, `0x0050` = `[in, out]`).
   - **Offset en el Stack:** Los siguientes 2 bytes indican la posición relativa en el marco de la llamada.
   - **Descriptor de Tipo:** Los 2 bytes finales contienen el tipo básico (`FC_LONG = 0x08`, `FC_HYPER = 0x0b`, `FC_CHAR = 0x02`) o un offset relativo hacia **`TypeFormatString`** (almacenado en `MIDL_STUB_DESC+0x28`).
3. **Tipos Complejos en `TypeFormatString`:**
   - `0x11` (`FC_RP`): Puntero de referencia (no puede ser nulo).
   - `0x12` (`FC_UP`): Puntero único (puede ser nulo).
   - `0x21` (`FC_C_CSTRING`): Cadena ASCII conformante terminada en nulo (`char*`).
   - `0x22` (`FC_C_WSTRING`): Cadena UTF-16 conformante terminada en nulo (`wchar_t*`).
   - `0x1A` (`FC_BOGUS_STRUCT`): Estructura compleja con alineación manual y punteros anidados.

El laboratorio `plantillas_codigo/rpc_com_server_lab.c` y su definición `rpc_com_server_lab.idl` permiten compilar un servidor local sobre `ncalrpc` y verificar la disposición exacta de estas tablas en memoria.

## ALPC

ALPC es el mecanismo de mensajes locales que usan muchos componentes de Windows. Su contrato no está documentado para uso general y cambia entre versiones, así que el curso solo pide **reconocerlo**: qué proceso lo usa, que existe una clase de eventos ETW para ALPC (ver [2D.12](2d-12-etw.html)) y que, si un análisis llega a ALPC, la conclusión debe apoyarse en la documentación del componente, no en suposiciones sobre el formato de los mensajes.

## Ejemplo trabajado

*(Ejemplo ilustrativo de una app propia; los valores no son una captura.)*

```text
BlocClient -> \\.\pipe\BlocLab.Status -> BlocService
Mensaje: {version=1, request=GET_STATUS}
Respuesta: {status=READY}
Seguridad: ACL permite al usuario de la sesión; no acepta datos arbitrarios
```

El pipe sugiere el transporte, pero hay que confirmar el proceso propietario, ACL, modo de lectura y formato del protocolo. Un nombre predecible no implica vulnerabilidad por sí solo.

Ficha del análisis, separando observación de inferencia:

| Dato | Valor (ilustrativo) | Tipo |
|---|---|---|
| Creador del pipe | `BlocService.exe`, cuenta de servicio de laboratorio | Observación (handle y proceso) |
| Flags de creación | `PIPE_ACCESS_DUPLEX`, `FILE_FLAG_FIRST_PIPE_INSTANCE`, `PIPE_TYPE_MESSAGE`, `PIPE_REJECT_REMOTE_CLIENTS` | Observación (argumentos en el código o el depurador) |
| DACL | Lectura/escritura al *logon SID* de la sesión; control total a SYSTEM | Observación (`GetSecurityInfo` en el lab) |
| Impersonación | `ImpersonateNamedPipeClient` antes de leer la configuración del usuario; `RevertToSelf` en salida normal y en error | Observación en código propio |
| Validación | Mensaje de tamaño fijo; versión distinta de 1 se rechaza | Observación en código propio |
| “Ningún otro proceso puede hacerse pasar por servidor” | — | Inferencia: la sostiene la primera instancia con bandera, no el nombre |

> **Ampliación editorial basada en fuentes externas — Inspección práctica de puertos y conexiones ALPC en user-mode y WinDbg (`!alpc`)**
>
> Aunque ALPC (*Advanced Local Procedure Call*) es una interfaz interna de `ntdll.dll`, el analista necesita saber reconocer sus llamadas en un binario y auditar qué procesos están conectados a un puerto local durante una sesión de depuración (*Windows Internals 7th Ed., Cap. 3 / extensión `!alpc` de WinDbg*) (**Hecho confirmado**):
>
> 1. **Las tres primitivas de `ntdll.dll` y el espacio de nombres `\RPC Control\`:**
>    * **Servidor:** Llama a `ntdll!NtAlpcCreatePort(&PortHandle, &ObjectAttributes, &PortInformation)` publicando un objeto de tipo `ALPC Port` en el directorio del Object Manager (casi siempre bajo `\RPC Control\<NombreDelPuerto>` o `\Sessions\<N>\BaseNamedObjects\...`).
>    * **Cliente:** Se conecta con `ntdll!NtAlpcConnectPort` (o `NtAlpcConnectPortEx`) especificando el `UNICODE_STRING` del puerto destino.
>    * **Intercambio de mensajes:** Ambos lados usan `ntdll!NtAlpcSendWaitReceivePort(PortHandle, Flags, SendMessage, SendMessageAttributes, ReceiveMessage, &BufferLength, ReceiveMessageAttributes, Timeout)`.
>
> 2. **Cabecera `PORT_MESSAGE` en memoria (`+0x00..+0x27`, 40 bytes en x64 / 24 bytes en x86):**
>    Todo mensaje enviado o recibido por ALPC comienza con una cabecera fija `PORT_MESSAGE` seguida inmediatamente por los datos de la aplicación:
>    ```c
>    typedef struct _PORT_MESSAGE_X64 {
>        USHORT DataLength;     // +0x00 (2B): Bytes útiles del payload después de esta cabecera
>        USHORT TotalLength;    // +0x02 (2B): sizeof(PORT_MESSAGE) (0x28 en x64) + DataLength
>        USHORT Type;           // +0x04 (2B): LPC_REQUEST (1), LPC_REPLY (2), LPC_CONNECTION_REQUEST (10)
>        USHORT DataInfoOffset; // +0x06 (2B)
>        PVOID  ClientIdUniqueProcess; // +0x08 (8B): PID del emisor (CLIENT_ID.UniqueProcess)
>        PVOID  ClientIdUniqueThread;  // +0x10 (8B): TID del emisor (CLIENT_ID.UniqueThread)
>        ULONG  MessageId;      // +0x18 (4B): ID correlativo del mensaje
>        ULONG  Reserved;       // +0x1C (4B)
>        ULONG_PTR ClientViewSize; // +0x20 (8B): Total cabecera = 0x28 (40 bytes en x64)
>    } PORT_MESSAGE_X64;
>    ```
>
> 3. **Comandos de inspección en solo lectura (Sysinternals y WinDbg de kernel):**
>    ```text
>    # En user-mode (consola elevada en la VM): listar todos los puertos ALPC abiertos y su proceso dueño
>    handle.exe -a -p <PID_o_nombre> "ALPC Port"
>
>    # En WinDbg conectado al kernel de la VM (extensión !alpc):
>    kd> !alpc /lpp <dir_EPROCESS>    ; Lista todos los puertos ALPC creados y conectados por ese proceso
>    kd> !alpc /p <dir_PortObject>    ; Muestra el proceso servidor, la cola de mensajes y todos los clientes conectados
>    kd> !alpc /m <dir_Message>       ; Decodifica un mensaje ALPC en vuelo y quién lo envió
>    ```

## Práctica

Con un cliente/servidor propios ya preparados:

1. Listá los pipes visibles en la VM solo para ubicar el tuyo (en PowerShell, `Get-ChildItem \\.\pipe\` muestra nombres) y no abras pipes ajenos.
2. Inspeccioná en Process Explorer/Procmon la apertura del endpoint y seguí una sola solicitud inocua. Capturá nombre, PID, operación, respuesta y ACL observada.
3. Completá la tabla “Qué revisar en un pipe propio” con evidencia del código o del depurador.
4. Para RPC, usá el propio contrato local: anotá UUID/versión, secuencias de protocolo registradas, flags de registro y si hay callback de seguridad.
5. Para ALPC, describí una traza/documentación existente, sin enviar mensajes.

## Entregable

Diagrama de dos procesos, mecanismo IPC, endpoint, identidad, controles, esquema del mensaje y evidencia. Incluí la tabla de revisión del pipe (o del registro RPC) con observación/inferencia. Ocultá datos personales; no registres payloads sensibles.

## Repaso

?? ¿Un named pipe siempre es local?
!! No. Puede ser local o accesible por red según cómo se publique y la configuración del sistema/servidor; `PIPE_REJECT_REMOTE_CLIENTS` rechaza clientes remotos.

?? ¿Qué diferencia RPC de un pipe?
!! RPC expresa una llamada mediante una interfaz; un pipe es un canal de bytes/mensajes. RPC puede usar distintos transportes.

?? ¿Qué derecho permite crear instancias de un pipe y por qué importa una ACL con escritura genérica?
!! `FILE_CREATE_PIPE_INSTANCE`. `FILE_GENERIC_WRITE` lo incluye, así que esa ACL también permite crear instancias, es decir, actuar como servidor.

?? ¿Para qué sirve `FILE_FLAG_FIRST_PIPE_INSTANCE`?
!! Hace que la creación falle si el nombre ya existe, así el servidor detecta que otro proceso ocupó el pipe antes.

?? ¿Quién controla hasta dónde puede impersonar un servidor de pipe?
!! El cliente, con `SECURITY_SQOS_PRESENT` y el nivel elegido al abrir el pipe; por defecto es `SecurityImpersonation`.

?? Un servidor RPC registra solo `ncalrpc`. ¿Queda accesible solo localmente?
!! No necesariamente: en un proceso con otros servidores RPC, la interfaz es invocable por cualquier endpoint del proceso. Se controla con un callback de seguridad.

?? ¿`RpcServerRegisterAuthInfo` impide que se conecten clientes no autenticados?
!! No. Agrega una opción de autenticación, no un requisito; hacen falta chequeos propios.

?? ¿Por qué ALPC se trata como concepto?
!! Es una interfaz interna de bajo nivel con contratos menos estables; el curso enseña reconocimiento, no clientes de endpoints del sistema.

:::{nota} Puerta optativa
Podés distinguir pipe, RPC y ALPC, seguir un intercambio propio, revisar ACL, primera instancia, clientes remotos, modo e impersonación de un pipe, y explicar por qué en RPC el control debe estar en el callback de seguridad y no en el endpoint.
:::

:::{nota} Lo que queda fuera
El protocolo de red de los pipes remotos, el formato interno de RPC (NDR), los mensajes ALPC, mailslots, memoria compartida y otros mecanismos IPC no se desarrollan. No se enseña a enviar datos a pipes ni a endpoints RPC ajenos.
:::

## Fuentes

- Microsoft Learn: [Interprocess Communications](https://learn.microsoft.com/en-us/windows/win32/ipc/interprocess-communications), [Named Pipes](https://learn.microsoft.com/en-us/windows/win32/ipc/named-pipes), [RPC](https://learn.microsoft.com/en-us/windows/win32/rpc/rpc-start-page), [ALPC ETW class](https://learn.microsoft.com/en-us/windows/win32/etw/alpc).
- Microsoft Learn, pipes: [CreateNamedPipe](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-createnamedpipea), [Named Pipe Security and Access Rights](https://learn.microsoft.com/en-us/windows/win32/ipc/named-pipe-security-and-access-rights), [Impersonating a Named Pipe Client](https://learn.microsoft.com/en-us/windows/win32/ipc/impersonating-a-named-pipe-client), [Named Pipe Type, Read, and Wait Modes](https://learn.microsoft.com/en-us/windows/win32/ipc/named-pipe-type-read-and-wait-modes).
- Microsoft Learn, RPC seguro: [Writing a Secure RPC Client or Server](https://learn.microsoft.com/en-us/windows/win32/rpc/writing-a-secure-rpc-client-or-server), [Be Wary of Other RPC Endpoints Running in the Same Process](https://learn.microsoft.com/en-us/windows/win32/rpc/be-wary-of-other-rpc-endpoints-running-in-the-same-process), [RpcServerRegisterAuthInfo doesn't deny unauthorized users](https://learn.microsoft.com/en-us/windows/win32/rpc/common-mistake-assuming-rpcserverregisterauthinfo-prevents-unauthorized-users-from-calling-your-server), [Interface Registration Flags](https://learn.microsoft.com/en-us/windows/win32/rpc/interface-registration-flags), [Protocol Sequence Constants](https://learn.microsoft.com/en-us/windows/win32/rpc/protocol-sequence-constants).
- **Fundamentos previos:** call stack y procesos en [1.3](01-procesos.html); DCOM/RPC en [2D.8](2d-08-dcom-rpc.html).

:::{nota} Etiquetas
**Núcleo conceptual:** procesos e IPC general. **Conocimiento externo:** IPC Windows, seguridad de named pipes y RPC. **Ejemplo ilustrativo:** protocolo y ficha BlocLab. **Laboratorio verificado:** no; ejemplo propio propuesto.
:::
