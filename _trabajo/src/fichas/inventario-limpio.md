---
title: "Inventario limpio de CLS"
description: "Ficha del recurso: CSV de 8.154 filas, hashes SHA-256, resumen JSON y listado de comprimidos"
---

# Inventario limpio de CLS

| Campo | Dato |
|---|---|
| **Autor / organización** | Proyecto CLS (sesión previa) |
| **Tipo** | CSV de 8.154 filas, hashes SHA-256, resumen JSON y listado de comprimidos |
| **Ruta local** | `CLS_resultados_intermedios/inventario_limpio` |
| **Etapa** | 0 y transversal |
| **Nivel** | No aplica |
| **Prerrequisitos** | Ninguno |
| **Duración** | No aplica |
| **Estado** | Revisado: LEEME, resumen y muestreo del CSV |

## Qué se revisó

LEEME.md, _resumen.json, estructura del CSV y consultas por tipo/fuente/estado. No se recorrieron las 8.154 filas una por una.

## Contenido explicado

Una fila por archivo en disco, con estado (`util`, `cuarentena`, `excluido`, `duplicado`, `descartado`), tipo, fuente, tamaño, fecha, autor, ID de mensaje, hash y ruta.

## Utilidad para el curso

Mapa maestro para localizar material y entender la clasificación. Es la fuente de conteos de esta guía.

## Limitaciones y antigüedad

`util` no implica seguridad, calidad ni vigencia. Es el inventario vigente (26/10/2026), distinto del histórico de `CLS_resultados` (6.499 filas, 24/10/2026).

## Referencias verificables

- {{src:CLS_resultados_intermedios/inventario_limpio/LEEME.md|LEEME del inventario}}
- {{src:CLS_resultados_intermedios/inventario_limpio/CLS_inventario_limpio.csv|Inventario}}
- {{src:CLS_resultados_intermedios/inventario_limpio/_comprimidos.csv|Listado de comprimidos}}

:::nota Volver
[Índice de fichas](index.html) · [Mapa del curso](../guia/index.html) · [Inicio](../00_EMPEZAR_AQUI.html)
:::
