# -*- coding: utf-8 -*-
"""Genera un buscador offline del curso: CLS_Guia/buscar.html con el índice EMBEBIDO.

Recorre los .html de CLS_Guia, saca título + texto visible (recortado) de cada uno y
arma una página con un cuadro de búsqueda en JavaScript. El índice va embebido en la
propia página (no usa fetch) para que funcione abriendo por file:// sin bloqueos.

Correr DESPUÉS de build.py y de los generadores de páginas.
"""
import html as _html
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build

GUIA = build.GUIA
# Carpetas/páginas que no vale la pena indexar.
SALTAR_DIR = {"_trabajo", "img"}
SALTAR_PREFIJO = ("_backup_",)
SALTAR_ARCH = {"buscar.html"}
MAX_TXT = 900  # caracteres de texto por página


def limpiar(h):
    h = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", h)
    titulo = ""
    m = re.search(r"(?is)<title>(.*?)</title>", h)
    if m:
        titulo = _html.unescape(re.sub(r"\s+", " ", m.group(1))).strip()
    cuerpo = h
    mm = re.search(r'(?is)<main[^>]*>(.*?)</main>', h)
    if mm:
        cuerpo = mm.group(1)
    texto = _html.unescape(re.sub(r"(?s)<[^>]+>", " ", cuerpo))
    texto = re.sub(r"\s+", " ", texto).strip()
    return titulo, texto


def recolectar():
    docs = []
    for root, dirs, files in os.walk(GUIA):
        dirs[:] = [d for d in dirs if d not in SALTAR_DIR and not d.startswith(SALTAR_PREFIJO)]
        for f in sorted(files):
            if not f.endswith(".html") or f in SALTAR_ARCH:
                continue
            full = os.path.join(root, f)
            rel = os.path.relpath(full, GUIA).replace("\\", "/")
            try:
                titulo, texto = limpiar(open(full, encoding="utf-8").read())
            except OSError:
                continue
            if not titulo:
                titulo = rel
            docs.append({"u": rel, "t": titulo, "x": texto[:MAX_TXT]})
    return docs


def main():
    docs = recolectar()
    datos = json.dumps(docs, ensure_ascii=False)
    cuerpo = """
<p class="migas"><a href="00_EMPEZAR_AQUI.html">← Inicio</a> · <a href="materiales.html">Materiales</a></p>
<h1>Buscar en el curso</h1>
<p>Escribí una o varias palabras. Busca en el título y el texto de todas las páginas del curso (offline).</p>
<input id="q" type="search" placeholder="por ejemplo: canary, IAT, little endian, breakpoint..."
       autocomplete="off" style="width:100%;max-width:38rem;padding:.6rem .7rem;font-size:1rem;border:1px solid var(--borde,#bbb);border-radius:6px;margin:.4rem 0 1rem">
<p id="estado" class="meta-tute"></p>
<div id="res"></div>
<script id="idx" type="application/json">__DATOS__</script>
<script>
(function(){
  var DOCS = JSON.parse(document.getElementById('idx').textContent);
  var q = document.getElementById('q'), res = document.getElementById('res'), est = document.getElementById('estado');
  function norm(s){ return s.toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g,''); }
  var IDX = DOCS.map(function(d){ return {d:d, t:norm(d.t), x:norm(d.x)}; });
  function escape(s){ var e=document.createElement('div'); e.textContent=s; return e.innerHTML; }
  function buscar(){
    var terms = norm(q.value).split(/\\s+/).filter(Boolean);
    res.innerHTML='';
    if(!terms.length){ est.textContent=''; return; }
    var hits = IDX.map(function(it){
      var sc=0, ok=true;
      terms.forEach(function(t){
        var inT=it.t.indexOf(t)>=0, inX=it.x.indexOf(t)>=0;
        if(inT) sc+=5; if(inX) sc+=1;
        if(!inT && !inX) ok=false;
      });
      return ok ? {d:it.d, sc:sc} : null;
    }).filter(Boolean).sort(function(a,b){return b.sc-a.sc;});
    est.textContent = hits.length + ' página(s)';
    hits.slice(0,40).forEach(function(h){
      var d=h.d;
      var i=norm(d.x).indexOf(terms[0]);
      var frag = i>=0 ? d.x.substring(Math.max(0,i-60), i+120) : d.x.substring(0,160);
      var div=document.createElement('p');
      var a=document.createElement('a'); a.setAttribute('href', d.u); a.innerHTML='<strong>'+escape(d.t)+'</strong>';
      div.appendChild(a);
      div.insertAdjacentHTML('beforeend', '<br><span style="color:var(--tenue,#666);font-size:.9rem">…'+escape(frag)+'…</span>');
      res.appendChild(div);
    });
  }
  q.addEventListener('input', buscar);
  var p=new URLSearchParams(location.search).get('q'); if(p){ q.value=p; buscar(); }
  q.focus();
})();
</script>
""".replace("__DATOS__", datos)
    build.construir(os.path.join(GUIA, "buscar.html"), "Buscar en el curso (CLS)",
                    "Buscador offline del curso CLS: título y texto de todas las páginas.", cuerpo)
    print(f"buscar.html -> {len(docs)} páginas indexadas ({len(datos)//1024} KB de índice)")


if __name__ == "__main__":
    main()
