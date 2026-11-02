# Fuentes, metodología y límites técnicos

**Edición Libre y Abierta · Revisión 5.4 (Ampliada)**

Este documento expone las fuentes técnicas, la metodología de redacción, la cobertura verificada y los límites pedagógicos y éticos de esta obra.

## 0. Alcance y enfoque técnico: Reversing en Windows

Esta obra cubre de manera exhaustiva el **reversing y análisis de binarios en sistemas Windows** (formato PE, arquitecturas x86 y x64). Otras plataformas como Linux/ELF, macOS/Mach-O, Android (APK/DEX) y arquitecturas como ARM/AArch64 quedan fuera del alcance principal por diseño pedagógico (ver `guia/05-fuera-de-alcance.html`), permitiendo profundizar en la arquitectura interna de Windows, el modelo de memoria del sistema y el desarrollo de drivers KMDF.

El curso integra un extenso cuerpo de conocimiento moderno: **punto flotante y SSE** (`guia/02-flotante.html`), **optimizaciones del compilador** (`guia/02-optimizaciones.html`), **reconocimiento de criptografía simétrica y asimétrica** (`guia/04-cripto.html`), **reversing de C++ moderno** (RTTI, SSO, layouts de smart pointers y std::function), **Windows Internals** (objetos del kernel, tokens, ALPC, RPC, servicios Win32, ETW y excepciones de 64 bits), **desofuscación simbólica** (angr, Triton, Z3), **análisis de máquinas virtuales y packers multicapa**, y **revisión estática y dinámica de drivers de modo kernel** (`guia/etapa-6.html`).

## 1. Naturaleza y evolución de esta obra

Esta obra es un **manual técnico integral, libre y autónomo** de ingeniería inversa en sistemas operativos Windows.

Si bien en sus etapas iniciales el proyecto tomó como punto de partida notas personales, resúmenes y recopilaciones procedentes de diversas comunidades y talleres de estudio clásicos en español, **la obra fue completamente reescrita, estructurada, corregida y expandida** mediante investigación técnica independiente, desarrollo de especímenes propios en C/C++ y documentación primaria oficial de acceso público en Internet.

La proporción de conceptos provenientes de aquellos apuntes embrionarios es hoy **ínfima** en comparación con el volumen masivo de análisis moderno en 64 bits, reversing de lenguajes como Go y Rust, disección de formatos binarios propietarios, mecanismos de evasión y call stack spoofing, arquitectura KMDF y plantillas de laboratorio compilables desarrolladas específicamente para esta obra.

La obra se publica y distribuye de forma **libre, abierta y anónima**, sin filiación con ninguna academia, empresa privada ni colectivo cerrado, como un aporte formativo de libre acceso para la comunidad hispanohablante de seguridad informática e ingeniería inversa.

## 2. Fuentes técnicas primarias y estándares abiertos

El contenido de esta obra se fundamenta directamente en fuentes técnicas oficiales, estándares abiertos y documentación primaria de la industria:

1. **Documentación oficial de Microsoft:**
   - *Microsoft Learn / MSDN:* especificación del formato PE/COFF (*Microsoft Portable Executable and Common Object File Format Specification*), API Win32/Windows SDK, arquitectura del Kernel de Windows, Windows Driver Frameworks (KMDF/UMDF), Driver Development Tools (WDK), Time Travel Debugging (TTD) y gestión de memoria virtual/heap.
   - *Windows Internals (Russinovich, Ionescu, Yosifovich):* conceptos arquitectónicos de objetos de sistema, procesos, hilos, LPC/ALPC y subsistemas.

2. **Especificaciones de arquitectura de procesador:**
   - *Intel 64 and IA-32 Architectures Software Developer's Manuals* (Volumes 1, 2, 3): codificación de instrucciones x86/x64, registros de propósito general y SIMD (SSE/AVX), modos de direccionamiento, flags, llamadas de sistema (`syscall`/`sysenter`) e interrupciones.
   - *AMD64 Architecture Programmer's Manual*: especificación y extensiones de 64 bits.

3. **Herramientas de ingeniería inversa y análisis:**
   - *Ghidra:* documentación oficial de la NSA, guía de desarrollo de extensiones, lenguaje SLEIGH y motor de descompilación.
   - *x64dbg:* documentación oficial, arquitectura de plugins y scripting condicional.
   - *angr / Z3 SMT Solver:* documentación técnica de angr (Symbolic Execution Engine) y especificaciones SMT-LIB2 / Theorem Prover de Microsoft Research.
   - *Frida Dynamic Binary Instrumentation:* documentación de la API JavaScript de Frida, Stalker engine y hooks en memoria.
   - *Scylla / pefile / Capstone / Keystone / Wireshark:* documentación y repositorios de código abierto.

4. **Compiladores y runtimes:**
   - *Microsoft Visual C++ (MSVC):* especificación de ABI x64, convenciones de llamada, estructuras de excepciones estructuradas (`.pdata`/`.xdata`), manejadores `__CxxFrameHandler3` y `__CxxFrameHandler4`, y optimizaciones de código.
   - *MinGW-w64 / GCC:* especificaciones de runtime GNU en Windows.
   - *Go & Rust:* especificaciones de runtime de Go (`pclntab`, ABIInternal) y RFCs de Rust (RFC 2603 para *v0 symbol mangling*).

5. **Influencias formativas clásicas:**
   - Reconocimiento histórico a los tutoriales didácticos y aportes docentes de pioneros del reversing en español (Ricardo Narvaja y Solid con «Reversing desde cero», Cayetano de Juan Úbeda con «MASM32 y OllyDbg», y Daniel Bermúdez en lógica de programación), cuyos primeros textos inspiraron los inicios de varias generaciones de analistas hispanohablantes.

## 3. Metodología didáctica y reproducibilidad

1. **Enfoque en binarios propios:** Todas las lecciones proponen prácticas basadas en programas fuente propios escritos en C/C++ o compilados en la VM de laboratorio. Esto garantiza que el alumno conozca la verdad subyacente del código antes de enfrentarse al desensamblador.
2. **Aislamiento en laboratorio:** El análisis dinámico y la experimentación se realizan en máquinas virtuales desconectadas de la red de host y configuradas con instantáneas (*snapshots*), garantizando un entorno seguro y reproducible.
3. **No elusión ni cracking:** La obra no incluye técnicas de elusión de protecciones comerciales, generación de licencias, piratería ni manipulación de software ajeno no autorizado. El estudio de protectores y ofuscación se aborda exclusivamente desde una perspectiva defensiva, taxonómica y sobre especímenes didácticos creados en laboratorio.

## 4. Qué se construyó a lo largo de las ediciones

### 4.1 Bloque 2B · Windows intermedio
7 lecciones que introducen el análisis de binarios reales:
- **2.10 Ofuscación nativa** · **2.11 TLS callbacks** · **2.12 MFC y mensajes de Windows**.
- **2.13 Huella de compilador** (MSVC, GCC/MinGW, Delphi, Go, Rust, Python con PyInstaller y Electron) · **2.14 PE fino** (Rich header, resolución dinámica de APIs, API Hashing, DllMain y sideloading) · **2.15 Técnicas anti-análisis y detección de Call Stack Spoofing** · **2.16 Ghidra práctico**.

### 4.2 Bloque 2C · Windows avanzado
5 lecciones de profundización técnica:
- **2.17 Packers y desempaquetado con Scylla** · **2.18 C++ profundo** (vtables, RTTI, SSO, unique_ptr, shared_ptr, std::function y excepciones x64) · **2.19 WinDbg, Heap y TTD** · **2.20 Patch diffing con Diaphora y BinDiff** · **2.21 Scripting y Frida**.

### 4.3 Rama 2D · Windows Internals y Etapa 6 · Kernel y Drivers KMDF
- **Rama 2D:** 13 lecciones completas sobre objetos y seguridad, PEB/TEB, registro, servicios Win32 nativos (`svclab_min.c`), tareas programadas, COM, DCOM/RPC, WMI, IPC (Named Pipes y ALPC con inspección en WinDbg), excepciones estructuradas (SEH, VEH y tablas `.pdata`/`UNWIND_INFO`) y ETW.
- **Etapa 6:** 6 lecciones sobre arquitectura del kernel de Windows, programación de drivers KMDF (`bloclab_kmdf_min.c`), depuración con WinDbg KDNET, revisión de seguridad en controladores y minifilters de sistema de archivos.

### 4.4 Bloque 2E — Desofuscación, arquitecturas y ecosistemas modernos (2.25–2.35), 4.6 y 6.7
- **2.25** Ejecución simbólica y concólica (angr, Triton, Miasm, solvers SMT Z3, simplificación de expresiones MBA).
- **2.26** Ofuscación basada en máquina virtual (VM-based: dispatcher, bytecode y handlers).
- **2.27** Reconocimiento de protectores multicapa comerciales (taxonomía de VMProtect, Themida, Enigma).
- **2.28** Neutralización de técnicas anti-análisis en laboratorio.
- **2.29** Instrumentación binaria dinámica (DBI) con DynamoRIO e Intel Pin.
- **2.30** Trazas dinámicas y cobertura de código con Frida Stalker.
- **2.31** Extensiones de Ghidra y modelado de arquitecturas con SLEIGH.
- **2.32** Reversing avanzado de binarios Go (slices, hmap, itab, concurrencia) y Rust (dyn Trait, async/await).
- **2.33** Análisis de ejecutables Visual Basic 6 en p-code y código nativo.
- **2.34** Desvirtualización práctica, lifting simbólico con Z3 y arquitecturas completas en SLEIGH (.slaspec, .cspec, .pspec, .ldefs).
- **2.35** Ecosistemas modernos en Windows 11: binarios híbridos ARM64EC, Windows Runtime (WinRT / IInspectable) y .NET Native AOT con JIT Hooking en clrjit.dll.
- **4.6** Protocolos de red propietarios de terceros (captura, hooks de sockets y disectores Lua en Wireshark).
- **6.7** Seguridad profunda en kernel x64: arquitectura VBS/HVCI (VTL0 vs VTL1, securekernel.exe, kCFG), auditoría de telemetría de kernel (PspCreateProcessNotifyRoutine, ObRegisterCallbacks, ETWti) en WinDbg y condiciones de carrera en MDLs.

## 5. Limitaciones declaradas

- La obra se enfoca exclusivamente en la arquitectura de sistemas operativos Windows x86 y x64.
- Las herramientas de depuración y desensamblado evolucionan continuamente; los menús y atajos descritos corresponden a las versiones estables utilizadas al momento de redacción.
- El análisis dinámico de binarios desconocidos exige un entorno de máquina virtual aislado y descartable con instantáneas limpias.

## 6. Atribución y Licencia Libre

Esta obra es un **manual libre, abierto e independiente**, desarrollado con propósitos pedagógicos, científicos y de investigación en seguridad informática defensiva.

Se reconoce y agradece con respeto la labor de todos los investigadores, docentes y creadores de software libre que han impulsado la disciplina del análisis binario y la ingeniería inversa en todo el mundo.

**Modelo de publicación:** Distribución libre, anónima y gratuita para fines educativos. Se permite su consulta, lectura y estudio sin restricciones.
