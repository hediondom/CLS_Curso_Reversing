---
title: "2.34 · Desvirtualización Práctica, Lifting Simbólico y Arquitecturas Completas en SLEIGH"
description: "Identificación de indirect threading en desensamblado x64, extracción de bytecode, lifting simbólico con Z3/Triton y especificación de procesadores virtuales en SLEIGH para Ghidra."
etapa: "Etapa 2 · Reversing (Bloque 2E: Técnicas avanzadas e industriales)"
---

# Desvirtualización Práctica, Lifting Simbólico y Arquitecturas Completas en SLEIGH

:::{nota} Propósito y Alcance
Esta lección profundiza operativamente los conceptos introducidos en las lecciones 2.25 y 2.26. Mientras que los cursos introductorios se limitan a mostrar bucles `switch-case` elementales, los protectores y máquinas virtuales reales en arquitecturas x64 evitan el bucle central mediante técnicas de **Indirect Threading** (despacho directo por tabla de punteros). Aprenderás a identificar esta firma en desensamblado, extraer la secuencia de handlers, levantar el bytecode a restricciones simbólicas con **Z3 / Triton** para simplificar expresiones MBA y compilar una especificación de arquitectura completa en **SLEIGH** (`.ldefs`, `.pspec`, `.cspec`, `.slaspec`) para que Ghidra descompile el bytecode a código C limpio.
:::

## 1. Arquitectura de Despacho: Switch Central vs. Indirect Threading

En un ofuscador elemental por VM, el grafo de flujo de control (CFG) exhibe un nodo dominante central con decenas de aristas salientes (un `switch` tradicional). En contraste, los virtualizadores industriales (como VMProtect, CodeVirtualizer o implementaciones propietarias) eliminan el bucle central utilizando **Indirect Threading** o **Direct Call Threading**.

### Firma en Desensamblado x64 (Indirect Threading)

En lugar de saltar hacia un nodo central para buscar el siguiente opcode, cada *handler* de la VM es responsable de leer el siguiente byte del flujo de instrucciones virtuales (`VIP`), indexar una tabla global de direcciones y transferir el control inmediatamente mediante un salto indirecto:

```nasm
; --- Handler OP_XOR en x64 ---
loc_handler_xor:
    movzx   eax, byte ptr [rsi]         ; RSI = Puntero de Instrucción Virtual (VIP). Lee operando inmediato.
    inc     rsi                         ; Avanza VIP al siguiente byte
    xor     r13b, al                    ; R13B = Acumulador Virtual (VACC). Ejecuta la semántica real.
    
    ; --- Dispatcher incrustado en el epílogo del handler ---
    movzx   eax, byte ptr [rsi]         ; Lee el siguiente Opcode de la VM
    inc     rsi                         ; Avanza VIP
    jmp     qword ptr [r12 + rax*8]     ; R12 = Puntero base a DispatchTable. Salto indirecto inmediato.
```

**Propiedades diagnósticas del Indirect Threading:**
1. **Ausencia de bucle dominante:** En IDA/Ghidra el CFG no tiene un nodo "estrella"; cada handler termina en un `jmp qword ptr [base + reg*8]` o en un gadget `ret` (ROP virtual).
2. **Registro fijado para la tabla:** El registro base (en el ejemplo, `R12`) se inicializa una sola vez en el prólogo de la VM y permanece invariable durante toda la ejecución.
3. **Puntero de instrucción virtual dedicado:** Un registro volátil (típicamente `RSI`, `RDI` o `RBX`) actúa como `VIP`, siendo incrementado en cada lectura de opcode u operando.

---

## 2. Pipeline Completo de Desvirtualización: Tracing, Taint y Lifting con Triton / Z3

El desmontaje de una máquina virtual compleja se estructura en un pipeline industrial de tres etapas:

```text
[ Binario VM ] 
      │
      ▼ (Etapa 1: Tracing Dinámico con Frida Stalker / DynamoRIO)
Secuencia de Handlers e Instrucciones Ejecutadas (RIP Trace)
      │
      ▼ (Etapa 2: Dynamic Taint Analysis y Lifting a AST con Triton)
Árbol de Sintaxis Abstracta (AST) de la Semántica Virtual
      │
      ▼ (Etapa 3: Simplificación de Identidades MBA y Resolución SMT con Z3)
Fórmula Aritmética Canónica Colapsada y Preimagen Despejada
```

### Etapa 1: Tracing Dinámico con Frida Stalker
Para registrar la secuencia exacta de handlers ejecutados sin desarmar estáticamente toda la tabla de saltos, se utiliza **Frida Stalker** interceptando las transferencias indirectas de control:

```javascript
// trace_vm_handlers.js — Rastreo de handlers en ejecución
Stalker.follow(Process.getCurrentThreadId(), {
    events: { call: false, ret: false, exec: false, block: false, compile: true },
    transform(iterator) {
        let instruction = iterator.next();
        do {
            // Si la instrucción es un salto indirecto por tabla (jmp [r12 + rax*8])
            if (instruction.mnemonic === "jmp" && instruction.opStr.includes("r12")) {
                iterator.putCallout(function(context) {
                    const opcode = context.rax.toInt32();
                    const vip = context.rsi;
                    console.log(`[VM Trace] VIP=${vip} -> Handler Opcode: ${opcode}`);
                });
            }
            iterator.keep();
        } while ((instruction = iterator.next()) !== null);
    }
});
```

### Etapa 2: Dynamic Taint Analysis y AST Simbólico con Triton (`solve_vm_triton.py`)
Una vez capturada la secuencia, el framework **Triton** permite marcar la memoria de entrada del usuario como *contaminada* (`tainted`) y ejecutar simbólicamente las instrucciones de los handlers. Triton propaga la contaminación a través de los registros del procesador y genera automáticamente el AST simbólico simplificado, descartando el código muerto del dispatcher de la VM:

```python
# solve_vm_triton.py — Taint dinámico y lifting con Triton
from triton import TritonContext, ARCH, MemoryAccess, CPUSIZE

ctx = TritonContext(ARCH.X86_64)
# 1. Contaminar el byte de entrada del usuario
ctx.symbolizeMemory(MemoryAccess(INPUT_ADDR, CPUSIZE.BYTE), "user_input")
ctx.setTaintMemory(MemoryAccess(INPUT_ADDR, CPUSIZE.BYTE), True)

# 2. Emulación simbólica de la semántica de handlers
# Triton resuelve automáticamente la contaminación sobre R13B (acumulador)
# y construye el AST combinando las operaciones XOR, ADD y la identidad MBA:
acc_ast = ctx.getSymbolicMemory(INPUT_ADDR).getAst()
acc_ast = acc_ast ^ ctx.getAstContext().bv(0x23, 8)
acc_ast = acc_ast + ctx.getAstContext().bv(0x07, 8)

# Identidad MBA: (acc ^ 0x5A) + 2*(acc & 0x5A)
y = ctx.getAstContext().bv(0x5A, 8)
acc_ast = (acc_ast ^ y) + (ctx.getAstContext().bv(2, 8) * (acc_ast & y))

# Restricción hacia la bifurcación de éxito (CMP 0x87)
condicion_exito = (acc_ast == ctx.getAstContext().bv(0x87, 8))
modelo = ctx.getModel(condicion_exito)
```

### Etapa 3: Lifting Directo a Z3 para Resolver Expresiones MBA

Cuando la máquina virtual ejecuta operaciones aritmético-lógicas entrelazadas con identidades **Mixed Boolean-Arithmetic (MBA)**, el análisis estático se vuelve intratable manualmente. Por ejemplo, la identidad:

$$\text{acc} = (\text{acc} \oplus y) + 2 \cdot (\text{acc} \land y)$$

equivale matemáticamente a la suma estándar $\text{acc} + y$.

### Script Operativo de Lifting Simbólico (`solve_minivm_z3.py`)

A partir del volcado del bytecode extraído del binario de laboratorio (`plantillas_codigo/vm_mba_crackme.c`), el siguiente script en Python utiliza el motor SMT **Z3** para interpretar la semántica de los handlers de forma simbólica, colapsar las identidades MBA y despejar la preimagen exacta de entrada que satisface el flag de éxito:

```python
# solve_minivm_z3.py — Lifting simbólico directo del bytecode de la VM
from z3 import BitVec, BitVecVal, Solver, sat

# Constantes de opcodes extraídas del binario
OP_SET, OP_XOR, OP_ADD, OP_CMP, OP_MBA, OP_HALT = 1, 2, 3, 4, 5, 6

# Secuencia de bytecode volcada de la sección .rdata
bytecode = [
    (OP_XOR, 0x23),
    (OP_ADD, 0x07),
    (OP_MBA, 0x5A),  # MBA: (acc ^ 0x5A) + 2*(acc & 0x5A) -> equivale a acc + 0x5A
    (OP_CMP, 0x87),  # Compara con resultado esperado
    (OP_HALT, 0)
]

s = Solver()
# Variable simbólica de 8 bits correspondiente al carácter de entrada
entrada = BitVec("entrada_usuario", 8)
acc = entrada

for op, imm in bytecode:
    if op == OP_SET:
        acc = BitVecVal(imm, 8)
    elif op == OP_XOR:
        acc = acc ^ imm
    elif op == OP_ADD:
        acc = acc + imm
    elif op == OP_MBA:
        y = BitVecVal(imm, 8)
        acc = (acc ^ y) + 2 * (acc & y)
    elif op == OP_CMP:
        s.add(acc == imm)  # Restricción hacia la rama exitosa (zf == 1)
    elif op == OP_HALT:
        break

if s.check() == sat:
    modelo = s.model()
    sol = modelo[entrada].as_long()
    print(f"[+] Entrada resuelta por Z3: {sol:#04x} (carácter: '{chr(sol)}')")
```

---

## 3. Especificación de Arquitectura Completa en SLEIGH para Ghidra

Para que el descompilador de Ghidra transforme el bytecode propietario en código C de alto nivel, se debe estructurar un módulo de lenguaje completo en `Ghidra/Processors/<Nombre>/data/languages/`:

### A. Definición de Lenguaje (`minivm.ldefs`)
Define el identificador único del procesador, su variante, tamaño de puntero y endianness:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<language_definitions>
    <language processor="MiniVM" endian="little" size="32" variant="default"
              version="1.0" slafile="minivm.sla" processorspec="minivm.pspec"
              id="MiniVM:LE:32:default">
        <description>Procesador Didáctico MiniVM (Lección 2.34)</description>
        <compiler name="default" id="default" cspec="minivm.cspec"/>
    </language>
</language_definitions>
```

### B. Especificación del Procesador (`minivm.pspec`)
Declara el registro que actúa formalmente como Contador de Programa (`VIP`):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<processor_spec>
    <programcounter register="vip"/>
</processor_spec>
```

### C. Especificación del Compilador / ABI (`minivm.cspec`)
Establece qué registros contienen los parámetros de entrada y retorno de funciones virtuales:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<compiler_spec>
    <default_proto>
        <prototype name="__stdcall" extrapop="unknown" stackshift="4">
            <input><pentry minsize="1" maxsize="4"><register name="acc"/></pentry></input>
            <output><pentry minsize="1" maxsize="4"><register name="acc"/></pentry></output>
            <unaffected><register name="vsp"/></unaffected>
        </prototype>
    </default_proto>
</compiler_spec>
```

### D. Gramática Semántica (`minivm.slaspec`)
Contiene la declaración de espacios de memoria, registros y la semántica P-Code de cada instrucción:

```sleigh
define endian=little;
define alignment=2;

define space ram      type=ram_space      size=4 default;
define space register type=register_space size=4;

define register offset=0x00 size=4 [ acc vip vsp zf cf ];

define token instr (16)
    op   = (0, 7)
    imm8 = (8, 15)
;

macro update_flags(result) {
    zf = (result == 0);
}

:SET imm8 is op=1; imm8 {
    acc = zext(imm8);
    update_flags(acc);
}

:XOR imm8 is op=2; imm8 {
    acc = acc ^ zext(imm8);
    update_flags(acc);
}

:ADD imm8 is op=3; imm8 {
    acc = acc + zext(imm8);
    update_flags(acc);
}

:MBA imm8 is op=5; imm8 {
    local y:4 = zext(imm8);
    acc = (acc ^ y) + 2 * (acc & y);
    update_flags(acc);
}

:HALT is op=6 {
    return [vip];
}
```

---

## 4. Laboratorio Verificado

1. Compilá `plantillas_codigo/vm_mba_crackme.c` con `cl /W4 /Ox /GS- vm_mba_crackme.c`.
2. Abrí el binario en x64dbg y localizá la función `ejecutar_vm_indirect_threading`.
3. Verificá que el grafo no presenta un switch central, sino que cada handler concluye con `jmp qword ptr [r12 + rax*8]`.
4. Ejecutá `python plantillas_codigo/solve_minivm_z3.py` y comprobá que el carácter obtenido supera la validación del binario.
