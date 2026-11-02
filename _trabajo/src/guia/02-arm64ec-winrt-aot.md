---
title: "2.35 · Ecosistemas Modernos en Windows 11: ARM64EC, WinRT (IInspectable) y .NET Native AOT"
description: "Reversing de binarios híbridos ARM64EC en Windows 11, interfaz IInspectable y cadenas HSTRING en WinRT, y reversing de .NET Native AOT con JIT Hooking en clrjit.dll."
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

### .NET Native AOT
En .NET 7, 8 y versiones superiores, las aplicaciones pueden compilarse con la opción `PublishAot=true` (utilizando el compilador `ilc.exe`). En estos binarios:
- **No existe bytecode CIL (MSIL):** El archivo PE contiene exclusivamente código máquina nativo x64 en la sección `.text`. Herramientas como `dnSpy` o `ILSpy` no reconocen el binario como ensamblado administrado.
- **Estructura `__ReadyToRunHeader`:** Presenta la firma `0x00525452` (`"RTR\0"`).
- **Tablas de Tipos `MethodTable` (antes `EEType`):** Los objetos en el heap contienen en el offset `-0x08` (en x64) un puntero a su `MethodTable`. La estructura no contiene nombres en texto claro, pero agrupa punteros a funciones nativas correspondientes a los métodos de la clase.

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
