---
title: "2.23 (optativa) · Shellcode, red y C2: reconocer y describir"
description: "Identificar que un blob es shellcode y describir el tráfico de C2 contra un entorno simulado. Solo análisis y clasificación, no construcción. Ruta optativa."
etapa: "Etapa 2 · Windows avanzado (2C) · ruta optativa"
---

# Shellcode, red y C2: reconocer y describir

:::{aviso} Ruta optativa · solo análisis y clasificación
Especialización, no requisito de 2C. Acá se **reconoce y describe** —a alto nivel— shellcode y tráfico de C2 en un entorno controlado. **No** se explica cómo escribir shellcode ni cómo montar un C2: esta guía es defensiva y se queda en identificar y clasificar. **Prerrequisitos:** PE e imports (1.4), malware dinámico defensivo ([2.22](02-opt-malware-dinamico.html)), criptografía/encoding (4.2).
:::

## Cómo se reconoce que algo es shellcode

Shellcode es **código máquina suelto**, sin envoltura PE: no tiene cabecera, secciones ni tabla de imports. Para el análisis alcanza con **reconocerlo** por sus rasgos, sin entrar en cómo está hecho por dentro (**conocimiento externo**):

- **No es un PE:** aparece como un **blob de bytes** dentro de un buffer, un recurso (RCDATA), un documento o tráfico de red, no como un `.exe`/`.dll`.
- **No tiene IAT PE:** al ser un blob sin formato PE, no trae la tabla de imports PE. Eso **no demuestra** que resuelva APIs por su cuenta: puede recibir funciones o datos desde un cargador, no usar APIs, usar llamadas al sistema, o resolverlas en tiempo de ejecución. La ausencia de IAT por sí sola no identifica cuál de esos casos aplica.
- **Autosuficiente:** strings armadas al vuelo o cifradas, y saltos/llamadas por direcciones calculadas en vez de referencias con nombre.

El Curso IDA menciona shellcode en el contexto de exploiting (p. ej. el tute 40, que además avisa que técnicas viejas pueden no andar en Windows 10 moderno). Lo tomamos solo como **algo a identificar**, no a producir ({{src:CLS_Guia/_trabajo/extraido_ida/40-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|Curso IDA, tute 40}}).

## Analizar un blob sin ejecutarlo en tu sistema

La forma segura de ver **qué hace** un shellcode es un **emulador** que lo corre en una caja y te reporta su comportamiento, sin tocar tu Windows (**conocimiento externo**):

- **`scdbg`** (basado en libemu) o **blobrunner + debugger en la VM**: emulan el blob y listan **qué APIs resolvió y llamó**.
- Vos leés el **reporte** y deducís la intención: si llama a algo como `WinExec`/`CreateProcess`, ejecuta un programa; si descarga y corre, es un *downloader*; si reserva memoria y escribe en otro proceso, es inyección.

No hace falta entender byte a byte cómo se autoresuelve: te quedás con el **qué hace** que reporta el emulador.

## C2: describir el tráfico

**C2** (*command and control*) es cómo una muestra habla con el atacante. En el laboratorio de [2.22](02-opt-malware-dinamico.html), con **red simulada** (INetSim/FakeNet) y Wireshark, **describís** el canal sin darle salida real:

- **Beacon:** conexiones periódicas a un dominio/IP (cada N segundos).
- **Protocolo:** HTTP(S) con User-Agent raro, DNS con subdominios largos (indicio de *DNS tunneling*), o un puerto TCP fijo.
- **Datos:** muchas veces base64 o XOR sobre el contenido (lo reconocés con [4.2 criptografía](04-cripto.html)).

El entregable es una **descripción + IOCs de red** (dominios, IPs, patrón del beacon), no una réplica del canal.

## Ejemplo: cómo se lee el reporte de un emulador

*(Ejemplo **ilustrativo**: salida resumida de un emulador tipo `scdbg`, no un blob real.)*

```text
scdbg sobre blob_demo.bin (emulado, NO ejecutado en el host):
  APIs resueltas/llamadas:
    LoadLibraryA("wininet.dll")
    InternetOpenA / InternetOpenUrlA  → http://descarga.ejemplo-demo.test/p.bin
    CreateFileA("%TEMP%\p.bin")  → WriteFile
    WinExec("%TEMP%\p.bin")
  Lectura: es un DOWNLOADER → baja p.bin y lo ejecuta.
  IOCs: descarga.ejemplo-demo.test ; %TEMP%\p.bin
```

Con solo **leer qué APIs resolvió** el emulador, clasificás el shellcode (downloader) y sacás los IOCs, sin analizar su mecánica interna ni ejecutarlo en tu sistema.

## Práctica

En tu VM aislada, con un **blob de curso** (o un programa benigno que simule el comportamiento):

1. Comprobá si el blob tiene envoltura PE; tratá la ausencia de cabecera/imports solo como un indicio y usá el contexto y el análisis como evidencia adicional.
2. Pasalo por **`scdbg`** (o un emulador equivalente) y leé qué APIs resuelve.
3. Clasificalo: ¿ejecuta, descarga, inyecta? Justificá con las APIs del reporte.
4. Si hay red, describí el beacon en el laboratorio simulado y anotá los IOCs.

## Preguntas de repaso

?? ¿Qué distingue a un shellcode de un `.exe` normal?
!! No tiene envoltura **PE** (cabecera, secciones ni IAT PE): es código suelto dentro de un buffer, recurso o tráfico. Eso no permite concluir por sí solo cómo obtiene funciones; puede depender de un cargador, no usar APIs o resolverlas durante la ejecución.

?? ¿Cómo ves qué hace un shellcode sin ejecutarlo en tu máquina?
!! Con un **emulador** (`scdbg`/libemu, o blobrunner en la VM): corre el blob en una caja y reporta las **APIs que resuelve y llama**; vos leés ese reporte para clasificarlo.

?? Si el reporte muestra `InternetOpenUrlA` + `CreateFile` + `WinExec`, ¿qué es?
!! Un **downloader**: baja un archivo y lo ejecuta. La combinación de APIs delata la intención.

?? ¿Qué es un beacon de C2 y cómo lo describís?
!! Conexiones **periódicas** de la muestra hacia su servidor. Lo describís por el **patrón** (cada N segundos), el protocolo (HTTP/DNS) y el dominio/IP, usando la red simulada; no replicás el canal.

?? ¿Cuál es el límite de esta lección?
!! **Reconocer y clasificar**. No se enseña a escribir shellcode ni a montar un C2; el trabajo se queda en análisis defensivo e IOCs.

:::{nota} Puerta de salida (optativa)
Podés: (1) explicar por qué la ausencia de PE/IAT no basta para demostrar que un blob es shellcode ni cómo resuelve funciones; (2) usar un emulador para observar y clasificar comportamiento; (3) describir un beacon de C2 en el laboratorio simulado; (4) entregar IOCs de red. Siempre en análisis, nunca en construcción.
:::

## Fuentes de esta lección

- {{src:CLS_Guia/_trabajo/extraido_ida/40-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|Curso IDA, tute 40}} — menciona shellcode en contexto de exploiting (y que técnicas viejas pueden no andar en Win10).
- [Malware dinámico defensivo](02-opt-malware-dinamico.html) (2.22) — el laboratorio aislado y la red simulada donde se observa el C2.
- [Reconocer criptografía y encoding](04-cripto.html) (4.2) — base64/XOR en el tráfico y los payloads.

:::{nota} Capas de esta lección
**Contenido observado en CLS:** la mención de shellcode del tute 40. **Conocimiento externo:** la identificación de código sin envoltura PE, aclarando que la ausencia de IAT no demuestra por sí sola resolución dinámica, los emuladores (`scdbg`/libemu) y el modelo de C2 (beacon, protocolo, IOCs). **Recomendación editorial:** el enfoque estricto de reconocer-y-clasificar, el ejemplo ilustrativo de salida de emulador y el límite de no construir.
:::
