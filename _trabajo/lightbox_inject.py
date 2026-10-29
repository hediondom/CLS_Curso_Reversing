# -*- coding: utf-8 -*-
"""Inyecta un visor de imágenes (lightbox: click para ampliar) en todos los .html de CLS_Guia.

Es idempotente: si la página ya lo tiene (marca 'lightbox-ov'), la saltea. Así se agrega
el zoom a las páginas-tutorial y juntadas (con cientos de capturas) SIN regenerarlas ni
reprocesar imágenes. El CSS .lightbox-ov vive en guia/estilo.css.

Correr al final del pipeline (después de build y de los generadores de páginas).
"""
import os

GUIA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SALTAR_DIR = {"_trabajo"}
SALTAR_PREFIJO = ("_backup_",)
MARCA = "lightbox-ov"

SCRIPT = """<script>
(function(){
  function abrir(src){
    var o=document.createElement('div'); o.className='lightbox-ov';
    var i=document.createElement('img'); i.src=src; o.appendChild(i);
    function cerrar(){o.remove(); document.removeEventListener('keydown', onkey);}
    function onkey(e){ if(e.key==='Escape') cerrar(); }
    o.addEventListener('click', cerrar);
    document.addEventListener('keydown', onkey);
    document.body.appendChild(o);
  }
  document.addEventListener('DOMContentLoaded', function(){
    document.querySelectorAll('figure img, main img').forEach(function(img){
      img.style.cursor='zoom-in';
      img.addEventListener('click', function(){ abrir(img.currentSrc||img.src); });
    });
  });
})();
</script>
"""


def main():
    n = 0
    saltadas = 0
    for root, dirs, files in os.walk(GUIA):
        dirs[:] = [d for d in dirs if d not in SALTAR_DIR and not d.startswith(SALTAR_PREFIJO)]
        for f in files:
            if not f.endswith(".html"):
                continue
            full = os.path.join(root, f)
            h = open(full, encoding="utf-8").read()
            if MARCA in h or "</body>" not in h:
                saltadas += 1
                continue
            h = h.replace("</body>", SCRIPT + "</body>", 1)
            open(full, "w", encoding="utf-8").write(h)
            n += 1
    print(f"lightbox inyectado en {n} páginas ({saltadas} ya lo tenían o sin </body>)")


if __name__ == "__main__":
    main()
