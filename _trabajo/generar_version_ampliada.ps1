$ErrorActionPreference = 'Stop'
$guia = 'd:\CLS_proyecto\CLS_Guia'
$origHtmlPath = Join-Path $guia '_trabajo\print\CLS_Curso_Reversing_imprimible.html'
$outHtmlRoot  = Join-Path $guia 'CLS_Curso_Reversing_v5.1_Ampliada.html'
$outHtmlPrint = Join-Path $guia '_trabajo\print\CLS_Curso_Reversing_v5.1_Ampliada.html'

$html = [System.IO.File]::ReadAllText($origHtmlPath, [System.Text.Encoding]::UTF8)

$cssExtra = @"
.print-sec .tabla { overflow-x: visible !important; }
.print-sec table { width: 100%; table-layout: auto; word-wrap: break-word; overflow-wrap: anywhere; }
.ampliacion-ext {
  margin: 12pt 0;
  padding: 9pt 11pt;
  border-radius: 6pt;
  border-left: 5pt solid #1d4f2a;
  background: #eef7f0;
  break-inside: avoid;
  page-break-inside: avoid;
}
.nota-ed {
  margin: 12pt 0;
  padding: 9pt 11pt;
  border-radius: 6pt;
  border-left: 5pt solid #5b4b8a;
  background: #f3f0fa;
  break-inside: avoid;
  page-break-inside: avoid;
}
.ampliacion-ext .callout-titulo, .nota-ed .callout-titulo {
  font-weight: 700;
  color: #12171b;
  margin-bottom: 4pt !important;
}
"@

$html = $html.Replace("</style></head>", "$cssExtra`n</style></head>")

$bloques = [ordered]@{
    "mapa-curso" = @"
<aside class="nota-ed">
<p class="callout-titulo">Nota editorial separada — Sincronización de carga horaria de la Etapa 4 y orden sugerido para rutas 2C (Ref. Entregable 3 · Módulo 1)</p>
<p><strong>1. Carga horaria de la Etapa 4:</strong> En las tablas resumen de apertura figura el valor previo de <code>14–18 h</code> (y <code>4</code> lecciones), mientras que la portada de la Etapa 4 declara <code>19 a 25 horas</code> y lista las <strong>5 lecciones</strong> vigentes: <code>4.1</code> (6 h), <code>4.5</code> (6 h), <code>4.2</code> (3 h), <code>4.3</code> (3 h) y <code>4.4</code> (3 h), cuya suma directa es de <strong>21 horas</strong> <em>(Hecho confirmado en el propio documento, [Ref-Interna])</em>.</p>
<p><strong>2. Orden sugerido para 2.22, 2.23 y 2.24:</strong> Como las tres rutas optativas del bloque 2C declaran como prerrequisitos las lecciones <code>4.1</code>, <code>4.2</code>, <code>4.4</code> y <code>5.1</code>, se recomienda cursarlas después de completar la Etapa 4 y la lección 5.1, manteniendo intacta la numeración original del curso <em>(Recomendación editorial)</em>.</p>
</aside>
"@

    "sec-guia-02-debugger" = @"
<aside class="nota-ed">
<p class="callout-titulo">Nota editorial separada — Alcance arquitectónico de getdword(sp+8) en WindowProc (Ref. Entregable 3 · Módulo 2)</p>
<p>La expresión <code>getdword(sp+8) == 0x111 &amp;&amp; getdword(sp+0xC) == 0x13A</code> de esta sección aplica a binarios de <strong>32 bits (x86)</strong> (donde <code>__stdcall</code> apila <code>hWnd</code> en <code>[esp+4]</code>, <code>uMsg</code> en <code>[esp+8]</code> y <code>wParam</code> en <code>[esp+0xC]</code>) y asume que la palabra alta de <code>wParam</code> (código de notificación, p. ej. <code>BN_CLICKED = 0</code>) vale cero.</p>
</aside>
<aside class="ampliacion-ext">
<p class="callout-titulo">Ampliación editorial basada en fuentes externas — Condiciones para WndProc en x64 y función arg.get() en x64dbg [Ref-1, Ref-2, Ref-3]</p>
<p>Según la especificación oficial de <code>WindowProc</code> y <code>WM_COMMAND</code> en Microsoft Learn <em>(Hecho confirmado, [Ref-1, Ref-2])</em> y la documentación de expresiones de x64dbg <em>(Hecho confirmado, [Ref-3])</em>:</p>
<ul>
<li><strong>En binarios de 64 bits (x64):</strong> Los cuatro argumentos llegan en <code>RCX</code> (<code>hWnd</code>), <code>RDX</code> (<code>uMsg</code>), <code>R8</code> (<code>wParam</code>) y <code>R9</code> (<code>lParam</code>), y el ID del control ocupa solo los 16 bits bajos (<code>LOWORD(wParam)</code>) [Ref-1, Ref-2]:
<pre><code>breakif: rdx == 0x111 &amp;&amp; (r8 &amp; 0xFFFF) == 0x13A
log:     "WM_COMMAND: notif={r8&gt;&gt;16} id={r8&amp;0xFFFF} hwnd={rcx}"</code></pre></li>
<li><strong>Expresión universal (x86 y x64) en el prólogo con <code>arg.get(n)</code> [Ref-3]:</strong>
<pre><code>breakif: arg.get(1) == 0x111 &amp;&amp; (arg.get(2) &amp; 0xFFFF) == 0x13A
log:     "uMsg={arg.get(1)} control_id={arg.get(2)&amp;0xFFFF}"</code></pre></li>
</ul>
</aside>
"@

    "sec-guia-02-ofuscacion" = @"
<aside class="ampliacion-ext">
<p class="callout-titulo">Ampliación editorial basada en fuentes externas — Criterio de triage estático: Aplanamiento de Flujo (CFF) vs. Máquina Virtual de bytecode (VM) [Ref-4, Ref-5]</p>
<p>Aunque desofuscar una máquina virtual queda fuera del alcance del curso, en el inventario estático (Etapa 4) tanto CFF como un intérprete de VM producen un grafo con un gran bucle y un <code>switch</code> central <em>(Hecho confirmado, [Ref-4, Ref-5])</em>. Esta tabla permite distinguirlos en pocos minutos:</p>
<div class="tabla"><table>
<thead><tr><th>Criterio observable</th><th>Aplanamiento del Flujo de Control (CFF) [Ref-4]</th><th>Ofuscación por Máquina Virtual (VM) [Ref-5]</th></tr></thead>
<tbody>
<tr><td><strong>Contenido de los bloques del switch</strong></td><td>Operaciones reales de la función original (llamadas a APIs, acceso a variables locales y comparaciones del negocio).</td><td>Micro-operaciones genéricas (<em>handlers</em> del CPU virtual: <code>vADD</code>, <code>vPUSH</code>, <code>vMOV</code>, <code>vNOR</code>) sin lógica de negocio directa.</td></tr>
<tr><td><strong>Selección del siguiente bloque</strong></td><td>Cada bloque asigna una constante fija a una variable local de estado (<code>mov [rbp-8], 0x3A1F...</code>) y vuelve al encabezado del <code>switch</code>.</td><td>Un registro físico actúa como puntero de bytecode (<code>VIP</code>/<code>VPC</code>), lee el siguiente opcode de una tabla de datos (<code>lodsb</code> / <code>movzx eax, byte ptr [rsi] ; inc rsi</code>) y salta vía tabla de handlers (<code>jmp [rbx+rax*8]</code>).</td></tr>
<tr><td><strong>Reutilización entre funciones</strong></td><td>Cada función aplanada tiene su propio bucle y sus propios bloques básicos.</td><td>Varias funciones protegidas empujan un offset de bytecode distinto y saltan al mismo intérprete (<code>VM_Entry</code>).</td></tr>
</tbody></table></div>
</aside>
"@

    "sec-guia-02-mfc" = @"
<aside class="ampliacion-ext">
<p class="callout-titulo">Ampliación editorial basada en fuentes externas — Definición en C y offsets de AFX_MSGMAP y AFX_MSGMAP_ENTRY para análisis estático [Ref-6]</p>
<p>Cuando un binario MFC está enlazado estáticamente o se analiza sin ejecutarlo en IDA (<em>Local Types</em>) o Ghidra (<em>Parse C Source</em>), las estructuras oficiales de <code>&lt;afxwin.h&gt;</code> tienen el siguiente layout en memoria <em>(Hecho confirmado, [Ref-6])</em>:</p>
<pre><code>struct AFX_MSGMAP_ENTRY {
    unsigned int nMessage;   // +0x00 (4B): Mensaje (p. ej. 0x0111 = WM_COMMAND)
    unsigned int nCode;      // +0x04 (4B): Código de notificación (0 = BN_CLICKED)
    unsigned int nID;        // +0x08 (4B): Control ID inicial
    unsigned int nLastID;    // +0x0C (4B): Control ID final (igual a nID si es único)
    uintptr_t    nSig;       // +0x10 (4B en x86 / 8B en x64): Firma AfxSig_* (0 = AfxSig_end)
    void*        pfn;        // +0x14 en x86 (total 24B) / +0x18 en x64 (total 32B): Puntero al handler
};
struct AFX_MSGMAP {
    const void* pfnGetBaseMap;                // +0x00: Puntero al mapa base
    const struct AFX_MSGMAP_ENTRY* lpEntries; // +0x04 (x86) / +0x08 (x64): Arreglo terminado en {0,0,0,0,0,0}
};</code></pre>
<p><em>Recomendación editorial:</em> El método virtual <code>GetMessageMap()</code> en la vtable de cualquier clase derivada de <code>CWnd</code> devuelve la dirección de su <code>AFX_MSGMAP</code> en dos instrucciones (<code>lea rax, [rip + MiDialog_messageMap] ; ret</code>) [Ref-6].</p>
</aside>
"@

    "sec-guia-02-huella-compilador" = @"
<aside class="nota-ed">
<p class="callout-titulo">Nota editorial separada — Verificación bibliográfica oficial para Delphi (Ref. Entregable 3 · Módulo 5)</p>
<p>Se dejan verificadas contra la documentación primaria de Embarcadero RAD Studio (DocWiki) las tres referencias sobre Delphi (convención <code>register</code>, cabecera de <code>string</code> y recursos <code>TPF0</code>) que figuraban pendientes de enlace al final de esta lección.</p>
</aside>
<aside class="ampliacion-ext">
<p class="callout-titulo">Ampliación editorial basada en fuentes externas — ABI register, cabecera StrRec en offsets negativos y firma TPF0 en Delphi [Ref-7, Ref-8, Ref-9]</p>
<ul>
<li><strong>Convención <code>register</code> en 32 bits vs. x64 [Ref-7]:</strong> En Delphi x86 (<code>DCC32</code>), los tres primeros argumentos de hasta 32 bits van en <code>EAX</code> (1.º, o <code>Self</code> en métodos), <code>EDX</code> (2.º) y <code>ECX</code> (3.º); los restantes se apilan de izquierda a derecha y la función llamada limpia el stack (<code>ret N</code>). En Delphi x64 (<code>DCC64</code>), el compilador usa la ABI estándar de Microsoft (<code>RCX</code>, <code>RDX</code>, <code>R8</code>, <code>R9</code>) [Ref-7].</li>
<li><strong>Layout en memoria de cadenas largas (<code>AnsiString</code> / <code>UnicodeString</code>, Delphi 2009+) [Ref-8]:</strong> El puntero de cadena apunta al primer carácter (<code>offset 0</code>), precedido por una cabecera de 12 bytes en desplazamientos negativos: <code>[ptr - 12]</code> = <code>codePage</code> (2 B), <code>[ptr - 10]</code> = <code>elemSize</code> (2 B), <code>[ptr - 8]</code> = <code>refCnt</code> (4 B; <code>-1</code> en literales constantes) y <code>[ptr - 4]</code> = <code>length</code> en caracteres (4 B). Por eso <code>Length(s)</code> se traduce como <code>mov eax, [eax - 4]</code> [Ref-8].</li>
<li><strong>Formularios en <code>.rsrc</code> (<code>TPF0</code>) [Ref-9]:</strong> Los formularios VCL/FMX compilados en recursos <code>RT_RCDATA</code> comienzan con los 4 bytes ASCII <code>54 50 46 30</code> (<code>"TPF0"</code>) generados por <code>TWriter</code> y asocian cada control con el nombre de su método de evento publicado [Ref-9].</li>
</ul>
</aside>
"@

    "sec-guia-02-pe-fino" = @"
<aside class="nota-ed">
<p class="callout-titulo">Nota editorial separada — Por qué [rsi+20h] apunta a DllBase en el listado de resolución por PEB (Ref. Entregable 3 · Módulo 6)</p>
<p>En el listado ilustrativo x64 de esta lección, <code>mov rsi, [rax+20h]</code> lee <code>Ldr-&gt;InMemoryOrderModuleList.Flink</code>. Como ese enlace apunta al campo <code>InMemoryOrderLinks</code> (ubicado en el offset <code>+0x10</code> dentro de <code>LDR_DATA_TABLE_ENTRY</code> en x64, o <code>+0x08</code> en x86) y no al inicio <code>+0x00</code> de la estructura, todos los accesos posteriores con base en <code>rsi</code> llevan restado ese desplazamiento.</p>
</aside>
<aside class="ampliacion-ext">
<p class="callout-titulo">Ampliación editorial basada en fuentes externas — Tabla completa de offsets de PEB, PEB_LDR_DATA y LDR_DATA_TABLE_ENTRY en x86 y x64 [Ref-10, Ref-11, Ref-12]</p>
<div class="tabla"><table>
<thead><tr><th>Estructura y campo</th><th>Offset en x86 (32 bits)</th><th>Offset en x64 (64 bits)</th><th>Relativo desde InMemoryOrderLinks (x86 / x64)</th></tr></thead>
<tbody>
<tr><td>Puntero al <code>PEB</code></td><td><code>fs:[0x30]</code></td><td><code>gs:[0x60]</code></td><td>—</td></tr>
<tr><td><code>PEB-&gt;Ldr</code> (<code>PEB_LDR_DATA*</code>)</td><td><code>+0x0C</code></td><td><code>+0x18</code></td><td>—</td></tr>
<tr><td><code>Ldr-&gt;InLoadOrderModuleList</code></td><td><code>+0x0C</code></td><td><code>+0x10</code></td><td>—</td></tr>
<tr><td><code>Ldr-&gt;InMemoryOrderModuleList</code></td><td><code>+0x14</code></td><td><code>+0x20</code></td><td>—</td></tr>
<tr><td><code>Ldr-&gt;InInitializationOrderModuleList</code></td><td><code>+0x1C</code></td><td><code>+0x30</code></td><td>—</td></tr>
<tr><td><code>LDR_DATA_TABLE_ENTRY.InLoadOrderLinks</code></td><td><code>+0x00</code></td><td><code>+0x00</code></td><td><code>-0x08</code> / <code>-0x10</code></td></tr>
<tr><td><code>LDR_DATA_TABLE_ENTRY.InMemoryOrderLinks</code></td><td><code>+0x08</code></td><td><code>+0x10</code></td><td><code>0x00</code> / <code>0x00</code> <em>(base de RSI)</em></td></tr>
<tr><td><code>LDR_DATA_TABLE_ENTRY.InInitializationOrderLinks</code></td><td><code>+0x10</code></td><td><code>+0x20</code></td><td><code>+0x08</code> / <code>+0x10</code></td></tr>
<tr><td><strong><code>LDR_DATA_TABLE_ENTRY.DllBase</code></strong></td><td><strong><code>+0x18</code></strong></td><td><strong><code>+0x30</code></strong></td><td><strong><code>+0x10</code> (x86) / <code>+0x20</code> (x64)</strong></td></tr>
<tr><td><code>LDR_DATA_TABLE_ENTRY.EntryPoint</code></td><td><code>+0x1C</code></td><td><code>+0x38</code></td><td><code>+0x14</code> (x86) / <code>+0x28</code> (x64)</td></tr>
<tr><td><code>LDR_DATA_TABLE_ENTRY.FullDllName</code> (<code>UNICODE_STRING</code>)</td><td><code>+0x24</code></td><td><code>+0x48</code></td><td><code>+0x1C</code> (x86) / <code>+0x38</code> (x64)</td></tr>
<tr><td><code>LDR_DATA_TABLE_ENTRY.BaseDllName</code> (<code>UNICODE_STRING</code>)</td><td><code>+0x2C</code></td><td><code>+0x58</code></td><td><code>+0x24</code> (x86) / <code>+0x48</code> (x64)</td></tr>
</tbody></table></div>
</aside>
"@

    "sec-guia-02-anti-analisis" = @"
<aside class="ampliacion-ext">
<p class="callout-titulo">Ampliación editorial basada en fuentes externas — PEB.NtGlobalFlag en x86 vs. x64 y clases 0x1E / 0x1F de NtQueryInformationProcess [Ref-10, Ref-13, Ref-14, Ref-15]</p>
<ul>
<li><strong><code>PEB.NtGlobalFlag</code> (valor <code>0x70</code>):</strong> Combina <code>FLG_HEAP_ENABLE_TAIL_CHECK (0x10) | FLG_HEAP_ENABLE_FREE_CHECK (0x20) | FLG_HEAP_VALIDATE_PARAMETERS (0x40) = 0x70</code> [Ref-14]. En <strong>x86</strong> se ubica en <code>fs:[30h] -&gt; [peb + 0x68]</code>; en <strong>x64</strong> se desplaza a <code>gs:[60h] -&gt; [peb + 0xBC]</code> [Ref-10, Ref-15].</li>
<li><strong><code>ProcessDebugObjectHandle</code> (clase <code>0x1E = 30</code>):</strong> Consulta el handle al <code>DEBUG_OBJECT</code> del kernel. Si no hay debugger, <code>NtQueryInformationProcess</code> devuelve <code>0xC0000353</code> (<code>STATUS_PORT_NOT_SET</code>) [Ref-13, Ref-15].</li>
<li><strong><code>ProcessDebugFlags</code> (clase <code>0x1F = 31</code>):</strong> Consulta <code>NoDebugInherit</code>; devuelve <code>0</code> si hay depurador activo y <code>1</code> si no está siendo depurado [Ref-13, Ref-15].</li>
</ul>
</aside>
"@

    "sec-guia-02-packers" = @"
<aside class="ampliacion-ext">
<p class="callout-titulo">Ampliación editorial basada en fuentes externas — Procedimiento paso a paso del breakpoint de hardware en el stack («ESP/RSP trick») [Ref-15, Ref-16]</p>
<p>El paso 2 de esta lección menciona el breakpoint de hardware sobre el stack. Su fundamento combina la propiedad LIFO de la pila con los registros <code>DR0–DR3</code> <em>(Hecho confirmado, [Ref-15, Cap. 18; Ref-16])</em>:</p>
<ol>
<li>En el inicio del stub de UPX, ejecutá <strong>una sola vez <code>F8</code></strong> sobre el <code>pushad</code> inicial (que guarda los 8 registros en el stack).</li>
<li>En el panel de registros de x64dbg, hacé clic derecho en el nuevo valor de <strong><code>ESP</code></strong> &rarr; <em>Follow in Dump</em>.</li>
<li>Seleccioná los primeros 4 bytes en el <em>Dump</em>, clic derecho &rarr; <em>Breakpoint &rarr; Hardware, Access &rarr; Dword</em>.</li>
<li>Presioná <strong><code>F9</code> (Run)</strong>: cuando el stub termine de descomprimir y ejecute <code>popad</code> para restaurar esos mismos 4 bytes, el procesador disparará la interrupción de depuración y se detendrá exactamente sobre el <code>jmp OEP</code> [Ref-15, Ref-16].</li>
</ol>
</aside>
"@

    "sec-guia-02-cpp-profundo" = @"
<aside class="ampliacion-ext">
<p class="callout-titulo">Ampliación editorial basada en fuentes externas — Diferencia entre __CxxFrameHandler3 y __CxxFrameHandler4 (FH4) en MSVC x64 [Ref-17]</p>
<p>Desde Visual Studio 2019 16.3+ y Visual Studio 2022, MSVC x64 activa por defecto <code>/d2FH4</code> (<code>__CxxFrameHandler4</code>), reduciendo entre un 30 % y un 60 % el tamaño de las tablas en <code>.xdata</code> <em>(Hecho confirmado, [Ref-17])</em>:</p>
<ul>
<li><strong><code>__CxxFrameHandler3</code>:</strong> Apunta a una estructura <code>FuncInfo</code> de campos fijos de 32 bits que empieza con la firma mágica <code>0x19930520</code>.</li>
<li><strong><code>__CxxFrameHandler4</code> (<code>FuncInfo4</code>):</strong> Elimina la constante <code>0x19930520</code>; comienza con un byte de banderas (<code>FuncInfoHeader</code>) y comprime los desplazamientos y conteos con enteros de longitud variable de 1 a 4 bytes. Para compilar una práctica que conserve el formato fijo clásico <code>FuncInfo</code>, puede pasarse <code>/d2FH4-</code> a <code>cl.exe</code> [Ref-17].</li>
</ul>
</aside>
"@

    "sec-guia-02-windbg-heap" = @"
<aside class="ampliacion-ext">
<p class="callout-titulo">Ampliación editorial basada en fuentes externas — NT Heap (0xEEFFEEFF) vs. Segment Heap (0xDDEEDDEE) en Windows 10/11 [Ref-18, Ref-19]</p>
<p>En Windows 10 y 11 coexisten dos backends de heap en user mode <em>(Hecho confirmado, [Ref-18, Ref-19])</em>: el <strong>NT Heap</strong> clásico (firma <code>0xEEFFEEFF</code>) y el <strong>Segment Heap</strong> (firma <code>0xDDEEDDEE</code>, activo en servicios del sistema, apps MSIX y ejecutables con <code>&lt;segmentHeap&gt;true&lt;/segmentHeap&gt;</code> en su manifiesto). En WinDbg moderno, <code>!heap</code> muestra la columna <code>Type</code> (<code>NT Heap</code> vs. <code>Segment Heap</code>); cuando activás <strong>Full Page Heap</strong> (<code>gflags /p /enable prog.exe /full</code>), las reservas pasan por <code>_DPH_HEAP_ROOT</code> y <code>!heap -p -a &lt;dir&gt;</code> funciona de forma idéntica en ambos casos [Ref-19].</p>
</aside>
"@

    "sec-guia-03-dotnet-runtime" = @"
<aside class="ampliacion-ext">
<p class="callout-titulo">Ampliación editorial basada en fuentes externas — Cómo distinguir Single-File Bundle y ReadyToRun (R2R) frente a Native AOT en .NET 6/8/9+ [Ref-20, Ref-21]</p>
<p>En .NET moderno, ver un <code>.exe</code> sin cabecera CLR en PE-bear no implica necesariamente que sea <strong>Native AOT</strong> <em>(Hecho confirmado, [Ref-20, Ref-21])</em>:</p>
<div class="tabla"><table>
<thead><tr><th>Formato de publicación</th><th>Estructura del PE</th><th>¿Conserva IL y metadatos?</th><th>Cómo analizarlo</th></tr></thead>
<tbody>
<tr><td><strong>Single-File Deployment</strong> (<code>PublishSingleFile</code>) [Ref-20]</td><td><code>apphost.exe</code> nativo que lleva concatenado un <em>Bundle</em> con las <code>.dll</code> administradas (marcador <code>.net bundle</code> / <code>hostfxr</code>).</td><td><strong>Sí</strong>, completos dentro de las DLLs embebidas.</td><td>Abrirlo directamente en <strong>ILSpy 8.x/9.x</strong>, que extrae y decompila las DLLs del bundle.</td></tr>
<tr><td><strong>ReadyToRun (R2R)</strong> (<code>PublishReadyToRun</code>) [Ref-21]</td><td>PE con cabecera CLR cuyo <code>ManagedNativeHeader</code> apunta a <code>READYTORUN_HEADER</code> (firma <code>0x00525452</code> = <code>"RTR\0"</code>).</td><td><strong>Sí</strong>, conserva el IL original junto al código nativo precompilado.</td><td>Se lee como C#/IL normal en ILSpy o dnSpyEx.</td></tr>
<tr><td><strong>Native AOT</strong> (<code>PublishAot</code>) [Ref-20]</td><td>PE 100 % nativo compilado con <code>ilc</code>, sin JIT ni bundle de IL.</td><td><strong>No hay IL</strong>.</td><td>Se analiza como nativo en IDA o Ghidra.</td></tr>
</tbody></table></div>
</aside>
"@

    "sec-guia-04-formatos-protocolos" = @"
<aside class="nota-ed">
<p class="callout-titulo">Nota editorial separada — Formato tabulado del mapa de bytes CLSF y de la máquina de estados (Ref. Entregable 3 · Módulo 12)</p>
<p>Los dos esquemas delimitados con <code>~~~text</code> en esta lección se presentan aquí con sus saltos de línea originales restaurados:</p>
<pre><code>Offset  Bytes                                      Lectura provisional
00      43 4C 53 46                                 firma ASCII «CLSF»
04      01                                          versión candidata = 1
05      00                                          flags candidatos = 0
06      0C 00                                       tamaño de cabecera candidato = 12 (LE)
08      05 00                                       tamaño de cuerpo candidato = 5 (LE)
0A      2A 00                                       campo variable = 42 (LE)
0C      48 45 4C 4C 4F                              cuerpo ASCII «HELLO»</code></pre>
<pre><code>DESCONECTADO --conectar--&gt; ESPERA_SALUDO
ESPERA_SALUDO --saludo válido--&gt; LISTO
LISTO --petición--&gt; ESPERA_RESPUESTA
ESPERA_RESPUESTA --respuesta/error--&gt; LISTO
cualquier estado --cierre--&gt; DESCONECTADO</code></pre>
</aside>
"@

    "sec-guia-04-cripto" = @"
<aside class="ampliacion-ext">
<p class="callout-titulo">Ampliación editorial basada en fuentes externas — Reconocimiento de ChaCha20 / Salsa20 (RFC 8439) por sus constantes y operaciones ARX [Ref-22]</p>
<p>En binarios modernos de Windows, el cifrado de flujo <strong>ChaCha20</strong> (IETF RFC 8439) es sumamente frecuente y no utiliza tablas S-box <em>(Hecho confirmado, [Ref-22])</em>:</p>
<ul>
<li><strong>Constante mágica de 16 bytes (clave de 256 bits):</strong> La cadena ASCII <strong><code>"expand 32-byte k"</code></strong> o los cuatro <code>DWORD</code> little-endian <strong><code>0x61707865</code>, <code>0x3320646e</code>, <code>0x79622d32</code>, <code>0x6b206574</code></strong> en las palabras <code>0..3</code> de un estado de 16 palabras (64 bytes) [Ref-22]. (Para clave de 128 bits: <code>"expand 16-byte k"</code>).</li>
<li><strong>Firma en el código (Quarter-Round ARX):</strong> Un bucle de 20 rondas (10 iteraciones dobles) compuesto exclusivamente por sumas de 32 bits (<code>add</code>), <code>xor</code> y rotaciones (<code>rol</code>) con conteos de <strong>16, 12, 8 y 7 bits</strong> (o 7, 9, 13 y 18 en Salsa20) [Ref-22].</li>
</ul>
</aside>
"@

    "sec-guia-05-automatizacion" = @"
<aside class="ampliacion-ext">
<p class="callout-titulo">Ampliación editorial basada en fuentes externas — Compatibilidad con IDA 9.0+: reemplazo de ida_struct e ida_enum por ida_typeinf [Ref-23]</p>
<p>En <strong>IDA 9.0+</strong>, Hex-Rays eliminó por completo los módulos <code>ida_struct</code> e <code>ida_enum</code> (y wrappers como <code>idc.get_enum</code> citado en el ejemplo del cap. 22b), unificándolos en <strong><code>ida_typeinf</code> (<code>tinfo_t</code>)</strong> <em>(Hecho confirmado, [Ref-23])</em>. Para consultar el nombre simbólico de un valor en una enumeración de <em>Local Types</em> en IDA 9.0+:</p>
<pre><code>import ida_typeinf

def nombre_miembro_enum(nombre_enum: str, valor: int) -&gt; str | None:
    tif = ida_typeinf.tinfo_t()
    if not tif.get_named_type(None, nombre_enum) or not tif.is_enum():
        return None
    ed = ida_typeinf.enum_type_data_t()
    if not tif.get_enum_details(ed):
        return None
    for m in ed:
        if m.value == valor:
            return m.name
    return None</code></pre>
</aside>
"@

    "sec-guia-6-02-kmdf-ioctl" = @"
<aside class="nota-ed">
<p class="callout-titulo">Nota editorial separada — Restitución de la 5.ª columna de la tabla de métodos IOCTL (Ref. Entregable 3 · Módulo 15)</p>
<p>En el PDF original (pág. 266), la quinta columna (<em>«Cómo lo obtiene un driver KMDF»</em>) de la tabla de métodos IOCTL se recortó en el borde derecho por el estilo <code>overflow-x: auto</code>. En esta edición ampliada se ha ajustado el contenedor de impresión para que las 5 columnas completas se visualicen íntegras sin recorte.</p>
</aside>
<aside class="ampliacion-ext">
<p class="callout-titulo">Ampliación editorial basada en fuentes externas — Verificación de MinimumRequiredSize y EvtIoInCallerContext en KMDF [Ref-24, Ref-25]</p>
<ul>
<li><strong>Validación de tamaño en <code>WdfRequestRetrieveInputBuffer</code> / <code>WdfRequestRetrieveOutputBuffer</code> [Ref-24]:</strong> El segundo parámetro (<code>RDX</code> en x64) es <code>MinimumRequiredLength</code> / <code>MinimumRequiredSize</code>. Si el buffer es menor, KMDF devuelve <code>STATUS_BUFFER_TOO_SMALL</code> (<code>0xC0000023</code>). Al revisar un driver en IDA/Ghidra (Lección 6.4), comprobá siempre que ese segundo argumento no sea <code>0</code> cuando luego se escribe una estructura de tamaño fijo [Ref-24].</li>
<li><strong>Por qué <code>METHOD_NEITHER</code> requiere <code>EvtIoInCallerContext</code> [Ref-25]:</strong> Como las colas WDF pueden despachar solicitudes en un hilo arbitrario, las direcciones de usuario (<code>Type3InputBuffer</code> y <code>UserBuffer</code>) solo son válidas en el contexto del llamador. Por eso deben tomarse en <code>EvtIoInCallerContext</code> con <code>WdfRequestRetrieveUnsafeUserInputBuffer</code> y bloquearse con <code>WdfRequestProbeAndLockUserBufferForRead</code> / <code>ForWrite</code> antes de encolar la solicitud [Ref-25].</li>
</ul>
</aside>
"@

    "sec-guia-2d-02-memoria-loader" = @"
<aside class="nota-ed">
<p class="callout-titulo">Nota editorial separada — Correspondencia de las preguntas de repaso sobre VAD y WOW64 (Ref. Entregable 3 · Módulo 16)</p>
<p>En la sección de repaso de arriba, las respuestas a las preguntas 2 y 3 quedaron fusionadas bajo el desplegable de WOW64 por falta de una línea <code>!!</code> intermedia. Su correspondencia exacta es:</p>
<ul>
<li><strong>¿Qué describe una VAD?</strong> Un <strong>rango</strong> de direcciones virtuales del proceso: su tipo (<code>Image</code>/<code>Mapped</code>/<code>Private</code>), permisos y a qué archivo/sección corresponde. El kernel las mantiene en un árbol por proceso; <code>!vadump</code> sirve para listar regiones en user mode y <code>!vad</code> para inspección detallada en el contexto de depuración de kernel.</li>
<li><strong>¿Qué precaución tomás al analizar un proceso WOW64?</strong> Anoto por separado la arquitectura del proceso y la del sistema, confirmo el contexto de registros y módulos, y tengo en cuenta la redirección de archivos/Registro. Un proceso de 32 bits no puede cargar una DLL de 64 bits para ejecutarla.</li>
</ul>
</aside>
"@

    "glosario" = @"
<aside class="ampliacion-ext">
<p class="callout-titulo">Ampliación editorial basada en fuentes externas — Términos adicionales de la Revisión 5.1 (Ref. Entregable 3 · Módulo 17)</p>
<div class="tabla"><table>
<thead><tr><th>Término</th><th>Explicación</th></tr></thead>
<tbody>
<tr><td><strong><code>arg.get(n)</code> (x64dbg)</strong></td><td>Función de expresión de x64dbg que lee el argumento <code>n</code> (basado en 0) según la arquitectura (<code>[esp+4*(n+1)]</code> en x86; <code>RCX</code>, <code>RDX</code>, <code>R8</code>, <code>R9</code> en x64) [Ref-3].</td></tr>
<tr><td><strong>ChaCha20</strong></td><td>Cifrado de flujo moderno (RFC 8439) basado en operaciones ARX (<code>ADD</code>, <code>ROTATE</code>, <code>XOR</code>) sobre 16 palabras de 32 bits; se reconoce por la constante ASCII <code>"expand 32-byte k"</code> (<code>0x61707865...</code>) [Ref-22].</td></tr>
<tr><td><strong><code>__CxxFrameHandler4</code> (FH4)</strong></td><td>Manejador de excepciones C++ por defecto en MSVC x64 (VS 2019 16.3+ / 2022) que comprime las tablas de <code>.xdata</code> en <code>FuncInfo4</code> sin la firma fija <code>0x19930520</code> [Ref-17].</td></tr>
<tr><td><strong><code>ida_typeinf</code> (<code>tinfo_t</code>)</strong></td><td>Módulo de IDAPython que en IDA 9.0+ reemplazó a los módulos eliminados <code>ida_struct</code> e <code>ida_enum</code> para manipular estructuras y enumeraciones [Ref-23].</td></tr>
<tr><td><strong>ReadyToRun (R2R) / Single-File (.NET)</strong></td><td>Variantes de despliegue en .NET moderno: <em>Single-File</em> concatena las DLLs de IL dentro de un <code>apphost.exe</code> nativo, y <em>R2R</em> agrega código nativo precompilado (<code>READYTORUN_HEADER</code>, <code>"RTR\0"</code>) conservando el IL original [Ref-20, Ref-21].</td></tr>
<tr><td><strong>Segment Heap</strong></td><td>Administrador de heap moderno de Windows 10/11 (firma <code>0xDDEEDDEE</code>), usado por servicios del sistema y apps con manifiesto <code>segmentHeap</code>, distinto del <em>NT Heap</em> clásico (<code>0xEEFFEEFF</code>) [Ref-18, Ref-19].</td></tr>
</tbody></table></div>
</aside>
"@
}

$count = 0
foreach ($key in $bloques.Keys) {
    $val = $bloques[$key].Trim()
    $pattern = "(?s)(<section class=`"print-sec`" id=`"$([regex]::Escape($key))`">.*?)(</section>)"
    $regex = [regex]::new($pattern)
    if (-not $regex.IsMatch($html)) {
        throw "No se encontro la seccion: $key"
    }
    $html = $regex.Replace($html, "`$1`n$val`n`$2", 1)
    $count++
}

[System.IO.File]::WriteAllText($outHtmlRoot, $html, [System.Text.Encoding]::UTF8)
[System.IO.File]::WriteAllText($outHtmlPrint, $html, [System.Text.Encoding]::UTF8)
Write-Output "Generado HTML ampliado con $count modulos insertados: $outHtmlRoot ($([System.IO.FileInfo]::new($outHtmlRoot).Length) bytes)"
