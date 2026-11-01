import shutil
import os

src_dir = r"C:\Users\agust\.gemini\antigravity\scratch\CLS_Guia"
brain_dir = r"C:\Users\agust\.gemini\antigravity\brain\5f78e7db-99bc-4011-8024-f93ab7c13c8f"
d_dir = r"D:\Guia\CLS_Guia_Gemini"

pdf_files = [
    "CLS_Curso_Reversing.pdf",
    "CLS_Tomo_1_Tronco_y_Apoyo.pdf",
    "CLS_Tomo_2_Kernel_e_Internals.pdf",
    "CLS_Separata_Escritorio.pdf",
    "CLS_Tomo_1_Parte_A_pags_1-171.pdf",
    "CLS_Tomo_1_Parte_B_pags_172-328.pdf",
    "CLS_Tomo_1_Parte_A_pags_1-170.pdf",
    "CLS_Tomo_1_Parte_A_pags_1-172.pdf",
    "CLS_Tomo_1_Parte_B_pags_171-328.pdf",
    "CLS_Tomo_1_Parte_B_pags_171-330.pdf",
    "CLS_Tomo_1_Parte_B_pags_173-328.pdf",
]

for pdf in pdf_files:
    src_path = os.path.join(src_dir, pdf)
    if os.path.exists(src_path):
        # Mirror to D:
        dst_d = os.path.join(d_dir, pdf)
        shutil.copy2(src_path, dst_d)
        print(f"Copied {pdf} to D: ({os.path.getsize(dst_d):,} bytes)")
        
        # Mirror to brain
        dst_b = os.path.join(brain_dir, pdf)
        shutil.copy2(src_path, dst_b)
        print(f"Copied {pdf} to brain ({os.path.getsize(dst_b):,} bytes)")

# Also copy CLS_Curso_Reversing.pdf as CLS_Curso_Reversing_v5.4_Ampliada.pdf
full_pdf = os.path.join(src_dir, "CLS_Curso_Reversing.pdf")
if os.path.exists(full_pdf):
    shutil.copy2(full_pdf, os.path.join(d_dir, "CLS_Curso_Reversing_v5.4_Ampliada.pdf"))
    shutil.copy2(full_pdf, os.path.join(brain_dir, "CLS_Curso_Reversing_v5.4_Ampliada.pdf"))
    print("Updated CLS_Curso_Reversing_v5.4_Ampliada.pdf in D: and brain")

print("All PDF mirrors successfully updated!")
