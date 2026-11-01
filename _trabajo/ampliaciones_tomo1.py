# -*- coding: utf-8 -*-
"""Ampliaciones editoriales de nivel avanzado para el Tomo I:
1. Reversing práctico de Go y Rust (pclntab, strings, ABI y enums)
2. Reversing de DLLs, ciclo de vida, depuración y DLL Sideloading / Proxying
3. Anatomía de la inyección de procesos en user-mode (Hollowing, Early Bird APC y Reflective Loading)
4. Criptografía asimétrica (RSA/ECC) e intercepción en APIs nativas de Windows (CryptoAPI y CNG)
5. Evasión en User-Mode: API Hooking de EDRs vs. Syscalls Directas (Hell's Gate / Halo's Gate)
6. Flujo operativo de trinchera en x64dbg y extracción masiva de strings cifradas
"""

AMPLIACION_GO_RUST = """
<aside class="ampliacion-ext">
<p class="callout-titulo">Ampliación editorial basada en fuentes externas — Metodología de reversing para binarios en Go (pclntab, strings y ABI) y Rust (mangling v0 y enums)</p>
<p>Dada la proliferación de binarios compilados en <strong>Go</strong> y <strong>Rust</strong> en software de sistema, herramientas defensivas y amenazas modernas, su análisis requiere técnicas específicas que difieren sustancialmente del código compilado en C/C++ clásico:</p>

<h4 style="margin: 0.8rem 0 0.4rem 0; color: #1d4f2a;">1. Reversing de Binarios en Go</h4>
<ul>
<li><strong>Recuperación de símbolos mediante la tabla <code>pclntab</code>:</strong> El compilador de Go (<code>gc</code>) enlaza una tabla en la sección <code>.gopclntab</code> o <code>.rodata</code> denominada <em>Program Counter Line Table</em> (<a href="https://go.dev/src/runtime/symtab.go" rel="noopener" target="_blank">Go Runtime: symtab.go</a>). Esta estructura asocia cada dirección virtual con el nombre de su función, archivo fuente <code>.go</code> y número de línea. En binarios sin símbolos (<em>stripped</em>), <code>pclntab</code> <strong>permanece intacta</strong> porque el recolector de basura, el planificador y <code>runtime.panic</code> la necesitan para generar trazas de pila.
<br><em>Herramientas de recuperación:</em> Plugins como <code>go_parser</code> (IDA Pro), el analizador integrado <em>Go Module Analyzer</em> (Ghidra 11+) o la utilidad <code>GoReSym</code> leen el número mágico al inicio de la tabla (<code>0xFFFFFFFB</code> en Go 1.2, <code>0xFFFFFFFA</code> en Go 1.16, <code>0xFFFFFFF0</code> en Go 1.18+ y <code>0xFFFFFFF1</code> en Go 1.20+) y renuevan en pocos segundos los nombres de las 2.000+ funciones (revelando de inmediato funciones críticas como <code>main.main</code> o <code>main.verificarLicencia</code>).</li>
<li><strong>Estructura interna de cadenas (<code>string</code>):</strong> Un <code>string</code> en Go es un par inmutable <code>struct { const char* str; ptrdiff_t len; }</code> (16 bytes en x64). No contiene terminador nulo <code>0x00</code>. En desensamblado x64 se reconoce el patrón invariable de carga del puntero seguido de su tamaño en un registro secundario:
<pre><code>lea rax, [rip + 0x2A150]   ; Puntero al inicio del buffer en .rodata
mov rbx, 0x18              ; Longitud exacta: 24 bytes (sin terminador nulo)</code></pre></li>
<li><strong>Convención de llamadas por registros (Go 1.17+ ABI):</strong> A partir de Go 1.17, las funciones internas pasan argumentos y retornos en 9 registros enteros ordenados: <code>RAX</code>, <code>RBX</code>, <code>RCX</code>, <code>RDI</code>, <code>RSI</code>, <code>R8</code>, <code>R9</code>, <code>R10</code>, <code>R11</code>, pasando a la pila solo los excedentes.</li>
<li><strong>Prólogo de comprobación de pila:</strong> En el inicio de casi toda función Go aparece una comprobación con el puntero de la goroutine activa (almacenado en <code>R14</code> en x64):
<pre><code>cmp rsp, qword ptr [r14 + 0x10]   ; Comprueba límite de pila de la goroutine
jbe runtime.morestack             ; Aloca un segmento de pila nuevo si falta espacio</code></pre></li>
</ul>

<h4 style="margin: 0.8rem 0 0.4rem 0; color: #1d4f2a;">2. Reversing de Binarios en Rust</h4>
<ul>
<li><strong>Name Mangling v0 (RFC 2603):</strong> Desde Rust 1.59+, los símbolos usan el esquema estándar iniciado con el prefijo <code>_R</code> (<a href="https://rust-lang.github.io/rfcs/2603-symbol-mangling-v0.html" rel="noopener" target="_blank">Rust RFC 2603</a>). Nombres crudos como <code>_RNvNtCs1234_7mi_app4auth14verificar_pass</code> se decodifican de inmediato con la herramienta oficial <code>rustfilt</code> a <code>mi_app::auth::verificar_pass</code>.</li>
<li><strong>Tipos algebraicos <code>Result&lt;T, E&gt;</code> y <code>Option&lt;T&gt;</code>:</strong> En memoria se compilan como estructuras con un byte discriminante (*tag*):
<pre><code>struct Option_u32 {
    uint8_t  tag;   // 0 = None, 1 = Some
    uint32_t valor; // Válido únicamente si tag == 1
};</code></pre>
En ensamblador se observa la comprobación del byte discriminante previa a operar con el dato (<code>cmp byte ptr [rsp+0x18], 1 ; jne fallo</code>).</li>
<li><strong>Manejo de pánicos y cadenas de error:</strong> Cuando una función aborta, Rust invoca a <code>core::panicking::panic_fmt</code> pasando una estructura que contiene el nombre del archivo fuente <code>.rs</code> y la línea exacta como cadenas ASCII legibles en <code>.rdata</code>.</li>
</ul>
</aside>
</section>
"""

AMPLIACION_DLL_SIDELOADING = """
<section class="subseccion-ampliacion" id="ciclo-vida-dll-sideloading">
<h2 id="ampliacion-ciclo-vida-dll">Ampliación: Ciclo de vida de DLLs, depuración y técnica de DLL Sideloading / Proxying</h2>
<aside class="ampliacion-ext">
<p class="callout-titulo">Ampliación editorial basada en fuentes externas</p>
<p>Las bibliotecas de enlace dinámico (<code>.dll</code>) constituyen la unidad fundamental de modularidad y ejecución en Windows. Su análisis dinámico y los vectores de interceptación más comunes se rigen por las siguientes reglas técnicas (<a href="https://learn.microsoft.com/en-us/windows/win32/dlls/dynamic-link-library-best-practices" rel="noopener" target="_blank">Microsoft Learn: DLL Best Practices</a>):</p>

<h4 style="margin: 0.8rem 0 0.4rem 0; color: #1d4f2a;">1. Ciclo de Vida y DllMain</h4>
<p>El punto de entrada de una DLL tiene la firma estandarizada:</p>
<pre><code>BOOL WINAPI DllMain(HINSTANCE hinstDLL, DWORD fdwReason, LPVOID lpvReserved);</code></pre>
<ul>
<li><strong><code>DLL_PROCESS_ATTACH</code> (1):</strong> Se ejecuta cuando el proceso mapea la DLL por primera vez (mediante import estático o llamada explícita a <code>LoadLibraryA/W</code>). Si <code>DllMain</code> devuelve <code>FALSE</code>, el proceso anfitrión aborta su inicio con error de inicialización.</li>
<li><strong><code>DLL_THREAD_ATTACH</code> (2) / <code>DLL_THREAD_DETACH</code> (3):</strong> Se invocan cada vez que un hilo secundario se crea o termina limpiamente en el proceso.</li>
<li><strong><code>DLL_PROCESS_DETACH</code> (0):</strong> Se ejecuta cuando la DLL es descargada (vía <code>FreeLibrary</code> o al cerrar el proceso).</li>
<li><strong>La restricción del <em>Loader Lock</em>:</strong> Durante la ejecución de <code>DllMain</code>, el sistema mantiene adquirido un bloqueo exclusivo del cargador (<em>Loader Lock</em>). Intentar llamar a <code>LoadLibrary</code>, crear procesos o sincronizar hilos dentro de <code>DllMain</code> puede provocar un interbloqueo (*deadlock*) irreversible.</li>
</ul>

<h4 style="margin: 0.8rem 0 0.4rem 0; color: #1d4f2a;">2. Cómo Depurar una DLL en x64dbg e IDA Pro</h4>
<ul>
<li><strong>Opción A — Mediante Rundll32:</strong> Configurar como ejecutable anfitrión en el depurador:
<pre><code>C:\\Windows\\System32\\rundll32.exe C:\\ruta\\libreria.dll,NombreDeExportada</code></pre></li>
<li><strong>Opción B — Eventos de carga en x64dbg:</strong> En x64dbg, acceder a <em>Opciones -> Preferencias -> Eventos</em> y activar la casilla <strong>DLL Entry</strong>. Al lanzar cualquier ejecutable anfitrión, el depurador interrumpirá la ejecución automáticamente en el <code>DllMain</code> de la biblioteca tan pronto el sistema la proyecte en memoria.</li>
<li><strong>Opción C — Arnés en C (Harness):</strong> Compilar un lanzador de prueba mínimo de 4 líneas que invoque <code>LoadLibraryA("muestra.dll")</code> y llame a la función exportada mediante <code>GetProcAddress</code>.</li>
</ul>

<h4 style="margin: 0.8rem 0 0.4rem 0; color: #1d4f2a;">3. DLL Sideloading y DLL Proxying con Export Forwarding</h4>
<ul>
<li><strong>Orden estándar de búsqueda de DLLs (<code>SafeDllSearchMode</code>):</strong>
1. Directorio donde reside el ejecutable anfitrión (<code>.exe</code>).
2. Directorio del sistema (<code>System32</code>).
3. Directorio de Windows (<code>C:\\Windows</code>).
4. Directorio de trabajo actual (CWD).
5. Directorios declarados en la variable de entorno <code>PATH</code>.</li>
<li><strong>Vulnerabilidad de DLL Sideloading:</strong> Si un ejecutable legítimo y firmado busca una biblioteca que no está en la lista de <code>KnownDLLs</code> del registro (p. ej. <code>version.dll</code> o <code>cryptbase.dll</code>), cargará la copia situada en su misma carpeta antes que la copia oficial de <code>System32</code>.</li>
<li><strong>DLL Proxying con reenvío de exportaciones (<em>Export Forwarding</em>):</strong> Para ejecutar lógica propia en <code>DLL_PROCESS_ATTACH</code> sin que la aplicación anfitriona falle por funciones faltantes, la DLL desarrollada redirige sus exportaciones a la biblioteca legítima de Windows mediante directivas de enlace:
<pre><code>#pragma comment(linker, "/export:VerQueryValueW=C:\\\\Windows\\\\System32\\\\version.VerQueryValueW")
#pragma comment(linker, "/export:GetFileVersionInfoW=C:\\\\Windows\\\\System32\\\\version.GetFileVersionInfoW")</code></pre></li>
</ul>
</aside>
"""

AMPLIACION_INYECCION_PROCESOS = """
<aside class="ampliacion-ext">
<p class="callout-titulo">Ampliación editorial basada en fuentes externas — Anatomía de la inyección de procesos en memoria: Process Hollowing, Early Bird APC y Reflective Loading</p>
<p>En el análisis de software dinámico y amenazas defensivas, las técnicas de inyección en user-mode buscan ejecutar código dentro del espacio de direcciones virtual de un proceso legítimo para enmascarar su presencia (<a href="https://learn.microsoft.com/en-us/windows/win32/procthread/process-creation-flags" rel="noopener" target="_blank">Microsoft Learn: Process Creation Flags</a>):</p>

<div class="tabla"><table>
<thead><tr><th>Técnica de Inyección</th><th>Secuencia de APIs Clave</th><th>Comportamiento y Huella en Memoria</th><th>Detección y Caza</th></tr></thead>
<tbody>
<tr><td><strong>Inyección Clásica (CreateRemoteThread)</strong></td><td><code>OpenProcess</code> -> <code>VirtualAllocEx(RWX)</code> -> <code>WriteProcessMemory</code> -> <code>CreateRemoteThread</code></td><td>Aloca un bloque independiente en un proceso ya en ejecución y crea un hilo remoto.</td><td>Interceptada por telemetría del kernel (<code>PsSetCreateThreadNotifyRoutine</code>) y monitores de API.</td></tr>
<tr><td><strong>Process Hollowing (RunPE)</strong></td><td><code>CreateProcess(CREATE_SUSPENDED)</code> -> <code>NtUnmapViewOfSection</code> -> <code>VirtualAllocEx</code> -> <code>WriteProcessMemory</code> -> <code>SetThreadContext</code> -> <code>ResumeThread</code></td><td>Vacia el binario legítimo original de la memoria del proceso y proyecta un ejecutable completamente nuevo.</td><td>Discrepancia entre la memoria mapeada y el archivo en disco (detectable con <code>PE-sieve</code> o inspección de VAD).</td></tr>
<tr><td><strong>Early Bird APC Injection</strong></td><td><code>CreateProcess(CREATE_SUSPENDED)</code> -> <code>VirtualAllocEx</code> -> <code>WriteProcessMemory</code> -> <code>QueueUserAPC</code> -> <code>ResumeThread</code></td><td>Encola una Asynchronous Procedure Call (APC) antes de que inicie el hilo principal, ejecutándose en el primer estado de alerta.</td><td>Monitoreo de llamadas a <code>QueueUserAPC</code> dirigidas al hilo primario de procesos recién creados.</td></tr>
<tr><td><strong>Reflective DLL Injection</strong></td><td><code>VirtualAllocEx</code> -> <code>WriteProcessMemory</code> -> <code>CreateRemoteThread(offset_ReflectiveLoader)</code></td><td>La DLL inyectada incluye su propio loader interno que resuelve imports y relocalizaciones sin usar <code>LoadLibrary</code>.</td><td>La DLL no figura en las listas del PEB (<code>InLoadOrderModuleList</code>), dejando páginas de memoria huérfanas con permisos de ejecución.</td></tr>
</tbody>
</table></div>

<h4 style="margin: 0.8rem 0 0.4rem 0; color: #1d4f2a;">Flujo paso a paso de Process Hollowing (RunPE)</h4>
<ol>
<li><strong>Creación suspendida:</strong> El cargador inicia un proceso del sistema benigno (ej. <code>svchost.exe</code>) pasando el flag <code>CREATE_SUSPENDED (0x00000004)</code> a <code>CreateProcessW</code>.</li>
<li><strong>Desmapeo:</strong> Invoca <code>NtUnmapViewOfSection(pi.hProcess, baseImageOriginal)</code> para desalojar el ejecutable legítimo de la memoria virtual.</li>
<li><strong>Reserva y escritura:</strong> Asigna memoria con <code>VirtualAllocEx</code> en la dirección base preferida del nuevo binario (<code>ImageBase</code>) y escribe las cabeceras PE y secciones con <code>WriteProcessMemory</code>.</li>
<li><strong>Reajuste de contexto:</strong> Llama a <code>GetThreadContext(pi.hThread, &ctx)</code>, sobrescribe el registro del EntryPoint (<code>ctx.Rcx</code> en x64 o <code>ctx.Eax</code> en x86) con la nueva dirección del OEP, aplica <code>SetThreadContext</code> y despierta el proceso con <code>ResumeThread</code>.</li>
</ol>
</aside>
"""

AMPLIACION_CRIPTO_ASIMETRICA_APIS = """
<aside class="ampliacion-ext">
<p class="callout-titulo">Ampliación editorial basada en fuentes externas — Criptografía asimétrica (RSA/ECC) y tabla de intercepción en APIs nativas de Windows (CryptoAPI y CNG)</p>
<p>El software moderno rara vez implementa algoritmos criptográficos desde cero; en su lugar, utiliza esquemas híbridos apoyados en las bibliotecas criptográficas nativas de Windows (<a href="https://learn.microsoft.com/en-us/windows/win32/seccng/cng-portal" rel="noopener" target="_blank">Microsoft Learn: Cryptography Next Generation</a> y <a href="https://learn.microsoft.com/en-us/windows/win32/seccrypto/cryptography-portal" rel="noopener" target="_blank">CryptoAPI</a>):</p>

<h4 style="margin: 0.8rem 0 0.4rem 0; color: #1d4f2a;">1. Esquemas Criptográficos Híbridos en la Práctica</h4>
<p>La carga útil o los datos de configuración se cifran con un algoritmo simétrico de alta velocidad (AES-CBC, AES-GCM o ChaCha20) utilizando una clave de sesión generada al vuelo. A continuación, esa clave de sesión se cifra con una <strong>clave pública asimétrica</strong> (RSA o Curvas Elípticas ECC) embebida en el binario. Solo quien posee la clave privada correspondiente puede descifrar la clave de sesión y acceder a los datos.</p>

<h4 style="margin: 0.8rem 0 0.4rem 0; color: #1d4f2a;">2. Reconocimiento de Claves Asimétricas en Binarios</h4>
<ul>
<li><strong>RSA:</strong> Se detecta por la presencia del exponente público estándar <code>e = 65537</code> (<code>0x00010001</code>, codificado en little-endian como <code>01 00 01 00</code> en memoria) y módulos grandes <code>N</code> de 256 bytes (2048 bits) o 512 bytes (4096 bits) en <code>.rdata</code>.</li>
<li><strong>Estructura <code>RSAPUBKEY</code> (CryptoAPI clásica):</strong>
<pre><code>struct RSAPUBKEY {
    DWORD magic;  // 0x31415352 = ASCII "RSA1" (clave pública) / 0x32415352 = "RSA2" (privada)
    DWORD bitlen; // Tamaño en bits (ej. 0x00000800 = 2048 bits)
    DWORD pubexp; // Exponente público (ej. 0x00010001 = 65537)
};</code></pre></li>
<li><strong>Curvas Elípticas (ECC / ECDSA / ECDH):</strong> Se identifican por constantes de curvas estándares como <code>secp256r1</code> (NIST P-256) o <code>Curve25519</code> (constante de campo primo <code>2^255 - 19</code>).</li>
</ul>

<h4 style="margin: 0.8rem 0 0.4rem 0; color: #1d4f2a;">3. Tabla de APIs Criptográficas Nativas y Puntos de Intercepción en Depuración</h4>
<div class="tabla"><table>
<thead><tr><th>Operación</th><th>CryptoAPI Clásica (advapi32.dll)</th><th>CNG Moderna (bcrypt.dll)</th><th>Estrategia de Intercepción en Depurador</th></tr></thead>
<tbody>
<tr><td><strong>Inicialización</strong></td><td><code>CryptAcquireContextW</code></td><td><code>BCryptOpenAlgorithmProvider</code></td><td>Identifica el algoritmo pasando cadenas como <code>BCRYPT_AES_ALGORITHM</code> o <code>BCRYPT_RSA_ALGORITHM</code>.</td></tr>
<tr><td><strong>Importación de Clave</strong></td><td><code>CryptImportKey</code></td><td><code>BCryptImportKeyPair</code> / <code>BCryptGenerateSymmetricKey</code></td><td>Poner breakpoint para volcar el buffer de la clave en memoria (estructura <code>BLOBHEADER</code> o clave simétrica cruda).</td></tr>
<tr><td><strong>Cifrado de Datos</strong></td><td><code>CryptEncrypt</code></td><td><code>BCryptEncrypt</code></td><td><strong>Punto crítico de intercepción:</strong> Poner breakpoint en la entrada. El argumento <code>pbData</code> (CryptoAPI) o <code>pbInput</code> (<code>RDX</code> en x64 para CNG) contiene el <strong>texto plano antes de ser cifrado</strong>.</td></tr>
<tr><td><strong>Descifrado de Datos</strong></td><td><code>CryptDecrypt</code></td><td><code>BCryptDecrypt</code></td><td>Poner breakpoint en el <strong>retorno de la función</strong>. El buffer de salida contendrá el texto descifrado en memoria.</td></tr>
</tbody>
</table></div>
</aside>
"""

AMPLIACION_API_HOOKING_SYSCALLS = """
<aside class="ampliacion-ext">
<p class="callout-titulo">Ampliación editorial basada en fuentes externas — Evasión en User-Mode: API Hooking de EDRs, Syscalls Directas (Hell's Gate / Halo's Gate) y DLL Unhooking</p>
<p>El análisis de binarios modernos en entornos corporativos exige comprender cómo interactúa el software con los agentes de seguridad (antivirus/EDR) en el espacio de usuario (<a href="https://learn.microsoft.com/en-us/windows-hardware/drivers/debugger/x64-architecture" rel="noopener" target="_blank">Microsoft Learn: x64 Architecture & System Calls</a>):</p>

<h4 style="margin: 0.8rem 0 0.4rem 0; color: #1d4f2a;">1. Mecanismo de los Inline API Hooks</h4>
<p>Los sistemas de seguridad inyectan una DLL en cada proceso para supervisar llamadas sensibles. Para interceptar la ejecución, modifican los primeros bytes de las funciones de <code>ntdll.dll</code> reemplazando el prólogo original por un salto incondicional (<em>inline hook</em>):</p>
<pre><code>; --- ntdll.dll original (Limpia) ---
mov r10, rcx
mov eax, 0x18         ; SSN (System Service Number de NtAllocateVirtualMemory)
test byte ptr [0x7ffe0308], 1
jne short ...
syscall
ret

; --- ntdll.dll hookeada por un EDR ---
jmp qword ptr [rip + 0x10240]   ; Salto (0xE9 o 0xFF 0x25) al motor de análisis del EDR</code></pre>

<h4 style="margin: 0.8rem 0 0.4rem 0; color: #1d4f2a;">2. Técnicas de Evasión Reversibles</h4>
<ul>
<li><strong>Syscalls Directas (Direct Syscalls):</strong> El programa no invoca a <code>ntdll.dll</code>; en su lugar, define un stub propio en ensamblador con la instrucción <code>syscall</code> y el número SSN correspondiente.</li>
<li><strong>Algoritmos Hell's Gate y Halo's Gate:</strong> Como los números SSN cambian entre versiones y compilaciones de Windows:
  <ul>
  <li><em>Hell's Gate (2020):</em> Parsea la tabla de exportaciones de <code>ntdll.dll</code> en memoria, localiza la función deseada y lee los bytes <code>4C 8B D1 B8 [SSN]</code>. Si la función tiene un <code>jmp</code> (está hookeada), falla.</li>
  <li><em>Halo's Gate:</em> Supera la limitación inspeccionando las funciones vecinas inmediatamente adyacentes (offsets &plusmn;32 bytes). Si la función vecina no está hookeada, lee su SSN y le suma o resta el desplazamiento para deducir el SSN de la función bloqueada.</li>
  </ul>
</li>
<li><strong>DLL Unhooking:</strong> El binario abre <code>C:\\Windows\\System32\\ntdll.dll</code> directamente desde disco con <code>CreateFileW</code> + <code>MapViewOfFile</code>, localiza la sección <code>.text</code> limpia, cambia los permisos de la copia en memoria con <code>VirtualProtect(PAGE_EXECUTE_READWRITE)</code> y sobrescribe los hooks con <code>memcpy</code>, restaurando el prólogo original de todas las APIs.</li>
</ul>

<h4 style="margin: 0.8rem 0 0.4rem 0; color: #1d4f2a;">3. Criterio de Detección Defensiva</h4>
<p>La presencia de instrucciones <code>syscall</code> fuera del rango de memoria virtual asignado a <code>ntdll.dll</code> o <code>win32u.dll</code> constituye una anomalía heurística de máxima prioridad que delata intentos deliberados de evasión de telemetría.</p>
</aside>
"""

AMPLIACION_X64DBG_STRINGS = """
<aside class="ampliacion-ext">
<p class="callout-titulo">Ampliación editorial basada en fuentes externas — Flujo operativo de trinchera en x64dbg y extracción masiva de cadenas cifradas</p>
<p>El uso ágil del depurador dinámico y la desofuscación rápida de cadenas constituyen dos habilidades prácticas decisivas (<a href="https://help.x64dbg.com/" rel="noopener" target="_blank">x64dbg Documentation</a>):</p>

<h4 style="margin: 0.8rem 0 0.4rem 0; color: #1d4f2a;">1. Hoja de Ruta Táctica de Operaciones en x64dbg</h4>
<ul>
<li><strong>Atajos de Navegación Esenciales:</strong> <code>F2</code> (Poner/quitar breakpoint de software), <code>F7</code> (Paso a paso dentro de la función), <code>F8</code> (Paso a paso sobre la función), <code>Ctrl+F9</code> (Ejecutar hasta el <code>ret</code> de la función actual), <code>F9</code> (Reanudar ejecución continua) y <code>Ctrl+G</code> (Saltar a una dirección o expresión).</li>
<li><strong>Follow in Dump:</strong> Clic derecho sobre cualquier registro en el panel de CPU o sobre una dirección en el Stack -> <em>Follow in Dump</em>: proyecta inmediatamente el contenido de la memoria apuntada en la vista hexadecimal.</li>
<li><strong>Búsqueda de Referencias Intermodulares:</strong> Clic derecho en el desensamblado -> <em>Search for -> Current Module -> Intermodular calls</em>: lista todas las llamadas a APIs importadas por el binario. Permite seleccionar múltiples funciones (ej. <code>RegOpenKeyEx</code>, <code>CreateFileW</code>, <code>InternetOpenA</code>) y presionar <code>F2</code> para establecer breakpoints simultáneos en todas ellas.</li>
<li><strong>Memory Map (<code>Alt+M</code>):</strong> Visualiza todas las páginas de memoria del proceso. Presionar <code>Ctrl+B</code> permite buscar cadenas o secuencias de bytes en toda la memoria dinámica. Facilita la detección de bloques con protección <code>PAGE_EXECUTE_READWRITE</code> (<code>ERW</code>), indicio clásico de payloads inyectados o shellcode.</li>
<li><strong>Reconstrucción con Scylla:</strong> Menú <em>Plugins -> Scylla</em> integrado en x64dbg: automatiza la detección del OEP (<em>IAT Autosearch</em>), lectura de importaciones (<em>Get Imports</em>), volcado a disco (<em>Dump</em>) y corrección de la tabla de importaciones (<em>Fix Dump</em>).</li>
</ul>

<h4 style="margin: 0.8rem 0 0.4rem 0; color: #1d4f2a;">2. Los 3 Métodos Estándar para Extraer Cadenas Cifradas en Masa</h4>
<ol>
<li><strong>Método 1 — Breakpoint Condicional con Log en el Retorno del Decodificador (x64dbg):</strong>
Cuando un binario tiene decenas de llamadas a una rutina decodificadora XOR o RC4, no se debe revertir una por una a mano. Se localiza la instrucción <code>ret</code> de la función decodificadora y se configura un breakpoint:
<pre><code>Log text:        "Cadena descifrada: {utf8@rax}"   ; (o {utf16@rax} según corresponda)
Break condition: 0                                 ; Condición 0: no pausa la ejecución</code></pre>
Al presionar <code>F9</code>, el programa se ejecuta a velocidad normal y la pestaña <em>Log</em> de x64dbg vuelca automáticamente todas las cadenas descifradas secuencialmente.</li>
<li><strong>Método 2 — Scripting Estático en IDAPython / Ghidra:</strong>
Si la clave está embebida y el algoritmo es determinista, se escribe un script que localice las referencias cruzadas (XREFs) al buffer cifrado y aplique la operación directamente en la base de datos de IDA:
<pre><code>import ida_bytes
def decode_xor(ea, length, key):
    raw = ida_bytes.get_bytes(ea, length)
    return bytes([b ^ key for b in raw]).decode('latin1', errors='ignore')</code></pre></li>
<li><strong>Método 3 — Micro-emulación con Unicorn Engine:</strong>
Permite aislar únicamente los 30 o 40 bytes de la rutina decodificadora, inicializar los registros de la CPU virtual con los punteros y longitudes deseadas, y ejecutar el bloque emulado sin interactuar con dependencias del sistema operativo ni requerir un entorno Windows activo.</li>
</ol>
</aside>
"""
