---
title: "2.26 · Ofuscación por máquina virtual: dispatcher, bytecode y handlers"
description: "Reconocer un binario virtualizado (dispatcher, VPC, tabla de handlers y bytecode), entender la devirtualización a alto nivel y practicar sobre una mini-VM propia. No se desvirtualizan protectores comerciales."
etapa: "Etapa 2 · Desofuscación avanzada (2E)"
---

# Ofuscación por máquina virtual: dispatcher, bytecode y handlers

:::{nota} Objetivo de la lección
**Reconocer** un binario protegido por virtualización de código e identificar sus piezas (*dispatcher*, puntero de instrucción virtual, tabla de *handlers* y región de *bytecode*), y entender a alto nivel cómo se **devirtualiza**. La práctica es sobre una **mini-VM propia**. **Prerrequisitos:** ofuscación nativa ([2.10](02-ofuscacion.html)) y ejecución simbólica ([2.25](02-simbolico-desofuscacion.html)).
:::

:::{peligro} Límite declarado
Esta lección enseña a **reconocer y entender** la virtualización. **No** se desvirtualizan protectores comerciales (VMProtect, Themida/WinLicense) ni se practica sobre software ajeno: eso queda [fuera de alcance](05-fuera-de-alcance.html). Se practica sobre una VM didáctica que vos mismo escribís.
:::

## Qué es virtualizar código

En vez de proteger el x86 original, el protector lo **traduce a un bytecode propio** —un juego de instrucciones inventado, distinto en cada binario— y embebe un **intérprete** que lo ejecuta. El resultado: cuando abrís la función en IDA/Ghidra, el x86 original **ya no está**; lo que ves es el intérprete corriendo un «programa» que no entendés, porque su lenguaje es secreto (**conocimiento externo**). Es la protección nativa más dura que vas a cruzar.

## Anatomía de una VM de protección

- **Bytecode:** una región de datos (a menudo cifrada) con el «programa» virtual.
- **VIP** (*virtual instruction pointer*): puntero al bytecode; hace de «EIP» de la VM.
- **VSP** (*virtual stack pointer*): la VM suele ser de pila; opera sobre su propio stack.
- **Contexto virtual:** un bloque de memoria con los «registros» virtuales.
- **VMEnter / VMExit:** al entrar, guarda los registros nativos (típico `pushad`/`pushfd`); al salir, los restaura. Marca la frontera entre lo nativo y lo virtual.
- **Dispatcher:** el gran bucle *fetch → decode → dispatch*: lee el opcode que apunta el VIP y salta al handler que lo implementa, normalmente por una **tabla** (salto indirecto).
- **Handlers:** muchas rutinas chicas, una por operación virtual (sumar, xor, cargar, saltar…). Terminan volviendo al dispatcher.

## Cómo reconocerla (las señales)

1. Un **bucle central enorme** con un **salto indirecto** a una tabla de direcciones.
2. **Muchos bloques pequeños** parecidos entre sí, todos terminando en el mismo lugar (vuelta al dispatcher): son los handlers.
3. Un **guardado masivo de contexto** al entrar y restaurarlo al salir (frontera VMEnter/VMExit).
4. Una **región de datos** que se recorre con un puntero que solo avanza (el VIP sobre el bytecode).
5. El *decompiler* produce algo gigante y sin sentido para una función que debería ser corta.

:::{aviso} Si no ves un despachador central: *threaded code*
No todas las VM convergen en un único `switch`. En protectores agresivos (VMProtect, Tigress en modo duro) se usa *indirect threading*: **cada handler termina con su propio *fetch*** del siguiente opcode y **salta directo al siguiente handler** (`jmp [tabla_handlers + rbx*8]`), sin volver a un despachador común. Si en IDA no aparece un bucle que converja en un solo bloque, buscá handlers encadenados que saltan de uno a otro por una tabla: también es una VM, solo que sin dispatcher central.
:::

## Devirtualizar: la idea, a alto nivel

No se «desvirtualiza con un botón». El flujo de trabajo de investigación es:

1. **Ubicar** el dispatcher y la tabla de handlers; aislar la frontera VMEnter/VMExit.
2. **Trazar** una corrida (con DBI, [2.29](02-dbi-dynamorio-pin.html), o Triton) para ver qué handlers se ejecutan y en qué orden.
3. **Dar semántica** a cada handler: qué operación x86 equivale (este suma, este hace xor, este salta).
4. **Levantar** la traza a una IR (Triton/Miasm) y **simplificar** (deshacer MBA con el solver, [2.25](02-simbolico-desofuscacion.html)), hasta recuperar la lógica original.

Es trabajoso y específico de cada VM. Para aprender el mecanismo —sin tocar un protector comercial— lo mejor es construir y analizar una VM propia.

## Ejemplo paso a paso: una mini-VM didáctica

*(Ejemplo **ilustrativo**: VM propia en C para ver el patrón *fetch-decode-dispatch*, no un volcado de un protector.)*

```c
// mini_vm.c — intérprete de un bytecode propio (didáctico)
enum { OP_SET=1, OP_XOR, OP_ADD, OP_CMP, OP_JNZ, OP_HALT };

// "programa" virtual: SET acc,0x41 ; XOR acc,0x23 ; CMP acc,0x62 ; HALT
unsigned char bytecode[] = { OP_SET,0x41,  OP_XOR,0x23,  OP_CMP,0x62,  OP_HALT };

int vm(unsigned char *vip) {       // vip = puntero de instrucción virtual
    int acc = 0, zf = 0;
    for (;;) {
        unsigned char op = *vip++;         // FETCH
        switch (op) {                       // DECODE + DISPATCH (la tabla)
            case OP_SET: acc  = *vip++;              break;   // handler SET
            case OP_XOR: acc ^= *vip++;              break;   // handler XOR
            case OP_ADD: acc += *vip++;              break;   // handler ADD
            case OP_CMP: zf   = (acc == *vip++);     break;   // handler CMP
            case OP_JNZ: { char d=*vip++; if(!zf) vip+=d; } break;
            case OP_HALT: return acc;                          // VMExit
        }
    }
}
```

Reconocé las piezas: `vip` es el VIP, el `for(;;)` + `switch` es el **dispatcher**, cada `case` es un **handler** y `bytecode[]` es el programa virtual. Un protector real tiene handlers cifrados, decenas de operaciones, el bytecode ofuscado y la frontera VMEnter/VMExit con `pushad`; pero el **esqueleto es este**. Si lo compilás y lo abrís en IDA, vas a ver el bucle con el salto a tabla: esa es la huella que hay que aprender a reconocer.

## Práctica

En tu VM, sobre tu **propia** mini-VM:

1. Compilá `mini_vm.c` y abrilo en IDA/Ghidra; señalá el dispatcher, la tabla de saltos y la región de bytecode.
2. Agregá dos operaciones nuevas (p. ej. `OP_SHL` y `OP_SUB`) y mirá cómo crece la tabla de handlers.
3. A partir del binario (sin mirar el fuente), **reconstruí el programa virtual**: qué hace cada opcode y qué calcula `bytecode[]`.
4. Escribí en dos renglones por qué un *decompiler* no puede recuperar la lógica original mirando solo el intérprete.

## Preguntas de repaso

?? ¿Qué le pasó al x86 original cuando una función está virtualizada?
!! Se **tradujo a un bytecode propio** del protector y se reemplazó por un **intérprete** que lo ejecuta. El x86 original ya no aparece en el listado; ves el intérprete corriendo un «programa» en un lenguaje secreto.

?? Nombrá tres piezas de una VM de protección.
!! **Dispatcher** (el bucle fetch-decode-dispatch), **tabla de handlers** (una rutina por operación virtual), **VIP** (puntero al bytecode). También VSP, contexto virtual y la frontera VMEnter/VMExit.

?? ¿Cuál es la señal más característica en el listado?
!! Un **bucle central** con un **salto indirecto a una tabla** y **muchos handlers chicos** que vuelven todos al mismo punto. Más el guardado masivo de contexto al entrar.

?? ¿Por qué no se «desvirtualiza con un botón»?
!! Porque el juego de instrucciones es **distinto en cada binario**. Hay que darle semántica a cada handler, trazar una corrida, levantar a IR y simplificar. Es trabajo específico de cada VM.

?? ¿Dónde queda la línea de lo que se practica?
!! Sobre una **VM propia** y para **reconocer** la técnica en general. Desvirtualizar protectores comerciales o software ajeno está **fuera de alcance**.

:::{nota} Puerta de salida
Podés: (1) explicar qué significa virtualizar código y por qué desaparece el x86 original; (2) identificar dispatcher, tabla de handlers, VIP y bytecode en tu mini-VM; (3) listar las señales de virtualización en un listado; (4) describir el flujo de devirtualización a alto nivel (trazar → dar semántica → levantar → simplificar).
:::

## Fuentes de esta lección

- [Rolles, «Unpacking Virtualization Obfuscators» (USENIX WOOT 2009)](https://www.usenix.org/legacy/events/woot09/tech/full_papers/rolles.pdf) — anatomía dispatcher/handlers y estrategia de devirtualización (conocimiento externo).
- [tigress.wtf](https://tigress.wtf/) — obfuscador académico (Collberg) que incluye virtualización; sirve para generar muestras propias de estudio.
- [Triton](https://triton-library.github.io/) y [Miasm](https://github.com/cea-sec/miasm) — *lifting* y simplificación de trazas.
- [2.10 Ofuscación nativa](02-ofuscacion.html) y [2.25 Simbólico](02-simbolico-desofuscacion.html) — el aplanamiento de flujo y el solver que se usan al simplificar.

:::{nota} Capas de esta lección
**Contenido observado en CLS:** la ofuscación nativa de 2.10 como escalón previo. **Conocimiento externo (agregado por esta edición):** la arquitectura de las VM de protección y el flujo de devirtualización, basados en literatura pública. **Recomendación editorial:** la mini-VM, los ejemplos y la práctica son ilustrativos; no se analizó ningún protector comercial.
:::
