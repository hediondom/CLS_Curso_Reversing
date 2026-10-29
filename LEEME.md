# CLS — Curso de reversing

Paquete de estudio autónomo, en español, construido a partir del proyecto CLS.

## Abrir

Abrí **`00_EMPEZAR_AQUI.html`** en un navegador. Funciona sin conexión. Desde ahí llegás al mapa del curso, las fichas, el glosario, las preguntas y el seguimiento.

## Contenido

- `00_EMPEZAR_AQUI.html`: portada, método de estudio, estado de cobertura y enlaces.
- `guia/`: 46 lecciones numeradas en siete etapas (0–4 recorrido base; 5–6 optativas) con ejemplos, prácticas, respuestas y puertas de salida. La rama optativa 2D añade 13 lecciones y una extensión Hyper-V fuera del núcleo.
- `ida_tutes/`: 69 tutoriales ilustrados con capturas, enlazados desde el índice de materiales; 1–28 se relacionan con lecciones del recorrido y 29–69 se conservan como referencia avanzada.
- `juntadas/` y `audios/`: materiales locales de apoyo, con fotogramas, transcripciones y un índice de audios.
- `fichas/`: 20 fichas de recursos con estado de revisión, límites y referencias.
- `glosario.html`: términos explicados en lenguaje de principiante.
- `preguntas_y_respuestas.html`: repaso por etapa con respuestas razonadas.
- `mapa_de_cobertura.csv`: tema ↔ recurso ↔ archivo/capítulo ↔ estado.
- `registro_de_cobertura.csv`: lotes revisados, pendientes y motivos.
- `seguimiento.csv`: planilla de avance.
- `FUENTES_Y_LIMITES.md`: criterios, alcance, exclusiones y limitaciones.
- `plantilla_informe.md`: base para informes reproducibles.
- En el árbol local, `_trabajo/src/` conserva las fuentes Markdown y `_trabajo/*.py` los scripts de generación. La copia portable omite los scripts y fuentes de trabajo, pero conserva los textos extraídos citados.
- El árbol de trabajo local conserva `_backup_2026-10-26/`; no forma parte de la copia portable. Los borradores de lecciones, capturas de revisión, documentos de Edición 4, la copia DeepSeek y el generador/salida del PDF completo anterior están archivados fuera de la guía vigente y también se excluyen de la portable.

La copia portable excluye respaldos, borradores, cachés del navegador y temporales. El paquete local y esta carpeta de trabajo no son una selección autorizada para publicación pública.

## Criterios

- Marco educativo, defensivo y autorizado.
- Prácticas con programas propios, software abierto o crackmes diseñados para aprender.
- No se enseña a eludir licencias, DRM, autenticación ni controles de acceso.
- No se ejecutaron binarios del corpus ni se extrajeron comprimidos.
- `util` en el inventario no significa seguro, bueno ni vigente.
- Los estados `cuarentena`, `excluido`, `descartado` y `duplicado` se respetan.

## Estado

Edición 5, 27/10/2026. La cobertura es parcial y está declarada en `registro_de_cobertura.csv`. Lo que falta está en `FUENTES_Y_LIMITES.md`.
