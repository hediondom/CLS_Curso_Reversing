# -*- coding: utf-8 -*-
"""Integra las Notas Editoriales y las Ampliaciones basadas en fuentes externas
directamente en las páginas HTML del curso (guia/*.html, glosario.html, etc.)
y regenera CLS_Curso_Reversing.pdf y buscar.html, creando previamente un backup
íntegro de los archivos previos en _backup_2026-10-29_pre_v5.1/.
"""
import os
import re
import shutil
import sys

GUIA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import buscador  # noqa: E402
import pdf as pdf_mod  # noqa: E402

BACKUP_DIR = os.path.join(GUIA, "_backup_2026-10-29_pre_v5.1")

CSS_MARKER = "/* --- Ampliaciones Editoriales v5.1 --- */"
CSS_ADDITION = """
/* --- Ampliaciones Editoriales v5.1 --- */
.ampliacion-ext {
  margin: 1.2rem 0;
  padding: .85rem 1.05rem;
  border-radius: 8px;
  border-left: 5px solid #1d4f2a;
  background: #eef7f0;
}
.nota-ed {
  margin: 1.2rem 0;
  padding: .85rem 1.05rem;
  border-radius: 8px;
  border-left: 5px solid #5b4b8a;
  background: #f3f0fa;
}
.ampliacion-ext .callout-titulo, .nota-ed .callout-titulo {
  font-weight: 700;
  color: #12171b;
  margin-top: .1rem !important;
  margin-bottom: .35rem !important;
}
@media print {
  .tabla { overflow-x: visible !important; }
  table { width: 100%; table-layout: auto; word-wrap: break-word; overflow-wrap: anywhere; }
  .ampliacion-ext, .nota-ed { break-inside: avoid; page-break-inside: avoid; }
}
"""

# Mapa de archivo HTML relativo a CLS_Guia -> bloque HTML a insertar antes del pager/Volver o al final de <main>
INSERCIONES_HTML = {
    "guia/index.html": """
<aside class="nota-ed">
<p class="callout-titulo">Nota editorial separada — Sincronización de carga horaria de la Etapa 4 y orden sugerido para rutas 2C (Revisión 5.1)</p>
<p><strong>1. Carga horaria y lecciones de la Etapa 4:</strong> En las tablas resumen de apertura figura el valor previo de <code>14–18 h</code> (y <code>4</code> lecciones), mientras que la portada de la <a href="etapa-4.html">Etapa 4</a> declara <code>19 a 25 horas</code> y lista las <strong>5 lecciones</strong> vigentes: <code>4.1</code> (6 h), <code>4.5</code> (6 h), <code>4.2</code> (3 h), <code>4.3</code> (3 h) y <code>4.4</code> (3 h), cuya suma directa es de <strong>21 horas</strong> <em>(Hecho confirmado en el propio documento)</em>.</p>
<p><strong>2. Orden sugerido para 2.22, 2.23 y 2.24:</strong> Como las tres rutas optativas del bloque 2C (<a href="02-opt-malware-dinamico.html">2.22</a>, <a href="02-opt-shellcode-c2.html">2.23</a> y <a href="02-opt-fuzzing.html">2.24</a>) declaran como prerrequisitos las lecciones <code>4.1</code>, <code>4.2</code>, <code>4.4</code> y <code>5.1</code>, se recomienda cursarlas después de completar la Etapa 4 y la lección 5.1, manteniendo intacta la numeración original del curso <em>(Recomendación editorial)</em>.</p>
</aside>
""",
    "guia/02-debugger.html": """
<aside class="nota-ed">
<p class="callout-titulo">Nota editorial separada — Alcance arquitectónico de getdword(sp+8) en WindowProc</p>
<p>La expresión <code>getdword(sp+8) == 0x111 &amp;&amp; getdword(sp+0xC) == 0x13A</code> de esta lección aplica a binarios de <strong>32 bits (x86)</strong> (donde <code>__stdcall</code> apila <code>hWnd</code> en <code>[esp+4]</code>, <code>uMsg</code> en <code>[esp+8]</code> y <code>wParam</code> en <code>[esp+0xC]</code>) y asume que la palabra alta de <code>wParam</code> (código de notificación, p. ej. <code>BN_CLICKED = 0</code>) vale cero.</p>
</aside>
<aside class="ampliacion-ext">
<p class="callout-titulo">Ampliación editorial basada en fuentes externas — Condiciones para WndProc en x64 y función arg.get() en x64dbg</p>
<p>Según la especificación oficial de <a href="https://learn.microsoft.com/en-us/windows/win32/api/winuser/nc-winuser-wndproc" rel="noopener" target="_blank">WindowProc</a> y <a href="https://learn.microsoft.com/en-us/windows/win32/menurc/wm-command" rel="noopener" target="_blank">WM_COMMAND</a> en Microsoft Learn <em>(Hecho confirmado)</em> y la documentación de <a href="https://help.x64dbg.com/en/latest/introduction/Expressions.html" rel="noopener" target="_blank">Expressions &amp; Functions de x64dbg</a> <em>(Hecho confirmado)</em>:</p>
<ul>
<li><strong>En binarios de 64 bits (x64):</strong> Los cuatro argumentos llegan en <code>RCX</code> (<code>hWnd</code>), <code>RDX</code> (<code>uMsg</code>), <code>R8</code> (<code>wParam</code>) y <code>R9</code> (<code>lParam</code>), y el ID del control ocupa solo los 16 bits bajos (<code>LOWORD(wParam)</code>):
<pre><code>breakif: rdx == 0x111 &amp;&amp; (r8 &amp; 0xFFFF) == 0x13A
log:     "WM_COMMAND: notif={r8&gt;&gt;16} id={r8&amp;0xFFFF} hwnd={rcx}"</code></pre></li>
<li><strong>Expresión universal (x86 y x64) en el prólogo con <code>arg.get(n)</code>:</strong>
<pre><code>breakif: arg.get(1) == 0x111 &amp;&amp; (arg.get(2) &amp; 0xFFFF) == 0x13A
log:     "uMsg={arg.get(1)} control_id={arg.get(2)&amp;0xFFFF}"</code></pre></li>
</ul>
</aside>
""",
    "guia/02-ofuscacion.html": """
<aside class="ampliacion-ext">
<p class="callout-titulo">Ampliación editorial basada en fuentes externas — Criterio de triage estático: Aplanamiento de Flujo (CFF) vs. Máquina Virtual de bytecode (VM)</p>
<p>Aunque desofuscar una máquina virtual queda fuera del alcance del curso, en el inventario estático (Etapa 4) tanto CFF (<a href="https://github.com/obfuscator-llvm/obfuscator/wiki/Control-Flow-Flattening" rel="noopener" target="_blank">Obfuscator-LLVM</a>) como un intérprete de VM (<a href="https://www.usenix.org/legacy/events/woot09/tech/full_papers/rolles.pdf" rel="noopener" target="_blank">Rolles, USENIX WOOT '09</a>) producen un grafo con un gran bucle y un <code>switch</code> central <em>(Hecho confirmado)</em>. Esta tabla permite distinguirlos en pocos minutos:</p>
<div class="tabla"><table>
<thead><tr><th>Criterio observable</th><th>Aplanamiento del Flujo de Control (CFF)</th><th>Ofuscación por Máquina Virtual (VM de bytecode)</th></tr></thead>
<tbody>
<tr><td><strong>Contenido de los bloques del switch</strong></td><td>Operaciones reales de la función original (llamadas a APIs, acceso a variables locales y comparaciones del negocio).</td><td>Micro-operaciones genéricas (<em>handlers</em> del CPU virtual: <code>vADD</code>, <code>vPUSH</code>, <code>vMOV</code>, <code>vNOR</code>) sin lógica de negocio directa.</td></tr>
<tr><td><strong>Selección del siguiente bloque</strong></td><td>Cada bloque asigna una constante fija a una variable local de estado (<code>mov [rbp-8], 0x3A1F...</code>) y vuelve al encabezado del <code>switch</code>.</td><td>Un registro físico actúa como puntero de bytecode (<code>VIP</code>/<code>VPC</code>), lee el siguiente opcode de una tabla de datos (<code>lodsb</code> / <code>movzx eax, byte ptr [rsi] ; inc rsi</code>) y salta vía tabla de handlers (<code>jmp [rbx+rax*8]</code>).</td></tr>
<tr><td><strong>Reutilización entre funciones</strong></td><td>Cada función aplanada tiene su propio bucle y sus propios bloques básicos.</td><td>Varias funciones protegidas empujan un offset de bytecode distinto y saltan al mismo intérprete (<code>VM_Entry</code>).</td></tr>
</tbody></table></div>
</aside>
""",
    "guia/02-mfc.html": """
<aside class="ampliacion-ext">
<p class="callout-titulo">Ampliación editorial basada en fuentes externas — Definición en C y offsets de AFX_MSGMAP y AFX_MSGMAP_ENTRY para análisis estático</p>
<p>Cuando un binario MFC está enlazado estáticamente o se analiza sin ejecutarlo en IDA (<em>Local Types</em>) o Ghidra (<em>Parse C Source</em>), las estructuras oficiales de <code>&lt;afxwin.h&gt;</code> (<a href="https://learn.microsoft.com/en-us/cpp/mfc/tn006-message-maps" rel="noopener" target="_blank">Microsoft Learn: TN006 Message Maps</a>) tienen el siguiente layout en memoria <em>(Hecho confirmado)</em>:</p>
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
<p><em>Recomendación editorial:</em> El método virtual <code>GetMessageMap()</code> en la vtable de cualquier clase derivada de <code>CWnd</code> devuelve la dirección de su <code>AFX_MSGMAP</code> en dos instrucciones (<code>lea rax, [rip + MiDialog_messageMap] ; ret</code>).</p>
</aside>
""",
    "guia/02-huella-compilador.html": """
<aside class="nota-ed">
<p class="callout-titulo">Nota editorial separada — Verificación bibliográfica oficial para Delphi</p>
<p>Se dejan verificadas contra la documentación primaria de Embarcadero RAD Studio (DocWiki) las tres referencias sobre Delphi (convención <code>register</code>, cabecera de <code>string</code> y recursos <code>TPF0</code>) que habían quedado sin enlace activo en la revisión anterior.</p>
</aside>
<aside class="ampliacion-ext">
<p class="callout-titulo">Ampliación editorial basada en fuentes externas — ABI register, cabecera StrRec en offsets negativos y firma TPF0 en Delphi</p>
<ul>
<li><strong>Convención <code>register</code> en 32 bits vs. x64 (<a href="https://docwiki.embarcadero.com/RADStudio/en/Program_Control" rel="noopener" target="_blank">Embarcadero DocWiki: Program Control</a>):</strong> En Delphi x86 (<code>DCC32</code>), los tres primeros argumentos de hasta 32 bits van en <code>EAX</code> (1.º, o <code>Self</code> en métodos), <code>EDX</code> (2.º) y <code>ECX</code> (3.º); los restantes se apilan de izquierda a derecha y la función llamada limpia el stack (<code>ret N</code>). En Delphi x64 (<code>DCC64</code>), el compilador usa la ABI estándar de Microsoft (<code>RCX</code>, <code>RDX</code>, <code>R8</code>, <code>R9</code>) <em>(Hecho confirmado)</em>.</li>
<li><strong>Layout en memoria de cadenas largas (<a href="https://docwiki.embarcadero.com/RADStudio/en/Internal_Data_Formats_(Delphi)" rel="noopener" target="_blank">Embarcadero DocWiki: Internal Data Formats</a>):</strong> El puntero de cadena (Delphi 2009+) apunta al primer carácter (<code>offset 0</code>), precedido por una cabecera de 12 bytes en desplazamientos negativos: <code>[ptr - 12]</code> = <code>codePage</code> (2 B), <code>[ptr - 10]</code> = <code>elemSize</code> (2 B), <code>[ptr - 8]</code> = <code>refCnt</code> (4 B; <code>-1</code> en literales constantes) y <code>[ptr - 4]</code> = <code>length</code> en caracteres (4 B). Por eso <code>Length(s)</code> se traduce como <code>mov eax, [eax - 4]</code> <em>(Hecho confirmado)</em>.</li>
<li><strong>Formularios en <code>.rsrc</code> (<code>TPF0</code>) (<a href="https://docwiki.embarcadero.com/RADStudio/en/Using_Resource_Files" rel="noopener" target="_blank">Embarcadero DocWiki: Using Resource Files</a>):</strong> Los formularios VCL/FMX compilados en recursos <code>RT_RCDATA</code> comienzan con los 4 bytes ASCII <code>54 50 46 30</code> (<code>"TPF0"</code>) generados por <code>TWriter</code> y asocian cada control con el nombre de su método de evento publicado <em>(Hecho confirmado)</em>.</li>
</ul>
</aside>
""",
    "guia/02-pe-fino.html": """
<aside class="nota-ed">
<p class="callout-titulo">Nota editorial separada — Por qué [rsi+20h] apunta a DllBase en el listado de resolución por PEB</p>
<p>En el listado ilustrativo x64 de esta lección, <code>mov rsi, [rax+20h]</code> lee <code>Ldr-&gt;InMemoryOrderModuleList.Flink</code>. Como ese enlace apunta al campo <code>InMemoryOrderLinks</code> (ubicado en el offset <code>+0x10</code> dentro de <code>LDR_DATA_TABLE_ENTRY</code> en x64, o <code>+0x08</code> en x86) y no al inicio <code>+0x00</code> de la estructura, todos los accesos posteriores con base en <code>rsi</code> llevan restado ese desplazamiento.</p>
</aside>
<aside class="ampliacion-ext">
<p class="callout-titulo">Ampliación editorial basada en fuentes externas — Tabla completa de offsets de PEB, PEB_LDR_DATA y LDR_DATA_TABLE_ENTRY en x86 y x64</p>
<p>De acuerdo con <a href="https://learn.microsoft.com/en-us/windows/win32/api/winternl/ns-winternl-peb" rel="noopener" target="_blank">PEB (winternl.h)</a> y <a href="https://learn.microsoft.com/en-us/windows/win32/api/winternl/ns-winternl-peb_ldr_data" rel="noopener" target="_blank">PEB_LDR_DATA (winternl.h)</a> en Microsoft Learn <em>(Hecho confirmado)</em>:</p>
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
""",
    "guia/02-anti-analisis.html": """
<aside class="ampliacion-ext">
<p class="callout-titulo">Ampliación editorial basada en fuentes externas — PEB.NtGlobalFlag en x86 vs. x64 y clases 0x1E / 0x1F de NtQueryInformationProcess</p>
<p>Según <a href="https://learn.microsoft.com/en-us/windows-hardware/drivers/debugger/gflags-flag-table" rel="noopener" target="_blank">GFlags Flag Table</a> y <a href="https://learn.microsoft.com/en-us/windows/win32/api/winternl/nf-winternl-ntqueryinformationprocess" rel="noopener" target="_blank">NtQueryInformationProcess</a> en Microsoft Learn <em>(Hecho confirmado)</em>:</p>
<ul>
<li><strong><code>PEB.NtGlobalFlag</code> (valor <code>0x70</code>):</strong> Combina <code>FLG_HEAP_ENABLE_TAIL_CHECK (0x10) | FLG_HEAP_ENABLE_FREE_CHECK (0x20) | FLG_HEAP_VALIDATE_PARAMETERS (0x40) = 0x70</code>. En <strong>x86</strong> se ubica en <code>fs:[30h] -&gt; [peb + 0x68]</code>; en <strong>x64</strong> se desplaza a <code>gs:[60h] -&gt; [peb + 0xBC]</code>.</li>
<li><strong><code>ProcessDebugObjectHandle</code> (clase <code>0x1E = 30</code>):</strong> Consulta el handle al <code>DEBUG_OBJECT</code> del kernel. Si no hay debugger, <code>NtQueryInformationProcess</code> devuelve <code>0xC0000353</code> (<code>STATUS_PORT_NOT_SET</code>).</li>
<li><strong><code>ProcessDebugFlags</code> (clase <code>0x1F = 31</code>):</strong> Consulta <code>NoDebugInherit</code>; devuelve <code>0</code> si hay depurador activo y <code>1</code> si no está siendo depurado.</li>
</ul>
</aside>
""",
    "guia/02-packers.html": """
<aside class="ampliacion-ext">
<p class="callout-titulo">Ampliación editorial basada en fuentes externas — Procedimiento paso a paso del breakpoint de hardware en el stack («ESP/RSP trick»)</p>
<p>El paso 2 de esta lección menciona el breakpoint de hardware sobre el stack. Su fundamento combina la propiedad LIFO de la pila con los registros <code>DR0–DR3</code> (<em>Practical Malware Analysis</em>, Cap. 18; Intel SDM Vol. 3B §17.2) <em>(Hecho confirmado)</em>:</p>
<ol>
<li>En el inicio del stub de UPX, ejecutá <strong>una sola vez <code>F8</code></strong> sobre el <code>pushad</code> inicial (que guarda los 8 registros en el stack).</li>
<li>En el panel de registros de x64dbg, hacé clic derecho en el nuevo valor de <strong><code>ESP</code></strong> &rarr; <em>Follow in Dump</em>.</li>
<li>Seleccioná los primeros 4 bytes en el <em>Dump</em>, clic derecho &rarr; <em>Breakpoint &rarr; Hardware, Access &rarr; Dword</em>.</li>
<li>Presioná <strong><code>F9</code> (Run)</strong>: cuando el stub termine de descomprimir y ejecute <code>popad</code> para restaurar esos mismos 4 bytes, el procesador disparará la interrupción de depuración y se detendrá exactamente sobre el <code>jmp OEP</code>.</li>
</ol>
</aside>
""",
    "guia/02-cpp-profundo.html": """
<aside class="ampliacion-ext">
<p class="callout-titulo">Ampliación editorial basada en fuentes externas — Diferencia entre __CxxFrameHandler3 y __CxxFrameHandler4 (FH4) en MSVC x64</p>
<p>Desde Visual Studio 2019 16.3+ y Visual Studio 2022, MSVC x64 activa por defecto <code>/d2FH4</code> (<a href="https://devblogs.microsoft.com/cppblog/making-cpp-exception-handling-smaller-x64/" rel="noopener" target="_blank">Making C++ Exception Handling Smaller on x64</a>), reduciendo entre un 30 % y un 60 % el tamaño de las tablas en <code>.xdata</code> <em>(Hecho confirmado)</em>:</p>
<ul>
<li><strong><code>__CxxFrameHandler3</code>:</strong> Apunta a una estructura <code>FuncInfo</code> de campos fijos de 32 bits que empieza con la firma mágica <code>0x19930520</code>.</li>
<li><strong><code>__CxxFrameHandler4</code> (<code>FuncInfo4</code>):</strong> Elimina la constante <code>0x19930520</code>; comienza con un byte de banderas (<code>FuncInfoHeader</code>) y comprime los desplazamientos y conteos con enteros de longitud variable de 1 a 4 bytes. Para compilar una práctica que conserve el formato fijo clásico <code>FuncInfo</code>, puede pasarse <code>/d2FH4-</code> a <code>cl.exe</code>.</li>
</ul>
</aside>
""",
    "guia/02-windbg-heap.html": """
<aside class="ampliacion-ext">
<p class="callout-titulo">Ampliación editorial basada en fuentes externas — NT Heap (0xEEFFEEFF) vs. Segment Heap (0xDDEEDDEE) en Windows 10/11</p>
<p>En Windows 10 y 11 coexisten dos backends de heap en user mode (<a href="https://learn.microsoft.com/en-us/windows/win32/sbscs/application-manifests#segmentHeap" rel="noopener" target="_blank">Microsoft Learn: Segment Heap</a> y <a href="https://learn.microsoft.com/en-us/windows-hardware/drivers/debuggercmds/-heap" rel="noopener" target="_blank">!heap</a>) <em>(Hecho confirmado)</em>: el <strong>NT Heap</strong> clásico (firma <code>0xEEFFEEFF</code>) y el <strong>Segment Heap</strong> (firma <code>0xDDEEDDEE</code>, activo en servicios del sistema, apps MSIX y ejecutables con <code>&lt;segmentHeap&gt;true&lt;/segmentHeap&gt;</code> en su manifiesto). En WinDbg moderno, <code>!heap</code> muestra la columna <code>Type</code> (<code>NT Heap</code> vs. <code>Segment Heap</code>); cuando activás <strong>Full Page Heap</strong> (<code>gflags /p /enable prog.exe /full</code>), las reservas pasan por <code>_DPH_HEAP_ROOT</code> y <code>!heap -p -a &lt;dir&gt;</code> funciona de forma idéntica en ambos casos.</p>
</aside>
""",
    "guia/03-dotnet-runtime.html": """
<aside class="ampliacion-ext">
<p class="callout-titulo">Ampliación editorial basada en fuentes externas — Cómo distinguir Single-File Bundle y ReadyToRun (R2R) frente a Native AOT en .NET 6/8/9+</p>
<p>En .NET moderno, ver un <code>.exe</code> sin cabecera CLR en PE-bear no implica necesariamente que sea <strong>Native AOT</strong> (<a href="https://learn.microsoft.com/en-us/dotnet/core/deploying/single-file/overview" rel="noopener" target="_blank">Single-file deployment</a> y <a href="https://learn.microsoft.com/en-us/dotnet/core/deploying/ready-to-run" rel="noopener" target="_blank">ReadyToRun deployment</a>) <em>(Hecho confirmado)</em>:</p>
<div class="tabla"><table>
<thead><tr><th>Formato de publicación</th><th>Estructura del PE</th><th>¿Conserva IL y metadatos?</th><th>Cómo analizarlo</th></tr></thead>
<tbody>
<tr><td><strong>Single-File Deployment</strong> (<code>PublishSingleFile</code>)</td><td><code>apphost.exe</code> nativo que lleva concatenado un <em>Bundle</em> con las <code>.dll</code> administradas (marcador <code>.net bundle</code> / <code>hostfxr</code>).</td><td><strong>Sí</strong>, completos dentro de las DLLs embebidas.</td><td>Abrirlo directamente en <strong>ILSpy 8.x/9.x</strong>, que extrae y decompila las DLLs del bundle.</td></tr>
<tr><td><strong>ReadyToRun (R2R)</strong> (<code>PublishReadyToRun</code>)</td><td>PE con cabecera CLR cuyo <code>ManagedNativeHeader</code> apunta a <code>READYTORUN_HEADER</code> (firma <code>0x00525452</code> = <code>"RTR\0"</code>).</td><td><strong>Sí</strong>, conserva el IL original junto al código nativo precompilado.</td><td>Se lee como C#/IL normal en ILSpy o dnSpyEx.</td></tr>
<tr><td><strong>Native AOT</strong> (<code>PublishAot</code>)</td><td>PE 100 % nativo compilado con <code>ilc</code>, sin JIT ni bundle de IL.</td><td><strong>No hay IL</strong>.</td><td>Se analiza como nativo en IDA o Ghidra.</td></tr>
</tbody></table></div>
</aside>
""",
    "guia/04-formatos-protocolos.html": """
<aside class="nota-ed">
<p class="callout-titulo">Nota editorial separada — Formato tabulado del mapa de bytes CLSF y de la máquina de estados</p>
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
""",
    "guia/04-cripto.html": """
<aside class="ampliacion-ext">
<p class="callout-titulo">Ampliación editorial basada en fuentes externas — Reconocimiento de ChaCha20 / Salsa20 (RFC 8439) por sus constantes y operaciones ARX</p>
<p>En binarios modernos de Windows, el cifrado de flujo <strong>ChaCha20</strong> (<a href="https://www.rfc-editor.org/rfc/rfc8439" rel="noopener" target="_blank">IETF RFC 8439</a>) es sumamente frecuente y no utiliza tablas S-box <em>(Hecho confirmado)</em>:</p>
<ul>
<li><strong>Constante mágica de 16 bytes (clave de 256 bits):</strong> La cadena ASCII <strong><code>"expand 32-byte k"</code></strong> o los cuatro <code>DWORD</code> little-endian <strong><code>0x61707865</code>, <code>0x3320646e</code>, <code>0x79622d32</code>, <code>0x6b206574</code></strong> en las palabras <code>0..3</code> de un estado de 16 palabras (64 bytes). (Para clave de 128 bits: <code>"expand 16-byte k"</code>).</li>
<li><strong>Firma en el código (Quarter-Round ARX):</strong> Un bucle de 20 rondas (10 iteraciones dobles) compuesto exclusivamente por sumas de 32 bits (<code>add</code>), <code>xor</code> y rotaciones (<code>rol</code>) con conteos de <strong>16, 12, 8 y 7 bits</strong> (o 7, 9, 13 y 18 en Salsa20).</li>
</ul>
</aside>
""",
    "guia/05-automatizacion.html": """
<aside class="ampliacion-ext">
<p class="callout-titulo">Ampliación editorial basada en fuentes externas — Compatibilidad con IDA 9.0+: reemplazo de ida_struct e ida_enum por ida_typeinf</p>
<p>En <strong>IDA 9.0+</strong> (<a href="https://docs.hex-rays.com/user-guide/idapython/idapython-porting-guide-ida-9" rel="noopener" target="_blank">IDAPython Porting Guide to IDA 9.0</a>), Hex-Rays eliminó por completo los módulos <code>ida_struct</code> e <code>ida_enum</code> (y wrappers como <code>idc.get_enum</code> citado en el ejemplo del cap. 22b), unificándolos en <strong><code>ida_typeinf</code> (<code>tinfo_t</code>)</strong> <em>(Hecho confirmado)</em>. Para consultar el nombre simbólico de un valor en una enumeración de <em>Local Types</em> en IDA 9.0+:</p>
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
""",
    "guia/6-02-kmdf-ioctl.html": """
<aside class="nota-ed">
<p class="callout-titulo">Nota editorial separada — Restitución visual de la 5.ª columna de la tabla de métodos IOCTL en el PDF</p>
<p>En la impresión anterior del PDF (pág. 266), la quinta columna (<em>«Cómo lo obtiene un driver KMDF»</em>) de la tabla de métodos IOCTL quedaba recortada en el borde derecho por el estilo <code>overflow-x: auto</code>. En esta edición se ha ajustado el estilo de impresión para que las 5 columnas completas se visualicen íntegras en papel/PDF sin tocar el texto original.</p>
</aside>
<aside class="ampliacion-ext">
<p class="callout-titulo">Ampliación editorial basada en fuentes externas — Verificación de MinimumRequiredSize y EvtIoInCallerContext en KMDF</p>
<p>Según <a href="https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdfrequest/nf-wdfrequest-wdfrequestretrieveoutputbuffer" rel="noopener" target="_blank">WdfRequestRetrieveOutputBuffer</a> y <a href="https://learn.microsoft.com/en-us/windows-hardware/drivers/wdf/accessing-data-buffers-in-wdf-drivers" rel="noopener" target="_blank">Accessing Data Buffers in WDF Drivers</a> en Microsoft Learn <em>(Hecho confirmado)</em>:</p>
<ul>
<li><strong>Validación de tamaño en <code>WdfRequestRetrieveInputBuffer</code> / <code>WdfRequestRetrieveOutputBuffer</code>:</strong> El segundo parámetro (<code>RDX</code> en x64) es <code>MinimumRequiredLength</code> / <code>MinimumRequiredSize</code>. Si el buffer es menor, KMDF devuelve <code>STATUS_BUFFER_TOO_SMALL</code> (<code>0xC0000023</code>). Al revisar un driver en IDA/Ghidra (<a href="6-04-revision-driver.html">6.4</a>), comprobá siempre que ese segundo argumento no sea <code>0</code> cuando luego se escribe una estructura de tamaño fijo.</li>
<li><strong>Por qué <code>METHOD_NEITHER</code> requiere <code>EvtIoInCallerContext</code>:</strong> Como las colas WDF pueden despachar solicitudes en un hilo arbitrario, las direcciones de usuario (<code>Type3InputBuffer</code> y <code>UserBuffer</code>) solo son válidas en el contexto del llamador. Por eso deben tomarse en <code>EvtIoInCallerContext</code> con <code>WdfRequestRetrieveUnsafeUserInputBuffer</code> y bloquearse con <code>WdfRequestProbeAndLockUserBufferForRead</code> / <code>ForWrite</code> antes de encolar la solicitud.</li>
</ul>
</aside>
""",
    "guia/2d-02-memoria-loader.html": """
<aside class="nota-ed">
<p class="callout-titulo">Nota editorial separada — Correspondencia de las preguntas de repaso sobre VAD y WOW64</p>
<p>En la sección de repaso de arriba, las respuestas a las preguntas 2 y 3 quedaron fusionadas bajo el desplegable de WOW64 por falta de una línea <code>!!</code> intermedia. Su correspondencia exacta es:</p>
<ul>
<li><strong>¿Qué describe una VAD?</strong> Un <strong>rango</strong> de direcciones virtuales del proceso: su tipo (<code>Image</code>/<code>Mapped</code>/<code>Private</code>), permisos y a qué archivo/sección corresponde. El kernel las mantiene en un árbol por proceso; <code>!vadump</code> sirve para listar regiones en user mode y <code>!vad</code> para inspección detallada en el contexto de depuración de kernel.</li>
<li><strong>¿Qué precaución tomás al analizar un proceso WOW64?</strong> Anoto por separado la arquitectura del proceso y la del sistema, confirmo el contexto de registros y módulos, y tengo en cuenta la redirección de archivos/Registro. Un proceso de 32 bits no puede cargar una DLL de 64 bits para ejecutarla.</li>
</ul>
</aside>
""",
    "glosario.html": """
<aside class="ampliacion-ext">
<p class="callout-titulo">Ampliación editorial basada en fuentes externas — Términos adicionales de la Revisión 5.1</p>
<div class="tabla"><table>
<thead><tr><th>Término</th><th>Explicación</th></tr></thead>
<tbody>
<tr><td><strong><code>arg.get(n)</code> (x64dbg)</strong></td><td>Función de expresión de x64dbg que lee el argumento <code>n</code> (basado en 0) según la arquitectura (<code>[esp+4*(n+1)]</code> en x86; <code>RCX</code>, <code>RDX</code>, <code>R8</code>, <code>R9</code> en x64). Ver <a href="guia/02-debugger.html">Debugger</a>.</td></tr>
<tr><td><strong>ChaCha20</strong></td><td>Cifrado de flujo moderno (RFC 8439) basado en operaciones ARX (<code>ADD</code>, <code>ROTATE</code>, <code>XOR</code>) sobre 16 palabras de 32 bits; se reconoce por la constante ASCII <code>"expand 32-byte k"</code> (<code>0x61707865...</code>). Ver <a href="guia/04-cripto.html">Criptografía</a>.</td></tr>
<tr><td><strong><code>__CxxFrameHandler4</code> (FH4)</strong></td><td>Manejador de excepciones C++ por defecto en MSVC x64 (VS 2019 16.3+ / 2022) que comprime las tablas de <code>.xdata</code> en <code>FuncInfo4</code> sin la firma fija <code>0x19930520</code>. Ver <a href="guia/02-cpp-profundo.html">C++ profundo</a>.</td></tr>
<tr><td><strong><code>ida_typeinf</code> (<code>tinfo_t</code>)</strong></td><td>Módulo de IDAPython que en IDA 9.0+ reemplazó a los módulos eliminados <code>ida_struct</code> e <code>ida_enum</code> para manipular estructuras y enumeraciones. Ver <a href="guia/05-automatizacion.html">Automatización</a>.</td></tr>
<tr><td><strong>ReadyToRun (R2R) / Single-File (.NET)</strong></td><td>Variantes de despliegue en .NET moderno: <em>Single-File</em> concatena las DLLs de IL dentro de un <code>apphost.exe</code> nativo, y <em>R2R</em> agrega código nativo precompilado (<code>READYTORUN_HEADER</code>, <code>"RTR\\0"</code>) conservando el IL original. Ver <a href="guia/03-dotnet-runtime.html">.NET runtime</a>.</td></tr>
<tr><td><strong>Segment Heap</strong></td><td>Administrador de heap moderno de Windows 10/11 (firma <code>0xDDEEDDEE</code>), usado por servicios del sistema y apps con manifiesto <code>segmentHeap</code>, distinto del <em>NT Heap</em> clásico (<code>0xEEFFEEFF</code>). Ver <a href="guia/02-windbg-heap.html">WinDbg y heap</a>.</td></tr>
</tbody></table></div>
</aside>
""",
}


def respaldar(rel_path):
    origen = os.path.join(GUIA, rel_path.replace("/", os.sep))
    destino = os.path.join(BACKUP_DIR, rel_path.replace("/", os.sep))
    if os.path.exists(origen) and not os.path.exists(destino):
        os.makedirs(os.path.dirname(destino), exist_ok=True)
        shutil.copy2(origen, destino)


def actualizar_css():
    rel = "guia/estilo.css"
    respaldar(rel)
    ruta = os.path.join(GUIA, "guia", "estilo.css")
    with open(ruta, encoding="utf-8") as f:
        css = f.read()
    if CSS_MARKER not in css:
        css = css.rstrip() + "\n\n" + CSS_ADDITION.strip() + "\n"
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(css)
        print("Actualizado:", rel)


def inyectar_en_html(rel, bloque):
    respaldar(rel)
    # Partir siempre desde la copia original de respaldo para idempotencia limpia
    ruta_backup = os.path.join(BACKUP_DIR, rel.replace("/", os.sep))
    ruta_dest = os.path.join(GUIA, rel.replace("/", os.sep))
    with open(ruta_backup, encoding="utf-8") as f:
        html = f.read()

    bloque_limpio = bloque.strip()

    # Si la página tiene <div class="pager"> o el callout Volver al final de <main>,
    # insertamos justo antes para que los botones Anterior/Siguiente sigan quedando al pie.
    m_volver = re.search(r'<aside class="callout[^"]*"><p class="callout-titulo">Volver</p>.*?</aside>\s*</main>', html, flags=re.S)
    m_pager = re.search(r'<div class="pager">.*?</div>\s*</main>', html, flags=re.S)

    if m_volver:
        pos = m_volver.start()
        nuevo = html[:pos] + bloque_limpio + "\n\n" + html[pos:]
    elif m_pager:
        pos = m_pager.start()
        nuevo = html[:pos] + bloque_limpio + "\n\n" + html[pos:]
    else:
        pos = html.rfind("</main>")
        if pos == -1:
            raise RuntimeError(f"No se encontró </main> en {rel}")
        nuevo = html[:pos] + "\n" + bloque_limpio + "\n</main>" + html[pos + 7:]

    with open(ruta_dest, "w", encoding="utf-8") as f:
        f.write(nuevo)
    print("Actualizado:", rel)


def main():
    os.makedirs(BACKUP_DIR, exist_ok=True)
    respaldar("CLS_Curso_Reversing.pdf")
    respaldar("buscar.html")
    respaldar("_trabajo/print/CLS_Curso_Reversing_imprimible.html")

    actualizar_css()

    for rel, bloque in INSERCIONES_HTML.items():
        inyectar_en_html(rel, bloque)

    print("\nActualizando buscador offline (buscar.html)...")
    buscador.main()

    print("\nRegenerando CLS_Curso_Reversing.pdf (con índice paginado, marcadores y numeración)...")
    pdf_mod.main()

    # Copiar también al archivo CLS_Curso_Reversing_v5.1_Ampliada.pdf para mantener ambos sincronizados
    shutil.copy2(
        os.path.join(GUIA, "CLS_Curso_Reversing.pdf"),
        os.path.join(GUIA, "CLS_Curso_Reversing_v5.1_Ampliada.pdf"),
    )
    shutil.copy2(
        os.path.join(GUIA, "_trabajo", "print", "CLS_Curso_Reversing_imprimible.html"),
        os.path.join(GUIA, "CLS_Curso_Reversing_v5.1_Ampliada.html"),
    )
    print("Listo: HTML y PDF actualizados con éxito.")


if __name__ == "__main__":
    main()
