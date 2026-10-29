---
title: "Etapa 4 · Reconocer criptografía y encoding en un binario"
description: "Identificar XOR, base64 y algoritmos conocidos por sus constantes y tablas en binarios de Windows, sin implementar criptografía."
etapa: "Etapa 4 · Práctica guiada"
---

# Reconocer criptografía y encoding en un binario

:::{aviso} De dónde sale esta lección
Este tema **no está en el corpus CLS**: es **conocimiento externo** que agregamos para completar la guía. Se incluye porque reconocer cripto y encoding es rutina en análisis de malware de Windows y en CTF. El enfoque es **defensivo y de identificación**: reconocer qué algoritmo hay, no implementar criptografía ni romperla.
:::

:::{nota} Objetivo de la lección
Al terminar vas a poder distinguir encoding de cifrado, reconocer un XOR y un base64 en un listado, e identificar algoritmos conocidos (AES, RC4, MD5/SHA, TEA, CRC32) por sus **constantes y tablas**.
:::

**Prerrequisitos:** instrucciones, flujo, método (Etapas 2 y 4). **Duración sugerida:** 3 horas.

## Encoding no es cifrado

Es la primera distinción, y la que más se confunde:

- **Encoding** (base64, hex, URL-encoding) transforma datos para transportarlos. **No tiene clave**: cualquiera lo revierte. Si algo está en base64, está "ofuscado", no "cifrado".
- **Cifrado** usa una **clave**. Sin la clave no se recupera el texto (salvo error de implementación).
- **Hashing** (MD5, SHA) es de **una sola vía**: no se "descifra". Se usa para comparar o verificar.

Para el análisis, la pregunta no es "¿cómo lo rompo?", sino "¿qué transformación es y con qué parámetros?".

## XOR: el disfraz más común

El XOR byte a byte contra una clave fija es el modismo número uno para esconder strings en malware:

```asm
loop:
    mov   al, [esi]
    xor   al, 0x5A        ; clave de 1 byte
    mov   [edi], al
    inc   esi
    inc   edi
    loop  loop
```

Señales de XOR:

- Un bucle corto con `xor` contra una constante o contra bytes de otra zona.
- Strings que **no aparecen** con `strings`/`Shift+F12` pero que el programa "tiene" (están XOR-eadas y se desXOR-ean en runtime).
- Datos en `.data` que parecen basura hasta que corre una rutina.

El XOR de 1 byte es trivial de deshacer (hay 255 claves posibles). Para análisis, muchas veces alcanza con un breakpoint **después** del bucle para leer el texto ya desXOR-eado en memoria, sin tocar el algoritmo.

## Base64: la tabla que lo delata

Base64 se reconoce por su **alfabeto** de 64 caracteres, que casi siempre aparece como un string en `.rdata`:

```text
ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/
```

Más el `=` de relleno. Si ves ese alfabeto (o una variante con `-_` en vez de `+/`, que es base64 "url-safe"), hay base64. Procesa de a **4 caracteres → 3 bytes**. Un alfabeto reordenado es base64 "custom": misma mecánica, otra tabla.

## Algoritmos conocidos: las constantes los delatan

Casi todos los algoritmos famosos tienen **constantes o tablas fijas**. Encontrarlas es identificar el algoritmo sin leer una sola instrucción de la rutina:

| Algoritmo | Qué buscar |
|---|---|
| **AES (Rijndael)** | La S-box, que empieza `63 7C 77 7B F2 6B 6F C5 30 01 67 2B …`; o las T-tables |
| **MD5** | Init `67452301 EFCDAB89 98BADCFE 10325476`; tabla de senos `D76AA478 …` |
| **SHA-1** | Init `67452301 EFCDAB89 98BADCFE 10325476 C3D2E1F0` |
| **SHA-256** | Init `6A09E667 BB67AE85 3C6EF372 …`; constantes `428A2F98 71374491 …` |
| **RC4** | Un arreglo de **256 bytes** inicializado `0,1,2,…,255` y un bucle de *swaps* (KSA/PRGA) |
| **TEA / XTEA** | La constante *delta* `0x9E3779B9` (número áureo) |
| **CRC32** | El polinomio `0xEDB88320` o una tabla de 256 entradas de 32 bits |
| **DES** | Tablas de permutación fijas (IP, S-boxes) |

Un bucle que recorre un arreglo de 256 bytes haciendo intercambios casi seguro es **RC4**. Cuatro valores `67452301…` juntos casi seguro son **MD5 o SHA-1**. No hace falta entender el algoritmo: alcanza con nombrarlo y buscar su especificación.

## Herramientas que automatizan el reconocimiento

- **FindCrypt / findcrypt-yara** (plugin de IDA/Ghidra): busca estas constantes y te dice qué algoritmo hay.
- **signsrch**: firmas de cientos de algoritmos.
- **CAPA** (Mandiant): identifica capacidades, incluida criptografía, por patrones.
- **YARA** con reglas de cripto: para clasificar muestras.
- **Detect It Easy / entropía**: una sección con entropía muy alta (cercana a 8 bits/byte) suele estar **cifrada o comprimida/empaquetada**; es una señal, no una prueba.

:::{nota} En Windows, muchas veces no hay que reconocer nada
Antes de pelear con una rutina de cripto, mirá los **imports**: si el programa usa la criptografía del sistema (CryptoAPI en `advapi32.dll` —`CryptEncrypt`, `CryptHashData`— o CNG en `bcrypt.dll` —`BCryptEncrypt`—), el algoritmo y la clave pasan por esas APIs. Un breakpoint en esas funciones te muestra los datos en claro sin reimplementar nada. El trabajo de reconocer constantes queda para cuando el programa trae su **propia** implementación embebida.
:::

## Un método de reconocimiento

1. Corré `strings` y FindCrypt/CAPA primero: muchas veces resuelven la identificación en segundos.
2. Si hay strings que "faltan", buscá un bucle con `xor` y poné un breakpoint después para leerlas en claro.
3. Si hay un alfabeto de 64 caracteres, es base64; mirá si es estándar o custom.
4. Si hay constantes de la tabla de arriba, nombrá el algoritmo y buscá su especificación.
5. Documentá **qué** algoritmo es y **con qué parámetros** (clave embebida, IV, tabla custom). No necesitás reimplementarlo para el informe.

:::{peligro} Marco de uso
Identificar criptografía para entender un programa, detectar malware o resolver un CTF es análisis legítimo. Usar esto para romper el cifrado de software o datos ajenos, o para producir malware, no entra en esta guía. El objetivo es **reconocer y documentar**, no vulnerar.
:::

:::{practica} Práctica
1. Escribí un programa propio que guarde una string XOR-eada con una clave de 1 byte y la desXOR-ee al arrancar. Analizalo: encontrá el bucle `xor` y leé la string en memoria después.
2. Meté el alfabeto base64 en un programa y comprobá que aparece como string en `.rdata`.
3. Bajá una implementación de referencia de MD5 (de código abierto), compilala y buscá las constantes `67452301…` en el binario con tu desensamblador.
4. Corré FindCrypt o CAPA sobre esos binarios propios y compará con lo que encontraste a mano.
:::

## Preguntas de repaso

?? ¿Cuál es la diferencia entre encoding y cifrado?
!! El encoding (base64, hex) no tiene clave y cualquiera lo revierte; el cifrado usa una clave y sin ella no se recupera el texto. El hashing, además, es de una sola vía.

?? ¿Cómo reconocés base64 en un binario?
!! Por su alfabeto de 64 caracteres (`A–Z a–z 0–9 + /`) en `.rdata` y el `=` de relleno; procesa de a 4 caracteres → 3 bytes.

?? Encontrás un arreglo de 256 bytes inicializado `0,1,2,…` y un bucle de intercambios. ¿Qué algoritmo es probable?
!! RC4 (su fase de inicialización, KSA).

?? Ves las constantes `67452301 EFCDAB89 98BADCFE 10325476`. ¿Qué sugieren?
!! MD5 o SHA-1 (comparten ese estado inicial). Hay que mirar el resto para distinguirlos.

## Antes de avanzar

Tenés que poder:

- Distinguir encoding, cifrado y hashing.
- Reconocer un XOR y un base64 en un listado.
- Identificar un algoritmo conocido por sus constantes/tablas.
- Usar FindCrypt/CAPA y la entropía como ayuda.

:::{nota} Puerta de salida
Si podés mirar un binario, decir "acá hay base64 y acá un XOR con clave de 1 byte, y esta tabla es la S-box de AES" y documentarlo, cumpliste el objetivo.
:::

## Fuentes de esta lección

- *Practical Malware Analysis* (Sikorski & Honig), capítulo de criptografía: XOR, base64 y reconocimiento de algoritmos.
- Proyectos **FindCrypt**, **signsrch** y **CAPA** (Mandiant) como referencia de firmas.
- Especificaciones públicas: FIPS 197 (AES), RFC 1321 (MD5), FIPS 180-4 (SHA), RFC 4648 (base64).

:::{nota} Capas de esta lección
**Conocimiento externo (agregado por esta edición):** todo el contenido (XOR, base64, constantes de algoritmos, CryptoAPI/CNG, herramientas). No proviene de CLS. **Recomendación editorial:** el método de reconocimiento y el encuadre defensivo.
:::
