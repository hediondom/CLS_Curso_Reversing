---
title: "2D.8 · DCOM y RPC: activación remota y límites de confianza"
description: "Seguir la activación y llamada DCOM/RPC entre equipos, entender autenticación, autorización, permisos de lanzamiento/acceso y niveles de impersonación, y documentar errores sin rebajar protecciones."
etapa: "Etapa 2 · 2D · Windows internals (optativa)"
---

# DCOM y RPC: activación remota y límites de confianza

:::{aviso} Laboratorio aislado
No habilites acceso remoto ni abras puertos para esta lección. No cambies DCOMCNFG, permisos, identidades, restricciones de equipo ni políticas. Usá dos VMs ya configuradas para un ejercicio autorizado; si la práctica requeriría debilitar una protección, limitate al análisis del diagrama y de la configuración existente.
:::

:::{nota} Propósito
Entender DCOM como activación/llamada de objetos COM a través de RPC y separar identidad autenticada, autorización, permisos de lanzamiento/activación y permisos de acceso. Al terminar deberías poder leer un error de DCOM como **un dato con varias explicaciones posibles** y documentarlo sin proponer que se baje la seguridad.
:::

**Prerrequisitos**

- *Obligatorios:* [2D.6 COM](2d-06-com-interfaces.html), [2D.7 activación](2d-07-com-activacion.html), red básica ([1.3](01-procesos.html)).
- *Recomendados:* tokens e impersonación ([2D.1](2d-01-objetos.html)); Windows Firewall y seguridad de cuenta; no exige completar toda 2D.

## Modelo

RPC permite invocar operaciones entre procesos locales o remotos. DCOM añade al modelo COM activación distribuida, proxies/stubs y negociación de seguridad. Una interfaz remota no se convierte en acceso libre por conocer su CLSID: intervienen autenticación, nivel de protección, identidad del servidor, permisos de lanzamiento/activación, permisos de acceso, firewall y políticas locales/dominio.

La autenticación de paquetes puede aportar integridad; privacidad agrega cifrado. Las actualizaciones de hardening DCOM elevaron requisitos de autenticación para activación. El detalle efectivo depende de la versión, actualizaciones y políticas administradas: documentá el estado, no copies recetas antiguas que bajan el nivel.

## Dos momentos distintos: activar y llamar

Conviene separar siempre dos operaciones, porque las controlan **permisos distintos** y fallan por **motivos distintos**.

**1. Activación remota.** El cliente pide un objeto en otro equipo (por ejemplo, `CoCreateInstanceEx` con un `COSERVERINFO`, o un `RemoteServerName` configurado en el AppID). El pedido llega al servicio de activación del equipo servidor, que:

- identifica al cliente (con el token de proceso o, si el cliente usa *cloaking*, el de hilo);
- comprueba los **permisos de lanzamiento y activación**: si el servidor no está corriendo, hace falta permiso para **lanzarlo**; si ya corre, permiso para **activar** un objeto en él;
- si corresponde, lanza el servidor con la **identidad** configurada (usuario que lanza, usuario interactivo, una cuenta concreta o un servicio);
- devuelve al cliente una referencia marshaleada, que en el cliente se convierte en un **proxy**.

**2. Llamada a un método.** Con el proxy ya en mano, cada llamada viaja por RPC al proceso servidor. Ahí se evalúan los **permisos de acceso** (quién puede llamar a un servidor que ya está corriendo), con el nivel de autenticación negociado, y el servidor puede **impersonar** al cliente dentro del nivel que el cliente permitió.

Consecuencia: un cliente puede **activar** con éxito y luego fallar en la **primera llamada**, o al revés. El informe tiene que decir en qué momento ocurrió el fallo.

## Cómo encuentra la llamada su destino: endpoints y puertos dinámicos

Muchos servidores RPC de Windows, entre ellos los servidores DCOM, no escuchan en un puerto fijo. Usan **endpoints dinámicos**: al arrancar, el servidor obtiene un puerto del rango dinámico y registra sus interfaces en el **mapeador de endpoints** (*Endpoint Mapper*, servicio RPCSS). El cliente primero pregunta al mapeador del equipo remoto —que en TCP escucha en el puerto **135**— dónde está la interfaz, y después se conecta al puerto que le devuelven. Desde Windows Vista y Server 2008, el rango dinámico predeterminado de TCP/IP es **49152–65535**, salvo que una política o configuración lo cambie.

En DCOM hay un detalle más: la referencia de interfaz que el servidor devuelve al activar contiene **direcciones IP del servidor** tal como él las ve. Microsoft advierte que por eso DCOM no funciona a través de firewalls que traducen direcciones (NAT).

Qué cambia para la evidencia:

- En el escenario típico, la activación usa el mapeador en el 135 y las llamadas posteriores van al **puerto dinámico** del proceso servidor. Un firewall que deja pasar el 135 pero no ese puerto produce exactamente el patrón “activa bien, falla la primera llamada”, sin que haya un problema de **permisos**.
- Un `0x800706BA` (servidor RPC no disponible) puede venir del mapeador inaccesible, del puerto dinámico bloqueado, de una dirección no alcanzable dentro de la referencia o de un servidor que terminó.
- En el laboratorio, de solo lectura: el puerto y el PID que escuchan en la VM servidor (`netstat -ano`), las reglas de firewall existentes y la dirección que la VM cliente usó. No se abren puertos ni se fija un rango para que “funcione”.

## Autenticación, autorización y permisos

- **Autenticación**: establece *quién* es el interlocutor (con NTLM, Kerberos u otro proveedor). No otorga nada por sí misma.
- **Autorización**: decide *qué puede hacer* esa identidad. En DCOM se expresa con listas de control de acceso.

Desde Windows XP SP2 / Server 2003 SP1, los derechos se separan por **distancia** (local o remoto):

| ACL | Derechos | Qué controla | Dónde vive |
|---|---|---|---|
| **Lanzamiento y activación** | Local Launch, Remote Launch, Local Activation, Remote Activation | Quién puede **arrancar** el servidor y quién puede **obtener** un objeto (un puntero de interfaz). | `LaunchPermission` del AppID; si no existe, `DefaultLaunchPermission`. |
| **Acceso** | Local Access, Remote Access | Quién puede **llamar** a un servidor que ya está en ejecución. | `AccessPermission` del AppID (solo si el proceso **no** llama a `CoInitializeSecurity`), el descriptor que pase `CoInitializeSecurity` o el valor por defecto del equipo. |
| **Restricciones de equipo** | Las mismas, como mínimo obligatorio | Un control adicional que se aplica a **todo** servidor COM del equipo, además del propio de cada aplicación. | `MachineLaunchRestriction` / `MachineAccessRestriction` o la política de grupo equivalente. |

Leé estas ACL como capas: una solicitud tiene que pasar **la restricción del equipo y** la de la aplicación. Que una ACL de aplicación sea permisiva no alcanza si la restricción del equipo lo impide, y viceversa.

## Nivel de autenticación frente a nivel de impersonación

Son dos perillas distintas que se negocian en el mismo “blanket” de seguridad:

| | Nivel de **autenticación** (`RPC_C_AUTHN_LEVEL_*`) | Nivel de **impersonación** (`RPC_C_IMP_LEVEL_*`) |
|---|---|---|
| Pregunta que responde | ¿Cuánta protección tiene la comunicación? | ¿Cuánto puede hacer el servidor **en nombre** del cliente? |
| Valores | None, Default, Connect, Call, Packet, Packet Integrity, Packet Privacy | Anonymous, Identify (el predeterminado del sistema), Impersonate, Delegate |
| Quién decide | Cliente y servidor proponen; en el handshake se usa **el más alto** de los dos. | Lo fija el **cliente** en su proxy. |
| Matices documentados | La mayoría de los proveedores promueve Call a Packet; Default nunca elige None. | Anonymous solo funciona en transporte local (en otros se promueve a Identify); Delegate requiere configuración de dominio específica. |

Un nivel de autenticación alto no autoriza más operaciones, y un nivel de impersonación bajo no debilita el cifrado: son ejes independientes.

## Servicio de autenticación: Kerberos, NTLM, Negotiate y el SPN

El *security blanket* —el conjunto de valores de seguridad que COM negocia para cada proxy— incluye, además de los niveles de la sección anterior, el **servicio de autenticación**: el paquete que de verdad autentica. Los más comunes en DCOM son **NTLM** (`RPC_C_AUTHN_WINNT`), **Kerberos** (`RPC_C_AUTHN_GSS_KERBEROS`) y **Negotiate/Snego** (`RPC_C_AUTHN_GSS_NEGOTIATE`), que no autentica por sí mismo sino que elige, entre los paquetes que admiten cliente y servidor, uno que funcione para ambos.

Qué paquete termina usándose **depende del contexto y de la configuración**: las listas que cada lado declaró (explícitamente con `CoInitializeSecurity`/`CoSetProxyBlanket` o por defecto), si los equipos y cuentas están en un dominio y se confían, el nombre con el que el cliente llegó al servidor, la existencia del SPN correcto y las políticas que restringen paquetes. No hay una regla universal del tipo “primero Kerberos y si no, NTLM” que puedas aplicar sin mirar esa configuración.

El **SPN** (*Service Principal Name*) es el identificador único de una instancia de servicio que Kerberos usa para asociarla con la cuenta con la que esa instancia inicia sesión. El SPN se registra en el objeto de esa cuenta en Active Directory, un mismo SPN puede estar en **una sola** cuenta, y si la cuenta del servicio cambia, los SPN deben registrarse de nuevo. El cliente **compone** el SPN a partir del nombre con el que localizó el servicio y lo presenta al autenticar; por eso, con Kerberos, el nombre de principal del servidor tiene que ser el correcto o la llamada falla.

Para la evidencia:

- Anotá **con qué nombre** se llegó al servidor (nombre corto, FQDN, alias o IP), **con qué cuenta** corre el servidor y si el binario fija un servicio de autenticación o un nombre de principal en `CoInitializeSecurity`/`CoSetProxyBlanket`.
- Si el código usa Negotiate, `CoQueryProxyBlanket` informa **Negotiate** y no el paquete que eligió: no deduzcas “Kerberos” o “NTLM” de esa consulta.
- Si había auditoría de inicio de sesión habilitada en el servidor, el registro de seguridad suele indicar el paquete usado; si no la había, decí que no se pudo determinar.

:::{nota} Recuadro conceptual: delegación de Kerberos
El nivel de impersonación **Delegate** permite que el servidor use la identidad del cliente hacia **otros** equipos, y solo funciona con Kerberos y configuración de dominio específica. Microsoft distingue, a grandes rasgos, tres modalidades: **sin restricciones** (la cuenta del servidor puede delegar hacia cualquier servicio), **restringida** (la cuenta del servidor solo puede delegar hacia una lista de servicios; se configura sobre la cuenta del servicio de entrada) y **restringida basada en recursos** (la decide el dueño del servicio de destino, sobre la cuenta de ese recurso). Señales que vale la pena **revisar**, sin cambiarlas: código que pide `RPC_C_IMP_LEVEL_DELEGATE`, cuentas de servicio marcadas como confiables para delegación, servicios con listas de delegación o con delegación basada en recursos, y cuentas sensibles que deberían estar marcadas como “no delegables”. Esta lección no enseña a configurar ni a probar delegación: el inventario lo hace o lo autoriza quien administra el directorio.
:::

## `CoInitializeSecurity` y `CoSetProxyBlanket`

- **`CoInitializeSecurity`** fija la seguridad **por proceso**: nivel de autenticación, nivel de impersonación, servicios de autenticación y, del lado servidor, quién puede acceder. Si el proceso la llama, **se ignoran** los valores de seguridad del registro para ese proceso (salvo que se le pase un AppID, en cuyo caso usa solo el registro). Algunas opciones, como cambiar el nivel de impersonación por defecto del proceso, solo se pueden fijar así.
- **`CoSetProxyBlanket`** ajusta la seguridad de **un proxy concreto** (una interfaz remota), sobrescribiendo los valores del proceso para las llamadas por ese proxy. Internamente equivale a pedir `IClientSecurity` al proxy y llamar a `SetBlanket`.

Para el análisis: si ves `CoInitializeSecurity` en el binario, lo que diga DCOMCNFG sobre **acceso** de esa aplicación puede no ser lo efectivo. Si ves `CoSetProxyBlanket`, el nivel usado en esa interfaz puede diferir del resto. Registrá los argumentos constantes que veas y marcá como inferencia los que dependen de valores en tiempo de ejecución.

## Ejemplo trabajado

*(Diagrama hipotético, sin tráfico capturado ni HRESULT observado.)*

```text
VM-Cliente: CoCreateInstanceEx(CLSID propio, servidor VM-Servicio)
  -> [ACTIVACIÓN] RPC hacia el servicio de activación de VM-Servicio
VM-Servicio: autentica al cliente
  -> restricción de equipo (launch/activation)  ¿pasa?
  -> LaunchPermission del AppID (o el valor por defecto)  ¿pasa?
  -> lanza BlocSrv.exe con la identidad configurada (si no estaba en ejecución)
  -> devuelve referencia marshaleada -> proxy para IID_IStatus en VM-Cliente
```

```text
VM-Cliente: p->GetState(&state)
  -> [LLAMADA] RPC al proceso BlocSrv.exe, con el nivel de autenticación negociado
VM-Servicio: restricción de equipo (access) + permisos de acceso del proceso  ¿pasa?
  -> stub -> BlocStatus::GetState; respuesta HRESULT + estructura de estado
```

Si la activación falla, las causas pueden estar en identidad, permisos, endpoint, DNS/red o hardening. Un error aislado no identifica cuál. El análisis correcto conserva HRESULT, evento y contexto y compara con la documentación de la versión.

### Cómo documentar un error sin atribuirle una causa única

| Dato | Ejemplo de registro | Por qué importa |
|---|---|---|
| Versión y build de **ambos** equipos | Edición, número de build, actualizaciones instaladas | El hardening DCOM cambió con actualizaciones; el mismo código puede comportarse distinto. |
| Momento del fallo | ¿Activación o llamada? ¿Primera llamada o posterior? | Separa permisos de lanzamiento/activación de permisos de acceso. |
| HRESULT exacto | Valor hexadecimal, no solo “acceso denegado” | `0x80070005` (`E_ACCESSDENIED`) puede venir de lanzamiento, activación o acceso; `0x800706BA` (servidor RPC no disponible) puede ser red, nombre, endpoint o firewall; `0x80080005` (`CO_E_SERVER_EXEC_FAILURE`) puede ser identidad, ruta o un fallo propio del servidor. |
| Identidades | Cuenta del cliente, identidad configurada del servidor | Distingue quién pidió de quién ejecuta. |
| Red y nombre | Nombre usado para llegar al servidor, puerto y PID que escuchan, reglas de firewall existentes | Separa fallos de transporte (mapeador, puerto dinámico, NAT) de fallos de autorización. |
| Autenticación | Servicio pedido en código (si es constante), paquete observado en auditoría (si existía), SPN esperado | Evita suponer Kerberos o NTLM sin evidencia. |
| Configuración leída (sin cambiarla) | AppID, `LaunchPermission`/`AccessPermission` presentes o ausentes, si el binario llama a `CoInitializeSecurity` | Indica qué capa podría estar decidiendo. |
| Eventos | Entradas de origen DCOM en el registro *System* de **ambos** equipos, con fecha y hora | Suelen nombrar CLSID/AppID y la identidad, pero no siempre la capa exacta. |
| Hipótesis y descartes | “Compatible con X; no descartado Y porque…” | Evita que el informe convierta una correlación en causa. |

## Práctica

Solo con dos VMs en una red virtual host-only, ya provistas y aprobadas por quien administra el laboratorio:

1. Revisá sin modificar DCOM Config (identidad del servidor, permisos de lanzamiento/acceso, autenticación), las restricciones de equipo y el firewall. Anotá versión/build de ambas VMs.
2. En el binario cliente y servidor, buscá llamadas a `CoInitializeSecurity` y `CoSetProxyBlanket` y registrá los niveles constantes que veas.
3. Si hay un componente propio de prueba ya preparado, registrá una llamada inocua de consulta, separando el resultado de la **activación** y el de la **llamada**, y la identidad visible en ambos lados.
4. Si no está preparado o la activación requiere cambiar la seguridad, no la habilites: reconstruí el flujo a partir de documentación y del diagrama del ejemplo, completando la tabla de documentación de errores como ejercicio.
5. Apagá las VMs o revertí ambos snapshots; no reutilices credenciales de producción ni expongas la red virtual al host/LAN.

## Entregable

Diagrama cliente–RPC–servidor con los dos momentos (activación y llamada) y las capas de control; versión/actualizaciones observadas; identidad; permisos; niveles de autenticación e impersonación; HRESULT/eventos y limitaciones. No incluyas credenciales, direcciones públicas ni cambios de seguridad.

## Repaso

?? ¿Qué añade DCOM a una llamada COM local?
!! Activación y comunicación distribuidas a través de RPC, con proxies/stubs y controles de seguridad remotos.

?? ¿Autenticación equivale a autorización?
!! No. La autenticación establece quién es el interlocutor; la autorización decide qué puede hacer.

?? ¿Qué permiso falta si la activación funciona pero la primera llamada al método devuelve acceso denegado?
!! Un candidato fuerte es un permiso de **acceso** (de la aplicación o la restricción de equipo), porque el de lanzamiento/activación ya se cumplió. Pero si el error es de transporte (por ejemplo, `0x800706BA`), también encaja un firewall que bloquea el puerto dinámico del servidor. Se distingue con el HRESULT exacto, eventos y configuración antes de afirmarlo.

?? ¿Por qué un firewall que permite el puerto 135 puede no alcanzar para DCOM?
!! Porque el 135 es el del mapeador de endpoints; las llamadas al objeto van al puerto dinámico que registró el proceso servidor.

?? El código usa Negotiate y `CoQueryProxyBlanket` devuelve Negotiate. ¿Se autenticó con Kerberos?
!! No se puede saber por esa consulta: informa Negotiate, no el paquete elegido. Hace falta otra evidencia, como la auditoría de inicio de sesión del servidor.

?? ¿Qué es un SPN y por qué importa el nombre con el que se llega al servidor?
!! Es el identificador de una instancia de servicio que Kerberos asocia a la cuenta del servicio. El cliente lo compone a partir del nombre que usó; si no corresponde a un SPN registrado en la cuenta correcta, Kerberos no puede autenticar ese servicio.

?? ¿En qué se diferencian el nivel de autenticación y el de impersonación?
!! El de autenticación fija la protección de la comunicación (y se usa el más alto propuesto); el de impersonación, que fija el cliente, limita qué puede hacer el servidor en su nombre.

?? El registro de una aplicación dice una cosa y la aplicación se comporta como si dijera otra. ¿Qué buscás en el binario?
!! Una llamada a `CoInitializeSecurity` (que hace ignorar los valores del registro para ese proceso) o a `CoSetProxyBlanket` (que cambia la seguridad de un proxy).

?? ¿Qué hacés si la práctica requiere desactivar hardening?
!! No la ejecutás. Analizás la configuración existente o usás un laboratorio actualizado que funcione con las protecciones vigentes.

:::{nota} Puerta optativa
Podés explicar las capas COM/DCOM/RPC, separar activación de llamada, autenticación de autorización y permisos de lanzamiento de permisos de acceso, distinguir nivel de autenticación de nivel de impersonación y documentar un error sin atribuirle una causa única ni recomendar bajar protecciones.
:::

:::{nota} Lo que queda fuera
El formato del protocolo DCOM en la red (OBJREF, resolución OXID), la configuración de puertos o rangos, el funcionamiento interno de Kerberos y NTLM, la configuración de delegación (solo como recuadro), *cloaking* y COM+ no se desarrollan. Tampoco se enseña a configurar DCOM ni el firewall: la lección es de lectura y diagnóstico.
:::

## Fuentes

- Microsoft Learn: [COM Clients and Servers](https://learn.microsoft.com/en-us/windows/win32/com/com-clients-and-servers), [Locating a Remote Object](https://learn.microsoft.com/en-us/windows/win32/com/locating-a-remote-object), [Activation Security](https://learn.microsoft.com/en-us/windows/win32/com/activation-security), [Authentication Level](https://learn.microsoft.com/en-us/windows/win32/com/authentication-level), [Impersonation Levels](https://learn.microsoft.com/en-us/windows/win32/com/impersonation-levels).
- Microsoft Learn, configuración: [Process-wide security / DCOMCNFG](https://learn.microsoft.com/en-us/windows/win32/com/setting-processwide-security-using-dcomcnfg), [Process-wide security with CoInitializeSecurity](https://learn.microsoft.com/en-us/windows/win32/com/setting-processwide-security-with-coinitializesecurity), [CoSetProxyBlanket](https://learn.microsoft.com/en-us/windows/win32/api/combaseapi/nf-combaseapi-cosetproxyblanket), [LaunchPermission](https://learn.microsoft.com/en-us/windows/win32/com/launchpermission), [AccessPermission](https://learn.microsoft.com/en-us/windows/win32/com/accesspermission), [DCOM Security Enhancements (XP SP2 / 2003 SP1)](https://learn.microsoft.com/en-us/windows/win32/com/dcom-security-enhancements-in-windows-xp-service-pack-2-and-windows-server-2003-service-pack-1).
- Microsoft Learn, red y autenticación: [Security Blanket Negotiation](https://learn.microsoft.com/en-us/windows/win32/com/security-blanket-negotiation), [COM authentication service constants](https://learn.microsoft.com/en-us/windows/win32/com/com-authentication-service-constants), [Snego](https://learn.microsoft.com/en-us/windows/win32/com/snego), [Service Principal Names](https://learn.microsoft.com/en-us/windows/win32/ad/service-principal-names), [How clients compose a service's SPN](https://learn.microsoft.com/en-us/windows/win32/ad/how-clients-compose-a-serviceampaposs-spn), [Kerberos constrained delegation overview](https://learn.microsoft.com/en-us/windows-server/security/kerberos/kerberos-constrained-delegation-overview), [RPC dynamic ports and firewalls](https://learn.microsoft.com/en-us/troubleshoot/windows-server/networking/configure-rpc-dynamic-port-allocation-with-firewalls), [Default dynamic port range](https://learn.microsoft.com/en-us/troubleshoot/windows-server/networking/default-dynamic-port-range-tcpip-chang), [Service overview and network port requirements](https://learn.microsoft.com/en-us/troubleshoot/windows-server/networking/service-overview-and-network-port-requirements).
- Microsoft Support: [DCOM hardening KB5004442](https://support.microsoft.com/en-us/topic/kb5004442-manage-changes-for-windows-dcom-server-security-feature-bypass-cve-2021-26414-f1400b52-c141-43d2-941e-37ed901c769c).
- **CLS:** contratos COM en [2D.6](2d-06-com-interfaces.html); activación en [2D.7](2d-07-com-activacion.html).

:::{nota} Etiquetas
**Observado en CLS:** ninguno específico de DCOM. **Conocimiento externo:** COM/RPC, mapeador de endpoints y puertos dinámicos, permisos, niveles de seguridad, servicios de autenticación, SPN, delegación (recuadro) y hardening. **Ejemplo ilustrativo:** flujo hipotético y tabla de registro de errores. **Laboratorio verificado:** no; la práctica depende de dos VMs preconfiguradas.
:::
