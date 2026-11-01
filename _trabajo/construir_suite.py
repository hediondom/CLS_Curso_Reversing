# -*- coding: utf-8 -*-
"""Construye la Edición 5 · Revisión 5.4 (con las 3 recomendaciones de precisión industrial integradas)
y genera el paquete HTML actualizado y el PDF final paginado y con marcadores.
"""
import html as _html
import os
import re
import shutil
import subprocess
import sys
import unicodedata

# Detección automática del directorio raíz del proyecto
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if os.path.basename(THIS_DIR) == "_trabajo":
    REPO_ROOT = os.path.dirname(THIS_DIR)
    MODULES_DIR = THIS_DIR
else:
    REPO_ROOT = THIS_DIR
    MODULES_DIR = os.path.join(THIS_DIR, "_trabajo")

sys.path.insert(0, MODULES_DIR)
import contenidos_nuevos as cn  # noqa: E402
import ampliaciones_tomo1 as at1  # noqa: E402
import ampliaciones_v54 as av54  # noqa: E402
import ampliaciones_t2_sep as at2  # noqa: E402

SRC_GUIA = REPO_ROOT
DST_GUIA = REPO_ROOT
ARTIFACT_DIR = r"C:\Users\agust\.gemini\antigravity\brain\5f78e7db-99bc-4011-8024-f93ab7c13c8f" if os.path.exists(r"C:\Users\agust\.gemini\antigravity\brain\5f78e7db-99bc-4011-8024-f93ab7c13c8f") else None

def buscar_chrome():
    candidatos = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ]
    for c in candidatos:
        if os.path.exists(c):
            return c
    return shutil.which("chrome") or shutil.which("msedge") or "chrome.exe"

CHROME = buscar_chrome()


def copiar_estructura_base():
    """Copia CLS_Guia a DST_GUIA excluyendo carpetas de backup pesadas."""
    os.makedirs(DST_GUIA, exist_ok=True)
    if os.path.abspath(SRC_GUIA) == os.path.abspath(DST_GUIA):
        print("DST_GUIA es el mismo origen; se conservan archivos base.")
        return

    excluir_dirs = {"_backup_2026-10-26", "_backup_2026-10-29_pre_v5.1", "chrome-perfil", "__pycache__"}
    for root, dirs, files in os.walk(SRC_GUIA):
        dirs[:] = [d for d in dirs if d not in excluir_dirs]
        rel_dir = os.path.relpath(root, SRC_GUIA)
        target_dir = DST_GUIA if rel_dir == "." else os.path.join(DST_GUIA, rel_dir)
        os.makedirs(target_dir, exist_ok=True)
        for f in files:
            if f.endswith(".pdf") or f.endswith(".numerado"):
                continue
            shutil.copy2(os.path.join(root, f), os.path.join(target_dir, f))

    # Restaurar los HTML previos a v5.1 desde _backup_2026-10-29_pre_v5.1 para partir limpios
    backup_v51 = os.path.join(SRC_GUIA, "_backup_2026-10-29_pre_v5.1")
    if os.path.exists(backup_v51):
        for root, _dirs, files in os.walk(backup_v51):
            rel_dir = os.path.relpath(root, backup_v51)
            target_dir = DST_GUIA if rel_dir == "." else os.path.join(DST_GUIA, rel_dir)
            os.makedirs(target_dir, exist_ok=True)
            for f in files:
                if f.endswith(".html") or f.endswith(".css"):
                    shutil.copy2(os.path.join(root, f), os.path.join(target_dir, f))
    print("Estructura base copiada en:", DST_GUIA)


CSS_ADDITION = """
/* --- Ampliaciones Editoriales v5.4 --- */
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


# Bloques técnicos basados en fuentes externas que se mantienen (sin las notas correctivas ya unificadas)
INSERCIONES_TECNICAS_HTML = {
    "guia/02-opt-malware-dinamico.html": at1.AMPLIACION_INYECCION_PROCESOS,
    "guia/02-debugger.html": at1.AMPLIACION_X64DBG_STRINGS + "\n\n" + av54.AMPLIACION_X64DBG_DOBLE_BP + """
<aside class="nota-ed">
<p class="callout-titulo">Nota de alcance arquitectónico — Expresión getdword(sp+8) en WindowProc (x86 vs. x64)</p>
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
    "guia/02-huella-compilador.html": at1.AMPLIACION_GO_RUST + "\n\n" + av54.AMPLIACION_RUST_NICHE + """
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
<p class="callout-titulo">Nota de lectura sobre el listado x64 — Por qué [rsi+20h] apunta a DllBase al recorrer el PEB</p>
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
    "guia/02-anti-analisis.html": at1.AMPLIACION_API_HOOKING_SYSCALLS + "\n\n" + av54.AMPLIACION_INDIRECT_SYSCALLS + """
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
<li><strong><code>__CxxFrameHandler4</code> (<code>FuncInfo4</code>):</strong> Elimina la constante <code>0x19930520</code>; comienza con un byte de banderas (<code>FuncInfoHeader</code>) y comprime los desplazamientos y conteos con enteros de longitud variable de 1 a 4 bytes. Para compilar una práctica que conserve el formato fijo clásico <code>FuncInfo</code>, puede pasarse <code>/d2FH4-</code> a <code>cl.exe</code> (ver plantilla <code>cpp_rtti_sso.cpp</code> en el <a href="../hilo-conductor-y-plantillas.html">Kit de plantillas C/C++</a>).</li>
</ul>
</aside>
""",
    "guia/02-windbg-heap.html": """
<aside class="ampliacion-ext">
<p class="callout-titulo">Ampliación editorial basada en fuentes externas — NT Heap (0xEEFFEEFF) vs. Segment Heap (0xDDEEDDEE) en Windows 10/11</p>
<p>En Windows 10 y 11 coexisten dos backends de heap en user mode (<a href="https://learn.microsoft.com/en-us/windows/win32/sbscs/application-manifests#segmentHeap" rel="noopener" target="_blank">Microsoft Learn: Segment Heap</a> y <a href="https://learn.microsoft.com/en-us/windows-hardware/drivers/debuggercmds/-heap" rel="noopener" target="_blank">!heap</a>) <em>(Hecho confirmado)</em>: el <strong>NT Heap</strong> clásico (firma <code>0xEEFFEEFF</code>) y el <strong>Segment Heap</strong> (firma <code>0xDDEEDDEE</code>, activo en servicios del sistema, apps MSIX y ejecutables con <code>&lt;segmentHeap&gt;true&lt;/segmentHeap&gt;</code> en su manifiesto). En WinDbg moderno, <code>!heap</code> muestra la columna <code>Type</code> (<code>NT Heap</code> vs. <code>Segment Heap</code>); cuando activás <strong>Full Page Heap</strong> (<code>gflags /p /enable prog.exe /full</code>), las reservas pasan por <code>_DPH_HEAP_ROOT</code> y <code>!heap -p -a &lt;dir&gt;</code> funciona de forma idéntica en ambos casos (podés practicarlo con <code>heap_bug.c</code> del <a href="../hilo-conductor-y-plantillas.html">Kit de plantillas C/C++</a>).</p>
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
    "guia/04-cripto.html": at1.AMPLIACION_CRIPTO_ASIMETRICA_APIS + "\n\n" + av54.AMPLIACION_ENDIANNESS_CNG_CRYPTO + """
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
<aside class="ampliacion-ext">
<p class="callout-titulo">Ampliación editorial basada en fuentes externas — Verificación de MinimumRequiredSize y EvtIoInCallerContext en KMDF</p>
<p>Según <a href="https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdfrequest/nf-wdfrequest-wdfrequestretrieveoutputbuffer" rel="noopener" target="_blank">WdfRequestRetrieveOutputBuffer</a> y <a href="https://learn.microsoft.com/en-us/windows-hardware/drivers/wdf/accessing-data-buffers-in-wdf-drivers" rel="noopener" target="_blank">Accessing Data Buffers in WDF Drivers</a> en Microsoft Learn <em>(Hecho confirmado)</em>:</p>
<ul>
<li><strong>Validación de tamaño en <code>WdfRequestRetrieveInputBuffer</code> / <code>WdfRequestRetrieveOutputBuffer</code>:</strong> El segundo parámetro (<code>RDX</code> en x64) es <code>MinimumRequiredLength</code> / <code>MinimumRequiredSize</code>. Si el buffer es menor, KMDF devuelve <code>STATUS_BUFFER_TOO_SMALL</code> (<code>0xC0000023</code>). Al revisar un driver en IDA/Ghidra (<a href="6-04-revision-driver.html">6.4</a>), comprobá siempre que ese segundo argumento no sea <code>0</code> cuando luego se escribe una estructura de tamaño fijo.</li>
<li><strong>Por qué <code>METHOD_NEITHER</code> requiere <code>EvtIoInCallerContext</code>:</strong> Como las colas WDF pueden despachar solicitudes en un hilo arbitrario, las direcciones de usuario (<code>Type3InputBuffer</code> y <code>UserBuffer</code>) solo son válidas en el contexto del llamador. Por eso deben tomarse en <code>EvtIoInCallerContext</code> con <code>WdfRequestRetrieveUnsafeUserInputBuffer</code> y bloquearse con <code>WdfRequestProbeAndLockUserBufferForRead</code> / <code>ForWrite</code> antes de encolar la solicitud.</li>
</ul>
</aside>
""",
    "guia/6-04-revision-driver.html": at2.AMPLIACION_6_04_DISPATCH_ROUTINES,
    "guia/6-05-minifilters.html": at2.AMPLIACION_6_05_MINIFILTERS_CALLBACKS,
    "guia/2d-01-objetos.html": at2.AMPLIACION_2D_01_EPROCESS_TOKEN,
    "guia/2d-10-ipc.html": at2.AMPLIACION_2D_10_RPC_INTERFACE,
    "guia/2d-11-excepciones.html": at2.AMPLIACION_2D_11_UNWIND_PDATA,
    "guia/2d-12-etw.html": at2.AMPLIACION_2D_12_ETW_PATCHING,
}


def envolver_pagina_html(titulo, descripcion, cuerpo_main):
    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{_html.escape(titulo)}</title>
<meta name="description" content="{_html.escape(descripcion)}">
<link rel="stylesheet" href="guia/estilo.css">
</head>
<body>
<a class="salto" href="#contenido">Saltar al contenido</a>
<header class="cabecera">
  <div class="marca"><a href="00_EMPEZAR_AQUI.html">CLS · Curso de reversing</a> <span class="edicion">edición 5 · rev. 5.4</span></div>
  <nav class="principal" aria-label="Navegación principal">
    <a href="00_EMPEZAR_AQUI.html">Inicio</a>
    <a href="guia/index.html">Curso</a>
    <a href="materiales.html">Materiales</a>
    <a href="fichas/index.html">Fichas</a>
    <a href="glosario.html">Glosario</a>
    <a href="preguntas_y_respuestas.html">Repaso</a>
    <a href="buscar.html">Buscar</a>
  </nav>
</header>
<main id="contenido">
{cuerpo_main.strip()}
<aside class="callout nota"><p class="callout-titulo">Volver</p><p><a href="guia/index.html">Mapa del curso</a> · <a href="00_EMPEZAR_AQUI.html">Inicio</a></p></aside>
</main>
<footer class="pie">
  <p>Material educativo y defensivo. Las prácticas se limitan a programas propios, software abierto o crackmes diseñados para aprender. No se enseña a eludir licencias, DRM ni controles de acceso.</p>
  <p><a href="00_EMPEZAR_AQUI.html">Inicio</a> · <a href="guia/etapa-0.html">Etapas</a> · <a href="fuentes_y_limites.html">Fuentes y límites</a> · <a href="registro_de_cobertura.csv">Registro de cobertura</a></p>
</footer>
</body>
</html>
"""


def aplicar_6_mejoras_html():
    # 0. Actualizar CSS
    css_path = os.path.join(DST_GUIA, "guia", "estilo.css")
    css = open(css_path, encoding="utf-8").read()
    if "/* --- Ampliaciones Editoriales" not in css:
        css = css.rstrip() + "\n\n" + CSS_ADDITION.strip() + "\n"
        open(css_path, "w", encoding="utf-8").write(css)

    # 1. Mejora 6a + enlaces en 00_EMPEZAR_AQUI.html
    p_home = os.path.join(DST_GUIA, "00_EMPEZAR_AQUI.html")
    h_home = open(p_home, encoding="utf-8").read()
    old_row4 = '<tr><td><strong>4</strong></td><td><a href="guia/etapa-4.html">Práctica guiada</a></td><td>14–18 h</td><td>Análisis completo + informe reproducible</td></tr>'
    new_row4 = '<tr><td><strong>4</strong></td><td><a href="guia/etapa-4.html">Práctica guiada</a></td><td>19–25 h</td><td>Método, formatos/protocolos, cripto, informe y dinámico seguro (5 lecciones)</td></tr>'
    if old_row4 in h_home:
        pass
    h_home = h_home.replace(old_row4, new_row4, 1)

    old_callout = '<aside class="callout nota"><p class="callout-titulo">Cómo se cuentan las lecciones</p><p>La <strong>Etapa 2</strong> reúne 2A, 2B y 2C, además de 3 rutas optativas (2.22–2.24) que no son obligatorias. La rama optativa 2D se asocia a la Etapa 2 después de 2C y aporta 13 lecciones fuera de sus horas obligatorias. La Etapa 6 tiene 6 lecciones optativas. La extensión Hyper-V está fuera de ambos núcleos. El apartado 5.4 «Fuera de alcance» es una página de límites, no una lección a cursar.</p></aside>'
    new_callout = '<aside class="callout nota"><p class="callout-titulo">Cómo se cuentan las lecciones y en qué orden cursar 2.22–2.24</p><p>La <strong>Etapa 2</strong> reúne 2A (2.1–2.9), 2B (2.10–2.16) y 2C (2.17–2.21), además de 3 rutas optativas (<a href="guia/02-opt-malware-dinamico.html">2.22</a>, <a href="guia/02-opt-shellcode-c2.html">2.23</a> y <a href="guia/02-opt-fuzzing.html">2.24</a>) que no son obligatorias. Como esas tres optativas declaran como prerrequisitos las lecciones <code>4.1</code>, <code>4.2</code>, <code>4.4</code> y <code>5.1</code>, se recomienda cursarlas <strong>después de completar la Etapa 4 y la lección 5.1</strong>, manteniendo intacta la numeración del curso. La Etapa 4 comprende <strong>5 lecciones</strong> (<code>4.1</code>, <code>4.5</code>, <code>4.2</code>, <code>4.3</code> y <code>4.4</code>; 19–25 h). La rama optativa 2D aporta 13 lecciones fuera de las horas obligatorias y la Etapa 6 suma 6 lecciones optativas. El apartado 5.4 «Fuera de alcance» es una página de límites, no una lección a cursar.</p></aside>'
    if old_callout in h_home:
        pass
    h_home = h_home.replace(old_callout, new_callout, 1)

    old_pkg_row = '<tr><td><a href="glosario.html">glosario.html</a></td><td>Términos en lenguaje de principiante</td></tr>'
    new_pkg_rows = (
        '<tr><td><a href="hilo-conductor-y-plantillas.html">hilo-conductor-y-plantillas.html</a></td><td>Evolución de un mismo binario en los 3 niveles (<code>check.c</code> &rarr; <code>BlocLab</code>) y kit de 5 plantillas C/C++ en <code>plantillas_codigo/</code></td></tr>\n'
        '<tr><td><a href="hojas-referencia-rapida.html">hojas-referencia-rapida.html</a></td><td>Hojas de referencia rápida (<em>Cheat Sheets</em>) para Principiante, Intermedio y Avanzado</td></tr>\n'
        + old_pkg_row
    )
    if "hilo-conductor-y-plantillas.html" not in h_home and old_pkg_row in h_home:
        h_home = h_home.replace(old_pkg_row, new_pkg_rows, 1)
    open(p_home, "w", encoding="utf-8").write(h_home)
    print("Actualizado: 00_EMPEZAR_AQUI.html")

    # 2. Mejora 5 (3 Perfiles de estudio) + Mejora 6a en guia/index.html
    p_idx = os.path.join(DST_GUIA, "guia", "index.html")
    h_idx = open(p_idx, encoding="utf-8").read()
    old_idx_r4 = '<tr><td><strong>4</strong></td><td><a href="etapa-4.html">Práctica guiada</a></td><td>14 a 18 horas</td><td>4</td></tr>'
    new_idx_r4 = '<tr><td><strong>4</strong></td><td><a href="etapa-4.html">Práctica guiada</a></td><td>19 a 25 horas</td><td>5</td></tr>'
    if old_idx_r4 in h_idx:
        pass
    h_idx = h_idx.replace(old_idx_r4, new_idx_r4, 1)

    old_e2_desc = '<p>Leer assembly x86/x64, seguir el flujo y usar debugger y desensamblador con criterio. Se divide en 2A (base, 2.1–2.9), 2B (Windows intermedio, 2.10–2.16: ofuscación, TLS, MFC, huella, PE fino, anti-análisis, Ghidra) y 2C (Windows avanzado, 2.17+: packers didácticos, C++ profundo, WinDbg/heap, patch diffing, scripting). Las rutas de malware dinámico, shellcode/C2 y fuzzing quedan como optativas, fuera de la puerta obligatoria.</p>'
    new_e2_desc = '<p>Leer assembly x86/x64, seguir el flujo y usar debugger y desensamblador con criterio. Se divide en 2A (base, 2.1–2.9), 2B (Windows intermedio, 2.10–2.16: ofuscación, TLS, MFC, huella, PE fino, anti-análisis, Ghidra) y 2C (Windows avanzado, 2.17–2.21: packers didácticos, C++ profundo, WinDbg/heap, patch diffing, scripting). Las tres rutas optativas (<a href="02-opt-malware-dinamico.html">2.22</a>, <a href="02-opt-shellcode-c2.html">2.23</a> y <a href="02-opt-fuzzing.html">2.24</a>) quedan fuera de la puerta obligatoria; como requieren las lecciones <code>4.1</code>, <code>4.2</code>, <code>4.4</code> y <code>5.1</code>, se recomienda cursarlas después de completar la Etapa 4 y la lección 5.1.</p>'
    if old_e2_desc in h_idx:
        pass
    h_idx = h_idx.replace(old_e2_desc, new_e2_desc, 1)

    anchor_que_es = '<h2 id="qué-es-cada-etapa">Qué es cada etapa</h2>'
    if "Tres perfiles o rutas de estudio" not in h_idx and anchor_que_es in h_idx:
        h_idx = h_idx.replace(anchor_que_es, cn.BLOQUE_RUTAS_ESTUDIO.strip() + "\n\n" + anchor_que_es, 1)

    old_mat_glo = '<li><a href="../glosario.html">Glosario</a>: términos en lenguaje de principiante.</li>'
    new_mat_glo = (
        '<li><a href="../hilo-conductor-y-plantillas.html">Hilo conductor multi-nivel y kit de plantillas C/C++</a>: evolución de <code>check.c</code> a <code>BlocLab</code> en los 3 niveles y 5 esqueletos en C/C++ listos para compilar.</li>'
        '<li><a href="../hojas-referencia-rapida.html">Hojas de referencia rápida (Cheat Sheets)</a>: resumen de 1 página por nivel (Principiante, Intermedio y Avanzado).</li>'
        + old_mat_glo
    )
    if "hilo-conductor-y-plantillas.html" not in h_idx and old_mat_glo in h_idx:
        h_idx = h_idx.replace(old_mat_glo, new_mat_glo, 1)
    open(p_idx, "w", encoding="utf-8").write(h_idx)
    print("Actualizado: guia/index.html (con 3 Perfiles de estudio y Etapa 4 unificada)")

    # 3. Mejora 2 (Árbol de decisión de triage inicial) en guia/04-metodo.html
    p_met = os.path.join(DST_GUIA, "guia", "04-metodo.html")
    h_met = open(p_met, encoding="utf-8").read()
    anchor_paso3 = '<h2 id="paso-3-análisis-estático">Paso 3: análisis estático</h2>'
    if "Árbol de decisión de triage inicial" not in h_met and anchor_paso3 in h_met:
        h_met = h_met.replace(anchor_paso3, cn.BLOQUE_ARBOL_TRIAGE.strip() + "\n\n" + anchor_paso3, 1)
    open(p_met, "w", encoding="utf-8").write(h_met)
    print("Actualizado: guia/04-metodo.html (con Árbol de decisión de triage inicial)")

    # 4. Mejora 6b en guia/04-formatos-protocolos.html (reemplazo directo de ~~~text)
    p_fmt = os.path.join(DST_GUIA, "guia", "04-formatos-protocolos.html")
    h_fmt = open(p_fmt, encoding="utf-8").read()
    old_clsf_line = '<p>~~~text Offset  Bytes                                      Lectura provisional 00      43 4C 53 46                                 firma ASCII «CLSF» 04      01                                          versión candidata = 1 05      00                                          flags candidatos = 0 06      0C 00                                       tamaño de cabecera candidato = 12 (LE) 08      05 00                                       tamaño de cuerpo candidato = 5 (LE) 0A      2A 00                                       campo variable = 42 (LE) 0C      48 45 4C 4C 4F                              cuerpo ASCII «HELLO» ~~~</p>'
    new_clsf_pre = """<pre><code class="lenguaje-text">Offset  Bytes                                      Lectura provisional
00      43 4C 53 46                                 firma ASCII «CLSF»
04      01                                          versión candidata = 1
05      00                                          flags candidatos = 0
06      0C 00                                       tamaño de cabecera candidato = 12 (LE)
08      05 00                                       tamaño de cuerpo candidato = 5 (LE)
0A      2A 00                                       campo variable = 42 (LE)
0C      48 45 4C 4C 4F                              cuerpo ASCII «HELLO»</code></pre>"""
    if old_clsf_line in h_fmt:
        pass
    h_fmt = h_fmt.replace(old_clsf_line, new_clsf_pre, 1)

    old_fsm_line = '<p>~~~text DESCONECTADO --conectar--&gt; ESPERA_SALUDO ESPERA_SALUDO --saludo válido--&gt; LISTO LISTO --petición--&gt; ESPERA_RESPUESTA ESPERA_RESPUESTA --respuesta/error--&gt; LISTO cualquier estado --cierre--&gt; DESCONECTADO ~~~</p>'
    new_fsm_pre = """<pre><code class="lenguaje-text">DESCONECTADO --conectar--&gt; ESPERA_SALUDO
ESPERA_SALUDO --saludo válido--&gt; LISTO
LISTO --petición--&gt; ESPERA_RESPUESTA
ESPERA_RESPUESTA --respuesta/error--&gt; LISTO
cualquier estado --cierre--&gt; DESCONECTADO</code></pre>"""
    if old_fsm_line in h_fmt:
        pass
    h_fmt = h_fmt.replace(old_fsm_line, new_fsm_pre, 1)
    open(p_fmt, "w", encoding="utf-8").write(h_fmt)
    print("Actualizado: guia/04-formatos-protocolos.html (bloques <pre><code> unificados)")

    # 5. Mejora 6c en guia/2d-02-memoria-loader.html (separación directa de VAD y WOW64)
    p_2d2 = os.path.join(DST_GUIA, "guia", "2d-02-memoria-loader.html")
    h_2d2 = open(p_2d2, encoding="utf-8").read()
    old_qa_2d2 = (
        '<details class="qa"><summary>¿Qué describe una VAD?</summary><div class="respuesta"></div></details>\n'
        '<details class="qa"><summary>¿Qué precaución tomás al analizar un proceso WOW64?</summary><div class="respuesta"><p>Anoto por separado la arquitectura del proceso y la del sistema, confirmo el contexto de registros y módulos, y tengo en cuenta la redirección de archivos/Registro. Un proceso de 32 bits no puede cargar una DLL de 64 bits para ejecutarla.</p></div></details>\n'
        '<p>!! Un <strong>rango</strong> de direcciones virtuales del proceso: su tipo (Image/Mapped/Private), permisos y a qué archivo/sección corresponde. El kernel las mantiene en un árbol por proceso; <code>!vadump</code> sirve para listar regiones en user mode y <code>!vad</code> para inspección detallada en el contexto de depuración de kernel.</p>'
    )
    new_qa_2d2 = (
        '<details class="qa"><summary>¿Qué describe una VAD?</summary><div class="respuesta"><p>Un <strong>rango</strong> de direcciones virtuales del proceso: su tipo (<code>Image</code>/<code>Mapped</code>/<code>Private</code>), permisos y a qué archivo/sección corresponde. El kernel las mantiene en un árbol por proceso; <code>!vadump</code> sirve para listar regiones en user mode y <code>!vad</code> para inspección detallada en el contexto de depuración de kernel.</p></div></details>\n'
        '<details class="qa"><summary>¿Qué precaución tomás al analizar un proceso WOW64?</summary><div class="respuesta"><p>Anoto por separado la arquitectura del proceso y la del sistema, confirmo el contexto de registros y módulos, y tengo en cuenta la redirección de archivos/Registro. Un proceso de 32 bits no puede cargar una DLL de 64 bits para ejecutarla.</p></div></details>'
    )
    if old_qa_2d2 in h_2d2.replace("\r\n", "\n"):
        h_2d2 = h_2d2.replace("\r\n", "\n").replace(old_qa_2d2, new_qa_2d2, 1)
        open(p_2d2, "w", encoding="utf-8").write(h_2d2)
        print("Actualizado: guia/2d-02-memoria-loader.html (Q&A de VAD y WOW64 unificados)")

    # 6. Mejora 6d en guia/02-huella-compilador.html (integrar enlaces DocWiki de Delphi directo en Fuentes)
    p_hue = os.path.join(DST_GUIA, "guia", "02-huella-compilador.html")
    h_hue = open(p_hue, encoding="utf-8").read()
    old_delphi_src = '<li>Delphi: la convención <code>register</code>, la firma <code>TPF0</code> de los formularios y la cabecera de los <code>string</code> son conocimiento externo sin enlace verificado en esta revisión (la documentación de Embarcadero no respondió durante la verificación).</li>'
    new_delphi_src = '<li>Delphi (conocimiento externo verificado en Embarcadero RAD Studio DocWiki): <a href="https://docwiki.embarcadero.com/RADStudio/en/Program_Control" rel="noopener" target="_blank">Program Control (convención register)</a>, <a href="https://docwiki.embarcadero.com/RADStudio/en/Internal_Data_Formats_(Delphi)" rel="noopener" target="_blank">Internal Data Formats (cabecera StrRec en offsets negativos)</a> y <a href="https://docwiki.embarcadero.com/RADStudio/en/Using_Resource_Files" rel="noopener" target="_blank">Using Resource Files (recursos DFM/TPF0)</a>.</li>'
    if old_delphi_src in h_hue:
        pass
    h_hue = h_hue.replace(old_delphi_src, new_delphi_src, 1)
    open(p_hue, "w", encoding="utf-8").write(h_hue)
    print("Actualizado: guia/02-huella-compilador.html (Fuentes de Delphi unificadas)")

    # 7. Inyectar las ampliaciones técnicas basadas en fuentes externas
    for rel, bloque in INSERCIONES_TECNICAS_HTML.items():
        ruta_dest = os.path.join(DST_GUIA, rel.replace("/", os.sep))
        html_txt = open(ruta_dest, encoding="utf-8").read()
        bloque_limpio = bloque.strip()
        m_volver = re.search(r'<aside class="callout[^"]*"><p class="callout-titulo">Volver</p>.*?</aside>\s*</main>', html_txt, flags=re.S)
        m_pager = re.search(r'<div class="pager">.*?</div>\s*</main>', html_txt, flags=re.S)
        # Evitar duplicación comprobando si el bloque ya fue inyectado
        if bloque_limpio in html_txt:
            print("Ampliación técnica ya presente en:", rel)
            continue

        # Si los callouts ya existen por título pero cambió su contenido, actualizarlos
        callouts = re.findall(r'<aside class="(?:ampliacion-ext|nota-ed)">.*?</aside>', bloque_limpio, flags=re.S)
        if callouts:
            actualizado = False
            for c in callouts:
                c_tit = re.search(r'<p class="callout-titulo">(.*?)</p>', c)
                if c_tit:
                    pattern = rf'<aside class="(?:ampliacion-ext|nota-ed)">\s*<p class="callout-titulo">{re.escape(c_tit.group(1))}</p>.*?</aside>'
                    if re.search(pattern, html_txt, flags=re.S):
                        html_txt = re.sub(pattern, lambda _: c, html_txt, count=1, flags=re.S)
                        actualizado = True
            if actualizado:
                open(ruta_dest, "w", encoding="utf-8").write(html_txt)
                print("Ampliación técnica actualizada en:", rel)
                continue
        
        # Si contiene múltiples callouts, inyectar solo los que falten
        callouts = re.findall(r'<aside class="(?:ampliacion-ext|nota-ed)">.*?</aside>', bloque_limpio, flags=re.S)
        bloque_a_inyectar = []
        if callouts:
            for c in callouts:
                c_tit = re.search(r'<p class="callout-titulo">(.*?)</p>', c)
                if not c_tit or c_tit.group(1) not in html_txt:
                    bloque_a_inyectar.append(c)
            bloque_final = "\n\n".join(bloque_a_inyectar).strip()
        else:
            bloque_final = bloque_limpio if bloque_limpio not in html_txt else ""

        if not bloque_final:
            print("Ampliación técnica ya presente en:", rel)
            continue

        if m_volver:
            pos = m_volver.start()
            nuevo = html_txt[:pos] + bloque_final + "\n\n" + html_txt[pos:]
        elif m_pager:
            pos = m_pager.start()
            nuevo = html_txt[:pos] + bloque_final + "\n\n" + html_txt[pos:]
        else:
            pos = html_txt.rfind("</main>")
            nuevo = html_txt[:pos] + "\n" + bloque_final + "\n</main>" + html_txt[pos + 7:]
        open(ruta_dest, "w", encoding="utf-8").write(nuevo)
        print("Ampliación técnica integrada en:", rel)

    # 8. Crear las páginas nuevas: hilo-conductor-y-plantillas.html y hojas-referencia-rapida.html
    p_hilo = os.path.join(DST_GUIA, "hilo-conductor-y-plantillas.html")
    open(p_hilo, "w", encoding="utf-8").write(
        envolver_pagina_html(
            "Hilo conductor multi-nivel y kit de plantillas C/C++",
            "Evolución de un mismo binario a través de los niveles Principiante, Intermedio y Avanzado, y 5 plantillas mínimas en C/C++ listas para compilar.",
            cn.PAGINA_HILO_Y_PLANTILLAS,
        )
    )
    print("Creado: hilo-conductor-y-plantillas.html")

    p_cheat = os.path.join(DST_GUIA, "hojas-referencia-rapida.html")
    open(p_cheat, "w", encoding="utf-8").write(
        envolver_pagina_html(
            "Hojas de referencia rápida por nivel (Cheat Sheets)",
            "Tablas de referencia rápida para Principiante (registros, flags, Jcc, PE, ABI), Intermedio (PEB/LDR, cripto, anti-análisis, x64dbg/Frida) y Avanzado (C++ RTTI/SSO, IOCTL, IRQL, WinDbg).",
            cn.PAGINA_CHEAT_SHEETS,
        )
    )
    print("Creado: hojas-referencia-rapida.html")

    # 9. Guardar los 5 archivos .c / .cpp en plantillas_codigo/
    dir_plantillas = os.path.join(DST_GUIA, "plantillas_codigo")
    os.makedirs(dir_plantillas, exist_ok=True)
    for fname, code_txt in cn.PLANTILLAS_ARCHIVOS.items():
        open(os.path.join(dir_plantillas, fname), "w", encoding="utf-8").write(code_txt)
    print("Creados 5 archivos fuente en plantillas_codigo/")


def normalizar(texto):
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", texto).strip().casefold()


def parsear_pdf_destinos_y_paginas(ruta_pdf, anclas):
    """Extrae en Python puro el mapa {ancla: pagina_1_based}, {ancla: page_obj_id} y total de páginas."""
    data = open(ruta_pdf, "rb").read()
    objs = {}
    for m in re.finditer(rb"(\d+)\s+0\s+obj\b(.*?)endobj", data, re.S):
        oid = int(m.group(1))
        body = m.group(2)
        if b"stream" not in body:
            objs[oid] = body

    cat_id = next(oid for oid, b in objs.items() if b"/Type /Catalog" in b)
    cat = objs[cat_id]
    pages_root = int(re.search(rb"/Pages\s+(\d+)\s+0\s+R", cat).group(1))
    dests_oid = int(re.search(rb"/Dests\s+(\d+)\s+0\s+R", cat).group(1))

    def walk_pages(oid):
        b = objs[oid]
        if b"/Type /Page\b" in b or b"/Type /Pages" not in b:
            return [oid]
        m = re.search(rb"/Kids\s*\[(.*?)\]", b, re.S)
        kids = [int(x) for x in re.findall(rb"(\d+)\s+0\s+R", m.group(1))]
        res = []
        for k in kids:
            res.extend(walk_pages(k))
        return res

    page_objs = walk_pages(pages_root)
    page_num_by_oid = {oid: idx + 1 for idx, oid in enumerate(page_objs)}

    dests_page = {}
    dests_oid_map = {}
    for name_b, p_oid_b in re.findall(rb"/([^\s\[]+)\s+\[(\d+)\s+0\s+R\b", objs[dests_oid]):
        name = name_b.decode("utf-8", errors="replace")
        p_oid = int(p_oid_b)
        dests_page[name] = page_num_by_oid[p_oid]
        dests_oid_map[name] = p_oid

    resultado = {}
    for a in anclas:
        if a not in dests_page:
            raise ValueError(f"No se encontró el destino PDF #{a}")
        resultado[a] = dests_page[a]

    return resultado, dests_oid_map, page_objs, len(page_objs)


def pdf_utf16_hex(texto):
    return b"<FEFF" + texto.encode("utf-16-be").hex().upper().encode("ascii") + b">"


def inyectar_outlines_puro(ruta_pdf, arbol_marcadores, dests_oid_map):
    """Inyecta el árbol /Outlines jerárquico en el PDF actualizando el Catalog y la tabla xref."""
    data = open(ruta_pdf, "rb").read()
    m_startxref = re.search(rb"startxref\s+(\d+)\s+%%EOF", data)
    assert m_startxref, "No se encontró startxref en el PDF"
    xref_pos = int(m_startxref.group(1))

    m_trailer = re.search(rb"trailer\s*<<(.*?)>>\s*startxref", data[xref_pos:], re.S)
    assert m_trailer, "No se encontró trailer"
    trailer_body = m_trailer.group(1)
    orig_size = int(re.search(rb"/Size\s+(\d+)", trailer_body).group(1))
    cat_oid = int(re.search(rb"/Root\s+(\d+)\s+0\s+R", trailer_body).group(1))
    info_m = re.search(rb"/Info\s+(\d+)\s+0\s+R", trailer_body)
    info_oid = int(info_m.group(1)) if info_m else 1

    # Parsear las entradas de la tabla xref original
    xref_lines = data[xref_pos:xref_pos + m_trailer.start()].splitlines()
    assert xref_lines[0].strip() == b"xref"
    entries = {}
    idx = 0
    for ln in xref_lines[1:]:
        ln = ln.strip()
        if not ln:
            continue
        parts = ln.split()
        if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
            idx = int(parts[0])
        elif len(parts) == 3:
            entries[idx] = (int(parts[0]), int(parts[1]), parts[2].decode("ascii"))
            idx += 1

    # Leer objeto Catalog original
    cat_offset = entries[cat_oid][0]
    m_cat = re.match(rb"\d+\s+0\s+obj\s*<<(.*?)>>\s*endobj", data[cat_offset:cat_offset + 2048], re.S)
    assert m_cat, "No se pudo leer Catalog original"
    cat_dict_inner = m_cat.group(1).strip()

    next_oid = orig_size
    outlines_root_oid = next_oid
    next_oid += 1

    nuevos_objetos = {}

    # Construir nodos top-level y sus hijos
    # arbol_marcadores = [(titulo, anchor_id, [(sub_titulo, sub_anchor), ...]), ...]
    top_oids = []
    for _tit, _anc, _children in arbol_marcadores:
        top_oids.append(next_oid)
        next_oid += 1

    total_visibles = len(top_oids)

    for i, (tit, anc, children) in enumerate(arbol_marcadores):
        my_oid = top_oids[i]
        p_oid = dests_oid_map[anc]
        partes_dict = [
            b"/Title " + pdf_utf16_hex(tit),
            f"/Parent {outlines_root_oid} 0 R".encode("ascii"),
            f"/Dest [{p_oid} 0 R /XYZ 0 841.92 0]".encode("ascii"),
        ]
        if i > 0:
            partes_dict.append(f"/Prev {top_oids[i - 1]} 0 R".encode("ascii"))
        if i < len(top_oids) - 1:
            partes_dict.append(f"/Next {top_oids[i + 1]} 0 R".encode("ascii"))

        if children:
            child_oids = []
            for _ctit, _canc in children:
                child_oids.append(next_oid)
                next_oid += 1
            partes_dict.append(f"/First {child_oids[0]} 0 R".encode("ascii"))
            partes_dict.append(f"/Last {child_oids[-1]} 0 R".encode("ascii"))
            partes_dict.append(f"/Count {len(child_oids)}".encode("ascii"))
            total_visibles += len(child_oids)

            for j, (ctit, canc) in enumerate(children):
                c_oid = child_oids[j]
                cp_oid = dests_oid_map[canc]
                c_partes = [
                    b"/Title " + pdf_utf16_hex(ctit),
                    f"/Parent {my_oid} 0 R".encode("ascii"),
                    f"/Dest [{cp_oid} 0 R /XYZ 0 841.92 0]".encode("ascii"),
                ]
                if j > 0:
                    c_partes.append(f"/Prev {child_oids[j - 1]} 0 R".encode("ascii"))
                if j < len(child_oids) - 1:
                    c_partes.append(f"/Next {child_oids[j + 1]} 0 R".encode("ascii"))
                nuevos_objetos[c_oid] = b"<<" + b"\n".join(c_partes) + b">>"

        nuevos_objetos[my_oid] = b"<<" + b"\n".join(partes_dict) + b">>"

    nuevos_objetos[outlines_root_oid] = (
        f"<</Type /Outlines\n/First {top_oids[0]} 0 R\n/Last {top_oids[-1]} 0 R\n/Count {total_visibles}>>".encode("ascii")
    )

    # Escribir los nuevos objetos a partir de xref_pos y reconstruir la tabla xref
    buf = bytearray(data[:xref_pos])

    # Nuevo Catalog con /Outlines
    nuevo_cat_body = cat_dict_inner + f"\n/Outlines {outlines_root_oid} 0 R".encode("ascii")
    entries[cat_oid] = (len(buf), 0, "n")
    buf.extend(f"{cat_oid} 0 obj\n<<".encode("ascii") + nuevo_cat_body + b">>\nendobj\n")

    for oid in sorted(nuevos_objetos.keys()):
        entries[oid] = (len(buf), 0, "n")
        buf.extend(f"{oid} 0 obj\n".encode("ascii") + nuevos_objetos[oid] + b"\nendobj\n")

    nuevo_xref_pos = len(buf)
    nuevo_size = next_oid
    buf.extend(f"xref\n0 {nuevo_size}\n".encode("ascii"))
    for i in range(nuevo_size):
        off, gen, st = entries.get(i, (0, 65535 if i == 0 else 0, "f"))
        buf.extend(f"{off:010d} {gen:05d} {st} \n".encode("ascii"))

    buf.extend(
        f"trailer\n<</Size {nuevo_size}\n/Root {cat_oid} 0 R\n/Info {info_oid} 0 R>>\nstartxref\n{nuevo_xref_pos}\n%%EOF\n".encode("ascii")
    )
    open(ruta_pdf, "wb").write(buf)
    print(f"  marcadores PDF (/Outlines) inyectados: {total_visibles} entradas")


def generar_pdf_completo():
    sys.path.insert(0, os.path.join(DST_GUIA, "_trabajo"))
    import build as build_mod  # noqa: E402

    LECCIONES = [
        ("guia/00-laboratorio.html", "0.1 Laboratorio"),
        ("guia/01-numeros.html", "1.1 Números y hexadecimal"),
        ("guia/01-memoria.html", "1.2 Memoria y stack"),
        ("guia/01-procesos.html", "1.3 Procesos e hilos"),
        ("guia/01-pe.html", "1.4 Formato PE"),
        ("guia/01-c-python.html", "1.5 C y Python"),
        ("guia/02-registros.html", "2.1 Registros y flags"),
        ("guia/02-instrucciones.html", "2.2 Instrucciones"),
        ("guia/02-flotante.html", "2.3 Punto flotante y SSE"),
        ("guia/02-flujo.html", "2.4 Flujo"),
        ("guia/02-llamadas.html", "2.5 Llamadas"),
        ("guia/02-debugger.html", "2.6 Debugger"),
        ("guia/02-ida.html", "2.7 IDA"),
        ("guia/02-optimizaciones.html", "2.8 Optimizaciones"),
        ("guia/02-herramientas.html", "2.9 Herramientas"),
        ("guia/02-ofuscacion.html", "2.10 Ofuscación nativa"),
        ("guia/02-tls.html", "2.11 TLS callbacks"),
        ("guia/02-mfc.html", "2.12 MFC"),
        ("guia/02-huella-compilador.html", "2.13 Huella de compilador"),
        ("guia/02-pe-fino.html", "2.14 PE fino"),
        ("guia/02-anti-analisis.html", "2.15 Taxonomía anti-análisis"),
        ("guia/02-ghidra.html", "2.16 Ghidra/Cutter"),
        ("guia/02-packers.html", "2.17 Packers didácticos"),
        ("guia/02-cpp-profundo.html", "2.18 C++ profundo"),
        ("guia/02-windbg-heap.html", "2.19 WinDbg, TTD y heap"),
        ("guia/02-patch-diffing.html", "2.20 Patch diffing y CVE"),
        ("guia/02-scripting-debugger.html", "2.21 Scripting de debugger"),
        ("guia/02-opt-malware-dinamico.html", "2.22 (opt) Malware dinámico"),
        ("guia/02-opt-shellcode-c2.html", "2.23 (opt) Shellcode, red y C2"),
        ("guia/02-opt-fuzzing.html", "2.24 (opt) Fuzzing y simbólico"),
        ("guia/03-dotnet-runtime.html", "3.1 .NET runtime"),
        ("guia/03-dotnet-il.html", "3.2 Leer IL"),
        ("guia/04-metodo.html", "4.1 Método de análisis"),
        ("guia/04-cripto.html", "4.2 Reconocer criptografía"),
        ("guia/04-informe.html", "4.3 Informe"),
        ("guia/04-dinamico-seguro.html", "4.4 Dinámico seguro"),
        ("guia/04-formatos-protocolos.html", "4.5 Reconstruir formatos y protocolos"),
        ("guia/05-malware.html", "5.1 Malware"),
        ("guia/05-vulnerabilidades.html", "5.2 Vulnerabilidades"),
        ("guia/05-automatizacion.html", "5.3 Automatización"),
        ("guia/05-fuera-de-alcance.html", "5.4 Fuera de alcance"),
        ("guia/6-01-arquitectura-kernel.html", "6.1 Arquitectura del kernel"),
        ("guia/6-02-kmdf-ioctl.html", "6.2 KMDF e IOCTL inocuo"),
        ("guia/6-03-debug-kernel.html", "6.3 Debugging de kernel"),
        ("guia/6-04-revision-driver.html", "6.4 Revisión defensiva de drivers"),
        ("guia/6-05-minifilters.html", "6.5 Minifilters"),
        ("guia/6-06-mitigaciones.html", "6.6 Mitigaciones para drivers"),
    ]

    ETAPAS = [
        ("guia/etapa-0.html", "Etapa 0 · Laboratorio"),
        ("guia/etapa-1.html", "Etapa 1 · Fundamentos"),
        ("guia/etapa-2.html", "Etapa 2 · Reversing"),
        ("guia/etapa-3.html", "Etapa 3 · .NET"),
        ("guia/etapa-4.html", "Etapa 4 · Práctica"),
        ("guia/etapa-5.html", "Etapa 5 · Ramas"),
        ("guia/etapa-6.html", "Etapa 6 · Rama optativa: Kernel y drivers"),
    ]

    RAMA_2D = [
        ("2d.html", "2D · Windows internals (optativa)"),
        ("guia/2d-01-objetos.html", "2D.1 Objetos y tokens"),
        ("guia/2d-02-memoria-loader.html", "2D.2 Memoria y loader"),
        ("guia/2d-03-registro.html", "2D.3 Registro"),
        ("guia/2d-04-servicios.html", "2D.4 Servicios"),
        ("guia/2d-05-task-scheduler.html", "2D.5 Task Scheduler"),
        ("guia/2d-06-com-interfaces.html", "2D.6 COM interfaces"),
        ("guia/2d-07-com-activacion.html", "2D.7 COM activación"),
        ("guia/2d-08-dcom-rpc.html", "2D.8 DCOM y RPC"),
        ("guia/2d-09-wmi.html", "2D.9 WMI"),
        ("guia/2d-10-ipc.html", "2D.10 IPC"),
        ("guia/2d-11-excepciones.html", "2D.11 Excepciones"),
        ("guia/2d-12-etw.html", "2D.12 ETW"),
        ("guia/2d-13-integrador.html", "2D.13 Integrador"),
        ("2d-hyperv.html", "Extensión optativa Hyper-V"),
    ]

    FICHAS = [
        "reversing-desde-cero", "ida-desde-cero", "masm32-cayetano", "ollydbg-cayetano",
        "python-iso", "reverse-engineering-ricardo", "teorias-numeradas", "ida-pro-docx",
        "inventario-limpio", "chat-unido", "transcripciones-telegram", "scenere-docs",
        "exploiting-contenedores", "malware-virus", "themida",
        "zips-anteriores", "exportacion-sesion", "plan-estudio-historico", "curso-reversing-2020",
    ]

    def ancla(rel):
        return "sec-" + re.sub(r"[^a-zA-Z0-9]+", "-", rel.replace(".html", "")).strip("-")

    def contenido(rel):
        with open(os.path.join(DST_GUIA, rel.replace("/", os.sep)), encoding="utf-8") as f:
            h = f.read()
        m = re.search(r'<main id="contenido">(.*?)</main>', h, re.S)
        if not m:
            raise ValueError(rel)
        cuerpo = m.group(1)
        cuerpo = re.sub(r'<nav class="migas".*?</nav>', "", cuerpo, flags=re.S)
        cuerpo = re.sub(r'<div class="pager">.*?</div>', "", cuerpo, flags=re.S)
        cuerpo = re.sub(r'<aside class="callout[^"]*"><p class="callout-titulo">Volver</p>.*?</aside>', "", cuerpo, flags=re.S)
        # Evitar colisión de id="fuentes" en subtítulos internos con la sección final #fuentes
        cuerpo = cuerpo.replace('<h2 id="fuentes">', '<h2>')
        cuerpo = cuerpo.replace("<details", "<details open")
        return cuerpo

    def limpiar_enlaces(html_str, mapa):
        def rep(m):
            clase = m.group(1) or ""
            href = m.group(2)
            texto = m.group(3)
            if href.startswith(("http://", "https://", "mailto:")):
                return f'<a href="{href}">{texto}</a>'
            if "fuente" in clase:
                return f'<span class="fuente">{texto}</span>'
            if href in mapa:
                return f'<a href="#{mapa[href]}">{texto}</a>'
            if href.startswith("#"):
                return f'<a href="{href}">{texto}</a>'
            return f"<span>{texto}</span>"

        return re.sub(
            r'<a(?:\s+class="([^"]*)")?\s+href="([^"]+)"[^>]*>(.*?)</a>',
            rep, html_str, flags=re.S,
        )

    toc_anchors = []
    page_labels = {}

    def ref(anchor_id):
        return f'<span class="toc-pag" data-anchor="{anchor_id}">{page_labels.get(anchor_id, "calculando")}</span>'

    def row(anchor_id, title):
        toc_anchors.append(anchor_id)
        return f'<li><a href="#{anchor_id}">{title}</a>{ref(anchor_id)}</li>'

    def heading(anchor_id, title):
        toc_anchors.append(anchor_id)
        return f'<div class="etapa"><a href="#{anchor_id}">{title}</a>{ref(anchor_id)}</div>'

    mapa = {}
    for rel, _ in LECCIONES + ETAPAS:
        mapa[rel] = ancla(rel)
        mapa[os.path.basename(rel)] = ancla(rel)
    for rel, _ in RAMA_2D:
        mapa[rel] = ancla(rel)
        mapa[os.path.basename(rel)] = ancla(rel)
    mapa["../2d.html"] = ancla("2d.html")
    mapa["../2d-hyperv.html"] = ancla("2d-hyperv.html")
    mapa["../guia/etapa-6.html"] = ancla("guia/etapa-6.html")
    for slug in FICHAS:
        mapa[f"fichas/{slug}.html"] = "ficha-" + slug
    mapa["fichas/index.html"] = "fichas"
    mapa["hilo-conductor-y-plantillas.html"] = "hilo-plantillas"
    mapa["../hilo-conductor-y-plantillas.html"] = "hilo-plantillas"
    mapa["hojas-referencia-rapida.html"] = "hojas-referencia"
    mapa["../hojas-referencia-rapida.html"] = "hojas-referencia"
    mapa["glosario.html"] = "glosario"
    mapa["../glosario.html"] = "glosario"
    mapa["preguntas_y_respuestas.html"] = "preguntas"
    mapa["../preguntas_y_respuestas.html"] = "preguntas"
    mapa["fuentes_y_limites.html"] = "fuentes"
    mapa["../fuentes_y_limites.html"] = "fuentes"
    mapa["00_EMPEZAR_AQUI.html"] = "portada-texto"
    mapa["../00_EMPEZAR_AQUI.html"] = "portada-texto"
    mapa["guia/index.html"] = "mapa-curso"
    mapa["index.html"] = "mapa-curso"
    mapa["videos.html"] = "videos"

    css = open(os.path.join(DST_GUIA, "guia", "estilo.css"), encoding="utf-8").read()
    css_print = """
@page {
  size: A4;
  margin: 18mm 16mm 20mm 16mm;
  @bottom-center {
    content: counter(page);
    font-family: Helvetica, Arial, sans-serif;
    font-size: 8pt;
    color: #666666;
  }
}
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { background: #fff; font-size: 10.5pt; line-height: 1.5; }
main { max-width: none; padding: 0; }
.print-sec { break-before: page; }
.print-sec:first-of-type { break-before: auto; }
.print-sec h1 { font-size: 20pt; margin-top: 0; }
.print-sec h2 { font-size: 13pt; margin-top: 1.4em; }
.print-sec h3 { font-size: 11.5pt; }
.print-sec pre { font-size: 8.3pt; white-space: pre-wrap; break-inside: avoid; page-break-inside: avoid; }
.print-sec pre.arbol-triage { font-size: 6.5pt; line-height: 1.17; padding: 6px 10px; margin: 4px 0; }
.print-sec table { font-size: 8.6pt; width: 100%; table-layout: auto; word-wrap: break-word; overflow-wrap: break-word; word-break: normal; }
.print-sec th, .print-sec td { overflow-wrap: break-word; word-break: normal; hyphens: none; }
.print-sec td:not(:first-child) code, .print-sec th:not(:first-child) code { word-break: break-word; }
.print-sec .tabla { overflow-x: visible !important; break-inside: avoid; page-break-inside: avoid; }
.print-sec tr { break-inside: avoid; page-break-inside: avoid; }
.print-sec .callout, .print-sec .gate, .print-sec details, .print-sec .ampliacion-ext, .print-sec .nota-ed { break-inside: avoid; page-break-inside: avoid; }
.print-sec h2, .print-sec h3, .print-sec h4 { break-after: avoid; page-break-after: avoid; }
.print-sec a { color: #000; text-decoration: none; }
.hoja-compacta { font-size: 8.5pt; line-height: 1.25; }
.hoja-compacta h2 { font-size: 11pt !important; margin: 0 0 4pt !important; border-bottom: 1px solid #0b5f6b; padding-bottom: 2pt; color: #0b5f6b; }
.hoja-compacta h3 { font-size: 9.3pt !important; margin: 4pt 0 2pt !important; color: #222; }
.hoja-compacta table { font-size: 7.6pt !important; margin: 2px 0 4px !important; }
.hoja-compacta th, .hoja-compacta td { padding: 2px 4px !important; }
.hoja-compacta pre { font-size: 7.2pt !important; line-height: 1.15 !important; margin: 2px 0 !important; padding: 2px 4px !important; }
.hoja-compacta ul, .hoja-compacta p { margin: 2px 0 3px !important; }
.hoja-compacta li { margin-bottom: 2px !important; }
.portada-pdf { text-align: left; padding-top: 26mm; }
.portada-pdf .kicker { color: #0b5f6b; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; font-size: 9pt; }
.portada-pdf h1 { font-size: 34pt; line-height: 1.05; margin: .2em 0 .3em; }
.portada-pdf .sub { font-size: 12.5pt; color: #333; max-width: 155mm; }
.portada-pdf .aviso { border-left: 4px solid #8a1c1c; background: #fbe7e7; padding: 8pt 10pt; margin: 16pt 0; font-size: 9.5pt; }
.toc { margin-top: 14pt; columns: 2; column-gap: 12mm; font-size: 9.8pt; }
.toc h2 { column-span: all; border-bottom: 1px solid #999; }
.toc ol { margin: 0; padding-left: 16pt; }
.toc li { display: flex; align-items: baseline; gap: 5pt; margin: 2pt 0; break-inside: avoid; }
.toc li a { flex: 1; min-width: 0; }
.toc-pag { white-space: nowrap; font-size: 8pt; color: #444; }
.toc .etapa { display: flex; justify-content: space-between; gap: 5pt; font-weight: 700; margin-top: 6pt; color: #0b5f6b; break-inside: avoid; }
.toc .etapa a { color: inherit; text-decoration: none; }
details.qa { padding: 4pt 6pt; margin: 4pt 0; }
details.qa summary { font-size: 10pt; }
"""

    partes = [f'<!doctype html><html lang="es"><head><meta charset="utf-8"><title>CLS · Curso de reversing</title><style>{css}\n{css_print}</style></head><body><main>']

    partes.append("""
<section class="print-sec portada-pdf" id="portada">
<p class="kicker">Proyecto CLS · Edición 5 · Revisión 5.4 (Ampliada)</p>
<h1>Curso de reversing</h1>
<p class="sub">De los fundamentos al análisis guiado. Un curso en español, progresivo y verificable, construido a partir del material del proyecto CLS.</p>
<p class="sub"><strong>Actualizado 29 de octubre de 2026</strong> · Ruta base: Etapas 0–4 · Optativas: Etapas 5–6 y rama 2D de la Etapa 2</p>
<p class="sub">Incluye 3 perfiles o rutas de estudio (Principiante, Intermedio y Avanzado), Árbol de decisión de triage inicial, Hilo conductor multi-nivel (<code>check.c</code> &rarr; <code>BlocLab</code>), Kit de 5 plantillas C/C++ listas para compilar y 3 Hojas de referencia rápida (<em>Cheat Sheets</em>).</p>
<p class="sub"><em>Edición de estudio — teoría y referencia práctica. Para abrir los videos, los tutes ilustrados de IDA, el banco de prácticas, las transcripciones, los audios y el buscador usá la versión <strong>HTML</strong> del curso, entrando por <code>00_EMPEZAR_AQUI.html</code>.</em></p>
<div class="aviso"><strong>Material educativo y defensivo.</strong> Las prácticas usan programas propios, software abierto o crackmes diseñados para aprender. No se enseña a eludir licencias, DRM ni controles de acceso. No se ejecutaron binarios del corpus ni se extrajeron comprimidos.</div>
<p class="sub">Esta edición es una cobertura parcial y declarada del corpus. Lo que falta está en <em>Fuentes y límites</em>, al final del documento.</p>
</section>
""")

    toc = ['<section class="print-sec" id="toc"><h1>Contenido</h1><div class="toc">']
    toc.append('<div class="etapa">Apertura</div><ol>')
    toc.append(row("portada-texto", "Cómo estudiar y qué se revisó"))
    toc.append(row("mapa-curso", "Mapa del curso y rutas de estudio"))
    toc.append('</ol>')

    orden = [
        ("Etapa 0", ["guia/00-laboratorio.html"]),
        ("Etapa 1", ["guia/01-numeros.html", "guia/01-memoria.html", "guia/01-procesos.html", "guia/01-pe.html", "guia/01-c-python.html"]),
        ("Etapa 2", ["guia/02-registros.html", "guia/02-instrucciones.html", "guia/02-flotante.html", "guia/02-flujo.html", "guia/02-llamadas.html", "guia/02-debugger.html", "guia/02-ida.html", "guia/02-optimizaciones.html", "guia/02-herramientas.html", "guia/02-ofuscacion.html", "guia/02-tls.html", "guia/02-mfc.html", "guia/02-huella-compilador.html", "guia/02-pe-fino.html", "guia/02-anti-analisis.html", "guia/02-ghidra.html", "guia/02-packers.html", "guia/02-cpp-profundo.html", "guia/02-windbg-heap.html", "guia/02-patch-diffing.html", "guia/02-scripting-debugger.html", "guia/02-opt-malware-dinamico.html", "guia/02-opt-shellcode-c2.html", "guia/02-opt-fuzzing.html"]),
        ("Etapa 3", ["guia/03-dotnet-runtime.html", "guia/03-dotnet-il.html"]),
        ("Etapa 4", ["guia/04-metodo.html", "guia/04-cripto.html", "guia/04-informe.html", "guia/04-dinamico-seguro.html", "guia/04-formatos-protocolos.html"]),
        ("Etapa 5", ["guia/05-malware.html", "guia/05-vulnerabilidades.html", "guia/05-automatizacion.html", "guia/05-fuera-de-alcance.html"]),
        ("Etapa 6 · Rama optativa", ["guia/6-01-arquitectura-kernel.html", "guia/6-02-kmdf-ioctl.html", "guia/6-03-debug-kernel.html", "guia/6-04-revision-driver.html", "guia/6-05-minifilters.html", "guia/6-06-mitigaciones.html"]),
    ]
    nombres = dict(LECCIONES)
    for etapa, lecs in orden:
        numero = re.search(r"\d+", etapa).group(0)
        toc.append(heading(mapa[f"guia/etapa-{numero}.html"], etapa) + '<ol>')
        for rel in lecs:
            toc.append(row(mapa[rel], nombres[rel]))
        toc.append('</ol>')

    toc.append(heading(mapa["2d.html"], "2D · Windows internals (optativa)") + '<ol>')
    for rel, titulo in RAMA_2D:
        if rel == "2d.html":
            continue
        toc.append(row(mapa[rel], titulo))
    toc.append('</ol>')

    toc.append('<div class="etapa">Material de apoyo</div><ol>')
    toc.append(row("hilo-plantillas", "Hilo conductor y plantillas C/C++"))
    toc.append(row("hojas-referencia", "Hojas de referencia rápida (Cheat Sheets)"))
    toc.append(row("glosario", "Glosario"))
    toc.append(row("preguntas", "Preguntas y respuestas"))
    toc.append(row("fuentes", "Fuentes y límites"))
    toc.append('</ol></div></section>')
    partes.append("".join(toc))

    # Apertura
    for rel, anchor in [("00_EMPEZAR_AQUI.html", "portada-texto"), ("guia/index.html", "mapa-curso")]:
        h = limpiar_enlaces(contenido(rel), mapa)
        partes.append(f'<section class="print-sec" id="{anchor}">{h}</section>')

    # Etapas y lecciones
    for rel, _ in ETAPAS:
        h = limpiar_enlaces(contenido(rel), mapa)
        partes.append(f'<section class="print-sec" id="{mapa[rel]}">{h}</section>')
        etapa_num = rel.split("-")[-1].replace(".html", "")
        pref = f"guia/{etapa_num}-" if etapa_num == "6" else f"guia/0{etapa_num}-"
        lecs = [x for x in LECCIONES if x[0].startswith(pref)]
        for lrel, _ in lecs:
            lh = limpiar_enlaces(contenido(lrel), mapa)
            partes.append(f'<section class="print-sec" id="{mapa[lrel]}">{lh}</section>')

    # Rama 2D
    for rel, _titulo in RAMA_2D:
        h = limpiar_enlaces(contenido(rel), mapa)
        partes.append(f'<section class="print-sec" id="{mapa[rel]}">{h}</section>')

    # Material de apoyo: Hilo conductor + plantillas, Cheat Sheets, Glosario y Preguntas
    for rel, anchor in [
        ("hilo-conductor-y-plantillas.html", "hilo-plantillas"),
        ("hojas-referencia-rapida.html", "hojas-referencia"),
        ("glosario.html", "glosario"),
        ("preguntas_y_respuestas.html", "preguntas"),
    ]:
        h = limpiar_enlaces(contenido(rel), mapa)
        if anchor == "preguntas":
            h = h.replace('<details class="qa">', '<details class="qa" open>')
        partes.append(f'<section class="print-sec" id="{anchor}">{h}</section>')

    # Fuentes y límites
    with open(os.path.join(DST_GUIA, "FUENTES_Y_LIMITES.md"), encoding="utf-8") as f:
        fuentes_md = f.read()
    fuentes_html = limpiar_enlaces(build_mod.md(fuentes_md), mapa)
    partes.append(f'<section class="print-sec" id="fuentes"><h1>Fuentes y límites</h1>{fuentes_html}</section>')

    partes.append("</main></body></html>")

    salida_html = os.path.join(DST_GUIA, "_trabajo", "print", "CLS_Curso_Reversing_imprimible.html")
    os.makedirs(os.path.dirname(salida_html), exist_ok=True)
    draft_pdf = os.path.join(DST_GUIA, "_trabajo", "print", "CLS_Curso_Reversing_borrador.pdf")
    salida_pdf = os.path.join(DST_GUIA, "CLS_Curso_Reversing.pdf")

    html_documento = "\n".join(partes)

    def etiquetas_paginas(anclas, paginas, total):
        etiquetas = {}
        for i, ancla_id in enumerate(anclas):
            inicio = paginas[ancla_id]
            fin = total
            for siguiente in anclas[i + 1:]:
                if paginas[siguiente] > inicio:
                    fin = paginas[siguiente] - 1
                    break
            cantidad = fin - inicio + 1
            rango = str(inicio) if inicio == fin else f"{inicio}-{fin}"
            unidad = "pág." if cantidad == 1 else "págs."
            etiquetas[ancla_id] = f"p. {rango} · {cantidad} {unidad}"
        return etiquetas

    def reemplazar_etiquetas(html_s, etiquetas):
        def rep(m):
            ancla_id = m.group(1)
            texto = etiquetas.get(ancla_id, "páginas pendientes")
            return f'<span class="toc-pag" data-anchor="{ancla_id}">{texto}</span>'
        return re.sub(
            r'<span class="toc-pag" data-anchor="([^"]+)">.*?</span>',
            rep, html_s, flags=re.S,
        )

    def renderizar(ruta_html, ruta_pdf):
        cmd = [
            CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
            "--user-data-dir=" + os.path.join(SCRATCH_BRAIN, "chrome-prof"),
            "--allow-file-access-from-files", "--virtual-time-budget=15000",
            "--no-pdf-header-footer", "--print-to-pdf-no-header",
            f"--print-to-pdf={ruta_pdf}",
            "file:///" + ruta_html.replace("\\", "/"),
        ]
        subprocess.run(cmd, check=True)

    etiquetas = {}
    paginas = {}
    dests_oid_map = {}
    total = 0
    print("\nGenerando PDF con Chrome Headless e iterando el índice paginado...")
    for intento in range(5):
        with open(salida_html, "w", encoding="utf-8") as f:
            f.write(html_documento)
        renderizar(salida_html, draft_pdf)
        paginas, dests_oid_map, _page_objs, total = parsear_pdf_destinos_y_paginas(draft_pdf, toc_anchors)
        nuevas = etiquetas_paginas(toc_anchors, paginas, total)
        print(f"  Intento {intento + 1}: {total} páginas | {len(nuevas)} destinos TOC")
        if intento > 0 and nuevas == etiquetas:
            break
        etiquetas = nuevas
        html_documento = reemplazar_etiquetas(html_documento, etiquetas)
    else:
        raise RuntimeError("El índice paginado no se estabilizó tras cinco generaciones")

    # Construir el árbol de marcadores (Outline) idéntico a pdf.py + las 2 nuevas secciones
    arbol_marcadores = [
        ("Portada", "portada-texto", []),
        ("Mapa del curso y rutas de estudio", "mapa-curso", []),
    ]
    for erel, etit in ETAPAS:
        mnum = re.search(r"etapa-(\d)", erel)
        hijos = []
        if mnum:
            pref = f"{mnum.group(1)}-" if mnum.group(1) == "6" else f"0{mnum.group(1)}-"
            for lrel, ltit in LECCIONES:
                if os.path.basename(lrel).startswith(pref):
                    hijos.append((ltit, ancla(lrel)))
        arbol_marcadores.append((etit, ancla(erel), hijos))

    hijos_2d = [(titulo, ancla(rel)) for rel, titulo in RAMA_2D if rel != "2d.html"]
    arbol_marcadores.append(("2D · Windows internals (optativa)", ancla("2d.html"), hijos_2d))
    arbol_marcadores.append(("Hilo conductor y plantillas C/C++", "hilo-plantillas", []))
    arbol_marcadores.append(("Hojas de referencia rápida (Cheat Sheets)", "hojas-referencia", []))
    arbol_marcadores.append(("Glosario", "glosario", []))
    arbol_marcadores.append(("Preguntas y respuestas", "preguntas", []))
    arbol_marcadores.append(("Fuentes y límites", "fuentes", []))

    total_contenido = total
    if total % 2 == 1:
        print(f"  [Edición Completa] Total impar ({total} págs.) -> agregando 1 página de Bitácora/Colofón para paridad doble faz...")
        html_documento = html_documento.replace(
            "</main></body></html>",
            bloque_colofon_notas("Edición Completa") + "\n</main></body></html>",
        )
        with open(salida_html, "w", encoding="utf-8") as f:
            f.write(html_documento)
        renderizar(salida_html, draft_pdf)
        paginas, dests_oid_map, _page_objs, total = parsear_pdf_destinos_y_paginas(
            draft_pdf, toc_anchors
        )
        print(f"  [Edición Completa] Nuevo total par: {total} páginas ({total // 2} hojas a doble faz)")

    inyectar_outlines_puro(draft_pdf, arbol_marcadores, dests_oid_map)
    os.replace(draft_pdf, salida_pdf)

    # Copiar a las variantes de nombre para comodidad del usuario
    pdf_v51 = os.path.join(DST_GUIA, "CLS_Curso_Reversing_v5.1_Ampliada.pdf")
    pdf_v54 = os.path.join(DST_GUIA, "CLS_Curso_Reversing_v5.4_Ampliada.pdf")
    pdf_artifact = os.path.join(ARTIFACT_DIR, "CLS_Curso_Reversing_v5.4_Ampliada.pdf")
    html_v54 = os.path.join(DST_GUIA, "CLS_Curso_Reversing_v5.4_Ampliada.html")

    shutil.copy2(salida_pdf, pdf_v51)
    shutil.copy2(salida_pdf, pdf_v54)
    shutil.copy2(salida_pdf, pdf_artifact)
    shutil.copy2(salida_html, html_v54)

    print(f"\nPDF FINAL GENERADO: {salida_pdf} ({os.path.getsize(salida_pdf):,} bytes, {total} páginas)")
    print(f"Copia en Artifact Dir: {pdf_artifact}")

    # Verificación automática de rangos TOC
    problemas = []
    orden_anc = list(toc_anchors)
    for i, anc in enumerate(orden_anc):
        lab = etiquetas[anc]
        m = re.match(r"p\. (\d+)(?:-(\d+))? · (\d+) p", lab)
        if not m:
            problemas.append(("etiqueta ilegible", anc, lab))
            continue
        a, b, n = int(m.group(1)), int(m.group(2) or m.group(1)), int(m.group(3))
        if b - a + 1 != n:
            problemas.append(("cantidad incoherente", anc, lab))
        if paginas[anc] != a:
            problemas.append(("inicio != destino", anc, lab, paginas[anc]))
        sig = next((paginas[s] for s in orden_anc[i + 1:] if paginas[s] > a), total_contenido + 1)
        if b != sig - 1:
            problemas.append(("fin de rango", anc, a, b, sig - 1))

    print("VERIFICACIÓN DE ÍNDICE Y PÁGINAS — PROBLEMAS:", len(problemas))
    for p in problemas:
        print(" ", p)

    return {
        "paginas": paginas,
        "etiquetas": etiquetas,
        "total": total,
        "total_contenido": total_contenido,
        "mapa": mapa,
        "css": css,
        "css_print": css_print,
        "contenido_fn": contenido,
        "limpiar_enlaces_fn": limpiar_enlaces,
        "etiquetas_paginas_fn": etiquetas_paginas,
        "reemplazar_etiquetas_fn": reemplazar_etiquetas,
        "renderizar_fn": renderizar,
        "LECCIONES": LECCIONES,
        "ETAPAS": ETAPAS,
        "RAMA_2D": RAMA_2D,
        "ancla_fn": ancla,
        "build_mod": build_mod,
    }


def bloque_colofon_notas(titulo_volumen):
    return f"""
<section class="print-sec" id="colofon-notas">
<h1>Bitácora de laboratorio y notas — {titulo_volumen}</h1>
<p><em>Esta página cierra el último pliego en paridad par (múltiplo de 2) para impresión profesional a doble faz en gráfica y sirve como registro rápido de parámetros de tu entorno de laboratorio.</em></p>
<div class="tabla"><table>
<thead><tr>
<th>Parámetro del entorno / VM</th>
<th>Valor configurado en tu laboratorio</th>
<th>Notas / Comandos frecuentes</th>
</tr></thead><tbody>
<tr><td><strong>Snapshot base de la VM</strong></td><td>&nbsp;<br>&nbsp;</td><td>Verificar red aislada (<em>Host-Only</em> / desconectada) antes de abrir muestras</td></tr>
<tr><td><strong>Ruta de símbolos (<code>_NT_SYMBOL_PATH</code>)</strong></td><td>&nbsp;<br>&nbsp;</td><td><code>srv*C:\\Symbols*https://msdl.microsoft.com/download/symbols</code></td></tr>
<tr><td><strong>Compilador MSVC / MinGW-w64</strong></td><td>&nbsp;<br>&nbsp;</td><td>x64 Native Tools Command Prompt / <code>cl /Zi /Od</code> vs <code>cl /Zi /O2</code></td></tr>
<tr><td><strong>VM de depuración Kernel (KDNET)</strong></td><td>&nbsp;<br>&nbsp;</td><td><code>bcdedit /debug on</code> · <code>bcdedit /dbgsettings net hostip:... port:50000</code></td></tr>
</tbody></table></div>
<h2>Registro de sesiones, direcciones clave (RVA / VA) e hipótesis</h2>
<div class="tabla"><table>
<thead><tr>
<th>Fecha / Binario</th>
<th>SHA-256 / Arquitectura</th>
<th>RVA clave (<code>OEP</code> / <code>main</code> / <code>vtable</code> / <code>IOCTL</code>)</th>
<th>Observaciones y conclusiones verificadas</th>
</tr></thead><tbody>
<tr><td>&nbsp;<br>&nbsp;<br>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr>
<tr><td>&nbsp;<br>&nbsp;<br>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr>
<tr><td>&nbsp;<br>&nbsp;<br>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr>
<tr><td>&nbsp;<br>&nbsp;<br>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr>
<tr><td>&nbsp;<br>&nbsp;<br>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr>
<tr><td>&nbsp;<br>&nbsp;<br>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr>
</tbody></table></div>
</section>
"""


def compilar_volumen_pdf(
    nombre_interno,
    titulo_volumen,
    html_documento,
    toc_anchors,
    arbol_marcadores,
    ctx,
    asegurar_par=True,
):
    salida_html = os.path.join(DST_GUIA, "_trabajo", "print", f"{nombre_interno}.html")
    draft_pdf = os.path.join(DST_GUIA, "_trabajo", "print", f"{nombre_interno}_borrador.pdf")
    salida_pdf = os.path.join(DST_GUIA, f"{nombre_interno}.pdf")
    artifact_pdf = os.path.join(ARTIFACT_DIR, f"{nombre_interno}.pdf")

    etiquetas = {}
    paginas = {}
    dests_oid_map = {}
    total = 0
    print(f"\n[{nombre_interno}] Generando PDF con Chrome Headless e iterando el índice paginado...")
    for intento in range(5):
        with open(salida_html, "w", encoding="utf-8") as f:
            f.write(html_documento)
        ctx["renderizar_fn"](salida_html, draft_pdf)
        paginas, dests_oid_map, _page_objs, total = parsear_pdf_destinos_y_paginas(draft_pdf, toc_anchors)
        nuevas = ctx["etiquetas_paginas_fn"](toc_anchors, paginas, total)
        print(f"  Intento {intento + 1}: {total} páginas | {len(nuevas)} destinos TOC")
        if intento > 0 and nuevas == etiquetas:
            break
        etiquetas = nuevas
        html_documento = ctx["reemplazar_etiquetas_fn"](html_documento, etiquetas)
    else:
        raise RuntimeError(f"[{nombre_interno}] El índice paginado no se estabilizó tras cinco generaciones")

    total_contenido = total
    # Si el total de páginas es impar y se solicita paridad para doble faz, agregamos la bitácora final de 1 página
    if asegurar_par and (total % 2 == 1):
        print(f"  [{nombre_interno}] Total impar ({total} págs.) -> agregando 1 página de Bitácora/Colofón para paridad doble faz...")
        html_documento = html_documento.replace(
            "</main></body></html>",
            bloque_colofon_notas(titulo_volumen) + "\n</main></body></html>",
        )
        with open(salida_html, "w", encoding="utf-8") as f:
            f.write(html_documento)
        ctx["renderizar_fn"](salida_html, draft_pdf)
        paginas, dests_oid_map, _page_objs, total = parsear_pdf_destinos_y_paginas(
            draft_pdf, toc_anchors
        )
        print(f"  [{nombre_interno}] Nuevo total par: {total} páginas ({total // 2} hojas a doble faz)")

    inyectar_outlines_puro(draft_pdf, arbol_marcadores, dests_oid_map)
    os.replace(draft_pdf, salida_pdf)
    shutil.copy2(salida_pdf, artifact_pdf)

    # Verificar exactitud del TOC respecto de total_contenido
    problemas = []
    orden_anc = list(toc_anchors)
    for i, anc in enumerate(orden_anc):
        lab = etiquetas[anc]
        m = re.match(r"p\. (\d+)(?:-(\d+))? · (\d+) p", lab)
        if not m:
            problemas.append(("etiqueta ilegible", anc, lab))
            continue
        a, b, n = int(m.group(1)), int(m.group(2) or m.group(1)), int(m.group(3))
        if b - a + 1 != n:
            problemas.append(("cantidad incoherente", anc, lab))
        if paginas[anc] != a:
            problemas.append(("inicio != destino", anc, lab, paginas[anc]))
        sig = next((paginas[s] for s in orden_anc[i + 1:] if paginas[s] > a), total_contenido + 1)
        if b != sig - 1:
            problemas.append(("fin de rango", anc, a, b, sig - 1))

    print(f"[{nombre_interno}] PDF FINAL: {salida_pdf} ({os.path.getsize(salida_pdf):,} bytes, {total} págs., PROBLEMAS TOC: {len(problemas)})")
    for p in problemas:
        print(" ", p)

    return {
        "salida_pdf": salida_pdf,
        "artifact_pdf": artifact_pdf,
        "paginas": paginas,
        "etiquetas": etiquetas,
        "total": total,
        "total_contenido": total_contenido,
    }


def generar_tomos_y_separata(ctx):
    LECCIONES = ctx["LECCIONES"]
    ETAPAS = ctx["ETAPAS"]
    RAMA_2D = ctx["RAMA_2D"]
    ancla = ctx["ancla_fn"]
    build_mod = ctx["build_mod"]
    mapa = ctx["mapa"]
    css = ctx["css"]
    css_print = ctx["css_print"]
    contenido = ctx["contenido_fn"]
    limpiar_enlaces = ctx["limpiar_enlaces_fn"]
    nombres = dict(LECCIONES)

    # =========================================================================
    # 1. TOMO I — TRONCO PRINCIPAL (ETAPAS 0 A 5) Y MATERIAL DE APOYO
    # =========================================================================
    t1_anchors = []

    def t1_ref(aid):
        return f'<span class="toc-pag" data-anchor="{aid}">calculando</span>'

    def t1_row(aid, title):
        t1_anchors.append(aid)
        return f'<li><a href="#{aid}">{title}</a>{t1_ref(aid)}</li>'

    def t1_heading(aid, title):
        t1_anchors.append(aid)
        return f'<div class="etapa"><a href="#{aid}">{title}</a>{t1_ref(aid)}</div>'

    partes_t1 = [f'<!doctype html><html lang="es"><head><meta charset="utf-8"><title>CLS · Curso de reversing — Tomo I</title><style>{css}\n{css_print}</style></head><body><main>']
    partes_t1.append("""
<section class="print-sec portada-pdf" id="portada">
<p class="kicker">Proyecto CLS · Edición 5 · Revisión 5.4 (Ampliada) · TOMO I DE II</p>
<h1>Curso de reversing<br><span style="font-size: 20pt; font-weight: 600; color: #0b5f6b;">Tomo I · Tronco Principal (Etapas 0 a 5) y Material de Apoyo</span></h1>
<p class="sub">De los fundamentos al análisis guiado en user-mode: arquitectura x86/x64, formato PE y DLLs (ciclo de vida y sideloading), IDA, Ghidra, x64dbg (flujo táctico y extracción masiva de strings), reversing de Go y Rust, evasión en user-mode (API hooking, direct/indirect syscalls y call stack spoofing), inyección de procesos en memoria, criptografía híbrida y APIs nativas (CryptoAPI/CNG), .NET, C++ profundo, WinDbg/TTD, malware y vulnerabilidades.</p>
<p class="sub"><strong>Contenido de este volumen (Tomo I):</strong> Apertura y 3 Rutas de Estudio · Etapas 0, 1, 2 (2A, 2B, 2C y optativas 2.22–2.24), 3, 4 y 5 · Hilo conductor multi-nivel y Kit de 5 plantillas C/C++ · 3 Hojas de referencia rápida (<em>Cheat Sheets</em>) · Glosario · Preguntas y respuestas · Fuentes y límites.</p>
<p class="sub"><strong>En el Tomo II y Separata:</strong> La <strong>Etapa 6 (Kernel y drivers KMDF)</strong> y la <strong>Rama 2D (Windows internals y Hyper-V)</strong> se encuentran encuadernadas en el <strong>Tomo II</strong>. Para consulta rápida junto al teclado, usá la <strong>Separata de Escritorio</strong>.</p>
<div class="aviso"><strong>Material educativo y defensivo.</strong> Las prácticas usan programas propios, software abierto o crackmes diseñados para aprender. No se enseña a eludir licencias, DRM ni controles de acceso.</div>
</section>
""")

    toc_t1 = ['<section class="print-sec" id="toc"><h1>Contenido — Tomo I</h1><div class="toc">']
    toc_t1.append('<div class="etapa">Apertura</div><ol>')
    toc_t1.append(t1_row("portada-texto", "Cómo estudiar y qué se revisó"))
    toc_t1.append(t1_row("mapa-curso", "Mapa del curso y rutas de estudio"))
    toc_t1.append('</ol>')

    orden_t1 = [
        ("Etapa 0", ["guia/00-laboratorio.html"]),
        ("Etapa 1", ["guia/01-numeros.html", "guia/01-memoria.html", "guia/01-procesos.html", "guia/01-pe.html", "guia/01-c-python.html"]),
        ("Etapa 2", ["guia/02-registros.html", "guia/02-instrucciones.html", "guia/02-flotante.html", "guia/02-flujo.html", "guia/02-llamadas.html", "guia/02-debugger.html", "guia/02-ida.html", "guia/02-optimizaciones.html", "guia/02-herramientas.html", "guia/02-ofuscacion.html", "guia/02-tls.html", "guia/02-mfc.html", "guia/02-huella-compilador.html", "guia/02-pe-fino.html", "guia/02-anti-analisis.html", "guia/02-ghidra.html", "guia/02-packers.html", "guia/02-cpp-profundo.html", "guia/02-windbg-heap.html", "guia/02-patch-diffing.html", "guia/02-scripting-debugger.html", "guia/02-opt-malware-dinamico.html", "guia/02-opt-shellcode-c2.html", "guia/02-opt-fuzzing.html"]),
        ("Etapa 3", ["guia/03-dotnet-runtime.html", "guia/03-dotnet-il.html"]),
        ("Etapa 4", ["guia/04-metodo.html", "guia/04-cripto.html", "guia/04-informe.html", "guia/04-dinamico-seguro.html", "guia/04-formatos-protocolos.html"]),
        ("Etapa 5", ["guia/05-malware.html", "guia/05-vulnerabilidades.html", "guia/05-automatizacion.html", "guia/05-fuera-de-alcance.html"]),
    ]
    for etapa, lecs in orden_t1:
        numero = re.search(r"\d+", etapa).group(0)
        toc_t1.append(t1_heading(mapa[f"guia/etapa-{numero}.html"], etapa) + '<ol>')
        for rel in lecs:
            toc_t1.append(t1_row(mapa[rel], nombres[rel]))
        toc_t1.append('</ol>')

    toc_t1.append('<div class="etapa">Material de apoyo (en este Tomo I)</div><ol>')
    toc_t1.append(t1_row("hilo-plantillas", "Hilo conductor y plantillas C/C++"))
    toc_t1.append(t1_row("hojas-referencia", "Hojas de referencia rápida (Cheat Sheets)"))
    toc_t1.append(t1_row("glosario", "Glosario"))
    toc_t1.append(t1_row("preguntas", "Preguntas y respuestas"))
    toc_t1.append(t1_row("fuentes", "Fuentes y límites"))
    toc_t1.append('</ol>')
    toc_t1.append('<div class="etapa" style="margin-top:10pt; color:#555;">En el Tomo II (Ramas Especializadas)</div><ol>')
    toc_t1.append('<li><span>Etapa 6 · Kernel y drivers en Windows (6.1 a 6.6)</span><span class="toc-pag">ver Tomo II</span></li>')
    toc_t1.append('<li><span>Rama 2D · Windows internals y Hyper-V (2D.1 a 2D.13)</span><span class="toc-pag">ver Tomo II</span></li>')
    toc_t1.append('</ol></div></section>')
    partes_t1.append("".join(toc_t1))

    # Mapa de enlaces internos de Tomo I (sin Etapa 6 ni 2D para que no apunten a anclas ausentes)
    anclas_presentes_t1 = set(t1_anchors) | {"portada", "toc"}
    mapa_t1 = {k: v for k, v in mapa.items() if v in anclas_presentes_t1}

    for rel, anchor in [("00_EMPEZAR_AQUI.html", "portada-texto"), ("guia/index.html", "mapa-curso")]:
        h = limpiar_enlaces(contenido(rel), mapa_t1)
        partes_t1.append(f'<section class="print-sec" id="{anchor}">{h}</section>')

    for rel, _ in ETAPAS:
        etapa_num = rel.split("-")[-1].replace(".html", "")
        if etapa_num == "6":
            continue
        h = limpiar_enlaces(contenido(rel), mapa_t1)
        partes_t1.append(f'<section class="print-sec" id="{mapa[rel]}">{h}</section>')
        pref = f"guia/0{etapa_num}-"
        lecs = [x for x in LECCIONES if x[0].startswith(pref)]
        for lrel, _ in lecs:
            if lrel == "guia/02-cpp-profundo.html":
                partes_t1.append("""
<section class="print-sec" id="parte-b-portadilla" style="page-break-before: always; break-before: page;">
<div style="margin-top: 25mm; padding: 18mm 15mm; border: 2px solid #2b5797; background: #fafbfc; border-radius: 4px; text-align: center;">
<p style="font-size: 11pt; text-transform: uppercase; letter-spacing: 2px; color: #555; margin-bottom: 8pt;">Curso de Reversing · Tomo I</p>
<h1 style="font-size: 26pt; color: #1a365d; margin: 0 0 10pt; border: none;">PARTE B</h1>
<h2 style="font-size: 15pt; color: #2b5797; font-weight: 600; margin: 0 0 16pt; border: none;">Reversing Avanzado, Ecosistemas y Material de Apoyo</h2>
<hr style="width: 60px; height: 3px; background: #2b5797; border: none; margin: 0 auto 16pt;">
<p style="font-size: 9.8pt; color: #333; line-height: 1.6; max-width: 480px; margin: 0 auto 12pt; text-align: left;">
Este volumen continúa el <strong>Bloque 2C (Windows Avanzado)</strong> a partir del análisis profundo de C++ y sus estructuras en memoria (RTTI, vtables, STL y excepciones), cubriendo además las <strong>Etapas 3 (.NET), 4 (Método y Criptografía) y 5 (Malware y Automatización)</strong>, culminando con el <strong>Kit de 5 Plantillas C/C++</strong>, las <strong>Hojas de Referencia Rápida</strong>, el <strong>Glosario A–Z unificado</strong> y las <strong>Preguntas de Repaso</strong>.
</p>
<div style="margin-top: 20pt; padding: 10pt 14pt; background: #eef3f8; border-left: 4px solid #2b5797; font-size: 8.8pt; color: #2d3748; text-align: left;">
<strong>Entorno activo de laboratorio para la Parte B:</strong><br>
VM con Windows x64 aislada, Visual Studio Developer Command Prompt (<code>cl.exe</code>), IDA Free o Ghidra 11+, <code>x64dbg</code> y <code>WinDbg Preview</code>.
</div>
</div>
</section>
""")
            lh = limpiar_enlaces(contenido(lrel), mapa_t1)
            partes_t1.append(f'<section class="print-sec" id="{mapa[lrel]}">{lh}</section>')

    for rel, anchor in [
        ("hilo-conductor-y-plantillas.html", "hilo-plantillas"),
        ("hojas-referencia-rapida.html", "hojas-referencia"),
        ("glosario.html", "glosario"),
        ("preguntas_y_respuestas.html", "preguntas"),
    ]:
        h = limpiar_enlaces(contenido(rel), mapa_t1)
        if anchor == "preguntas":
            h = h.replace('<details class="qa">', '<details class="qa" open>')
        partes_t1.append(f'<section class="print-sec" id="{anchor}">{h}</section>')

    with open(os.path.join(DST_GUIA, "FUENTES_Y_LIMITES.md"), encoding="utf-8") as f:
        fuentes_md = f.read()
    fuentes_html_t1 = limpiar_enlaces(build_mod.md(fuentes_md), mapa_t1)
    partes_t1.append(f'<section class="print-sec" id="fuentes"><h1>Fuentes y límites</h1>{fuentes_html_t1}</section>')
    partes_t1.append("</main></body></html>")

    arbol_t1 = [
        ("Portada — Tomo I", "portada-texto", []),
        ("Mapa del curso y rutas de estudio", "mapa-curso", []),
    ]
    for erel, etit in ETAPAS:
        mnum = re.search(r"etapa-(\d)", erel)
        if mnum and mnum.group(1) == "6":
            continue
        hijos = []
        if mnum:
            pref = f"0{mnum.group(1)}-"
            for lrel, ltit in LECCIONES:
                if os.path.basename(lrel).startswith(pref):
                    hijos.append((ltit, ancla(lrel)))
        arbol_t1.append((etit, ancla(erel), hijos))
    arbol_t1.extend([
        ("Hilo conductor y plantillas C/C++", "hilo-plantillas", []),
        ("Hojas de referencia rápida (Cheat Sheets)", "hojas-referencia", []),
        ("Glosario", "glosario", []),
        ("Preguntas y respuestas", "preguntas", []),
        ("Fuentes y límites", "fuentes", []),
    ])

    info_t1 = compilar_volumen_pdf(
        "CLS_Tomo_1_Tronco_y_Apoyo",
        "Tomo I · Tronco Principal y Material de Apoyo",
        "\n".join(partes_t1),
        t1_anchors,
        arbol_t1,
        ctx,
        asegurar_par=True,
    )

    # =========================================================================
    # 2. TOMO II — RAMAS ESPECIALIZADAS: KERNEL (ETAPA 6) Y WINDOWS INTERNALS (2D)
    # =========================================================================
    t2_anchors = []

    def t2_ref(aid):
        return f'<span class="toc-pag" data-anchor="{aid}">calculando</span>'

    def t2_row(aid, title):
        t2_anchors.append(aid)
        return f'<li><a href="#{aid}">{title}</a>{t2_ref(aid)}</li>'

    def t2_heading(aid, title):
        t2_anchors.append(aid)
        return f'<div class="etapa"><a href="#{aid}">{title}</a>{t2_ref(aid)}</div>'

    partes_t2 = [f'<!doctype html><html lang="es"><head><meta charset="utf-8"><title>CLS · Curso de reversing — Tomo II</title><style>{css}\n{css_print}</style></head><body><main>']
    partes_t2.append("""
<section class="print-sec portada-pdf" id="portada">
<p class="kicker">Proyecto CLS · Edición 5 · Revisión 5.4 (Ampliada) · TOMO II DE II</p>
<h1>Curso de reversing<br><span style="font-size: 20pt; font-weight: 600; color: #0b5f6b;">Tomo II · Ramas Especializadas: Kernel, Drivers y Windows Internals</span></h1>
<p class="sub">Profundización avanzada en el sistema operativo Windows: arquitectura del kernel NT, drivers WDM/KMDF, IOCTLs, depuración kernel con WinDbg (KDNET), minifiltros, mitigaciones HVCI/VBS, objetos del ejecutivo, procesos/hilos, Registro, servicios, Task Scheduler, COM/DCOM, RPC, WMI, IPC, SEH/VEH/WER, ETW y Hyper-V.</p>
<p class="sub"><strong>Contenido de este volumen (Tomo II):</strong> <strong>Etapa 6 completa (6.1 a 6.6)</strong> · <strong>Rama 2D completa (2D.1 a 2D.13 + Anexo Hyper-V)</strong>.</p>
<p class="sub"><strong>Requisitos previos y consulta rápida:</strong> Este tomo asume el dominio del tronco principal (Etapas 0 a 4 del <strong>Tomo I</strong>). Durante las prácticas con WinDbg, KMDF y estructuras del sistema, mantené abierta la <strong>Separata de Escritorio</strong> (especialmente la <em>Hoja 2: Offsets PEB/LDR</em> y la <em>Hoja 3: CTL_CODE, IRQL y comandos de WinDbg</em>).</p>
<div class="aviso"><strong>Seguridad de laboratorio obligatoria.</strong> Toda práctica con drivers de kernel (<code>.sys</code>), <code>bcdedit /debug on</code>, Driver Verifier, servicios o mecanismos de persistencia debe realizarse exclusivamente dentro de una <strong>máquina virtual descartable y aislada</strong>, nunca en el equipo anfitrión.</div>
</section>
""")

    toc_t2 = ['<section class="print-sec" id="toc"><h1>Contenido — Tomo II</h1><div class="toc" style="columns: 1; max-width: 165mm;">']
    lecs_e6 = ["guia/6-01-arquitectura-kernel.html", "guia/6-02-kmdf-ioctl.html", "guia/6-03-debug-kernel.html", "guia/6-04-revision-driver.html", "guia/6-05-minifilters.html", "guia/6-06-mitigaciones.html"]
    toc_t2.append(t2_heading(mapa["guia/etapa-6.html"], "Etapa 6 · Kernel y drivers en Windows (rama optativa)") + '<ol>')
    for rel in lecs_e6:
        toc_t2.append(t2_row(mapa[rel], nombres[rel]))
    toc_t2.append('</ol>')

    toc_t2.append(t2_heading(mapa["2d.html"], "Rama 2D · Windows internals (rama optativa de Etapa 2)") + '<ol>')
    for rel, titulo in RAMA_2D:
        if rel == "2d.html":
            continue
        toc_t2.append(t2_row(mapa[rel], titulo))
    toc_t2.append('</ol>')

    toc_t2.append('<div class="etapa" style="margin-top:12pt; color:#555;">Referencias cruzadas en Tomo I y Separata de Escritorio</div><ol>')
    toc_t2.append(f'<li><span>Tronco principal (Etapas 0 a 5)</span><span class="toc-pag">Tomo I · p. 1–{info_t1["paginas"]["hilo-plantillas"] - 1}</span></li>')
    toc_t2.append(f'<li><span>Hilo conductor multi-nivel y Kit de 5 plantillas C/C++</span><span class="toc-pag">Tomo I · {info_t1["etiquetas"]["hilo-plantillas"]}</span></li>')
    toc_t2.append(f'<li><span>Hojas de referencia rápida (Cheat Sheets 1 a 5)</span><span class="toc-pag">Separata y Tomo I · {info_t1["etiquetas"]["hojas-referencia"]}</span></li>')
    toc_t2.append(f'<li><span>Glosario y Preguntas frecuentes</span><span class="toc-pag">Tomo I · p. {info_t1["paginas"]["glosario"]}–{info_t1["paginas"]["fuentes"] - 1}</span></li>')
    toc_t2.append('</ol></div></section>')
    partes_t2.append("".join(toc_t2))

    anclas_presentes_t2 = set(t2_anchors) | {"portada", "toc"}
    mapa_t2 = {k: v for k, v in mapa.items() if v in anclas_presentes_t2}

    # Etapa 6
    h_e6 = limpiar_enlaces(contenido("guia/etapa-6.html"), mapa_t2)
    partes_t2.append(f'<section class="print-sec" id="{mapa["guia/etapa-6.html"]}">{h_e6}</section>')
    for lrel in lecs_e6:
        lh = limpiar_enlaces(contenido(lrel), mapa_t2)
        partes_t2.append(f'<section class="print-sec" id="{mapa[lrel]}">{lh}</section>')

    # Rama 2D
    for rel, _titulo in RAMA_2D:
        h = limpiar_enlaces(contenido(rel), mapa_t2)
        partes_t2.append(f'<section class="print-sec" id="{mapa[rel]}">{h}</section>')

    partes_t2.append("</main></body></html>")

    hijos_e6 = [(nombres[r], ancla(r)) for r in lecs_e6]
    hijos_2d = [(titulo, ancla(rel)) for rel, titulo in RAMA_2D if rel != "2d.html"]
    arbol_t2 = [
        ("Etapa 6 · Kernel y drivers en Windows", ancla("guia/etapa-6.html"), hijos_e6),
        ("2D · Windows internals (optativa)", ancla("2d.html"), hijos_2d),
    ]

    info_t2 = compilar_volumen_pdf(
        "CLS_Tomo_2_Kernel_e_Internals",
        "Tomo II · Kernel, Drivers y Windows Internals",
        "\n".join(partes_t2),
        t2_anchors,
        arbol_t2,
        ctx,
        asegurar_par=True,
    )

    # =========================================================================
    # 3. SEPARATA DE ESCRITORIO — REFERENCIA RÁPIDA JUNTO AL TECLADO
    # =========================================================================
    from contenidos_nuevos import BLOQUE_RUTAS_ESTUDIO, BLOQUE_ARBOL_TRIAGE, PAGINA_CHEAT_SHEETS

    sep_anchors = []

    def sep_ref(aid):
        return f'<span class="toc-pag" data-anchor="{aid}">calculando</span>'

    def sep_row(aid, title):
        sep_anchors.append(aid)
        return f'<li><a href="#{aid}">{title}</a>{sep_ref(aid)}</li>'

    # Extraer las 3 hojas de PAGINA_CHEAT_SHEETS por su salto de página
    partes_cs = PAGINA_CHEAT_SHEETS.split('<div style="break-before: page; page-break-before: always;"></div>')
    hoja1_raw = partes_cs[0]
    hoja2_raw = partes_cs[1] if len(partes_cs) > 1 else ""
    hoja3_raw = partes_cs[2] if len(partes_cs) > 2 else ""

    # Quitar el h1 y callout introductorio de hoja1_raw para que Hoja 1 entre directo al grano en su página
    m_h2_hoja1 = re.search(r'<h2 id="hoja-1-[^"]*">', hoja1_raw)
    if m_h2_hoja1:
        hoja1_limpia = hoja1_raw[m_h2_hoja1.start():]
    else:
        hoja1_limpia = hoja1_raw

    # Helper para formatear rangos entre lecciones en Tomo I / Tomo II / Master
    def rango_en(info_vol, ancla_ini, ancla_fin_excl=None):
        p_ini = info_vol["paginas"][ancla_ini]
        if ancla_fin_excl and ancla_fin_excl in info_vol["paginas"]:
            p_fin = info_vol["paginas"][ancla_fin_excl] - 1
        else:
            p_fin = info_vol.get("total_contenido", info_vol["total"])
        return f"p. {p_ini}–{p_fin}" if p_ini != p_fin else f"p. {p_ini}"

    partes_sep = [f'<!doctype html><html lang="es"><head><meta charset="utf-8"><title>CLS · Separata de Escritorio</title><style>{css}\n{css_print}</style></head><body><main>']

    # Página 1 de la Separata: Portada compacta + Índice de la Separata + Mapa Cruzado de los Tomos
    toc_sep_items = [
        sep_row("rutas-estudio", "1. Tres perfiles o rutas de estudio (Principiante, Intermedio y Avanzado)"),
        sep_row("arbol-triage", "2. Árbol de decisión de triage inicial («¿Por dónde empiezo?») y 10 señales"),
        sep_row("resumen-hilo", "3. Mapa del Hilo Conductor (check_v1 → BlocLab) y comandos del Kit C/C++"),
        sep_row("hoja-1", "4. Hoja de Referencia 1 · Nivel Principiante (Registros, saltos, VA/RVA, ABIs)"),
        sep_row("hoja-2", "5. Hoja de Referencia 2 · Nivel Intermedio (Offsets PEB/LDR, cripto, x64dbg, Frida)"),
        sep_row("hoja-3", "6. Hoja de Referencia 3 · Nivel Avanzado (C++ RTTI/SSO, CTL_CODE, IRQL, WinDbg/TTD)"),
        sep_row("hoja-4", "7. Hoja de Referencia 4 · Evasión User-Mode, Inyección, Go/Rust y x64dbg (Rev. 5.4)"),
        sep_row("hoja-5", "8. Hoja de Referencia 5 · Criptografía Nativa (CryptoAPI/CNG) y Drivers .sys (Rev. 5.4)"),
    ]

    partes_sep.append(f"""
<section class="print-sec" id="portada-separata">
<p style="color: #0b5f6b; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; font-size: 8.5pt; margin: 0;">Proyecto CLS · Edición 5 · Revisión 5.4 · Cuadernillo de Consulta Rápida</p>
<h1 style="font-size: 22pt; margin: 2pt 0 6pt;">Separata de Escritorio y Referencia Rápida</h1>
<p style="margin: 0 0 8pt; font-size: 9.8pt; color: #333;">Cuadernillo diseñado para permanecer abierto junto al teclado (abrochado a caballete o anillado fino) mientras trabajás con IDA, Ghidra, x64dbg, ILSpy o WinDbg y leés el <strong>Tomo I</strong> o el <strong>Tomo II</strong>.</p>

<h2 style="font-size: 11.5pt; margin: 8pt 0 4pt; border-bottom: 1px solid #999;">Contenido de esta Separata de Escritorio</h2>
<div class="toc" style="columns: 1; margin-top: 4pt; font-size: 9.5pt;">
<ol style="padding-left: 14pt;">
{''.join(toc_sep_items)}
</ol>
</div>

<h2 style="font-size: 11.5pt; margin: 12pt 0 4pt; border-bottom: 1px solid #999;">Índice Maestro Cruzado: Localización rápida en Tomo I, Tomo II y Edición Completa</h2>
<div class="tabla"><table>
<thead><tr>
<th>Bloque / Etapa del curso</th>
<th>Nivel principal</th>
<th>Volumen impreso</th>
<th>Páginas en Tomo I / II</th>
<th>Páginas en Ed. Completa</th>
</tr></thead><tbody>
<tr><td><strong>Apertura y Mapa del curso</strong> (<code>00_EMPEZAR_AQUI</code>, <code>index</code>)</td><td>Todos</td><td><strong>Tomo I</strong></td><td>{rango_en(info_t1, "portada-texto", ancla("guia/etapa-0.html"))}</td><td>{rango_en(ctx, "portada-texto", ancla("guia/etapa-0.html"))}</td></tr>
<tr><td><strong>Etapa 0 · Laboratorio seguro</strong> (<code>0.1</code>)</td><td>Principiante</td><td><strong>Tomo I</strong></td><td>{rango_en(info_t1, ancla("guia/etapa-0.html"), ancla("guia/etapa-1.html"))}</td><td>{rango_en(ctx, ancla("guia/etapa-0.html"), ancla("guia/etapa-1.html"))}</td></tr>
<tr><td><strong>Etapa 1 · Fundamentos binarios y PE</strong> (<code>1.1–1.5</code>)</td><td>Principiante</td><td><strong>Tomo I</strong></td><td>{rango_en(info_t1, ancla("guia/etapa-1.html"), ancla("guia/etapa-2.html"))}</td><td>{rango_en(ctx, ancla("guia/etapa-1.html"), ancla("guia/etapa-2.html"))}</td></tr>
<tr><td><strong>Etapa 2A · Núcleo x86/x64, IDA y x64dbg</strong> (<code>2.1–2.9</code>)</td><td>Principiante</td><td><strong>Tomo I</strong></td><td>{rango_en(info_t1, ancla("guia/etapa-2.html"), ancla("guia/02-ofuscacion.html"))}</td><td>{rango_en(ctx, ancla("guia/etapa-2.html"), ancla("guia/02-ofuscacion.html"))}</td></tr>
<tr><td><strong>Etapa 2B · Ofuscación, TLS, MFC, PEB, Anti-debug, Ghidra</strong> (<code>2.10–2.16</code>)</td><td>Intermedio</td><td><strong>Tomo I</strong></td><td>{rango_en(info_t1, ancla("guia/02-ofuscacion.html"), ancla("guia/02-packers.html"))}</td><td>{rango_en(ctx, ancla("guia/02-ofuscacion.html"), ancla("guia/02-packers.html"))}</td></tr>
<tr><td><strong>Etapa 2C · Packers, C++ profundo, WinDbg/TTD, Diffing, Frida</strong> (<code>2.17–2.21</code>)</td><td>Interm. / Avanzado</td><td><strong>Tomo I</strong></td><td>{rango_en(info_t1, ancla("guia/02-packers.html"), ancla("guia/02-opt-malware-dinamico.html"))}</td><td>{rango_en(ctx, ancla("guia/02-packers.html"), ancla("guia/02-opt-malware-dinamico.html"))}</td></tr>
<tr><td><strong>Etapa 2 Optativas · Malware dinámico, Shellcode, Fuzzing</strong> (<code>2.22–2.24</code>)</td><td>Interm. / Avanzado</td><td><strong>Tomo I</strong></td><td>{rango_en(info_t1, ancla("guia/02-opt-malware-dinamico.html"), ancla("guia/etapa-3.html"))}</td><td>{rango_en(ctx, ancla("guia/02-opt-malware-dinamico.html"), ancla("guia/etapa-3.html"))}</td></tr>
<tr><td><strong>Etapa 3 · Reversing en .NET e IL</strong> (<code>3.1–3.2</code>)</td><td>Principiante</td><td><strong>Tomo I</strong></td><td>{rango_en(info_t1, ancla("guia/etapa-3.html"), ancla("guia/etapa-4.html"))}</td><td>{rango_en(ctx, ancla("guia/etapa-3.html"), ancla("guia/etapa-4.html"))}</td></tr>
<tr><td><strong>Etapa 4 · Método de 5 pasos, protocolos, cripto e informe</strong> (<code>4.1–4.5</code>)</td><td>Princ. / Intermedio</td><td><strong>Tomo I</strong></td><td>{rango_en(info_t1, ancla("guia/etapa-4.html"), ancla("guia/etapa-5.html"))}</td><td>{rango_en(ctx, ancla("guia/etapa-4.html"), ancla("guia/etapa-5.html"))}</td></tr>
<tr><td><strong>Etapa 5 · Malware estático, vulnerabilidades, automatización</strong> (<code>5.1–5.4</code>)</td><td>Interm. / Avanzado</td><td><strong>Tomo I</strong></td><td>{rango_en(info_t1, ancla("guia/etapa-5.html"), "hilo-plantillas")}</td><td>{rango_en(ctx, ancla("guia/etapa-5.html"), ancla("guia/etapa-6.html"))}</td></tr>
<tr><td><strong>Etapa 6 · Kernel y drivers KMDF/WDM en Windows</strong> (<code>6.1–6.6</code>)</td><td>Avanzado</td><td><strong>Tomo II</strong></td><td>{rango_en(info_t2, ancla("guia/etapa-6.html"), ancla("2d.html"))}</td><td>{rango_en(ctx, ancla("guia/etapa-6.html"), ancla("2d.html"))}</td></tr>
<tr><td><strong>Rama 2D · Windows internals y Hyper-V</strong> (<code>2D.1–2D.13</code> + Hyper-V)</td><td>Interm. / Avanzado</td><td><strong>Tomo II</strong></td><td>{rango_en(info_t2, ancla("2d.html"), None)}</td><td>{rango_en(ctx, ancla("2d.html"), "hilo-plantillas")}</td></tr>
<tr><td><strong>Hilo conductor multi-nivel y Kit de 5 plantillas C/C++</strong></td><td>Todos</td><td><strong>Tomo I</strong></td><td>{rango_en(info_t1, "hilo-plantillas", "hojas-referencia")}</td><td>{rango_en(ctx, "hilo-plantillas", "hojas-referencia")}</td></tr>
<tr><td><strong>Hojas de referencia rápida (Cheat Sheets 1 a 5)</strong></td><td>Todos</td><td><strong>Separata y Tomo I</strong></td><td>{rango_en(info_t1, "hojas-referencia", "glosario")}</td><td>{rango_en(ctx, "hojas-referencia", "glosario")}</td></tr>
<tr><td><strong>Glosario, Preguntas frecuentes y Fuentes/límites</strong></td><td>Todos</td><td><strong>Tomo I</strong></td><td>{rango_en(info_t1, "glosario", None)}</td><td>{rango_en(ctx, "glosario", None)}</td></tr>
</tbody></table></div>
</section>
""")

    # Sección 1 de Separata: 3 Perfiles o Rutas de Estudio
    rutas_limpio = limpiar_enlaces(BLOQUE_RUTAS_ESTUDIO, {})
    partes_sep.append(f'<section class="print-sec" id="rutas-estudio">{rutas_limpio}</section>')

    # Sección 2 de Separata: Árbol de Decisión de Triage Inicial y 10 Señales
    triage_limpio = limpiar_enlaces(BLOQUE_ARBOL_TRIAGE, {})
    partes_sep.append(f'<section class="print-sec" id="arbol-triage">{triage_limpio}</section>')

    # Sección 3 de Separata: Resumen del Hilo Conductor + Guía rápida de compilación de las 5 plantillas C/C++
    partes_sep.append("""
<section class="print-sec" id="resumen-hilo">
<h2>Mapa del Hilo Conductor Multi-Nivel (<code>check_v1</code> &rarr; <code>check_v2</code> &rarr; <code>BlocLab</code>)</h2>
<p>La misma regla de negocio —aceptar dos enteros <code>a &lt;= 50</code> (<code>0x32</code>), <code>b &gt;= 50</code> (<code>0x32</code>) tales que <code>(a + b) * 4 == 480</code> (<code>0x1E0</code>)— recorre los tres niveles del curso. El código fuente completo está en el <strong>Tomo I</strong> (<em>Hilo conductor y plantillas C/C++</em>) y en la carpeta <code>plantillas_codigo/</code>:</p>
<div class="tabla"><table>
<thead><tr>
<th>Estadio y Nivel</th>
<th>Qué agrega sobre el binario anterior</th>
<th>Qué ves en IDA / Ghidra / x64dbg / WinDbg</th>
<th>Lecciones que conecta</th>
</tr></thead><tbody>
<tr>
<td><strong>Estadio 1 · Principiante</strong><br><code>check_v1_O0.exe</code> vs <code>check_v1_O2.exe</code></td>
<td>Compilación en C puro sin optimizar (<code>/Od</code>) frente a optimizada (<code>/O2</code>).</td>
<td>En <code>/Od</code>: variables en stack y 2 saltos condicionales. En <code>/O2</code>: argumentos directo en <code>ECX</code>/<code>EDX</code>, <code>lea eax, [rcx+rdx]</code>, <code>cmp eax, 78h</code> (<code>480/4 = 120</code>) y selección sin salto (<code>cmove rcx, rdx</code>).</td>
<td>1.5, 2.4, 2.5, 2.7, 2.8, 4.1</td>
</tr>
<tr>
<td><strong>Estadio 2 · Intermedio</strong><br><code>check_v2.exe</code> + <code>parser_clsf.exe</code></td>
<td><strong>TLS Callback</strong> anti-debug antes de <code>main</code>, string cifrada con <code>XOR 0x5A</code>, empaquetado UPX y archivo binario <code>.clsf</code> (12B header + body).</td>
<td>Con debugger sin ocultar, el TLS callback cambia <code>g_objetivo = 999</code> antes de <code>main</code>. La string <code>"Correcto"</code> no aparece en <code>.rdata</code>; se descifra en el stack antes de <code>puts</code>.</td>
<td>2.10, 2.11, 2.14, 2.15, 2.17, 2.21, 4.2, 4.5</td>
</tr>
<tr>
<td><strong>Estadio 3 · Avanzado</strong><br><code>cpp_fh4.exe</code> + <code>heap_bug_v1.exe</code> + <code>pipe_server_min.exe</code></td>
<td>Herencia múltiple C++ (<code>ValidadorBloc</code>), <code>std::string</code> SSO, excepciones x64, bug de heap (20B en bloque de 16B), Named Pipe y despacho IOCTL en KMDF.</td>
<td>Ajuste de <code>this</code> (<code>add rcx, 10h</code>), umbral SSO (<code>cmp [rcx+18h], 10h</code>), <code>!heap -p -a</code> con Page Heap / <code>g-</code> en TTD, protocolo <code>\\\\.\\pipe\\BlocLabPipe</code> y tabla <code>CTL_CODE</code>.</td>
<td>2.18, 2.19, 2.20, 5.2, 2D.6–2D.10, 6.2, 6.4</td>
</tr>
</tbody></table></div>

<h2>Referencia rápida de compilación y prueba del Kit de 5 Plantillas C/C++</h2>
<div class="tabla"><table>
<thead><tr>
<th>Archivo en <code>plantillas_codigo/</code></th>
<th>Comando de compilación (MSVC / MinGW-w64)</th>
<th>Objetivo de práctica y comando de verificación</th>
</tr></thead><tbody>
<tr>
<td><strong>1. <code>check_evolucion.c</code></strong><br><em>(Principiante e Intermedio)</em></td>
<td><code>cl /Zi /Od check_evolucion.c /Fe:check_v1_O0.exe</code><br><code>cl /Zi /O2 check_evolucion.c /Fe:check_v1_O2.exe</code><br><code>cl /Zi /O1 /DMODO_INTERMEDIO check_evolucion.c /Fe:check_v2.exe</code></td>
<td>Comparar grafo con/sin <code>CMOVcc</code> en IDA (2.8/4.1); inspeccionar directorio TLS en PE-bear y frenar en <code>tls_antidebug</code> antes de <code>main</code> (2.11/2.15). Par válido: <code>40 80</code>.</td>
</tr>
<tr>
<td><strong>2. <code>cpp_rtti_sso.cpp</code></strong><br><em>(Avanzado · C++ x64)</em></td>
<td><code>cl /EHsc /GR /Zi /O1 cpp_rtti_sso.cpp /Fe:cpp_fh4.exe</code><br><code>cl /EHsc /GR /Zi /O1 /d2FH4- cpp_rtti_sso.cpp /Fe:cpp_fh3.exe</code></td>
<td>Localizar las 2 vtables de <code>ValidadorBloc</code>, leer <code>vtable[-1]</code> (RTTI), distinguir string SSO (<code>&lt; 16B</code>) de heap (<code>&gt;= 16B</code>) y comparar <code>__CxxFrameHandler4</code> vs <code>FH3</code> en <code>.pdata/.xdata</code> (2.18).</td>
</tr>
<tr>
<td><strong>3. <code>heap_bug.c</code></strong><br><em>(Avanzado · WinDbg y Diffing)</em></td>
<td><code>cl /Zi /O1 heap_bug.c /Fe:heap_bug_v1.exe</code><br><code>cl /Zi /O1 /DPARCHE_SEGURO heap_bug.c /Fe:heap_bug_v2.exe</code></td>
<td>Activar Page Heap: <code>gflags /p /enable heap_bug_v1.exe /full</code>, correr con 20 <code>A</code>s en WinDbg y ejecutar <code>!heap -p -a @rcx</code> (2.19). Comparar <code>v1</code> vs <code>v2</code> en Diaphora/BinDiff (2.20).</td>
</tr>
<tr>
<td><strong>4. <code>parser_clsf.c</code></strong><br><em>(Intermedio · Formatos y Fuzzing)</em></td>
<td><code>cl /Zi /O1 parser_clsf.c /Fe:parser_clsf.exe</code><br>Generar muestra: <code>parser_clsf.exe --gen muestra_A.clsf</code></td>
<td>Reconstruir la cabecera de 12 bytes (<code>magic "CLSF"</code>, <code>version</code>, <code>flags</code>, <code>hdr_len=12</code>, <code>body_len</code>, <code>seq_id</code>) viendo cómo acota cada campo en el desensamblado (4.5 y 2.24).</td>
</tr>
<tr>
<td><strong>5. <code>pipe_server_min.c</code></strong><br><em>(Intermedio/Avanzado · IPC)</em></td>
<td><code>cl /Zi /O1 pipe_server_min.c /Fe:pipe_server_min.exe</code></td>
<td>Inspeccionar flags de <code>CreateNamedPipeW</code> (<code>PIPE_REJECT_REMOTE_CLIENTS</code>) y la máquina de estados en <code>\\\\.\\pipe\\BlocLabPipe</code> (4.5 y 2D.10).</td>
</tr>
</tbody></table></div>
</section>
""")

    # Secciones 4, 5 y 6 de Separata: Hojas 1, 2 y 3 de Cheat Sheets
    partes_sep.append(f'<section class="print-sec" id="hoja-1">{limpiar_enlaces(hoja1_limpia, {})}</section>')
    partes_sep.append(f'<section class="print-sec" id="hoja-2">{limpiar_enlaces(hoja2_raw, {})}</section>')
    partes_sep.append(f'<section class="print-sec" id="hoja-3">{limpiar_enlaces(hoja3_raw, {})}</section>')
    partes_sep.append(f'<section class="print-sec hoja-compacta" id="hoja-4">{limpiar_enlaces(at2.HOJA4_HTML, {})}</section>')
    partes_sep.append(f'<section class="print-sec hoja-compacta" id="hoja-5">{limpiar_enlaces(at2.HOJA5_HTML, {})}</section>')
    partes_sep.append("</main></body></html>")

    arbol_sep = [
        ("1. Tres perfiles o rutas de estudio", "rutas-estudio", []),
        ("2. Árbol de decisión de triage inicial y 10 señales", "arbol-triage", []),
        ("3. Mapa del Hilo Conductor y Kit de 5 plantillas C/C++", "resumen-hilo", []),
        ("4. Hoja 1 · Nivel Principiante (Registros, saltos, VA/RVA, ABIs)", "hoja-1", []),
        ("5. Hoja 2 · Nivel Intermedio (PEB/LDR, cripto, x64dbg, Frida)", "hoja-2", []),
        ("6. Hoja 3 · Nivel Avanzado (C++ RTTI/SSO, CTL_CODE, IRQL, WinDbg)", "hoja-3", []),
        ("7. Hoja 4 · Evasión User-Mode, Inyección, Go/Rust y x64dbg (Rev. 5.4)", "hoja-4", []),
        ("8. Hoja 5 · Criptografía Nativa (CryptoAPI/CNG) y Drivers .sys (Rev. 5.4)", "hoja-5", []),
    ]

    info_sep = compilar_volumen_pdf(
        "CLS_Separata_Escritorio",
        "Separata de Escritorio · Referencia Rápida",
        "\n".join(partes_sep),
        sep_anchors,
        arbol_sep,
        ctx,
        asegurar_par=True,
    )

    return info_t1, info_t2, info_sep


def particionar_tomo1_automatico(base_dir):
    """Divide el Tomo 1 en Parte A y Parte B con paridad estricta para imprenta/anillado."""
    import pypdf
    src_pdf = os.path.join(base_dir, "CLS_Tomo_1_Tronco_y_Apoyo.pdf")
    if not os.path.exists(src_pdf):
        print(f"[Aviso] No se encontró {src_pdf} para particionar.")
        return
    reader = pypdf.PdfReader(src_pdf)
    total_pages = len(reader.pages)
    print(f"\n--- Particionando Tomo 1 ({total_pages} páginas) en Parte A y Parte B ---")

    # Parte A: Páginas 1 a 172 (índices 0 a 171) -> 172 páginas (86 hojas a doble faz)
    writer_a = pypdf.PdfWriter()
    for i in range(0, 172):
        writer_a.add_page(reader.pages[i])

    # Parte B: Páginas 173 a fin (índices 172 a total_pages-1) -> 158 páginas (79 hojas)
    writer_b = pypdf.PdfWriter()
    for i in range(172, total_pages):
        writer_b.add_page(reader.pages[i])

    nom_a = "CLS_Tomo_1_Parte_A_pags_1-172.pdf"
    nom_b = f"CLS_Tomo_1_Parte_B_pags_173-{total_pages}.pdf"

    path_a = os.path.join(base_dir, nom_a)
    path_b = os.path.join(base_dir, nom_b)
    with open(path_a, "wb") as f:
        writer_a.write(f)
    with open(path_b, "wb") as f:
        writer_b.write(f)
    print(f"  Generado {nom_a}: {len(writer_a.pages)} págs ({os.path.getsize(path_a):,} bytes)")
    print(f"  Generado {nom_b}: {len(writer_b.pages)} págs ({os.path.getsize(path_b):,} bytes)")

    # Nombres de compatibilidad
    for compat in ["CLS_Tomo_1_Parte_A_pags_1-171.pdf", "CLS_Tomo_1_Parte_A_pags_1-170.pdf"]:
        shutil.copy2(path_a, os.path.join(base_dir, compat))
    for compat in ["CLS_Tomo_1_Parte_B_pags_172-328.pdf", "CLS_Tomo_1_Parte_B_pags_171-328.pdf", "CLS_Tomo_1_Parte_B_pags_171-330.pdf"]:
        shutil.copy2(path_b, os.path.join(base_dir, compat))

    # Replicar en ARTIFACT_DIR si existe
    if ARTIFACT_DIR and os.path.exists(ARTIFACT_DIR):
        for name in [nom_a, nom_b, "CLS_Tomo_1_Parte_A_pags_1-171.pdf", "CLS_Tomo_1_Parte_B_pags_172-328.pdf"]:
            shutil.copy2(os.path.join(base_dir, name), os.path.join(ARTIFACT_DIR, name))

def imprimir_resumen_suite(base_dir):
    import pypdf
    archivos = [
        ("CLS_Curso_Reversing.pdf", "Edición Unificada Completa (Rev. 5.4)"),
        ("CLS_Tomo_1_Tronco_y_Apoyo.pdf", "Tomo I: Tronco y Apoyo"),
        ("CLS_Tomo_1_Parte_A_pags_1-172.pdf", "Tomo I · Parte A (Fundamentos a Packers)"),
        ("CLS_Tomo_1_Parte_B_pags_173-330.pdf", "Tomo I · Parte B (Windows Avanzado a Apoyo)"),
        ("CLS_Tomo_2_Kernel_e_Internals.pdf", "Tomo II: Kernel, Drivers e Internals"),
        ("CLS_Separata_Escritorio.pdf", "Separata de Escritorio (Cheat Sheets y Rutas)"),
    ]
    print("\n" + "=" * 80)
    print(f"{'Archivo PDF':<38} | {'Págs':<6} | {'Hojas':<6} | {'Tamaño':<11} | {'Paridad'}")
    print("-" * 80)
    for fname, desc in archivos:
        p = os.path.join(base_dir, fname)
        if os.path.exists(p):
            r = pypdf.PdfReader(p)
            c = len(r.pages)
            h = (c + 1) // 2
            sz = f"{os.path.getsize(p):,} B"
            par = "PAR (OK)" if c % 2 == 0 else "IMPAR"
            print(f"{fname:<38} | {c:<6} | {h:<6} | {sz:<11} | {par}")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    copiar_estructura_base()
    aplicar_6_mejoras_html()
    ctx_master = generar_pdf_completo()
    generar_tomos_y_separata(ctx_master)
    particionar_tomo1_automatico(DST_GUIA)
    imprimir_resumen_suite(DST_GUIA)