---
title: "Glosario de reversing"
description: "Términos del curso explicados en lenguaje de principiante, con enlaces a las lecciones."
---

# Glosario

Términos que aparecen en el curso, explicados en lenguaje sencillo. Donde el concepto se desarrolla en una lección, hay un enlace. No es una enciclopedia: es el vocabulario mínimo para leer las lecciones sin frenarte.

## A–C

| Término | Explicación |
|---|---|
| **ABI Itanium (C++)** | Especificación de cómo GCC, Clang y MinGW organizan vtables, RTTI, nombres (`_ZTV…`) y excepciones; cada plataforma la adapta. Distinta del modelo de MSVC. Ver [C++ profundo](guia/02-cpp-profundo.html). |
| **Address (dirección)** | Número que identifica una posición de memoria. En un debugger se escribe en hexadecimal. |
| **Adjustor thunk** | Fragmento de código en una vtable que corrige `this` (por ejemplo, `sub rcx, 10h` y un salto) antes de llegar al método real; aparece con herencia múltiple. Ver [C++ profundo](guia/02-cpp-profundo.html). |
| **AL / AH / AX** | Partes de `EAX`: `AL` es el byte bajo, `AH` el byte alto y `AX` los dos bytes bajos. Ver [registros](guia/02-registros.html). |
| **Anti-debug** | Conjunto de técnicas con las que un programa detecta que está siendo depurado. Se estudia para reconocerlo, no para evadirlo. Ver [debugger](guia/02-debugger.html). |
| **API** | Función que ofrece un sistema operativo o una biblioteca para que otro programa la use (`MessageBoxA`, `CreateFileW`). |
| **API hashing** | Técnica que localiza funciones comparando un hash de cada nombre exportado contra una constante, para no dejar el nombre de la API como cadena. Ver [PE fino](guia/02-pe-fino.html). |
| **Aplanamiento del flujo de control** | Ofuscación que pone todos los bloques de una función dentro de un bucle con un `switch` sobre una variable de estado. Ver [Ofuscación](guia/02-ofuscacion.html). |
| **Argumento** | Valor que se pasa a una función. En 32 bits suele ir en el stack; en x64, los primeros cuatro en registros. |
| **ASLR** | *Address Space Layout Randomization*: técnica que carga las imágenes en direcciones distintas en cada ejecución. Ver [PE](guia/01-pe.html). |
| **Assembly** | Representación legible de las instrucciones de la CPU. Cada línea suele ser una operación con sus operandos. |
| **Big-endian** | Orden en que el byte más significativo se guarda primero. x86/x64 usa little-endian. |
| **Binario** | Sistema de numeración en base 2, con 0 y 1. Un byte son 8 bits. Ver [números](guia/01-numeros.html). |
| **BinDiff / BinExport** | Differ de binarios de código abierto; trabaja sobre exportaciones en formato BinExport generadas desde IDA, Binary Ninja o Ghidra. Ver [Patch diffing](guia/02-patch-diffing.html). |
| **Bit** | Unidad mínima de información: 0 o 1. |
| **Breakpoint** | Pausa que se pone en el programa para observar su estado. Puede ser por software, hardware o memoria. Ver [debugger](guia/02-debugger.html). |
| **Byte** | 8 bits. Unidad básica de almacenamiento. |
| **C** | Lenguaje compilado de bajo nivel, muy usado para programas que se analizan con debuggers. |
| **C#** | Lenguaje de .NET que se compila a IL. Ver [.NET](guia/03-dotnet-runtime.html). |
| **Cadena armada en el stack** | Texto que el programa escribe de a pedazos con `mov` de constantes en vez de guardarlo en `.rdata`; no aparece en la ventana de strings. Ver [IDA](guia/02-ida.html). |
| **CALL** | Instrucción que llama a una función: empuja la dirección de retorno y salta. Ver [llamadas](guia/02-llamadas.html). |
| **Canary (stack canary)** | Valor aleatorio que el compilador coloca antes del return address para detectar desbordes. Ver [vulnerabilidades](guia/05-vulnerabilidades.html). |
| **CF (carry flag)** | Flag que indica acarreo o desborde en una operación sin signo. |
| **CMP** | Instrucción que resta dos valores, actualiza flags y descarta el resultado. Se usa antes de un salto condicional. |
| **Código administrado** | Código que corre bajo un runtime (como el CLR de .NET) que administra memoria y ejecución. |
| **Código nativo** | Código máquina específico de la CPU, generado por un compilador como C/C++. |
| **Complete Object Locator (COL)** | Estructura de RTTI de MSVC a la que apunta `vtable[-1]`; lleva al nombre de la clase. En x64 usa RVA. Ver [C++ profundo](guia/02-cpp-profundo.html). |
| **Complemento a dos** | Convención para representar negativos: se invierten los bits y se suma 1. `0xFB` = −5 en 8 bits. Ver [números](guia/01-numeros.html). |
| **Constante** | Valor fijo que no cambia durante la ejecución. En assembly aparece como inmediato (`mov eax, 50`). |
| **CPU** | Unidad central de proceso. Ejecuta instrucciones y tiene registros. |
| **Crackme** | Programa pequeño diseñado para practicar reversing, generalmente con un objetivo didáctico. |
| **CS / DS / SS** | Registros de segmento de 16 bits. En 32/64 bits casi no se usan, salvo `FS`/`GS` para estructuras del sistema. |

## D–H

| Término | Explicación |
|---|---|
| **DWORD** | Doble WORD: 4 bytes (32 bits). |
| **Debugger** | Programa que ejecuta otro paso a paso, con pausas y vista de registros y memoria. En el curso se usa x64dbg. |
| **Decompilador** | Herramienta que reconstruye una vista legible aproximada a partir de un binario o del IL. No recupera el código original exacto. |
| **Desplazamiento (displacement)** | Distancia que se suma a una dirección para calcular un destino o un campo. En un `call`/`jmp` relativo, se mide desde la instrucción siguiente. |
| **DLL** | Biblioteca de código que otros programas cargan en tiempo de ejecución (`.dll` en Windows). |
| **DR0–DR3** | Registros de depuración del procesador que sostienen breakpoints de hardware. Hay cuatro por hilo. |
| **EAX / RAX** | Registro acumulador; suele guardar el resultado de una función. |
| **EBP / RBP** | Base pointer: referencia estable del marco de pila en funciones de 32 bits. |
| **EBX / RBX** | Registro de propósito general; a veces apunta a datos. |
| **ECX / RCX** | Registro contador; se usa en bucles, shifts variables y `rep`. En x64 es el primer argumento. |
| **EDI / RDI** | Destination index: registro de destino en copias de memoria (`movs`, `stos`). |
| **EDX / RDX** | Registro de datos; parte alta en multiplicaciones/divisiones. En x64 es el segundo argumento. |
| **EIP / RIP** | Instruction pointer: dirección de la próxima instrucción a ejecutar. |
| **Entropía** | Medida de cuán aleatorios son unos bytes (0 a 8 bits por byte); cerca de 8 sugiere datos comprimidos o cifrados. Ver [Packers](guia/02-packers.html). |
| **Entry point** | Primera instrucción del código de un programa; no es necesariamente `main`. |
| **ESI / RSI** | Source index: origen en copias de memoria. |
| **ESP / RSP** | Stack pointer: apunta a la cima del stack. |
| **Excepción de primera / segunda oportunidad** | Avisos del depurador antes de buscar handlers (primera) y cuando nadie la manejó (segunda). Solo la segunda indica un fallo no manejado. Ver [2D.11](guia/2d-11-excepciones.html). |
| **Export** | Función o símbolo que una DLL ofrece a otros programas. |
| **FIFO** | *First in, first out*: lo primero que entra es lo primero que sale (una cola). |
| **Flag** | Bit de estado que resume el resultado de una operación (`ZF`, `SF`, `CF`, `OF`). Ver [registros](guia/02-registros.html). |
| **Frida** | Herramienta de instrumentación dinámica que inyecta JavaScript en un proceso para enganchar funciones (`Interceptor.attach`). Ver [Scripting de debugger](guia/02-scripting-debugger.html). |
| **Función** | Bloque de código con un nombre, parámetros y un valor de retorno. |
| **Handle** | Identificador opaco que el sistema da para referenciar un recurso (archivo, ventana, hilo). |
| **Heap** | Zona de memoria dinámica, administrada por `malloc`/`new` o por el runtime. |
| **Hexadecimal** | Base 16, con dígitos 0–9 y A–F. Cada dígito representa 4 bits. |
| **Hipervisor** | Programa que crea y administra máquinas virtuales (VirtualBox, VMware, Hyper-V). |

## I–O

| Término | Explicación |
|---|---|
| **IAT** | *Import Address Table*: tabla de punteros que el cargador completa con las direcciones de las funciones importadas. Ver [PE](guia/01-pe.html). |
| **IDA** | Desensamblador y debugger interactivo. IDA Free es la versión gratuita. Ver [IDA](guia/02-ida.html). |
| **IL / MSIL** | Lenguaje intermedio de .NET, compilado a máquina por el JIT. Ver [.NET](guia/03-dotnet-runtime.html). |
| **Image base** | Dirección preferida en la que se carga una imagen. ASLR puede cambiarla. |
| **Import** | Función o símbolo que un programa toma de una DLL. |
| **Instrucción** | Operación elemental que ejecuta la CPU (`mov`, `add`, `jmp`). |
| **JIT** | *Just-in-time compiler*: compila IL a código nativo en tiempo de ejecución. |
| **JMP** | Salto incondicional. |
| **Kernel** | Núcleo del sistema operativo, con el máximo privilegio. Fuera del alcance de esta edición. Ver [fuera de alcance](guia/05-fuera-de-alcance.html). |
| **LEA** | *Load effective address*: calcula una dirección sin leer memoria. |
| **LIFO** | *Last in, first out*: lo último que entra es lo primero que sale (una pila). |
| **Little-endian** | Orden en que el byte menos significativo se guarda primero. Es el de x86/x64. Ver [números](guia/01-numeros.html). |
| **Malware** | Software diseñado para dañar, espiar o tomar control. Se estudia de forma defensiva. Ver [malware](guia/05-malware.html). |
| **Marco de pila (stack frame)** | Región del stack de una función: argumentos, return address, `EBP` guardado y variables locales. |
| **Memoria virtual** | Espacio de direcciones que el sistema presenta a cada proceso, independiente de la memoria física. |
| **Memoria W+X** | Región o sección escribible y ejecutable a la vez; típica del stub de un packer que escribe código y después lo ejecuta. Ver [Packers](guia/02-packers.html). |
| **Metadatos** | Información sobre tipos, métodos y referencias que acompaña al IL en un ensamblado .NET. |
| **Mnemónico** | Nombre legible de una instrucción (`mov`, `add`). |
| **MOV** | Instrucción de transferencia de datos; no modifica flags. |
| **NOP** | Instrucción que no hace nada (`0x90`). Se usa para rellenar o parchear. |
| **Número mágico** | Bytes fijos al comienzo de un archivo o mensaje que identifican su formato (por ejemplo `MZ` en un PE). Ver [Método de análisis](guia/04-metodo.html). |
| **NX / DEP** | Mitigación que impide ejecutar código en páginas de datos (stack/heap). |
| **OEP** | *Original Entry Point*: punto de entrada del programa original antes de empaquetarlo; ahí se dumpea. Ver [Packers](guia/02-packers.html). |
| **Offset** | Distancia desde un punto de referencia. En un archivo, posición de un byte; en una estructura, distancia a un campo. |
| **Opcode** | Byte(s) que codifican una instrucción. |
| **Overflow (OF)** | Flag que indica desborde en una operación con signo. |

## P–S

| Término | Explicación |
|---|---|
| **pclntab** | Tabla de los binarios de Go que relaciona direcciones con funciones y líneas; el runtime la necesita, así que los nombres sobreviven sin símbolos. Ver [Huella de compilador](guia/02-huella-compilador.html). |
| **PE** | *Portable Executable*: formato de ejecutables y DLLs de Windows. Ver [PE](guia/01-pe.html). |
| **PEB** | *Process Environment Block*: estructura del sistema con información del proceso. `PEB+2` delata el debugger. |
| **PIE** | *Position Independent Executable*: código que puede cargarse en cualquier base (ELF). |
| **Pila (stack)** | Zona LIFO donde se guardan argumentos, direcciones de retorno y variables locales. |
| **Predicado opaco** | Condición cuyo resultado el ofuscador conoce de antemano (siempre verdadera o siempre falsa), disfrazada de salto condicional. Ver [Ofuscación](guia/02-ofuscacion.html). |
| **Prólogo / epílogo** | Instrucciones al inicio y al final de una función que arman y desarman el marco de pila (`push ebp; mov ebp, esp` / `mov esp, ebp; pop ebp; ret`). |
| **Proceso** | Programa en ejecución, con su espacio de direcciones, handles e hilos. |
| **QWORD** | 8 bytes (64 bits). |
| **R8–R15** | Registros adicionales de 64 bits en x86-64. |
| **Registro** | Memoria pequeña y rápida dentro del procesador. Ver [registros](guia/02-registros.html). |
| **Relocación** | Ajuste de direcciones absolutas cuando una imagen se carga en una base distinta de la preferida. |
| **RET** | Instrucción que vuelve de una función: saca el return address del stack y salta. |
| **ROP** | *Return-Oriented Programming*: encadenar fragmentos de código existente para ejecutar operaciones. Se explica conceptualmente en [vulnerabilidades](guia/05-vulnerabilidades.html). |
| **RTTI** | *Run-Time Type Information*: datos que el compilador deja para `dynamic_cast` y `typeid`; en reversing da nombres de clases. Ver [C++ profundo](guia/02-cpp-profundo.html). |
| **Sandbox** | Entorno aislado donde se ejecuta código no confiable. |
| **Sección** | Región de un binario con un propósito (`.text`, `.data`, `.rdata`). |
| **Segmento** | Región que el cargador mapea con permisos (ELF/PE). |
| **Shellcode** | Código pequeño pensado para ejecutarse desde memoria; se estudia conceptualmente, no se produce. |
| **Símbolos públicos** | Archivos de símbolos que Microsoft publica para sus binarios: nombres de funciones y globales, sin código fuente ni tipos privados. Ver [Patch diffing](guia/02-patch-diffing.html). |
| **Snapshot** | Estado guardado de una VM que permite volver atrás. |
| **SSO (Small String Optimization)** | Optimización de `std::string` que guarda cadenas cortas dentro del propio objeto, sin memoria dinámica. Ver [C++ profundo](guia/02-cpp-profundo.html). |
| **Stack** | Ver **pila**. |
| **String** | Secuencia de caracteres, generalmente terminada en `0x00` en C. |

## T–Z

| Término | Explicación |
|---|---|
| **TEB** | *Thread Environment Block*: estructura por hilo; `FS:[0x18]` apunta a ella en 32 bits. |
| **TLS** | *Thread Local Storage*: variables globales con una copia por hilo. |
| **Traza condicional** | Ejecución paso a paso automática del debugger que evalúa condiciones de corte y de log en cada instrucción. Ver [Scripting de debugger](guia/02-scripting-debugger.html). |
| **UTF-16 / funciones A y W** | Windows guarda el texto Unicode en UTF-16 (dos bytes por carácter en el caso común); las APIs de texto tienen versión `A` (página de códigos) y `W` (Unicode). Ver [IDA](guia/02-ida.html). |
| **VA (virtual address)** | Dirección en el espacio de memoria del proceso. |
| **VEH (vectored exception handler)** | Manejador de excepciones de todo el proceso, registrado con `AddVectoredExceptionHandler`, que se llama antes que los handlers por marco. Ver [2D.11](guia/2d-11-excepciones.html). |
| **Version Tracking** | Herramienta de Ghidra que empareja funciones entre dos versiones y traslada nombres y comentarios. Ver [Ghidra](guia/02-ghidra.html). |
| **VTable** | Tabla de punteros a métodos virtuales de un objeto C++. |
| **WORD** | 2 bytes (16 bits). |
| **XOR** | Operación lógica "o exclusivo": 1 si los bits son distintos. Se usa para cifrar, poner a cero y ofuscar. |
| **YARA** | Herramienta y lenguaje de reglas para detectar patrones en archivos. Ver [malware](guia/05-malware.html). |
| **ZF (zero flag)** | Flag que se activa cuando el resultado de una operación es cero. |

## Formatos y protocolos

| **Campo** | Componente de un archivo o mensaje identificado por offset, tamaño y regla de interpretación. Ver [4.5](guia/04-formatos-protocolos.html). |
| **Framing** | Regla que permite decidir dónde empieza y termina cada mensaje. En TCP la aplicación define esos límites. Ver [4.5](guia/04-formatos-protocolos.html). |
| **TLV** | Esquema Type-Length-Value: cada elemento especifica tipo, longitud y valor. Ver [4.5](guia/04-formatos-protocolos.html). |
| **Checksum / CRC** | Valor para detectar ciertas corrupciones accidentales; no equivale a MAC ni autentica al emisor. Ver [4.5](guia/04-formatos-protocolos.html). |
| **Máquina de estados** | Modelo de estados y transiciones que ayuda a interpretar mensajes según el intercambio previo. Ver [4.5](guia/04-formatos-protocolos.html). |

## Windows internals y drivers

| Término | Explicación |
|---|---|
| **Agregación (COM)** | Técnica por la que un objeto externo expone interfaces de uno interno como propias, manteniendo un único `IUnknown`. Ver [2D.6](guia/2d-06-com-interfaces.html). |
| **ALPC** | Mecanismo de mensajes locales de bajo nivel que usan componentes de Windows; poco documentado para uso general. Ver [2D.10](guia/2d-10-ipc.html). |
| **Altitud (minifilter)** | Número que fija la posición de un minifilter en la pila de archivos; Microsoft la asigna por grupo de carga. Ver [6.5](guia/6-05-minifilters.html). |
| **Apartamento (STA / MTA)** | Grupo de hilos y objetos COM que pueden llamarse directamente; entre apartamentos se usa un proxy. Ver [2D.6](guia/2d-06-com-interfaces.html). |
| **API set** | Nombre de contrato (`api-ms-win-…`) que el loader redirige a la DLL que implementa las funciones; puede no existir como archivo. Ver [PE fino](guia/02-pe-fino.html). |
| **AutoLogger** | Sesión ETW configurada en el registro que arranca al iniciar el sistema. Ver [2D.12](guia/2d-12-etw.html). |
| **CLSID / IID** | GUID que identifica, respectivamente, una clase COM y un contrato de interfaz. Ver [2D.6](guia/2d-06-com-interfaces.html). |
| **COM** | Modelo de componentes de Windows basado en interfaces y reglas de vida de objetos. Ver la rama [2D](2d.html). |
| **DPC** | *Deferred Procedure Call*: trabajo diferido que corre a `DISPATCH_LEVEL`, por ejemplo después de una interrupción. Ver [6.1](guia/6-01-arquitectura-kernel.html). |
| **ETW** | *Event Tracing for Windows*: sistema de providers, controllers y consumers para registrar eventos. Ver [2D.12](guia/2d-12-etw.html). |
| **Free-threaded marshaler (FTM)** | Objeto agregable que hace que un puntero COM pase a otro apartamento del mismo proceso sin proxy; entre procesos no evita el marshaling. Ver [2D.6](guia/2d-06-com-interfaces.html). |
| **HRESULT** | Código de resultado de APIs COM; se interpreta con reglas de éxito/fallo, no como booleano. Ver [2D.6](guia/2d-06-com-interfaces.html). |
| **IOCTL** | Código de control que una aplicación envía a un driver con `DeviceIoControl`; incluye tipo de dispositivo, función, método y acceso. Ver [6.2](guia/6-02-kmdf-ioctl.html). |
| **IRP** | Paquete que lleva una solicitud de E/S por la pila de drivers de Windows. Ver [6.1](guia/6-01-arquitectura-kernel.html). |
| **IRQL** | Nivel de prioridad del kernel que limita qué operaciones y memoria pueden usarse. Ver [6.1](guia/6-01-arquitectura-kernel.html). |
| **KMDF / UMDF** | Marcos de drivers de Windows para kernel mode y user mode. Ver [6.2](guia/6-02-kmdf-ioctl.html). |
| **LIST_ENTRY** | Estructura de lista doblemente enlazada y circular de Windows (`Flink`, `Blink`) embebida en cada elemento; se llega al elemento restando el offset del campo. Ver [IDA](guia/02-ida.html). |
| **MDL** | *Memory Descriptor List*: descripción de las páginas físicas de un buffer bloqueado; la usa el I/O directo. Ver [6.2](guia/6-02-kmdf-ioctl.html). |
| **METHOD_NEITHER** | Método de IOCTL en el que el driver recibe direcciones de user mode sin validar; se revisa como patrón de riesgo. Ver [6.4](guia/6-04-revision-driver.html). |
| **Minifilter** | Driver que se registra ante el Filter Manager para observar o modificar operaciones de archivos. Ver [6.5](guia/6-05-minifilters.html). |
| **MOF** | *Managed Object Format*: lenguaje que describe clases e instancias de WMI; se compila al repositorio con `mofcomp`. Ver [2D.9](guia/2d-09-wmi.html). |
| **Moniker / ROT** | Objeto que nombra a otro objeto COM y sabe obtenerlo; la ROT registra los objetos en ejecución con su moniker. Ver [2D.6](guia/2d-06-com-interfaces.html). |
| **Named pipe** | Canal de comunicación nombrado entre procesos, local o de red, protegido por un descriptor de seguridad. Ver [2D.10](guia/2d-10-ipc.html). |
| **ntdll / API nativa** | Capa de funciones `Nt`/`Zw` sobre la que se apoyan las APIs documentadas; sus stubs cargan el número de servicio y ejecutan `syscall`. Ver [PE fino](guia/02-pe-fino.html). |
| **Pool (paginado / no paginado / NX)** | Memoria del kernel; la no paginada se usa a cualquier IRQL y la NX no permite ejecutar código. Ver [6.1](guia/6-01-arquitectura-kernel.html). |
| **ProcessDebugPort** | Clase de información de `NtQueryInformationProcess`; un valor distinto de cero indica un debugger de modo usuario. Ver [Anti-análisis](guia/02-anti-analisis.html). |
| **Proxy / stub** | Par de objetos que empaqueta (proxy, del lado del llamador) y desempaqueta (stub, del lado del servidor) una llamada COM entre apartamentos o procesos. Ver [2D.6](guia/2d-06-com-interfaces.html). |
| **SPN** | *Service Principal Name*: identificador de una instancia de servicio que Kerberos asocia a la cuenta del servicio. Ver [2D.8](guia/2d-08-dcom-rpc.html). |
| **VAD** | Descriptor que representa un rango de direcciones virtuales de un proceso. Ver [2D.2](guia/2d-02-memoria-loader.html). |
| **VBS / HVCI** | Seguridad basada en virtualización e integridad de código protegida por hypervisor; controles relacionados, no garantías absolutas. Ver [6.6](guia/6-06-mitigaciones.html). |
| **WMI** | Infraestructura Windows de clases, proveedores y consumidores para consultar datos y eventos. Ver [2D.9](guia/2d-09-wmi.html). |
| **WQL** | Lenguaje de consultas de WMI, subconjunto de SQL con cláusulas propias para eventos (`WITHIN`, `GROUP WITHIN`). Ver [2D.9](guia/2d-09-wmi.html). |

:::{nota} ¿Falta un término?
Si una lección usa una palabra que no está acá, anotala en tu bitácora. El glosario se amplía con las dudas reales, no con definiciones que nadie usa.
:::
