---
title: 4.5 · Reconstruir formatos y protocolos propios
description: Deducir estructura, framing, estados y transformaciones a partir de muestras controladas de programas propios en Windows.
etapa: Etapa 4 · Práctica guiada
---

# Reconstruir formatos y protocolos propios

:::{nota} Objetivo de la lección
Dado un conjunto pequeño de archivos o mensajes generados por un programa propio, formular y comprobar una estructura: campos, offsets, longitudes, endianness, framing y estados. Distinguir checksum, hash, MAC, compresión y cifrado como hipótesis diferentes, y anotar qué evidencia sostiene cada conclusión.
:::

**Prerrequisitos:** [Bits y endianness](01-numeros.html) (1.1), [formato PE](01-pe.html) (1.4), [método de análisis](04-metodo.html) (4.1), [IPC de Windows](2d-10-ipc.html) como referencia. **Duración sugerida:** 6 horas.

:::{aviso} Alcance y muestras
Usá archivos y programas **propios** o diseñados para la práctica. Para un protocolo, trabajá con dos procesos tuyos en una VM, una named pipe local o loopback. No envíes datos a servicios de terceros. **Capas:** conocimiento externo; ejemplo CLSF ilustrativo y sintético; laboratorio no verificado. La práctica propuesta usa programas propios y comunicación local.
:::

## Del síntoma a una pregunta comprobable

«¿Qué significa este blob?» es demasiado amplio. Convertí la duda en una pregunta que permita diseñar una prueba:

- ¿Los primeros cuatro bytes son una firma constante?
- ¿Este entero describe la longitud del cuerpo, del encabezado o del archivo completo?
- ¿Dos mensajes consecutivos se separan por longitud, delimitador o estado de la conexión?
- ¿Qué campo cambia cuando cambia solo el contenido?
- ¿El bloque final detecta corrupción accidental, autentica el mensaje o solo parece aleatorio?

Conservá cada muestra original sin modificarla, calculá su hash y anotá cómo se obtuvo. Trabajá sobre copias. Una tabla de diferencias entre muestras vale más que una interpretación basada en un solo archivo.

## Procedimiento de reconstrucción

1. **Inventario.** Anotá tamaño, hash, origen de laboratorio, herramienta que lo produjo y si el espécimen es archivo, mensaje, flujo o captura. Identificá la envoltura conocida y separala del formato interno.
2. **Muestras controladas.** Generá pares que difieran en una sola propiedad: una cadena más larga, otro valor, un registro adicional o una versión distinta. Incluí casos válidos vacíos y límites que tu programa admita.
3. **Mapa de bytes.** Numera offsets desde cero; registra bytes, ASCII/UTF-16, enteros little-endian/big-endian, alineación y regiones repetidas. No decidas el tipo de un campo por su apariencia aislada.
4. **Hipótesis.** Para cada campo escribe hipótesis, evidencia, alternativa y prueba que la refutaría. «Parece una longitud» no es conclusión hasta comprobar varios tamaños.
5. **Framing y estructura.** Separa cabecera, registros, cuerpo y tráiler. Prueba longitudes prefijadas, tamaños fijos, delimitadores, terminadores, conteos y esquemas TLV. Comprueba si las longitudes incluyen o excluyen cabecera/tráiler.
6. **Estado y secuencia.** Dibuja estados y transiciones: conexión, saludo, petición, respuesta, error y cierre. Relaciona cada mensaje con el estado previo; un opcode puede significar cosas distintas según el estado.
7. **Transformaciones.** Investiga por separado codificación, compresión, checksum/CRC, hash, MAC y cifrado. Usa perturbaciones controladas y evidencia del programa propio; entropía alta por sí sola no demuestra cifrado ni compresión.
8. **Validación independiente.** Comprueba la hipótesis con muestras no usadas para formularla, límites y entradas malformadas inocuas. Escribe un esquema y un parser de referencia mínimo.

## Endianness, longitudes y TLV

Un entero de dos bytes 05 00 vale 5 en little-endian; 00 05 vale 5 en big-endian. En tráfico IP, los campos numéricos de Winsock usan orden de red (big-endian), aunque el host x86/x64 use little-endian. Un formato puede mezclar órdenes: documenta el orden **por campo**.

En un esquema **TLV** (type, length, value), cada elemento indica tipo, longitud y valor. Confirma el ancho de tipo/longitud, si la longitud incluye el encabezado y cómo se representa un elemento desconocido.

## Ejemplo trabajado: formato sintético CLSF

*(Ejemplo **ilustrativo**, generado para la lección; no proviene de un archivo CLS.)* Supongamos un programa propio que escribe estos bytes:

~~~text
Offset  Bytes                                      Lectura provisional
00      43 4C 53 46                                 firma ASCII «CLSF»
04      01                                          versión candidata = 1
05      00                                          flags candidatos = 0
06      0C 00                                       tamaño de cabecera candidato = 12 (LE)
08      05 00                                       tamaño de cuerpo candidato = 5 (LE)
0A      2A 00                                       campo variable = 42 (LE)
0C      48 45 4C 4C 4F                              cuerpo ASCII «HELLO»
~~~

La muestra completa tiene 17 bytes. Es tentador llamar «secuencia» al campo en offset 0A, pero una sola muestra no lo justifica. Generamos variantes cambiando una cosa cada vez:

| Muestra | Cambios controlados | Observación |
|---|---|---|
| A | Cuerpo HELLO, campo 2A 00 | Longitud 5; total 17 bytes |
| B | Mismo cuerpo, campo 2B 00 | Solo cambia el campo en 0A; podría ser contador, ID o checksum |
| C | Cuerpo BYE!!, campo 2A 00 | Cambia solo el cuerpo; el campo 0A permanece |
| D | Cuerpo HELLO!!!, campo 2A 00 | Cuerpo crece tres bytes y el campo 08 pasa de 5 a 8 |

A y D apoyan la hipótesis «offset 08 es longitud del cuerpo» y que empieza en 0C. A/B/C sugieren que 0A no es un checksum simple del cuerpo, pero no identifican su significado. Solo al observar varias operaciones del programa propio —por ejemplo, que incrementa entre mensajes— podríamos etiquetarlo como contador. Cada etiqueta queda como hipótesis hasta probarla.

## Framing y máquina de estados

En un archivo, el inicio y final vienen dados por el archivo. En un protocolo hay que averiguar **dónde termina cada mensaje**:

- **Tamaño fijo:** cada mensaje tiene la misma longitud.
- **Longitud prefijada:** un encabezado anuncia cuántos bytes siguen; determina si cuenta desde el encabezado o solo el cuerpo.
- **Delimitador:** un byte o secuencia separa mensajes; prueba cómo se escapa si aparece en el cuerpo.
- **Estado o longitud implícita:** el final depende de una operación o fase del protocolo.

TCP es un flujo de bytes: los límites de una llamada send no son automáticamente límites de mensaje para quien recibe. El framing pertenece al protocolo de aplicación. Named pipes de Windows pueden operar en modo byte o mensaje; identifica el modo antes de interpretar lecturas, y documenta también la estructura interna definida por la aplicación.

~~~text
DESCONECTADO --conectar--> ESPERA_SALUDO
ESPERA_SALUDO --saludo válido--> LISTO
LISTO --petición--> ESPERA_RESPUESTA
ESPERA_RESPUESTA --respuesta/error--> LISTO
cualquier estado --cierre--> DESCONECTADO
~~~

El diagrama es una hipótesis hasta contrastarla con trazas de una ejecución propia. Anota estado previo, bytes, respuesta y efecto observable para cada transición.

## No confundir checksum, hash, MAC, compresión y cifrado

- **Checksum/CRC:** detecta ciertas corrupciones accidentales; no autentica al emisor.
- **Hash:** resumen de tamaño fijo; sin secreto no prueba quién creó el mensaje.
- **MAC:** etiqueta con clave compartida que permite verificar integridad/autenticidad bajo ese secreto.
- **Cifrado:** transforma datos usando una clave para ocultar contenido; no implica por sí mismo integridad.
- **Compresión:** transforma la representación para reducirla; firmas y cambios de tamaño dan pistas, pero entropía alta no prueba compresión ni cifrado.
- **Codificación:** cambia la representación (por ejemplo, base64 o UTF-16) sin ser cifrado.

Cambia un solo byte y compara el tráiler en muchas muestras. Después cambia una propiedad semántica y repite. Si no puedes validar una fórmula o identificar una llamada concreta en el programa propio, registra «campo no resuelto» en vez de adivinar CRC/AES.

## Práctica

En una VM, con **un escritor/parser propio** y, si eliges la rama de protocolo, dos procesos tuyos:

1. Genera al menos cuatro muestras con una sola variable distinta por par. Conserva originales y hashes.
2. Completa una tabla de offsets, ancho, orden de bytes, valor observado, hipótesis y confianza.
3. Identifica el framing y dibuja una máquina de estados para un intercambio local. Si usas named pipe, registra su modo byte/mensaje.
4. Investiga un posible tráiler variando un byte y el contenido; distingue qué puedes concluir y qué no sobre checksum, hash, MAC, cifrado o compresión.
5. Escribe un esquema breve y un parser de referencia para muestras válidas. Añade límites y casos malformados inocuos.
6. Reserva dos muestras para validación: predice sus offsets, longitudes y transiciones antes de abrirlas.

## Entregable

Un mini-informe con hashes, tabla de campos/offsets, diagrama de estados si es protocolo, esquema, pruebas, hipótesis refutadas y límites. Marca cada campo como **confirmado**, **probable** o **sin resolver**, con su evidencia.

## Preguntas de repaso

?? ¿Por qué un mensaje TCP no termina necesariamente donde terminó la llamada send?
!! TCP entrega un flujo de bytes; el protocolo de aplicación define el framing. Los segmentos y llamadas de envío no garantizan los límites que verá cada lectura.

?? ¿Qué experimento ayuda a identificar un campo de longitud?
!! Cambiar solo el tamaño del cuerpo en varias muestras y comprobar si el campo cambia coherentemente y si cuenta encabezado o archivo completo.

?? ¿Que un tráiler cambie al modificar el cuerpo demuestra que es un CRC?
!! No. También podría ser hash, MAC, cifrado u otro campo dependiente del contenido. Hay que probar la hipótesis con más muestras y evidencia.

?? ¿Qué diferencia hay entre minimizar una muestra y confirmar un formato?
!! Minimizar reduce una entrada manteniendo un comportamiento o cobertura; confirmar exige que una hipótesis estructural prediga muestras independientes y casos límite.

:::{nota} Puerta de salida
Podés reconstruir un formato o protocolo propio desde muestras controladas: marcar campos y offsets, explicar endianness/longitudes/framing, dibujar estados cuando corresponda, separar transformaciones candidatas y validar el esquema con muestras reservadas. No hace falta adivinar todos los campos; sí declarar qué evidencia falta.
:::

## Fuentes

- Microsoft Learn: [Byte Ordering](https://learn.microsoft.com/en-us/windows/win32/winsock/byte-ordering-2), [Named Pipes](https://learn.microsoft.com/en-us/windows/win32/ipc/named-pipes), [Named Pipe Type, Read, and Wait Modes](https://learn.microsoft.com/en-us/windows/win32/ipc/named-pipe-type-read-and-wait-modes).
- IETF: [RFC 9293, Transmission Control Protocol (TCP)](https://www.rfc-editor.org/rfc/rfc9293).
- [Método de análisis](04-metodo.html), [IPC en Windows](2d-10-ipc.html) y [fuzzing/análisis simbólico](02-opt-fuzzing.html).

