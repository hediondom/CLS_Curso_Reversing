# solve_minivm_z3.py — Lifting simbólico directo del bytecode de mini_vm (Lección 2.34)
# Uso: python solve_minivm_z3.py
from z3 import BitVec, BitVecVal, Solver, sat

# Constantes de opcodes de la máquina virtual (indirect threading / bytecode)
OP_SET, OP_XOR, OP_ADD, OP_CMP, OP_HALT = 1, 2, 3, 4, 6

# Bytecode extraído estáticamente del binario de práctica (.data)
# En este flujo, el operando inicial es simbólico (el input proporcionado por el usuario)
bytecode = [
    (OP_XOR, 0x23),
    (OP_ADD, 0x07),
    (OP_XOR, 0x5A),
    (OP_CMP, 0x3D),
    (OP_HALT, 0)
]

s = Solver()
# Creamos la variable simbólica de 8 bits para representar el byte de entrada
entrada = BitVec("entrada_usuario", 8)
acc = entrada

print("[*] Iniciando lifting simbólico del bytecode...")

for op, imm in bytecode:
    if op == OP_SET:
        acc = BitVecVal(imm, 8)
    elif op == OP_XOR:
        acc = acc ^ imm
    elif op == OP_ADD:
        acc = acc + imm
    elif op == OP_CMP:
        # Añadimos la restricción que conduce a la bifurcación de éxito (zf == 1)
        s.add(acc == imm)
        print(f"    [+] Restricción agregada: acc == {imm:#04x}")
    elif op == OP_HALT:
        break

if s.check() == sat:
    modelo = s.model()
    solucion = modelo[entrada].as_long()
    print(f"\n[+] ¡Éxito! Valor resuelto por el motor SMT (Z3): {solucion:#04x} ('{chr(solucion)}')")
    print(f"    Verificación: (({solucion:#04x} ^ 0x23) + 0x07) ^ 0x5a = {(((solucion ^ 0x23) + 0x07) ^ 0x5a) & 0xff:#04x} (esperado: 0x3d)")
else:
    print("[-] No se encontró solución para las restricciones dadas.")
