---
title: "2.11 · TLS: código que corre antes de main"
description: "Thread Local Storage y TLS callbacks: el directorio TLS del PE, AddressOfCallBacks y por qué ese código se ejecuta antes del entry point."
etapa: "Etapa 2 · Windows intermedio"
---

# TLS: código que corre antes de `main`

:::{nota} Objetivo de la lección
Entender qué es el **Thread Local Storage (TLS)** y, sobre todo, los **TLS callbacks**: código que Windows ejecuta **antes del entry point**, un lugar clásico para esconder lógica. Saber encontrarlo en el PE y en el debugger. **Prerrequisitos:** PE y directorios (1.4), procesos e hilos (1.5), debugger (2.6).
:::

## Dos cosas distintas con el mismo nombre

El capítulo 38 es un apéndice teórico sobre TLS y aclara que en un mismo ejercicio (`EjemploTLS`) conviven **dos formas** de guardar datos por hilo ({{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_38 Apéndice teórico TLS_Apéndice teórico TLS.txt|Reversing desde cero, cap. 38}}):

1. **Por API:** `TlsAlloc`, `TlsSetValue`, `TlsGetValue`, `TlsFree`. El programa pide un índice y guarda/lee un valor propio de cada hilo. Es explícito y se ve en los imports.
2. **Por variable `__declspec(thread)`:** el compilador reserva el dato en la sección `.tls` y lo resuelve con ayuda del loader. No hay llamadas visibles: el acceso aparece como lectura de una zona por hilo.

Y hay un **tercer mecanismo, aparte**: los **TLS callbacks**. No dependen de cómo declares las variables —`__declspec(thread)` usa `.tls` pero **no** crea callbacks por sí solo—; los callbacks se registran en el **directorio TLS del PE** y son lo que más importa para el reversing, porque corren antes de `main`.

## El directorio TLS y los callbacks

El PE tiene un **directorio TLS** (`IMAGE_TLS_DIRECTORY`) entre sus *data directories*. Su campo clave para el análisis es **`AddressOfCallBacks`**: un puntero a un arreglo de funciones terminado en cero. Esas funciones son los **TLS callbacks**, y el loader de Windows **las ejecuta antes de que corra el entry point** (antes de `main`), en cada carga y en cada creación/destrucción de hilo.

La consecuencia para quien analiza (**conocimiento externo**, confirmado por el rol de TLS que explica el cap. 38): si ponés el breakpoint solo en el entry point, **te perdés todo lo que pasó en el callback**. Es el escondite preferido para anti-debug temprano o para inicializaciones que no querés que se vean.

## Cómo encontrarlo

- **En el PE** (PE-bear, CFF Explorer o IDA): abrí el *data directory* **TLS**; si `AddressOfCallBacks` no es cero, seguilo y vas a ver la lista de callbacks.
- **En IDA:** aparecen como `TlsCallback_0`, `TlsCallback_1`… y suelen quedar fuera del flujo del `main`; búscalos por nombre o desde el directorio TLS.
- **En x64dbg:** activá *Options → Preferences → Events → **TLS Callbacks*** para que el debugger **pare en el primer callback**, antes del entry point. Si no, arrancás ya pasado el punto interesante.

## Ejemplo paso a paso: leer el directorio TLS

*(Ejemplo **ilustrativo**: valores construidos; en un binario real cambian las direcciones.)*

En PE-bear, el *data directory* número 9 (TLS) apunta a la estructura, y adentro seguís `AddressOfCallBacks`:

```text
DataDirectory[9] TLS → RVA 0x3000, size 0x18

IMAGE_TLS_DIRECTORY  (en .rdata)
  StartAddressOfRawData  0x00404000
  EndAddressOfRawData    0x00404008
  AddressOfIndex         0x00404100
  AddressOfCallBacks     0x00403020   ← seguí este puntero
  SizeOfZeroFill         0
  Characteristics        0

En 0x00403020 (arreglo de punteros, terminado en NULL):
  20 10 40 00   00 00 00 00
  → callback[0] = 0x00401020
  → callback[1] = NULL  (fin de la lista)
```

Vas a `0x00401020` y ahí está el `TlsCallback_0`: ese código corre **antes** del entry point. Si `AddressOfCallBacks` fuera `0`, no habría callbacks y bastaría el breakpoint en el entry point.

## Práctica

En tu VM, con un **programa propio**:

1. Compilá algo mínimo con un callback TLS. En MSVC, el código mínimo es:

   ```c
   #include <windows.h>
   #include <stdio.h>

   volatile int orden = 0;   /* lo escribe el callback; lo lee main */

   void NTAPI mi_cb(PVOID h, DWORD motivo, PVOID r) {
       /* OJO: nada de printf acá. El callback corre ANTES de que
          el CRT se inicialice, así que el runtime de C todavía no
          está listo. Solo tocamos una variable. */
       if (motivo == DLL_PROCESS_ATTACH) orden = 1;
   }

   /* El símbolo del linker cambia según la arquitectura:
      x86 -> __tls_used (dos guiones bajos); x64 -> _tls_used (uno). */
   #ifdef _WIN64
   #pragma comment(linker, "/INCLUDE:_tls_used")
   #else
   #pragma comment(linker, "/INCLUDE:__tls_used")
   #endif
   #pragma const_seg(".CRT$XLB")
   EXTERN_C const PIMAGE_TLS_CALLBACK p_cb = mi_cb;
   #pragma const_seg()

   int main(void) {
       printf("orden al entrar a main = %d  (1 => el callback ya corrió)\n", orden);
       return 0;
   }
   ```
2. Abrilo en PE-bear y confirmá que el directorio **TLS** no está vacío y que `AddressOfCallBacks` apunta a tu función.
3. En x64dbg, activá el breakpoint de TLS callbacks y verificá que **para antes de `main`**.
4. Confirmá el orden **sin** imprimir desde el callback: que el callback solo escriba `orden = 1` y que `main` imprima `orden`. Si al entrar a `main` vale 1, el callback corrió antes (imprimir desde el callback puede colgar: el CRT todavía no se inicializó).

## Preguntas de repaso

?? ¿Qué hace especial a un TLS callback frente a cualquier otra función?
!! Que el loader lo ejecuta **antes del entry point** (y en cada alta/baja de hilo), sin que el `main` lo llame. Corre "solo", por estar registrado en el directorio TLS.

?? ¿Qué campo del directorio TLS mirás primero y por qué?
!! `AddressOfCallBacks`: si no es cero, hay callbacks. Apunta a un arreglo de punteros a función terminado en cero.

?? Si solo ponés un breakpoint en el entry point, ¿qué te perdés?
!! Todo lo que haya hecho el/los callbacks TLS, que ya corrieron. Por eso en x64dbg conviene habilitar el breakpoint de TLS callbacks.

?? ¿En qué se diferencian las dos formas de TLS del `EjemploTLS`?
!! Una usa **APIs** (`TlsAlloc`/`TlsGetValue`/`TlsSetValue`), visible en imports; la otra usa **`__declspec(thread)`**, resuelta por el compilador y el loader vía la sección `.tls`, sin llamadas explícitas.

?? ¿Por qué el TLS es un buen escondite para anti-debug?
!! Porque corre antes que el código "principal" y mucha gente empieza a mirar desde el entry point; un chequeo puesto en un callback se ejecuta y decide antes de que el analista llegue.

:::{nota} Puerta de salida
Podés: (1) distinguir TLS por API de `__declspec(thread)`; (2) ubicar el directorio TLS y `AddressOfCallBacks` en un PE; (3) hacer que x64dbg pare en el primer callback; (4) demostrar con tu propio binario que el callback corre antes de `main`.
:::

## Fuentes de esta lección

- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_38 Apéndice teórico TLS_Apéndice teórico TLS.txt|Reversing desde cero, cap. 38}} — `EjemploTLS`: TLS por API (`TlsAlloc`/`TlsGetValue`/`TlsSetValue`) y por `__declspec(thread)`.

:::{nota} Capas de esta lección
**Contenido observado en CLS:** las dos formas de TLS del `EjemploTLS` del capítulo 38. **Conocimiento externo:** la estructura `IMAGE_TLS_DIRECTORY`, `AddressOfCallBacks`, el orden de ejecución antes del entry point y el breakpoint de TLS en x64dbg. **Recomendación editorial:** el método de búsqueda y la práctica con binario propio.
:::
