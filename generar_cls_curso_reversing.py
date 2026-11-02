import os
import shutil
import pypdf

base_dir = r"C:\Users\agust\.gemini\antigravity\scratch\CLS_Guia"
artifact_dir = r"C:\Users\agust\.gemini\antigravity\brain\5f78e7db-99bc-4011-8024-f93ab7c13c8f"
mirror_dir = r"D:\Guia\CLS_Guia_Gemini"
pendrive_dir = r"E:\\"

f_t1 = os.path.join(base_dir, "Tomo_1_Tronco_y_Apoyo.pdf")
f_t2 = os.path.join(base_dir, "Tomo_2_Kernel_e_Internals.pdf")
f_t3 = os.path.join(base_dir, "Tomo_3_LLVM_Rust_Contenedores_IA.pdf")

print("=== CONSTRUCCIÓN DEL ARCHIVO MAESTRO CLS_Curso_Reversing.pdf ===")
print("Leyendo volúmenes fuente...")

r1 = pypdf.PdfReader(f_t1)
r2 = pypdf.PdfReader(f_t2)
r3 = pypdf.PdfReader(f_t3)

p1, p2, p3 = len(r1.pages), len(r2.pages), len(r3.pages)
print(f"  Tomo I:   {p1:>3} páginas ({p1//2} hojas)")
print(f"  Tomo II:  {p2:>3} páginas ({p2//2} hojas)")
print(f"  Tomo III: {p3:>3} páginas ({p3//2} hojas)")
total_pages = p1 + p2 + p3
print(f"  TOTAL TRILOGÍA MAESTRA: {total_pages} páginas ({total_pages//2} hojas a doble faz)")
assert total_pages % 2 == 0, "El total de páginas debe ser par"

writer = pypdf.PdfWriter()

# Transfer all pages
for page in r1.pages:
    writer.add_page(page)
for page in r2.pages:
    writer.add_page(page)
for page in r3.pages:
    writer.add_page(page)

# Function to copy outlines recursively
def copy_outlines(reader, outline_list, page_offset, parent_item=None):
    last_item = parent_item
    for item in outline_list:
        if isinstance(item, list):
            copy_outlines(reader, item, page_offset, parent_item=last_item)
        else:
            try:
                pnum = reader.get_destination_page_number(item)
                dest_pnum = pnum + page_offset
                dest_pnum = min(dest_pnum, len(writer.pages) - 1)
                title = item.title if hasattr(item, 'title') else str(item)
                new_item = writer.add_outline_item(title, dest_pnum, parent=parent_item)
                last_item = new_item
            except Exception as e:
                print(f"  [Aviso] No se pudo transferir marcador {getattr(item, 'title', item)}: {e}")

# Build outline roots
print("Inyectando jerarquía completa de marcadores...")
t1_root = writer.add_outline_item("TOMO I · TRONCO Y APOYO (Fundamentos a Especialización)", 0)
copy_outlines(r1, r1.outline, 0, parent_item=t1_root)

t2_root = writer.add_outline_item("TOMO II · KERNEL, DRIVERS E INTERNALS (Modo Núcleo y Windows Internals)", p1)
copy_outlines(r2, r2.outline, p1, parent_item=t2_root)

t3_root = writer.add_outline_item("TOMO III · LLVM, RUST, CONTENEDORES E INTELIGENCIA ARTIFICIAL", p1 + p2)
copy_outlines(r3, r3.outline, p1 + p2, parent_item=t3_root)

# Write master output file
out_master = os.path.join(base_dir, "CLS_Curso_Reversing.pdf")
with open(out_master, "wb") as f:
    writer.write(f)

print(f"\n[OK] Generado exitosamente: {out_master}")
print(f"  Tamaño: {os.path.getsize(out_master):,} bytes")
print(f"  Páginas verificadas: {len(writer.pages)}")

# Verify reading the written master
r_check = pypdf.PdfReader(out_master)
print(f"  Verificación de lectura: {len(r_check.pages)} páginas, {len(r_check.outline)} secciones raíz.")
