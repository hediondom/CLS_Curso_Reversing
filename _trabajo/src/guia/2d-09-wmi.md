---
title: "2D.9 · WMI: proveedores, filtros y consumidores"
description: "Leer proveedores y suscripciones WMI; distinguir consultas temporales de consumidores permanentes, relacionar filtro, binding, consumidor y proveedor, revisar CreatorSID, EventAccess y ACL del namespace, y documentar sin concluir de más."
etapa: "Etapa 2 · 2D · Windows internals (optativa)"
---

# WMI: proveedores, filtros y consumidores

:::{aviso} Alcance de la práctica
La práctica principal inspecciona WMI y usa consultas temporales. No crea suscripciones permanentes, no ejecuta las acciones que encuentre y no borra ni “repara” objetos durante el triage. Si un docente prepara una demostración permanente, debe usar solo una VM aislada y un consumidor benigno, con inventario previo y limpieza verificada.
:::

:::{nota} Propósito
Reconocer el modelo WMI/CIM y entender por qué un filtro unido a un consumidor permanente merece revisión, sin concluir malware solo por encontrar una suscripción. Al terminar deberías poder reconstruir una suscripción completa —qué evento la dispara, qué hace, quién la creó y con qué permisos— y dejar constancia de lo que **no** pudiste determinar.
:::

**Prerrequisitos**

- *Obligatorios:* Registro ([2D.3](2d-03-registro.html)) y contexto de seguridad ([2D.1](2d-01-objetos.html)).
- *Recomendados:* COM ([2D.6](2d-06-com-interfaces.html)), Task Scheduler ([2D.5](2d-05-task-scheduler.html)), servicios ([2D.4](2d-04-servicios.html)).

## Modelo

WMI expone clases/instancias a través de namespaces y proveedores. Un cliente consulta o se suscribe a eventos. La suscripción **temporal** vive mientras el cliente está conectado; una permanente permanece en el repositorio hasta cancelarse y relaciona `__EventFilter`, una instancia de `__EventConsumer` y `__FilterToConsumerBinding`. Los proveedores y consumidores tienen configuración y seguridad propias.

Para revisar una suscripción, lee namespace, filtro, consumidor, binding, propietario/CreatorSID, permisos y destino. Los consumidores estándar pueden tener efectos diferentes; no ejecutes scripts ni comandos encontrados. Una suscripción inesperada es un hallazgo que requiere contexto, no una prueba automática.

## Temporal frente a permanente

| | Consumidor **temporal** | Consumidor **permanente** |
|---|---|---|
| Cómo nace | Un programa o script llama a `ExecNotificationQuery` (o su variante asíncrona) y recibe eventos mientras corre. | Se guardan en el repositorio un filtro, un consumidor lógico y un binding. |
| Cuánto dura | Hasta que el cliente termina, WMI se detiene o el sistema se reinicia. | Hasta que alguien cancela la registración; sobrevive a reinicios. |
| Quién lo ejecuta | El propio cliente. | WMI carga el consumidor físico cuando hace falta. |
| Para el analista | Es lo que usás en la práctica para observar. | Es lo que inventariás y documentás, sin tocar. |

La documentación recomienda llamadas **semisíncronas** antes que asíncronas para consumidores temporales, porque en el modo asíncrono un llamador no autenticado puede entregar datos al *sink*.

## Namespaces: dónde vive la suscripción y de dónde vienen los eventos

WMI organiza clases en **namespaces** (`root\cimv2`, `root\subscription`, `root\default` y muchos otros que agregan productos y roles). Para este tema importan dos ideas:

- `root\cimv2` aloja las clases del proveedor Win32 y eventos intrínsecos como `__InstanceCreationEvent` sobre esas clases.
- Microsoft **recomienda** compilar las suscripciones permanentes en `root\subscription`, para tener un solo lugar donde buscarlas. Es una recomendación, no una garantía: los tres objetos pueden existir en **cualquier** namespace que tenga las clases necesarias. Un inventario que solo mira `root\subscription` puede quedar incompleto.

Hay que distinguir **dos namespaces** por suscripción:

1. El namespace donde **están guardados** el filtro, el consumidor y el binding (por ejemplo, `root\subscription`).
2. El valor de la propiedad **`EventNamespace`** del filtro: el namespace de los **eventos** que el filtro consulta (por ejemplo, `root\cimv2`). Con eso se arman suscripciones *cross-namespace*: el objeto vive en un lugar y escucha eventos de otro.

Si en la ficha anotás solo uno de los dos, la reconstrucción queda ambigua.

## Las piezas de una suscripción permanente

```text
__EventFilter                 (Name, Query WQL, QueryLanguage, EventNamespace,
   ^                           EventAccess, CreatorSID)
   | Filter
__FilterToConsumerBinding     (Filter, Consumer, MaintainSecurityContext, CreatorSID)
   | Consumer
   v
<consumidor lógico>           instancia de una clase derivada de __EventConsumer
                              (p. ej. NTEventLogEventConsumer, LogFileEventConsumer,
                               CommandLineEventConsumer, ActiveScriptEventConsumer…)
   | clase del consumidor
   v
__EventConsumerProviderRegistration  -> __Win32Provider (proveedor de consumidor, COM)
   v
consumidor físico (objeto COM que realmente ejecuta la acción)
```

- **Filtro**: *qué* evento interesa (consulta WQL de eventos).
- **Consumidor lógico**: *qué hacer* (escribir en el registro de eventos, en un archivo, lanzar un proceso, ejecutar un script, enviar correo…). Sus propiedades describen la acción, no el evento.
- **Binding**: la asociación que dice qué filtro alimenta a qué consumidor. Un filtro puede tener varios consumidores y un consumidor varios filtros.
- **Proveedor de consumidor**: el objeto COM que WMI localiza, mediante `__EventConsumerProviderRegistration`, para ejecutar al consumidor físico de esa clase. Por eso un consumidor de una clase no estándar te lleva a revisar también su registro COM (2D.7).

Entre los consumidores estándar, `CommandLineEventConsumer` lanza un proceso **en el contexto de sistema local**, y `ActiveScriptEventConsumer` ejecuta un script. Microsoft los señala como sensibles. Su presencia aumenta la prioridad de revisión; no define la intención.

## Leer la consulta del filtro: WQL de eventos

La propiedad `Query` del filtro está escrita en **WQL**. Microsoft la describe como un subconjunto de SQL con cambios semánticos: las consultas de datos van contra **una clase por vez**, su lista de palabras clave no incluye `JOIN` ni sentencias de modificación, y las consultas de **eventos** agregan cláusulas propias. No la leas como SQL general.

**Qué clase de evento se pide.**

- **Intrínsecos:** reflejan un cambio en el modelo de datos de WMI: creación, modificación o borrado de instancias, clases o namespaces (`__InstanceCreationEvent`, `__InstanceModificationEvent`, `__InstanceDeletionEvent`, `__InstanceOperationEvent`…). La instancia afectada viaja en `TargetInstance`, y el operador `ISA` restringe a una clase y sus subclases: `WHERE TargetInstance ISA 'Win32_Service'`.
- **Extrínsecos:** sucesos que un proveedor define como clase propia derivada de `__ExtrinsicEvent`, sin relación directa con instancias. Por ejemplo, el proveedor del registro define `RegistryKeyChangeEvent`.
- **De temporizador:** clases de reloj (`__TimerEvent` y relacionadas) que disparan en momentos o intervalos.

**Dos usos distintos de `WITHIN`.** La misma palabra cumple dos funciones que no son intercambiables:

| Forma | Dónde va | Qué hace | Qué te dice como analista |
|---|---|---|---|
| `WITHIN n` (sondeo) | Inmediatamente **antes** de `WHERE` | Fija el **intervalo de sondeo** que WMI usa para detectar eventos intrínsecos cuando no hay un proveedor de eventos para esa clase. Admite fracciones de segundo, pero valores demasiado chicos pueden rechazarse; Microsoft recomienda intervalos mayores a 5 minutos para la mayoría de los consumidores. | El costo y la latencia de detección. Un sondeo muy frecuente sobre una clase grande es una carga constante; la notificación puede llegar hasta `n` segundos tarde. |
| `GROUP WITHIN n` (agrupación) | **Después** de `WHERE`, tras `GROUP` | Junta los eventos similares que llegan durante `n` segundos desde el primero y entrega **un** evento agregado (`__AggregateEvent`). Admite `BY propiedades` y `HAVING NumberOfEvents …`. | Que el consumidor reacciona a **ráfagas o umbrales**, no a cada evento. |

Ejemplos de lectura (ilustrativos):

```text
SELECT * FROM __InstanceCreationEvent WITHIN 30
  WHERE TargetInstance ISA 'Win32_Process'
  -> sondea cada 30 s la aparición de procesos; reacciona a cada uno

SELECT * FROM __InstanceCreationEvent
  WHERE TargetInstance ISA 'Win32_NTLogEvent'
  GROUP WITHIN 600 BY TargetInstance.SourceName
  HAVING NumberOfEvents > 25
  -> agrupa 10 minutos por origen; solo entrega si hubo más de 25
```

Microsoft indica además que crear consumidores **permanentes** con consultas de sondeo requiere privilegios de administrador, y que cuando la consulta de un consumidor permanente falla se registra un evento de origen *WinMgmt* con id 10. Ese evento es evidencia útil de un filtro roto.

## Seguridad: CreatorSID, EventAccess y ACL del namespace

**`CreatorSID`.** WMI guarda en cada instancia el SID de quien la creó. Para que una suscripción permanente funcione, el filtro, el consumidor y el binding deben tener **el mismo** `CreatorSID`, y el creador debe ser una cuenta de dominio con privilegios de administrador local o el grupo Administradores local. Para los consumidores sensibles, WMI verifica que ese SID pertenezca a Administradores. Qué revisar:

- ¿Coinciden los tres `CreatorSID`? Si no, la suscripción probablemente no funciona; queda como hallazgo a explicar, no a reparar.
- ¿A qué cuenta o grupo corresponde el SID? Convertí el arreglo de bytes a SID de texto y resolvelo; si no resuelve (cuenta borrada, otro dominio), anotalo.

**`EventAccess`.** Es un descriptor de seguridad SDDL en el filtro que limita **qué identidades pueden publicar** eventos hacia él (derecho `WBEM_RIGHT_PUBLISH`). El valor por defecto es `NULL`, que permite a todos. Que esté vacío no es anómalo en sí; que esté restringido indica una configuración deliberada.

**ACL del namespace.** Cada namespace tiene un descriptor de seguridad que WMI compara con el token de quien se conecta: derechos como *Enable Account*, *Execute Methods*, *Full Write*, *Partial Write*, *Provider Write*, *Remote Enable*, *Read Security* y *Edit Security*. Revisá quién tiene escritura en el namespace donde vive la suscripción, comparalo con los permisos por defecto que documenta Microsoft y anotá las diferencias. La auditoría de namespaces existe (SACL), pero no viene habilitada; si no estaba activa **antes** del incidente, no esperes encontrar eventos de quién creó la suscripción.

## Leer un archivo MOF sin compilarlo

**MOF** (*Managed Object Format*) es el lenguaje con el que se describen clases e instancias CIM. Un proveedor suele distribuirse como un MOF (que define sus clases) más una DLL (que entrega los datos), y el MOF se **compila** al repositorio con `mofcomp`. Para el triage importa porque una suscripción permanente también puede escribirse como MOF.

Qué mirar en un `.mof` encontrado durante una revisión, **solo leyéndolo como texto**:

- `#pragma namespace("\\\\.\\root\\subscription")`: en qué namespace se crearían los objetos.
- Bloques `instance of __EventFilter as $FLT { … }`, `instance of <ClaseConsumidor> as $CONS { … }` e `instance of __FilterToConsumerBinding { Filter = $FLT; Consumer = $CONS; }`: es exactamente la terna filtro–consumidor–binding de esta lección.
- `#pragma autorecover`: agrega el archivo a la lista que WMI **recompila automáticamente** si reconstruye un repositorio dañado (la lista vive en `HKLM\SOFTWARE\Microsoft\WBEM\CIMOM\autorecover mofs`).

Dos límites de interpretación:

- Un MOF en disco **no prueba** que esos objetos existan en el repositorio: pudo no haberse compilado nunca. Y al revés, una suscripción puede existir en el repositorio sin ningún MOF en disco.
- **Nunca** ejecutes `mofcomp` sobre un archivo encontrado durante una revisión: compilarlo **crearía** los objetos que describe.

:::{nota} Recuadro conceptual: proveedores WMI
Un **proveedor** es un componente COM que entrega instancias, métodos o eventos de ciertas clases. Se registra con una instancia de `__Win32Provider`, cuyo `CLSID` apunta a su servidor COM (el recorrido de 2D.7 se aplica igual). La propiedad `HostingModel` define dónde y con qué cuenta corre: dentro de un proceso anfitrión compartido `WmiPrvSE.exe` como *NetworkService* (el predeterminado desde Vista cuando no se especifica), *LocalService* o *LocalSystem*; como servidor propio (*SelfHost*), o como proveedor desacoplado dentro de otra aplicación. Microsoft desaconseja *LocalSystem* por su privilegio y documenta eventos de registro cuando un proveedor usa ese modelo. Para la revisión basta con saber leer `__Win32Provider`, su CLSID y su `HostingModel`; **escribir** proveedores queda fuera del curso.
:::

## WMI remoto: el modelo, sin habilitar nada

Un cliente puede conectarse a WMI de **otro** equipo indicando el nombre del equipo en la ruta del namespace (`\\EQUIPO\root\cimv2` en `IWbemLocator::ConnectServer`, o `-ComputerName` en PowerShell). Esa conexión clásica viaja por **DCOM**, así que todo lo de 2D.8 aplica: firewall, permisos y autenticación DCOM, más el derecho **Remote Enable** sobre el namespace y las restricciones de UAC para cuentas remotas. La alternativa es **WinRM**, la implementación de Microsoft del protocolo WS-Management (SOAP sobre HTTP/HTTPS), que expone datos de WMI a través de su propio servicio y con su propia configuración; las sesiones CIM de PowerShell pueden usarlo.

Para la evidencia: una suscripción o una consulta pudo haberse creado **desde otro equipo**. Por eso un `CreatorSID` de cuenta de dominio, sin actividad local que lo explique, es una pista para preguntar al administrador por herramientas de gestión remota, no una conclusión. Esta lección **no** habilita WMI remoto, WinRM ni reglas de firewall.

## Criterios para documentar sin concluir de más

Una suscripción **existe**: eso es una observación. Que sea **maliciosa** es una conclusión que necesita más evidencia. Antes de clasificar, respondé:

- **Origen plausible:** ¿la instaló un producto conocido (agente de gestión, monitoreo, antivirus)? Nombres, rutas y proveedores de consumidor suelen delatar al producto; confirmalo con el inventario de software o con el administrador.
- **Coherencia:** ¿coinciden los `CreatorSID`? ¿El consumidor apunta a un archivo que existe, firmado, en una ruta protegida? Una ruta escribible por usuarios en un `CommandLineEventConsumer` es un riesgo aunque el producto sea legítimo.
- **Disparador:** ¿qué hace la consulta? Un temporizador, el arranque, el inicio de sesión o la creación de un proceso tienen implicancias distintas.
- **Temporalidad:** ¿hay registros de cambio, tickets o eventos que fechen la creación? Si no, decí que no se pudo fechar.
- **Alcance:** ¿la misma suscripción aparece en otros equipos de la flota? Si es así, sugiere despliegue centralizado (legítimo o no).

Conclusiones calibradas posibles: “esperada y documentada”, “legítima con riesgo de configuración”, “sin origen identificado: escalar”, “inconsistente/no funcional”. Ninguna de estas habilita a borrarla durante el triage.

## Ejemplo trabajado

*(Vista conceptual ficticia de un laboratorio, sin consulta activa. Nombres, rutas y SID son marcadores.)*

```text
Namespace de la suscripción: ROOT\subscription
  __EventFilter.Name           = "BlocLab-Filtro"
  __EventFilter.Query          = SELECT * FROM __InstanceCreationEvent WITHIN 30
                                 WHERE TargetInstance ISA 'Win32_Process'
                                 AND TargetInstance.Name = 'BlocLab.exe'
  __EventFilter.EventNamespace = root\cimv2
  __EventFilter.EventAccess    = (vacío)
  Consumidor: NTEventLogEventConsumer "BlocLab-Log"
  Binding: Filtro "BlocLab-Filtro" -> Consumidor "BlocLab-Log"
  CreatorSID (filtro, consumidor, binding): S-1-5-32-544 (los tres iguales)
```

Lectura: la suscripción vive en `root\subscription`, pero escucha eventos de `root\cimv2` (cross-namespace). El filtro sondea cada 30 segundos (`WITHIN 30`) la creación de un proceso llamado `BlocLab.exe` y el consumidor escribe una entrada en el registro de eventos: una acción de bajo impacto. Los tres `CreatorSID` coinciden con el SID del grupo Administradores, que es una forma documentada de crear suscripciones. `EventAccess` vacío significa que cualquier proveedor puede publicar al filtro.

La relación filtro–binding–consumidor permite reconstruir el flujo. Si falta un elemento o los SIDs no coinciden, la suscripción puede estar incompleta o requerir explicación; no la repares ni la borres durante triage.

### Ficha de evidencia

| Campo | Valor (ejemplo) | Fuente / tipo |
|---|---|---|
| Equipo, versión/build, fecha y hora de la revisión | VM-Lab-01, *(completar)* | Observación |
| Herramienta y cuenta usadas para inspeccionar | *(completar)*; sesión elevada sí/no | Observación |
| Namespace de la suscripción | `ROOT\subscription` | Observación |
| `EventNamespace` del filtro | `root\cimv2` | Observación |
| Filtro: nombre, consulta, lenguaje | `BlocLab-Filtro`, WQL arriba | Observación |
| Lectura de la consulta | Evento intrínseco de creación; sondeo `WITHIN 30`; sin `GROUP` | Interpretación de la WQL |
| Consumidor: clase, nombre y propiedades de acción | `NTEventLogEventConsumer`, `BlocLab-Log` | Observación (no ejecutado) |
| Proveedor de consumidor | Estándar de WMI | Inferencia por clase; confirmar registración |
| Binding y `MaintainSecurityContext` | Filtro → consumidor; *(completar)* | Observación |
| `CreatorSID` de los tres objetos y resolución | Iguales; Administradores | Observación + resolución |
| `EventAccess` | Vacío (`NULL`, todos pueden publicar) | Observación |
| ACL del namespace (escritura) | *(completar)*; diferencias con los valores documentados | Observación |
| Archivos referenciados (ruta, firma, hash, ACL) | No aplica para este consumidor | Observación |
| Origen plausible y evidencia | Laboratorio del curso, ticket *(completar)* | Contexto |
| Conclusión calibrada | Esperada y documentada | Juicio del analista |
| Lo que no se pudo determinar | Fecha de creación (sin auditoría previa) | Límite declarado |

## Práctica: inspección y evidencia

1. En una VM de laboratorio, inspeccioná primero una clase/proveedor WMI y una consulta temporal de lectura sobre datos conocidos (por ejemplo, instancias de `Win32_Service`).
2. Listá los namespaces existentes y decidí cuáles revisar; no te limites a `root\subscription`. Con PowerShell, de solo lectura: `Get-CimInstance -Namespace root -ClassName __NAMESPACE` para los namespaces y `Get-CimInstance -Namespace root/subscription -ClassName __EventFilter` (y luego `__EventConsumer` y `__FilterToConsumerBinding`) para cada namespace elegido.
3. Para cada suscripción, completá la ficha: namespace, `EventNamespace`, filtro, consumidor, binding, `CreatorSID` convertido a SID de texto, `EventAccess` y ACL del namespace. Sin ejecutar sus acciones.
4. Contrastá cuenta creadora, ACL del namespace, query y destino. Para cada consulta, anotá tipo de evento, si usa sondeo (`WITHIN`) o agrupación (`GROUP WITHIN`) y con qué intervalos. Redactá rutas personales antes de compartir evidencia.
5. Si en la VM hay archivos `.mof` de laboratorio, leelos como texto y compará lo que describen con lo que está en el repositorio. No los compiles.
6. No cambies ni elimines suscripciones encontradas. Si el laboratorio incluye una permanente creada previamente por el docente, identificá su ticket/ID y seguí la hoja de limpieza del laboratorio; verificá que los tres objetos vinculados ya no aparecen.

## Entregable

Ficha de evidencia de una consulta temporal o de una suscripción auditada, con todos los campos de la tabla, la conclusión calibrada y la sección de límites. Si no había una suscripción autorizada de prueba, indicá que no realizaste el paso de eliminación.

## Repaso

?? ¿Qué mantiene viva una suscripción permanente?
!! La inscripción persistente de filtro, consumidor y binding en el repositorio WMI; permanece hasta que se cancela.

?? ¿Por qué hay que revisar el binding?
!! Une qué evento se busca con qué consumidor recibirá el evento.

?? ¿Qué diferencia hay entre el namespace de la suscripción y `EventNamespace`?
!! El primero es donde están guardados filtro, consumidor y binding; `EventNamespace` indica de qué namespace vienen los eventos que el filtro consulta.

?? ¿Alcanza con revisar `root\subscription`?
!! No. Es la ubicación recomendada, pero una suscripción puede crearse en otros namespaces.

?? Los `CreatorSID` del filtro y del binding no coinciden. ¿Qué concluís?
!! Que la suscripción probablemente no funciona tal como está y que hay algo que explicar; no la reparás ni la borrás durante el triage.

?? ¿Qué controla `EventAccess`?
!! Qué identidades pueden publicar eventos hacia ese filtro; vacío (`NULL`) permite a todos.

?? ¿Qué diferencia hay entre `WITHIN 30` antes del `WHERE` y `GROUP WITHIN 30` después?
!! El primero fija un intervalo de **sondeo** para detectar eventos intrínsecos; el segundo **agrupa** eventos durante 30 s y entrega uno agregado (`__AggregateEvent`). No son intercambiables.

?? ¿Qué distingue un evento intrínseco de uno extrínseco?
!! El intrínseco refleja un cambio en el modelo de datos de WMI (instancias, clases, namespaces); el extrínseco es una clase de evento definida por un proveedor para un suceso que no es un cambio de instancia.

?? Encontrás un `.mof` con un filtro, un consumidor y un binding. ¿Prueba que la suscripción existe?
!! No. Hay que comprobarlo en el repositorio; el archivo pudo no compilarse nunca. Y no se compila durante la revisión, porque crearía los objetos.

?? ¿Qué aporta `#pragma autorecover` en un MOF?
!! Que WMI lo recompile automáticamente si reconstruye el repositorio; por eso conviene anotarlo junto con la entrada de registro correspondiente.

?? ¿Por qué un `CreatorSID` de dominio sin actividad local no prueba nada por sí solo?
!! Porque WMI admite conexiones remotas (por DCOM o WinRM): la suscripción pudo crearse con una herramienta de gestión remota. Es una pregunta para el administrador.

?? ¿Encontrar `__EventFilter` prueba una infección?
!! No. Hace falta relacionarlo con consumidor, binding, identidad, autorización y producto que lo instaló.

?? ¿Qué no se debe hacer con un consumidor desconocido?
!! No ejecutarlo, borrarlo ni repararlo durante la revisión; preservá datos y escalá al administrador.

:::{nota} Puerta optativa
Podés distinguir consulta temporal y suscripción permanente, ubicar ambos namespaces de una suscripción, leer la WQL del filtro (tipo de evento, sondeo y agrupación), reconstruir filtro–binding–consumidor–proveedor, leer un MOF sin compilarlo, revisar `CreatorSID`, `EventAccess` y ACL del namespace, y describir evidencia con una conclusión calibrada sin ejecutar la acción configurada.
:::

:::{nota} Lo que queda fuera
La escritura de proveedores (solo como recuadro), la sintaxis completa de MOF y de WQL (consultas de esquema, `ASSOCIATORS OF`, `REFERENCES OF`), el formato interno del repositorio, la configuración de WMI remoto o WinRM, y la habilitación de trazas o auditoría (que son cambios de configuración y no corresponden al triage) no se desarrollan.
:::

## Fuentes

- Microsoft Learn: [WMI architecture](https://learn.microsoft.com/en-us/windows/win32/wmisdk/wmi-architecture), [Monitoring Events](https://learn.microsoft.com/en-us/windows/win32/wmisdk/monitoring-events), [Receiving Events at All Times](https://learn.microsoft.com/en-us/windows/win32/wmisdk/receiving-events-at-all-times), [Receiving Events Securely](https://learn.microsoft.com/en-us/windows/win32/wmisdk/receiving-events-securely), [Maintaining WMI Security](https://learn.microsoft.com/en-us/windows/win32/wmisdk/maintaining-wmi-security).
- Microsoft Learn, clases y namespaces: [__EventFilter](https://learn.microsoft.com/en-us/windows/win32/wmisdk/--eventfilter), [__EventConsumer](https://learn.microsoft.com/en-us/windows/win32/wmisdk/--eventconsumer), [__FilterToConsumerBinding](https://learn.microsoft.com/en-us/windows/win32/wmisdk/--filtertoconsumerbinding), [__EventConsumerProviderRegistration](https://learn.microsoft.com/en-us/windows/win32/wmisdk/--eventconsumerproviderregistration), [Standard Consumer Classes](https://learn.microsoft.com/en-us/windows/win32/wmisdk/standard-consumer-classes), [Cross-Namespace Permanent Event Subscriptions](https://learn.microsoft.com/en-us/windows/win32/wmisdk/implementing-cross-namespace-permanent-event-subscriptions), [Access to WMI Namespaces](https://learn.microsoft.com/en-us/windows/win32/wmisdk/access-to-wmi-namespaces).
- Microsoft Learn, WQL y MOF: [WQL (SQL for WMI)](https://learn.microsoft.com/en-us/windows/win32/wmisdk/wql-sql-for-wmi), [Determining the Type of Event to Receive](https://learn.microsoft.com/en-us/windows/win32/wmisdk/determining-the-type-of-event-to-receive), [WITHIN Clause](https://learn.microsoft.com/en-us/windows/win32/wmisdk/within-clause), [GROUP Clause](https://learn.microsoft.com/en-us/windows/win32/wmisdk/group-clause), [HAVING Clause](https://learn.microsoft.com/en-us/windows/win32/wmisdk/having-clause), [ISA Operator for Event Queries](https://learn.microsoft.com/en-us/windows/win32/wmisdk/isa-operator-for-event-queries), [Managed Object Format (MOF)](https://learn.microsoft.com/en-us/windows/win32/wmisdk/managed-object-format--mof-), [pragma autorecover](https://learn.microsoft.com/en-us/windows/win32/wmisdk/pragma-autorecover).
- Microsoft Learn, proveedores y remoto: [__Win32Provider](https://learn.microsoft.com/en-us/windows/win32/wmisdk/--win32provider), [Provider Hosting and Security](https://learn.microsoft.com/en-us/windows/win32/wmisdk/provider-hosting-and-security), [Connecting to WMI on a Remote Computer](https://learn.microsoft.com/en-us/windows/win32/wmisdk/connecting-to-wmi-on-a-remote-computer), [About Windows Remote Management](https://learn.microsoft.com/en-us/windows/win32/winrm/about-windows-remote-management).
- **CLS:** servicios y tareas en [2D.4](2d-04-servicios.html) y [2D.5](2d-05-task-scheduler.html); DCOM en [2D.8](2d-08-dcom-rpc.html).

:::{nota} Etiquetas
**Observado en CLS:** análisis defensivo y persistencia como concepto. **Conocimiento externo:** arquitectura, namespaces, suscripciones, WQL de eventos, MOF, proveedores (recuadro), WMI remoto y seguridad de eventos WMI. **Ejemplo ilustrativo:** suscripción y ficha del laboratorio ficticio. **Laboratorio verificado:** no; inspección de solo lectura.
:::
