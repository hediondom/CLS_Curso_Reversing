import os
import subprocess
import shutil
import pypdf

base_dir = r"C:\Users\agust\.gemini\antigravity\scratch\CLS_Guia"
html_path = os.path.join(base_dir, "orden_impresion.html")
pdf_path = os.path.join(base_dir, "orden_impresion.pdf")
png_path = os.path.join(base_dir, "orden_impresion.png")
chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

html_content = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Especificación de Impresión y Encuadernación — Reversing en Windows</title>
<style>
  @page {
    size: A4 landscape;
    margin: 1.0cm 1.2cm;
  }
  * {
    box-sizing: border-box;
  }
  body {
    font-family: Arial, "Segoe UI", Helvetica, sans-serif;
    color: #000;
    background-color: #ffffff;
    margin: 0;
    padding: 20px 25px;
  }
  .header-box {
    margin-bottom: 14px;
    border-bottom: 2px solid #000;
    padding-bottom: 8px;
  }
  .header-box h1 {
    margin: 0 0 4px 0;
    font-size: 22px;
    font-weight: 800;
    letter-spacing: 0.5px;
    text-transform: uppercase;
  }
  .header-box p {
    margin: 0;
    font-size: 13px;
    color: #333;
  }
  table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 14px;
  }
  th, td {
    border: 1.2px solid #111;
    padding: 10px 12px;
    text-align: left;
    vertical-align: middle;
    font-size: 13.5px;
    line-height: 1.25;
  }
  th {
    font-weight: bold;
    background-color: #f0f0f0;
    color: #000;
    font-size: 14px;
  }
  .col-vol { width: 20%; font-weight: bold; font-size: 14px; }
  .col-arch { width: 32%; font-family: "Consolas", "Courier New", monospace; font-size: 13px; word-break: break-all; }
  .col-pags { width: 11%; text-align: left; font-size: 13.5px; }
  .col-hojas { width: 13%; text-align: left; font-weight: bold; font-size: 14px; }
  .col-enc { width: 24%; font-size: 13px; }

  tr.total-row {
    background-color: #f9f9f9;
    border-top: 2.5px solid #000;
  }
  tr.total-row td {
    font-weight: bold;
    font-size: 14px;
    padding: 10px 12px;
  }

  .nota-maestro {
    border: 1.5px dashed #444;
    background-color: #fcfcfc;
    padding: 8px 12px;
    margin-bottom: 12px;
    font-size: 12.5px;
    line-height: 1.35;
  }
  .nota-maestro strong {
    color: #000;
  }
  .nota-maestro .nombre-maestro {
    font-family: "Consolas", monospace;
    font-weight: bold;
    font-size: 13px;
    background-color: #eaeaea;
    padding: 1px 5px;
  }

  .footer-specs {
    font-size: 13px;
    line-height: 1.4;
    color: #111;
  }
  .destacado-papel {
    font-size: 26px;
    font-weight: 900;
    letter-spacing: 1.2px;
    color: #000;
    text-align: right;
    margin-top: 8px;
  }
</style>
</head>
<body>

<div class="header-box">
  <h1>Orden de Impresión y Encuadernación — Obra Reversing en Windows</h1>
  <p>Especificación técnica para taller/imprenta · Suite completa de 5 volúmenes físicos independientes</p>
</div>

<table>
  <thead>
    <tr>
      <th class="col-vol">Volumen</th>
      <th class="col-arch">Archivo PDF</th>
      <th class="col-pags">Páginas</th>
      <th class="col-hojas">Hojas (doble faz)</th>
      <th class="col-enc">Encuadernación</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td class="col-vol">1. Tomo I — Parte A</td>
      <td class="col-arch">Tomo_1_Parte_A_pags_1-178.pdf</td>
      <td class="col-pags">178 págs.</td>
      <td class="col-hojas">89 hojas</td>
      <td class="col-enc">Anillado metálico Ring Wire / espiral o binder con tapa dura/polipropileno</td>
    </tr>
    <tr>
      <td class="col-vol">2. Tomo I — Parte B</td>
      <td class="col-arch">Tomo_1_Parte_B_pags_179-410.pdf</td>
      <td class="col-pags">232 págs.</td>
      <td class="col-hojas">116 hojas</td>
      <td class="col-enc">Anillado metálico Ring Wire / espiral o binder con tapa dura/polipropileno</td>
    </tr>
    <tr>
      <td class="col-vol">3. Tomo II</td>
      <td class="col-arch">Tomo_2_Kernel_e_Internals.pdf</td>
      <td class="col-pags">198 págs.</td>
      <td class="col-hojas">99 hojas</td>
      <td class="col-enc">Anillado metálico Ring Wire / espiral o binder con tapa dura/polipropileno</td>
    </tr>
    <tr>
      <td class="col-vol">4. Tomo III</td>
      <td class="col-arch">Tomo_3_LLVM_Rust_Contenedores_IA.pdf</td>
      <td class="col-pags">52 págs.</td>
      <td class="col-hojas">26 hojas</td>
      <td class="col-enc">Anillado metálico Ring Wire / espiral o binder con tapa dura/polipropileno</td>
    </tr>
    <tr>
      <td class="col-vol">5. Separata de Escritorio</td>
      <td class="col-arch">Separata_Escritorio.pdf</td>
      <td class="col-pags">18 págs.</td>
      <td class="col-hojas">9 hojas</td>
      <td class="col-enc">Anillado metálico Ring Wire / espiral o binder con tapa dura/polipropileno</td>
    </tr>
    <tr class="total-row">
      <td class="col-vol">TOTAL FÍSICO A IMPRIMIR</td>
      <td class="col-arch">5 volúmenes encuadernados</td>
      <td class="col-pags">678 págs.</td>
      <td class="col-hojas">339 hojas</td>
      <td class="col-enc">100 % Paridad Par (sin hojas impares ni blancas sueltas)</td>
    </tr>
  </tbody>
</table>

<div class="nota-maestro">
  <strong>* Archivo maestro digital de consulta (Trilogía Completa Unificada):</strong> <span class="nombre-maestro">CLS_Curso_Reversing.pdf</span> (660 págs. · 330 hojas).<br>
  Contiene los Tomos I, II y III consolidados en un solo archivo con marcadores de navegación completa. <strong>NO se manda a imprimir físicamente</strong> (para lectura digital en pantalla o archivo). Los archivos para impresión son exclusivamente los 5 listados arriba.
</div>

<div class="footer-specs">
  <strong>Parámetros de impresión:</strong> Formato A4 (210 &times; 297 mm), escala al 100 % (tamaño real, sin reducir ni ajustar márgenes al imprimible) a <strong>doble faz sobre el borde largo</strong> (giro lateral / duplex long-edge). Tapa transparente de polipropileno al frente y contratapa opaca atrás para cada volumen.
</div>

<div class="destacado-papel">
  PAPEL OBRA DE 80 GR
</div>

</body>
</html>
"""

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Escribió: {html_path}")

# Render to PDF
cmd_pdf = [
    chrome_path,
    "--headless=new",
    "--disable-gpu",
    "--no-pdf-header-footer",
    f"--print-to-pdf={pdf_path}",
    html_path
]
subprocess.run(cmd_pdf, check=True)

# Render to PNG
cmd_png = [
    chrome_path,
    "--headless=new",
    "--disable-gpu",
    "--window-size=1200,800",
    "--default-background-color=ffffffff",
    f"--screenshot={png_path}",
    html_path
]
subprocess.run(cmd_png, check=True)

# Check page count
r = pypdf.PdfReader(pdf_path)
print(f"Renderizado orden_impresion.pdf: {len(r.pages)} página(s), {os.path.getsize(pdf_path):,} bytes")
print(f"Renderizado orden_impresion.png: {os.path.getsize(png_path):,} bytes")
assert len(r.pages) == 1, "Debe ser exactamente 1 página landscape"
