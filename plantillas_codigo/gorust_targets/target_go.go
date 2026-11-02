// target_go.go — Binario de validación didáctico en Go para reversing de bajo nivel (Lección 2.32)
// Compilación sin símbolos (stripped):
//   go build -ldflags="-s -w" -o target_go.exe target_go.go
// Reversing:
//   GoReSym.exe -t -p target_go.exe > go_meta.json

package main

import (
	"fmt"
	"os"
	"sync"
)

// Interfaz para ejercitar itab
type Validador interface {
	Validar(entrada []byte) bool
	ObtenerNombre() string
}

// Estructura que implementa la interfaz
type VerificadorClave struct {
	Nombre     string
	MascaraXOR byte
}

func (v *VerificadorClave) Validar(entrada []byte) bool {
	if len(entrada) < 4 {
		return false
	}
	// Operación sobre slice
	suma := 0
	for _, b := range entrada {
		suma += int(b ^ v.MascaraXOR)
	}
	return (suma % 256) == 0x42
}

func (v *VerificadorClave) ObtenerNombre() string {
	return v.Nombre
}

func trabajadorGoroutine(id int, ch chan int, wg *sync.WaitGroup) {
	defer wg.Done()
	ch <- (id * 0x1337)
}

func main() {
	if len(os.Args) < 2 {
		fmt.Printf("Uso: %s <clave>\n", os.Args[0])
		return
	}

	// 1. Ejercitar Slices (24 bytes) y Despacho Dinámico vía itab
	var v Validador = &VerificadorClave{
		Nombre:     "ValidadorEspecial",
		MascaraXOR: 0x5A,
	}

	datos := []byte(os.Args[1]) // Slice: {ptr, len, cap}
	fmt.Printf("[*] Ejecutando: %s\n", v.ObtenerNombre())

	if v.Validar(datos) {
		fmt.Println("[+] ¡Clave válida!")
	} else {
		fmt.Println("[-] Clave incorrecta.")
	}

	// 2. Ejercitar Canales y Goroutines (runtime.newproc / runtime.chanrecv1)
	ch := make(chan int, 2)
	var wg sync.WaitGroup

	wg.Add(2)
	go trabajadorGoroutine(1, ch, &wg)
	go trabajadorGoroutine(2, ch, &wg)

	wg.Wait()
	close(ch)

	for res := range ch {
		fmt.Printf("[+] Resultado de goroutine: 0x%x\n", res)
	}
}
