#!/usr/bin/env python3
# ==============================================================================
# reconstruct_slices.py · Recuperación de Slices y Blobs en Binarios Rust
# Obra: Reversing en Windows — Tomo III (Módulo 1)
#
# Funcionalidad dual:
#   1. Standalone (CLI): analiza el binario PE con pefile y capstone.
#   2. En PyGhidra: puede ejecutarse como script de análisis desatendido.
#
# Objetivo:
#   Identificar pares (puntero, longitud) en instrucciones de desensamblado
#   para recuperar cadenas &str de Rust que no tienen terminador nulo 0x00.
# ==============================================================================

import sys
import os

def is_printable_ascii(byte_seq):
    if not byte_seq:
        return False
    return all(32 <= b <= 126 or b in (9, 10, 13) for b in byte_seq)

def analyze_standalone(pe_path):
    try:
        import pefile
    except ImportError:
        print("[-] Se requiere la biblioteca 'pefile'. Instale con: pip install pefile")
        return

    print(f"[*] Analizando binario PE: {pe_path}")
    pe = pefile.PE(pe_path)

    # Localizar sección .rdata
    rdata_section = None
    for section in pe.sections:
        name = section.Name.decode('utf-8', errors='ignore').strip('\x00')
        if name == '.rdata':
            rdata_section = section
            break

    if not rdata_section:
        print("[-] No se encontró la sección .rdata en el binario.")
        return

    rdata_va = pe.OPTIONAL_HEADER.ImageBase + rdata_section.VirtualAddress
    rdata_size = rdata_section.Misc_VirtualSize
    rdata_data = rdata_section.get_data()

    print(f"[+] Sección .rdata localizada: VA=0x{rdata_va:016X}, Tamaño={rdata_size} bytes")

    # Escaneo heurístico de blobs de texto continuos
    print("\n[*] Extrayendo literales de cadena detectados en .rdata:")
    print("=" * 80)
    print(f"{'Offset VA':<20} | {'Longitud':<10} | {'Contenido del Slice'}")
    print("-" * 80)

    # Heurística: fragmentación de secuencias contiguas de caracteres imprimibles
    i = 0
    found_count = 0
    while i < len(rdata_data):
        if 32 <= rdata_data[i] <= 126:
            start = i
            while i < len(rdata_data) and (32 <= rdata_data[i] <= 126):
                i += 1
            length = i - start
            if length >= 4: # Filtrar fragmentos triviales menores a 4 caracteres
                text = rdata_data[start:i].decode('ascii', errors='ignore')
                slice_va = rdata_va + start
                print(f"0x{slice_va:016X}   | {length:<10} | \"{text}\"")
                found_count += 1
        else:
            i += 1

    print("=" * 80)
    print(f"[+] Total de cadenas de Rust reconstruidas: {found_count}\n")

# Integración con PyGhidra (si se ejecuta dentro del entorno Ghidra)
def run_in_ghidra():
    try:
        # Variables provistas por el entorno de Ghidra Scripting
        currentProgram = globals().get('currentProgram')
        if not currentProgram:
            return False

        listing = currentProgram.getListing()
        memory = currentProgram.getMemory()
        print("[*] Ejecutando reconstruct_slices.py en entorno Ghidra...")
        
        # Iterar sobre las instrucciones buscando patrones LEA + MOV reg, len
        instructions = listing.getInstructions(True)
        slices_found = 0
        for instr in instructions:
            mnemonic = instr.getMnemonicString()
            if mnemonic == "LEA":
                op_objs = instr.getOpObjects(1)
                for obj in op_objs:
                    # Si apunta a memoria en sección de solo lectura
                    if hasattr(obj, 'getOffset'):
                        target_addr = obj
                        next_instr = instr.getNext()
                        if next_instr and next_instr.getMnemonicString() == "MOV":
                            scalar = next_instr.getScalar(1)
                            if scalar and 1 <= scalar.getValue() <= 512:
                                length = int(scalar.getValue())
                                # Crear string con longitud explícita en Ghidra
                                try:
                                    buf = bytearray(length)
                                    memory.getBytes(target_addr, buf)
                                    if is_printable_ascii(buf):
                                        text = buf.decode('ascii', errors='ignore')
                                        setPlateComment(instr.getAddress(), f"[Rust Slice &str] \"{text}\" (len={length})")
                                        slices_found += 1
                                except Exception:
                                    pass
        print(f"[+] Finalizado análisis en Ghidra: {slices_found} slices anotados.")
        return True
    except Exception:
        return False

if __name__ == '__main__':
    # Intentar ejecutar en Ghidra primero; si no, correr en modo standalone
    if not run_in_ghidra():
        if len(sys.argv) < 2:
            print("Uso standalone: python reconstruct_slices.py <ruta_al_binario.exe>")
            sys.exit(1)
        analyze_standalone(sys.argv[1])
