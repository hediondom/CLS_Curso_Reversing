# -*- coding: utf-8 -*-
"""Contenidos nuevos para las 6 mejoras de alto impacto (Edición 5 · Revisión 5.2)."""

BLOQUE_RUTAS_ESTUDIO = """
<h2 id="tres-perfiles-o-rutas-de-estudio-principiante-intermedio-y-avanzado">Tres perfiles o rutas de estudio (Principiante, Intermedio y Avanzado)</h2>
<p>Aunque el curso completo supera las 400 páginas al sumar el tronco obligatorio (Etapas 0–4), los bloques intermedio y avanzado de la Etapa 2 (2B y 2C), la rama de Windows internals (2D) y la de Kernel y drivers (Etapa 6), <strong>no hace falta leerlo de corrido de principio a fin en una sola sentada</strong>. Podés recorrerlo en tres hitos progresivos claramente delimitados según tu nivel actual y tu objetivo:</p>
<div class="tabla"><table>
<thead><tr>
<th>Perfil y nivel</th>
<th>Carga estimada</th>
<th>Secuencia exacta de etapas y lecciones</th>
<th>Herramientas centrales</th>
<th>Hito práctico al cerrar el nivel</th>
</tr></thead><tbody>
<tr>
<td><strong>Ruta 1 · Fundamentos Firmes</strong><br><em>(Nivel Principiante)</em></td>
<td>~65 a 75 h</td>
<td><a href="etapa-0.html">Etapa 0</a> (0.1) &rarr; <a href="etapa-1.html">Etapa 1</a> (1.1–1.5) &rarr; <a href="etapa-2.html">Etapa 2A</a> (2.1–2.9) &rarr; <a href="etapa-3.html">Etapa 3</a> (3.1–3.2) &rarr; <a href="etapa-4.html">Etapa 4 base</a> (4.1, 4.2, 4.3 y 4.4)</td>
<td>Visor PE (PE-bear / DIE), editor hex, IDA Free, x64dbg, ILSpy / dnSpyEx, compilador C y Python</td>
<td>Analizar un binario propio en C y uno en .NET de punta a punta sin ver el fuente, confirmar hipótesis con breakpoints y redactar un informe reproducible.</td>
</tr>
<tr>
<td><strong>Ruta 2 · Analista de Binarios y Malware Defensivo</strong><br><em>(Nivel Intermedio)</em></td>
<td>+45 a 55 h<br><em>(acumulado ~115–130 h)</em></td>
<td>Bloque <strong>2B</strong> (<a href="02-ofuscacion.html">2.10</a>–<a href="02-ghidra.html">2.16</a>) &rarr; <a href="02-packers.html">2.17</a> (Packers) &rarr; <a href="02-scripting-debugger.html">2.21</a> (Scripting y Frida) &rarr; <a href="04-formatos-protocolos.html">4.5</a> (Formatos y protocolos) &rarr; <a href="05-malware.html">5.1</a> (Malware estático) y <a href="05-automatizacion.html">5.3</a> (Automatización) &rarr; Optativas <a href="02-opt-malware-dinamico.html">2.22</a>, <a href="02-opt-shellcode-c2.html">2.23</a> y <a href="2d-01-objetos.html">2D.1</a>–<a href="2d-05-task-scheduler.html">2D.5</a></td>
<td>Ghidra, Scylla, trazas condicionales de x64dbg, Frida, IDAPython (<code>ida_typeinf</code>), <code>pefile</code>, <code>capstone</code>, YARA y Sysinternals / WinDbg básico</td>
<td>Desempaquetar un binario UPX propio (x86/x64) hasta el OEP, recuperar strings ocultas y APIs por PEB/hash, reconstruir un formato binario propio (<code>CLSF</code>) y escribir reglas YARA e informes de persistencia.</td>
</tr>
<tr>
<td><strong>Ruta 3 · Investigador de Vulnerabilidades, Internals y Kernel</strong><br><em>(Nivel Avanzado)</em></td>
<td>+80 a 110 h<br><em>(curso completo)</em></td>
<td>Núcleo duro de <strong>2C</strong> (<a href="02-cpp-profundo.html">2.18</a> C++ profundo, <a href="02-windbg-heap.html">2.19</a> WinDbg/TTD/Heap, <a href="02-patch-diffing.html">2.20</a> Patch diffing) &rarr; <a href="05-vulnerabilidades.html">5.2</a> (Vulnerabilidades) &rarr; <a href="02-opt-fuzzing.html">2.24</a> (Fuzzing y simbólico) &rarr; <a href="2d-06-com-interfaces.html">2D.6</a>–<a href="2d-13-integrador.html">2D.13</a> (COM/RPC/WMI/IPC/Excepciones/ETW) &rarr; <a href="etapa-6.html">Etapa 6</a> (6.1–6.6, Kernel y drivers)</td>
<td>WinDbg Preview + Time-Travel Debugging (TTD), GFlags / Page Heap, BinDiff / Diaphora / Version Tracking, OleViewDotNet, WDK / KMDF y Driver Verifier en VM descartable</td>
<td>Reconstruir clases C++ (vtable, RTTI, SSO, excepciones x64), diagnosticar corrupciones de heap con Page Heap/TTD, aislar un parche de seguridad con diffing, auditar canales IPC/COM y revisar un driver <code>.sys</code> estática y dinámicamente.</td>
</tr>
</tbody></table></div>

<aside class="callout nota"><p class="callout-titulo">Consejo para elegir tu punto de entrada</p><p>Si empezás desde cero, completá primero la <strong>Ruta 1</strong> sin desviarte a 2B ni a 2C cuando llegues al final de 2.9: saltar de 2.9 directo a la Etapa 3 (.NET) y a la Etapa 4 base te da una victoria real y consolida el método en la mitad de tiempo. Una vez aprobada la puerta de salida de la Etapa 4, volvé para cursar la <strong>Ruta 2</strong> y luego la <strong>Ruta 3</strong>. En cualquier nivel, acompañate con el <a href="../hilo-conductor-y-plantillas.html">Hilo conductor multi-nivel y kit de plantillas C/C++</a> y las <a href="../hojas-referencia-rapida.html">Hojas de referencia rápida (Cheat Sheets)</a>.</p></aside>
"""


BLOQUE_ARBOL_TRIAGE = """
<h2 id="árbol-de-decisión-de-triage-inicial-por-dónde-empiezo">Árbol de decisión de triage inicial («¿Por dónde empiezo?»)</h2>
<p>Cuando te enfrentás a un binario desconocido (un crackme, un programa propio compilado meses atrás o un componente de laboratorio), los primeros diez minutos del <strong>Paso 2 (Inventario)</strong> definen qué herramientas abrir y a qué lección del curso acudir. Usar IDA sobre un ensamblado .NET puro o buscar strings en un binario empaquetado con UPX hace perder horas. Este árbol de decisión conecta los tres niveles del curso (Principiante, Intermedio y Avanzado) en un flujo único (y se complementa con el <a href="../hilo-conductor-y-plantillas.html">Hilo conductor multi-nivel y kit de plantillas C/C++</a>):</p>

<pre class="arbol-triage"><code class="lenguaje-text">┌────────────────────────────────────────────────────────────────────────────┐
│ FASE 1 · CONTENEDOR, ARQUITECTURA Y RUNTIME (PE-bear / DIE · 2 minutos)    │
└─────────────────────────────────────┬──────────────────────────────────────┘
                                      │
  ├─► ¿NO empieza con "MZ" / "PE\\0\\0"?
  │     ├─► ¿Es archivo de datos / captura de mensajes? ──► Lección 4.5 (Formatos y protocolos)
  │     └─► ¿Es código máquina sin cabecera (posición independiente)? ──► Lección 2.23 (Shellcode)
  │
  ├─► ¿Es PE32 (0x10B, 32 bits) o PE32+ (0x20B, 64 bits)? (Lecciones 1.4 y 2.5)
  │     ├─► 32 bits (x86): argumentos en stack (cdecl/stdcall) o ECX/EDX (fastcall/thiscall);
  │     │                  en Windows x64 corre bajo WOW64 (ver Lección 2D.2).
  │     └─► 64 bits (x64): argumentos en RCX, RDX, R8, R9 + shadow space de 32 bytes.
  │
  └─► ¿Tiene cabecera CLR (.NET) o marcador ".net bundle" (hostfxr)? (Lección 3.1)
        ├─► SÍ (IL puro, ReadyToRun "RTR\\0" o Single-File Bundle):
        │     └──► Abrirlo en ILSpy / dnSpyEx (Etapa 3: Lecciones 3.1 y 3.2).
        └─► NO (Nativo puro o .NET Native AOT):
              └──► Avanzar a la FASE 2.

┌────────────────────────────────────────────────────────────────────────────┐
│ FASE 2 · ENTROPÍA, SECCIONES, IMPORTS Y HUELLA DE COMPILADOR (3 minutos)   │
└─────────────────────────────────────┬──────────────────────────────────────┘
                                      │
  ├─► ¿Entropía alta (> 6,8), secciones renombradas (UPX0/UPX1), permisos W+X
  │   o primera sección con RawSize = 0 e IAT mínima (LoadLibraryA + GetProcAddress)?
  │     ├─► SÍ: Posible PACKER (Lección 2.17).
  │     │     ├──► En UPX x86: "ESP trick" (F8 sobre pushad + HW breakpoint en [ESP]).
  │     │     ├──► En UPX x64: breakpoint de memoria en ejecución sobre la sección vacía.
  │     │     └──► En el OEP: dumpear y reconstruir IAT con Scylla (si es VM o protector comercial: ver 2.26 / 2.27 / 5.4).
  │     └─► IAT casi vacía pero entropía normal:
  │           └──► Resolución dinámica por PEB / API Hashing (Lección 2.14):
  │                buscar lecturas de fs:[30h] / gs:[60h], recorrido de InMemoryOrderModuleList
  │                ([rsi+20h] = DllBase en x64) y constantes de hash de 32 bits.
  │
  └─► ¿Qué compilador o runtime delata la huella? (Lección 2.13)
        ├─► MSVC C/C++ (Rich header + vcruntime140.dll / ucrtbase.dll + __security_cookie):
        │     └──► ¿Hay vtables con RTTI en vtable[-1] o __CxxFrameHandler3/4 en .pdata/.xdata?
        │          ──► Lección 2.18 (C++ profundo: RTTI, std::string SSO, STL y excepciones).
        ├─► MFC (mfc140u.dll o estático con CWnd/CDialog):
        │     └──► Lección 2.12: localizar GetMessageMap() ──► AFX_MSGMAP y AFX_MSGMAP_ENTRY.
        ├─► MinGW / GCC (msvcrt.dll + __mingw_* + sección .eh_frame, sin Rich header):
        │     └──► Lección 2.13: ubicar main pasado a __getmainargs.
        ├─► Delphi (recursos RCDATA con firma "TPF0", TForm/TObject):
        │     └──► Lección 2.13: ABI register en x86 (EAX=Self, EDX, ECX) y longitud en [ptr-4].
        ├─► Go (binario grande estático, "Go build ID", tabla pclntab):
        │     └──► Lecciones 2.13 y 2.32: ir a main.main o recuperar nombres/tipos con GoReSym; string = {ptr, len}.
        └─► Rust (rutas "src/main.rs", mensajes de pánico Option::unwrap, símbolos _ZN / _R):
              └──► Lecciones 2.13 y 2.32: separar ramas de pánico; demangle de símbolos _ZN/_R; string = {ptr, len}.

┌────────────────────────────────────────────────────────────────────────────┐
│ FASE 3 · PRE-MAIN, OFUSCACIÓN Y ROL DEL COMPONENTE (5 minutos)             │
└─────────────────────────────────────┬──────────────────────────────────────┘
                                      │
  ├─► ¿El directorio TLS (AddressOfCallBacks) tiene punteros?
  │     └──► SÍ: Inspeccionar TLS Callbacks antes de main (Lección 2.11); suelen ejecutar
  │          chequeos anti-debug (IsDebuggerPresent, PEB.NtGlobalFlag, NtQueryInformationProcess, 2.15).
  │
  ├─► ¿La ventana de Strings (Shift+F12) no muestra los mensajes esperados?
  │     └──► Buscar cadenas UTF-16 (funciones W, Lección 2.7), cadenas armadas en el stack (mov byte)
  │          o bucles de descifrado XOR / RC4 / ChaCha20 / AES previos al uso (Lecciones 2.10 y 4.2).
  │
  ├─► ¿El grafo de la función en IDA/Ghidra es un único bucle gigante con switch?
  │     └──► Distinguir Aplanamiento de Flujo (CFF: bloques con lógica real y variable de estado)
  │          frente a Máquina Virtual (VM: handlers genéricos leídos por VIP) (Lección 2.10).
  │
  └─► ¿Cuál es el rol del binario y tu objetivo de análisis?
        ├─► Programa de consola/GUI estándar ──► Ciclo de 5 pasos de esta lección (4.1) + 2.6 / 2.7 / 2.16.
        ├─► Servicio de Windows (StartServiceCtrlDispatcher) ──► Lección 2D.4 (Servicios).
        ├─► Persistencia en Registro / Tareas / WMI ──► Lecciones 2D.3, 2D.5 y 2D.9.
        ├─► Servidor o cliente COM / DCOM / RPC / Named Pipe ──► Lecciones 2D.6 a 2D.10 y 4.5.
        ├─► Diagnóstico de crash, corrupción de heap o comparación con parche ──► Lecciones 2.19, 2.20, 2D.11 y 5.2.
        └─► Driver de kernel (.sys, importa ntoskrnl.exe / WdfVersionBind) ──► Etapa 6 (6.1 a 6.6).</code></pre>

<div class="tabla"><table>
<thead><tr>
<th>Nivel</th>
<th>Señal observada en los primeros 5 minutos</th>
<th>Qué significa (hipótesis inicial)</th>
<th>Acción inmediata y lección de referencia</th>
</tr></thead><tbody>
<tr><td><strong>Principiante</strong></td><td>Imports claros (<code>scanf</code>, <code>printf</code>, <code>MessageBoxW</code>) y strings visibles en <code>.rdata</code></td><td>Binario C/C++ sin empaquetar ni ofuscar</td><td>Buscar la string clave con <code>Shift+F12</code>, saltar por xref (<code>X</code>) y aplicar el ciclo de 5 pasos (<a href="02-ida.html">2.7</a>, <a href="04-metodo.html">4.1</a>).</td></tr>
<tr><td><strong>Principiante</strong></td><td>Las strings de éxito y error están en el <strong>mismo bloque básico</strong> sin salto condicional entre ellas</td><td>Selección sin salto (<em>branchless</em>) producida por el compilador (<code>-O2</code>)</td><td>Buscar una instrucción <code>CMOVcc</code> (<code>cmovne</code>/<code>cmove</code>) que elige qué puntero de cadena pasar a <code>puts</code>/<code>printf</code> (<a href="02-flujo.html">2.4</a>, <a href="02-optimizaciones.html">2.8</a>, <a href="04-metodo.html">4.1</a>).</td></tr>
<tr><td><strong>Principiante</strong></td><td>Importa <code>mscoree.dll</code> (<code>_CorExeMain</code>) o contiene metadatos <code>.NET</code> / marcador <code>.net bundle</code></td><td>Aplicación administrada .NET (IL, ReadyToRun o Single-File)</td><td>Abrir en <strong>ILSpy</strong> o <strong>dnSpyEx</strong> para leer C# e IL antes de tocar un desensamblador nativo (<a href="03-dotnet-runtime.html">3.1</a>, <a href="03-dotnet-il.html">3.2</a>).</td></tr>
<tr><td><strong>Intermedio</strong></td><td>Secciones <code>UPX0</code> (<code>RawSize = 0</code>) y <code>UPX1</code> (entropía &gt; 7,5, permisos <code>W+X</code>), pocos imports</td><td>Ejecutable empaquetado con UPX</td><td>Llegar al OEP (<em>ESP trick</em> en x86 o breakpoint de memoria en ejecución sobre <code>UPX0</code> en x64), dumpear y reconstruir IAT con Scylla (<a href="02-packers.html">2.17</a>).</td></tr>
<tr><td><strong>Intermedio</strong></td><td>Mi breakpoint en <code>main</code> nunca se alcanza, o una variable global ya llega alterada al entrar a <code>main</code></td><td>Código ejecutado antes del entry point principal</td><td>Revisar el directorio <strong>TLS (<code>AddressOfCallBacks</code>)</strong> en PE-bear/IDA y poner breakpoint en cada callback (<a href="02-tls.html">2.11</a>, <a href="02-anti-analisis.html">2.15</a>).</td></tr>
<tr><td><strong>Intermedio</strong></td><td>Casi sin imports ni strings, pero lee <code>gs:[60h]</code> &rarr; <code>[rax+18h]</code> &rarr; <code>[rax+20h]</code> y rota enteros (<code>ror edx, 0Dh</code>)</td><td>Resolución dinámica de APIs por recorrido del PEB y <em>API hashing</em></td><td>Poner breakpoint en el <code>call reg</code> del resolvedor o cruzar constantes con listas de hashes de exportaciones (<a href="02-pe-fino.html">2.14</a>).</td></tr>
<tr><td><strong>Intermedio</strong></td><td>Constantes <code>0x637c777b</code> (AES), <code>"expand 32-byte k"</code> (ChaCha20) o <code>0x9E3779B9</code> (TEA) en <code>.rdata</code>/código</td><td>Transformación criptográfica estándar o cifrado de configuración/mensajes</td><td>Etiquetar la función criptográfica por su constante mágica e interceptar su entrada/salida en vez de analizar las rondas internas (<a href="04-cripto.html">4.2</a>, <a href="02-scripting-debugger.html">2.21</a>).</td></tr>
<tr><td><strong>Avanzado</strong></td><td>Llamadas indirectas <code>call qword ptr [rax+18h]</code> donde <code>rax</code> proviene de <code>[rcx]</code></td><td>Despacho virtual C++ (<code>vtable</code>) o interfaz COM (<code>IUnknown</code>)</td><td>Ubicar la <code>vtable</code> en <code>.rdata</code>, leer <code>vtable[-1]</code> (<code>Complete Object Locator</code>, RVAs en x64) para recuperar el nombre de la clase (<a href="02-cpp-profundo.html">2.18</a>, <a href="2d-06-com-interfaces.html">2D.6</a>).</td></tr>
<tr><td><strong>Avanzado</strong></td><td>El proceso muere dentro de <code>ntdll!RtlFreeHeap</code> lejos de donde ocurrió el error real</td><td>Corrupción de heap previa (desborde, <em>use-after-free</em> o <em>double free</em>)</td><td>Activar <strong>Full Page Heap</strong> (<code>gflags /p /enable app.exe /full</code>) o grabar traza <strong>TTD</strong> en WinDbg y retroceder con <code>ba w4</code> + <code>g-</code> (<a href="02-windbg-heap.html">2.19</a>).</td></tr>
<tr><td><strong>Avanzado</strong></td><td>Archivo <code>.sys</code> que importa <code>WdfVersionBind</code> y registra <code>EvtIoDeviceControl</code></td><td>Driver de modo kernel basado en KMDF</td><td>Desglosar cada constante <code>CTL_CODE</code> del <code>switch</code> (DeviceType, Access, Function, Method), revisar <code>SDDL</code> y auditar tamaños mínimos y usos de <code>METHOD_NEITHER</code> (<a href="6-02-kmdf-ioctl.html">6.2</a>, <a href="6-04-revision-driver.html">6.4</a>).</td></tr>
</tbody></table></div>
"""


PAGINA_HILO_Y_PLANTILLAS = """<h1 id="hilo-conductor-multi-nivel-y-kit-de-plantillas-c-c">Hilo conductor multi-nivel y kit de plantillas C/C++</h1>
<aside class="callout nota"><p class="callout-titulo">Propósito de esta sección transversal</p><p>Conectar de forma práctica los tres niveles del curso (Principiante, Intermedio y Avanzado). En la <strong>Parte I</strong> vemos cómo un único programa de validación (desde el <code>check.c</code> básico de la Etapa 1 hasta el componente <code>BlocLab</code> de las Etapas 2C, 2D y 6) cambia en el desensamblador y en el debugger a medida que evoluciona. En la <strong>Parte II</strong> tenés <strong>7 plantillas mínimas en C y C++</strong> listas para copiar y compilar en tu VM para practicar todas las lecciones intermedias y avanzadas sin depender de muestras externas.</p></aside>

<h2 id="parte-i-el-hilo-conductor-un-mismo-binario-a-través-de-los-tres-niveles">Parte I · El hilo conductor: un mismo binario a través de los tres niveles</h2>
<p>Una de las dificultades más comunes al estudiar reversing es sentir que cada tema nuevo (optimizaciones, TLS callbacks, packers, C++ con vtables, named pipes o drivers KMDF) pertenece a un mundo desconectado del anterior. Para unirlos, sigamos <strong>la misma regla de negocio</strong> en sus tres estadios de evolución:</p>
<blockquote><p><strong>Regla de negocio constante:</strong> aceptar dos enteros <code>a</code> y <code>b</code> tales que <code>a &lt;= 50</code> (<code>0x32</code>), <code>b &gt;= 50</code> (<code>0x32</code>) y <code>(a + b) * 4 == 480</code> (<code>0x1E0</code>).</p></blockquote>

<h3 id="estadio-1-nivel-principiante-check-v1-c-con-o0-frente-a-o2">Estadio 1 · Nivel Principiante: <code>check_v1.c</code> con <code>-O0</code> frente a <code>-O2</code> (Etapas 1, 2A y 4.1)</h3>
<p>En el nivel Principiante escribimos la función en C puro y comparamos qué genera el compilador en x64 sin optimizaciones (<code>-O0</code> / <code>/Od</code>) frente a compilación optimizada (<code>-O2</code>):</p>
<pre><code class="lenguaje-c">// Regla base en C (Lecciones 1.5, 2.4, 2.8 y 4.1)
int validar_pares(int a, int b) {
    if (a &gt; 50 || b &lt; 50) return 0;
    return ((a + b) * 4) == 480;
}</code></pre>
<pre><code class="lenguaje-text">Compilación sin optimizar (-O0, x64)          Compilación optimizada (-O2, x64)
──────────────────────────────────────────    ──────────────────────────────────────────
validar_pares:                                validar_pares:
  mov   dword ptr [rsp+8], ecx   ; guarda a     xor   eax, eax          ; resultado = 0 por defecto
  mov   dword ptr [rsp+10h], edx ; guarda b     cmp   ecx, 32h          ; ¿a &gt; 50? (ECX = a)
  cmp   dword ptr [rsp+8], 32h   ; ¿a &gt; 50?     jg    short salir       ; si a &gt; 50, retorna 0
  jg    short fallo                             cmp   edx, 32h          ; ¿b &lt; 50? (EDX = b)
  cmp   dword ptr [rsp+10h], 32h ; ¿b &lt; 50?     jl    short salir       ; si b &lt; 50, retorna 0
  jl    short fallo                             lea    ecx, [rcx+rdx]    ; ecx = a + b (con LEA, 2.2)
  mov   eax, dword ptr [rsp+8]                  cmp   ecx, 78h          ; ¡480 / 4 = 120 (0x78)!
  add   eax, dword ptr [rsp+10h] ; eax = a+b    sete  al                ; AL = 1 si (a+b)==120 (2.4)
  shl   eax, 2                   ; eax *= 4   salir:
  cmp   eax, 1E0h                ; ¿== 480?     ret
  jne   short fallo
  mov   eax, 1
  ret
fallo:
  xor   eax, eax
  ret</code></pre>
<p><strong>Qué aprende el alumno al comparar ambos listados:</strong></p>
<ul>
<li>Con <code>-O0</code> (izquierda) cada variable baja al <em>shadow space</em> (<code>[rsp+8]</code>, <code>[rsp+10h]</code>, <a href="guia/01-memoria.html">1.2</a> y <a href="guia/02-llamadas.html">2.5</a>) y la multiplicación por 4 se ve como <code>shl eax, 2</code> seguida de <code>cmp eax, 1E0h</code>.</li>
<li>Con <code>-O2</code> (derecha) el compilador aplica reducción algebraica (<a href="guia/02-optimizaciones.html">2.8</a>): en lugar de multiplicar <code>(a + b) * 4</code> y comparar contra <code>480</code>, suma con <code>lea ecx, [rcx+rdx]</code> y compara directamente contra <code>120</code> (<code>0x78 = 480 / 4</code>), usando <code>sete al</code> en vez de un salto condicional. Si en <code>main</code> se elige entre <code>"Correcto"</code> e <code>"Incorrecto"</code>, <code>-O2</code> carga ambas direcciones con <code>lea</code> y selecciona una con <code>cmovne</code> (<a href="guia/04-metodo.html">4.1</a>).</li>
</ul>

<h3 id="estadio-2-nivel-intermedio-check-v2-c-con-tls-callback-xor-y-upx">Estadio 2 · Nivel Intermedio: <code>check_v2.c</code> con TLS Callback, XOR y UPX (Etapas 2B, 2.17, 2.21 y 4.2)</h3>
<p>En el nivel Intermedio, el mismo programa incorpora tres capas que frustran el camino directo de Principiante:</p>
<ol>
<li><strong>Un TLS Callback previo a <code>main</code> (<a href="guia/02-tls.html">2.11</a> y <a href="guia/02-anti-analisis.html">2.15</a>):</strong> una función registrada en <code>.CRT$XLB</code> se ejecuta antes del entry point y consulta <code>IsDebuggerPresent()</code> (o lee <code>gs:[60h] &rarr; [peb+2]</code>). En lugar de mostrar un cartel evidente, si detecta un depurador cambia una variable global <code>g_objetivo</code> de <code>480</code> (<code>0x1E0</code>) a <code>999</code> (<code>0x3E7</code>). Quien pone el breakpoint directamente en <code>main</code> ve que <code>40</code> y <code>80</code> fallan sin entender quién alteró <code>g_objetivo</code>.</li>
<li><strong>Cadenas ocultas con XOR (<a href="guia/02-ofuscacion.html">2.10</a> y <a href="guia/04-cripto.html">4.2</a>):</strong> la cadena <code>"Correcto"</code> ya no está en texto claro en <code>.rdata</code>; se almacena como <code>{0x19, 0x35, 0x28, 0x28, 0x3F, 0x39, 0x2E, 0x35, 0x00}</code> y un bucle corto aplica <code>xor byte ptr [rcx+rax], 5Ah</code> justo antes de imprimir.</li>
<li><strong>Empaquetado didáctico con UPX (<a href="guia/02-packers.html">2.17</a>):</strong> al pasar el ejecutable por <code>upx -9 check_v2.exe</code>, las secciones originales se comprimen dentro de <code>UPX1</code> y la IAT queda reducida a <code>LoadLibraryA</code> y <code>GetProcAddress</code>.</li>
</ol>
<pre><code class="lenguaje-text"> Secuencia de resolución en el Nivel Intermedio:
 1. Triage PE-bear (1.4 / 2.17) ──► Secciones UPX0 (RawSize=0) y UPX1 (entropía 7,8)
 2. Desempaquetado en x64dbg (2.17) ──► Breakpoint de ejecución en memoria sobre UPX0
                                    ──► F9 hasta caer en el OEP ──► Dump + Scylla IAT Fix
 3. Inspección del Dump en IDA/Ghidra (2.11 / 2.16) ──► Directorio TLS apunta a tls_callback_0
                                                    ──► Se observa escritura a g_objetivo si BeingDebugged != 0
 4. Recuperación de cadena XOR (2.10 / 2.21) ──► Bucle xor [reg], 0x5A antes de puts
                                             ──► Breakpoint de log en x64dbg: "msg={s:rcx}"</code></pre>

<h3 id="estadio-3-nivel-avanzado-bloclab-en-c-ipc-y-kernel">Estadio 3 · Nivel Avanzado: <code>BlocLab</code> en C++, IPC y Kernel (Etapas 2C, 2D, 4.5, 5.2 y 6)</h3>
<p>En el nivel Avanzado, la misma verificación vive dentro de una arquitectura realista de Windows:</p>
<ul>
<li><strong>Polimorfismo C++, RTTI, SSO y Excepciones (<a href="guia/02-cpp-profundo.html">2.18</a> y <a href="guia/2d-11-excepciones.html">2D.11</a>):</strong> un objeto derivado <code>ValidadorBloc</code> implementa el método virtual <code>verificar(const std::string&amp; etiqueta, const MensajeCLSF* m)</code>. En el listado vemos <code>mov rax, [rcx] ; call qword ptr [rax+8]</code>. Inspeccionando <code>vtable[-1]</code> en <code>.rdata</code> encontramos el <code>_RTTICompleteObjectLocator</code> (con RVAs en x64) que lleva al nombre <code>.?AVValidadorBloc@@</code>. Si los parámetros violan el rango, lanza una excepción C++ despachada por <code>__CxxFrameHandler4</code> a través de <code>.pdata</code> y <code>.xdata</code>.</li>
<li><strong>Protocolo binario <code>CLSF</code> sobre Named Pipe (<a href="guia/04-formatos-protocolos.html">4.5</a> y <a href="guia/2d-10-ipc.html">2D.10</a>):</strong> en lugar de pedir números por consola con <code>scanf</code>, un proceso servidor crea <code>\\.\pipe\BlocLabPipe</code> (con <code>FILE_FLAG_FIRST_PIPE_INSTANCE</code> y <code>PIPE_REJECT_REMOTE_CLIENTS</code>) y recibe una trama <code>CLSF</code> cuyos campos en offset <code>0x08</code> y <code>0x0A</code> transportan <code>a</code> y <code>b</code> en little-endian.</li>
<li><strong>Auditoría de memoria y Kernel (<a href="guia/02-windbg-heap.html">2.19</a>, <a href="guia/02-patch-diffing.html">2.20</a> y <a href="guia/6-02-kmdf-ioctl.html">6.2</a>):</strong> si el parser copia el cuerpo del mensaje sin validar <code>body_len</code> contra el tamaño del buffer reservado en el heap, diagnosticamos el desborde con <strong>Full Page Heap</strong> y <strong>WinDbg TTD</strong> (<code>!heap -p -a</code> y <code>g-</code>), comparamos el binario vulnerable (<code>v1</code>) contra el corregido (<code>v2</code>) con <strong>BinDiff / Version Tracking</strong>, y verificamos cómo el servidor consulta la versión del subsistema mediante <code>DeviceIoControl(IOCTL_BLOCLAB_QUERY_VERSION = 0x80006000)</code> hacia el driver KMDF de laboratorio.</li>
</ul>

<div class="tabla"><table>
<thead><tr>
<th>Aspecto observable</th>
<th>Estadio 1 · Principiante (<code>check_v1</code>)</th>
<th>Estadio 2 · Intermedio (<code>check_v2</code>)</th>
<th>Estadio 3 · Avanzado (<code>BlocLab</code>)</th>
</tr></thead><tbody>
<tr><td><strong>Punto de entrada a la lógica</strong></td><td><code>main</code> &rarr; <code>validar_pares</code> hallado por xref desde la string <code>"Correcto"</code></td><td>OEP tras desempaquetar UPX + <code>tls_callback</code> en directorio <code>.tls</code></td><td>Slot de <code>vtable</code> de <code>ValidadorBloc</code> invocado tras <code>ReadFile</code> del Named Pipe</td></tr>
<tr><td><strong>Cómo llega la entrada</strong></td><td><code>scanf("%d", ...)</code> en variables locales del stack</td><td>Argumentos de consola + variable global condicionada por el TLS callback</td><td>Estructura binaria <code>CLSF</code> en el heap o buffer de <code>IRP</code> (<code>SystemBuffer</code> en KMDF)</td></tr>
<tr><td><strong>Cómo se ven los textos</strong></td><td>ASCII plano terminado en <code>0</code> en <code>.rdata</code></td><td>Arreglo de bytes cifrado con <code>XOR 0x5A</code> descifrado en un bucle local</td><td><code>std::string</code> con <em>Small String Optimization</em> (SSO, 16B unión + 8B size + 8B cap)</td></tr>
<tr><td><strong>Herramienta que destraba el caso</strong></td><td>IDA Free / Ghidra + breakpoint simple en x64dbg</td><td>PE-bear + x64dbg (breakpoint de memoria / Scylla) + traza condicional</td><td>RTTI en IDA/Ghidra + Frida + WinDbg (Page Heap / TTD) + revisión de <code>CTL_CODE</code></td></tr>
</tbody></table></div>

<hr>

<h2 id="parte-ii-kit-de-5-plantillas-de-código-mínimo-boilerplates-listos-para-compilar">Parte II · Kit de 7 plantillas de código mínimo (Boilerplates listos para compilar)</h2>
<p>Todas las prácticas del curso están pensadas para ejecutarse sobre <strong>programas propios en tu VM aislada</strong> (Etapa 0). Para que no tengas que escribir desde cero cada escenario técnico, acá tenés siete esqueletos autocontenidos de ~35 líneas en C y C++ estándar (también guardados como archivos sueltos en la carpeta <code>plantillas_codigo/</code> del paquete HTML). Compilalos en la VM con <strong>Visual Studio Developer Command Prompt (<code>cl.exe</code>)</strong> o con <strong>MinGW-w64 (<code>gcc</code> / <code>g++</code>)</strong>.</p>

<h3 id="plantilla-1-check-evolucion-c-práctica-para-1-5-2-4-2-8-2-10-2-11-2-15-2-17-y-4-1">Plantilla 1 · <code>check_evolucion.c</code> (Práctica para 1.5, 2.4, 2.8, 2.10, 2.11, 2.15, 2.17 y 4.1)</h3>
<p>Un único archivo en C que podés compilar en modo Principiante (por defecto) o en modo Intermedio (pasando <code>/DMODO_INTERMEDIO</code> o <code>-DMODO_INTERMEDIO</code>), lo que activa un <strong>TLS Callback</strong> que comprueba <code>IsDebuggerPresent()</code> y una rutina de descifrado <strong>XOR</strong> sobre el mensaje de éxito:</p>
<pre><code class="lenguaje-c">// Archivo: plantillas_codigo/check_evolucion.c
// Compilar Principiante (MSVC): cl /Zi /Od check_evolucion.c /Fe:check_v1_O0.exe
// Compilar Optimizado   (MSVC): cl /Zi /O2 check_evolucion.c /Fe:check_v1_O2.exe
// Compilar Intermedio   (MSVC): cl /Zi /O1 /DMODO_INTERMEDIO check_evolucion.c /Fe:check_v2.exe
// Compilar en MinGW-w64 (GCC) : gcc -O0 -g check_evolucion.c -o check_v1_O0.exe
#include &lt;windows.h&gt;
#include &lt;stdio.h&gt;
#include &lt;stdlib.h&gt;

static int g_objetivo = 480; // 0x1E0 en condiciones normales

#ifdef MODO_INTERMEDIO
static void NTAPI tls_antidebug(PVOID h, DWORD reason, PVOID res) {
    (void)h; (void)res;
    if (reason == DLL_PROCESS_ATTACH &amp;&amp; IsDebuggerPresent()) {
        g_objetivo = 999; // Desvía la constante antes de entrar a main (Lecciones 2.11 y 2.15)
    }
}
#ifdef _MSC_VER
#pragma comment(linker, "/INCLUDE:_tls_used")
#pragma section(".CRT$XLB", long, read)
__declspec(allocate(".CRT$XLB")) PIMAGE_TLS_CALLBACK p_tls = tls_antidebug;
#else
PIMAGE_TLS_CALLBACK p_tls __attribute__((used, section(".CRT$XLB"))) = tls_antidebug;
#endif
#endif

int validar_pares(int a, int b) {
    if (a &gt; 50 || b &lt; 50) return 0;
    return ((a + b) * 4) == g_objetivo;
}

int main(int argc, char** argv) {
    int a = (argc &gt; 2) ? atoi(argv[1]) : 0;
    int b = (argc &gt; 2) ? atoi(argv[2]) : 0;
    if (argc &lt;= 2) {
        printf("Primer valor: ");  if (scanf("%d", &amp;a) != 1) return 1;
        printf("Segundo valor: "); if (scanf("%d", &amp;b) != 1) return 1;
    }
    if (validar_pares(a, b)) {
#ifdef MODO_INTERMEDIO
        // "Correcto" cifrado con XOR 0x5A (Lecciones 2.10 y 4.2)
        unsigned char enc[] = {0x19, 0x35, 0x28, 0x28, 0x3F, 0x39, 0x2E, 0x35, 0x00};
        for (int i = 0; enc[i] != 0; ++i) enc[i] ^= 0x5A;
        puts((const char*)enc);
#else
        puts("Correcto");
#endif
        return 0;
    }
    puts("Incorrecto");
    return 1;
}</code></pre>

<h3 id="plantilla-2-cpp-rtti-sso-cpp-práctica-para-2-18-y-2d-11">Plantilla 2 · <code>cpp_rtti_sso.cpp</code> (Práctica para 2.18 y 2D.11)</h3>
<p>Genera en un solo binario: una jerarquía con herencia múltiple (para observar la <code>vtable</code>, el <code>_RTTICompleteObjectLocator</code> en <code>vtable[-1]</code> y un <em>adjustor thunk</em> <code>sub rcx, 8</code>), dos objetos <code>std::string</code> (uno corto en el buffer SSO de 16 bytes y otro largo en el heap), un <code>std::vector&lt;int&gt;</code> y un bloque <code>try/catch</code> con tablas en <code>.pdata</code>/<code>.xdata</code>:</p>
<pre><code class="lenguaje-cpp">// Archivo: plantillas_codigo/cpp_rtti_sso.cpp
// Compilar (MSVC FH4 actual): cl /EHsc /GR /Zi /O1 cpp_rtti_sso.cpp /Fe:cpp_fh4.exe
// Compilar (MSVC FH3 clásico): cl /EHsc /GR /Zi /O1 /d2FH4- cpp_rtti_sso.cpp /Fe:cpp_fh3.exe
// Compilar (MinGW ABI Itanium): g++ -O1 -g cpp_rtti_sso.cpp -o cpp_itanium.exe
#include &lt;iostream&gt;
#include &lt;string&gt;
#include &lt;vector&gt;
#include &lt;stdexcept&gt;
#include &lt;typeinfo&gt;

struct Componente {
    int id = 0x10;
    virtual ~Componente() = default;
    virtual int evaluar(int a, int b) const = 0;
};
struct Auditable {
    int nivel_log = 2;
    virtual void registrar(const char* evento) const { std::cout &lt;&lt; "[LOG] " &lt;&lt; evento &lt;&lt; "\\n"; }
};
class ValidadorBloc : public Componente, public Auditable {
    std::string etiqueta_corta = "BLOC_SSO";                        // &lt; 16B: queda inline (SSO)
    std::string etiqueta_larga = "BLOC_CADENA_LARGA_EN_EL_HEAP_2026"; // &gt;= 16B: reserva en heap
    std::vector&lt;int&gt; historial = {40, 80, 120};
public:
    int evaluar(int a, int b) const override {
        if (a &lt; 0 || b &lt; 0) throw std::runtime_error("Valores negativos no permitidos");
        return (a &lt;= 50 &amp;&amp; b &gt;= 50 &amp;&amp; (a + b) * 4 == (int)historial[2] * 4) ? 1 : 0;
    }
    void registrar(const char* ev) const override {
        std::cout &lt;&lt; "[" &lt;&lt; etiqueta_corta &lt;&lt; "|" &lt;&lt; etiqueta_larga.size() &lt;&lt; "] " &lt;&lt; ev &lt;&lt; "\\n";
    }
};

int main(int argc, char** argv) {
    Componente* obj = new ValidadorBloc();
    std::cout &lt;&lt; "RTTI: " &lt;&lt; typeid(*obj).name() &lt;&lt; "\\n";
    try {
        int res = obj-&gt;evaluar(argc &gt; 1 ? std::stoi(argv[1]) : 40, 80);
        dynamic_cast&lt;Auditable*&gt;(obj)-&gt;registrar(res ? "OK" : "FALLO");
    } catch (const std::exception&amp; ex) {
        std::cerr &lt;&lt; "Excepcion capturada: " &lt;&lt; ex.what() &lt;&lt; "\\n";
    }
    delete obj;
    return 0;
}</code></pre>

<h3 id="plantilla-3-heap-bug-c-práctica-para-2-19-2-20-y-5-2">Plantilla 3 · <code>heap_bug.c</code> (Práctica para 2.19, 2.20 y 5.2)</h3>
<p>Diseñada con un doble propósito: (1) activar <strong>Full Page Heap</strong> (<code>gflags /p /enable heap_bug_v1.exe /full</code>) y ver en <strong>WinDbg</strong> cómo el proceso se detiene exactamente en la instrucción que escribe más allá de los 16 bytes reservados (en vez de fallar más tarde en <code>free</code>), y (2) compilar una versión vulnerable (<code>heap_bug_v1.exe</code>) y una corregida con <code>/DPARCHE_SEGURO</code> (<code>heap_bug_v2.exe</code>) para comparar ambas en <strong>BinDiff / Ghidra Version Tracking</strong> (<a href="guia/02-patch-diffing.html">2.20</a>):</p>
<pre><code class="lenguaje-c">// Archivo: plantillas_codigo/heap_bug.c
// Compilar v1 (vulnerable): cl /Zi /O1 heap_bug.c /Fe:heap_bug_v1.exe
// Compilar v2 (parcheada) : cl /Zi /O1 /DPARCHE_SEGURO heap_bug.c /Fe:heap_bug_v2.exe
// En la VM con Page Heap  : gflags /p /enable heap_bug_v1.exe /full
// Ejecutar en WinDbg      : heap_bug_v1.exe AAAAAAAAAAAAAAAAAAAA  --&gt; !heap -p -a @rcx
#include &lt;stdio.h&gt;
#include &lt;stdlib.h&gt;
#include &lt;string.h&gt;

typedef struct {
    char etiqueta[12];
    unsigned int estado;
} RegistroBloc; // sizeof(RegistroBloc) == 16 bytes exactos

int procesar_entrada(const char* entrada) {
    size_t len = strlen(entrada);
    RegistroBloc* reg = (RegistroBloc*)malloc(sizeof(RegistroBloc));
    if (!reg) return -1;
    reg-&gt;estado = 0xCAFE0001u;

#ifdef PARCHE_SEGURO
    // Versión v2 corregida: valida el límite antes de copiar (Lecciones 2.20 y 5.2)
    if (len &gt;= sizeof(reg-&gt;etiqueta)) {
        puts("Error: entrada excede el buffer de 12 bytes");
        free(reg);
        return 1;
    }
    memcpy(reg-&gt;etiqueta, entrada, len + 1);
#else
    // Versión v1 con defecto didáctico: copia hasta 20 bytes en un bloque de 16 bytes (Lección 2.19)
    if (len &gt; 20) len = 20;
    memcpy(reg-&gt;etiqueta, entrada, len);
    reg-&gt;etiqueta[11] = '\\0';
#endif
    printf("Registro: %s | Estado: 0x%08X\\n", reg-&gt;etiqueta, reg-&gt;estado);
    free(reg);
    return 0;
}

int main(int argc, char** argv) {
    const char* dato = (argc &gt; 1) ? argv[1] : "BLOC_NORMAL";
    return procesar_entrada(dato);
}</code></pre>

<h3 id="plantilla-4-parser-clsf-c-práctica-para-4-1-4-5-y-2-24">Plantilla 4 · <code>parser_clsf.c</code> (Práctica para 4.1, 4.5 y 2.24)</h3>
<p>Implementa el escritor y el lector del formato binario sintético <strong><code>CLSF</code></strong> de la lección <a href="guia/04-formatos-protocolos.html">4.5</a> (12 bytes de cabecera + cuerpo variable). Si lo ejecutás con <code>--gen muestra.clsf</code>, genera la muestra exacta de 17 bytes vista en la teoría; si le pasás un archivo, valida cada campo y devuelve un código de estado distinto por cada fallo (ideal para confirmación diferencial en <a href="guia/04-metodo.html">4.1</a>/<a href="guia/04-formatos-protocolos.html">4.5</a> y como <em>harness</em> en <a href="guia/02-opt-fuzzing.html">2.24</a>):</p>
<pre><code class="lenguaje-c">// Archivo: plantillas_codigo/parser_clsf.c
// Compilar (MSVC) : cl /Zi /O1 parser_clsf.c /Fe:parser_clsf.exe
// Compilar (MinGW): gcc -O1 -g parser_clsf.c -o parser_clsf.exe
// Generar muestra : parser_clsf.exe --gen muestra_A.clsf
// Analizar muestra: parser_clsf.exe muestra_A.clsf
#include &lt;stdio.h&gt;
#include &lt;stdint.h&gt;
#include &lt;string.h&gt;

#pragma pack(push, 1)
typedef struct {
    uint8_t  magic[4];   // +0x00: "CLSF" (43 4C 53 46)
    uint8_t  version;    // +0x04: 1
    uint8_t  flags;      // +0x05: 0
    uint16_t hdr_len;    // +0x06: 12 (0x000C LE)
    uint16_t body_len;   // +0x08: longitud del cuerpo (LE)
    uint16_t seq_id;     // +0x0A: campo variable / secuencia (0x002A = 42 LE)
} CabeceraCLSF;          // Total cabecera: 12 bytes
#pragma pack(pop)

int main(int argc, char** argv) {
    if (argc == 3 &amp;&amp; strcmp(argv[1], "--gen") == 0) {
        CabeceraCLSF h = {{'C','L','S','F'}, 1, 0, 12, 5, 42};
        FILE* f = fopen(argv[2], "wb");
        if (!f) return 1;
        fwrite(&amp;h, sizeof(h), 1, f);
        fwrite("HELLO", 1, 5, f);
        fclose(f);
        puts("Muestra CLSF de 17 bytes generada.");
        return 0;
    }
    if (argc &lt; 2) { puts("Uso: parser_clsf [--gen salida.clsf | entrada.clsf]"); return 1; }
    FILE* f = fopen(argv[1], "rb");
    if (!f) return 2;
    uint8_t buf[256] = {0};
    size_t n = fread(buf, 1, sizeof(buf), f);
    fclose(f);
    if (n &lt; sizeof(CabeceraCLSF)) { puts("Error: archivo truncado"); return 3; }
    const CabeceraCLSF* h = (const CabeceraCLSF*)buf;
    if (memcmp(h-&gt;magic, "CLSF", 4) != 0) { puts("Error: magic invalido"); return 4; }
    if (h-&gt;version != 1)                  { puts("Error: version no soportada"); return 5; }
    if (h-&gt;hdr_len != 12)                 { puts("Error: hdr_len != 12"); return 6; }
    if ((size_t)h-&gt;hdr_len + h-&gt;body_len &gt; n) { puts("Error: body_len excede archivo"); return 7; }
    printf("CLSF OK | ver=%u flags=0x%02X seq=%u body(%u)=\\"%.*s\\"\\n",
           h-&gt;version, h-&gt;flags, h-&gt;seq_id, h-&gt;body_len, h-&gt;body_len, (const char*)(buf + h-&gt;hdr_len));
    return 0;
}</code></pre>

<h3 id="plantilla-5-pipe-server-min-c-práctica-para-2d-1-2d-10-4-5-y-2-21">Plantilla 5 · <code>pipe_server_min.c</code> (Práctica para 2D.1, 2D.10, 4.5 y 2.21)</h3>
<p>Servidor local de <strong>Named Pipe</strong> en modo mensaje que aplica las banderas defensivas estudiadas en <a href="guia/2d-10-ipc.html">2D.10</a> (<code>FILE_FLAG_FIRST_PIPE_INSTANCE</code> y <code>PIPE_REJECT_REMOTE_CLIENTS</code>) e implementa la máquina de estados de <a href="guia/04-formatos-protocolos.html">4.5</a> (<code>ESPERA_SALUDO &rarr; LISTO</code>). Podés conectarte desde un script de Python en la misma VM e inspeccionar las llamadas con Process Explorer, WinDbg o Frida:</p>
<pre><code class="lenguaje-c">// Archivo: plantillas_codigo/pipe_server_min.c
// Compilar (MSVC) : cl /Zi /O1 pipe_server_min.c /Fe:pipe_server_min.exe
// Compilar (MinGW): gcc -O1 -g pipe_server_min.c -o pipe_server_min.exe
// Probar en Python: open(r'\\\\.\\pipe\\BlocLabPipe', 'r+b', buffering=0)
#include &lt;windows.h&gt;
#include &lt;stdio.h&gt;
#include &lt;string.h&gt;

int main(void) {
    const wchar_t* nombre = L"\\\\\\\\.\\\\pipe\\\\BlocLabPipe";
    HANDLE hPipe = CreateNamedPipeW(
        nombre,
        PIPE_ACCESS_DUPLEX | FILE_FLAG_FIRST_PIPE_INSTANCE,
        PIPE_TYPE_MESSAGE | PIPE_READMODE_MESSAGE | PIPE_WAIT | PIPE_REJECT_REMOTE_CLIENTS,
        1, 256, 256, 0, NULL);
    if (hPipe == INVALID_HANDLE_VALUE) {
        printf("CreateNamedPipeW fallo (GLE=%lu)\\n", GetLastError());
        return 1;
    }
    puts("[ESPERA_SALUDO] Escuchando en \\\\\\\\.\\\\pipe\\\\BlocLabPipe ...");
    if (ConnectNamedPipe(hPipe, NULL) || GetLastError() == ERROR_PIPE_CONNECTED) {
        char buf[128] = {0};
        DWORD leidos = 0, escritos = 0;
        if (ReadFile(hPipe, buf, sizeof(buf) - 1, &amp;leidos, NULL) &amp;&amp; leidos &gt;= 4 &amp;&amp; memcmp(buf, "CLSF", 4) == 0) {
            puts("[LISTO] Saludo CLSF valido recibido; enviando respuesta fija.");
            const char resp[] = "CLSF_ACK_V1_READY";
            WriteFile(hPipe, resp, (DWORD)strlen(resp), &amp;escritos, NULL);
        } else {
            const char err[] = "CLSF_ERR_BAD_HELLO";
            WriteFile(hPipe, err, (DWORD)strlen(err), &amp;escritos, NULL);
        }
        FlushFileBuffers(hPipe);
        DisconnectNamedPipe(hPipe);
    }
    CloseHandle(hPipe);
    return 0;
}</code></pre>
<h3 id="plantilla-6-bloclab-kmdf-min-c-práctica-para-6-1-a-6-5">Plantilla 6 · <code>bloclab_kmdf_min.c</code> (Práctica para 6.1 a 6.5)</h3>
<p>Esqueleto mínimo de driver KMDF para Windows x64. Implementa el registro de <code>EvtDriverDeviceAdd</code>, creación de dispositivo con SDDL restrictivo (solo SYSTEM y Administradores), y despacho de IOCTLs con validación estricta de buffer de salida (<code>WdfRequestRetrieveOutputBuffer</code>) para auditoría en IDA/Ghidra y prueba dinámica en VM descartable:</p>
<pre><code class="lenguaje-c">// Archivo: plantillas_codigo/bloclab_kmdf_min.c
// Plantilla 6 (Tomo II, Lección 6.2): bloclab_kmdf_min.c
// Esqueleto mínimo KMDF para análisis estático en IDA/Ghidra y prueba en VM descartable.
// El SDDL restringe la apertura únicamente a SYSTEM y Administradores.
#include &lt;ntddk.h&gt;
#include &lt;wdf.h&gt;
#include &lt;wdmsec.h&gt;

#define IOCTL_BLOCLAB_QUERY_VERSION \
    CTL_CODE(0x8000, 0x800, METHOD_BUFFERED, FILE_READ_DATA) // 0x80006000

typedef struct _BLOCLAB_INFO {
    ULONG Size;
    ULONG Version;
    ULONG State;
} BLOCLAB_INFO, *PBLOCLAB_INFO;

EVT_WDF_DRIVER_DEVICE_ADD BlocLabEvtDeviceAdd;
EVT_WDF_IO_QUEUE_IO_DEVICE_CONTROL BlocLabEvtIoDeviceControl;

NTSTATUS DriverEntry(PDRIVER_OBJECT DriverObject, PUNICODE_STRING RegistryPath) {
    WDF_DRIVER_CONFIG config;
    WDF_DRIVER_CONFIG_INIT(&amp;config, BlocLabEvtDeviceAdd); // +0x08 en x64 = EvtDriverDeviceAdd
    return WdfDriverCreate(DriverObject, RegistryPath, WDF_NO_OBJECT_ATTRIBUTES, &amp;config, WDF_NO_HANDLE);
}

NTSTATUS BlocLabEvtDeviceAdd(WDFDRIVER Driver, PWDFDEVICE_INIT DeviceInit) {
    UNREFERENCED_PARAMETER(Driver);
    DECLARE_CONST_UNICODE_STRING(ntDeviceName, L"\\Device\\BlocLab");
    DECLARE_CONST_UNICODE_STRING(symbolicLink, L"\\DosDevices\\BlocLab");

    NTSTATUS status = WdfDeviceInitAssignName(DeviceInit, &amp;ntDeviceName);
    if (!NT_SUCCESS(status)) return status;

    // Restringe apertura únicamente a SYSTEM y Administradores:
    status = WdfDeviceInitAssignSDDLString(DeviceInit, &amp;SDDL_DEVOBJ_SYS_ALL_ADM_ALL);
    if (!NT_SUCCESS(status)) return status;

    WDFDEVICE device;
    status = WdfDeviceCreate(&amp;DeviceInit, WDF_NO_OBJECT_ATTRIBUTES, &amp;device);
    if (!NT_SUCCESS(status)) return status;

    status = WdfDeviceCreateSymbolicLink(device, &amp;symbolicLink);
    if (!NT_SUCCESS(status)) return status;

    WDF_IO_QUEUE_CONFIG queueConfig;
    WDF_IO_QUEUE_CONFIG_INIT_DEFAULT_QUEUE(&amp;queueConfig, WdfIoQueueDispatchSequential);
    queueConfig.EvtIoDeviceControl = BlocLabEvtIoDeviceControl; // +0x28 en x64

    return WdfIoQueueCreate(device, &amp;queueConfig, WDF_NO_OBJECT_ATTRIBUTES, WDF_NO_HANDLE);
}

VOID BlocLabEvtIoDeviceControl(WDFQUEUE Queue, WDFREQUEST Request,
                               size_t OutputBufferLength, size_t InputBufferLength,
                               ULONG IoControlCode) {
    UNREFERENCED_PARAMETER(Queue);
    UNREFERENCED_PARAMETER(OutputBufferLength);

    if (IoControlCode != IOCTL_BLOCLAB_QUERY_VERSION) {
        WdfRequestComplete(Request, STATUS_INVALID_DEVICE_REQUEST);
        return;
    }
    if (InputBufferLength != 0) {
        WdfRequestComplete(Request, STATUS_INVALID_PARAMETER);
        return;
    }

    PBLOCLAB_INFO outBuf = NULL;
    NTSTATUS status = WdfRequestRetrieveOutputBuffer(Request, sizeof(BLOCLAB_INFO), (PVOID*)&amp;outBuf, NULL);
    if (!NT_SUCCESS(status)) {
        WdfRequestComplete(Request, status);
        return;
    }

    RtlZeroMemory(outBuf, sizeof(BLOCLAB_INFO));
    outBuf-&gt;Size    = sizeof(BLOCLAB_INFO);
    outBuf-&gt;Version = 1;
    outBuf-&gt;State   = 1; // READY
    WdfRequestCompleteWithInformation(Request, STATUS_SUCCESS, sizeof(BLOCLAB_INFO));
}
</code></pre>

<h3 id="plantilla-7-svclab-min-c-práctica-para-2d-4-2d-1-y-2-21">Plantilla 7 · <code>svclab_min.c</code> (Práctica para 2D.4, 2D.1 y 2.21)</h3>
<p>Servicio Win32 nativo completo que implementa el contrato SCM (<code>StartServiceCtrlDispatcherW</code>, <code>ServiceMain</code>, <code>RegisterServiceCtrlHandlerExW</code>) y soporta modo consola con <code>--console</code>. Ideal para practicar depuración de servicios, transiciones de estado y elevación de privilegios:</p>
<pre><code class="lenguaje-c">// Archivo: plantillas_codigo/svclab_min.c
// Práctica para Lección 2D.4 (Servicios: SCM, ciclo de vida, cuentas y auditoría)
// Compilar (MSVC) : cl /Zi /O1 /DUNICODE /D_UNICODE svclab_min.c advapi32.lib /Fe:SvcLab.exe
// Compilar (MinGW): gcc -O1 -g -municode svclab_min.c -ladvapi32 -o SvcLab.exe
// Probar en consola antes de registrar: SvcLab.exe --console
// Registrar en VM (cmd elevado):
//   sc.exe create CLSLabSvc binPath= "C:\CLS-Lab\SvcLab.exe" start= demand obj= "NT AUTHORITY\LocalService"
//   sc.exe start CLSLabSvc
//   sc.exe query CLSLabSvc
//   sc.exe stop CLSLabSvc
//   sc.exe delete CLSLabSvc

#include &lt;windows.h&gt;
#include &lt;stdio.h&gt;

#ifdef _MSC_VER
#pragma comment(lib, "advapi32.lib")
#endif

#define SVC_NAME L"CLSLabSvc"

static SERVICE_STATUS        g_Status = {0};
static SERVICE_STATUS_HANDLE g_hStatus = NULL;
static HANDLE                g_hStopEvent = NULL;

static void ReportarEstado(DWORD dwCurrentState, DWORD dwWin32ExitCode, DWORD dwWaitHint) {
    static DWORD dwCheckPoint = 1;
    g_Status.dwServiceType      = SERVICE_WIN32_OWN_PROCESS;
    g_Status.dwCurrentState     = dwCurrentState;
    g_Status.dwWin32ExitCode    = dwWin32ExitCode;
    g_Status.dwWaitHint         = dwWaitHint;
    g_Status.dwControlsAccepted = (dwCurrentState == SERVICE_START_PENDING) ? 0 : (SERVICE_ACCEPT_STOP | SERVICE_ACCEPT_SHUTDOWN);
    g_Status.dwCheckPoint       = (dwCurrentState == SERVICE_RUNNING || dwCurrentState == SERVICE_STOPPED) ? 0 : dwCheckPoint++;
    if (g_hStatus) {
        SetServiceStatus(g_hStatus, &amp;g_Status);
    }
}

static DWORD WINAPI SvcCtrlHandlerEx(DWORD dwControl, DWORD dwEventType, LPVOID lpEventData, LPVOID lpContext) {
    (void)dwEventType; (void)lpEventData; (void)lpContext;
    switch (dwControl) {
        case SERVICE_CONTROL_STOP:
        case SERVICE_CONTROL_SHUTDOWN:
            ReportarEstado(SERVICE_STOP_PENDING, NO_ERROR, 2000);
            if (g_hStopEvent) SetEvent(g_hStopEvent);
            return NO_ERROR;
        case SERVICE_CONTROL_INTERROGATE:
            return NO_ERROR;
        default:
            return ERROR_CALL_NOT_IMPLEMENTED;
    }
}

static VOID WINAPI SvcLabMain(DWORD dwArgc, LPWSTR* lpszArgv) {
    (void)dwArgc; (void)lpszArgv;
    g_hStatus = RegisterServiceCtrlHandlerExW(SVC_NAME, SvcCtrlHandlerEx, NULL);
    if (!g_hStatus) return;

    ReportarEstado(SERVICE_START_PENDING, NO_ERROR, 2000);
    g_hStopEvent = CreateEventW(NULL, TRUE, FALSE, NULL);
    if (!g_hStopEvent) {
        ReportarEstado(SERVICE_STOPPED, GetLastError(), 0);
        return;
    }

    ReportarEstado(SERVICE_RUNNING, NO_ERROR, 0);
    WaitForSingleObject(g_hStopEvent, INFINITE);

    CloseHandle(g_hStopEvent);
    g_hStopEvent = NULL;
    ReportarEstado(SERVICE_STOPPED, NO_ERROR, 0);
}

int wmain(int argc, wchar_t* argv[]) {
    if (argc &gt; 1 &amp;&amp; wcscmp(argv[1], L"--console") == 0) {
        wprintf(L"[SvcLab] Modo diagnóstico de consola OK. Para usar con el SCM, registralo con sc.exe create.\n");
        return 0;
    }
    SERVICE_TABLE_ENTRYW DispatchTable[] = {
        { (LPWSTR)SVC_NAME, (LPSERVICE_MAIN_FUNCTIONW)SvcLabMain },
        { NULL, NULL }
    };
    if (!StartServiceCtrlDispatcherW(DispatchTable)) {
        DWORD err = GetLastError();
        if (err == ERROR_FAILED_SERVICE_CONTROLLER_CONNECT) {
            wprintf(L"Error 1063 (ERROR_FAILED_SERVICE_CONTROLLER_CONNECT): este binario es un servicio Win32.\n"
                    L"Inicialo con 'sc.exe start CLSLabSvc' o probalo con 'SvcLab.exe --console'.\n");
        }
        return (int)err;
    }
    return 0;
}

"""


PAGINA_CHEAT_SHEETS = """<h1 id="hojas-de-referencia-rápida-por-nivel-cheat-sheets">Hojas de referencia rápida por nivel (Cheat Sheets)</h1>
<p>Estas tres hojas condensan las tablas, fórmulas, desplazamientos de memoria, constantes mágicas y comandos de depuración de todo el curso, organizadas por nivel (<strong>Principiante</strong>, <strong>Intermedio</strong> y <strong>Avanzado</strong>) para tenerlas abiertas al lado del desensamblador o impresas en el escritorio.</p>

<h2 id="hoja-1-nivel-principiante-etapas-0-1-2a-3-y-4-base">Hoja 1 · Nivel Principiante (Etapas 0, 1, 2A, 3 y 4 base)</h2>

<h3 id="1-1-registros-x64-x86-y-regla-de-solapamiento-lección-2-1">1.1 Registros x64 / x86 y regla de solapamiento (Lección 2.1)</h3>
<div class="tabla"><table>
<thead><tr>
<th>64 bits</th>
<th>32 bits</th>
<th>16 bits</th>
<th>8 bits (alto / bajo)</th>
<th>Uso convencional en Windows x64 / x86</th>
<th>Preservación (ABI x64)</th>
</tr></thead><tbody>
<tr><td><code>RAX</code></td><td><code>EAX</code></td><td><code>AX</code></td><td><code>AH</code> / <code>AL</code></td><td>Valor de retorno entero o puntero; acumulador aritmético</td><td>Volátil (lo pisa la función llamada)</td></tr>
<tr><td><code>RCX</code></td><td><code>ECX</code></td><td><code>CX</code></td><td><code>CH</code> / <code>CL</code></td><td><strong>1.er argumento en x64</strong>; <code>this</code> en MSVC; contador de turnos/bucles</td><td>Volátil</td></tr>
<tr><td><code>RDX</code></td><td><code>EDX</code></td><td><code>DX</code></td><td><code>DH</code> / <code>DL</code></td><td><strong>2.º argumento en x64</strong>; parte alta en <code>MUL</code>/<code>DIV</code></td><td>Volátil</td></tr>
<tr><td><code>RBX</code></td><td><code>EBX</code></td><td><code>BX</code></td><td><code>BH</code> / <code>BL</code></td><td>Registro general preservado (suele guardar punteros o variables de bucle)</td><td><strong>No volátil</strong> (debe restaurarse)</td></tr>
<tr><td><code>RSP</code></td><td><code>ESP</code></td><td><code>SP</code></td><td><code>SPL</code></td><td>Puntero al tope actual del stack (crece hacia direcciones menores)</td><td><strong>No volátil</strong> (alineado a 16B antes de <code>CALL</code>)</td></tr>
<tr><td><code>RBP</code></td><td><code>EBP</code></td><td><code>BP</code></td><td><code>BPL</code></td><td>Puntero de marco de función (en x86: argumentos en <code>[ebp+8...]</code>, locales en <code>[ebp-...]</code>)</td><td><strong>No volátil</strong></td></tr>
<tr><td><code>RSI</code> / <code>RDI</code></td><td><code>ESI</code> / <code>EDI</code></td><td><code>SI</code> / <code>DI</code></td><td><code>SIL</code> / <code>DIL</code></td><td>Origen y destino en operaciones de bloques (<code>rep movsb</code>); variables locales</td><td><strong>No volátiles</strong> en Windows</td></tr>
<tr><td><code>R8</code>, <code>R9</code></td><td><code>R8D</code>, <code>R9D</code></td><td><code>R8W</code>, <code>R9W</code></td><td><code>R8B</code>, <code>R9B</code></td><td><strong>3.er y 4.º argumento entero/puntero en x64</strong></td><td>Volátiles</td></tr>
<tr><td><code>R10</code>, <code>R11</code></td><td><code>R10D</code>, <code>R11D</code></td><td><code>R10W</code>, <code>R11W</code></td><td><code>R10B</code>, <code>R11B</code></td><td>Temporales de llamada / <code>syscall</code></td><td>Volátiles</td></tr>
<tr><td><code>R12</code>–<code>R15</code></td><td><code>R12D</code>–<code>R15D</code></td><td><code>R12W</code>–<code>R15W</code></td><td><code>R12B</code>–<code>R15B</code></td><td>Registros de propósito general de larga vida en la función</td><td><strong>No volátiles</strong></td></tr>
</tbody></table></div>
<p><strong>Regla de oro en x64:</strong> Escribir en un subregistro de <strong>32 bits</strong> (p. ej. <code>mov eax, 1</code>) <strong>pone en cero los 32 bits superiores</strong> de <code>RAX</code>. Escribir en <strong>16 u 8 bits</strong> (<code>ax</code>, <code>al</code>) <strong>conserva intactos</strong> los bits restantes.</p>

<h3 id="1-2-flags-y-saltos-condicionales-tras-cmp-op1-op2-lección-2-4">1.2 Flags y saltos condicionales tras <code>CMP op1, op2</code> (Lección 2.4)</h3>
<div class="tabla"><table>
<thead><tr>
<th>Relación lógica (<code>op1</code> vs <code>op2</code>)</th>
<th>Salto SIN signo (<code>unsigned</code> / direcciones)</th>
<th>Salto CON signo (<code>int</code> / complemento a 2)</th>
<th>Condición exacta en los flags (<code>EFLAGS</code>)</th>
</tr></thead><tbody>
<tr><td>Igual (<code>op1 == op2</code>) / Cero</td><td><code>JE</code> / <code>JZ</code></td><td><code>JE</code> / <code>JZ</code></td><td><code>ZF = 1</code> (tras <code>test eax, eax</code>: salta si <code>eax == 0</code>)</td></tr>
<tr><td>Distinto (<code>op1 != op2</code>) / No cero</td><td><code>JNE</code> / <code>JNZ</code></td><td><code>JNE</code> / <code>JNZ</code></td><td><code>ZF = 0</code></td></tr>
<tr><td>Mayor estricto (<code>op1 &gt; op2</code>)</td><td><code>JA</code> / <code>JNBE</code> (<em>Above</em>)</td><td><code>JG</code> / <code>JNLE</code> (<em>Greater</em>)</td><td>Sin signo: <code>CF = 0 y ZF = 0</code> · Con signo: <code>ZF = 0 y SF == OF</code></td></tr>
<tr><td>Mayor o igual (<code>op1 &gt;= op2</code>)</td><td><code>JAE</code> / <code>JNB</code> / <code>JNC</code></td><td><code>JGE</code> / <code>JNL</code></td><td>Sin signo: <code>CF = 0</code> · Con signo: <code>SF == OF</code></td></tr>
<tr><td>Menor estricto (<code>op1 &lt; op2</code>)</td><td><code>JB</code> / <code>JNAE</code> / <code>JC</code> (<em>Below</em>)</td><td><code>JL</code> / <code>JNGE</code> (<em>Less</em>)</td><td>Sin signo: <code>CF = 1</code> · Con signo: <code>SF != OF</code></td></tr>
<tr><td>Menor o igual (<code>op1 &lt;= op2</code>)</td><td><code>JBE</code> / <code>JNA</code></td><td><code>JLE</code> / <code>JNG</code></td><td>Sin signo: <code>CF = 1 o ZF = 1</code> · Con signo: <code>ZF = 1 o SF != OF</code></td></tr>
</tbody></table></div>

<h3 id="1-3-conversión-va-rva-file-offset-y-convenciones-de-llamada-lecciones-1-2-1-4-y-2-5">1.3 Conversión VA &harr; RVA &harr; File Offset y convenciones de llamada (Lecciones 1.2, 1.4 y 2.5)</h3>
<pre><code class="lenguaje-text">RVA         = VA_en_memoria - ImageBase_actual
File Offset = RVA - VirtualAddress_sección + PointerToRawData_sección
VA_en_IDA   = Base_en_IDA + (VA_en_x64dbg - Base_en_x64dbg)   [Sincronización rápida con ASLR]</code></pre>
<div class="tabla"><table>
<thead><tr>
<th>Convención</th>
<th>Arquitectura</th>
<th>Dónde van los primeros argumentos</th>
<th>Quién limpia el stack</th>
<th>Detalle clave en el desensamblado</th>
</tr></thead><tbody>
<tr><td><code>cdecl</code></td><td>x86 (32 bits)</td><td>Todos en el stack (de derecha a izquierda; el 1.º en <code>[esp+4]</code> tras <code>call</code>)</td><td>El <strong>llamador</strong> (<code>add esp, N</code> después del <code>call</code>)</td><td>Permite funciones variádicas (<code>printf</code>, <code>scanf</code>).</td></tr>
<tr><td><code>stdcall</code></td><td>x86 (32 bits)</td><td>Todos en el stack (de derecha a izquierda)</td><td>La <strong>función llamada</strong> (<code>ret N</code>, p. ej. <code>ret 10h</code> = 4 args)</td><td>Estándar de la API Win32 de 32 bits (<code>MessageBoxA</code>, <code>WindowProc</code>).</td></tr>
<tr><td><code>fastcall</code></td><td>x86 (32 bits)</td><td>1.º en <code>ECX</code>, 2.º en <code>EDX</code>; del 3.º en adelante en el stack</td><td>La función llamada (<code>ret N</code> para los del stack)</td><td>En <strong>Delphi x86 (<code>register</code>)</strong>: 1.º <code>EAX</code>, 2.º <code>EDX</code>, 3.º <code>ECX</code> (2.13).</td></tr>
<tr><td><code>thiscall</code></td><td>x86 (MSVC)</td><td>Puntero <code>this</code> en <code>ECX</code>; argumentos explícitos en el stack</td><td>La función llamada (<code>ret N</code>)</td><td>En GCC/MinGW x86, <code>this</code> se apila como 1.er argumento oculto en el stack.</td></tr>
<tr><td><strong>Microsoft x64</strong></td><td>x64 (64 bits)</td><td>1.º <code>RCX</code> (o <code>XMM0</code>), 2.º <code>RDX</code> (<code>XMM1</code>), 3.º <code>R8</code> (<code>XMM2</code>), 4.º <code>R9</code> (<code>XMM3</code>); 5.º+ en <code>[rsp+20h]</code></td><td>El llamador (reserva marco fijo en su prólogo y libera en el epílogo)</td><td>El llamador reserva siempre <strong>32 bytes (<code>0x20</code>) de <em>Shadow Space</em></strong> en <code>[rsp+8..rsp+20h]</code> tras el <code>call</code>.</td></tr>
</tbody></table></div>

<div style="break-before: page; page-break-before: always;"></div>

<h2 id="hoja-2-nivel-intermedio-etapas-2b-2-17-2-21-4-2-4-5-5-1-5-3-y-2d-1-2d-5">Hoja 2 · Nivel Intermedio (Etapas 2B, 2.17, 2.21, 4.2, 4.5, 5.1, 5.3 y 2D.1–2D.5)</h2>

<h3 id="2-1-offsets-de-peb-peb-ldr-data-y-ldr-data-table-entry-lecciones-2-14-2-15-y-2d-2">2.1 Offsets de <code>PEB</code>, <code>PEB_LDR_DATA</code> y <code>LDR_DATA_TABLE_ENTRY</code> (Lecciones 2.14, 2.15 y 2D.2)</h3>
<div class="tabla"><table>
<thead><tr>
<th>Estructura / Campo</th>
<th>x86 (32 bits)</th>
<th>x64 (64 bits)</th>
<th>Desde <code>InMemoryOrderLinks</code> (x86 / x64)</th>
<th>Para qué lo usa el binario o el analista</th>
</tr></thead><tbody>
<tr><td>Puntero al <code>TEB</code> / al <code>PEB</code></td><td><code>fs:[0x18]</code> / <code>fs:[0x30]</code></td><td><code>gs:[0x30]</code> / <code>gs:[0x60]</code></td><td>—</td><td>Punto de partida de resolución de APIs y chequeos anti-debug</td></tr>
<tr><td><code>PEB.BeingDebugged</code> (1 byte)</td><td><code>+0x02</code></td><td><code>+0x02</code></td><td>—</td><td>Leído por <code>IsDebuggerPresent()</code> (<code>1</code> si hay debugger user-mode)</td></tr>
<tr><td><code>PEB.Ldr</code> (<code>PEB_LDR_DATA*</code>)</td><td><code>+0x0C</code></td><td><code>+0x18</code></td><td>—</td><td>Encabezado de las 3 listas circulares de DLLs cargadas</td></tr>
<tr><td><code>PEB.ProcessParameters</code></td><td><code>+0x10</code></td><td><code>+0x20</code></td><td>—</td><td>Contiene <code>ImagePathName</code> y <code>CommandLine</code></td></tr>
<tr><td><code>PEB.NtGlobalFlag</code> (<code>DWORD</code>)</td><td><code>+0x68</code></td><td><code>+0xBC</code></td><td>—</td><td>Vale <code>0x70</code> si el proceso fue creado por un debugger sin Page Heap</td></tr>
<tr><td><code>Ldr.InLoadOrderModuleList</code></td><td><code>+0x0C</code></td><td><code>+0x10</code></td><td>—</td><td>Lista en orden de carga (<code>Flink</code> apunta a <code>+0x00</code> del entry)</td></tr>
<tr><td><code>Ldr.InMemoryOrderModuleList</code></td><td><code>+0x14</code></td><td><code>+0x20</code></td><td>—</td><td>Lista más usada en shellcode/PEB walk (<code>Flink</code> apunta a <code>+0x08</code>/<code>+0x10</code>)</td></tr>
<tr><td><strong><code>LDR_DATA_TABLE_ENTRY</code><br><code>.DllBase</code></strong></td><td><strong><code>+0x18</code></strong></td><td><strong><code>+0x30</code></strong></td><td><strong><code>+0x10</code> (x86) / <code>+0x20</code> (x64)</strong></td><td>Base de la DLL en memoria (cabecera <code>MZ</code> para ir a la tabla de Exports)</td></tr>
<tr><td><code>LDR_DATA_TABLE_ENTRY</code><br><code>.FullDllName</code></td><td><code>+0x24</code></td><td><code>+0x48</code></td><td><code>+0x1C</code> (x86) / <code>+0x38</code> (x64)</td><td><code>UNICODE_STRING</code> con la ruta completa de la DLL</td></tr>
<tr><td><code>LDR_DATA_TABLE_ENTRY</code><br><code>.BaseDllName</code></td><td><code>+0x2C</code></td><td><code>+0x58</code></td><td><code>+0x24</code> (x86) / <code>+0x48</code> (x64)</td><td><code>UNICODE_STRING</code> con el nombre corto (p. ej. <code>kernel32.dll</code>; buffer en <code>+4</code>/<code>+8</code>)</td></tr>
</tbody></table></div>

<h3 id="2-2-constantes-mágicas-de-criptografía-hashing-y-encoding-lección-4-2">2.2 Constantes mágicas de criptografía, hashing y encoding (Lección 4.2)</h3>
<div class="tabla"><table>
<thead><tr>
<th>Algoritmo</th>
<th>Constantes / Bytes característicos en memoria o en instrucciones</th>
<th>Patrón estructural en el código desensamblado</th>
</tr></thead><tbody>
<tr><td><strong>AES (Rijndael)</strong></td><td>S-box: <code>63 7C 77 7B F2 6B 6F C5...</code> · Rcon: <code>01 02 04 08 10 20 40 80 1B 36</code></td><td>Tablas de 256 bytes (o T-tables de 1 KB) o instrucciones nativas <code>aesenc</code> / <code>aesdec</code> / <code>aeskeygenassist</code>.</td></tr>
<tr><td><strong>ChaCha20 / Salsa20</strong></td><td>ASCII <code>"expand 32-byte k"</code> (<code>0x61707865, 0x3320646e, 0x79622d32, 0x6b206574</code>)</td><td>Sin tablas; estado de 16 <code>DWORD</code>s (64B) y 20 rondas ARX (<code>add</code>, <code>xor</code>, <code>rol</code> de <strong>16, 12, 8 y 7 bits</strong>).</td></tr>
<tr><td><strong>RC4</strong></td><td>Sin constantes fijas; arreglo <code>S[256]</code> inicializado con <code>0x00..0xFF</code></td><td>Dos bucles de 256 iteraciones (KSA con módulo <code>&amp; 0xFF</code> e intercambio de bytes + PRGA con <code>xor</code> al flujo).</td></tr>
<tr><td><strong>TEA / XTEA</strong></td><td>Delta áureo: <code>0x9E3779B9</code> (o resta de <code>0x61C88647</code>); suma inicial <code>0xC6EF3720</code> (32 rondas)</td><td>Bucle de 32 o 64 iteraciones que combina <code>(v &lt;&lt; 4) ^ (v &gt;&gt; 5)</code> y suma el delta en cada vuelta.</td></tr>
<tr><td><strong>MD5 / SHA-1</strong></td><td>IV: <code>0x67452301</code>, <code>0xEFCDAB89</code>, <code>0x98BADCFE</code>, <code>0x10325476</code> (+ <code>0xC3D2E1F0</code> en SHA-1)</td><td>Procesamiento en bloques de 64 bytes (64 pasos en MD5; 80 pasos con rotaciones en SHA-1).</td></tr>
<tr><td><strong>SHA-256</strong></td><td>IV: <code>0x6A09E667</code>, <code>0xBB67AE85</code>, <code>0x3C6EF372</code>, <code>0xA54FF53A...</code> · <code>K[0] = 0x428A2F98</code></td><td>Tabla <code>K[64]</code> de 64 <code>DWORD</code>s y 64 rondas sobre 8 registros de estado (<code>a..h</code>).</td></tr>
<tr><td><strong>CRC32</strong></td><td>Polinomio reflejado: <code>0xEDB88320</code> (segunda entrada de tabla: <code>0x77073096</code>), IV <code>0xFFFFFFFF</code></td><td>Bucle por byte con <code>crc = (crc &gt;&gt; 8) ^ tabla[(crc ^ byte) &amp; 0xFF]</code> y <code>not crc</code> al final.</td></tr>
<tr><td><strong>Base64</strong></td><td>Tabla de 64 caracteres <code>"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"</code> y <code>'='</code></td><td>Toma grupos de 3 bytes (24 bits) y los divide en 4 índices de 6 bits (<code>&gt;&gt; 18</code>, <code>&gt;&gt; 12</code>, <code>&gt;&gt; 6</code>, <code>&amp; 0x3F</code>).</td></tr>
</tbody></table></div>

<h3 id="2-3-expresiones-de-x64dbg-scripting-y-frida-lecciones-2-6-y-2-21">2.3 Expresiones de x64dbg, scripting y Frida (Lecciones 2.6 y 2.21)</h3>
<pre><code class="lenguaje-text"># Breakpoint condicional universal (x86/x64) en WindowProc para botón ID 0x13A (WM_COMMAND = 0x111):
breakif:  arg.get(1) == 0x111 &amp;&amp; (arg.get(2) &amp; 0xFFFF) == 0x13A
log:      "WM_COMMAND control={arg.get(2)&amp;0xFFFF} notif={arg.get(2)&gt;&gt;16} hwnd={arg.get(0)}"

# Formateadores de log sin detener la ejecución (Break Condition = 0) en x64dbg:
ASCII: {s:rcx}   |   UTF-16: {utf16@rcx}   |   Bytes hex: {mem;16@rcx}   |   Retorno: {rax}

# Plantilla mínima de Frida (guardar como hook.js y correr: frida -f app.exe -l hook.js):
const addr = DebugSymbol.fromName("CreateFileW").address; // o base.add(0x1420)
Interceptor.attach(addr, {
  onEnter(args) { this.path = args[0].readUtf16String(); },
  onLeave(retval) { console.log("CreateFileW:", this.path, "-&gt; handle:", retval); }
});</code></pre>

<div style="break-before: page; page-break-before: always;"></div>

<h2 id="hoja-3-nivel-avanzado-etapas-2-18-2-20-2-24-5-2-2d-6-2d-13-y-etapa-6">Hoja 3 · Nivel Avanzado (Etapas 2.18–2.20, 2.24–2.33, 5.2, 2D.6–2D.13 y Etapa 6)</h2>

<h3 id="3-1-layout-en-memoria-de-c-en-msvc-x64-rtti-sso-stl-y-excepciones-lección-2-18">3.1 Layout en memoria de C++ en MSVC x64: RTTI, SSO, STL y excepciones (Lección 2.18)</h3>
<div class="tabla"><table>
<thead><tr>
<th>Estructura C++ (MSVC x64 Release)</th>
<th>Tamaño total</th>
<th>Desplazamientos y campos internos</th>
<th>Cómo reconocerla en el listado</th>
</tr></thead><tbody>
<tr><td><strong>Objeto con métodos virtuales + RTTI</strong></td><td><code>8B + campos</code></td><td><code>+0x00</code>: <code>vptr</code> (apunta a <code>vtable[0]</code> en <code>.rdata</code>). En <strong><code>vtable[-1]</code></strong> (<code>[vptr - 8]</code>) hay un puntero a <code>_RTTICompleteObjectLocator</code>: <code>+0x00 signature (1)</code>, <code>+0x04 offset</code>, <code>+0x0C pTypeDescriptor (RVA)</code>, <code>+0x10 pClassDescriptor (RVA)</code>, <code>+0x14 pSelf (RVA)</code>.</td><td>Llamada <code>mov rax, [rcx] ; call qword ptr [rax + 8*i]</code>. Sumar <code>ImageBase</code> a <code>pTypeDescriptor</code> lleva a <code>".?AVNombreClase@@"</code>.</td></tr>
<tr><td><strong><code>std::string</code> (SSO)</strong></td><td><code>32 bytes</code> (<code>0x20</code>)</td><td><code>+0x00..+0x0F</code>: unión <code>_Bx</code> (16B buffer local <code>_Buf</code> si <code>_Myres &lt; 16</code>, o puntero <code>_Ptr</code> de 8B en <code>+0x00</code> si <code>_Myres &gt;= 16</code>) · <code>+0x10</code>: <code>_Mysize</code> (8B) · <code>+0x18</code>: <code>_Myres</code> (8B, capacidad).</td><td>Comparación <code>cmp qword ptr [rcx+18h], 10h</code> seguida de un <code>cmovae rcx, [rcx]</code> antes de leer los caracteres.</td></tr>
<tr><td><strong><code>std::wstring</code> (SSO UTF-16)</strong></td><td><code>32 bytes</code> (<code>0x20</code>)</td><td>Igual layout de 32B, pero cada carácter ocupa 2 bytes: el umbral de SSO es <code>_Myres &lt; 8</code> caracteres (<code>cmp [rcx+18h], 8</code>).</td><td><code>cmp qword ptr [rcx+18h], 8</code> antes de elegir entre buffer inline y puntero <code>_Ptr</code>.</td></tr>
<tr><td><strong><code>std::vector&lt;T&gt;</code></strong></td><td><code>24 bytes</code> (<code>0x18</code>)</td><td><code>+0x00</code>: <code>_Myfirst</code> (inicio) · <code>+0x08</code>: <code>_Mylast</code> (fin de usados) · <code>+0x10</code>: <code>_Myend</code> (fin de reserva).</td><td>Cantidad de elementos = <code>(_Mylast - _Myfirst) / sizeof(T)</code>; bucle que itera desde <code>[rcx]</code> hasta <code>[rcx+8]</code>.</td></tr>
<tr><td><strong>Excepciones x64 (<code>.pdata</code> / <code>.xdata</code>)</strong></td><td>12B por entrada <code>.pdata</code></td><td><code>RUNTIME_FUNCTION</code>: 3 RVAs de 4B (<code>BeginAddress</code>, <code>EndAddress</code>, <code>UnwindData</code>). En <code>.xdata</code>, el handler apunta a <code>__CxxFrameHandler3</code> (<code>FuncInfo</code> con firma <code>0x19930520</code>) o <code>__CxxFrameHandler4</code> (<code>FuncInfo4</code> comprimido en VS 2019 16.3+/2022).</td><td>No hay cadena <code>FS:[0]</code> en el prólogo x64; las tablas viven fuera del flujo de código en <code>.pdata</code> y <code>.xdata</code>.</td></tr>
</tbody></table></div>

<h3 id="3-2-desglose-de-ctl-code-32-bits-y-métodos-de-ioctl-en-drivers-kmdf-wdm-lecciones-6-2-y-6-4">3.2 Desglose de <code>CTL_CODE</code> (32 bits) y métodos de IOCTL en drivers KMDF/WDM (Lecciones 6.2 y 6.4)</h3>
<pre><code class="lenguaje-text"> 31                  16 15    14 13                   2 1      0
┌──────────────────────┬────────┬──────────────────────┬────────┐
│   DeviceType (16b)   │ Access │    Function (12b)    │ Method │
│ 0x8000+ = fabricante │  (2b)  │  0x800+ = fabricante │  (2b)  │
└──────────────────────┴────────┴──────────────────────┴────────┘
Fórmula: (DeviceType &lt;&lt; 16) | (Access &lt;&lt; 14) | (Function &lt;&lt; 2) | Method
  Access: 0 = FILE_ANY_ACCESS | 1 = FILE_READ_DATA | 2 = FILE_WRITE_DATA | 3 = READ | WRITE
  Method: 0 = METHOD_BUFFERED (SystemBuffer compartido; seguro salvo punteros embebidos)
          1 = METHOD_IN_DIRECT  (entrada en SystemBuffer; 2.º buffer en Irp-&gt;MdlAddress p/lectura)
          2 = METHOD_OUT_DIRECT (entrada en SystemBuffer; 2.º buffer en Irp-&gt;MdlAddress p/escritura)
          3 = METHOD_NEITHER    (Type3InputBuffer y UserBuffer son punteros crudos de user-mode;
                                 exige EvtIoInCallerContext + ProbeAndLock + captura única)</code></pre>

<h3 id="3-3-niveles-de-irql-y-comandos-esenciales-de-windbg-lecciones-2-19-2d-2-2d-11-6-1-y-6-3">3.3 Niveles de <code>IRQL</code> y comandos esenciales de WinDbg (Lecciones 2.19, 2D.2, 2D.11, 6.1 y 6.3)</h3>
<div class="tabla"><table>
<thead><tr>
<th>IRQL</th>
<th>Contexto típico de ejecución</th>
<th>Memoria permitida</th>
<th>Sincronización y esperas permitidas</th>
</tr></thead><tbody>
<tr><td><code>PASSIVE_LEVEL (0)</code></td><td>Hilos de usuario, <code>DriverEntry</code>, <code>EvtDriverDeviceAdd</code>, mayoría de callbacks de archivos/registro</td><td><code>PagedPool</code> y <code>NonPagedPoolNx</code></td><td>Puede esperar (<code>KeWaitForSingleObject</code> con timeout != 0), usar mutexes/eventos y tocar código/datos paginables.</td></tr>
<tr><td><code>APC_LEVEL (1)</code></td><td>Regiones críticas / Guarded mutexes (<code>Fast Mutex</code>)</td><td><code>PagedPool</code> y <code>NonPagedPoolNx</code></td><td>APCs normales de hilo deshabilitadas; page faults aún permitidos.</td></tr>
<tr><td><code>DISPATCH_LEVEL (2)</code></td><td>DPCs (<code>EvtInterruptDpc</code>), código bajo <code>KSPIN_LOCK</code> (<code>KeAcquireSpinLock</code>)</td><td><strong>Solo <code>NonPagedPoolNx</code></strong> (tocar memoria paginada = bugcheck <code>0x0A</code> / <code>0xD1</code>)</td><td><strong>Prohibido esperar</strong> con intervalo no nulo (solo timeout = 0 y spinlocks). El despachador de hilos no puede cambiar de hilo en ese procesador.</td></tr>
<tr><td><code>DIRQL (&gt; 2)</code></td><td>Rutinas de servicio de interrupción de hardware (<code>ISR</code> / <code>EvtInterruptIsr</code>)</td><td><strong>Solo <code>NonPagedPoolNx</code></strong></td><td>Solo spinlocks de interrupción en su propio <code>DIRQL</code>; delegar el trabajo pesado a un DPC (<code>DISPATCH_LEVEL</code>).</td></tr>
</tbody></table></div>

<pre><code class="lenguaje-text"># 1. Triage de excepción o volcado (User-mode / Kernel-mode — Lecciones 2.19, 2D.11 y 6.3):
!analyze -v                  ; análisis automático del fallo / bugcheck
.exr -1                      ; muestra el EXCEPTION_RECORD actual (código y parámetros)
.ecxr                        ; restaura el contexto de registros en el instante exacto de la excepción
k   /   kv                   ; stack trace actual   |   ln &lt;addr&gt; : símbolo más cercano a una dirección

# 2. Diagnóstico de Heap, Memoria, PEB y WOW64 (Lecciones 2.19 y 2D.2):
!heap                        ; lista los heaps del proceso e indica Type (NT Heap vs Segment Heap)
!heap -p -a &lt;addr&gt;           ; con Full Page Heap activo: muestra el call stack que reservó/liberó el bloque
!vadump                      ; lista todas las regiones VAD en user-mode (Image / Mapped / Private)
!peb   /   !teb   /   lm     ; inspecciona PEB, TEB y lista de módulos cargados
!wow64exts.sw  /  !wow64exts.k ; alterna contexto 32/64 bits y muestra pila combinada en procesos WOW64

# 3. Time-Travel Debugging (TTD) y Kernel/WDF (Lecciones 2.19, 6.2 y 6.3):
g-   /   p-   /   t-         ; ejecuta hacia atrás / paso atrás sobre una traza TTD (.run)
ba w4 &lt;addr&gt;  ;  g-          ; frena en la instrucción pasada exacta que sobrescribió esos 4 bytes
dx @$cursession.TTD.Calls("ntdll!NtCreateFile")  ; consulta todas las llamadas a una API en la traza
!drvobj &lt;driver&gt; 7           ; muestra el DRIVER_OBJECT y su tabla de rutinas MajorFunction (IRP_MJ_*)
!wdfkd.wdflogdump &lt;driver&gt;   ; vuelca el In-flight Recorder (IFR) de un driver KMDF</code></pre>

<h3 id="3-4-desofuscación-y-dbi-bloque-2e-lecciones-2-25-2-33">3.4 · Desofuscación y análisis dinámico avanzado (Bloque 2E, Lecciones 2.25–2.33)</h3>
<div class="tabla"><table>
<thead><tr>
<th>Tarea</th>
<th>Herramienta y comando / API clave</th>
<th>Lección</th>
</tr></thead><tbody>
<tr><td><strong>Resolver una condición / clave</strong></td><td><strong>angr</strong>: <code>simgr.explore(find=…, avoid=…)</code>. En Windows arrancá en el prólogo de la validación (<code>blank_state(addr=…)</code> + <code>estado.regs.rcx = BUF_ADDR</code>) para no modelar el CRT.</td><td>2.25</td></tr>
<tr><td><strong>Demostrar que un MBA es una op simple</strong></td><td><strong>Z3</strong>: <code>prove((x ^ y) + 2*(x &amp; y) == x + y)</code> &rarr; <code>proved</code>.</td><td>2.25</td></tr>
<tr><td><strong>Reconocer una VM de protección</strong></td><td>Bucle <em>dispatcher</em> + tabla de <em>handlers</em> + VIP. Ojo con <em>threaded code</em>: handlers encadenados (<code>jmp [tabla+rbx*8]</code>) sin despachador central.</td><td>2.26</td></tr>
<tr><td><strong>Identificar packer / protector</strong></td><td><strong>DIE</strong> (<code>diec --entropy</code>): sección con entropía ~7,9 = comprimida/cifrada; IAT mínima o vacía (<em>splicing</em>/emulación de APIs) = empaquetado.</td><td>2.27</td></tr>
<tr><td><strong>Neutralizar anti-debug (en VM)</strong></td><td><strong>ScyllaHide</strong> (x64dbg) o hook de <strong>Frida</strong> sobre <code>IsDebuggerPresent</code>, PEB <code>BeingDebugged</code>, <code>rdtsc</code> y DRx (vía <code>NtGetContextThread</code> / VEH).</td><td>2.28</td></tr>
<tr><td><strong>Cobertura (colorear caminos)</strong></td><td><strong>DynamoRIO</strong>: <code>drrun -t drcov -- app.exe</code> &rarr; abrir en Lighthouse. <strong>Frida</strong>: <code>frida-drcov</code> / Stalker <code>compile</code>.</td><td>2.29 / 2.30</td></tr>
<tr><td><strong>Traza de instrucciones (reconstruir algoritmo)</strong></td><td><strong>Pin</strong>: <code>pin -t pinatrace.dll -- app.exe</code>; <strong>DynamoRIO</strong>: <code>drcachesim</code>; Frida Stalker <code>exec</code>.</td><td>2.29 / 2.30</td></tr>
<tr><td><strong>OEP genérico (sin conocer el packer)</strong></td><td>Regla <strong>W&oplus;X</strong>: avisar cuando se ejecuta una página escrita antes (DBI nativa o Stalker).</td><td>2.29 / 2.30</td></tr>
<tr><td><strong>Modelar un bytecode en Ghidra</strong></td><td><strong>SLEIGH</strong> (<code>.slaspec</code>) + <strong>PyGhidra</strong> (Python 3, estándar en Ghidra 11+; podés usar <code>z3-solver</code> en el script).</td><td>2.31</td></tr>
<tr><td><strong>Recuperar nombres Go / Rust</strong></td><td><strong>GoReSym</strong> (pclntab de un Go <em>stripped</em>); <strong>rustfilt</strong> (demangle v0 <code>_R…</code>); los <em>panics</em> (<code>panic_bounds_check</code>) revelan tamaños de buffer.</td><td>2.32</td></tr>
<tr><td><strong>VB6 en p-code</strong></td><td><strong>VB Decompiler</strong> (IDA/Ghidra solo muestran el intérprete de <code>MSVBVM60</code>, no la lógica).</td><td>2.33</td></tr>
<tr><td><strong>Protocolo propietario</strong></td><td>Hook en <code>send</code>/<code>recv</code> (texto claro) + disector <strong>Lua</strong> de Wireshark (<code>Proto</code>/<code>ProtoField</code>); reensamblar TCP con <code>pinfo.desegment_len</code>.</td><td>4.6</td></tr>
</tbody></table></div>
"""


PLANTILLAS_ARCHIVOS = {
    "check_evolucion.c": """// Archivo: plantillas_codigo/check_evolucion.c
// Compilar Principiante (MSVC): cl /Zi /Od check_evolucion.c /Fe:check_v1_O0.exe
// Compilar Optimizado   (MSVC): cl /Zi /O2 check_evolucion.c /Fe:check_v1_O2.exe
// Compilar Intermedio   (MSVC): cl /Zi /O1 /DMODO_INTERMEDIO check_evolucion.c /Fe:check_v2.exe
// Compilar en MinGW-w64 (GCC) : gcc -O0 -g check_evolucion.c -o check_v1_O0.exe
#include <windows.h>
#include <stdio.h>
#include <stdlib.h>

static int g_objetivo = 480; // 0x1E0 en condiciones normales

#ifdef MODO_INTERMEDIO
static void NTAPI tls_antidebug(PVOID h, DWORD reason, PVOID res) {
    (void)h; (void)res;
    if (reason == DLL_PROCESS_ATTACH && IsDebuggerPresent()) {
        g_objetivo = 999; // Desvia la constante antes de entrar a main (Lecciones 2.11 y 2.15)
    }
}
#ifdef _MSC_VER
#pragma comment(linker, "/INCLUDE:_tls_used")
#pragma section(".CRT$XLB", long, read)
__declspec(allocate(".CRT$XLB")) PIMAGE_TLS_CALLBACK p_tls = tls_antidebug;
#else
PIMAGE_TLS_CALLBACK p_tls __attribute__((used, section(".CRT$XLB"))) = tls_antidebug;
#endif
#endif

int validar_pares(int a, int b) {
    if (a > 50 || b < 50) return 0;
    return ((a + b) * 4) == g_objetivo;
}

int main(int argc, char** argv) {
    int a = (argc > 2) ? atoi(argv[1]) : 0;
    int b = (argc > 2) ? atoi(argv[2]) : 0;
    if (argc <= 2) {
        printf("Primer valor: ");  if (scanf("%d", &a) != 1) return 1;
        printf("Segundo valor: "); if (scanf("%d", &b) != 1) return 1;
    }
    if (validar_pares(a, b)) {
#ifdef MODO_INTERMEDIO
        // "Correcto" cifrado con XOR 0x5A (Lecciones 2.10 y 4.2)
        unsigned char enc[] = {0x19, 0x35, 0x28, 0x28, 0x3F, 0x39, 0x2E, 0x35, 0x00};
        for (int i = 0; enc[i] != 0; ++i) enc[i] ^= 0x5A;
        puts((const char*)enc);
#else
        puts("Correcto");
#endif
        return 0;
    }
    puts("Incorrecto");
    return 1;
}
""",
    "cpp_rtti_sso.cpp": """// Archivo: plantillas_codigo/cpp_rtti_sso.cpp
// Compilar (MSVC FH4 actual): cl /EHsc /GR /Zi /O1 cpp_rtti_sso.cpp /Fe:cpp_fh4.exe
// Compilar (MSVC FH3 clasico): cl /EHsc /GR /Zi /O1 /d2FH4- cpp_rtti_sso.cpp /Fe:cpp_fh3.exe
// Compilar (MinGW ABI Itanium): g++ -O1 -g cpp_rtti_sso.cpp -o cpp_itanium.exe
#include <iostream>
#include <string>
#include <vector>
#include <stdexcept>
#include <typeinfo>

struct Componente {
    int id = 0x10;
    virtual ~Componente() = default;
    virtual int evaluar(int a, int b) const = 0;
};
struct Auditable {
    int nivel_log = 2;
    virtual void registrar(const char* evento) const { std::cout << "[LOG] " << evento << "\\n"; }
};
class ValidadorBloc : public Componente, public Auditable {
    std::string etiqueta_corta = "BLOC_SSO";                        // < 16B: queda inline (SSO)
    std::string etiqueta_larga = "BLOC_CADENA_LARGA_EN_EL_HEAP_2026"; // >= 16B: reserva en heap
    std::vector<int> historial = {40, 80, 120};
public:
    int evaluar(int a, int b) const override {
        if (a < 0 || b < 0) throw std::runtime_error("Valores negativos no permitidos");
        return (a <= 50 && b >= 50 && (a + b) * 4 == (int)historial[2] * 4) ? 1 : 0;
    }
    void registrar(const char* ev) const override {
        std::cout << "[" << etiqueta_corta << "|" << etiqueta_larga.size() << "] " << ev << "\\n";
    }
};

int main(int argc, char** argv) {
    Componente* obj = new ValidadorBloc();
    std::cout << "RTTI: " << typeid(*obj).name() << "\\n";
    try {
        int res = obj->evaluar(argc > 1 ? std::stoi(argv[1]) : 40, 80);
        dynamic_cast<Auditable*>(obj)->registrar(res ? "OK" : "FALLO");
    } catch (const std::exception& ex) {
        std::cerr << "Excepcion capturada: " << ex.what() << "\\n";
    }
    delete obj;
    return 0;
}
""",
    "heap_bug.c": """// Archivo: plantillas_codigo/heap_bug.c
// Compilar v1 (vulnerable): cl /Zi /O1 heap_bug.c /Fe:heap_bug_v1.exe
// Compilar v2 (parcheada) : cl /Zi /O1 /DPARCHE_SEGURO heap_bug.c /Fe:heap_bug_v2.exe
// En la VM con Page Heap  : gflags /p /enable heap_bug_v1.exe /full
// Ejecutar en WinDbg      : heap_bug_v1.exe AAAAAAAAAAAAAAAAAAAA  --> !heap -p -a @rcx
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    char etiqueta[12];
    unsigned int estado;
} RegistroBloc; // sizeof(RegistroBloc) == 16 bytes exactos

int procesar_entrada(const char* entrada) {
    size_t len = strlen(entrada);
    RegistroBloc* reg = (RegistroBloc*)malloc(sizeof(RegistroBloc));
    if (!reg) return -1;
    reg->estado = 0xCAFE0001u;

#ifdef PARCHE_SEGURO
    // Version v2 corregida: valida el limite antes de copiar (Lecciones 2.20 y 5.2)
    if (len >= sizeof(reg->etiqueta)) {
        puts("Error: entrada excede el buffer de 12 bytes");
        free(reg);
        return 1;
    }
    memcpy(reg->etiqueta, entrada, len + 1);
#else
    // Version v1 con defecto didactico: copia hasta 20 bytes en un bloque de 16 bytes (Leccion 2.19)
    if (len > 20) len = 20;
    memcpy(reg->etiqueta, entrada, len);
    reg->etiqueta[11] = '\\0';
#endif
    printf("Registro: %s | Estado: 0x%08X\\n", reg->etiqueta, reg->estado);
    free(reg);
    return 0;
}

int main(int argc, char** argv) {
    const char* dato = (argc > 1) ? argv[1] : "BLOC_NORMAL";
    return procesar_entrada(dato);
}
""",
    "parser_clsf.c": """// Archivo: plantillas_codigo/parser_clsf.c
// Compilar (MSVC) : cl /Zi /O1 parser_clsf.c /Fe:parser_clsf.exe
// Compilar (MinGW): gcc -O1 -g parser_clsf.c -o parser_clsf.exe
// Generar muestra : parser_clsf.exe --gen muestra_A.clsf
// Analizar muestra: parser_clsf.exe muestra_A.clsf
#include <stdio.h>
#include <stdint.h>
#include <string.h>

#pragma pack(push, 1)
typedef struct {
    uint8_t  magic[4];   // +0x00: "CLSF" (43 4C 53 46)
    uint8_t  version;    // +0x04: 1
    uint8_t  flags;      // +0x05: 0
    uint16_t hdr_len;    // +0x06: 12 (0x000C LE)
    uint16_t body_len;   // +0x08: longitud del cuerpo (LE)
    uint16_t seq_id;     // +0x0A: campo variable / secuencia (0x002A = 42 LE)
} CabeceraCLSF;          // Total cabecera: 12 bytes
#pragma pack(pop)

int main(int argc, char** argv) {
    if (argc == 3 && strcmp(argv[1], "--gen") == 0) {
        CabeceraCLSF h = {{'C','L','S','F'}, 1, 0, 12, 5, 42};
        FILE* f = fopen(argv[2], "wb");
        if (!f) return 1;
        fwrite(&h, sizeof(h), 1, f);
        fwrite("HELLO", 1, 5, f);
        fclose(f);
        puts("Muestra CLSF de 17 bytes generada.");
        return 0;
    }
    if (argc < 2) { puts("Uso: parser_clsf [--gen salida.clsf | entrada.clsf]"); return 1; }
    FILE* f = fopen(argv[1], "rb");
    if (!f) return 2;
    uint8_t buf[256] = {0};
    size_t n = fread(buf, 1, sizeof(buf), f);
    fclose(f);
    if (n < sizeof(CabeceraCLSF)) { puts("Error: archivo truncado"); return 3; }
    const CabeceraCLSF* h = (const CabeceraCLSF*)buf;
    if (memcmp(h->magic, "CLSF", 4) != 0) { puts("Error: magic invalido"); return 4; }
    if (h->version != 1)                  { puts("Error: version no soportada"); return 5; }
    if (h->hdr_len != 12)                 { puts("Error: hdr_len != 12"); return 6; }
    if ((size_t)h->hdr_len + h->body_len > n) { puts("Error: body_len excede archivo"); return 7; }
    printf("CLSF OK | ver=%u flags=0x%02X seq=%u body(%u)=\\"%.*s\\"\\n",
           h->version, h->flags, h->seq_id, h->body_len, h->body_len, (const char*)(buf + h->hdr_len));
    return 0;
}
""",
    "pipe_server_min.c": """// Archivo: plantillas_codigo/pipe_server_min.c
// Compilar (MSVC) : cl /Zi /O1 pipe_server_min.c /Fe:pipe_server_min.exe
// Compilar (MinGW): gcc -O1 -g pipe_server_min.c -o pipe_server_min.exe
// Probar en Python: open(r'\\\\.\\pipe\\BlocLabPipe', 'r+b', buffering=0)
#include <windows.h>
#include <stdio.h>
#include <string.h>

int main(void) {
    const wchar_t* nombre = L"\\\\\\\\.\\\\pipe\\\\BlocLabPipe";
    HANDLE hPipe = CreateNamedPipeW(
        nombre,
        PIPE_ACCESS_DUPLEX | FILE_FLAG_FIRST_PIPE_INSTANCE,
        PIPE_TYPE_MESSAGE | PIPE_READMODE_MESSAGE | PIPE_WAIT | PIPE_REJECT_REMOTE_CLIENTS,
        1, 256, 256, 0, NULL);
    if (hPipe == INVALID_HANDLE_VALUE) {
        printf("CreateNamedPipeW fallo (GLE=%lu)\\n", GetLastError());
        return 1;
    }
    puts("[ESPERA_SALUDO] Escuchando en \\\\.\\pipe\\BlocLabPipe ...");
    if (ConnectNamedPipe(hPipe, NULL) || GetLastError() == ERROR_PIPE_CONNECTED) {
        char buf[128] = {0};
        DWORD leidos = 0, escritos = 0;
        if (ReadFile(hPipe, buf, sizeof(buf) - 1, &leidos, NULL) && leidos >= 4 && memcmp(buf, "CLSF", 4) == 0) {
            puts("[LISTO] Saludo CLSF valido recibido; enviando respuesta fija.");
            const char resp[] = "CLSF_ACK_V1_READY";
            WriteFile(hPipe, resp, (DWORD)strlen(resp), &escritos, NULL);
        } else {
            const char err[] = "CLSF_ERR_BAD_HELLO";
            WriteFile(hPipe, err, (DWORD)strlen(err), &escritos, NULL);
        }
        FlushFileBuffers(hPipe);
        DisconnectNamedPipe(hPipe);
    }
    CloseHandle(hPipe);
    return 0;
}
""",
    "bloclab_kmdf_min.c": """// Archivo: plantillas_codigo/bloclab_kmdf_min.c
// Plantilla 6 (Tomo II, Lección 6.2): bloclab_kmdf_min.c
// Esqueleto mínimo KMDF para análisis estático en IDA/Ghidra y prueba en VM descartable.
// El SDDL restringe la apertura únicamente a SYSTEM y Administradores.
#include <ntddk.h>
#include <wdf.h>
#include <wdmsec.h>

#define IOCTL_BLOCLAB_QUERY_VERSION \
    CTL_CODE(0x8000, 0x800, METHOD_BUFFERED, FILE_READ_DATA) // 0x80006000

typedef struct _BLOCLAB_INFO {
    ULONG Size;
    ULONG Version;
    ULONG State;
} BLOCLAB_INFO, *PBLOCLAB_INFO;

EVT_WDF_DRIVER_DEVICE_ADD BlocLabEvtDeviceAdd;
EVT_WDF_IO_QUEUE_IO_DEVICE_CONTROL BlocLabEvtIoDeviceControl;

NTSTATUS DriverEntry(PDRIVER_OBJECT DriverObject, PUNICODE_STRING RegistryPath) {
    WDF_DRIVER_CONFIG config;
    WDF_DRIVER_CONFIG_INIT(&config, BlocLabEvtDeviceAdd); // +0x08 en x64 = EvtDriverDeviceAdd
    return WdfDriverCreate(DriverObject, RegistryPath, WDF_NO_OBJECT_ATTRIBUTES, &config, WDF_NO_HANDLE);
}

NTSTATUS BlocLabEvtDeviceAdd(WDFDRIVER Driver, PWDFDEVICE_INIT DeviceInit) {
    UNREFERENCED_PARAMETER(Driver);
    DECLARE_CONST_UNICODE_STRING(ntDeviceName, L"\\Device\\BlocLab");
    DECLARE_CONST_UNICODE_STRING(symbolicLink, L"\\DosDevices\\BlocLab");

    NTSTATUS status = WdfDeviceInitAssignName(DeviceInit, &ntDeviceName);
    if (!NT_SUCCESS(status)) return status;

    // Restringe apertura únicamente a SYSTEM y Administradores:
    status = WdfDeviceInitAssignSDDLString(DeviceInit, &SDDL_DEVOBJ_SYS_ALL_ADM_ALL);
    if (!NT_SUCCESS(status)) return status;

    WDFDEVICE device;
    status = WdfDeviceCreate(&DeviceInit, WDF_NO_OBJECT_ATTRIBUTES, &device);
    if (!NT_SUCCESS(status)) return status;

    status = WdfDeviceCreateSymbolicLink(device, &symbolicLink);
    if (!NT_SUCCESS(status)) return status;

    WDF_IO_QUEUE_CONFIG queueConfig;
    WDF_IO_QUEUE_CONFIG_INIT_DEFAULT_QUEUE(&queueConfig, WdfIoQueueDispatchSequential);
    queueConfig.EvtIoDeviceControl = BlocLabEvtIoDeviceControl; // +0x28 en x64

    return WdfIoQueueCreate(device, &queueConfig, WDF_NO_OBJECT_ATTRIBUTES, WDF_NO_HANDLE);
}

VOID BlocLabEvtIoDeviceControl(WDFQUEUE Queue, WDFREQUEST Request,
                               size_t OutputBufferLength, size_t InputBufferLength,
                               ULONG IoControlCode) {
    UNREFERENCED_PARAMETER(Queue);
    UNREFERENCED_PARAMETER(OutputBufferLength);

    if (IoControlCode != IOCTL_BLOCLAB_QUERY_VERSION) {
        WdfRequestComplete(Request, STATUS_INVALID_DEVICE_REQUEST);
        return;
    }
    if (InputBufferLength != 0) {
        WdfRequestComplete(Request, STATUS_INVALID_PARAMETER);
        return;
    }

    PBLOCLAB_INFO outBuf = NULL;
    // Valida automáticamente que OutputBufferLength >= sizeof(BLOCLAB_INFO) (12 bytes):
    NTSTATUS status = WdfRequestRetrieveOutputBuffer(Request, sizeof(BLOCLAB_INFO), (PVOID*)&outBuf, NULL);
    if (!NT_SUCCESS(status)) {
        WdfRequestComplete(Request, status); // Devuelve STATUS_BUFFER_TOO_SMALL
        return;
    }

    RtlZeroMemory(outBuf, sizeof(BLOCLAB_INFO));
    outBuf->Size    = sizeof(BLOCLAB_INFO);
    outBuf->Version = 1;
    outBuf->State   = 1; // READY
    WdfRequestCompleteWithInformation(Request, STATUS_SUCCESS, sizeof(BLOCLAB_INFO));
}
""",
    "svclab_min.c": """// Archivo: plantillas_codigo/svclab_min.c
// Práctica para Lección 2D.4 (Servicios: SCM, ciclo de vida, cuentas y auditoría)
// Compilar (MSVC) : cl /Zi /O1 /DUNICODE /D_UNICODE svclab_min.c advapi32.lib /Fe:SvcLab.exe
// Compilar (MinGW): gcc -O1 -g -municode svclab_min.c -ladvapi32 -o SvcLab.exe
// Probar en consola antes de registrar: SvcLab.exe --console
// Registrar en VM (cmd elevado):
//   sc.exe create CLSLabSvc binPath= "C:\CLS-Lab\SvcLab.exe" start= demand obj= "NT AUTHORITY\LocalService"
//   sc.exe start CLSLabSvc
//   sc.exe query CLSLabSvc
//   sc.exe stop CLSLabSvc
//   sc.exe delete CLSLabSvc

#include <windows.h>
#include <stdio.h>

#ifdef _MSC_VER
#pragma comment(lib, "advapi32.lib")
#endif

#define SVC_NAME L"CLSLabSvc"

static SERVICE_STATUS        g_Status = {0};
static SERVICE_STATUS_HANDLE g_hStatus = NULL;
static HANDLE                g_hStopEvent = NULL;

static void ReportarEstado(DWORD dwCurrentState, DWORD dwWin32ExitCode, DWORD dwWaitHint) {
    static DWORD dwCheckPoint = 1;
    g_Status.dwServiceType      = SERVICE_WIN32_OWN_PROCESS;
    g_Status.dwCurrentState     = dwCurrentState;
    g_Status.dwWin32ExitCode    = dwWin32ExitCode;
    g_Status.dwWaitHint         = dwWaitHint;
    g_Status.dwControlsAccepted = (dwCurrentState == SERVICE_START_PENDING) ? 0 : (SERVICE_ACCEPT_STOP | SERVICE_ACCEPT_SHUTDOWN);
    g_Status.dwCheckPoint       = (dwCurrentState == SERVICE_RUNNING || dwCurrentState == SERVICE_STOPPED) ? 0 : dwCheckPoint++;
    if (g_hStatus) {
        SetServiceStatus(g_hStatus, &g_Status);
    }
}

static DWORD WINAPI SvcCtrlHandlerEx(DWORD dwControl, DWORD dwEventType, LPVOID lpEventData, LPVOID lpContext) {
    (void)dwEventType; (void)lpEventData; (void)lpContext;
    switch (dwControl) {
        case SERVICE_CONTROL_STOP:
        case SERVICE_CONTROL_SHUTDOWN:
            ReportarEstado(SERVICE_STOP_PENDING, NO_ERROR, 2000);
            if (g_hStopEvent) SetEvent(g_hStopEvent);
            return NO_ERROR;
        case SERVICE_CONTROL_INTERROGATE:
            return NO_ERROR;
        default:
            return ERROR_CALL_NOT_IMPLEMENTED;
    }
}

static VOID WINAPI SvcLabMain(DWORD dwArgc, LPWSTR* lpszArgv) {
    (void)dwArgc; (void)lpszArgv;
    g_hStatus = RegisterServiceCtrlHandlerExW(SVC_NAME, SvcCtrlHandlerEx, NULL);
    if (!g_hStatus) return;

    ReportarEstado(SERVICE_START_PENDING, NO_ERROR, 2000);
    g_hStopEvent = CreateEventW(NULL, TRUE, FALSE, NULL);
    if (!g_hStopEvent) {
        ReportarEstado(SERVICE_STOPPED, GetLastError(), 0);
        return;
    }

    ReportarEstado(SERVICE_RUNNING, NO_ERROR, 0);
    // Espera pasiva sin consumir CPU hasta que el SCM envíe SERVICE_CONTROL_STOP
    WaitForSingleObject(g_hStopEvent, INFINITE);

    CloseHandle(g_hStopEvent);
    g_hStopEvent = NULL;
    ReportarEstado(SERVICE_STOPPED, NO_ERROR, 0);
}

int wmain(int argc, wchar_t* argv[]) {
    if (argc > 1 && wcscmp(argv[1], L"--console") == 0) {
        wprintf(L"[SvcLab] Modo diagnóstico de consola OK. Para usar con el SCM, registralo con sc.exe create.\n");
        return 0;
    }
    SERVICE_TABLE_ENTRYW DispatchTable[] = {
        { (LPWSTR)SVC_NAME, (LPSERVICE_MAIN_FUNCTIONW)SvcLabMain },
        { NULL, NULL }
    };
    if (!StartServiceCtrlDispatcherW(DispatchTable)) {
        DWORD err = GetLastError();
        if (err == ERROR_FAILED_SERVICE_CONTROLLER_CONNECT) {
            wprintf(L"Error 1063 (ERROR_FAILED_SERVICE_CONTROLLER_CONNECT): este binario es un servicio Win32.\n"
                    L"Inicialo con 'sc.exe start CLSLabSvc' o probalo con 'SvcLab.exe --console'.\n");
        }
        return (int)err;
    }
    return 0;
}
""",
}
