# -*- coding: utf-8 -*-
"""Ampliaciones editoriales de nivel avanzado para la Revisión 5.4:
1. Evolución de evasión en user-mode: Indirect Syscalls, Call Stack Unwinding y Call Stack Spoofing (02-anti-analisis.html)
2. La trampa del endianness en CNG vs. CryptoAPI, blobs de curvas elípticas y script de conversión Python (04-cripto.html)
3. Patrón de doble breakpoint encadenado en x64dbg para funciones void in-place y plugins tácticos (02-debugger.html)
4. Optimización de nicho (Niche Optimization) en Rust para tipos Option<&T> sin byte tag (02-huella-compilador.html)
"""

AMPLIACION_INDIRECT_SYSCALLS = """
<aside class="ampliacion-ext">
<p class="callout-titulo">Ampliación editorial basada en fuentes externas — De Direct Syscalls a Indirect Syscalls y Call Stack Spoofing</p>
<p>Aunque las <em>Direct Syscalls</em> (Hell's Gate / Halo's Gate) permiten evitar los hooks de <code>ntdll.dll</code>, los agentes de seguridad modernos (EDRs) y el propio kernel de Windows implementan contramedidas que detectan esta técnica (<a href="https://learn.microsoft.com/en-us/windows-hardware/drivers/debugger/x64-architecture" rel="noopener" target="_blank">Microsoft Learn: x64 Architecture &amp; System Calls</a> y telemetría ETWti):</p>

<h4 style="margin: 0.8rem 0 0.4rem 0; color: #1d4f2a;">1. La Limitación de las Syscalls Directas (Inspección de RIP)</h4>
<p>Cuando la CPU ejecuta la instrucción <code>syscall</code> en Ring 3, el procesador transfiere el control al manejador del kernel (<code>KiSystemCall64</code>). Durante esta transición, el kernel captura el registro <code>RIP</code> de origen en la estructura del hilo (<em>trap frame</em>). Mediante telemetría de kernel (como <strong>ETWti</strong> —<em>Microsoft-Windows-Threat-Intelligence</em>— o <em>ProcessInstrumentationCallback</em>):</p>
<ul>
<li>Si el <code>RIP</code> ejecutor reside en la sección <code>.text</code> de <code>ntdll.dll</code> o <code>win32u.dll</code>, la llamada se considera conforme al diseño del sistema.</li>
<li>Si el <code>RIP</code> apunta a la sección <code>.text</code> del propio ejecutable anfitrión o a memoria privada (<code>MEM_PRIVATE</code>), se genera una alerta inmediata por ejecución de llamadas al sistema anómalas.</li>
</ul>

<h4 style="margin: 0.8rem 0 0.4rem 0; color: #1d4f2a;">2. La Solución: Indirect Syscalls</h4>
<p>Para satisfacer la validación del <code>RIP</code> sin pasar por los hooks del EDR, el cargador prepara los registros de la llamada en su propio código, pero en lugar de emitir el opcode <code>0F 05</code> (<code>syscall</code>), realiza un salto (<code>jmp</code>) a una instrucción <code>syscall ; ret</code> legítima ya existente dentro de <code>ntdll.dll</code>:</p>
<pre><code>; --- Stub en el binario (Indirect Syscall) ---
mov r10, rcx
mov eax, 0x18                      ; SSN deducido dinámicamente con Halo's Gate
jmp qword ptr [rip + pfn_syscall]  ; Salta a la instrucción "syscall; ret" dentro de ntdll</code></pre>
<p>Al ejecutarse el <code>syscall</code> físicamente dentro del espacio de memoria de <code>ntdll.dll</code>, el <code>RIP</code> registrado en el kernel resulta 100 % legítimo.</p>

<h4 style="margin: 0.8rem 0 0.4rem 0; color: #1d4f2a;">3. El Problema del Call Stack Walking y Call Stack Spoofing</h4>
<p>Aun con <em>Indirect Syscalls</em>, los EDRs avanzados inspeccionan la pila de llamadas retrospectiva (<em>Call Stack Unwinding</em> guiado por las tablas <code>.pdata</code> / <code>UNWIND_INFO</code> vistas en la lección 2.14). Si el frame inmediatamente anterior a <code>ntdll!NtAllocateVirtualMemory</code> no es una API de alto nivel (como <code>kernelbase.dll!VirtualAllocEx</code>), sino memoria no respaldada o un salto anómalo, la llamada es detectada. Para evadir esto, los cargadores avanzados implementan <strong>Call Stack Spoofing</strong> (sintetizando marcos de pila falsos para simular que la llamada se originó en una secuencia legítima de Windows).</p>
<p><em>Nota sobre Tartarus' Gate:</em> Algunos EDRs modernos colocan su hook <code>jmp</code> no en el byte <code>+0</code>, sino después de <code>mov r10, rcx</code> (en el byte <code>+3</code>). La variante <em>Tartarus' Gate</em> verifica si el hook está desplazado y ajusta el puntero de lectura para no confundir el prólogo.</p>
</aside>
"""

AMPLIACION_ENDIANNESS_CNG_CRYPTO = """
<aside class="ampliacion-ext">
<p class="callout-titulo">Ampliación editorial basada en fuentes externas — La trampa del Endianness en CNG vs. CryptoAPI y script de conversión en Python</p>
<p>Una de las discrepancias arquitectónicas más frecuentes al extraer claves criptográficas de memoria radica en la convención de orden de bytes (<a href="https://learn.microsoft.com/en-us/windows/win32/seccng/cng-key-storage-functions" rel="noopener" target="_blank">Microsoft Learn: CNG Key Storage</a>):</p>

<div class="tabla"><table>
<thead><tr><th>Característica</th><th>CryptoAPI Clásica (advapi32.dll)</th><th>CNG Moderna (bcrypt.dll / ncrypt.dll)</th></tr></thead>
<tbody>
<tr><td><strong>Estructura del encabezado</strong></td><td><code>PUBLICKEYSTRUC</code> (<code>BLOBHEADER</code>) + <code>RSAPUBKEY</code></td><td><code>BCRYPT_RSAKEY_BLOB</code> / <code>BCRYPT_ECCKEY_BLOB</code></td></tr>
<tr><td><strong>Magic Bytes de clave pública RSA</strong></td><td><code>0x31415352</code> (ASCII <code>"RSA1"</code>)</td><td><code>0x31415352</code> (<code>BCRYPT_RSAPUBLIC_MAGIC</code> = <code>"RSA1"</code>)</td></tr>
<tr><td><strong>Magic Bytes de clave privada RSA</strong></td><td><code>0x32415352</code> (ASCII <code>"RSA2"</code>)</td><td><code>0x32415352</code> (<code>BCRYPT_RSAPRIVATE_MAGIC</code> = <code>"RSA2"</code>)</td></tr>
<tr><td><strong>Magic Bytes de Curvas Elípticas (P-256)</strong></td><td>No soportado de forma estándar</td><td><code>0x314B4345</code> (<code>"ECK1"</code> para ECDH) / <code>0x31534345</code> (<code>"ECS1"</code> para ECDSA)</td></tr>
<tr><td><strong>Orden de Bytes (Endianness) del Módulo y Claves</strong></td><td><strong>Little-Endian</strong> (el byte menos significativo va primero)</td><td><strong>Big-Endian</strong> (formato estándar de red / RFC)</td></tr>
</tbody>
</table></div>

<h4 style="margin: 0.8rem 0 0.4rem 0; color: #1d4f2a;">Reconocimiento Visual de Claves ASN.1 DER (X.509)</h4>
<p>Cuando un binario no utiliza APIs nativas de Windows y compila su propia librería (como mbedTLS u OpenSSL), las claves públicas suelen embeberse en formato ASN.1 DER binario. Se reconocen al instante por la secuencia invariable que codifica el OID de <code>rsaEncryption</code> (<code>1.2.840.113549.1.1.1</code>):</p>
<pre><code>30 82 .. .. 30 0D 06 09 2A 86 48 86 F7 0D 01 01 01 05 00 03 82 .. .. 00 30 82 ..</code></pre>

<h4 style="margin: 0.8rem 0 0.4rem 0; color: #1d4f2a;">Script de Extracción y Conversión a PEM (Python / PyCryptodome)</h4>
<p>Para convertir un volcado hexadecimal obtenido en x64dbg de una estructura <code>RSAPUBKEY</code> (CryptoAPI) a una clave pública <code>.pem</code> estándar utilizable en scripts defensivos, se debe invertir el orden de los bytes del módulo:</p>
<pre><code># Reconstrucción de clave pública RSA desde volcado de CryptoAPI (Little-Endian)
from Crypto.PublicKey import RSA

def parse_cryptoapi_rsapubkey(data: bytes) -> RSA.RsaKey:
    # data: buffer que comienza en RSAPUBKEY (después del BLOBHEADER de 8 bytes)
    magic = data[0:4]          # b'RSA1' (0x31415352)
    bitlen = int.from_bytes(data[4:8], 'little')
    pubexp = int.from_bytes(data[8:12], 'little')
    modlen = bitlen // 8
    # En CryptoAPI el módulo viene en little-endian; se invierte a big-endian:
    modulus = int.from_bytes(data[12:12+modlen][::-1], 'big')
    return RSA.construct((modulus, pubexp))

# Exportar a PEM: print(key.export_key().decode())</code></pre>
</aside>
"""

AMPLIACION_X64DBG_DOBLE_BP = """
<aside class="ampliacion-ext">
<p class="callout-titulo">Ampliación editorial basada en fuentes externas — Patrón de doble breakpoint encadenado para funciones in-place y plugins tácticos</p>
<p>En el flujo de extracción masiva de cadenas cifradas, existe un caso frecuente donde el truco estándar de leer <code>{utf8@rax}</code> en el <code>ret</code> no funciona:</p>

<h4 style="margin: 0.8rem 0 0.4rem 0; color: #1d4f2a;">1. Funciones Decodificadoras void con Buffer In-Place</h4>
<p>Cuando la función es <code>void decodificar(char* buffer, size_t len)</code>, el buffer se descifra sobre sí mismo (<em>in-place</em>) y la función no devuelve ningún puntero en <code>RAX</code>. En x64, el puntero al buffer llega en <code>RCX</code>, pero <code>RCX</code> es un registro volátil (*scratch*) que el compilador suele reutilizar como contador de bucle o índice, perdiéndose su valor antes de llegar al <code>ret</code>.</p>
<p><strong>Solución: Técnica de Doble Breakpoint Encadenado con Variable de Usuario ($ptr):</strong></p>
<ol>
<li><strong>En el prólogo de la función decodificadora (dirección inicial):</strong>
<pre><code>Break condition: 0
Command text:    $ptr = rcx    ; Guarda el puntero original antes de que el bucle lo pise</code></pre></li>
<li><strong>En la instrucción <code>ret</code> de la función:</strong>
<pre><code>Break condition: 0
Log text:        "Cadena descifrada: {utf8@$ptr}"    ; Lee el buffer ya descifrado en memoria</code></pre></li>
</ol>
<p>Al reanudar con <code>F9</code>, la consola de Log vuelca todas las cadenas limpias sin detener nunca la ejecución.</p>

<h4 style="margin: 0.8rem 0 0.4rem 0; color: #1d4f2a;">2. Ecosistema de Plugins Tácticos para x64dbg</h4>
<ul>
<li><strong>ScyllaHide:</strong> Plugin indispensable que intercepta a nivel de Ring 3 las APIs de anti-debug más comunes (<code>PEB.BeingDebugged</code>, <code>NtGlobalFlag</code>, <code>CheckRemoteDebuggerPresent</code>, <code>ProcessDebugPort</code> y temporizadores <code>RDTSC</code> / <code>GetTickCount</code>) con un solo clic.</li>
<li><strong>xAnalyzer:</strong> Analizador heurístico estático para x64dbg que reconoce automáticamente los prototipos de funciones de Windows y anota los nombres de los argumentos en el desensamblado, emulando la clásica vista contextual de OllyDbg en binarios modernos de 64 bits.</li>
<li><strong>OllyDumpEx / SwissArmyKnife:</strong> Permite realizar volcados selectivos de regiones de memoria específicas o secciones individuales directamente desde el <em>Memory Map</em> sin necesidad de reconstruir el binario completo.</li>
</ul>
</aside>
"""

AMPLIACION_RUST_NICHE = """
<aside class="ampliacion-ext">
<p class="callout-titulo">Ampliación editorial basada en fuentes externas — Optimización de nicho (Niche Optimization) en Rust para tipos Option sin byte tag</p>
<p>Al revertir binarios compilados en Rust, es fundamental conocer la <strong>optimización de nicho</strong> (<em>Niche Optimization</em> o <em>Null-Pointer Optimization</em>) implementada por el compilador (<a href="https://doc.rust-lang.org/nomicon/repr-rust.html" rel="noopener" target="_blank">The Rustonomicon: Alternative Representations</a>):</p>
<ul>
<li><strong>El principio del nicho:</strong> En tipos como <code>Option&lt;u32&gt;</code>, Rust debe reservar un byte extra como discriminante (<em>tag</em>) porque cualquier valor de 32 bits es un número válido. Sin embargo, para tipos que <strong>garantizan que nunca pueden ser nulos</strong> (como referencias <code>&amp;T</code>, punteros inteligentes <code>Box&lt;T&gt;</code>, punteros a función <code>fn()</code> o enteros no nulos <code>core::num::NonZeroU32</code>), el compilador <strong>elimina por completo el byte <code>tag</code></strong>.</li>
<li><strong>Representación en memoria:</strong>
  <ul>
  <li><code>Some(&amp;T)</code>: Se representa simplemente por la dirección de memoria válida del puntero (8 bytes en x64).</li>
  <li><code>None</code>: Se representa con el valor nulo exacto (<code>0x0000000000000000</code>).</li>
  </ul>
</li>
<li><strong>Patrón en desensamblado:</strong> Ante estos tipos, el analista <strong>no debe buscar</strong> un <code>cmp byte ptr [rsp+offset], 1</code>. En su lugar, el chequeo de <code>None</code> se compila de forma idéntica a una comprobación de puntero nulo en C:
<pre><code>test rax, rax     ; Comprueba si el Option&lt;&amp;T&gt; o Option&lt;Box&lt;T&gt;&gt; es nulo
jz es_none        ; Si es cero, equivale a la rama None
; ... continúa en la rama Some(&amp;T) usando RAX directamente como puntero</code></pre></li>
</ul>
</aside>
"""
