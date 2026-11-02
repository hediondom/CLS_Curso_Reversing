/* vm_mba_crackme.c — Crackme con Máquina Virtual por Indirect Threading y expresiones MBA (Lección 2.34)
 * Compilación: cl /W4 /Ox /GS- vm_mba_crackme.c
 */

#include <stdio.h>
#include <string.h>
#include <stdint.h>

// Definición de opcodes propietarios de la VM
#define OP_SET   1
#define OP_XOR   2
#define OP_ADD   3
#define OP_CMP   4
#define OP_MBA   5
#define OP_HALT  6

// Estructura de instrucción virtual (16 bits: 8 bits opcode, 8 bits operando)
#pragma pack(push, 1)
typedef struct {
    uint8_t op;
    uint8_t imm;
} VmInstruction;
#pragma pack(pop)

// Bytecode protegido alojado en .rdata / .data
static const VmInstruction kBytecode[] = {
    { OP_XOR,  0x23 }, // acc = acc ^ 0x23
    { OP_ADD,  0x07 }, // acc = acc + 0x07
    { OP_MBA,  0x5A }, // acc = (acc ^ 0x5A) + 2*(acc & 0x5A) - 0x5A (Identidad MBA: suma estándar disfrazada)
    { OP_CMP,  0x87 }, // Compara con resultado esperado
    { OP_HALT, 0x00 }
};

int ejecutar_vm_indirect_threading(uint8_t input_char) {
    uint8_t acc = input_char;
    const VmInstruction* vip = kBytecode;
    int zf = 0;

    // Tabla de salto para Indirect Threading (dispersion sin bucle switch central)
    static const void* dispatch_table[] = {
        &&do_halt, // 0: invalid/halt
        &&do_set,  // 1: OP_SET
        &&do_xor,  // 2: OP_XOR
        &&do_add,  // 3: OP_ADD
        &&do_cmp,  // 4: OP_CMP
        &&do_mba,  // 5: OP_MBA
        &&do_halt  // 6: OP_HALT
    };

    #define DISPATCH() goto *dispatch_table[vip->op]

    // Iniciar máquina virtual
    DISPATCH();

do_set:
    acc = vip->imm;
    vip++;
    DISPATCH();

do_xor:
    acc ^= vip->imm;
    vip++;
    DISPATCH();

do_add:
    acc += vip->imm;
    vip++;
    DISPATCH();

do_mba:
    // Expresión Mixed Boolean-Arithmetic (MBA): representa (acc + imm)
    {
        uint8_t y = vip->imm;
        acc = (uint8_t)((acc ^ y) + 2 * (acc & y));
    }
    vip++;
    DISPATCH();

do_cmp:
    zf = (acc == vip->imm) ? 1 : 0;
    vip++;
    DISPATCH();

do_halt:
    return zf;
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        printf("Uso: %s <caracter_clave>\n", argv[0]);
        return 1;
    }

    uint8_t c = (uint8_t)argv[1][0];
    if (ejecutar_vm_indirect_threading(c)) {
        printf("[+] Clave correcta: '%c' supera la maquina virtual!\n", c);
    } else {
        printf("[-] Clave incorrecta.\n");
    }
    return 0;
}
