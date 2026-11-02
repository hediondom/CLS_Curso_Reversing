# Binarios Didácticos de Laboratorio para Go y Rust (Lección 2.32)

Este directorio contiene dos especímenes benignos diseñados para ejercitar la recuperación de tipos, tablas internas de despacho y máquinas de estado en binarios compilados sin símbolos.

## 1. Binario en Go (`target_go.go`)

### Compilación:
```bash
go build -ldflags="-s -w" -o target_go.exe target_go.go
```

### Qué auditar en el desensamblador (IDA / Ghidra / x64dbg):
1. **Recuperación con `GoReSym`:**
   ```bash
   GoReSym.exe -t -p target_go.exe > go_meta.json
   ```
   Observa cómo reaparecen los nombres de funciones (`main.main`, `main.(*VerificadorClave).Validar`).
2. **Slices en memoria (24 bytes):** Inspecciona el paso del argumento `datos` en `main`: 3 slots correspondientes a `array *T` (+0x00), `len` (+0x08) y `cap` (+0x10).
3. **Despacho dinámico de interfaz (`itab`):** Localiza la llamada indirecta a través del par `(itab, data)`. En la tabla `itab` identifica el offset `+0x18` donde residen los punteros a métodos.
4. **Primitivas de concurrencia:** Identifica las llamadas internas a `runtime.newproc`, `runtime.chansend1` y `runtime.chanrecv1`.

---

## 2. Binario en Rust (`target_rust.rs`)

### Compilación:
```bash
rustc -O -C panic=abort -C lto=fat -o target_rust.exe target_rust.rs
```

### Qué auditar en el desensamblador:
1. **Desmanglado de Símbolos:**
   Inspecciona las cadenas de símbolos con esquema v0 (`_R...`) o legacy (`_ZN...E`) y utiliza `rustfilt`:
   ```bash
   rustfilt < simbolos.txt
   ```
2. **Fat Pointer `dyn Trait`:** Localiza el par de 16 bytes pasado a `obj`. Verifica que el segundo qword apunta a la vtable en `.rdata` con la estructura: `+0x00` destructor, `+0x08` tamaño, `+0x10` alineación, `+0x18` puntero a `comprobar`.
3. **Máquina de Estado `async/await`:** Localiza la implementación de `core::future::Future::poll` generada para `tarea_asincrona`. Observa el switch sobre el discriminante de estado para saltar entre puntos de suspensión.
