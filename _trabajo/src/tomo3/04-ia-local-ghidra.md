# Módulo 4 · Reversing Aumentado por IA Local: Ollama, PyGhidra y el Principio de Falsabilidad
*(Presupuesto editorial: 26 páginas — Prerrequisito: Tomo I, Lección 2.31, págs. 240–242 y Lección 2.9, págs. 115–120)*

---

## 4.1 El Principio de Soberanía y Confidencialidad en Ingeniería Inversa

La incorporación de modelos de lenguaje extensos (LLMs) al flujo de trabajo del analista de sistemas operativos y malware representa el mayor salto en productividad desde la introducción de los descompiladores basados en desofuscación intermedia (P-Code en Ghidra o microcódigo en Hex-Rays).

Sin embargo, en el ejercicio profesional de la ingeniería inversa defensiva rige una regla infranqueable: **el principio de soberanía y confidencialidad estricta**.

```
                   RIESGOS DE EXFILTRACIÓN EN REVERSING POR NUBE
                   
  [ Binario Bajo Análisis / 0-Day / Malware Propietario ]
              │
              ├── (API en la Nube: ChatGPT / Claude / Gemini) ──> [ Servidor Externo de Terceros ]
              │                                                             │
              │                                                             ├── Violación de NDA
              │                                                             ├── Fuga de 0-Day a Telemetría
              │                                                             └── Ruptura de Cadena de Custodia
              │
              └── (Inferencia 100% Local: Ollama en localhost) ─> [ GPU Local (VRAM Aislada) ]
                                                                            │
                                                                            └── Confidencialidad Absoluta (Offline)
```

### Por Qué Está Prohibido Enviar Pseudocódigo a Nubes Comerciales
1. **Acuerdos de Confidencialidad (NDA) y Respuesta a Incidentes:** Durante una investigación forense corporativa, el código descompilado extraído de memoria puede contener claves criptográficas propietarias, tokens de sesión o secretos industriales. Transmitir estos volcados a servidores de terceros viola las cláusulas contractuales de secreto profesional y las regulaciones de protección de datos (GDPR, HIPAA, leyes locales).
2. **Filtración de Vulnerabilidades de Día Cero (0-Days):** Si el reverser está analizando un binario en busca de una falla crítica aún no parcheada, enviar el fragmento vulnerable a un proveedor de IA expone la investigación a los sistemas de telemetría, indexación y moderación del proveedor antes de que el parche oficial esté disponible.
3. **Pérdida de la Cadena de Custodia en Informes Periciales:** En litigios judiciales o peritajes forenses, un tribunal puede impugnar un peritaje si no se puede demostrar que la evidencia binaria permaneció confinada dentro de un entorno informático controlado y estanco.

Por estos motivos, la metodología moderna de la obra exige que **toda asistencia por inteligencia artificial se ejecute exclusivamente sobre infraestructura local, offline y autocontenida**.

---

## 4.2 Infraestructura de Inferencia 100 % Local (Offline)

Para operar de forma soberana en una estación de trabajo de ingeniería inversa de gama media o alta, se utiliza un motor de inferencia local gobernado por API REST:

### A. Motores de Inferencia Recomendados
* **Ollama (`http://localhost:11434`):** La opción más sencilla y robusta. Empaqueta el runtime de `llama.cpp` y expone un servidor HTTP nativo en segundo plano que responde en milisegundos a solicitudes JSON.
* **`llama.cpp` nativo (`llama-server.exe`):** Máximo control de parámetros de microarquitectura (instrucciones AVX2, AVX-512, cuotas de capas descargadas a GPU con `--n-gpu-layers`).
* **LM Studio:** Entorno con interfaz gráfica que incluye servidor local con compatibilidad de API OpenAI (`http://localhost:1234/v1`).

### B. Selección de Modelos Cuantizados para Reversing
Para tareas de comprensión de código ensamblador y descompilación en C, los modelos de propósito general conversacional (tipo chat estándar) suelen alucinar o producir respuestas prolixas. Se deben utilizar modelos **especializados en programación (*coder models*)** en formatos cuantizados GGUF (4 bits u 8 bits):

| Modelo Local | Parámetros | Formato / Cuantización | VRAM Requerida | Perfil de Rendimiento |
|---|---|---|---|---|
| **`qwen2.5-coder:14b`** | 14 Mil Millones | `q4_K_M` (4 bits) | ~9.5 GB VRAM | **Recomendado:** Excelente comprensión de C/P-Code en GPUs de 12 GB (RTX 3060/4060). |
| **`qwen2.5-coder:7b`** | 7 Mil Millones | `q8_0` (8 bits) | ~8.0 GB VRAM | Rápido (latencia < 2s). Adecuado para renombrado masivo de funciones simples. |
| **`deepseek-r1-distill-qwen-14b`** | 14 Mil Millones | `q4_K_M` | ~10 GB VRAM | Modelo de razonamiento (*reasoning*). Ideal para desglosar algoritmos criptográficos opacos. |
| **`llama-3.3-70b`** | 70 Mil Millones | `q4_K_M` | ~42 GB VRAM | Máxima precisión. Requiere configuraciones multi-GPU o Macs con Apple Silicon M2/M3 Max. |

### C. Parámetros Críticos de Inferencia Determinista
En ingeniería inversa se busca **consistencia y determinismo**, no creatividad literaria. Al interrogar al modelo local:
* **Temperatura (`temperature = 0.0` o `0.1`):** Minimiza la dispersión aleatoria de tokens y fuerza al modelo a elegir siempre la hipótesis semántica más probable.
* **`top_p = 0.9`:** Descarta la cola de tokens improbables.
* **Semilla (`seed = 42`):** Permite reproducir exactamente el mismo análisis en corridas sucesivas.

---

## 4.3 Desarrollo del Puente PyGhidra ↔ Modelo Local (Plantilla 21)

El corazón práctico de este módulo es el script [`plantillas_codigo/plantilla_21_ghidra_ollama.py`](file:///C:/Users/agust/.gemini/antigravity/scratch/CLS_Guia/plantillas_codigo/plantilla_21_ghidra_ollama.py), el cual automatiza el enriquecimiento del proyecto de Ghidra:

```
                   PIPELINE DEL PUENTE PYGHIDRA ↔ OLLAMA LOCAL
                   
   [ Proyecto en Ghidra ]
             │
   1. Iterar funciones con prefijo 'FUN_*'
   2. Descompilar a C mediante DecompInterface
             │
             ▼
   [ Prompt Estructurado con Pseudocódigo C ] ──> HTTP POST (localhost:11434) ──> [ Ollama: Qwen 2.5 Coder ]
                                                                                           │
                                                                                  Respuesta JSON
                                                                                           │
   [ Parser Robusto con Fallback Regex ] <─────────────────────────────────────────────────┘
             │
   3. Validar sintaxis de nombres (sin espacios, caracteres C válidos)
   4. Aplicar cambios en la Base de Datos de Ghidra:
        ├── function.setName("ai_rc4_crypt_stream")
        ├── function.setComment("Implementación de stream cipher RC4...")
        └── createBookmark("Heuristica_IA")
```

### El Prompt Estructurado y el Formato JSON Forzado
Para evitar que el modelo responda con preámbulos conversacionales (*«Sure, here is what this function does...»*), el *System Prompt* define un contrato estricto:

```text
Eres un analista senior de ingeniería inversa en Windows. 
Analiza el siguiente pseudocódigo en C descompilado por Ghidra.
Debes responder ÚNICAMENTE con un objeto JSON válido, sin preámbulos ni explicaciones en Markdown.
Formato requerido:
{
  "suggested_name": "identificador_en_snake_case",
  "purpose": "resumen_del_proposito_en_una_sola_linea",
  "is_crypto_or_hash": true_o_false,
  "confidence": 0_a_100
}
```

### Tolerancia a Fallos y Fallback por Expresión Regular
Incluso con instrucciones estrictas, los modelos locales cuantizados a veces envuelven la salida en bloques de código tipo ````json { ... } ````. 

El script de la Plantilla 21 implementa una rutina de tolerancia en dos pasos:
```python
# Intento 1: Decodificación JSON directa
try:
    data = json.loads(response_text)
except json.JSONDecodeError:
    # Intento 2: Fallback por expresión regular aislando el primer bloque entre llaves
    match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
    if not match:
        match = re.search(r'\{.*\}', response_text, re.DOTALL)
    if match:
        data = json.loads(match.group(0))
    else:
        # Descartar sin alterar el proyecto de Ghidra
        print("[!] No se pudo parsear JSON. Función descartada.")
        return
```

---

## 4.4 El Principio de Falsabilidad: La IA Propone, el Binario Confirma

El error más peligroso que puede cometer un reverser novato es **aceptar ciegamente las sugerencias de un modelo de lenguaje**.

### Tres Casos Reales de Alucinación en Reversing de Windows

#### Caso 1: Confundir un PRNG Lineal con Criptografía Simétrica (RC4/AES)
* **Lo que ve el LLM:** Un bucle con operaciones `^`, `<<`, `>>` y una constante hexadecimal grande (`0x5BD1E995` o `0x9E3779B9`).
* **Sugerencia Alucinada:** `rc4_encrypt_block` o `aes_round_key`.
* **Falsación Empírica:** El reverser inspecciona las referencias cruzadas. La función no recibe claves de sesión, no interactúa con buffers de red ni almacena estados S-Box de 256 bytes. Es simplemente un generador pseudoaleatorio lineal (LCG) o un hash Murmur para una tabla de dispersión interna.

#### Caso 2: Confundir un Checksum de Integridad (Adler32/CRC32) con una Función Hash Criptográfica (MD5/SHA)
* **Lo que ve el LLM:** Dos acumuladores de 16 bits combinados en una palabra de 32 bits con divisiones modulares `65521`.
* **Sugerencia Alucinada:** `md5_transform_block`.
* **Falsación Empírica:** La presencia de la constante `65521` (el mayor número primo menor que $2^{16}$) es la firma matemática indiscutible del algoritmo **Adler-32** (usado en zlib/DEFLATE). No tiene relación con MD5 ni con hashing criptográfico.

#### Caso 3: Alucinar Actividad de Comando y Control (C2) en un Parser de Registro Local
* **Lo que ve el LLM:** Un bucle que concatena cadenas y formatea buffers de texto con parámetros hexadecimales.
* **Sugerencia Alucinada:** `beacon_c2_telemetry`.
* **Falsación Empírica:** Al auditar la tabla de importaciones (IAT) y las Xrefs, la función no invoca `HttpSendRequestW`, `WinHttpSendRequest` ni `WSASend`. Solo invoca a `RegQueryValueExW` y `RegSetValueExW`. La función es simplemente una rutina de guardado de configuración local.

---

### Protocolo Obligatorio de Falsación y Marcado Visual en Ghidra

Para resguardar la verdad forense, el puente automatizado aplica tres medidas de seguridad metodológica:
1. **Prefijo `ai_` y Preservación del Nombre Original:**  
   Nunca sobreescribe destructivamente el símbolo. Si la función se llamaba `FUN_140001850` y el LLM sugiere `decrypt_payload`, el script la renombra como `ai_decrypt_payload` y agrega en el comentario de cabecera:
   ```text
   [Heurística IA - Falsable]
   Original: FUN_140001850
   Confianza declarada: 85%
   Propósito sugerido: Desencriptación de flujo XOR
   Nota: Verificar llamadas salientes antes de validar como hecho forense.
   ```
2. **Marcador de Auditoría (Bookmark):**  
   Crea un bookmark en la categoría `Heuristica_IA` en la dirección de inicio de la función, permitiendo al analista revisar en una sola lista filtrable todas las funciones sugeridas por la IA y confirmarlas o descartarlas con un solo clic.

---

## 4.5 Resumen de las 5 Plantillas del Tomo III

Con el desarrollo de los Módulos 1 a 4, el catálogo de plantillas de la obra queda formalmente extendido:

```
===================================================================================================
Plantilla  | Archivo / Directorio                      | Módulo | Propósito y Técnica
---------------------------------------------------------------------------------------------------
17a        | plantilla_17a_clang_cfi.cpp               | Mód. 1 | Demostración de Clang CFI puro (trap ud2)
17b        | plantilla_17b_msvc_cfg.c (.exe verificado)| Mód. 1 | Microsoft kCFG (/guard:cf, GuardFlags 0x10017500)
18         | plantilla_18_rust_lto/                    | Mód. 1 | Rust stripped (panic=abort, reconstruct_slices.py)
19         | plantilla_19_auditar_lpac.ps1             | Mód. 2 | Auditoría PowerShell de SIDs S-1-15-3-* y LPAC
20         | plantilla_20_cet_shadow_stack.c (.exe)    | Mód. 3 | Intel CET Shadow Stack (_rdsspq, /CETCOMPAT)
21         | plantilla_21_ghidra_ollama.py             | Mód. 4 | Puente PyGhidra ↔ Ollama local con fallback regex
===================================================================================================
```
