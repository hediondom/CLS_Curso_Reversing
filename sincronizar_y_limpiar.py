import os
import shutil
import pypdf

base_dir = r"C:\Users\agust\.gemini\antigravity\scratch\CLS_Guia"
artifact_dir = r"C:\Users\agust\.gemini\antigravity\brain\5f78e7db-99bc-4011-8024-f93ab7c13c8f"
mirror_dir = r"D:\Guia\CLS_Guia_Gemini"
pendrive_dir = r"E:\\"

print("=== DEPURACIÓN Y SINCRONIZACIÓN DEFINITIVA ===")

# 1. Archivos obsoletos o duplicados a eliminar del pendrive
obsoletos_pen = [
    os.path.join(pendrive_dir, "Tomo_1_Parte_A_pags_1-172.pdf"),
    os.path.join(pendrive_dir, "Tomo_1_Parte_B_pags_173-410.pdf"),
    os.path.join(pendrive_dir, "Tomo_2_Kernel_e_Internals_2.pdf"),
    os.path.join(pendrive_dir, "Curso_Reversing_Windows.pdf")  # Se reemplaza por CLS_Curso_Reversing.pdf
]

for obs in obsoletos_pen:
    if os.path.exists(obs):
        try:
            os.remove(obs)
            print(f"[ELIMINADO DUPLICADO/OBSOLETO] {obs}")
        except Exception as e:
            print(f"[ERROR al eliminar] {obs}: {e}")

# 2. Lista canónica única de archivos para imprenta y archivo maestro
archivos_canonicos = [
    "CLS_Curso_Reversing.pdf",               # 660 págs (Obra Completa Unificada)
    "Tomo_1_Parte_A_pags_1-178.pdf",         # 178 págs (Tomo I - Parte A)
    "Tomo_1_Parte_B_pags_179-410.pdf",       # 232 págs (Tomo I - Parte B)
    "Tomo_2_Kernel_e_Internals.pdf",         # 198 págs (Tomo II)
    "Tomo_3_LLVM_Rust_Contenedores_IA.pdf",  # 52 págs (Tomo III)
    "Separata_Escritorio.pdf",               # 18 págs (Separata de Escritorio)
    "Tomo_1_Tronco_y_Apoyo.pdf",             # 410 págs (Tomo I íntegro de referencia)
    "orden_impresion.pdf",                   # Hoja de imprenta (PDF)
    "orden_impresion.png",                   # Hoja de imprenta (PNG)
    "orden_impresion.html"                   # Hoja de imprenta (HTML)
]

destinos = [
    ("Pendrive E:\\", pendrive_dir),
    ("Espejo D:\\Guia\\CLS_Guia_Gemini", mirror_dir),
    ("Artefactos Brain", artifact_dir)
]

for desc_dest, path_dest in destinos:
    if os.path.exists(path_dest):
        print(f"\n--- Sincronizando con {desc_dest} ---")
        for fname in archivos_canonicos:
            src_f = os.path.join(base_dir, fname)
            dst_f = os.path.join(path_dest, fname)
            if os.path.exists(src_f):
                shutil.copy2(src_f, dst_f)
                sz = os.path.getsize(dst_f)
                print(f"  [OK] {fname:<38} -> {sz:>10,} bytes")
            else:
                print(f"  [ERROR ARCHIVO FUENTE NO EXISTE] {src_f}")
    else:
        print(f"\n[Aviso] Destino no disponible: {path_dest}")

# 3. También en el mirror D:\ eliminar los duplicados viejos
obsoletos_mirror = [
    os.path.join(mirror_dir, "Tomo_1_Parte_A_pags_1-172.pdf"),
    os.path.join(mirror_dir, "Tomo_1_Parte_B_pags_173-410.pdf"),
    os.path.join(mirror_dir, "Tomo_2_Kernel_e_Internals_2.pdf")
]
for obs in obsoletos_mirror:
    if os.path.exists(obs):
        try:
            os.remove(obs)
            print(f"[ELIMINADO DUPLICADO EN D:\\] {obs}")
        except Exception as e:
            pass

print("\n--- AUDITORÍA FINAL DEL CONTENIDO EN PENDRIVE E:\\ ---")
archivos_en_e = sorted(os.listdir(pendrive_dir))
for f in archivos_en_e:
    fp = os.path.join(pendrive_dir, f)
    sz = os.path.getsize(fp)
    if f.endswith(".pdf"):
        try:
            r = pypdf.PdfReader(fp)
            pgs = len(r.pages)
            hojas = (pgs + 1) // 2
            par = "PAR" if pgs % 2 == 0 else "IMPAR"
            print(f"  {f:<38} | {pgs:>3} págs | {hojas:>3} hojas | {sz:>10,} bytes | {par}")
        except Exception as e:
            print(f"  {f:<38} | ERROR LECTURA PDF: {e}")
    else:
        print(f"  {f:<38} | {'-':>3} págs | {'-':>3} hojas | {sz:>10,} bytes | -")
