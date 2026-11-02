#!/usr/bin/env python3
# ==============================================================================
# plantilla_21_ghidra_ollama.py · Puente PyGhidra ↔ Ollama Local (Reversing con IA)
# Obra: Reversing en Windows — Tomo III (Módulo 4: Reversing Aumentado por IA Local)
#
# Propósito:
#   Automatiza el análisis semántico de funciones descompiladas en Ghidra
#   conectándose a un modelo LLM local (ej. qwen2.5-coder:14b) servido vía
#   Ollama en http://localhost:11434. Implementa el principio de falsabilidad,
#   extracción JSON con tolerancia a fallos (regex fallback) y marcado visual
#   en la base de datos de Ghidra.
#
# Entornos de Ejecución:
#   1. Ghidra Script Manager / PyGhidra Headless (modo nativo con Ghidra API).
#   2. Modo de prueba y benchmark offline (ejecución directa con python3).
# ==============================================================================

import sys
import os
import json
import re
import urllib.request
import urllib.error
import time

# Configuración por defecto del servicio Ollama local
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434")
DEFAULT_MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5-coder:14b")
DEFAULT_CONFIDENCE_THRESHOLD = 60
API_TIMEOUT_SECONDS = 15

SYSTEM_PROMPT = """Eres un analista senior de ingeniería inversa en sistemas Windows.
Analiza el siguiente pseudocódigo en C descompilado por Ghidra.
Debes responder ÚNICAMENTE con un objeto JSON válido, sin preámbulos, sin saludos ni explicaciones en Markdown.
El formato exacto requerido es:
{
  "suggested_name": "identificador_en_snake_case",
  "purpose": "resumen_tecnico_del_proposito_en_una_sola_linea",
  "is_crypto_or_hash": false,
  "confidence": 85
}
"""

def extract_json_from_llm(raw_text):
    """
    Rutina de tolerancia en dos pasos:
      1. Intento directo de decodificación JSON.
      2. Si falla o contiene wrappers de markdown (```json ... ```),
         aísla mediante expresión regular el bloque delimitado por llaves.
    """
    raw_cleaned = raw_text.strip()
    
    # Intento 1: Decodificación directa
    try:
        return json.loads(raw_cleaned)
    except json.JSONDecodeError:
        pass

    # Intento 2: Búsqueda de bloque JSON con regex
    # Limpiar bloques de código Markdown si existen
    code_block = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', raw_cleaned, re.DOTALL)
    if code_block:
        try:
            return json.loads(code_block.group(1))
        except json.JSONDecodeError:
            pass

    # Fallback general: aislar desde la primera llave de apertura hasta la última de cierre
    match = re.search(r'\{.*\}', raw_cleaned, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    return None

def is_valid_c_identifier(name):
    """Valida que la sugerencia sea un identificador C válido sin espacios ni símbolos prohibidos."""
    if not name or not isinstance(name, str):
        return False
    return bool(re.match(r'^[a-zA-Z_][a-zA-Z0-9_]{2,63}$', name))

def query_ollama(decompiled_c, model=DEFAULT_MODEL, host=OLLAMA_HOST, temperature=0.0):
    """
    Envía el fragmento de pseudocódigo C a Ollama usando la API REST /api/generate.
    Fuerza parámetros deterministas (temperature=0.0).
    """
    endpoint = f"{host}/api/generate"
    payload = {
        "model": model,
        "system": SYSTEM_PROMPT,
        "prompt": f"Pseudocódigo C descompilado:\n\n{decompiled_c}\n\nResponde solo con el JSON:",
        "stream": False,
        "options": {
            "temperature": temperature,
            "top_p": 0.9,
            "seed": 42
        }
    }

    req_data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        endpoint,
        data=req_data,
        headers={"Content-Type": "application/json"}
    )

    try:
        start_time = time.time()
        with urllib.request.urlopen(req, timeout=API_TIMEOUT_SECONDS) as resp:
            elapsed = time.time() - start_time
            result = json.loads(resp.read().decode("utf-8"))
            raw_response = result.get("response", "")
            return raw_response, elapsed
    except urllib.error.URLError as e:
        return None, 0.0

# ==============================================================================
# INTEGRACIÓN GHIDRA (Se activa si el script se invoca dentro de Ghidra)
# ==============================================================================

def run_inside_ghidra():
    try:
        # Importación condicional de paquetes de Ghidra
        from ghidra.app.decompiler import DecompInterface
        from ghidra.util.task import ConsoleTaskMonitor
        from ghidra.program.model.symbol import SourceType
    except ImportError:
        return False

    print("[*] Ejecutando dentro del entorno Ghidra...")
    decompiler = DecompInterface()
    decompiler.openProgram(currentProgram) # Inyectado por Ghidra
    monitor = ConsoleTaskMonitor()

    fm = currentProgram.getFunctionManager()
    functions = list(fm.getFunctions(True))
    total_funcs = len(functions)
    print(f"[*] Total de funciones detectadas en el programa: {total_funcs}")

    processed = 0
    renamed = 0

    for func in functions:
        fname = func.getName()
        # Filtrar solo funciones con nomenclatura genérica de Ghidra (FUN_*)
        if not fname.startswith("FUN_"):
            continue

        processed += 1
        entry_point = func.getEntryPoint()
        print(f"[*] Analizando {fname} en 0x{entry_point}...")

        # Descompilar a C
        decomp_results = decompiler.decompileFunction(func, 30, monitor)
        if not decomp_results.decompileCompleted():
            print(f"    [-] Falló la descompilación de {fname}")
            continue

        c_code = decomp_results.getDecompiledFunction().getC()
        if not c_code or len(c_code.strip()) < 20:
            print(f"    [-] Pseudocódigo insuficiente para análisis en {fname}")
            continue

        # Consultar Ollama
        raw_resp, elapsed = query_ollama(c_code)
        if not raw_resp:
            print(f"    [-] Sin respuesta de Ollama en {OLLAMA_HOST} ({elapsed:.2f}s)")
            continue

        parsed = extract_json_from_llm(raw_resp)
        if not parsed:
            print(f"    [!] Error parseando JSON retornado por el modelo. Respuesta cruda:\n{raw_resp[:120]}...")
            continue

        suggested = parsed.get("suggested_name", "")
        confidence = parsed.get("confidence", 0)
        purpose = parsed.get("purpose", "Sin descripción")
        is_crypto = parsed.get("is_crypto_or_hash", False)

        if not is_valid_c_identifier(suggested):
            print(f"    [-] Identificador sugerido inválido: '{suggested}'")
            continue

        if confidence < DEFAULT_CONFIDENCE_THRESHOLD:
            print(f"    [!] Confianza ({confidence}%) por debajo del umbral ({DEFAULT_CONFIDENCE_THRESHOLD}%). Ignorando.")
            continue

        # Aplicar el principio de falsabilidad:
        # Se añade prefijo 'ai_' y se registra el nombre original en un comentario
        new_name = f"ai_{suggested}"
        plate_comment = (
            f"[Heurística IA - Falsable]\n"
            f"Original: {fname}\n"
            f"Confianza: {confidence}%\n"
            f"Cripto/Hash: {is_crypto}\n"
            f"Propósito inferido: {purpose}\n"
            f"Nota: Verificar llamadas salientes (Xrefs) antes de validar."
        )

        func.setName(new_name, SourceType.USER_DEFINED)
        func.setComment(plate_comment)

        # Crear marcador visual (Bookmark)
        bookmark_mgr = currentProgram.getBookmarkManager()
        bookmark_mgr.setBookmark(entry_point, "Analysis", "Heuristica_IA", f"{new_name} ({confidence}%)")

        print(f"    [+] Renombrada con éxito: {fname} -> {new_name} [{confidence}% en {elapsed:.2f}s]")
        renamed += 1

    print(f"\n[+] Proceso finalizado: {processed} funciones evaluadas, {renamed} renombradas.")
    decompiler.dispose()
    return True

# ==============================================================================
# MODO STANDALONE / BENCHMARK OFFLINE
# ==============================================================================

MOCK_TEST_FUNCTIONS = [
    {
        "id": "FUN_140001000",
        "code": """
int FUN_140001000(unsigned char *buf, int len, unsigned char key) {
    for (int i = 0; i < len; i++) {
        buf[i] ^= key;
    }
    return len;
}
""",
        "expected_hint": "xor"
    },
    {
        "id": "FUN_140002150",
        "code": """
unsigned int FUN_140002150(const char *str) {
    unsigned int hash = 5381;
    int c;
    while ((c = *str++)) {
        hash = ((hash << 5) + hash) + c;
    }
    return hash;
}
""",
        "expected_hint": "hash"
    },
    {
        "id": "FUN_140003400",
        "code": """
int FUN_140003400(int a, int b) {
    return a + b;
}
""",
        "expected_hint": "add"
    }
]

def run_benchmark_offline():
    print("=" * 80)
    print("PLANTILLA 21 · BENCHMARK Y VERIFICACIÓN OFFLINE DE PARSEO JSON")
    print("=" * 80)
    print(f"Endpoint configurado: {OLLAMA_HOST}")
    print(f"Modelo objetivo:      {DEFAULT_MODEL}")
    print(f"Umbral de confianza:  {DEFAULT_CONFIDENCE_THRESHOLD}%")
    print("-" * 80)

    # 1. Probar robustez del parser contra casos patológicos de salida LLM
    print("[1] Verificando tolerancia a fallos del parser JSON con expresiones regulares:")
    test_cases = [
        ('{"suggested_name": "clean_json", "purpose": "ok", "confidence": 95}', True, "clean_json"),
        ('```json\n{"suggested_name": "markdown_wrap", "purpose": "ok", "confidence": 90}\n```', True, "markdown_wrap"),
        ('Sure! Here is your output:\n{"suggested_name": "preamble_test", "purpose": "ok", "confidence": 85}\nHope this helps!', True, "preamble_test"),
        ('No valid json at all', False, None),
    ]

    parser_passed = 0
    for idx, (raw, should_succeed, expected_name) in enumerate(test_cases, 1):
        parsed = extract_json_from_llm(raw)
        if should_succeed:
            if parsed and parsed.get("suggested_name") == expected_name:
                print(f"    [PASS] Caso {idx}: Extracción correcta ({expected_name})")
                parser_passed += 1
            else:
                print(f"    [FAIL] Caso {idx}: No se pudo parsear ({raw})")
        else:
            if parsed is None:
                print(f"    [PASS] Caso {idx}: Descarte correcto de contenido espurio")
                parser_passed += 1
            else:
                print(f"    [FAIL] Caso {idx}: Falso positivo en descarte")

    print(f"[+] Pruebas del parser: {parser_passed}/{len(test_cases)} aprobadas.")

    # 2. Verificar conectividad con Ollama
    print("\n[2] Comprobando disponibilidad del servicio Ollama local:")
    try:
        req = urllib.request.Request(f"{OLLAMA_HOST}/api/tags")
        with urllib.request.urlopen(req, timeout=3) as resp:
            models_data = json.loads(resp.read().decode("utf-8"))
            installed_models = [m.get("name") for m in models_data.get("models", [])]
            print(f"[+] Ollama ONLINE en {OLLAMA_HOST}")
            print(f"    Modelos instalados: {', '.join(installed_models) if installed_models else 'Ninguno'}")

            # Ejecutar inferencia real sobre una función sintética si el modelo está disponible
            target_model = None
            for im in installed_models:
                if DEFAULT_MODEL in im or "coder" in im or "qwen" in im:
                    target_model = im
                    break
            if not target_model and installed_models:
                target_model = installed_models[0]

            if target_model:
                print(f"\n[3] Ejecutando prueba de inferencia real con modelo '{target_model}':")
                test_func = MOCK_TEST_FUNCTIONS[0]
                raw_out, elapsed = query_ollama(test_func["code"], model=target_model)
                print(f"    Tiempo de respuesta: {elapsed:.2f} s")
                print(f"    Salida cruda del modelo:\n    {raw_out.strip()}")
                parsed = extract_json_from_llm(raw_out)
                if parsed:
                    print(f"    [+] JSON parseado con éxito: {parsed}")
                    valido = is_valid_c_identifier(parsed.get("suggested_name", ""))
                    print(f"    [+] Identificador C válido: {valido} ({parsed.get('suggested_name')})")
                else:
                    print("    [-] Falló la extracción JSON.")
            else:
                print("\n[3] No se encontró un modelo coder compatible en Ollama para prueba en vivo.")

    except Exception as e:
        print(f"[-] Ollama no disponible en {OLLAMA_HOST} ({e}).")
        print("    (Para producción: inicie 'ollama serve' y descargue 'qwen2.5-coder:14b').")

    print("\n" + "=" * 80)
    print("FIN DEL BENCHMARK")
    print("=" * 80)

if __name__ == "__main__":
    # Si 'currentProgram' existe en el contexto global, estamos dentro de Ghidra
    if "currentProgram" in globals():
        run_inside_ghidra()
    else:
        run_benchmark_offline()
