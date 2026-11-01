---
title: "4.6 · Protocolos de terceros: reconstruir un protocolo propietario"
description: "Reconstruir un protocolo de red propietario a partir de capturas y del reversing del cliente: framing, serialización (TLV/Protobuf), correlación con hooks en send/recv y un disector de Wireshark. Solo sistemas propios o autorizados."
etapa: "Etapa 4 · Práctica guiada"
---

# Protocolos de terceros: reconstruir un protocolo propietario

:::{nota} Objetivo de la lección
Reconstruir un **protocolo de red propietario** combinando **capturas** de tráfico y el **reversing del cliente**: descubrir el *framing*, la serialización y la máquina de estados, y documentarlo con un **disector de Wireshark**. **Prerrequisitos:** reconstruir formatos y protocolos ([formatos y protocolos](04-formatos-protocolos.html)), ofuscación ([2.10](02-ofuscacion.html)), scripting/Frida ([2.21](02-scripting-debugger.html)) y simbólico ([2.25](02-simbolico-desofuscacion.html)).
:::

:::{peligro} Solo sistemas propios o autorizados
Interceptar o descifrar tráfico de servicios ajenos sin permiso es ilegal. Esta lección se practica con un **cliente/servidor propio** o en un entorno con **autorización explícita**. No se reconstruyen protocolos para eludir controles de acceso ni para atacar servicios de terceros.
:::

## De formatos a protocolos

En la lección de formatos reconstruiste un **formato de archivo**: bytes quietos en disco. Un **protocolo** agrega dos cosas: **tiempo** (los mensajes van y vienen en una secuencia) y **estado** (un *handshake*, una autenticación, un *keepalive*). Lo reconstruís cruzando **lo que ves en la red** con **lo que hace el binario** (**conocimiento externo**).

## 1 · Capturar y aislar

Con **Wireshark** aislás la conversación (por IP/puerto) y mirás la dirección de cada mensaje. Si el tráfico está **cifrado** (TLS), **no se rompe la cripto**: se obtienen las claves del **propio cliente** (variable `SSLKEYLOGFILE`, o un *hook* que vuelca el buffer antes de cifrar). Analizás el texto claro del lado que controlás, no el de un tercero.

## 2 · Framing: dónde empieza y termina un mensaje

TCP es un chorro de bytes; el protocolo define cómo cortarlo. Los tres patrones:

- **Prefijo de longitud:** los primeros 2–4 bytes dicen cuánto mide el resto (el más común).
- **Delimitador:** un byte/secuencia marca el fin (p. ej. `\n`).
- **Tamaño fijo:** cada mensaje mide lo mismo.

## 3 · Serialización: cómo se empaquetan los campos

- **TLV** (*type-length-value*): un byte de tipo, una longitud y el valor. Muy frecuente y fácil de reconocer.
- **Protobuf sin `.proto`:** se reconstruye el esquema con `protobuf-inspector` (los *field numbers* y *wire types* se infieren de los bytes).
- **MessagePack / JSON / binario a medida:** cada uno con su huella.

## 4 · Correlación tráfico ↔ binario (el paso clave)

El salto de calidad es **enganchar la capa de aplicación**, no la red: poné *breakpoints* o *hooks* en `send`/`recv`/`WSASend`/`WSARecv` y mirá el buffer **antes de cifrar** (en el `send`) y **después de descifrar** (en el `recv`). Así ves el mensaje en claro y, subiendo por la pila de llamadas, **qué función lo arma**: ahí está la estructura real del protocolo.

## 5 · Máquina de estados y documentar

Con varios mensajes ordenás la secuencia: *handshake* → auth → comandos → cierre. Para **validar** tu reconstrucción, escribís un **disector de Wireshark en Lua**: si colorea bien los campos de capturas nuevas, entendiste el protocolo.

## Ejemplo paso a paso: un protocolo TLV propio

*(Ejemplo **ilustrativo**: cliente/servidor propio; hook y disector de referencia.)*

```javascript
// volcar.js — ver el mensaje EN CLARO antes de que el cliente PROPIO lo mande
Interceptor.attach(Module.getExportByName('ws2_32.dll', 'send'), {
  onEnter(args) {
    const buf = args[1], len = args[2].toInt32();
    console.log(hexdump(buf, { length: len }));   // tipo | longitud | valor
  }
});
```

```lua
-- miproto.lua — disector de Wireshark para el TLV propio
local p = Proto("miproto", "Mi protocolo TLV")
local f_tipo = ProtoField.uint8 ("miproto.tipo", "Tipo")
local f_len  = ProtoField.uint16("miproto.len",  "Longitud")
local f_val  = ProtoField.bytes ("miproto.val",  "Valor")
p.fields = { f_tipo, f_len, f_val }

function p.dissector(buf, pinfo, tree)
  pinfo.cols.protocol = "MIPROTO"
  local t   = tree:add(p, buf())
  -- OJO endianness: un struct C nativo en x86/x64 escribe la longitud en LITTLE-endian (05 00 = 5).
  -- En Lua, :uint()/:add() leen BIG-endian (05 00 = 1280) -> usá :le_uint()/:add_le().
  -- Si el cliente usa htons() (network byte order = big-endian), entonces sí van :uint()/:add().
  local len = buf(1,2):le_uint()
  t:add(f_tipo, buf(0,1))
  t:add_le(f_len,  buf(1,2))
  t:add(f_val,  buf(3, len))
end
DissectorTable.get("tcp.port"):add(9000, p)   -- puerto de TU servidor
```

El *hook* te muestra el mensaje en claro (tipo, longitud, valor) **antes** de que salga a la red; el disector formaliza esa estructura y la valida contra capturas nuevas. Cuando Wireshark colorea «Tipo = 3, Longitud = 12, Valor = …» en tus capturas, documentaste el protocolo.

:::{nota} TCP fragmenta: pedile a Wireshark que reensamble
Un mensaje TLV puede llegar partido en varios segmentos TCP (o varios mensajes en un mismo segmento). Si el disector lee `buf(3, len)` y el buffer todavía no está completo, falla. La solución estándar es decirle a Wireshark que **espere el resto** con `pinfo.desegment_len` y `pinfo.desegment_offset`:

```lua
function p.dissector(buf, pinfo, tree)
  if buf:len() < 3 then                       -- falta el encabezado tipo+longitud
    pinfo.desegment_len = DESEGMENT_ONE_MORE_SEGMENT
    return
  end
  local total = 3 + buf(1,2):le_uint()        -- tipo(1)+len(2)+valor; le_uint = struct C little-endian
  if buf:len() < total then                   -- falta parte del valor
    pinfo.desegment_len = total - buf:len()   -- cuántos bytes más esperar
    pinfo.desegment_offset = 0                -- re-disectar desde el inicio
    return
  end
  -- acá el mensaje ya está completo: armás el árbol como antes
end
```
:::

## Práctica

En tu VM, con un **cliente/servidor propio**:

1. Escribí un cliente/servidor con un protocolo TLV simple (tipo + longitud + valor) y capturá una sesión con Wireshark.
2. Deducí el **framing** solo mirando los bytes (¿prefijo de longitud?).
3. Enganchá `send` con Frida y confirmá la estructura desde el lado del binario; subí la pila para ver qué función arma el mensaje.
4. Escribí el disector Lua y validalo contra una captura nueva; documentá la máquina de estados (handshake → comandos).

## Preguntas de repaso

?? ¿Qué agrega un protocolo frente a un formato de archivo?
!! **Tiempo** (mensajes en secuencia) y **estado** (handshake, auth, keepalive). No alcanza con leer bytes quietos: hay que entender el orden y las transiciones.

?? Si el tráfico está cifrado, ¿qué hacés (y qué no)?
!! **No** se rompe la cripto. Se obtienen las claves del **propio cliente** (`SSLKEYLOGFILE` o un hook que vuelca el buffer antes de cifrar) y se analiza el lado que controlás, con autorización.

?? ¿Cuáles son los tres patrones de framing?
!! **Prefijo de longitud** (el más común), **delimitador** (un byte/secuencia de fin) y **tamaño fijo**. Definen cómo se corta el chorro de bytes de TCP en mensajes.

?? ¿Por qué enganchar `send`/`recv` y no la red?
!! Porque en esa capa el mensaje está **en claro** (antes de cifrar / después de descifrar) y, subiendo por la pila, encontrás **qué función lo arma**: ahí está la estructura real del protocolo.

?? ¿Cómo validás que entendiste el protocolo?
!! Escribís un **disector de Wireshark** (Lua): si colorea correctamente los campos de **capturas nuevas** que no usaste para deducirlo, tu reconstrucción es correcta.

:::{nota} Puerta de salida
Podés: (1) aislar una conversación y describir su framing; (2) identificar la serialización (TLV/Protobuf/…); (3) correlacionar tráfico con el binario vía hooks en send/recv; (4) escribir un disector Lua que valide la estructura y documentar la máquina de estados —todo sobre sistemas propios o autorizados.
:::

## Fuentes de esta lección

- [Wireshark · Lua dissectors (WSDG)](https://www.wireshark.org/docs/wsdg_html_chunked/wsluarm.html) — `Proto`, `ProtoField`, `DissectorTable` (conocimiento externo).
- [github.com/mildsunrise/protobuf-inspector](https://github.com/mildsunrise/protobuf-inspector) — reconstruir Protobuf sin `.proto`.
- [frida.re/docs](https://frida.re/docs/) — hooks en `send`/`recv`/`WSASend` para ver el mensaje en claro.
- [Reconstruir formatos y protocolos](04-formatos-protocolos.html) — el formato de archivo del que parte esta ampliación.

:::{nota} Capas de esta lección
**Contenido observado en CLS:** la reconstrucción de formatos/protocolos de la Etapa 4 como base. **Conocimiento externo (agregado por esta edición):** framing, serialización, correlación con hooks de red y disectores de Wireshark. **Recomendación editorial:** ejemplos y práctica ilustrativos, sobre sistemas propios o autorizados.
:::
