// dump_cil_jit.js — Intercepta clrjit.dll!CILJit::compileMethod en x64 para volcar IL por método (Lección 2.35)
// Uso con Frida: frida -p <PID> -l dump_cil_jit.js --no-pause
// Prototipo de la función en C++ (x64 MSVC ABI):
// CorJitResult CILJit::compileMethod(
//     ICorJitInfo*            comp,      // RCX
//     CORINFO_METHOD_INFO*    info,      // RDX
//     unsigned                flags,     // R8d
//     uint8_t**               nativeEntry,// R9
//     uint32_t*               nativeSizeOfCode // [rsp+28h]
// );

const clrjit = Process.findModuleByName("clrjit.dll");

if (!clrjit) {
    console.error("[-] No se encontró clrjit.dll en el proceso destino. ¿Es una aplicación .NET Core / Framework?");
} else {
    console.log(`[+] Módulo clrjit.dll localizado en: ${clrjit.base}`);
    const getJitExport = clrjit.findExportByName("getJit");
    
    if (!getJitExport) {
        console.error("[-] No se pudo localizar el export 'getJit'.");
    } else {
        const getJit = new NativeFunction(getJitExport, "pointer", []);
        const pJitInstance = getJit();
        const jitVtable = pJitInstance.readPointer();
        // Slot 0 (+0x00) de la vtable corresponde canónicamente a CILJit::compileMethod
        const compileMethodPtr = jitVtable.readPointer();
        
        console.log(`[+] Instancia CILJit: ${pJitInstance} | vtable: ${jitVtable}`);
        console.log(`[+] compileMethod localizado en: ${compileMethodPtr}`);

        Interceptor.attach(compileMethodPtr, {
            onEnter(args) {
                // RDX contiene el puntero a CORINFO_METHOD_INFO
                const pInfo = args[1];
                if (pInfo.isNull()) return;

                // Estructura CORINFO_METHOD_INFO en x64:
                // +0x00: CORINFO_METHOD_HANDLE ftn
                // +0x08: CORINFO_MODULE_HANDLE scope
                // +0x10: uint8_t*              ILCode
                // +0x18: unsigned              ILCodeSize
                // +0x1C: unsigned              maxStack
                // +0x20: unsigned              EHcount
                const ftnHandle = pInfo.readPointer();
                const ilCodePtr = pInfo.add(0x10).readPointer();
                const ilCodeSize = pInfo.add(0x18).readU32();

                if (ilCodeSize > 0 && !ilCodePtr.isNull()) {
                    console.log(`\n======================================================`);
                    console.log(`[JIT] Compilando Método ftn: ${ftnHandle}`);
                    console.log(`      Dirección de ILCode: ${ilCodePtr} | Longitud: ${ilCodeSize} bytes`);
                    console.log(`======================================================`);
                    
                    // Volcado hexadecimal de los primeros 64 bytes de bytecode IL
                    const previewLen = Math.min(ilCodeSize, 64);
                    console.log(hexdump(ilCodePtr, {
                        offset: 0,
                        length: previewLen,
                        header: true,
                        ansi: true
                    }));
                }
            }
        });
        console.log("[*] Gancho instalado con éxito. Esperando compilación de métodos JIT...");
    }
}
