// ==============================================================================
// Plantilla 18 · Demostración de Rust Endurecido y Reconstrucción de Slices
// Obra: Reversing en Windows — Tomo III (Módulo 1)
//
// Invocación Cargo:
//   cargo build --release
//
// Características a observar en Ghidra / IDA Pro:
//   1. Retorno Múltiple de la ABI de Rust en registros x64 (RAX, RDX, R8D).
//   2. Cadenas &str sin byte nulo 0x00 empaquetadas en un único blob en .rdata.
//   3. Ausencia total de cadenas de pánico (.rs) por panic = "abort".
// ==============================================================================

#![no_std]
#![no_main]

// Proveedor de salida para entorno bare-metal / no_std en Windows
#[link(name = "msvcrt")]
extern "C" {
    fn puts(s: *const u8) -> i32;
    fn printf(format: *const u8, ...) -> i32;
    fn ExitProcess(uExitCode: u32) -> !;
}

// Estructura de error simple
#[derive(Debug, Clone, Copy)]
pub enum ParserError {
    InvalidHeader = 1,
    BufferOverflow = 2,
    UnknownOpcode = 3,
}

// Función que exhibe retorno múltiple en ABI de Rust:
// Retorna (discriminante, u64, u32) repartido en RAX, RDX y R8D
#[inline(never)]
pub fn parse_packet_header(payload: &[u8]) -> Result<(u64, u32), ParserError> {
    if payload.len() < 8 {
        return Err(ParserError::InvalidHeader);
    }

    // Extracción de campos sin copias
    let magic = u32::from_le_bytes([payload[0], payload[1], payload[2], payload[3]]);
    if magic != 0x53594E43 { // "SYNC" en little-endian
        return Err(ParserError::UnknownOpcode);
    }

    let timestamp = u64::from_le_bytes([
        payload[0], payload[1], payload[2], payload[3],
        payload[4], payload[5], payload[6], payload[7],
    ]);

    let seq_id = (payload.len() as u32) ^ 0xA5A5A5A5;

    Ok((timestamp, seq_id))
}

// Conjunto de literales de cadena continuos en .rdata
const TOKEN_AUTH: &str = "AUTH_BEARER_V2";
const TOKEN_USER: &str = "SESSION_ADMIN_ROOT";
const MSG_SUCCESS: &str = "[+] Paquete procesado exitosamente con ID:";
const MSG_FAILURE: &str = "[-] Error al procesar paquete de red";

#[no_mangle]
pub extern "C" fn main() -> ! {
    let dummy_packet: [u8; 12] = [
        0x43, 0x4E, 0x59, 0x53, // "SYNC"
        0x10, 0x20, 0x30, 0x40,
        0x01, 0x02, 0x03, 0x04,
    ];

    match parse_packet_header(&dummy_packet) {
        Ok((ts, seq)) => {
            unsafe {
                // Notar cómo los literales se pasan como puntero y longitud
                printf(
                    b"%s %llu (Seq: %u)\n\0".as_ptr(),
                    MSG_SUCCESS.as_ptr(),
                    ts,
                    seq,
                );
                printf(b"Scope: %s | User: %s\n\0".as_ptr(), TOKEN_AUTH.as_ptr(), TOKEN_USER.as_ptr());
            }
        }
        Err(_) => {
            unsafe {
                puts(MSG_FAILURE.as_ptr());
            }
        }
    }

    unsafe { ExitProcess(0) };
}

#[panic_handler]
fn panic(_info: &core::panic::PanicInfo) -> ! {
    // Al compilar con panic = "abort", el compilador simplemente emite ud2
    // sin almacenar nombres de archivo ni cadenas de texto de error.
    unsafe {
        core::arch::asm!("ud2", options(noreturn));
    }
}
