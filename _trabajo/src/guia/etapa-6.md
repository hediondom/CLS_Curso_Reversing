---
title: "Etapa 6 · Rama optativa · Kernel y drivers"
description: "Comprender, construir y revisar un driver KMDF didáctico con una interfaz inocua, depurarlo solo en VM descartable y explicar mitigaciones actuales."
etapa: "Etapa 6 · Rama optativa · Kernel y drivers"
---

# Etapa 6 · Rama optativa · Kernel y drivers

:::{nota} Objetivo medible
Comprender, construir y revisar un driver KMDF didáctico con una interfaz inocua, depurarlo solo en VM descartable y explicar mitigaciones actuales.
:::

**Prerrequisitos:** Etapa 0 (laboratorio aislado), C, assembly, memoria y sincronización, WinDbg y 2D.1 (objetos/tokens), 2D.2 (memoria/loader) y 2D.11 (excepciones/debugging). Etapa 2C es recomendada, no requisito; no hace falta completar toda 2D.  
**Duración estimada:** 45–65 horas como estimación inicial; puede requerir más tiempo si C, WinDbg o WDK son nuevos.. Es una estimación de esta guía, derivada de la suma de las lecciones; no es una duración declarada por CLS.


:::{aviso} Rama optativa; fuera de la aprobación obligatoria
La Etapa 6 profundiza en kernel/drivers y no cambia los requisitos de las Etapas 0–4. Sus prácticas de carga requieren una VM descartable; nunca modifiques las protecciones del equipo principal.
:::

## Lecciones

| # | Lección | Qué aprendés |
|---|---|---|
| 6.1 | [Arquitectura del kernel y modelo de E/S](6-01-arquitectura-kernel.html) | user/kernel mode, IRQL, pool, IRP, I/O Manager, sincronización y bugchecks. |
| 6.2 | [KMDF: driver propio con IOCTL inocuo](6-02-kmdf-ioctl.html) | KMDF/UMDF y una respuesta fija con permisos restrictivos; sin acceso arbitrario a memoria. |
| 6.3 | [Debugging de kernel y bugchecks](6-03-debug-kernel.html) | WinDbg en target VM, stacks/dumps y Driver Verifier con rollback. |
| 6.4 | [Revisión defensiva de un driver](6-04-revision-driver.html) | device interfaces, IOCTLs, SDDL y validación de entradas. |
| 6.5 | [Minifilters y callbacks](6-05-minifilters.html) | Pila de filesystem, callbacks pre/post y límites de observación. |
| 6.6 | [Mitigaciones de Windows para drivers](6-06-mitigaciones.html) | firma, Secure Boot, HVCI/VBS, WDAC y vulnerable driver blocklist. |

## Recursos de CLS para esta etapa

- [2D · Windows internals (solo lecciones requeridas para esta rama)](../2d.html)
- [Extensión Hyper-V (optativa, no requisito)](../2d-hyperv.html)

## Evaluación de salida

- Explicar la ruta de una solicitud y los límites de IRQL, memoria y sincronización.
- Revisar un IOCTL propio de salida fija, con acceso limitado y validación completa; si no se puede cargar en VM conforme a la política vigente, entregar revisión estática.
- Leer un stack/dump de driver propio o muestra didáctica, indicando límites de símbolos y causalidad.
- Verificar mitigaciones en solo lectura y explicar qué protegen, sin desactivarlas.
- Demostrar rollback/limpieza de la VM; Driver Verifier no es requisito de aprobación.

:::{practica} Entregable de la etapa
Un archivo en tu bitácora con: lecciones completadas, ejercicios resueltos, dudas abiertas y evidencia (capturas, valores, hashes). Sin evidencia no se considera aprobada.
:::

## Errores frecuentes

- Probar un driver en el equipo principal o desactivar protecciones para forzar su carga.
- Crear IOCTLs de lectura/escritura arbitraria o asumir que una ACL reemplaza la validación.
- Interpretar el módulo del bugcheck como causa raíz sin revisar stack y contexto.

## Qué no entra en esta etapa

Los temas que no tienen material revisado o que exceden el marco se listan en [Kernel y otros territorios](05-fuera-de-alcance.html). No los uses como atajo: cada rama tiene prerrequisitos.

:::nota Volver
[Mapa del curso](index.html) · [Inicio](../00_EMPEZAR_AQUI.html)
:::
