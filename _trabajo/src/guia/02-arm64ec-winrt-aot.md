---
title: "2.35 · Ecosistemas Modernos en Windows 11: ARM64EC, WinRT (IInspectable, AppContainer/LPAC) y .NET Native AOT"
description: "Reversing de binarios híbridos ARM64EC en Windows 11, interfaz IInspectable y sandboxing AppContainer/LPAC en WinRT, y reversing de .NET Native AOT (secciones .managedcode y .hydrated, MethodTable y JIT Hooking en clrjit.dll)."
etapa: "Etapa 2 · Reversing (Bloque 2E: Técnicas avanzadas e industriales)"
---

# Ecosistemas Modernos en Windows 11: ARM64EC, WinRT y .NET Native AOT

:::{nota} Propósito y Relevancia
En Windows 11 contemporáneo, los analistas de software ya no se enfrentan únicamente a ejecutables x64 estándar. El ecosistema empresarial y de consumo incorpora tres nuevas realidades técnicas: binarios híbridos **ARM64EC** (*Emulation Compatible*) para dispositivos Copilot+ y portátiles basados en ARM, APIs de sistema basadas en **Windows Runtime (WinRT / IInspectable)** con sandboxes **AppContainer / LPAC**, y binarios **.NET compilados a código nativo estricto (Native AOT)** o protegidos con cifrado de métodos en el JIT. Esta lección aporta los patrones exactos de bajo nivel para auditar estos componentes.
:::

---

## 1. Binarios Híbridos ARM64EC (*Emulation Compatible*)

Con el despliegue de procesadores Snapdragon X Elite y procesadores ARM64 en Windows 11, Microsoft desarrolló la arquitectura **ARM64EC**. Un ejecutable ARM64EC no es un binario x64 emulado por completo ni un binario ARM64 puro: es un **PE híbrido** donde funciones en código máquina x64 y funciones en código máquina ARM64 conviven dentro del mismo espacio virtual de memoria y pueden llamarse entre sí sin sobrecosto de cambio de contexto de proceso.

### Anatomía del PE ARM64EC
1. **Machine Type en FileHeader:** `IMAGE_FILE_MACHINE_ARM64` (`0xAA64`).
2. **Directorio Load Config:** El campo `CHPEMetadataPointer` apunta a `IMAGE_ARM64EC_METADATA`, que gobierna las tablas de reubicación dinámica `IMAGE_DYNAMIC_RELOCATION_ARM64EC`.
3. **Mapeo de Registros en Transiciones:**
   Cuando el emulador JIT (`xtajit64.dll`) o los thunks de transición transfieren el control entre código x64 y código ARM64, los primeros 4 argumentos de llamada se mapean directamente:

| Argumento ABI | Registro x64 | Registro ARM64 | Propósito |
| :--- | :---: | :---: | :--- |
| **1º Parámetro** | `RCX` | `X0` | Puntero a objeto / Primer argumento entero o puntero |
| **2º Parámetro** | `RDX` | `X1` | Segundo argumento entero o puntero |
| **3º Parámetro** | `R8` | `X2` | Tercer argumento entero |
| **4º Parámetro** | `R9` | `X3` | Cuarto argumento entero |
| **Puntero de Pila** | `RSP` | `SP` | Alineación estricta a 16 bytes |

### Entry y Exit Thunks (`$$h`)
Cuando una función x64 llama a una función ARM64 nativa, la invocación no salta directamente a la rutina destino: salta a un **Entry Thunk** (identificado con el prefijo o símbolo `$$h` o `#entry_thunk`). Este stub de 8 a 16 bytes salva el estado del contexto de emulación x64, reajusta la pila y salta al código ARM64 nativo en `X16` / `X17`. Para el analista en IDA Pro o Ghidra, reconocer estos thunks evita interpretar el código de ajuste de ABI como lógica de ofuscación.

---

## 2. Windows Runtime (WinRT) y la Interfaz `IInspectable`

Las aplicaciones modernas de Windows 11, los servicios del sistema y los componentes empaquetados (MSIX) implementan **WinRT**, una evolución orientada a objetos de COM clásico. A diferencia de las interfaces COM estándar que heredan únicamente de `IUnknown` (3 slots de vtable), toda interfaz WinRT debe heredar obligatoriamente de **`IInspectable`**, la cual añade 3 métodos fundamentales en los slots 3, 4 y 5:

### Layout de la Vtable de `IInspectable` en x64:
- **`+0x00` (Slot 0):** `QueryInterface(REFIID riid, void** ppv)`
- **`+0x08` (Slot 1):** `AddRef()`
- **`+0x10` (Slot 2):** `Release()`
- **`+0x18` (Slot 3):** `GetIids(ULONG* iidCount, IID** iids)` &rarr; Enumera las interfaces implementadas.
- **`+0x20` (Slot 4):** `GetRuntimeClassName(HSTRING* className)` &rarr; Devuelve el nombre calificado de la clase en WinRT (ej. `"Windows.Storage.StorageFile"`).
- **`+0x28` (Slot 5):** `GetTrustLevel(TrustLevel* trustLevel)` &rarr; Informa el nivel de confianza (BaseTrust, PartialTrust, FullTrust).
- **`+0x30+` (Slot 6 en adelante):** Métodos propios de la interfaz concreta.

### Manejo de Cadenas Inmutables `HSTRING`
En WinRT, las cadenas de texto no son punteros crudos `wchar_t*` terminados en nulo, sino handles opacos de tipo `HSTRING`. Internamente, una cadena rápida de solo lectura se define mediante una cabecera `HSTRING_HEADER` de 24 bytes en x64:

```text
HSTRING_HEADER (24 bytes en x64):
+0x00: PVOID Reserved1;        // Flags internos (0x01 = Fast-pass / Buffer no asignado en heap)
+0x08: ULONG Length;           // Longitud de la cadena en caracteres UTF-16
+0x0C: ULONG Reserved2;        // Relleno de alineación
+0x10: PCWSTR StringRef;       // Puntero directo al buffer de caracteres UTF-16
```

Para activar una clase en WinRT, el binario invoca `combase.dll!RoActivateInstance` pasando el `HSTRING` del nombre de clase y recibiendo un puntero a `IInspectable`.

### Sandboxing Moderno: AppContainer y LPAC con Capacidades SID

Los procesos protegidos en Windows 11 (aplicaciones MSIX, procesos de pestañas de navegadores, servicios de sistema aislados) ya no confían únicamente en el modelo clásico de niveles de integridad de Windows Vista (Low/Medium/High). En su lugar, el kernel de Windows confina el proceso dentro de un **AppContainer** o un **LPAC** (*Less Privileged AppContainer*).

#### Anatomía Interna del Token de AppContainer
En el espacio de kernel, la estructura `_TOKEN` (`nt!_TOKEN`) contiene campos específicos que definen el aislamiento del contenedor:

1. **`TokenIsAppContainer` (`TOKEN_INFORMATION_CLASS = 29`):** Booleano que indica si el token está restringido por sandbox.
2. **`TokenAppContainerSid` (`TOKEN_INFORMATION_CLASS = 31`):** Retorna el SID de paquete exclusivo (`S-1-15-2-...`) asignado a la aplicación.
3. **`TokenCapabilities` (`TOKEN_INFORMATION_CLASS = 30`):** Apunta a una estructura `TOKEN_GROUPS` que contiene el arreglo de SIDs de permisos o *Capabilities* asignados explícitamente (`SID_AND_ATTRIBUTES` con atributos `SE_GROUP_ENABLED`).

```text
Estructura de Seguridad del Token en WinDbg:
dt nt!_TOKEN <Direccion_Token>
   +0x0a0 UserAndGroups    : Ptr64 _SID_AND_ATTRIBUTES
   +0x100 RestrictedSids   : Ptr64 _SID_AND_ATTRIBUTES
   +0x118 Capabilities     : Ptr64 _SID_AND_ATTRIBUTES  <--- Arreglo de SIDs de permisos
   +0x120 TokenFlags       : Uint4                      <--- Bit 0x20 activo en LPAC
```

#### SIDs de Capacidades Conocidos (Well-Known Capability SIDs)
En ingeniería inversa de aplicaciones UWP/WinRT y binarios empaquetados, el analista debe contrastar los SIDs del token contra la tabla de permisos del manifiesto `AppxManifest.xml`:

| SID de Capacidad | Identificador Declarativo | Privilegio Otorgado al Proceso |
| :--- | :--- | :--- |
| `S-1-15-3-1` | `internetClient` | Acceso a conexiones de red salientes hacia Internet. |
| `S-1-15-3-2` | `internetClientServer` | Servidor y cliente en redes públicas (abrir puertos de escucha). |
| `S-1-15-3-3` | `privateNetworkClientServer` | Comunicación entrante/saliente en redes domésticas o corporativas. |
| `S-1-15-3-4` | `picturesLibrary` | Acceso al directorio de imágenes del usuario. |
| `S-1-15-3-5` | `videosLibrary` | Acceso al directorio de videos del usuario. |
| `S-1-15-3-7` | `documentsLibrary` | Acceso al almacén general de documentos (restringido). |

#### Diferencia Crítica: AppContainer Estándar vs. LPAC
- **AppContainer Estándar:** El proceso tiene denegado el acceso a la mayor parte del sistema de archivos y registro, pero **conserva acceso de lectura implícito** a objetos que tengan en su lista de control de acceso discrecional (DACL) el SID de grupo bien conocido `ALL APPLICATION PACKAGES` (`S-1-15-2-1`).
- **LPAC (Less Privileged AppContainer):** Diseñado para componentes con alto riesgo de explotación (como los motores de renderizado de Edge o WebView2). Un token LPAC posee activo el flag `0x20` en `TokenFlags`. Para un LPAC, el kernel **ignora el SID `ALL APPLICATION PACKAGES`**: solo permite acceder a recursos que tengan explícitamente concedido el SID `ALL RESTRICTED APPLICATION PACKAGES` (`S-1-15-2-2`) y los SIDs de capacidades específicos declarados en su lista.

#### Auditoría Dinámica del Token
Para inspeccionar las capacidades de un proceso desde WinDbg:
```text
!process <PID> 1
!token <TokenAddress>
dt nt!_TOKEN <TokenAddress> Capabilities
```
En modo usuario, la función `GetTokenInformation` con la clase `TokenCapabilities` devuelve el listado completo de SIDs para comprobar si un proceso confinado intenta eludir sus fronteras de red o almacenamiento.

---

## 3. Reversing de .NET Native AOT y JIT Hooking por Método

### .NET Native AOT: Anatomía Binaria y Secciones
En .NET 7, 8 y 9+, las aplicaciones pueden compilarse con la opción `PublishAot=true` (utilizando el compilador ahead-of-time `ilc.exe`). En estos binarios:
- **No existe bytecode CIL (MSIL) ni metadatos ECMA-335 clásicos:** El archivo PE carece de streams `#Strings`, `#Blob`, `#GUID` o `#~`. Decompiladores tradicionales como `dnSpy` o `ILSpy` fallan o muestran el archivo como un binario nativo x64 estándar.
- **Sección `.managedcode`:** Sección PE con permisos de ejecución y lectura (`IMAGE_SCN_MEM_EXECUTE | IMAGE_SCN_MEM_READ`) donde `ilc.exe` aloja todas las rutinas compiladas en código máquina x64 nativo tanto para la lógica de la aplicación como para la biblioteca base (BCL / CoreLib). Las funciones carecen de nombres exportados y se invocan indirectamente a través de celdas de despacho de interfaz (*Interface Dispatch Cells*).
- **Sección `.hydrated` / `.rdata`:** Sección de solo lectura donde el compilador ubica las estructuras estáticas del runtime y los datos iniciales precomputados. Al cargar el binario, el runtime de Native AOT no parsea metadatos; "hidrata" directamente las estructuras de tipos (`MethodTable`) desde esta sección hacia la memoria virtual.

### Reconstrucción del Árbol de Tipos (`MethodTable` / `EEType`) sin Metadatos ECMA-335
Cada objeto administrado en el heap contiene en el offset **`-0x08`** (en arquitecturas x64) un puntero a su descriptor de tipo: la estructura **`MethodTable`** (históricamente denominada `EEType`):

| Offset (x64) | Campo en `MethodTable` | Tipo | Significado para el Reverser |
| :--- | :--- | :--- | :--- |
| **`+0x00`** | `Flags` | `UInt16` | Banderas que clasifican el tipo: clase, interfaz, struct de valor, array o genérico. |
| **`+0x02`** | `BaseSize` | `UInt16` | Tamaño físico en bytes que ocupa una instancia del tipo en el heap administrado. |
| **`+0x08`** | `RelatedType` | `Ptr64 MethodTable` | **Puntero a la clase base.** Permite reconstruir programáticamente el árbol jerárquico de herencia. |
| **`+0x10`** | `NumVtableSlots` | `UInt16` | Cantidad de funciones virtuales contenidas en la vtable. |
| **`+0x18`** | `VTable[0..N-1]` | Arreglo de punteros | Punteros directos a las funciones en código máquina x64 dentro de la sección `.managedcode`. |

Siguiendo recursivamente el puntero `RelatedType` desde cualquier instancia, un script en Python para IDA Pro o Ghidra puede reconstruir el grafo completo de clases del ejecutable sin depender de símbolos PDB ni de metadatos administrados.

### JIT Unpacking por Método con Frida (`dump_cil_jit.js`)
Cuando un protector .NET avanzado cifra el código CIL método por método (de modo que volcar `Assembly.Load(byte[])` devuelve métodos vacíos), el único punto de convergencia es el propio compilador JIT del runtime de .NET (`clrjit.dll`).

Justo antes de que un método sea compilado a ensamblador x64, el JIT recibe una estructura `CORINFO_METHOD_INFO` donde el bytecode CIL original se encuentra descifrado en memoria viva. Interceptando `compileMethod` con el script `plantillas_codigo/dump_cil_jit.js`:

```javascript
// Localizar el slot 0 de la vtable de CILJit
const clrjit = Process.getModuleByName("clrjit.dll");
const getJit = new NativeFunction(clrjit.getExportByName("getJit"), "pointer", []);
const compileMethodPtr = getJit().readPointer().readPointer();

Interceptor.attach(compileMethodPtr, {
    onEnter(args) {
        const info = args[1]; // RDX = CORINFO_METHOD_INFO*
        const ilCodePtr = info.add(0x10).readPointer();  // +0x10: Puntero al bytecode CIL en claro
        const ilCodeSize = info.add(0x18).readU32();      // +0x18: Tamaño del método en bytes
        if (ilCodeSize > 0) {
            console.log(`[JIT Dump] Método: ${info.readPointer()} | Tam: ${ilCodeSize} bytes`);
            console.log(hexdump(ilCodePtr, { length: ilCodeSize }));
        }
    }
});
```

Este procedimiento garantiza la extracción del bytecode original de cualquier método administrado sin importar el grado de empaquetado del cargador.

---

## 2.35.b — Análisis de Binarios Híbridos ARM64EC en IDA / Ghidra

La adopción de portátiles basados en ARM (Copilot+ PCs con Windows 11) consolidó la arquitectura **ARM64EC** (*Emulation Compatible*). Un analista de ingeniería inversa se encuentra frecuentemente con binarios de sistema o aplicaciones comerciales donde coexisten código x64 y ARM64 en el mismo espacio de direcciones. Comprender cómo operan los *thunks* de adaptación y cómo configurar los desensambladores es indispensable para auditar este software moderno.

### Mecánica de Thunking y el Emulador JIT (`xtajit64.dll`)
Cuando una función en código nativo ARM64 necesita invocar una función compilada en x64 (o viceversa), el sistema no realiza una costosa conmutación de arquitectura completa; en su lugar, atraviesa un **Thunk** generado por el compilador o provisto por el runtime de emulación:

1. **Entry Thunk (x64 $\to$ ARM64EC):**
   - Se ejecuta cuando una biblioteca x64 invoca una rutina compilada en ARM64EC.
   - Toma los argumentos pasados en registros x64 (`RCX`, `RDX`, `R8`, `R9`) y los mueve a los registros nativos ARM64 (`X0`, `X1`, `X2`, `X3`), preservando la pila y ajustando la convención de llamadas.
2. **Exit Thunk (ARM64EC $\to$ x64):**
   - Se ejecuta cuando una función ARM64EC llama a una API de Windows o biblioteca que solo existe en formato x64 emulado.
   - Invoca al emulador JIT en espacio de usuario **`xtajit64.dll`** (en `%SystemRoot%\System32\xtajit64.dll`).
   - El thunk almacena el contexto de registros en una estructura de transición y transfiere el control a la rutina de traducción JIT de `xtajit64`.

### Cabeceras PE y la Tabla `IMAGE_DYNAMIC_RELOCATION_ARM64EC`
En el formato PE de un binario ARM64EC:
- `FileHeader.Machine` se identifica como `IMAGE_FILE_MACHINE_ARM64` (`0xAA64`) o `IMAGE_FILE_MACHINE_ARM64EC` (`0xA641`).
- En el directorio de configuración de carga (`IMAGE_LOAD_CONFIG_DIRECTORY64`), el campo **`DynamicValueRelocTable`** apunta a una sección especial de relocalizaciones dinámicas que contiene la tabla **`IMAGE_DYNAMIC_RELOCATION_ARM64EC`**.
- Esta tabla contiene el mapa de **`FastForwardSequence`**: arreglos de punteros indirectos que permiten al cargador de Windows sustituir en caliente los punteros a funciones x64 por punteros directos a funciones ARM64EC nativas en tiempo de carga, eliminando el overhead de emulación.

### Desensamblado de un Salto Híbrido (Thunk de Transición)
En el desensamblado de IDA Pro o Ghidra, un salto de transición entre mundos x64 y ARM64 se reconoce por el uso de patrones de trampolín hacia el dispatcher de emulación:

```asm
; =========================================================================
; Desensamblado ARM64EC: Thunk de Salida hacia x64 (Exit Thunk)
; =========================================================================
.text:0000000180012A00  ADRP    X16, #qword_180045000 ; Carga la dirección del puntero x64
.text:0000000180012A04  LDR     X16, [X16, #0x120]    ; Desreferencia el target emulado
.text:0000000180012A08  BR      X16                   ; Salta al intermediario de xtajit64.dll

; =========================================================================
; En el destino emulado (x64):
; El emulador xtajit64 traduce las instrucciones x64 sobre la marcha
; =========================================================================
00007FF780034000  48 89 5C 24 08      mov     [rsp+8], rbx
00007FF780034005  48 83 EC 20         sub     rsp, 20h
```

### Configuración de Triage en IDA Pro y Ghidra
1. **En IDA Pro:**
   - Al cargar el archivo PE, IDA detecta la presencia de metadatos CHPE (*Combined Hexagon/PE* o ARM64EC) en el Load Config.
   - Si una función x64 aparece desensamblada como bytes inválidos en ARM64, se puede pulsar **`Alt+F7`** o presionar `Edit` $\to$ `Segments` $\to$ `Edit Segment` y cambiar el procesador predeterminado del segmento de código a `metapc` (x64) o `arm64`.
   - Utilizar el plugin oficial de soporte ARM64EC de IDA (versiones 8.3+) para que IDA resuelva automáticamente los *Entry/Exit Thunks* mostrando anotaciones cruzadas (`__x64_thunk_to_arm64ec`).
2. **En Ghidra:**
   - Crear el proyecto seleccionando el procesador **`AARCH64:LE:64:v8A`**.
   - Habilitar el analizador de cabeceras PE y marcar la opción de detección de metadatos `IMAGE_ARM64EC_METADATA`.
   - Para bloques de código emulados x64 dentro de la misma imagen, marcar el rango de bytes en el *Listing*, hacer clic derecho $\to$ *Disassemble (x86:64)* para forzar el desensamblado dual en la misma base de datos.
