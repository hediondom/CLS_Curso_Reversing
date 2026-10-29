---
title: "Curso IDA desde cero · índice de los 69 tutoriales"
description: "Qué enseña cada uno de los 69 tutoriales de IDA, con práctica, video afín y lección, y el texto extraído para leer offline."
---

# Curso «IDA desde cero» — índice de los 69 tutoriales

:::{nota} Qué es esto y cómo leerlo
Se **extrajo el texto y las 3.278 capturas** de los 69 tutoriales `.docx` del curso (en total ~122.397 palabras) y se armó este índice. 
Cada tute trae: **qué enseña** (síntesis leída de su apertura), la **práctica/target** que usa (dato observado en el texto), un **video afín** y la **lección** de esta guía con la que se conecta. Y el enlace **📖 Leer tutorial ilustrado**, que abre el tute completo como página (texto + las pantallas de IDA intercaladas + tiempo de lectura). Así no es solo texto: es un mapa de por dónde entrar.
:::

:::{aviso} Sobre el «video afín»
El curso IDA es **solo texto** (no tiene videos propios). El «▶ video afín» es del **mismo autor** (Ricardo Narvaja), de la serie «Reversing desde cero», que cubre el **mismo tema** pero con x64dbg/OllyDbg en vez de IDA. No es la grabación de ese tute: es el video que explica lo mismo. Lo abrís desde el [índice de videotutoriales](videos.html).
:::

:::{aviso} Alcance
La parte **base (tutes 1–28)** encaja en el recorrido de esta guía. De la **29 en adelante** es vulnerabilidades/exploiting y, de la 49, kernel: material avanzado de la Etapa 5, **defensivo**. No se enseña a atacar sistemas ajenos ni a vulnerar software comercial.
:::

## Tutes 1–13 · Base de IDA, assembly y primeras prácticas

En scope — Etapa 2.

**Se conecta con:** [Herramientas](guia/02-herramientas.html) · [IDA](guia/02-ida.html) · [Instrucciones](guia/02-instrucciones.html) · [Flujo](guia/02-flujo.html) · [Debugger](guia/02-debugger.html) · [Números](guia/01-numeros.html).

- **1 · Qué es IDA y el curso** — Presenta la serie (la versión en IDA del curso de OllyDbg): loader vs. debugger y cómo encarar Windows. · **📖 [Leer tutorial ilustrado](ida_tutes/1.html)** · *▶ video afín:* [«01 x64dbg primeros pasos»](videos.html) · {{src:CLS_Guia/_trabajo/extraido_ida/1-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|solo texto}} (1497 palabras)
- **2 · Sistemas de numeración** — Repaso base para arrancar de cero: binario, decimal, hexadecimal, bits y bytes. · **📖 [Leer tutorial ilustrado](ida_tutes/2.html)** · *▶ video afín:* [«03 Registros, Flags y Números»](videos.html) · {{src:CLS_Guia/_trabajo/extraido_ida/2-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|solo texto}} (1463 palabras)
- **3 · El LOADER de IDA** — El analizador estático: recorrer sus partes y las primeras instrucciones de transferencia. · **📖 [Leer tutorial ilustrado](ida_tutes/3.html)** · *Práctica:* `CRACKME.EXE`, `CRACKME.exe`, `DVCORE.dll` · *▶ video afín:* [«14 Conociendo IDA»](videos.html) · {{src:CLS_Guia/_trabajo/extraido_ida/3-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|solo texto}} (2214 palabras)
- **4 · Instrucciones de transferencia** — MOV/XCHG y cómo editar una instrucción en el loader (sobre el crackme de Cruehead). · **📖 [Leer tutorial ilustrado](ida_tutes/4.html)** · *Práctica:* `CRACKME.EXE`, `CRACKME.exe` · *▶ video afín:* [«04 Instrucciones 2»](videos.html) · {{src:CLS_Guia/_trabajo/extraido_ida/4-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|solo texto}} (1584 palabras)
- **5 · Más instrucciones** — Sigue con las instrucciones principales; su efecto se verá después en el debugger. · **📖 [Leer tutorial ilustrado](ida_tutes/5.html)** · *▶ video afín:* [«06 Instrucciones 3»](videos.html) · {{src:CLS_Guia/_trabajo/extraido_ida/5-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|solo texto}} (859 palabras)
- **6 · Aritméticas y lógicas** — ADD/SUB/AND/OR/XOR: operandos, registros y memoria. · **📖 [Leer tutorial ilustrado](ida_tutes/6.html)** · *Práctica:* `CRACKME.EXE` · *▶ video afín:* [«08 Instrucciones 4»](videos.html) · {{src:CLS_Guia/_trabajo/extraido_ida/6-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|solo texto}} (1328 palabras)
- **7 · Control de flujo** — Saltos condicionales e incondicionales y las comparaciones que los disparan. · **📖 [Leer tutorial ilustrado](ida_tutes/7.html)** · *▶ video afín:* [«09 Instrucciones 5»](videos.html) · {{src:CLS_Guia/_trabajo/extraido_ida/7-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|solo texto}} (1313 palabras)
- **8 · Trabajar en el loader** — Método de reversing estático: comentar y renombrar para entender sin ejecutar. · **📖 [Leer tutorial ilustrado](ida_tutes/8.html)** · *Práctica:* `crackme.exe`, `CRACKME.exe` · *▶ video afín:* [«15 Ejercicio 2 - Análisis estático»](videos.html) · {{src:CLS_Guia/_trabajo/extraido_ida/8-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|solo texto}} (1834 palabras)
- **9 · Práctica: crackme HOLA_REVERSER** — Primer análisis estático guiado de un crackme propio. · **📖 [Leer tutorial ilustrado](ida_tutes/9.html)** · *Práctica:* `HOLA_REVERSER.exe` · *▶ video afín:* [«15 Ejercicio 2 - Análisis estático»](videos.html) · {{src:CLS_Guia/_trabajo/extraido_ida/9-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|solo texto}} (1626 palabras)
- **10 · Loader + debugger** — Complementar estático y dinámico; IDA soporta varios debuggers. · **📖 [Leer tutorial ilustrado](ida_tutes/10.html)** · *▶ video afín:* [«07 Breakpoints»](videos.html) · {{src:CLS_Guia/_trabajo/extraido_ida/10-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|solo texto}} (1997 palabras)
- **11 · Bug de IDA 6.8** — Cómo detectar y mitigar el bug de esa versión (fixeado en 6.9). · **📖 [Leer tutorial ilustrado](ida_tutes/11.html)** · *Práctica:* `CRACKME.exe` · {{src:CLS_Guia/_trabajo/extraido_ida/11-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|solo texto}} (1305 palabras)
- **12 · Práctica: TEST_REVERSER** — Ejercicio propio sencillo para afianzar las instrucciones vistas. · **📖 [Leer tutorial ilustrado](ida_tutes/12.html)** · *Práctica:* `TEST_REVERSER.exe` · *▶ video afín:* [«16 Ejercicio 3 - Análisis Dinámico y Estático»](videos.html) · {{src:CLS_Guia/_trabajo/extraido_ida/12-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|solo texto}} (2208 palabras)
- **13 · Plugins de IDA** — Plugins útiles y cómo se usan (nota de compatibilidad 6.8/7.x). · **📖 [Leer tutorial ilustrado](ida_tutes/13.html)** · {{src:CLS_Guia/_trabajo/extraido_ida/13-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|solo texto}} (1996 palabras)

## Tutes 14–18 · Unpacking didáctico (UPX, ASPack), dump e IAT

Avanzado; packers didácticos, no protectores comerciales. El desempaquetado queda **fuera del recorrido base** de esta guía.

- **14 · Unpacking 1: UPX** — Desempacar un CRACKME comprimido con UPX y llegar al OEP. · **📖 [Leer tutorial ilustrado](ida_tutes/14.html)** · *Práctica:* `CRACKME.exe`, `PACKED_CRACKME.EXE`, `PACKED_CRACKME.exe` · *▶ video afín:* [«10 Unpacking 1 - UPX»](videos.html) · {{src:CLS_Guia/_trabajo/extraido_ida/14-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|solo texto}} (1832 palabras)
- **15 · Dump y reconstrucción de la IAT** — Dumpear y reconstruir la IAT con Scylla. · **📖 [Leer tutorial ilustrado](ida_tutes/15.html)** · *Práctica:* `Copy.exe`, `Copy_SCY.exe` · *▶ video afín:* [«17 Unpacking 3 - IAT Redirection»](videos.html) · {{src:CLS_Guia/_trabajo/extraido_ida/15-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|solo texto}} (1228 palabras)
- **16 · Unpacking ASPack 2.2** — Desempacar UnPackMe_ASPack 2.2 (packer didáctico, categoría sencilla). · **📖 [Leer tutorial ilustrado](ida_tutes/16.html)** · *▶ video afín:* [«13 Unpacking 2 - OEP»](videos.html) · {{src:CLS_Guia/_trabajo/extraido_ida/16-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|solo texto}} (1232 palabras)
- **17 · Resolver el ejercicio de unpacking** — Solución del UnPackMe pendiente. · **📖 [Leer tutorial ilustrado](ida_tutes/17.html)** · *Práctica:* `packed.exe`, `PACKED_PRACTICA_1.exe`, `packed_SCY.exe` · *▶ video afín:* [«13 Unpacking 2 - OEP»](videos.html) · {{src:CLS_Guia/_trabajo/extraido_ida/17-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|solo texto}} (1139 palabras)
- **18 · Reversear lo desempacado** — Analizar el ejecutable ya desempacado (crackme didáctico). · **📖 [Leer tutorial ilustrado](ida_tutes/18.html)** · {{src:CLS_Guia/_trabajo/extraido_ida/18-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|solo texto}} (1701 palabras)

## Tutes 19–24 · Crackmes, differ y ejercicios

En scope como práctica de análisis.

**Se conecta con:** [IDA](guia/02-ida.html) · [Llamadas y pila](guia/02-llamadas.html) · [Flujo](guia/02-flujo.html) · [Vulnerabilidades (defensivo)](guia/05-vulnerabilidades.html).

- **19 · Crackme de Cruehead** — Reversear el crackme clásico de Cruehead en el loader. · **📖 [Leer tutorial ilustrado](ida_tutes/19.html)** · *Práctica:* `wdsetup.exe` · *▶ video afín:* [«16 Ejercicio 3 - Análisis Dinámico y Estático»](videos.html) · {{src:CLS_Guia/_trabajo/extraido_ida/19-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|solo texto}} (1552 palabras)
- **20 · Qué es una vulnerabilidad** — Introducción al análisis de vulnerabilidades simples; qué es y cómo mirarla. · **📖 [Leer tutorial ilustrado](ida_tutes/20.html)** · *Práctica:* `Compilado_1.exe`, `Compilado_2.exe`, `Compilado_3.exe` · {{src:CLS_Guia/_trabajo/extraido_ida/20-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|solo texto}} (1493 palabras)
- **21 · ¿Vulnerable o no?** — Análisis del ejercicio: decidir si hay una vulnerabilidad real. · **📖 [Leer tutorial ilustrado](ida_tutes/21.html)** · *Práctica:* `NO_VULNERABLE.exe`, `VULNERABLE_o_NO.exe` · {{src:CLS_Guia/_trabajo/extraido_ida/21-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|solo texto}} (2013 palabras)
- **22 · Differ (comparar versiones)** — Qué es un differ y cómo empareja funciones entre dos versiones de un programa. · **📖 [Leer tutorial ilustrado](ida_tutes/22.html)** · *Práctica:* `IDA1.exe` · {{src:CLS_Guia/_trabajo/extraido_ida/22-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|solo texto}} (1385 palabras)
- **23 · Ejercicio IDA1.exe** — Función basada en EBP compilada con DevC++; resolverla. · **📖 [Leer tutorial ilustrado](ida_tutes/23.html)** · *Práctica:* `IDA1.exe`, `IDA2.exe` · *▶ video afín:* [«18 Funciones basadas en EBP vs basadas en ESP»](videos.html) · {{src:CLS_Guia/_trabajo/extraido_ida/23-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|solo texto}} (1518 palabras)
- **24 · Ejercicio IDA2 (cookies)** — Dos valores/cookies a comparar; soluciones de IDA2/3/4. · **📖 [Leer tutorial ilustrado](ida_tutes/24.html)** · *Práctica:* `IDA2.EXE`, `IDA2.exe`, `IDA3.exe` · *▶ video afín:* [«20 Ejercicio 4 - Análisis Estático»](videos.html) · {{src:CLS_Guia/_trabajo/extraido_ida/24-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|solo texto}} (721 palabras)

## Tutes 25–28 · Estructuras en IDA

En scope.

**Se conecta con:** [IDA](guia/02-ida.html) · [Memoria](guia/01-memoria.html).

- **25 · Estructuras en IDA (1)** — Cómo ayuda IDA cuando el programa usa estructuras. · **📖 [Leer tutorial ilustrado](ida_tutes/25.html)** · *Práctica:* `pepe.exe` · *▶ video afín:* [«23 Ejercicio con Estructuras (con símbolos)»](videos.html) · {{src:CLS_Guia/_trabajo/extraido_ida/25-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|solo texto}} (2362 palabras)
- **26 · Estructuras en IDA (2)** — Por qué agrupar datos en estructuras y cómo aplicarlo en IDA. · **📖 [Leer tutorial ilustrado](ida_tutes/26.html)** · *Práctica:* `ConsoleApplication4.exe`, `IDA_STRUCT.7z` · *▶ video afín:* [«23 Ejercicio con Estructuras (con símbolos)»](videos.html) · {{src:CLS_Guia/_trabajo/extraido_ida/26-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|solo texto}} (1569 palabras)
- **27 · Solución IDA_STRUCT** — Resolver el ejercicio de estructuras con símbolos. · **📖 [Leer tutorial ilustrado](ida_tutes/27.html)** · *Práctica:* `ConsoleApplication4.exe`, `IDA_STRUCT.7z` · *▶ video afín:* [«23 Ejercicio con Estructuras (con símbolos)»](videos.html) · {{src:CLS_Guia/_trabajo/extraido_ida/27-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|solo texto}} (2280 palabras)
- **28 · Teoría de repaso** — Temas teóricos variados intercalados entre ejercicios. · **📖 [Leer tutorial ilustrado](ida_tutes/28.html)** · *Práctica:* `EJEMPLO1.exe`, `EJEMPLO2.EXE` · {{src:CLS_Guia/_trabajo/extraido_ida/28-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|solo texto}} (2169 palabras)

## Tutes 29–48 · Vulnerabilidades y exploiting en user-mode (VLC/CVE, DEP, Mona, canary/SEH, shellcode, heap)

Etapa 5, **defensivo-avanzado**: la guía cubre el defecto y las mitigaciones de forma conceptual y defensiva, no la construcción de exploits.

**Se conecta con:** [Vulnerabilidades (defensivo)](guia/05-vulnerabilidades.html).

- **29 · Programas reales y CVE** — Pasar de crackmes a software real; propone un CVE para practicar. · **📖 [Leer tutorial ilustrado](ida_tutes/29.html)** · *Práctica:* `CVE-2008-4654` · {{src:CLS_Guia/_trabajo/extraido_ida/29-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|solo texto}} (221 palabras)
- **30 · VLC · CVE-2008-4654** — Diff de dos versiones de VLC guiado por el CVE. · **📖 [Leer tutorial ilustrado](ida_tutes/30.html)** · *Práctica:* `libty_plugin.dll`, `CVE-2008-4654` · {{src:CLS_Guia/_trabajo/extraido_ida/30-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|solo texto}} (2353 palabras)
- **31 · Explicación de la solución del CVE** — Aclara los puntos del buffer overflow del caso VLC. · **📖 [Leer tutorial ilustrado](ida_tutes/31.html)** · *Práctica:* `BUFFER1.exe`, `BUFFER2.exe`, `libvlccore.dll` · {{src:CLS_Guia/_trabajo/extraido_ida/31-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|solo texto}} (2411 palabras)
- **32 · WinDbg + IDA** — Instalar y manejar WinDbg desde la interfaz de IDA. · **📖 [Leer tutorial ilustrado](ida_tutes/32.html)** · {{src:CLS_Guia/_trabajo/extraido_ida/32-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|solo texto}} (775 palabras)
- **33 · Plugins de WinDbg + Mona** — Instalar Mona y plugins de WinDbg standalone. · **📖 [Leer tutorial ilustrado](ida_tutes/33.html)** · {{src:CLS_Guia/_trabajo/extraido_ida/33-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|solo texto}} (570 palabras)
- **34 · Explotación y mitigaciones** — Arranca ejecución de código e introduce DEP y otras protecciones. · **📖 [Leer tutorial ilustrado](ida_tutes/34.html)** · *Práctica:* `Mypepe.dll`, `NO_DEP.exe` · {{src:CLS_Guia/_trabajo/extraido_ida/34-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|solo texto}} (1583 palabras)
- **35 · DEP vs. sin DEP** — Compila con y sin DEP (SetProcessDEPPolicy) para comparar. · **📖 [Leer tutorial ilustrado](ida_tutes/35.html)** · *Práctica:* `DEP.exe`, `Mypepe.dll` · {{src:CLS_Guia/_trabajo/extraido_ida/35-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|solo texto}} (648 palabras)
- **36 · Solucionando DEP.exe** — Adaptar el script a la versión con DEP. · **📖 [Leer tutorial ilustrado](ida_tutes/36.html)** · *Práctica:* `DEP.exe`, `DEP.EXE` · {{src:CLS_Guia/_trabajo/extraido_ida/36-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|solo texto}} (1806 palabras)
- **37 · Mona en WinDbg** — Mismo ejemplo resuelto con Mona fuera de IDA. · **📖 [Leer tutorial ilustrado](ida_tutes/37.html)** · *Práctica:* `DEP.exe`, `mypepe.dll` · {{src:CLS_Guia/_trabajo/extraido_ida/37-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|solo texto}} (922 palabras)
- **38 · Canary y SEH** — Qué es el canary (stack cookie) y su relación con el SEH. · **📖 [Leer tutorial ilustrado](ida_tutes/38.html)** · *Práctica:* `CANARY_sin_DEP.exe` · *▶ video afín:* [«21 Excepciones 2»](videos.html) · {{src:CLS_Guia/_trabajo/extraido_ida/38-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|solo texto}} (1737 palabras)
- **39 · Canary + DEP pisando SEH** — Caso final: stack overflow con canary y DEP por SEH. · **📖 [Leer tutorial ilustrado](ida_tutes/39.html)** · *Práctica:* `agafi.exe`, `CANARY_con_DEP.EXE`, `CANARY_con_DEP.exe` · *▶ video afín:* [«21 Excepciones 2»](videos.html) · {{src:CLS_Guia/_trabajo/extraido_ida/39-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|solo texto}} (870 palabras)
- **40 · Shellcode** — Tipos de shellcode y su rol en el exploit (con nota de compatibilidad). · **📖 [Leer tutorial ilustrado](ida_tutes/40.html)** · {{src:CLS_Guia/_trabajo/extraido_ida/40-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|solo texto}} (843 palabras)
- **41 · Strings en stack y heap** — Ejemplo que ubica cadenas en stack vs. heap. · **📖 [Leer tutorial ilustrado](ida_tutes/41.html)** · {{src:CLS_Guia/_trabajo/extraido_ida/41-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|solo texto}} (1867 palabras)
- **42 · Ejercicios pendientes** — Resolución de los ejercicios dejados en la parte 41. · **📖 [Leer tutorial ilustrado](ida_tutes/42.html)** · *Práctica:* `Mypepe.dll` · {{src:CLS_Guia/_trabajo/extraido_ida/42-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|solo texto}} (1488 palabras)
- **43 · Solución práctica 41b** — Demangled names, new vs. malloc; primeros pasos de heap. · **📖 [Leer tutorial ilustrado](ida_tutes/43.html)** · *Práctica:* `mypepe.dll`, `PRACTICA41b.exe`, `ucrtbase.dll` · {{src:CLS_Guia/_trabajo/extraido_ida/43-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|solo texto}} (2070 palabras)
- **44 · WinDbg dentro de IDA (heap)** — Información de heap que se obtiene con WinDbg embebido. · **📖 [Leer tutorial ilustrado](ida_tutes/44.html)** · {{src:CLS_Guia/_trabajo/extraido_ida/44-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|solo texto}} (2432 palabras)
- **45 · Mona en PRACTICA41b** — Repasar el ejercicio con Mona en WinDbg. · **📖 [Leer tutorial ilustrado](ida_tutes/45.html)** · {{src:CLS_Guia/_trabajo/extraido_ida/45-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|solo texto}} (2309 palabras)
- **46 · Ejercicio parte 44 (heap)** — Consideraciones de los exploits de heap. · **📖 [Leer tutorial ilustrado](ida_tutes/46.html)** · *Práctica:* `Mypepe.dll`, `PRACTICA_44.7z` · {{src:CLS_Guia/_trabajo/extraido_ida/46-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|solo texto}} (2217 palabras)
- **47 · Más teoría de heap** — Aclara conceptos de heap sobre la práctica 44. · **📖 [Leer tutorial ilustrado](ida_tutes/47.html)** · *Práctica:* `PRACTICA_44.7z` · {{src:CLS_Guia/_trabajo/extraido_ida/47-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|solo texto}} (1250 palabras)
- **48 · LFH vs. heap estándar** — Seguir una alocación y ver dónde cae (LFH o heap estándar). · **📖 [Leer tutorial ilustrado](ida_tutes/48.html)** · {{src:CLS_Guia/_trabajo/extraido_ida/48-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|solo texto}} (2633 palabras)

## Tutes 49–69 · Kernel de Windows y temas avanzados (drivers, HackSys/HEVD, SSDT/syscalls, VA→física)

Avanzado, **fuera del recorrido base**. Material de explotación de kernel: se lista por completitud, no se desarrolla.

**Se conecta con:** [Fuera de alcance](guia/05-fuera-de-alcance.html).

- **49 · Cierre user-mode / rumbo a kernel** — Repaso de lo visto y anuncio de la rama de kernel. · **📖 [Leer tutorial ilustrado](ida_tutes/49.html)** · {{src:CLS_Guia/_trabajo/extraido_ida/49-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|solo texto}} (1339 palabras)
- **50 · Kernel de Windows: escenario** — Armar el entorno para reversear y debuggear kernel. · **📖 [Leer tutorial ilustrado](ida_tutes/50.html)** · *Práctica:* `jusched.exe`, `lsass.exe`, `lsm.exe` · {{src:CLS_Guia/_trabajo/extraido_ida/50-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|solo texto}} (4523 palabras)
- **51 · Drivers en kernel** — Compilar y reversear drivers propios para familiarizarse. · **📖 [Leer tutorial ilustrado](ida_tutes/51.html)** · {{src:CLS_Guia/_trabajo/extraido_ida/51-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|solo texto}} (1203 palabras)
- **52 · Estructuras de kernel** — Estructuras y mecanismos previos a la explotación. · **📖 [Leer tutorial ilustrado](ida_tutes/52.html)** · {{src:CLS_Guia/_trabajo/extraido_ida/52-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|solo texto}} (1884 palabras)
- **53 · IRP e IOCTL** — Reversear hasta el IOCTL code; la estructura IRP. · **📖 [Leer tutorial ilustrado](ida_tutes/53.html)** · {{src:CLS_Guia/_trabajo/extraido_ida/53-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|solo texto}} (744 palabras)
- **54 · Práctica driver + cliente Python** — Modificar el driver y hacer el cliente en user con Python. · **📖 [Leer tutorial ilustrado](ida_tutes/54.html)** · {{src:CLS_Guia/_trabajo/extraido_ida/54-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|solo texto}} (1034 palabras)
- **55 · Otro ejercicio de kernel** — Modificar un valor desde kernel evitando la pantalla azul. · **📖 [Leer tutorial ilustrado](ida_tutes/55.html)** · *Práctica:* `taskmgr.exe` · {{src:CLS_Guia/_trabajo/extraido_ida/55-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|solo texto}} (1633 palabras)
- **56 · HackSys vulnerable driver** — Driver con vulnerabilidades didácticas (HEVD) para estudiarlas. · **📖 [Leer tutorial ilustrado](ida_tutes/56.html)** · {{src:CLS_Guia/_trabajo/extraido_ida/56-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|solo texto}} (1703 palabras)
- **57 · HackSys: stack overflow** — Explotar el stack overflow del driver desde Python. · **📖 [Leer tutorial ilustrado](ida_tutes/57.html)** · {{src:CLS_Guia/_trabajo/extraido_ida/57-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|solo texto}} (1132 palabras)
- **58 · Shellcode de token (kernel)** — Shellcode que copia el token de un proceso system (se analiza). · **📖 [Leer tutorial ilustrado](ida_tutes/58.html)** · {{src:CLS_Guia/_trabajo/extraido_ida/58-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|solo texto}} (1142 palabras)
- **59 · Arbitrary overwrite** — Escritura arbitraria en el driver (método antiguo, XP/7). · **📖 [Leer tutorial ilustrado](ida_tutes/59.html)** · {{src:CLS_Guia/_trabajo/extraido_ida/59-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|solo texto}} (1099 palabras)
- **60 · HAL en kernel** — Script en Python basado en el código C del driver vulnerable. · **📖 [Leer tutorial ilustrado](ida_tutes/60.html)** · *Práctica:* `ntkrnlpa.exe` · {{src:CLS_Guia/_trabajo/extraido_ida/60-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|solo texto}} (2413 palabras)
- **61 · Integer overflow (kernel)** — Caso de integer overflow en el mismo driver. · **📖 [Leer tutorial ilustrado](ida_tutes/61.html)** · {{src:CLS_Guia/_trabajo/extraido_ida/61-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|solo texto}} (1299 palabras)
- **62 · Variante en Windows 10 x86** — La misma explotación del driver, ahora en Win10 de 32 bits. · **📖 [Leer tutorial ilustrado](ida_tutes/62.html)** · *Práctica:* `ntoskrnl.exe`, `x86.exe` · {{src:CLS_Guia/_trabajo/extraido_ida/62-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|solo texto}} (2742 palabras)
- **63 · Segmentación y paginación x86** — Manejo de memoria en x86 (y rumbo a 64 bits). · **📖 [Leer tutorial ilustrado](ida_tutes/63.html)** · {{src:CLS_Guia/_trabajo/extraido_ida/63-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|solo texto}} (1933 palabras)
- **64 · Desafío SCADA · CVE-2013-0657** — Reversear un CVE real propuesto en los grupos. · **📖 [Leer tutorial ilustrado](ida_tutes/64.html)** · *Práctica:* `dc.exe`, `CVE-2013-0657` · {{src:CLS_Guia/_trabajo/extraido_ida/64-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|solo texto}} (3630 palabras)
- **65 · Desafío Ekoparty 2018 (1)** — Reversear paso a paso el server de 64 bits del reto. · **📖 [Leer tutorial ilustrado](ida_tutes/65.html)** · {{src:CLS_Guia/_trabajo/extraido_ida/65-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|solo texto}} (5988 palabras)
- **66 · Desafío Ekoparty 2018 (2)** — Script en Python del exploit del reto. · **📖 [Leer tutorial ilustrado](ida_tutes/66.html)** · {{src:CLS_Guia/_trabajo/extraido_ida/66-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|solo texto}} (2318 palabras)
- **67 · HackSys pisando SEH (32-bit)** — Método para bypassear la cookie vía SEH. · **📖 [Leer tutorial ilustrado](ida_tutes/67.html)** · *Práctica:* `HackSysEVDExploit.exe`, `xxx.exe` · {{src:CLS_Guia/_trabajo/extraido_ida/67-INTRODUCCION AL REVERSING CON IDA PRO DESDE CERO.txt|solo texto}} (5246 palabras)
- **68 · SSDT y syscalls** — Resolver syscalls: a qué función de kernel saltan. · **📖 [Leer tutorial ilustrado](ida_tutes/68.html)** · *Práctica:* `ntkrnlmp.exe` · {{src:CLS_Guia/_trabajo/extraido_ida/68-SSDT Y COMO RESOLVEMOS LOS SYSCALLS.txt|solo texto}} (1868 palabras)
- **69 · VA → física a mano (64-bit)** — Traducir una dirección virtual a física manualmente. · **📖 [Leer tutorial ilustrado](ida_tutes/69.html)** · *Práctica:* `SkypeApp.exe` · {{src:CLS_Guia/_trabajo/extraido_ida/69-CONVERTIR DIRECCION VIRTUAL A FISICA A MANO.txt|solo texto}} (1101 palabras)
