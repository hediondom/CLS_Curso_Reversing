// target_rust.rs — Binario de validación didáctico en Rust para reversing de bajo nivel (Lección 2.32)
// Compilación sin símbolos en release:
//   rustc -O -C panic=abort -C lto=fat -o target_rust.exe target_rust.rs
// O con Cargo:
//   cargo build --release
// Reversing:
//   rustfilt < simbolos.txt

use std::env;
use std::future::Future;
use std::pin::Pin;
use std::task::{Context, Poll, RawWaker, RawWakerVTable, Waker};

// Trait para ejercitar fat pointers dyn Trait (vtable: drop, size, align, metodos)
trait ValidadorSeguro {
    fn comprobar(&self, texto: &str) -> Option<u32>;
    fn identificador(&self) -> &'static str;
}

struct VerificadorRust {
    salt: u32,
}

impl ValidadorSeguro for VerificadorRust {
    fn comprobar(&self, texto: &str) -> Option<u32> {
        if texto.len() < 3 {
            return None; // Ejercita Niche Optimization en Option<&T> o Option<NonZeroU32>
        }
        let mut acum: u32 = self.salt;
        for b in texto.bytes() {
            acum = acum.wrapping_add(b as u32 ^ 0x23);
        }
        Some(acum)
    }

    fn identificador(&self) -> &'static str {
        "MotorVerificadorRust_v1"
    }
}

// Función asíncrona para ejercitar corrutinas y máquinas de estado async/await
async fn tarea_asincrona(valor_inicial: u32) -> u32 {
    let paso1 = valor_inicial.wrapping_mul(3);
    // Punto de suspensión virtual (.await)
    let paso2 = paso1 ^ 0x1337;
    paso2
}

// Ejecutor mínimo para poll manual del Future en una sola función
fn ejecutar_future_manual<F: Future<Output = u32>>(mut f: F) -> u32 {
    unsafe fn dummy_clone(_: *const ()) -> RawWaker { dummy_raw_waker() }
    unsafe fn dummy_wake(_: *const ()) {}
    unsafe fn dummy_wake_by_ref(_: *const ()) {}
    unsafe fn dummy_drop(_: *const ()) {}
    static VTABLE: RawWakerVTable = RawWakerVTable::new(dummy_clone, dummy_wake, dummy_wake_by_ref, dummy_drop);
    fn dummy_raw_waker() -> RawWaker { RawWaker::new(std::ptr::null(), &VTABLE) }

    let waker = unsafe { Waker::from_raw(dummy_raw_waker()) };
    let mut cx = Context::from_waker(&waker);
    let mut pin_f = unsafe { Pin::new_unchecked(&mut f) };

    match pin_f.as_mut().poll(&mut cx) {
        Poll::Ready(val) => val,
        Poll::Pending => 0,
    }
}

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        println!("Uso: {} <clave>", args[0]);
        return;
    }

    // 1. Despacho dinámico a través de dyn Trait (fat pointer: [datos, vtable])
    let instancia = VerificadorRust { salt: 0xCAFEBABE };
    let obj: &dyn ValidadorSeguro = &instancia;

    println!("[*] Ejecutando componente: {}", obj.identificador());

    match obj.comprobar(&args[1]) {
        Some(resultado) => {
            println!("[+] Hash calculado: 0x{:08X}", resultado);
            
            // 2. Ejecución de la máquina de estado async Future::poll
            let res_async = ejecutar_future_manual(tarea_asincrona(resultado));
            println!("[+] Resultado async: 0x{:08X}", res_async);
        }
        None => {
            println!("[-] Clave demasiado corta (None por niche optimization).");
        }
    }
}
