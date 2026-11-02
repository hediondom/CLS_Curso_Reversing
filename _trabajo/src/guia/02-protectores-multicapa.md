---
title: "2.27 · Protectores comerciales y packers multicapa: reconocer, no evadir"
description: "Identificar familias de protector (VMProtect, Themida, Enigma, ASProtect) y binarios multicapa por sus huellas, y planear el análisis sin producir unpack de software comercial."
etapa: "Etapa 2 · Desofuscación avanzada (2E)"
---

# Protectores comerciales y packers multicapa: reconocer, no evadir

:::{nota} Objetivo de la lección
**Identificar** qué familia de protector tiene un binario y reconocer una protección **multicapa** (packer sobre cifrado sobre VM), y **planear** un análisis seguro. **Prerrequisitos:** packers didácticos ([2.17](02-packers.html)), taxonomía anti-análisis ([2.15](02-anti-analisis.html)) y ofuscación por VM ([2.26](02-ofuscacion-vm.html)).
:::

:::{peligro} Encuadre legal y de alcance
Esta lección es de **reconocimiento**. **No** se desempaquetan protectores comerciales (Themida, WinLicense, VMProtect, Enigma, ACProtect) como práctica, ni se producen cracks, keygens o parches. La práctica usa **binarios propios** empaquetados con herramientas libres, o malware estudiado **en estático**. Desempaquetar protectores está [fuera de alcance](05-fuera-de-alcance.html).
:::

## Packer vs protector

Un **packer** comprime el ejecutable y lo descomprime en memoria al arrancar (su objetivo original era el tamaño). Un **protector** suma **capas de defensa**: cifrado, anti-debug, anti-VM, anti-dump, verificación de integridad y, en la gama alta, **virtualización** ([2.26](02-ofuscacion-vm.html)) de las funciones críticas. En 2.17 desempaquetaste un UPX propio llegando al **OEP** (*original entry point*); acá subimos de dificultad para **reconocer** lo que no vas a poder —ni deber— desempaquetar.

## Familias y sus huellas

| Familia | Tipo | Huellas típicas (conocimiento externo) |
|---|---|---|
| UPX | Packer | Secciones `UPX0`/`UPX1`, IAT mínima, alta entropía; se reconoce con `upx -t` |
| ASPack / PECompact | Packer | Secciones `.aspack`/`.adata`; stub chico |
| ASProtect | Protector | SEH como flujo, IAT redirigida, trucos de robo de código |
| Enigma / Obsidium | Protector | Licenciamiento, anti-debug fuerte, VM parcial |
| Themida / WinLicense | Protector | Anti-todo, virtualización pesada, nombres de sección aleatorios |
| VMProtect | Protector (VM) | Virtualización dominante, poco código nativo, sección de bytecode |
| .NET Reactor / ConfuserEx | Protector .NET | Nombres *mangled*, control-flow en IL, anti-tamper (ver [3.1](03-dotnet-runtime.html)) |

## Las capas de una protección dura

Un protector serio no es una capa, son varias apiladas:

1. **Compresión / cifrado del cuerpo:** el código real no está legible en disco (entropía alta, casi sin imports).
2. **Stub de arranque:** descifra/descomprime en memoria y reconstruye la IAT.
3. **Anti-análisis:** chequeos de debugger/VM/tiempo ([2.15](02-anti-analisis.html)) que abortan si te detectan.
4. **Anti-dump y anti-attach:** borran encabezados en memoria, falsean tamaños, detectan *attach*.
5. **Virtualización** de las rutinas críticas (licencia, checks): lo más duro de todo.

Por eso el **OEP** que en UPX era un salto limpio acá **no existe** como punto único: hay código robado, re-cifrado por tramos y funciones que nunca vuelven a ser x86 nativo. Reconocer esto es saber *cuándo parar*.

## Herramientas de reconocimiento

- **Detect It Easy (DIE):** identifica packer/protector/compilador por firmas y muestra la **entropía por sección**.
- **PE-bear:** inspección de secciones, encabezados y directorios sin ejecutar nada.
- **Entropía:** una sección con entropía ~7,9/8 es casi seguro comprimida o cifrada; una sección de código normal ronda 6–6,5.
- **Imports:** una IAT con solo `LoadLibrary`/`GetProcAddress` grita «empaquetado».

:::{nota} IAT vacía: *splicing* y emulación de APIs
Los protectores duros van más allá de redirigir la IAT: la dejan **vacía o con entradas ficticias** y reemplazan cada llamada a una API importada por un *stub* propio que **emula la API** o ejecuta la *syscall* directamente. Por eso una IAT casi inexistente en un binario que claramente usa el sistema (abre archivos, red, registro) no es un error de lectura: es la huella de que los imports se resuelven y se envuelven en runtime. Reconstruir esa tabla es parte de lo que hace difícil —y, en software comercial, fuera de alcance— el análisis.
:::

## Ejemplo paso a paso: leer las capas de un binario propio

*(Ejemplo **ilustrativo**: valores típicos de un binario propio empaquetado; no un volcado verificado.)*

```text
# empaquetar un binario PROPIO con una herramienta libre y mirar sus huellas
upx -9 hola_propio.exe                 # capa 1: compresión (didáctica)

# luego, con Detect It Easy en modo consola:
diec --entropy hola_propio.exe
# Sección   Entropía   Estado
# UPX0        0.00      (vacía en disco; se llena en memoria)
# UPX1        7.91      packed    <- alta: comprimida
# .rsrc       4.20      not packed

diec hola_propio.exe
# packer: UPX(4.x)[NRV,best]    <- identificación por firma
```

Qué leíste **sin ejecutar**: dos secciones con nombres de UPX, una vacía en disco y otra con entropía ~7,9 (comprimida), y la firma del packer. Si encima hubiera una **segunda capa** propia (p. ej. un XOR del cuerpo hecho por vos para practicar), DIE mostraría entropía alta en otra sección y **no** reconocería firma: esa es la pista de «multicapa / a medida». El **plan** de análisis se escribe antes de tocar nada: qué capa resuelvo primero, qué espero ver, dónde está el riesgo.

## Práctica

En tu VM, con binarios **propios**:

1. Compilá un «hola mundo» propio, empaquetalo con UPX e identificalo con DIE; anotá secciones y entropías.
2. Agregá una **segunda capa propia** (cifrá el cuerpo con un XOR en un stub que vos escribís) y volvé a medir: ¿qué cambió en la entropía y en la firma?
3. Tomá tres nombres de protector de la tabla y describí, de memoria, una huella de cada uno.
4. Escribí un **plan de análisis** de media página para un binario multicapa hipotético: orden de capas, qué herramienta en cada paso y en qué punto decidirías que está *fuera de alcance*.

## Preguntas de repaso

?? ¿Qué diferencia a un packer de un protector?
!! El packer **comprime** (y descomprime al arrancar). El protector agrega **capas de defensa**: cifrado, anti-debug/anti-VM, anti-dump, integridad y, en la gama alta, **virtualización** de funciones críticas.

?? ¿Por qué la entropía por sección es una buena primera pista?
!! Porque datos comprimidos o cifrados tienen entropía **cercana a 8**, mientras que el código normal ronda 6–6,5. Una sección en ~7,9 casi seguro está empaquetada o cifrada, y se ve **sin ejecutar** el binario.

?? En un protector duro, ¿por qué el OEP «no existe» como en UPX?
!! Porque hay **código robado**, re-cifrado por tramos y funciones **virtualizadas** que nunca vuelven a ser x86 nativo. No hay un salto único y limpio al código original como en un packer de compresión.

?? ¿Qué delata una IAT con casi solo `LoadLibrary`/`GetProcAddress`?
!! Que el binario **resuelve sus imports en runtime** (los reconstruye el stub tras descomprimir): señal clásica de empaquetado. La IAT «real» no está en el PE de disco.

?? ¿Dónde está el límite de esta lección?
!! En **reconocer e inventariar** la protección y **planear**. Desempaquetar protectores comerciales o software ajeno está fuera de alcance; la práctica es sobre binarios propios y malware en estático.

:::{nota} Puerta de salida
Podés: (1) distinguir packer de protector; (2) identificar una familia por sus huellas con DIE/PE-bear; (3) leer entropía e imports para sospechar empaquetado sin ejecutar; (4) enumerar las capas de una protección dura y escribir un plan de análisis que incluya *cuándo parar*.
:::

## Fuentes de esta lección

- [github.com/horsicq/Detect-It-Easy](https://github.com/horsicq/Detect-It-Easy) — identificación de packer/protector y entropía por sección (conocimiento externo).
- [github.com/hasherezade/pe-bear](https://github.com/hasherezade/pe-bear) — inspección estática de PE.
- [upx.github.io](https://upx.github.io/) — el packer libre que se usa para empaquetar binarios propios de práctica.
- [2.17 Packers didácticos](02-packers.html) — el OEP/dump/IAT sobre UPX propio, escalón previo.
- [2.15 Anti-análisis](02-anti-analisis.html) y [2.26 VM](02-ofuscacion-vm.html) — las capas de defensa que apila un protector.

:::{nota} Capas de esta lección
**Núcleo conceptual:** el desempaquetado didáctico de UPX (2.17) y la exclusión declarada de protectores comerciales en [Fuentes y límites](../fuentes_y_limites.html). **Conocimiento externo (agregado por esta edición):** la taxonomía de familias, sus huellas y las herramientas de reconocimiento. **Recomendación editorial:** los ejemplos y la práctica son ilustrativos y sobre binarios propios.
:::
