---
title: "Etapa 4 · Análisis dinámico seguro: cuándo ejecutar y cuándo no"
description: "Criterios para decidir si un programa se ejecuta, cómo contenerlo y qué hacer si algo sale mal."
etapa: "Etapa 4 · Práctica guiada"
---

# Análisis dinámico seguro: cuándo ejecutar y cuándo no

:::{nota} Objetivo de la lección
Al terminar vas a poder decidir si un programa se analiza solo en estático o se ejecuta en un laboratorio, preparar la observación con herramientas de monitoreo y actuar si el comportamiento se sale de lo previsto.
:::

**Prerrequisitos:** laboratorio (Etapa 0) y método (Etapa 4). **Duración sugerida:** 3 horas. Estimación aproximada.

## La decisión más importante

No todo se ejecuta. Antes de abrir un programa en el debugger, hacete tres preguntas:

1. **¿Tengo permiso?** ¿Es mío, es de código abierto, es un crackme de práctica, o tengo autorización escrita?
2. **¿Puedo contenerlo?** ¿Está en una VM aislada, con snapshot, sin carpetas compartidas y sin red personal?
3. **¿Necesito ejecutarlo?** ¿La pregunta se responde con análisis estático, o el comportamiento dinámico es imprescindible?

Si alguna respuesta es "no", el programa no se ejecuta. Se analiza estático, se documenta y se deriva a quien corresponda.

| Situación | Qué hacer |
|---|---|
| Programa propio o de práctica | Ejecutar en VM, con snapshot |
| Software abierto que querés entender | Ejecutar en VM, con la licencia respetada |
| Binario de origen desconocido | Estático primero; dinámico solo en laboratorio dedicado |
| Malware confirmado | Estático y detección; dinámico solo con protocolo defensivo |
| Software comercial con protección | No eludir protecciones; analizar solo lo permitido |
| Archivo en cuarentena o excluido | No ejecutar; respetar la clasificación |

## Antes de ejecutar: línea base

Una observación sin línea base no sirve. Antes de correr el programa, registrá el estado del sistema:

- Procesos en ejecución.
- Conexiones de red.
- Archivos en la carpeta de trabajo.
- Claves de registro relevantes (si vas a observar persistencia).
- Hora de inicio.

Herramientas: **Process Explorer** (procesos, handles), **Process Monitor** (archivos, registro, procesos), **TCPView** (conexiones), **Autoruns** (persistencia). Todas son de Sysinternals o equivalentes gratuitos.

En la VM:

```text
1. Restaurar snapshot 00-limpia.
2. Anotar hora y estado.
3. Iniciar Process Monitor con filtro por nombre del proceso.
4. Iniciar TCPView.
5. Ejecutar el programa.
6. Observar, anotar y detenerse.
7. Cerrar el programa, detener las capturas y restaurar snapshot.
```

## Qué observar

| Categoría | Qué mirar | Herramienta |
|---|---|---|
| Archivos | Creación, lectura, escritura, borrado | Process Monitor |
| Registro | Claves creadas/modificadas | Process Monitor |
| Procesos | Hijos, inyecciones, elevación | Process Explorer |
| Red | Conexiones, DNS, puertos | TCPView, Wireshark |
| Memoria | Regiones RWX, módulos cargados | x64dbg, Process Explorer |
| Persistencia | Run keys, servicios, tareas | Autoruns |

No hace falta observar todo a la vez. Elegí dos o tres categorías según la pregunta.

## El caso Shelter: lo que CLS muestra y lo que no se copia

El video 37 analiza el malware Shelter dentro de una VM Windows 7 de 32 bits, con otra VM Kali Linux para simular el ataque. El propio autor distingue análisis estático y dinámico y dice que en su caso va a ejecutar la muestra ({{src:CLS_resultados_intermedios/transcripciones/extraidos/Videos y material adicional Ingenieria Inversa/Videos_Video37_Video37.txt|Videos y material adicional, Video 37}}, 00:24:01–00:24:21).

Ese video es un **caso observado**, no un modelo para esta guía. Ejecuta malware, monta un reverse shell y usa una segunda VM para el ataque. Para un principiante, el orden correcto es:

1. Triage estático: tipo de archivo, secciones, imports, strings, hashes.
2. Detección: reglas YARA, firmas, comparación con VirusTotal **sin subir muestras confidenciales**.
3. Documentación de indicadores.
4. Solo si hay un propósito defensivo claro y un laboratorio dedicado, análisis dinámico controlado.

El video 36 inyecta una puerta trasera de Metasploit en una calculadora y usa una VM "por seguridad" ({{src:CLS_resultados_intermedios/transcripciones/extraidos/Videos y material adicional Ingenieria Inversa/Videos_Video36_Video36.txt|Videos y material adicional, Video 36}}, 00:29:21–00:29:42). Tampoco es una práctica de esta guía.

:::{peligro} Lo que no se hace
No se ejecuta malware en el host. No se conecta la VM de análisis a la red doméstica. No se comparten carpetas. No se usan cuentas personales. No se sube una muestra a un servicio público sin evaluar si es confidencial. No se copia el malware fuera del laboratorio.
:::

## Anti-debug: una señal, no un obstacle a vencer

Si un programa detecta el debugger y se cierra, eso **es información**. Puede indicar:

- Que el programa tiene protecciones anti-análisis.
- Que está empaquetado.
- Que su comportamiento cambia según el entorno.

Los chequeos más comunes están en el capítulo 22 (PEB, `IsDebuggerPresent`, `NtGlobalFlag`) y en el capítulo 24 (lista de procesos, ParentPID, `CloseHandle` inválido). El capítulo 24 usa un crackme propio que muestra qué técnica lo detectó ({{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_24 Antidebug 2_24 Antidebug 2.txt|Reversing desde cero, cap. 24}}, 00:01:17–00:03:31).

Para esta guía:

- **Estudiá** los mecanismos para reconocerlos y explicar por qué un binario se comporta distinto.
- **No** aprendas a evadir las protecciones de software comercial.
- **No** uses técnicas de ocultamiento para analizar muestras fuera de un laboratorio autorizado.
- Si el objetivo es defender, la pregunta es "¿cómo detecto este comportamiento?", no "¿cómo lo esquivo?".

## Si algo sale mal

Un plan de contención tiene que existir antes de ejecutar:

1. **Detener la VM** (no suspenderla): apagado forzado si hace falta.
2. **Desconectar la red** de la VM desde el hipervisor.
3. **Restaurar la snapshot** limpia.
4. **Revisar el host**: procesos, conexiones, archivos compartidos, cuentas.
5. **Anotar** qué pasó, a qué hora y qué se observó.
6. **Reportar** si hubo exposición de datos o credenciales.
7. **Cambiar** las credenciales que pudieron quedar expuestas.

Si el programa logró escribir en una carpeta compartida o conectar a la red local, el aislamiento falló. Eso se documenta y se corrige antes de la próxima práctica.

## Práctica

1. Ejecutá tu `check.exe` en la VM con Process Monitor filtrando por el nombre del proceso. Anotá qué archivos abre y qué claves de registro lee.
2. Ejecutá una versión que abra un archivo (`fopen`) y observá la operación de escritura.
3. Hacé una lista de línea base antes y después. ¿Qué cambió?
4. Elegí un archivo del proyecto marcado `cuarentena` y hacé **solo** triage estático: tipo, secciones, imports, strings, hash. No lo ejecutes.
5. Escribí un procedimiento de 10 líneas para "qué hago si la VM se comporta raro".

## Preguntas de repaso

**1. ¿Cuándo NO se ejecuta un programa?**
Cuando no tenés permiso, no podés contenerlo o no necesitás el comportamiento dinámico. También cuando está en cuarentena o excluido.

**2. ¿Por qué se toma una línea base antes de ejecutar?**
Porque sin el estado inicial no podés atribuir los cambios al programa. La comparación antes/después es la evidencia.

**3. ¿Qué indica que un programa detecte el debugger?**
Que tiene protecciones anti-análisis o que su comportamiento depende del entorno. Es un dato para documentar, no un obstáculo para "saltar".

**4. ¿Qué hace primero si una muestra resulta sospechosa?**
Triage estático, cálculo de hash, documentación de indicadores y, si corresponde, derivación. No se ejecuta en el host.

**5. ¿Qué hace si la VM se conecta a la red local?**
Se desconecta desde el hipervisor, se restaura la snapshot, se revisa el host y se documenta el fallo de aislamiento.

## Antes de avanzar

Tenés que poder:

- Decidir si un programa se ejecuta o no, con justificación.
- Tomar una línea base y observar con Process Monitor/TCPView.
- Explicar por qué el video 37 no es un modelo de práctica.
- Describir un plan de contención.

:::{nota} Puerta de salida de la Etapa 4
Si podés analizar, documentar y contener una práctica completa, terminaste el recorrido base. Las ramas de la Etapa 5 son opcionales y exigen prerrequisitos.
:::

## Fuentes de esta lección

- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Videos y material adicional Ingenieria Inversa/Videos_Video37_Video37.txt|Videos y material adicional, Video 37}} — caso Shelter: VM, Kali y ejecución de malware; se cita como caso observado.
- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Videos y material adicional Ingenieria Inversa/Videos_Video36_Video36.txt|Videos y material adicional, Video 36}} — XOR, crypter y backdoor en VM.
- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_22 Antidebug 1_22 Antidebug 1.txt|Reversing desde cero, cap. 22}} — PEB y detección de debugger.
- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_24 Antidebug 2_24 Antidebug 2.txt|Reversing desde cero, cap. 24}} — cuatro chequeos anti-debug.
- {{src:CLS_resultados_intermedios/inventario_limpio/LEEME.md|Inventario limpio, LEEME}} — estados `cuarentena` y criterio de no ejecución.

:::{nota} Capas de esta lección
**Contenido observado en CLS:** el laboratorio con dos VMs del video 37, la inyección del video 36 y los chequeos de los capítulos 22 y 24. **Conocimiento externo:** observación con Process Monitor/TCPView y planes de contención. **Recomendación editorial:** la matriz de decisión y el protocolo de incidentes.
:::
