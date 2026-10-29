---
title: "Etapa 4 · El informe reproducible"
description: "Cómo documentar un análisis para que otra persona pueda repetirlo, verificarlo y entender sus límites."
etapa: "Etapa 4 · Práctica guiada"
---

# El informe reproducible

:::{nota} Objetivo de la lección
Al terminar vas a poder escribir un informe de análisis con entorno, hashes, método, evidencia, conclusión y límites, y revisar el informe de otra persona con una lista de verificación.
:::

**Prerrequisitos:** método de análisis. **Duración sugerida:** 3 horas. Estimación aproximada.

## Para qué sirve un informe

Un análisis sin registro es una anécdota. Sirve para vos mientras lo recordás; no sirve para un equipo, no se puede auditar y no se puede repetir. El informe convierte una sesión de debugger en **conocimiento verificable**.

Hay tres destinatarios posibles:

1. **Vos mismo, en dos semanas.** ¿Qué binario era? ¿Con qué versión? ¿Qué probaste?
2. **Otra persona del equipo.** ¿Puede repetir el experimento sin preguntarte nada?
3. **Un tercero que necesita decidir.** ¿Es seguro? ¿Hay un riesgo? ¿Qué mitigación recomendarías?

El nivel de detalle cambia según el destinatario, pero la estructura es la misma.

## Estructura mínima

```text
1. Identificación
   - Archivo, tamaño, SHA-256, origen, fecha de recepción
   - Entorno: SO, VM, herramientas y versiones, snapshot
2. Alcance y pregunta
   - Qué se analizó y qué quedó fuera
   - Pregunta concreta que guía el trabajo
3. Método
   - Estático: herramienta, pasos, direcciones
   - Dinámico: breakpoints, valores, condiciones
4. Observaciones
   - Tabla de evidencia: qué se hizo, qué se observó, dónde está la prueba
5. Conclusión
   - Respuesta directa, con grado de certeza
6. Límites
   - Qué no se probó, qué supuestos quedan, qué podría cambiar el resultado
7. Recomendaciones
   - Defensivas: detección, mitigación, monitoreo (si corresponde)
8. Anexos
   - Logs, capturas, scripts, hashes de artefactos
```

La plantilla del proyecto está en {{src:CLS_Guia/plantilla_informe.md|plantilla_informe.md}}. Esta lección la amplía con criterios de evidencia.

## Ejemplo: informe corto de `check.exe`

Este es un informe de ejemplo sobre el programa de práctica de la lección anterior. Los valores son los que se observaron en esa práctica; las direcciones son ilustrativas y pueden variar en tu compilación.

```text
INFORME DE ANÁLISIS — check.exe
Fecha: 2026-10-26
Analista: (tu nombre)

1. IDENTIFICACIÓN
Archivo: check.exe (52 KB)
SHA-256: <hash calculado con Get-FileHash>
Origen: compilado por el analista a partir de check.c (gcc -O0 -g)
Entorno: Windows 11 en VM, snapshot 00-limpia, x64dbg 2025.x, IDA Free 8.x
Alcance: determinar la condición de aceptación de dos números enteros.
Fuera de alcance: comportamiento fuera de la VM, otras compilaciones.

2. MÉTODO
Estático: búsqueda de la cadena "Correcto" (Shift+F12), xref (X),
lectura del grafo, renombrado de variables.
Dinámico: breakpoint en la comparación final, ejecución con
(40,80), (40,70) y (60,80).

3. OBSERVACIONES
| Entrada | EAX en la comparación | ZF | Salida |
| 40, 80  | 0x1E0                 | 1  | Correcto |
| 40, 70  | 0x1B8                 | 0  | Incorrecto |
| 60, 80  | no llega              | —  | Incorrecto (falla a>50) |

4. CONCLUSIÓN
El programa acepta pares (a,b) con a <= 50, b >= 50 y (a+b)*4 == 480.
Certeza: alta para esta compilación; no se probó exhaustivamente el espacio.

5. LÍMITES
No se analizaron otras compilaciones ni variantes del código.
No se evaluó el comportamiento con entradas no numéricas.
```

Ese informe es corto, pero responde: qué, cómo, con qué, qué se vio y qué falta.

## Qué hace que una evidencia sea buena

| Buena evidencia | Mala evidencia |
|---|---|
| Valor exacto, dirección, timestamp | "Se ve que compara" |
| Captura con la ventana y el valor visibles | Captura recortada sin contexto |
| Comando reproducible | "Lo hice con una herramienta" |
| Hash del binario | "El archivo que me pasaron" |
| Diferencia entre observado y supuesto | Mezcla de ambos sin aclarar |

Una captura vale si se entiende **qué** muestra y **dónde** está el dato. Si recortás la ventana y no se ve la dirección ni el registro, no sirve como evidencia.

## Trazabilidad: el hash y la cadena de custodia

El SHA-256 del binario es la forma de decir "este análisis corresponde exactamente a este archivo". Si el archivo cambia, el hash cambia.

Buenas prácticas:

1. Calculá el hash **al recibir** el archivo y anotalo.
2. Guardá una copia de trabajo con permisos de lectura.
3. No modifiques el original; si parcheás, trabajá sobre una copia y anotá el hash de la copia.
4. Registrá quién tuvo acceso y cuándo, si el contexto lo requiere.

Para malware, la cadena de custodia es más estricta: el archivo no sale del laboratorio, no se comparte por correo ni se sube a servicios públicos sin evaluar el riesgo.

## Cómo se redacta la conclusión

Una conclusión no es un resumen del método. Es una **respuesta**. Tiene que poder leerse sola.

| Mal | Bien |
|---|---|
| "Se analizó el binario y se encontraron comparaciones." | "El programa acepta `a <= 50`, `b >= 50` y `(a+b)*4 == 480`." |
| "Parece que hay un chequeo." | "El chequeo está en la comparación de `EAX` con `0x1E0`; con (40,80) `ZF=1`." |
| "Es seguro." | "No se observó actividad de red ni escritura fuera de la carpeta de trabajo en la VM." |

La segunda columna es más útil porque **afirma algo que se puede contradecir con evidencia**.

## Divulgación responsable

Si en un análisis autorizado encontrás una vulnerabilidad:

1. **No publiques el exploit** ni los detalles técnicos antes de que el proveedor pueda responder.
2. Documentá el impacto, la versión afectada y los pasos mínimos para reproducirlo.
3. Contactá al proveedor por un canal privado; guardá la evidencia.
4. Acordá un plazo razonable (por ejemplo, 90 días) antes de publicar.
5. No accedas a datos de terceros, no escales privilegios y no dejes puertas abiertas.

Esta guía no enseña a explotar sistemas ajenos. Los ejercicios de vulnerabilidades se hacen en programas propios o laboratorios diseñados para eso.

## Práctica

1. Escribí el informe completo de tu `check.exe` con la estructura de arriba.
2. Incluí una tabla de evidencia con al menos tres filas.
3. Agregá una sección de límites con dos supuestos que no verificaste.
4. Intercambiá el informe con un compañero (o releelo al día siguiente) y aplicá esta lista:

| Punto | Sí/No |
|---|---|
| ¿Está el hash del binario? | |
| ¿Está el entorno y la versión de las herramientas? | |
| ¿La pregunta es específica? | |
| ¿Cada conclusión tiene evidencia asociada? | |
| ¿Se distingue observado de supuesto? | |
| ¿Se puede repetir el experimento con lo escrito? | |
| ¿Los límites son honestos? | |

## Preguntas de repaso

**1. ¿Por qué el hash es parte del informe?**
Porque identifica sin ambigüedad el archivo analizado. Si el hash cambia, el informe ya no aplica a ese archivo.

**2. ¿Qué diferencia hay entre una observación y una conclusión?**
La observación es lo que viste ("EAX=0x1E0"); la conclusión es lo que inferís ("la condición es (a+b)*4=480").

**3. ¿Para qué sirve la sección de límites?**
Para que el lector sepa qué no se probó y no sobreestime el alcance del análisis.

**4. ¿Qué hace reproducible un informe?**
Que incluya el binario identificado por hash, el entorno, los pasos y los valores observados, de modo que otra persona pueda repetirlos.

**5. ¿Qué se hace si se encuentra una vulnerabilidad?**
Documentarla, reportarla en privado al proveedor, no publicar el exploit y acordar un plazo de divulgación.

## Antes de avanzar

Tenés que poder:

- Escribir un informe con las ocho secciones.
- Distinguir evidencia de opinión.
- Calcular y registrar el hash del binario.
- Explicar la diferencia entre divulgar y publicar un exploit.

:::{nota} Puerta de salida
Si tu informe puede repetirlo otra persona sin preguntarte nada, está listo. Si no, falta evidencia o falta método.
:::

## Fuentes de esta lección

- {{src:CLS_Guia/plantilla_informe.md|plantilla_informe.md}} — plantilla base del proyecto.
- {{src:CLS_resultados_intermedios/inventario_limpio/LEEME.md|Inventario limpio, LEEME}} — uso de SHA-256 y criterio de no ejecución.
- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_11 Ejercicio 1 - Análisis dinámico_11 Ejercicio 1 - Análisis dinámico.txt|Reversing desde cero, cap. 11}} — método de análisis y documentación visual.
- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_15 Ejercicio 2 - Análisis estático_15 Ejercicio 2 - Análisis estático.txt|Reversing desde cero, cap. 15}} — valores y confirmación que alimentan el informe de ejemplo.

:::{nota} Capas de esta lección
**Contenido observado en CLS:** el método de los capítulos 11 y 15 y el uso de hashes del inventario. **Conocimiento externo:** estructura de informes técnicos y divulgación responsable. **Recomendación editorial:** la plantilla ampliada, la tabla de evidencia y el informe de ejemplo.
:::
