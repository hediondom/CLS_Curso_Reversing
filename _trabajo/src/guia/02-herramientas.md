---
title: "Etapa 2 · Herramientas: del OllyDbg histórico al taller actual"
description: "Qué herramienta sirve para cada tarea, cuáles están discontinuadas y cómo armar un taller verificable."
etapa: "Etapa 2 · Introducción al reversing"
---

# Herramientas: del OllyDbg histórico al taller actual

:::{nota} Objetivo de la lección
Al terminar vas a poder elegir la herramienta adecuada para identificar, desensamblar, depurar o inspeccionar un binario, justificar por qué algunas del curso son históricas y registrar versiones y hashes de tu taller.
:::

**Prerrequisitos:** debugger e IDA. **Duración sugerida:** 2 horas. Estimación aproximada.

## Por qué hablar de herramientas

El conocimiento de reversing —registros, stack, saltos, PE— envejece poco. Las herramientas envejecen rápido. El curso de CLS mezcla material de 2007, 2016 y 2021, y usa OllyDbg en una parte y x64dbg en otra. Si no distinguís qué es concepto y qué es botón, vas a estudiar una interfaz muerta creyendo que estudias reversing.

## El taller mínimo

| Tarea | Herramienta | Estado | Nota |
|---|---|---|---|
| Depurar 32 y 64 bits | **x64dbg** | Activa | Gratis, open source, Windows |
| Desensamblar | **IDA Free** | Activa (versión gratuita) | Limitada pero suficiente para empezar |
| Desensamblar y decompilar | **Ghidra** | Activa | Gratis, open source, multiplataforma |
| Editar bytes | **HxD** | Activa | Gratis para uso personal; verificar licencia |
| Ver cabecera PE | **PE-bear**, **CFF Explorer**, **Detect It Easy** | Activas | Detect It Easy también identifica empaquetado |
| Ver procesos y handles | **Process Explorer** (Sysinternals) | Activa | Útil para el mapa de memoria y handles |
| Ver actividad de archivos/registro | **Process Monitor** | Activa | Para análisis dinámico controlado |
| Ver red | **TCPView**, **Wireshark** | Activas | Solo en laboratorio aislado |
| Automatizar | **Python** + `pefile`, `capstone` | Activas | Opcional |
| Detección | **YARA** | Activa | Para reglas defensivas |

No necesitás instalar todo el primer día. x64dbg, un editor hexadecimal y un visor de PE alcanzan para las etapas 1 a 4.

## El taller actual (2026): más allá de lo mínimo

:::{aviso} Actualización externa
El corpus CLS no cubre estas herramientas (son más nuevas que su material). Las agregamos como **conocimiento externo** para que el taller esté al día. Todas corren o se usan sobre **Windows**; no son obligatorias para el recorrido base, pero sí para análisis real.

Verificá siempre la versión y descargá desde el sitio oficial.
:::

Cuando el taller mínimo se te queda corto, estas categorías son las que usa hoy un analista de Windows:

| Categoría | Herramienta | Para qué |
|---|---|---|
| **Instrumentación dinámica** | **Frida** | Enganchar (*hook*) funciones de un proceso en vivo, leer/alterar argumentos y resultados con scripts. Potente para ver qué pasa sin trazar a mano. |
| **Time-travel debugging** | **WinDbg** + **TTD** | Grabar una ejecución completa y recorrerla **hacia atrás**. Ideal para "¿quién puso este valor?" sin reiniciar mil veces. |
| **Diffing de binarios** | **BinDiff**, **Diaphora** | Comparar dos versiones de un binario (por ejemplo, antes y después de un parche) para ver qué cambió. Clave en análisis de parches. |
| **Extracción de strings** | **FLOSS** (Mandiant) | Saca strings normales **y** las ofuscadas/apiladas que `strings` no ve. |
| **Triage y capacidades** | **CAPA**, **PEStudio** | Identifican qué "sabe hacer" un binario (red, cripto, persistencia) por patrones, sin ejecutarlo. |
| **Clasificación/detección** | **YARA** | Reglas para reconocer familias y rasgos. Defensivo. |
| **Emulación y análisis simbólico** | **Unicorn**, **Qiling**, **angr**, **Triton** | Ejecutar un fragmento sin el programa completo, o explorar caminos de forma simbólica (p. ej. "¿qué entrada llega a este bloque?"). |
| **Desensamblado programable** | **Capstone** (leer) + **Keystone** (ensamblar) | Librerías para construir tus propias herramientas en Python. |

:::{nota} Asistencia con IA (con cautela)
Hay plugins que usan modelos de lenguaje para **sugerir** nombres de funciones y variables o explicar un bloque decompilado (por ejemplo, asistentes para Ghidra/IDA). Pueden acelerar la lectura, pero **alucinan**: un nombre sugerido es una hipótesis, no un hecho. Usalos como punto de partida y **verificá** cada afirmación contra el código, igual que harías con el renombrado automático de un script.
:::

Elegí por tarea, no por moda: para "¿quién escribe este buffer?" quizás te alcance un breakpoint de memoria en x64dbg; TTD y angr son para cuando el problema lo justifica.

:::{nota} En el Curso IDA: plugins y cuidado con la versión
El Curso IDA dedica una parte a los **plugins** que amplían IDA, con una advertencia que sigue valiendo: algunos no andan en la 6.8 pero sí en la 7.x, así que si no los podés instalar, al menos leé para qué sirven. Y muestra un **bug de la versión 6.8** (corregido en la 6.9) y cómo reconocerlo. Moraleja: **fijate qué versión de IDA tenés** antes de pelearte con un plugin que "no funciona" ([Curso IDA · tute 13, Plugins](../ida_tutes/13.html) y [tute 11, Bug de la 6.8](../ida_tutes/11.html)).
:::

## OllyDbg: herramienta histórica, no obsoleta como concepto

OllyDbg es un debugger de **ring 3 para binarios de 32 bits**, muy popular en los 2000. El curso de Cayetano de Juan Úbeda lo usa como herramienta principal en los videos 23 a 40, con una máquina virtual Windows 7 de 32 bits ({{src:CLS_resultados_intermedios/transcripciones/extraidos/Videos y material adicional Ingenieria Inversa/Videos_Video24_Video24.txt|Videos y material adicional, Video 24}}, 00:00:00 y 00:31:47).

Lo que OllyDbg enseña sigue siendo válido:

- Ver el estado de los registros y la pila.
- Poner breakpoints y trazar instrucción por instrucción.
- Leer el flujo de un `if` compilado.
- Identificar una comparación de clave.

Lo que cambió:

- No maneja binarios de 64 bits.
- No se actualiza desde hace años.
- Su interfaz y sus atajos no son los de x64dbg.
- Algunos plugins y técnicas de la época ya no funcionan en Windows modernos.

**Conclusión:** mirá los videos de OllyDbg por el método y los conceptos, no para aprender la interfaz. Después repetí el mismo ejercicio en x64dbg.

## El flujo de trabajo con herramientas

```text
1. Identificar      -> Detect It Easy / ExeInfoPE / PE-bear
2. Entender formato -> cabecera PE, secciones, imports
3. Análisis estático-> IDA Free / Ghidra
4. Análisis dinámico-> x64dbg (solo en laboratorio)
5. Documentar       -> bitácora + informe
```

Cada paso tiene una pregunta:

| Paso | Pregunta que responde |
|---|---|
| Identificar | ¿Qué tipo de archivo es? ¿Está empacado? ¿Es .NET? |
| Formato | ¿Dónde está el código? ¿Qué imports usa? |
| Estático | ¿Qué hace esta función? ¿Qué cadenas y APIs aparecen? |
| Dinámico | ¿Qué valores toma en esta ejecución? ¿Qué camino sigue? |
| Documentar | ¿Puede otra persona reproducir lo que hice? |

El video 33 insiste en que el **mapa de memoria** es lo primero que abre al analizar un binario ({{src:CLS_resultados_intermedios/transcripciones/extraidos/Videos y material adicional Ingenieria Inversa/Videos_Video33_Video33.txt|Videos y material adicional, Video 33}}, 00:02:00–00:03:00). El video 39 muestra ExeInfoPE mirando cabecera, linker, secciones y entry point ({{src:CLS_resultados_intermedios/transcripciones/extraidos/Videos y material adicional Ingenieria Inversa/Videos_Video39_Video39.txt|Videos y material adicional, Video 39}}, 00:00:32–00:02:09).

## Lo que no cambia

Estos conceptos valen igual en OllyDbg, x64dbg, IDA y Ghidra:

- La diferencia entre dirección virtual, RVA y offset.
- El stack y las convenciones de llamada.
- El significado de `cmp`, `test` y los saltos.
- La IAT y las llamadas indirectas.
- La diferencia entre análisis estático y dinámico.

Si entendés eso, cambiar de herramienta es aprender una interfaz nueva, no empezar de cero.

## Práctica: inventario del taller

1. Instalá x64dbg, un editor hexadecimal y un visor de PE. Anotá versión y fecha de descarga.
2. Calculá el SHA-256 de cada instalador y guardalo en tu bitácora.
3. Abrí tu `check.exe` con el visor de PE, con x64dbg y con IDA Free. Completá:

| Herramienta | Qué te mostró que las otras no |
|---|---|
| Visor de PE | |
| x64dbg | |
| IDA Free | |

4. Buscá en el binario una cadena tuya ("Correcto") con las tres herramientas. ¿Cuál fue más rápida?
5. Escribí en tu bitácora qué herramienta usarías para: (a) saber si un binario está empacado, (b) encontrar quién escribe un buffer, (c) leer una función que nunca se ejecuta.

## Preguntas de repaso

**1. ¿Por qué OllyDbg se considera histórico?**
Porque es un debugger de 32 bits que ya no se actualiza. Sigue siendo útil para estudiar el método de la época, pero no es la herramienta recomendada para empezar hoy.

**2. ¿x64dbg reemplaza a IDA?**
No. x64dbg es un debugger; IDA es un desensamblador estático. Se complementan.

**3. ¿Qué herramienta usarías para saber si un binario está empacado?**
Detect It Easy, ExeInfoPE o un visor de PE: miran secciones, imports y entry point. La señal orienta, no concluye.

**4. ¿Qué significa que una herramienta esté "activa"?**
Que recibe mantenimiento y funciona en sistemas actuales. No significa que sea obligatoria ni que sea la mejor para todo.

**5. ¿Por qué registrar la versión de las herramientas?**
Porque un cambio de versión puede cambiar la interfaz o el comportamiento. Un informe reproducible dice con qué versión se hizo.

## Antes de avanzar

Tenés que poder:

- Elegir herramienta para identificar, desensamblar, depurar y editar.
- Explicar por qué OllyDbg es histórico y qué se puede aprender de él.
- Registrar versiones y hashes de tu taller.
- Decir qué conceptos no dependen de la herramienta.

:::{nota} Puerta de salida
Si tu bitácora tiene el inventario del taller con versiones y hashes, estás listo para .NET.
:::

## Fuentes de esta lección

- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Videos y material adicional Ingenieria Inversa/Videos_Video23_Video23.txt|Videos y material adicional, Video 23}} — introducción al reversing y limitaciones del análisis.
- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Videos y material adicional Ingenieria Inversa/Videos_Video24_Video24.txt|Videos y material adicional, Video 24}} — OllyDbg y la VM Windows 7 de 32 bits.
- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Videos y material adicional Ingenieria Inversa/Videos_Video33_Video33.txt|Videos y material adicional, Video 33}} — PE, secciones e imports.
- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Videos y material adicional Ingenieria Inversa/Videos_Video39_Video39.txt|Videos y material adicional, Video 39}} — ExeInfoPE.
- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_14 Conociendo IDA_14 Conociendo IDA.txt|Reversing desde cero, cap. 14}} — IDA y sus límites.
- [Curso IDA · tutes 11 y 13](../ida_tutes/11.html) — plugins de IDA y el bug de la versión 6.8 (atención a la versión).

:::{nota} Capas de esta lección
**Contenido observado en CLS:** el uso de OllyDbg en los videos 23–40, la VM Windows 7 y el recorrido de ExeInfoPE. **Conocimiento externo (agregado por esta edición):** el estado actual de las herramientas y todo el "taller actual 2026" (Frida, WinDbg/TTD, BinDiff/Diaphora, FLOSS, CAPA, angr/Unicorn, asistencia con IA). **Recomendación editorial:** el taller mínimo, la tabla de decisión y la cautela con la IA.
:::
