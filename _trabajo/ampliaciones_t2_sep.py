# Definiciones de las 6 Ampliaciones Técnicas para el Tomo II (Kernel y Windows Internals)
# y las 2 Hojas Nuevas para la Separata de Escritorio (Hojas 4 y 5)
# Revisión 5.4 — Versión Enriquecida al 100% (con tablas, RpcView/IDAPython, Flags, WdfVersionBind)

AMPLIACION_6_04_DISPATCH_ROUTINES = """<aside class="ampliacion-ext">
<p class="callout-titulo">Ampliación editorial basada en fuentes externas — Localización estática de Dispatch Routines (WDM vs. KMDF) en IDA y Ghidra</p>
<p>Al abrir un driver <code>.sys</code> sin símbolos en IDA Pro o Ghidra, la ausencia de una función <code>main</code> clásica desorienta al analista; la clave operativa para encontrar el manejador de IOCTLs radica en rastrear cómo el punto de entrada <code>DriverEntry(PDRIVER_OBJECT DriverObject, PUNICODE_STRING RegistryPath)</code> —donde <code>DriverObject</code> se recibe en <code>RCX</code> (x64) o <code>[esp+4]</code> (x86)— inicializa sus tablas de despacho (Microsoft Learn: <em>DRIVER_OBJECT</em> y <em>WDF_IO_QUEUE_CONFIG</em>) <em>(Hecho confirmado)</em>:</p>
<ul>
<li><strong>Drivers WDM clásicos (<code>MajorFunction</code>):</strong> El código escribe los punteros a sus rutinas directamente sobre el arreglo <code>DriverObject->MajorFunction</code> (offset <code>+0x70</code> en x64; <code>+0x38</code> en x86). Los desplazamientos clave en x64 son:
  <ul>
    <li><code>DriverUnload</code>: <code>[rcx + 0x68]</code> (<code>+0x34</code> en x86).</li>
    <li><code>IRP_MJ_CREATE (0x00)</code>: <code>[rcx + 0x70]</code> (<code>0x70 + 0 * 8</code>).</li>
    <li><code>IRP_MJ_CLOSE (0x02)</code>: <code>[rcx + 0x80]</code> (<code>0x70 + 2 * 8</code>).</li>
    <li><code>IRP_MJ_DEVICE_CONTROL (0x0E = 14)</code>: <strong><code>[rcx + 0xE0]</code></strong> (<code>0x70 + 14 * 8</code>; en x86 es <code>[reg + 0x70]</code>). En el desensamblado se reconoce típicamente por una instrucción como:
      <pre><code>mov qword ptr [rcx + 0xE0], sub_DispatchIoctl  ; Enlaza el procesador de DeviceControl</code></pre>
    </li>
  </ul>
</li>
<li><strong>Drivers KMDF (<code>EvtIoDeviceControl</code>):</strong> <code>DriverEntry</code> no puebla <code>MajorFunction</code> manualmente; en su lugar, inicializa la estructura <code>WDF_DRIVER_CONFIG</code> colocando el puntero a <code>EvtDriverDeviceAdd</code> en el offset <strong><code>+0x08</code></strong> (x64), enlaza el runtime con <strong><code>WdfVersionBind</code></strong> e invoca <code>WdfDriverCreate</code> (vía tabla global <code>WdfFunctions</code>). Posteriormente, dentro de <code>EvtDriverDeviceAdd</code>, se busca la inicialización de <code>WDF_IO_QUEUE_CONFIG</code> (96 bytes en x64), donde el puntero a <strong><code>EvtIoDeviceControl</code></strong> se almacena en el offset <strong><code>+0x28</code></strong> antes de invocar a <code>WdfIoQueueCreate</code>.</li>
</ul>
</aside>"""

AMPLIACION_6_05_MINIFILTERS_CALLBACKS = """<aside class="ampliacion-ext">
<p class="callout-titulo">Ampliación editorial basada en fuentes externas — Estructuras FLT_REGISTRATION y callbacks de monitoreo en Kernel</p>
<p>Al auditar en IDA o Ghidra drivers defensivos, EDRs o módulos de filtrado de archivos sin símbolos, el reverser necesita identificar de inmediato qué operaciones y eventos del sistema están siendo interceptados (Microsoft Learn: <em>FLT_REGISTRATION</em> y <em>ObRegisterCallbacks</em>) <em>(Hecho confirmado)</em>:</p>

<p><strong>1. Minifiltros de Filesystem (<code>FltRegisterFilter</code>):</strong> El segundo argumento (<code>RDX</code> en x64) apunta a la estructura estática <code>FLT_REGISTRATION</code> en <code>.rdata</code> / <code>.data</code>. Su campo <strong><code>OperationRegistration</code></strong> (offset <strong><code>+0x20</code></strong> en x64) apunta a un arreglo de estructuras <code>FLT_OPERATION_REGISTRATION</code> de 32 bytes cada una:</p>
<div class="tabla"><table>
<thead><tr><th>Offset (x64)</th><th>Campo</th><th>Tipo y Significado</th></tr></thead>
<tbody>
<tr><td><strong><code>+0x00</code></strong></td><td><code>MajorFunction</code></td><td><code>UCHAR</code> (ej. <code>0x00</code> = <code>IRP_MJ_CREATE</code>, <code>0x04</code> = <code>IRP_MJ_WRITE</code>; termina con <code>0x80</code> = <code>IRP_MJ_OPERATION_END</code>).</td></tr>
<tr><td><strong><code>+0x04</code></strong></td><td><code>Flags</code></td><td><code>ULONG</code> (banderas de operación, ej. <code>FLTFL_OPERATION_REGISTRATION_SKIP_CACHED_IO</code>).</td></tr>
<tr><td><strong><code>+0x08</code></strong></td><td><code>PreOperation</code></td><td><code>PFLT_PRE_OPERATION_CALLBACK</code> (puntero a la rutina previa a la E/S).</td></tr>
<tr><td><strong><code>+0x10</code></strong></td><td><code>PostOperation</code></td><td><code>PFLT_POST_OPERATION_CALLBACK</code> (puntero a la rutina posterior a la E/S).</td></tr>
<tr><td><strong><code>+0x18</code></strong></td><td><code>Reserved1</code></td><td><code>PVOID</code> (reservado para el sistema, completa los 32 bytes de la estructura).</td></tr>
</tbody></table></div>

<p><strong>2. Callbacks de Kernel no relacionados con Filesystem (Telemetría y Protección):</strong></p>
<div class="tabla"><table>
<thead><tr><th>API de Registro</th><th>Estructura / Parámetro Clave</th><th>Propósito Defensivo / Intercepción</th></tr></thead>
<tbody>
<tr><td><strong><code>PsSetCreateProcessNotifyRoutineEx</code></strong></td><td><code>NotifyRoutine</code> (1.er arg, <code>RCX</code>)</td><td>Notifica creación y terminación de procesos en el sistema; permite denegar la creación retornando error en <code>CreateInfo->CreationStatus</code>.</td></tr>
<tr><td><strong><code>PsSetLoadImageNotifyRoutine</code></strong></td><td><code>NotifyRoutine</code> (1.er arg, <code>RCX</code>)</td><td>Intercepta cada mapeo de ejecutables (<code>.exe</code>), bibliotecas (<code>.dll</code>) o módulos de kernel (<code>.sys</code>) en el espacio de memoria virtual.</td></tr>
<tr><td><strong><code>ObRegisterCallbacks</code></strong></td><td><code>OB_CALLBACK_REGISTRATION</code> &rarr; arreglo <code>OB_OPERATION_REGISTRATION</code> (<code>+0x20</code>)</td><td>Intercepta apertura y duplicación de handles sobre <code>PsProcessType</code> y <code>PsThreadType</code>, despojando máscaras de acceso críticas como <code>PROCESS_VM_WRITE</code> o <code>PROCESS_TERMINATE</code> para blindar procesos.</td></tr>
</tbody></table></div>
</aside>"""

AMPLIACION_2D_01_EPROCESS_TOKEN = """<aside class="ampliacion-ext">
<p class="callout-titulo">Ampliación editorial basada en fuentes externas — Inspección de _EPROCESS, _EX_FAST_REF y máscaras de privilegios en _TOKEN con WinDbg</p>
<p>Al analizar privilegios y niveles de integridad desde el depurador de kernel, las herramientas administrativas de user-mode (como Process Explorer) no bastan; el analista debe inspeccionar directamente las estructuras del ejecutivo en memoria (Microsoft Learn: <em>!process</em>, <em>!token</em> y símbolos públicos de <code>ntoskrnl.exe</code>) <em>(Hecho confirmado)</em>:</p>
<pre><code>kd&gt; !process 0 0 BlocLab.exe                ; Obtiene la dirección de _EPROCESS
kd&gt; dt nt!_EPROCESS &lt;dir_eprocess&gt; UniqueProcessId ActiveProcessLinks Token Protection</code></pre>
<ul>
<li><strong>Puntero <code>Token</code> (<code>_EX_FAST_REF</code>):</strong> En x64, los 4 bits menos significativos del campo <code>Token</code> almacenan un contador de referencias rápidas. Para obtener la dirección virtual real de la estructura <code>_TOKEN</code> se debe aplicar la máscara <strong><code>Token &amp; ~0xF</code></strong> (poniendo en <code>0</code> el último dígito hexadecimal).</li>
<li><strong>Máscaras de 64 bits en <code>_SEP_TOKEN_PRIVILEGES</code> (<code>dt nt!_TOKEN &lt;dir_token&gt; Privileges</code>):</strong> En lugar de recorrer listas de privilegios, el kernel ubica en el offset <code>+0x40</code> de <code>_TOKEN</code> tres campos <code>QWORD</code> contiguos: <code>Present</code>, <code>Enabled</code> y <code>EnabledByDefault</code>. Cada privilegio corresponde a un bit fijo (p. ej., <code>SeDebugPrivilege</code> es el bit 20 = <code>0x100000</code>), permitiendo verificar privilegios activos mediante una única instrucción bit a bit (<code>bt</code> / <code>test</code>).</li>
<li><strong>Nivel de protección (<code>PS_PROTECTION</code>):</strong> Un byte que codifica <code>Type</code> (bits 0..2: <code>0</code> = ninguno, <code>1</code> = <code>ProtectedLight</code> / PPL, <code>2</code> = <code>Protected</code>) y <code>Signer</code> (bits 4..7: <code>WinTcb</code>, <code>Antimalware</code>, <code>Lsa</code>), determinando si el proceso puede ser accedido desde user-mode.</li>
</ul>
</aside>"""

AMPLIACION_2D_10_RPC_INTERFACE = """<aside class="ampliacion-ext">
<p class="callout-titulo">Ampliación editorial basada en fuentes externas — Reconstrucción estática de interfaces RPC (RPC_SERVER_INTERFACE y MIDL_SERVER_INFO)</p>
<p>Cuando un binario registra un servidor RPC mediante <code>RpcServerRegisterIf</code> / <code>RpcServerRegisterIf2</code> / <code>RpcServerRegisterIfEx</code>, IDA Pro o Ghidra no resuelven por defecto la relación entre números de procedimiento (opcodes RPC) y funciones C. El primer argumento (<code>IfSpec</code>, registro <code>RCX</code> en x64) apunta a la estructura <code>RPC_SERVER_INTERFACE</code> en <code>.rdata</code> o <code>.data</code> generada por el compilador MIDL (<code>rpcndr.h</code> del Windows SDK) <em>(Hecho confirmado)</em>:</p>
<div class="tabla"><table>
<thead><tr><th>Offset (x64)</th><th>Campo en <code>RPC_SERVER_INTERFACE</code></th><th>Tipo y Significado en IDA / Ghidra</th></tr></thead>
<tbody>
<tr><td><strong><code>+0x04</code></strong></td><td><code>InterfaceId</code></td><td><code>RPC_SYNTAX_IDENTIFIER</code> (20 bytes: <code>GUID</code> de 16 bytes de la interfaz RPC + <code>MajorVersion</code> de 2B + <code>MinorVersion</code> de 2B).</td></tr>
<tr><td><strong><code>+0x30</code></strong></td><td><code>DispatchTable</code></td><td><code>PRPC_DISPATCH_TABLE</code>: cantidad de funciones (<code>DispatchTableCount</code>) y puntero al despachador NDR (<code>NdrServerCall2</code> / <code>NdrServerCallAll</code>).</td></tr>
<tr><td><strong><code>+0x50</code></strong></td><td><code>InterpreterInfo</code></td><td><code>const void*</code> que apunta a <code>MIDL_SERVER_INFO</code>: metadatos de decompilación del servidor.</td></tr>
</tbody></table></div>
<p>Siguiendo el puntero <strong><code>InterpreterInfo</code></strong> hacia la estructura <strong><code>MIDL_SERVER_INFO</code></strong>:</p>
<ul>
<li>En <strong><code>+0x00</code></strong> (<code>pStubDesc</code>) reside el descriptor de tipos y sintaxis NDR.</li>
<li>En <strong><code>+0x08</code></strong> (<strong><code>DispatchTable</code></strong>) reside el <strong>arreglo directo de punteros a las funciones C reales del servidor</strong> (<code>ServerRoutineTable[0..N-1]</code>). Navegar a esta dirección revela inmediatamente la lista completa de procedimientos remotos expuestos por el binario.</li>
</ul>
<p><strong>Automatización práctica:</strong> En análisis defensivo o auditoría de servicios de Windows, herramientas de código abierto como <strong><code>RpcView</code></strong> o un script de <strong>IDAPython</strong> que automatice la navegación <code>InterfaceId &rarr; InterpreterInfo &rarr; DispatchTable</code> permiten extraer y tipar todas las rutinas del servidor RPC en cuestión de segundos.</p>
</aside>"""

AMPLIACION_2D_11_UNWIND_PDATA = """<aside class="ampliacion-ext">
<p class="callout-titulo">Ampliación editorial basada en fuentes externas — Layout binario de RUNTIME_FUNCTION (.pdata) y UNWIND_INFO (.xdata) en x64</p>
<p>A diferencia de x86 (donde la lista SEH se enlaza en la pila mediante <code>FS:[0]</code>), en Windows x64 el desenrollado de pila y el despacho de excepciones se rigen por tablas estáticas en el PE sin tocar la pila en el prólogo (Microsoft Learn: <em>x64 exception handling</em>) <em>(Hecho confirmado)</em>:</p>

<div class="tabla"><table>
<thead><tr><th>Estructura y Sección</th><th>Offset / Tamaño</th><th>Campos Binarios y Significado</th></tr></thead>
<tbody>
<tr>
<td><strong><code>RUNTIME_FUNCTION</code></strong><br>(Sección <code>.pdata</code>)</td>
<td><code>12 bytes</code> fijos por función</td>
<td>
  &bull; <code>+0x00</code>: <code>DWORD BeginAddress</code> (RVA de inicio de la función).<br>
  &bull; <code>+0x04</code>: <code>DWORD EndAddress</code> (RVA de fin de la función).<br>
  &bull; <code>+0x08</code>: <code>DWORD UnwindInfoAddress</code> (RVA que apunta a la cabecera en <code>.xdata</code>).
</td>
</tr>
<tr>
<td><strong><code>UNWIND_INFO</code></strong><br>(Sección <code>.xdata</code>)</td>
<td><code>4 bytes</code> cabecera + array variable</td>
<td>
  &bull; <code>+0x00</code>: <code>Version : 3</code> (bits 0..2, vale 1 o 2) y <code>Flags : 5</code> (bits 3..7: <code>0x01 = UNW_FLAG_EHANDLER</code>, <code>0x02 = UNW_FLAG_UHANDLER</code>, <code>0x04 = UNW_FLAG_CHAININFO</code>).<br>
  &bull; <code>+0x01</code>: <code>UBYTE SizeOfProlog</code> (longitud en bytes del prólogo).<br>
  &bull; <code>+0x02</code>: <code>UBYTE CountOfCodes</code> (cantidad de slots de 2 bytes en <code>UnwindCode[]</code>).<br>
  &bull; <code>+0x03</code>: <code>UBYTE FrameRegisterAndOffset</code> (registro base y desplazamiento de marco).<br>
  &bull; <code>+0x04</code>: Arreglo <code>UNWIND_CODE[]</code> (códigos como <code>UWOP_PUSH_NONVOL=0</code>, <code>UWOP_ALLOC_SMALL=2</code> indicando qué registros se salvaron y cuánto creció <code>RSP</code>).<br>
  &bull; <strong>Tras <code>UnwindCode[]</code></strong> (alineado a 4B): Si <code>Flags &amp; 0x03</code>, sigue la <strong>RVA de 32 bits de <code>ExceptionHandler</code></strong> (<code>__C_specific_handler</code>, <code>__CxxFrameHandler3</code> o <code>__CxxFrameHandler4</code>) y los datos de excepción (<code>SCOPE_TABLE</code> / <code>FuncInfo</code>).
</td>
</tr>
</tbody></table></div>

<p><strong>Inspección en vivo con WinDbg:</strong> El comando <code>!fnent &lt;dirección_de_función&gt;</code> decodifica en vivo tanto la entrada <code>RUNTIME_FUNCTION</code> como todos los códigos <code>UNWIND_CODE</code> de <code>.xdata</code>, siendo fundamental para validar si una dirección de retorno en la pila fue falsificada (Call Stack Spoofing).</p>
</aside>"""

AMPLIACION_2D_12_ETW_PATCHING = """<aside class="ampliacion-ext">
<p class="callout-titulo">Ampliación editorial basada en fuentes externas — Extracción estática del Provider GUID (EventRegister) y detección de ETW Patching</p>
<p>Al analizar un binario en IDA o Ghidra que interactúa con ETW, existen dos patrones opuestos: la telemetría legítima instrumentada por el desarrollador y el intento de malware de cegar la monitorización del sistema (Microsoft Learn: <em>EventRegister</em> y <em>EtwEventWrite</em>) <em>(Hecho confirmado)</em>:</p>
<ol>
<li><strong>Localización del Provider GUID en aplicaciones legítimas o instrumentadas:</strong><br>
Al buscar referencias cruzadas a <code>advapi32!EventRegister</code> (o <code>ntdll!EtwEventRegister</code>), la firma en x64 recibe:
<pre><code>lea rcx, [rip + GUID_Provider] ; 1.er arg (RCX): Puntero a los 16 bytes del GUID en .rdata
xor edx, edx                   ; 2.º arg (RDX): EnableCallback (opcional)
xor r8d, r8d                   ; 3.er arg (R8) : CallbackContext
lea r9, [rip + g_RegHandle]    ; 4.º arg (R9) : Puntero global donde se guarda el REGHANDLE
call cs:EventRegister</code></pre>
El valor guardado a través de <strong><code>R9</code></strong> (<code>REGHANDLE</code>) es el manejador global que <strong>luego usarán todas las llamadas subsiguientes a <code>EventWrite</code> / <code>EtwEventWrite</code></strong> para emitir eventos. Leer los 16 bytes apuntados por <code>RCX</code> permite cruzar de inmediato el GUID con <code>logman query providers</code> en la VM para conocer la identidad y finalidad del proveedor.</li>
<li><strong>Reconocimiento defensivo de <em>ETW Patching</em> en User-Mode:</strong><br>
Ciertas muestras evasivas intentan silenciar la telemetría del propio proceso (como los eventos del runtime de <code>.NET CLR</code> o <code>AMSI</code>) resolviendo dinámicamente <code>ntdll!EtwEventWrite</code> (o <code>NtTraceEvent</code>), cambiando la protección de su página de memoria a <code>PAGE_EXECUTE_READWRITE</code> y sobrescribiendo su primer byte con <code>ret</code> (<code>0xC3</code>) o <code>xor eax, eax ; ret</code> (<code>33 C0 C3</code>). En el depurador, el analista lo detecta comparando los primeros bytes de <code>ntdll!EtwEventWrite</code> en memoria frente a la copia intacta de <code>ntdll.dll</code> en disco o monitoreando llamadas a <code>VirtualProtect</code> sobre rangos de memoria de <code>ntdll</code>.</li>
</ol>
</aside>"""

# HTML para Hoja 4 de la Separata (Página 15)
HOJA4_HTML = """
<h2 id="hoja-4">Hoja 4 · Evasión User-Mode, Inyección, Go/Rust y Extracción In-Place (Rev. 5.4)</h2>

<h3>4.1 Stubs de Syscall en <code>ntdll.dll</code> (x64) y Matriz de Evasión (Lecciones 2.14 y 2.15)</h3>
<div class="tabla"><table>
<thead><tr><th>Stub original en <code>ntdll.dll</code> (32 bytes)</th><th>Stub Indirect Syscall (en el binario)</th></tr></thead>
<tbody><tr>
<td><pre><code>4C 8B D1        mov r10, rcx
B8 [SSN 4B]     mov eax, &lt;SSN&gt;
F6 04 25 ...    test byte ptr [...], 1
75 03           jne short +3
0F 05           syscall
C3              ret</code></pre></td>
<td><pre><code>4C 8B D1        mov r10, rcx
B8 [SSN 4B]     mov eax, &lt;SSN&gt;
FF 25 [offset]  jmp qword ptr [pfn_ntdll_syscall]
                (salta al 0F 05 dentro de ntdll)</code></pre></td>
</tr></tbody></table></div>
<ul>
<li><strong>Hell's Gate:</strong> Busca <code>4C 8B D1 B8</code> en el export de <code>ntdll</code>. <strong>Halo's Gate:</strong> Si el byte <code>+0</code> es <code>0xE9</code> (hook), busca en vecinos a <code>±32 * i</code> bytes. <strong>Tartarus' Gate:</strong> Detecta hooks en el byte <code>+3</code> (tras <code>4C 8B D1</code>).</li>
<li><strong>Detección Defensiva:</strong> 1) <code>RIP</code> en <code>KiSystemCall64</code> fuera de <code>ntdll.dll</code>/<code>win32u.dll</code> (caza Direct Syscalls vía <code>ETWti</code> / <code>InstrumentationCallback</code>). 2) Desenrollado de pila vía <code>.pdata</code> donde el llamador de <code>ntdll</code> no es <code>kernelbase.dll</code> (caza Indirect Syscalls sin Call Stack Spoofing).</li>
</ul>

<h3>4.2 Firma Rápida de Inyección de Procesos en Memoria (Lección 2.22)</h3>
<div class="tabla"><table>
<thead><tr><th>Técnica</th><th>Secuencia de APIs característica</th><th>Punto exacto de intercepción / Evidencia</th></tr></thead>
<tbody>
<tr><td><strong>CreateRemoteThread</strong></td><td><code>OpenProcess</code> &rarr; <code>VirtualAllocEx</code> &rarr; <code>WriteProcessMemory</code> &rarr; <code>CreateRemoteThread</code></td><td>Breakpoint en <code>WriteProcessMemory</code> (<code>R8</code> = buffer local en x64) y <code>CreateRemoteThread</code>.</td></tr>
<tr><td><strong>Process Hollowing (RunPE)</strong></td><td><code>CreateProcessW(CREATE_SUSPENDED=4)</code> &rarr; <code>NtUnmapViewOfSection</code> &rarr; <code>VirtualAllocEx</code> &rarr; <code>WriteProcessMemory</code> &rarr; <code>SetThreadContext</code> &rarr; <code>ResumeThread</code></td><td>En <code>SetThreadContext</code>, el nuevo <code>EntryPoint</code> se escribe en <strong><code>ctx.Rcx</code></strong> (x64, offset <code>+0x80</code> de <code>CONTEXT</code>) o <strong><code>ctx.Eax</code></strong> (x86, offset <code>+0xB0</code>).</td></tr>
<tr><td><strong>Early Bird APC</strong></td><td><code>CreateProcessW(CREATE_SUSPENDED)</code> &rarr; <code>VirtualAllocEx</code> &rarr; <code>WriteProcessMemory</code> &rarr; <code>QueueUserAPC</code> &rarr; <code>ResumeThread</code></td><td>Primer argumento de <code>QueueUserAPC</code> (<code>RCX</code> en x64) apunta al payload inyectado.</td></tr>
<tr><td><strong>Reflective DLL</strong></td><td>Reserva memoria <code>RWX</code>/<code>RX</code> y salta a <code>ReflectiveLoader</code> sin <code>LoadLibrary</code></td><td>La DLL no figura en <code>PEB-&gt;Ldr</code> (<code>lm</code>), pero existe como región <code>Private</code> ejecutable en <code>!vadump</code>.</td></tr>
</tbody></table></div>

<h3>4.3 Go (1.17+ ABI) y Rust (Mangling v0 y Niche Optimization) (Lección 2.13)</h3>
<ul>
<li><strong>Go <code>pclntab</code> Magic Bytes:</strong> <code>0xFFFFFFFB</code> (Go 1.2), <code>0xFFFFFFFA</code> (Go 1.16), <code>0xFFFFFFF0</code> (Go 1.18+), <code>0xFFFFFFF1</code> (Go 1.20+). Recuperar nombres con <code>GoReSym</code> o Ghidra 11+.</li>
<li><strong>Go <code>string</code> y Registros:</strong> Par <code>{ptr, len}</code> de 16B <strong>sin byte <code>0x00</code></strong>. Registros de argumentos/retorno en orden: <strong><code>RAX, RBX, RCX, RDI, RSI, R8, R9, R10, R11</code></strong>. Goroutine activa en <strong><code>R14</code></strong> (<code>cmp rsp, [r14+10h]</code>).</li>
<li><strong>Rust <code>Option&lt;T&gt;</code>:</strong> Con tipos completos (<code>Option&lt;u32&gt;</code>) lleva un <code>tag</code> en <code>+0x00</code> (<code>0=None, 1=Some</code>). Con punteros no nulos (<code>Option&lt;&amp;T&gt;</code>, <code>Option&lt;Box&lt;T&gt;&gt;</code>, <code>NonZeroU32</code>), aplica <strong>Niche Optimization</strong>: suprime el <code>tag</code> y compila como <code>test rax, rax ; jz es_none</code>.</li>
</ul>

<h3>4.4 Doble Breakpoint Encadenado en <code>x64dbg</code> para Decodificadores <code>void</code> In-Place (Lección 2.6)</h3>
<pre><code>1) En el prólogo de la función decodificadora:  Break condition: 0  |  Command: $ptr = rcx
2) En la instrucción RET de la función:         Break condition: 0  |  Log:     "Str: {utf8@$ptr}"</code></pre>
"""

# HTML para Hoja 5 de la Separata (Página 16)
HOJA5_HTML = """
<h2 id="hoja-5">Hoja 5 · Criptografía Nativa (CryptoAPI / CNG) y Reversing de Drivers .sys (Rev. 5.4)</h2>

<h3>5.1 CryptoAPI (<code>advapi32.dll</code>) vs. CNG (<code>bcrypt.dll</code>) y Endianness (Lección 4.2)</h3>
<div class="tabla"><table>
<thead><tr><th>Propiedad</th><th>CryptoAPI Clásica (<code>advapi32.dll</code>)</th><th>CNG Moderna (<code>bcrypt.dll</code>)</th></tr></thead>
<tbody>
<tr><td><strong>Buffer de texto plano al cifrar</strong></td><td><code>CryptEncrypt</code>: 5.º arg <code>pbData</code> (<strong><code>[rsp+28h]</code></strong> en x64, <em>in-place</em>)</td><td><code>BCryptEncrypt</code>: 2.º arg <code>pbInput</code> (<strong><code>RDX</code></strong> en x64) y largo en <strong><code>R8D</code></strong></td></tr>
<tr><td><strong>Encabezado de clave y Magic</strong></td><td><code>BLOBHEADER</code> (8B) + <code>RSAPUBKEY</code> (<code>"RSA1"</code>=<code>0x31415352</code>, <code>"RSA2"</code>=<code>0x32415352</code>)</td><td><code>BCRYPT_RSAKEY_BLOB</code> (<code>"RSA1"</code>/<code>"RSA2"</code>) &middot; ECC P-256: <code>"ECK1"</code> (<code>0x314B4345</code>) / <code>"ECS1"</code> (<code>0x31534345</code>)</td></tr>
<tr><td><strong>Orden de bytes del Módulo RSA</strong></td><td><strong>Little-Endian</strong> (invertir con <code>[::-1]</code> antes de exportar a PEM)</td><td><strong>Big-Endian</strong> (orden de red estándar RFC)</td></tr>
<tr><td><strong>Firma ASN.1 DER (X.509 RSA)</strong></td><td colspan="2"><code>30 82 .. .. 30 0D 06 09 2A 86 48 86 F7 0D 01 01 01 05 00 03 82 .. .. 00 30 82</code></td></tr>
</tbody></table></div>

<h3>5.2 Offsets Críticos para Triage Estático de Drivers y RPC en x64 (Etapa 6 y Rama 2D)</h3>
<div class="tabla"><table>
<thead><tr><th>Estructura (x64)</th><th style="white-space: nowrap;">Offset</th><th>Campo y significado en IDA / Ghidra / WinDbg</th></tr></thead>
<tbody>
<tr><td><strong><code>DRIVER_OBJECT</code></strong><br>(<code>RCX</code> en <code>DriverEntry</code>)</td><td style="white-space: nowrap;"><code>+0x68</code><br><code>+0x70</code><br><code>+0xE0</code></td><td><code>DriverUnload</code><br><code>MajorFunction[0]</code> (<code>IRP_MJ_CREATE</code>)<br><code>MajorFunction[14]</code> (<strong><code>IRP_MJ_DEVICE_CONTROL</code></strong> = <code>0x70 + 14*8</code>)</td></tr>
<tr><td><strong><code>WDF_DRIVER_CONFIG</code></strong></td><td style="white-space: nowrap;"><code>+0x08</code></td><td><code>EvtDriverDeviceAdd</code> (pasado a <code>WdfDriverCreate</code>)</td></tr>
<tr><td><strong><code>WDF_IO_QUEUE_CONFIG</code></strong></td><td style="white-space: nowrap;"><code>+0x28</code></td><td><strong><code>EvtIoDeviceControl</code></strong> (pasado a <code>WdfIoQueueCreate</code>)</td></tr>
<tr><td><strong><code>FLT_REGISTRATION</code></strong></td><td style="white-space: nowrap;"><code>+0x20</code></td><td><code>OperationRegistration</code> &rarr; arreglo <code>FLT_OPERATION_REGISTRATION</code> (<code>+0x04</code> Flags, <code>+0x08</code> PreOp, <code>+0x10</code> PostOp)</td></tr>
<tr><td><strong><code>RPC_SERVER_INTERFACE</code></strong><br>(<code>RCX</code> en <code>RpcServerRegisterIf*</code>)</td><td style="white-space: nowrap;"><code>+0x04</code><br><code>+0x50</code></td><td><code>InterfaceId</code> (<code>RPC_SYNTAX_IDENTIFIER</code>: UUID de 16B + versión)<br><code>InterpreterInfo</code> &rarr; apunta a <code>MIDL_SERVER_INFO</code>, cuyo <strong><code>+0x08</code></strong> (<code>DispatchTable</code>) es el arreglo de punteros a las funciones C del servidor RPC.</td></tr>
</tbody></table></div>
"""
