import os, shutil, pypdf

base_dir = r"C:\Users\agust\.gemini\antigravity\scratch\CLS_Guia"
artifact_dir = r"C:\Users\agust\.gemini\antigravity\brain\5f78e7db-99bc-4011-8024-f93ab7c13c8f"
mirror_dir = r"D:\Guia\CLS_Guia_Gemini"
pendrive_dir = r"E:\\"

src_t1 = os.path.join(base_dir, "Tomo_1_Tronco_y_Apoyo.pdf")
cover_pdf = os.path.join(base_dir, "_trabajo", "print", "cover_tomo1.pdf")

r_master = pypdf.PdfReader(src_t1)
r_cover = pypdf.PdfReader(cover_pdf)
total_pages = len(r_master.pages)

# 1. Save master with new cover
t1_new_master = os.path.join(base_dir, "_trabajo", "print", "Tomo_1_master_updated.pdf")
w_master = pypdf.PdfWriter()
w_master.append(r_cover, pages=(0, 1))
w_master.append(r_master, pages=(1, total_pages))
with open(t1_new_master, "wb") as f:
    w_master.write(f)

shutil.copy2(t1_new_master, src_t1)
print(f"Updated Tomo_1_Tronco_y_Apoyo.pdf: {os.path.getsize(src_t1):,} bytes")

r_updated = pypdf.PdfReader(src_t1)

# 2. Recommended split at page 178:
# Parte A (1-178) = 178 pages (89 sheets, completes Lesson 2.17)
w_a_178 = pypdf.PdfWriter()
w_a_178.append(r_updated, pages=(0, 178))
file_a_178 = os.path.join(base_dir, "Tomo_1_Parte_A_pags_1-178.pdf")
with open(file_a_178, "wb") as f:
    w_a_178.write(f)

# Parte B (179-410) = 232 pages (116 sheets, opens with Parte B cover)
w_b_179 = pypdf.PdfWriter()
w_b_179.append(r_updated, pages=(178, total_pages))
file_b_179 = os.path.join(base_dir, f"Tomo_1_Parte_B_pags_179-{total_pages}.pdf")
with open(file_b_179, "wb") as f:
    w_b_179.write(f)

print(f"Generated {os.path.basename(file_a_178)}: {len(w_a_178.pages)} págs ({os.path.getsize(file_a_178):,} bytes)")
print(f"Generated {os.path.basename(file_b_179)}: {len(w_b_179.pages)} págs ({os.path.getsize(file_b_179):,} bytes)")

# 3. Legacy compatibility split at page 172:
w_a_172 = pypdf.PdfWriter()
w_a_172.append(r_updated, pages=(0, 172))
file_a_172 = os.path.join(base_dir, "Tomo_1_Parte_A_pags_1-172.pdf")
with open(file_a_172, "wb") as f:
    w_a_172.write(f)

w_b_173 = pypdf.PdfWriter()
w_b_173.append(r_updated, pages=(172, total_pages))
file_b_173 = os.path.join(base_dir, "Tomo_1_Parte_B_pags_173-410.pdf")
with open(file_b_173, "wb") as f:
    w_b_173.write(f)

print(f"Updated legacy {os.path.basename(file_a_172)}: {len(w_a_172.pages)} págs")
print(f"Updated legacy {os.path.basename(file_b_173)}: {len(w_b_173.pages)} págs")

# 4. Tomo_2_Kernel_e_Internals_2.pdf
t2_src = os.path.join(base_dir, "Tomo_2_Kernel_e_Internals.pdf")
t2_copy = os.path.join(base_dir, "Tomo_2_Kernel_e_Internals_2.pdf")
shutil.copy2(t2_src, t2_copy)
print(f"Created {os.path.basename(t2_copy)}: {os.path.getsize(t2_copy):,} bytes")

# 5. Distribute all to Artifacts, D:\ and E:\
dests = [artifact_dir, mirror_dir]
if os.path.exists(pendrive_dir):
    dests.append(pendrive_dir)

files_to_distribute = [
    "Tomo_1_Tronco_y_Apoyo.pdf",
    "Tomo_1_Parte_A_pags_1-178.pdf",
    "Tomo_1_Parte_B_pags_179-410.pdf",
    "Tomo_1_Parte_A_pags_1-172.pdf",
    "Tomo_1_Parte_B_pags_173-410.pdf",
    "Tomo_2_Kernel_e_Internals.pdf",
    "Tomo_2_Kernel_e_Internals_2.pdf",
    "Tomo_3_LLVM_Rust_Contenedores_IA.pdf"
]

for d in dests:
    if os.path.exists(d):
        for fname in files_to_distribute:
            src_f = os.path.join(base_dir, fname)
            dst_f = os.path.join(d, fname)
            if os.path.exists(src_f):
                shutil.copy2(src_f, dst_f)
        print(f"Synchronized all volumes to {d}")

print("\n--- FINAL DISTRIBUTION STATUS ---")
for fname in files_to_distribute:
    p = os.path.join(base_dir, fname)
    r = pypdf.PdfReader(p)
    sz = os.path.getsize(p)
    print(f"  {fname:<38} | {len(r.pages):>3} págs | {(len(r.pages)+1)//2:>3} hojas | {sz:>9,} bytes | Par: {len(r.pages)%2==0}")
