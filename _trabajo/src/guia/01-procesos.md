---
title: "Etapa 1 · Procesos, hilos y mapa de memoria"
description: "Qué es un proceso, qué agrega un hilo y cómo leer el mapa de memoria de un programa en ejecución."
etapa: "Etapa 1 · Fundamentos"
---

# Procesos, hilos y mapa de memoria

:::{nota} Objetivo de la lección
Al terminar vas a poder distinguir programa, proceso e hilo; explicar qué comparte y qué no comparte un hilo con los demás; crear un programa propio con dos hilos y encontrarlos en el debugger; y leer las regiones del mapa de memoria de un proceso.
:::

**Prerrequisitos:** memoria y stack. **Duración sugerida:** 3 horas. Estimación aproximada.

## Programa, proceso, hilo

Un **programa** es un archivo en disco: bytes, cabeceras, código. Un **proceso** es ese programa cargado y en ejecución, con su propio espacio de direcciones, sus handles y sus hilos. Un **hilo** (*thread*) es una secuencia de ejecución dentro del proceso.

La diferencia importa porque el debugger te muestra las tres cosas a la vez: el archivo que abriste, el proceso que creó y los hilos que están corriendo.

| Concepto | Qué es | Qué comparte |
|---|---|---|
| Programa | Archivo `.exe` en disco | Nada: es estático |
| Proceso | Instancia en ejecución | Espacio de direcciones, handles, token |
| Hilo | Flujo de ejecución | Código, datos globales, heap, handles |
| Hilo (propio) | Contexto de CPU, stack, estado | Nada de eso con otros hilos |

Cada hilo tiene **su propio stack** y **su propio contexto de CPU** (registros). Si dos hilos comparten una variable global, los dos ven la misma dirección; si cada uno declara una variable local, cada uno tiene su copia en su stack.

El capítulo 15b lo define así: un hilo es "una función o una parte del programa que se ejecuta" al mismo tiempo que otra ({{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_15b Apéndice teórico 1 - Threads_15b Apéndice teórico 1 - Threads.txt|Reversing desde cero, cap. 15b}}, 00:00:55).

## Ejemplo paso a paso: dos hilos en un programa propio

El capítulo 15b usa un programa de ejemplo con un hilo que incrementa un contador y un `main` que espera una tecla. La estructura es esta:

```c
#include <windows.h>
#include <stdio.h>

int MyCounter = 0;

DWORD WINAPI MyThread(LPVOID lpParam) {
    int *contador = (int *)lpParam;
    while (*contador < 0xFFF) {
        (*contador)++;
    }
    return 0;
}

int main(void) {
    HANDLE h = CreateThread(NULL, 0, MyThread, &MyCounter, 0, NULL);
    if (h == NULL) return 1;
    printf("Presione Enter para terminar...\n");
    getchar();
    printf("Contador: %d\n", MyCounter);
    CloseHandle(h);
    return 0;
}
```

Los argumentos de `CreateThread` que importan para el análisis son:

| Posición | Nombre | En el ejemplo |
|---|---|---|
| 3.º | `lpStartAddress` | `MyThread`: dónde empieza el hilo |
| 4.º | `lpParameter` | `&MyCounter`: puntero que recibe el hilo |
| 5.º | `dwCreationFlags` | `0` = arranca ya; `4` (`CREATE_SUSPENDED`) = creado detenido |
| Retorno | `HANDLE` | Se usa con `ResumeThread` o `CloseHandle` |

El capítulo muestra exactamente esto: el tercer argumento es la dirección de inicio, el cuarto es el puntero a la variable, la bandera `0` hace que arranque al instante y `4` lo deja suspendido hasta un `ResumeThread` (cap. 15b, 00:02:00–00:03:00).

### Qué ves en el debugger

1. Abrí el programa en x64dbg y dejalo en el entry point.
2. Abrí **Debugger → Thread List**. Vas a ver el hilo principal y el que creaste.
3. Poné un breakpoint en `MyThread` y dejá correr. Cuando el hilo llegue, el debugger se detiene **en ese hilo**.
4. En la lista de hilos, el que está detenido aparece en negrita.
5. Cambiá de hilo y mirá el stack: cada uno tiene el suyo.

En el ejemplo del curso aparecen dos hilos en la versión de 32 bits y cuatro en la de 64 bits (el principal más tres que crea el programa) (cap. 15b, 00:10:02 y 00:15:12).

:::{aviso} El debugger no puede mostrar dos hilos a la vez
Cuando un hilo se detiene en un breakpoint, los demás siguen o quedan suspendidos según cómo esté configurado el debugger, pero la pantalla te muestra **un contexto**. Si "de repente salta a otro lado", puede ser un cambio de hilo, no un salto del programa. Revisá la columna de hilo antes de asustarte (cap. 15b, 00:09:50 y 00:14:05).
:::

## Handles: los números que identifican recursos

Un **handle** es un identificador opaco que el sistema operativo te da para referenciar un recurso: una ventana, un archivo, un hilo, un evento. No es una dirección de memoria ni un puntero; es un índice a una tabla interna del proceso.

El capítulo 01 muestra la pestaña **Handles** de x64dbg y explica que son "identificadores de ventanas y archivos y demás cosas" ({{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_01 x64dbg primeros pasos_01 x64dbg primeros pasos.txt|Reversing desde cero, cap. 01}}, 00:06:20).

Para el análisis: cuando una API devuelve un handle y el programa lo guarda en una variable, esa variable no contiene "el archivo", contiene un número que el sistema traduce. Si ves un valor pequeño como `0x000000A4`, es un handle, no una dirección.

## El mapa de memoria

La pestaña **Memory Map** de x64dbg muestra las regiones del espacio de direcciones del proceso: imagen del ejecutable, DLLs cargadas, heap, stack y regiones reservadas. Cada fila tiene base, tamaño, permisos y tipo.

En el capítulo 05 se lee así: el ejecutable está mapeado desde `0x6D0000`; los primeros `0x1000` bytes son el header; después vienen `.text`, `.rdata`, `.data`, `.rsrc` y `.reloc` ({{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_05 Virtual Adress, RVA, Offsets y Desplazamientos_05 Virtual Adress, RVA, Offsets y Desplazamientos.txt|Reversing desde cero, cap. 05}}, 00:00:10–00:01:00).

Los permisos se leen en tres letras:

| Permiso | Significado | Ejemplo |
|---|---|---|
| `R` | Lectura | `.rdata` |
| `W` | Escritura | `.data`, heap, stack |
| `X` | Ejecución | `.text` |
| `RWX` | Todo | Sospechoso en un binario normal; típico de unpacking o shellcode |

Una región `RWX` no es prueba de malware, pero es una pregunta que vale la pena hacerse: ¿por qué este programa necesita escribir y ejecutar en la misma página?

## Hilos, excepciones y TLS: el puente a temas avanzados

Cada hilo tiene su propio estado de excepciones. En 32 bits, el sistema encadena los manejadores en el stack y el primer DWORD del bloque de información del hilo (`FS:[0]`) apunta al primero de la cadena (cap. 16b, 00:02:29). En 64 bits, esa información se guarda en tablas `.pdata`/`.rdata` y no en el stack (cap. 36, 00:00:27).

También cada hilo puede tener **TLS** (*Thread Local Storage*): variables globales que en realidad tienen una copia por hilo. El capítulo 38 lo trata en detalle; acá alcanza con saber que existe y que explica por qué una variable "global" puede tener valores distintos según el hilo.

No necesitás dominar esto para seguir. Lo importante es que cuando veas `FS:[0]`, `GS:[0]`, `.pdata` o `TlsAlloc`, sepas que estás frente a infraestructura del sistema, no a código del programa.

## Práctica

1. Compilá el programa de dos hilos de arriba (en el guest, con Visual Studio o MinGW).
2. Abrilo en x64dbg y completá esta tabla:

| Pregunta | Tu respuesta |
|---|---|
| ¿Cuántos hilos hay al inicio? | |
| ¿En qué dirección empieza `MyThread`? | |
| ¿Qué valor tiene el argumento que recibe? | |
| ¿Qué pasa si usás `CREATE_SUSPENDED` (`4`)? | |
| ¿Qué región de memoria es el stack? ¿Qué permisos tiene? | |

3. Agregá un `Sleep(5000)` dentro del hilo y observá la lista de hilos mientras duerme.
4. Poné un breakpoint condicional que registre `{EAX}` en el hilo y explicá qué valor ves.

## Preguntas de repaso

**1. ¿Qué comparte un hilo con los demás hilos del mismo proceso?**
El espacio de direcciones (código, datos globales, heap) y los handles. No comparte el stack ni los registros.

**2. ¿Un proceso puede tener varios hilos? ¿Y varios procesos el mismo código?**
Sí a las dos. Varios procesos pueden ejecutar la misma imagen (por ejemplo, dos instancias del mismo `.exe`), cada uno con su propio espacio de direcciones.

**3. ¿Qué hace `CREATE_SUSPENDED`?**
Crea el hilo detenido. No empieza a ejecutar hasta que otro hilo llame a `ResumeThread`.

**4. ¿Por qué el debugger muestra un solo hilo a la vez?**
Porque muestra el contexto de CPU de un hilo; los demás existen pero no se pueden "mirar" simultáneamente en la misma ventana.

**5. ¿Qué indica una región `RWX`?**
Que se puede leer, escribir y ejecutar. Es inusual en un binario compilado normal y aparece en etapas de desempaquetado, generación de código o shellcode. No prueba nada por sí sola, pero orienta la investigación.

## Antes de avanzar

Tenés que poder:

- Explicar la diferencia entre programa, proceso e hilo con un ejemplo.
- Nombrar los argumentos de `CreateThread` que importan y qué hace cada uno.
- Encontrar la lista de hilos y el mapa de memoria en x64dbg.
- Leer los permisos de una región y decir si es normal o sospechosa.

:::{nota} Puerta de salida
Si podés crear tu propio programa de dos hilos y encontrarlo en el debugger, estás listo para el formato PE. Si no, hacelo antes: es la mejor forma de entender qué significa "contexto de hilo".
:::

## Fuentes de esta lección

- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_15b Apéndice teórico 1 - Threads_15b Apéndice teórico 1 - Threads.txt|Reversing desde cero, cap. 15b}} — hilos, `CreateThread`, lista de hilos, cambio de contexto.
- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_01 x64dbg primeros pasos_01 x64dbg primeros pasos.txt|Reversing desde cero, cap. 01}} — handles y mapa de memoria.
- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_05 Virtual Adress, RVA, Offsets y Desplazamientos_05 Virtual Adress, RVA, Offsets y Desplazamientos.txt|Reversing desde cero, cap. 05}} — image base y secciones en el mapa.
- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_16b Apéndice teórico 2 - Excepciones 1_16b Apéndice teórico 2 - Excepciones 1.txt|Reversing desde cero, cap. 16b}} y {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_36 Excepciones en 64 bits_36 Excepciones en 64 bits.txt|cap. 36}} — estado de excepciones por hilo.

:::{nota} Capas de esta lección
**Contenido observado en CLS:** el ejemplo de `CreateThread` con `MyCounter`, la lista de hilos y la lectura del mapa del capítulo 05. **Conocimiento externo:** definición de proceso, handles como tabla interna, permisos de página. **Recomendación editorial:** el programa de práctica y la tabla de ejercicios.
:::
