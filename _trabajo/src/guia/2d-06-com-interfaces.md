---
title: "2D.6 · COM: interfaces, IUnknown y vida de los objetos"
description: "Leer contratos COM: GUID, IID, HRESULT, vtables, QueryInterface, reference counting, apartamentos STA/MTA y proxies, con un componente propio. Rama optativa 2D."
etapa: "Etapa 2 · 2D · Windows internals (optativa)"
---

# COM: interfaces, IUnknown y vida de los objetos

:::{aviso} Rama optativa 2D
Lección conceptual y de análisis. El ejemplo es un componente propio; no se registra ni modifica software ajeno.
:::

:::{nota} Propósito
Reconocer cómo un cliente pide una interfaz COM, cómo interpretar el resultado y cómo seguir la llamada hasta la implementación sin confundir una interfaz con una clase C++ concreta. Al terminar deberías poder decir, frente a una llamada indirecta, **qué contrato** se está usando, **en qué apartamento** vive el objeto y si el puntero que tenés delante es el objeto o un **proxy**.
:::

**Prerrequisitos**

- *Obligatorios:* punteros, estructuras y convención de llamada ([1.5](01-c-python.html), [2.5](02-llamadas.html)); objetos y handles ([2D.1](2d-01-objetos.html)).
- *Recomendados:* C++ profundo ([2.18](02-cpp-profundo.html)); memoria y loader ([2D.2](2d-02-memoria-loader.html)); procesos e hilos ([1.3](01-procesos.html)).

## Conceptos

- **CLSID** identifica una clase COM; **IID** identifica un contrato de interfaz. Ambos son GUID, pero responden preguntas distintas.
- **`IUnknown`** es la base de las interfaces COM: `QueryInterface`, `AddRef` y `Release`. La consulta devuelve `S_OK` si el objeto ofrece el IID o `E_NOINTERFACE` si no.
- **HRESULT** comunica éxito o fallo. No lo interpretes como un booleano: se usa `SUCCEEDED(hr)` / `FAILED(hr)`; algunos resultados no negativos (como `S_FALSE`) indican éxito informativo.
- Una **vtable** contiene punteros a métodos en orden contractual. En una interfaz derivada, los métodos de `IUnknown` preceden a los propios.
- El **reference counting** administra la vida del objeto. Una referencia obtenida debe equilibrarse con `Release`; después de la última liberación, ese puntero no se reutiliza.
- Una llamada puede atravesar una **proxy/stub** si el objeto vive en otro apartamento o proceso. El puntero visible al cliente no tiene por qué apuntar directamente al código servidor.

## Inicialización por hilo: `CoInitializeEx` y `CoUninitialize`

COM no se “enciende” una vez por proceso: **cada hilo** que usa interfaces COM llama a `CoInitializeEx` y, con eso, declara su modelo de concurrencia y queda asociado a un **apartamento**. El primer parámetro es reservado (`NULL`); el segundo lleva exactamente uno de `COINIT_APARTMENTTHREADED` o `COINIT_MULTITHREADED`, más opciones como `COINIT_DISABLE_OLE1DDE`.

Lo que conviene registrar al analizar un binario:

| Resultado | Significado documentado | Qué implica para el análisis |
|---|---|---|
| `S_OK` | COM se inicializó en ese hilo. | Debe haber un `CoUninitialize` equilibrado antes de que el hilo termine. |
| `S_FALSE` | COM ya estaba inicializado en ese hilo con el mismo modelo. | Es éxito; **también** debe equilibrarse con `CoUninitialize`. |
| `RPC_E_CHANGED_MODE` | Un llamado previo fijó un modelo incompatible para ese hilo. | Es fallo: el hilo **sigue** en el modelo anterior y no corresponde un `CoUninitialize` por este llamado. |

Microsoft indica además que no se llame a `CoInitialize(Ex)` ni a `CoUninitialize` desde `DllMain`. Cuando veas una DLL que lo hace, anotalo como hallazgo de calidad, no como intención maliciosa.

## Apartamentos: STA, MTA y por qué existe el marshaling

Un **apartamento** agrupa objetos COM y los hilos que pueden llamarlos **directamente**. Cada objeto vive en exactamente un apartamento; un hilo de otro apartamento que quiera llamarlo debe pasar por un **proxy**.

- **STA (single-threaded apartment)**: un único hilo. Las llamadas que llegan desde otros apartamentos se entregan a través de la **cola de mensajes** de ese hilo, así que se serializan y solo avanzan cuando el hilo bombea mensajes. Si un hilo STA se bloquea en una espera sin bombear (por ejemplo, `WaitForSingleObject`), las llamadas entrantes no se entregan y aparece un interbloqueo. La documentación recomienda `CoWaitForMultipleHandles` o `MsgWaitForMultipleObjects` en esos hilos.
- **MTA (multithreaded apartment)**: uno o más hilos; a lo sumo **una** MTA por proceso. Cualquier hilo de la MTA puede llamar directamente a los objetos de la MTA, y **el objeto** debe sincronizarse por su cuenta (secciones críticas, mutex, etc.).
- Un proceso puede tener **cero o más STA** y **cero o una MTA**. También existe el apartamento **neutral** (NA), que aparece en la próxima lección a través de `ThreadingModel=Neutral`.

**Marshaling** es empaquetar la llamada (parámetros, punteros de interfaz) para que cruce un límite de apartamento, de proceso o de equipo. Existe porque las reglas anteriores solo se cumplen si nadie copia un puntero de interfaz “crudo” a un hilo de otro apartamento. Para pasar una interfaz entre apartamentos del mismo proceso se usan mecanismos explícitos —la Global Interface Table o, en código moderno (Windows 8.1+), `RoGetAgileReference`— que devuelven un puntero directo si se resuelve en el mismo apartamento o un proxy si no.

:::{nota} Lectura defensiva del modelo de hilos
En un análisis, el modelo de hilos sale de la evidencia: el flag pasado a `CoInitializeEx` (si lo ves en un argumento constante), el `ThreadingModel` del servidor (2D.7) y la presencia de un bucle de mensajes. Si solo tenés una de las tres, escribí “probable STA/MTA” y por qué.
:::

## Proxies y stubs: cuando el puntero no es el objeto

Un **proxy** vive en el espacio del llamador y, para el cliente, *es* el objeto: implementa la misma interfaz, empaqueta los parámetros en un búfer y los entrega al canal (RPC). Del otro lado, un **stub** desempaqueta y llama a la implementación real. El proxy es un objeto compuesto: un *proxy manager* (que implementa el `IUnknown` controlador) y un *interface proxy* por cada interfaz expuesta a ese cliente. El código de esos interface proxies puede estar en una DLL distinta, que el registro asocia al IID mediante `HKCR\Interface\{IID}\ProxyStubClsid32`.

Cómo reconocerlo en el depurador, sin suponer nombres:

1. Tomá el puntero de interfaz `p` y leé su primer campo: es la dirección de la vtable.
2. Resolvé a qué **módulo** pertenecen la vtable y sus primeras entradas (`lm`/`ln` en WinDbg, o el mapa de memoria de tu depurador).
3. Si apuntan al **módulo servidor**, probablemente es un puntero directo. Si apuntan a módulos del runtime COM/RPC o a una DLL de proxy/stub, es un proxy. Los nombres concretos de esos módulos y funciones dependen de la versión de Windows y de los símbolos disponibles: registrá lo que veas, no lo que esperabas ver.
4. Confirmalo con el contexto: ¿el objeto se creó en otro proceso (`LocalServer32`) o en otro apartamento? ¿El hilo cliente es STA y el servidor `Free`?

Consecuencia práctica: poner un breakpoint en la entrada de la vtable de un proxy **no** te lleva a la implementación; te lleva al código de marshaling. La implementación se sigue en el **proceso o apartamento del servidor**.

## Marshaling a medida y el *free-threaded marshaler*

El marshaling estándar no es la única opción. Un objeto puede implementar **`IMarshal`** y decidir por su cuenta cómo se empaqueta una referencia a sí mismo (*custom marshaling*). Para el analista, esto significa que el proxy que aparece del otro lado puede no ser el estándar: puede ser un objeto escrito por el autor del componente, con su propio protocolo.

El caso más común es el **free-threaded marshaler** (FTM), que se obtiene con `CoCreateFreeThreadedMarshaler` y se **agrega** al objeto (ver “Agregación y *tear-offs*”, más abajo). Cuando alguien marshalea una interfaz de ese objeto, el FTM mira el contexto de destino:

- si el destino es **otro apartamento del mismo proceso** (`MSHCTX_INPROC`), copia el puntero real: el otro apartamento recibe un **puntero directo**, sin proxy;
- si el destino es **otro proceso u otro equipo**, delega en el marshaling estándar: ahí **sí** hay proxy y stub.

Tres límites que conviene escribir en el informe:

1. El FTM **no elimina** el marshaling entre procesos; solo evita el proxy dentro del proceso.
2. Al eliminar el proxy, también elimina la sincronización que el apartamento le daba al objeto: **el objeto tiene que manejar su propia concurrencia**. Microsoft lo describe como una violación calculada de las reglas de COM, con riesgo de comportamiento indefinido si el objeto guarda punteros directos a objetos que no usan el FTM o referencias a proxies de otros apartamentos.
3. En código nuevo (Windows 8.1+), Microsoft recomienda `RoGetAgileReference` en lugar del FTM.

Señales en un binario: una llamada a `CoCreateFreeThreadedMarshaler` en la construcción del objeto y un `QueryInterface` que responde a `IID_IMarshal` delegando en otro objeto. Si las ves, “no hay proxy entre apartamentos” deja de ser una anomalía y pasa a ser el comportamiento esperado; lo que hay que revisar es si el objeto se sincroniza bien.

## Reglas de `QueryInterface` que podés usar como evidencia

Microsoft fija tres reglas para implementar `QueryInterface`:

- **Identidad**: para un mismo objeto, `QueryInterface(IID_IUnknown)` devuelve **siempre el mismo valor de puntero**. Por eso, para saber si dos interfaces pertenecen al mismo objeto, se comparan los resultados de pedir `IID_IUnknown` a cada una, no los punteros de interfaz originales (que suelen diferir).
- **Conjunto estático**: si un IID devolvió `S_OK` una vez, no puede devolver `E_NOINTERFACE` después en el mismo objeto, y viceversa.
- **Reflexiva, simétrica y transitiva**: desde cualquier interfaz se puede pedir la misma interfaz, volver a la anterior y llegar a cualquier otra que el objeto ofrezca.

Uso en reversing: si observás un objeto que ofrece un IID “a veces”, o dos `IUnknown` distintos para lo que creías un solo objeto, no es una curiosidad. Puede ser un bug del componente, que en realidad son objetos distintos o que estás mirando un proxy. Registralo y explicá cuál hipótesis sostenés y con qué evidencia.

## Agregación y *tear-offs*: un objeto, varias implementaciones

La regla de identidad habla del **objeto COM**, no de una clase C++. Dos técnicas hacen que un objeto COM esté formado por varias piezas de código, y las dos se ven raras si no las conocés.

**Agregación.** Un objeto **externo** expone interfaces de un objeto **interno** como si fueran propias. Para que la identidad se mantenga:

- al crear el interno, el externo pasa su propio `IUnknown` como `pUnkOuter` en `CoCreateInstance` y **debe pedir `IID_IUnknown`**; si pide otra interfaz, la creación falla (un objeto que no admite agregación devuelve `CLASS_E_NOAGGREGATION`);
- el interno tiene **dos** `IUnknown`: uno propio (*no delegante*), que controla su vida y que solo conoce el externo, y el de sus demás interfaces, que **delega** `QueryInterface`, `AddRef` y `Release` en el `IUnknown` **controlador** del externo;
- el cliente siempre ve un solo objeto: pedir `IID_IUnknown` desde cualquier interfaz devuelve el `IUnknown` del externo.

Cómo se ve en un binario: un `CoCreateInstance` (o un constructor) que recibe un `pUnkOuter` no nulo junto con `IID_IUnknown`, y métodos `QueryInterface`/`AddRef`/`Release` que solo hacen un salto indirecto a través de un puntero guardado (el controlador). Si seguís la vtable de una interfaz agregada, sus primeros tres slots apuntan a código del **interno** que solo reenvía al controlador del **externo**, y el resto, a la implementación del interno, que puede estar en otra DLL.

**Tear-offs.** Algunas bibliotecas (ATL, por ejemplo, con `COM_INTERFACE_ENTRY_TEAR_OFF`) crean la implementación de una interfaz poco usada **recién cuando alguien la pide**, como un objeto auxiliar que delega `IUnknown` en el principal. Consecuencias: dos `QueryInterface` del mismo IID pueden devolver **punteros de interfaz distintos** (dos tear-offs), sin violar la identidad, porque ambos devuelven el mismo `IUnknown`; y la memoria de esa interfaz puede no existir antes del primer pedido.

Para el informe: si los punteros de interfaz difieren pero `IID_IUnknown` coincide, anotá “compatible con agregación o tear-off” y buscá el patrón de delegación antes de afirmar cuál es.

## Monikers y la tabla de objetos en ejecución (ROT)

Un **moniker** es un objeto (interfaz `IMoniker`) que **nombra** a otro objeto y sabe cómo obtenerlo: a eso se le llama *binding*. Hay monikers de archivo, de ítem, de clase, compuestos y otros; OLE los usa para conectar y activar objetos en el mismo equipo o en la red, por ejemplo en los vínculos de documentos compuestos.

La **ROT** (*Running Object Table*, interfaz `IRunningObjectTable`, obtenida con `GetRunningObjectTable`) es una tabla por estación de trabajo con pares (moniker, objeto en ejecución). Cuando un cliente resuelve un moniker, se consulta la ROT para conectarse a la instancia que ya corre en vez de crear otra. Un objeto se **registra** en la ROT al cargarse y debe **revocar** su registro al terminar.

Qué aporta al análisis:

- Un cliente que obtiene un objeto con `CoGetObject`, `BindMoniker`/`IMoniker::BindToObject` o consultando la ROT **no** pasa necesariamente por `CoCreateInstance`: si buscás solo activaciones, te lo perdés.
- Un servidor que llama a `IRunningObjectTable::Register` está publicando un objeto para que otros procesos lo encuentren por nombre. Anotá qué moniker usa y con qué flags; es parte de su superficie.
- Enumerar la ROT (`EnumRunning`) es una operación de lectura; conectarse a un objeto encontrado ahí **no** lo es, porque ejecuta código del servidor. En la práctica de esta lección solo se anota lo que el **binario propio** registra o consulta.

:::{nota} Recuadro conceptual: COM+
COM+ (Component Services) agrupa componentes COM en **aplicaciones COM+** que se administran como una unidad: alcance de despliegue, configuración y seguridad común, atributos que el autor del componente no escribió (transacciones, sincronización), y procesos anfitriones administrados (`DllHost.exe`) que cargan las DLL bajo demanda. Su configuración vive en un **catálogo** propio, no solo en las claves de 2D.7. Si en un análisis ves un `DllHost.exe` con una DLL de componente o referencias a contextos COM+, sabé que existe esta capa; esta lección **no** la desarrolla y no conviene sacar conclusiones de seguridad sin consultar la configuración del catálogo.
:::

## IID, orden de métodos, slot y convención de llamada

El **slot** de vtable se deduce así: `slot = offset / tamaño_de_puntero`. El nombre del método **no** sale del offset; sale de combinar cuatro datos:

1. **IID** usado para obtener el puntero (lo ves como argumento de `QueryInterface` o `CoCreateInstance`).
2. **Definición de la interfaz** (IDL, header, type library o PDB) con el **orden** de los métodos, incluida la herencia (`IUnknown` aporta los slots 0–2).
3. **Arquitectura**: 4 bytes por slot en x86, 8 bytes en x64.
4. **Convención de llamada**: en x86, los métodos COM usan `__stdcall` y `this` va en la pila como primer argumento; en x64 hay una sola convención y `this` viaja en `RCX`, seguido de `RDX`, `R8` y `R9`.

| Slot | Método (`IStatus : IUnknown`) | Offset x86 | Offset x64 |
|---|---|---|---|
| 0 | `QueryInterface` | `+0x00` | `+0x00` |
| 1 | `AddRef` | `+0x04` | `+0x08` |
| 2 | `Release` | `+0x08` | `+0x10` |
| 3 | `GetState` | `+0x0C` | `+0x18` |

Un `call [rax+18h]` en x64 es “slot 3”; solo es `IStatus::GetState` si el puntero vino de un `QueryInterface`/`CoCreateInstance` con `IID_IStatus` (o de una interfaz que deriva de ella) **y** la definición confirma el orden.

## Ejemplo trabajado (x64, MSVC)

*(Ejemplo ilustrativo de un componente propio `BlocStatus` compilado para **x64**. Las instrucciones muestran el patrón que genera MSVC para llamadas COM; las posiciones de pila y los resultados no son una captura de un binario real.)*

Contrato, tal como lo declararía el IDL propio:

```text
interface IStatus : IUnknown        // IID_IStatus
{
    HRESULT GetState([out] ULONG* state);   // slot 3
};
```

Llamadas del cliente, en el orden que se ve en el desensamblado. Primero, inicialización y creación:

```text
; hilo cliente
xor   ecx, ecx                    ; pvReserved = NULL
mov   edx, 2                      ; COINIT_APARTMENTTHREADED  -> hilo STA
call  CoInitializeEx              ; anotar HRESULT en eax

lea   rcx, CLSID_BlocStatus       ; rclsid
xor   edx, edx                    ; pUnkOuter = NULL
mov   r8d, 1                      ; CLSCTX_INPROC_SERVER
lea   r9,  IID_IStatus            ; riid
lea   rax, [rsp+40h]
mov   [rsp+20h], rax              ; ppv (5.º argumento, en la pila tras el shadow space)
call  CoCreateInstance
```

Después, las llamadas a través de la vtable y el cierre:

```text
mov   rcx, [rsp+40h]              ; this = p (IStatus*)
mov   rax, [rcx]                  ; rax = vptr
lea   rdx, [rsp+48h]              ; &state
call  qword ptr [rax+18h]         ; slot 3 = 0x18 / 8 -> IStatus::GetState

mov   rcx, [rsp+40h]
mov   rax, [rcx]
lea   rdx, IID_IResettable
lea   r8,  [rsp+50h]
call  qword ptr [rax]             ; slot 0 -> QueryInterface

mov   rcx, [rsp+40h]
mov   rax, [rcx]
call  qword ptr [rax+10h]         ; slot 2 -> Release

call  CoUninitialize              ; equilibra el CoInitializeEx anterior
```

Ficha de lectura, separando qué sale del código y qué se infiere:

| Dato | Fuente | Tipo |
|---|---|---|
| El hilo pide STA (`2` = `COINIT_APARTMENTTHREADED`). | Constante en `EDX` + definición del enum. | Observable en el binario. |
| `[rax+18h]` es el slot 3. | Aritmética x64: `0x18 / 8`. | Observable. |
| El slot 3 es `GetState`. | IID pasado en `R9` + IDL propio. | Inferencia respaldada por el contrato. |
| `E_NOINTERFACE` para `IID_IResettable`. | Valor de `EAX` tras la llamada al slot 0. | Se obtiene **solo** ejecutando en el laboratorio; acá es ilustrativo. |
| `p` apunta directo a la implementación. | Vtable dentro de `BlocCom.dll`, servidor in-proc compatible con STA. | Inferencia; se confirma resolviendo el módulo de la vtable. |

Variante x86, para contraste: el mismo `GetState` se vería como `push` de `&state`, `push` de `p` (el `this`), `mov eax,[p]` y `call [eax+0Ch]`, porque cada slot ocupa 4 bytes y `__stdcall` pasa `this` en la pila. No mezcles las dos tablas al leer un binario.

## Práctica

Con un componente COM **propio** o un binario didáctico ya incluido en una VM:

1. Anotá la arquitectura del cliente (x86/x64), CLSID e IIDs documentados, y cuál interfaz obtiene el cliente.
2. Ubicá `CoInitializeEx` en cada hilo que use COM: flag pasado, HRESULT y dónde está el `CoUninitialize` correspondiente. Si no lo encontrás, decilo.
3. En el depurador, seguí una llamada a `QueryInterface`; registrá IID solicitado, HRESULT y destino de retorno.
4. Identificá la dirección de la vtable, el **módulo** al que pertenece y si el puntero es directo o un proxy. Relacioná un método con su prototipo usando la tabla slot/offset de tu arquitectura. No invoques métodos desconocidos.
5. Pedí `IID_IUnknown` desde dos interfaces del mismo objeto y compará los punteros (regla de identidad). Si los punteros de interfaz difieren, buscá el patrón de agregación o tear-off.
6. Buscá en el binario `CoCreateFreeThreadedMarshaler`, respuestas a `IID_IMarshal`, `pUnkOuter` no nulos y llamadas a la ROT. Anotá cada hallazgo como observación y su consecuencia como inferencia.
7. Dibujá el ciclo de referencias: creación, consultas, `AddRef`/`Release` y liberación final. Si no hay símbolos, marcá las inferencias.

## Entregable

Diagrama cliente → (proxy/stub si corresponde) → interfaz → implementación; tabla CLSID/IID/HRESULT; tabla slot/offset/método con la arquitectura declarada; apartamento de cada hilo y evidencia de una llamada. Separá lo observado de lo inferido; no afirmes reference count exacto si el binario no lo expone.

## Repaso

?? ¿CLSID e IID significan lo mismo?
!! No. CLSID identifica la clase; IID, una interfaz/contrato que el objeto puede ofrecer.

?? ¿Qué comunica `E_NOINTERFACE`?
!! Que el objeto consultado no implementa el IID solicitado; no prueba que la clase COM no exista.

?? ¿Por qué una vtable no basta para nombrar métodos?
!! Los slots solo son direcciones. Hace falta el IID, el contrato con su orden, la arquitectura (tamaño de slot) y la convención de llamada para asociarlos con nombres y prototipos.

?? En x64, ¿qué slot es `call [rax+18h]` y dónde estaría ese mismo slot en x86?
!! Slot 3 (`0x18 / 8`). En x86 el slot 3 está en `+0x0C` (`3 × 4`).

?? ¿Qué riesgo hay después de `Release`?
!! Si se liberó la última referencia, el objeto pudo destruirse; reutilizar el puntero sería usar una referencia inválida.

?? `CoInitializeEx` devuelve `S_FALSE`. ¿Hace falta `CoUninitialize`?
!! Sí. `S_FALSE` es éxito (COM ya estaba inicializado en ese hilo) y debe equilibrarse igual. `RPC_E_CHANGED_MODE`, en cambio, es fallo y no se equilibra.

?? ¿Por qué un hilo STA que espera con `WaitForSingleObject` puede colgar una llamada COM?
!! Porque las llamadas entrantes a objetos de una STA se entregan por la cola de mensajes de ese hilo; si no bombea mensajes, nunca llegan.

?? ¿Cómo comprobás que dos punteros de interfaz pertenecen al mismo objeto?
!! Pidiendo `IID_IUnknown` a cada uno y comparando los resultados: la regla de identidad exige el mismo valor.

?? Un breakpoint en la entrada de vtable cae en código del runtime COM/RPC y no en tu DLL. ¿Qué estás viendo?
!! Probablemente un proxy: la llamada se empaqueta y la implementación corre en otro apartamento o proceso.

?? Un objeto agrega el free-threaded marshaler. ¿Hay proxy cuando se pasa a otro apartamento del mismo proceso? ¿Y a otro proceso?
!! Dentro del proceso, no: el otro apartamento recibe el puntero directo y el objeto debe sincronizarse solo. Hacia otro proceso, sí: el FTM delega en el marshaling estándar.

?? Dos `QueryInterface` del mismo IID devuelven punteros distintos, pero `IID_IUnknown` coincide. ¿Se rompió la identidad?
!! No necesariamente. Es compatible con tear-offs o agregación; la identidad se juzga por el `IUnknown`, no por cada puntero de interfaz.

?? ¿Por qué al crear un objeto agregado hay que pedir `IID_IUnknown`?
!! Porque el externo necesita el `IUnknown` no delegante del interno para controlar su vida; las demás interfaces del interno delegan en el externo.

?? ¿Por qué buscar solo `CoCreateInstance` puede no alcanzar para encontrar cómo un cliente obtiene un objeto?
!! Porque puede obtenerlo resolviendo un moniker o consultando la ROT, que conecta con una instancia ya en ejecución.

:::{nota} Puerta optativa
Podés distinguir CLSID/IID, interpretar HRESULT (incluidos los de `CoInitializeEx`), explicar qué cambia entre STA y MTA, reconocer un proxy por el módulo de su vtable, explicar cuándo el free-threaded marshaler evita un proxy y cuándo no, reconocer agregación y tear-offs sin confundirlos con una violación de identidad, aplicar la regla de identidad y nombrar un slot de vtable con el contrato y la arquitectura correctos.
:::

:::{nota} Lo que queda fuera
La implementación de `IMarshal` propio, el formato de una referencia marshaleada (OBJREF), el detalle interno de los proxies estándar, los contextos COM+ y el catálogo COM+ (solo como recuadro), la escritura de monikers propios y WinRT no se desarrollan. El apartamento neutral solo se menciona. La lección prepara para leer evidencia COM; no es una cobertura completa de COM.
:::

## Fuentes

- Microsoft Learn: [IUnknown](https://learn.microsoft.com/en-us/windows/win32/api/unknwn/nn-unknwn-iunknown), [QueryInterface](https://learn.microsoft.com/en-us/windows/win32/com/queryinterface--navigating-in-an-object), [reglas de QueryInterface](https://learn.microsoft.com/en-us/windows/win32/com/rules-for-implementing-queryinterface), [vida y reference counting](https://learn.microsoft.com/en-us/windows/win32/learnwin32/managing-the-lifetime-of-an-object), [HRESULT](https://learn.microsoft.com/en-us/windows/win32/seccrypto/common-hresult-values).
- Microsoft Learn, hilos y apartamentos: [Initializing the COM Library](https://learn.microsoft.com/en-us/windows/win32/learnwin32/initializing-the-com-library), [CoInitializeEx](https://learn.microsoft.com/en-us/windows/win32/api/combaseapi/nf-combaseapi-coinitializeex), [Processes, Threads, and Apartments](https://learn.microsoft.com/en-us/windows/win32/com/processes--threads--and-apartments), [Accessing Interfaces Across Apartments](https://learn.microsoft.com/en-us/windows/win32/com/accessing-interfaces-across-apartments).
- Microsoft Learn, proxies y convención: [Proxy](https://learn.microsoft.com/en-us/windows/win32/com/proxy), [ProxyStubClsid32](https://learn.microsoft.com/en-us/windows/win32/com/proxystubclsid32), [x64 calling convention](https://learn.microsoft.com/en-us/cpp/build/x64-calling-convention).
- Microsoft Learn, marshaling a medida y composición: [In-Process Server Threading Issues](https://learn.microsoft.com/en-us/windows/win32/com/in-process-server-threading-issues), [CoCreateFreeThreadedMarshaler](https://learn.microsoft.com/en-us/windows/win32/api/combaseapi/nf-combaseapi-cocreatefreethreadedmarshaler), [IMarshal](https://learn.microsoft.com/en-us/windows/win32/api/objidl/nn-objidl-imarshal), [Aggregation](https://learn.microsoft.com/en-us/windows/win32/com/aggregation), [ATL COM_INTERFACE_ENTRY macros (tear-offs)](https://learn.microsoft.com/en-us/cpp/atl/reference/com-interface-entry-macros).
- Microsoft Learn, monikers y COM+: [Monikers](https://learn.microsoft.com/en-us/windows/win32/com/monikers), [IRunningObjectTable](https://learn.microsoft.com/en-us/windows/win32/api/objidl/nn-objidl-irunningobjecttable), [COM+ Application Overview](https://learn.microsoft.com/en-us/windows/win32/cossdk/com--application-overview).
- **CLS:** complemento externo a la ruta de C++ y vtables de [2.18](02-cpp-profundo.html).

:::{nota} Etiquetas
**Observado en CLS:** conceptos generales de C++ y vtables. **Conocimiento externo:** COM, apartamentos, marshaling estándar y a medida, free-threaded marshaler, agregación, tear-offs, monikers/ROT, COM+ (recuadro), reglas de `QueryInterface` y convención x64. **Ejemplo ilustrativo:** desensamblado y resultados de `BlocStatus` (patrón MSVC x64, no capturado de un binario). **Laboratorio verificado:** no; usar solo un componente propio/didáctico.
:::
