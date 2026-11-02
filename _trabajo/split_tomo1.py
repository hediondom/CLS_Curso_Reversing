import pypdf
import os
import shutil

src_pdf = r"C:\Users\agust\.gemini\antigravity\scratch\CLS_Guia\CLS_Tomo_1_Tronco_y_Apoyo.pdf"
reader = pypdf.PdfReader(src_pdf)
total_pages = len(reader.pages)
print(f"Total páginas en el Tomo 1 original: {total_pages}")

# En Tomo 1 (330 páginas):
# - Págs. 1 a 172: Apertura, Etapa 0, 1, 2A, 2B y 2C (hasta Lección 2.17 Packers didácticos, que cierra en pág. 172).
# - Pág. 173: Portadilla completa de la Parte B.
# - Págs. 174 a 330: Lección 2.18 C++ profundo hasta el Apoyo Transversal y Colofón (pág. 330).

# 1. PARTE A: Páginas 1 a 172 (índices 0 a 171) -> 172 páginas (86 hojas a doble faz)
# Cierra limpiamente al final de la Lección 2.17 Packers didácticos (pág. 172). Cero solapamiento.
writer_a = pypdf.PdfWriter()
for i in range(0, 172):
    writer_a.add_page(reader.pages[i])

# 2. PARTE B: Páginas 173 a 330 (índices 172 a 329) -> 158 páginas (79 hojas a doble faz)
# Arranca limpiamente con la Portadilla de la Parte B (pág. 173) y continúa con Lección 2.18 (pág. 174).
writer_b = pypdf.PdfWriter()
for i in range(172, total_pages):
    writer_b.add_page(reader.pages[i])

destinos = [
    r"C:\Users\agust\.gemini\antigravity\scratch\CLS_Guia",
    r"C:\Users\agust\.gemini\antigravity\brain\5f78e7db-99bc-4011-8024-f93ab7c13c8f",
    r"D:\Guia\CLS_Guia_Gemini"
]

# Nombres canónicos limpios de la revisión actual
nombre_a_clean = "Tomo_1_Parte_A_pags_1-172.pdf"
nombre_b_clean = f"Tomo_1_Parte_B_pags_173-{total_pages}.pdf"
nombre_a_std = "CLS_Tomo_1_Parte_A_pags_1-172.pdf"
nombre_b_std = f"CLS_Tomo_1_Parte_B_pags_173-{total_pages}.pdf"

# Nombres compatibles para enlaces y referencias previas
nombres_a = [
    nombre_a_clean,
    nombre_a_std,
    "CLS_Tomo_1_Parte_A_pags_1-171.pdf",
    "CLS_Tomo_1_Parte_A_pags_1-170.pdf"
]

nombres_b = [
    nombre_b_clean,
    nombre_b_std,
    "CLS_Tomo_1_Parte_B_pags_172-328.pdf",
    "CLS_Tomo_1_Parte_B_pags_171-328.pdf",
    "CLS_Tomo_1_Parte_B_pags_171-330.pdf"
]

# Escribir en destino principal
for n in nombres_a:
    p = os.path.join(destinos[0], n)
    with open(p, "wb") as f:
        writer_a.write(f)
print(f"Generado {nombre_a_std} (y variantes) con {len(writer_a.pages)} páginas ({os.path.getsize(os.path.join(destinos[0], nombre_a_std)):,} bytes).")

for n in nombres_b:
    p = os.path.join(destinos[0], n)
    with open(p, "wb") as f:
        writer_b.write(f)
print(f"Generado {nombre_b_std} (y variantes) con {len(writer_b.pages)} páginas ({os.path.getsize(os.path.join(destinos[0], nombre_b_std)):,} bytes).")

# Replicar a brain y a D:\Guia\CLS_Guia_Gemini
all_names = nombres_a + nombres_b
for d in destinos[1:]:
    if os.path.exists(d):
        for name in all_names:
            src = os.path.join(destinos[0], name)
            dst = os.path.join(d, name)
            shutil.copy2(src, dst)
        print(f"Copiados tomos divididos a: {d}")

print("Generación y partición completada exitosamente.")
