---
title: "2.12 · MFC: llegar al handler cuando todo pasa por clases"
description: "Reconocer un binario MFC y llegar al manejador de un control (botón de un diálogo) a través del message map, cuando el WinProc no está a la vista."
etapa: "Etapa 2 · Windows intermedio"
---

# MFC: llegar al handler cuando todo pasa por clases

:::{nota} Objetivo de la lección
Reconocer un ejecutable hecho con **MFC** y llegar al **handler** de un control (el botón de un diálogo) aunque el `WinProc` clásico no esté a la vista. **Prerrequisitos:** mensajes de Windows y debugger (2.6), estructuras y vtables (2.7).
:::

## Por qué MFC complica la lectura

En los ejercicios anteriores la ventana se hacía **con la API de Windows directa**: el programa llamaba a `RegisterClassA` (que registra la clase y apunta al `WinProc`) y luego a `CreateWindow`; desde el `WinProc` se llegaba fácil a la comparación con los números de mensaje (`WM_COMMAND`, etc.) y de ahí al código que maneja cada evento. Era sencillo.

**MFC** (Microsoft Foundation Classes) es un conjunto de clases con mucha herencia que envuelve esa misma API. Por debajo sigue pasando lo mismo, pero **por arriba no se ve el `WinProc`**: Visual Studio genera una clase de diálogo (`CDialog`/`CWnd`) y el ruteo de mensajes queda escondido en el framework. Por eso, abrir un binario MFC y buscar el `WinProc` a mano no alcanza (**observado**, capítulo 39: {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_39 TIPS 2 MFC_TIPS 2 MFC.txt|Reversing desde cero, cap. 39}}).

## Señales de que es MFC

- Importa `mfc###u.dll` (p. ej. `mfc140u.dll`) y el runtime de VC — **si MFC está enlazado dinámico**. En **enlace estático** esa DLL no aparece: ahí te guiás por los símbolos (`CWnd`, `AfxWinInit`) y las strings.
- Aparecen `AfxWinMain`/`AfxWinInit` y nombres de clases MFC (`CWnd`, `CDialog`, `CWinApp`, `CString`).
- Las APIs de texto que te sirven como ancla siguen estando: `GetWindowTextW`, `SetWindowTextW`, `MessageBoxW`, `SendMessageW`.

## El message map: dónde está el ruteo

MFC asocia cada mensaje/control a una función con un **message map**, una tabla que el compilador arma a partir de macros del estilo `BEGIN_MESSAGE_MAP` / `ON_BN_CLICKED` / `END_MESSAGE_MAP`. En el binario queda como un arreglo de entradas **`AFX_MSGMAP_ENTRY`**, y cada entrada tiene más que "ID y puntero": `nMessage` (el mensaje, p. ej. `WM_COMMAND`), `nCode` (código de notificación), `nID` y `nLastID` (rango de IDs de control), `nSig` (la firma de la función) y **`pfn`** (el puntero al handler). El handler de "se hizo clic en el botón 1" suele llamarse `OnBnClickedButton1` en el fuente.

Dos caminos para llegar, sin pelearte con la tabla (**recomendación editorial**, apoyada en el método de mensajes del cap. 28):

1. **Por string/API (el más rápido):** buscá la string de la ventana ("clave", "acceso", el mensaje de éxito) o poné un breakpoint en `GetWindowTextW`/`SendMessageW`; al dispararse, el *call stack* te deja dentro del handler del control.
2. **Por el message map:** localizá la tabla del diálogo (cerca del constructor de la clase) y seguí el puntero de la entrada cuyo ID coincide con el del botón.

## Ejemplo paso a paso: del botón al handler

*(Ejemplo **ilustrativo**: direcciones y nombres construidos para mostrar la ruta.)*

Ponés un breakpoint en `GetWindowTextW`, tocás **Aceptar** en el diálogo y mirás el *call stack*:

```text
USER32!GetWindowTextW
app!CWnd::GetWindowTextW(...)          ; wrapper de MFC
app!CMiDialog::OnBnClickedOk+0x3e      ← el handler (acá estás)
mfc140u!_AfxDispatchCmdMsg+0x52        ; el framework ruteó el mensaje
mfc140u!CWnd::OnCommand+0x...
```

Subís al frame del handler `OnBnClickedOk` y encontrás la decisión:

```asm
lea   rdx, [rsp+0x40]        ; buffer donde quedó el texto tipeado
lea   rcx, [rsi+8]           ; el control (this)
call  CWnd::GetWindowTextW
lea   rdx, aS3cr3t           ; "s3cr3t"  (la clave esperada)
lea   rcx, [rsp+0x40]
call  wcscmp                 ; la comparación que decide éxito/fracaso
test  eax, eax
jnz   mal                    ; != 0 → clave incorrecta
```

Sin el call stack habría que desenredar el message map; con el breakpoint en la API de texto caés **directo** en `OnBnClickedOk`.

## Práctica

En tu VM:

1. Si tenés Visual Studio, creá una **app MFC basada en diálogo** con un botón y un `OnBnClickedButton1` que compare un texto; compilala. Si no, usá un **binario MFC de práctica**.
2. Confirmá que importa `mfc###u.dll` y ubicá `AfxWinMain`.
3. Poné un breakpoint en `GetWindowTextW` (o en `SendMessageW`), tocá el botón y, desde el *call stack*, llegá al handler.
4. Identificá en el handler la comparación que decide éxito/fracaso.

## Preguntas de repaso

?? ¿Por qué en un binario MFC no encontrás el `WinProc` como en los ejercicios con API directa?
!! Porque MFC **envuelve** la API: el ruteo de mensajes lo maneja el framework a través de clases y del message map, en vez de un `WinProc` propio que el programa registre con `RegisterClassA`.

?? ¿Qué es el message map y qué guarda cada entrada?
!! Una tabla que mapea **mensaje/control → función**. Cada entrada tiene el ID del control, el código de notificación y el **puntero al handler**.

?? Nombrá dos señales de que un binario es MFC.
!! Importa `mfc###u.dll` (p. ej. `mfc140u.dll`) y aparecen `AfxWinInit`/`AfxWinMain` y clases como `CDialog`/`CWnd`/`CString`.

?? ¿Cuál es la forma más rápida de llegar al handler de un botón?
!! Un breakpoint en `GetWindowTextW`/`SendMessageW` (o seguir la string del diálogo): al dispararse, el *call stack* te deja dentro del handler, sin recorrer la tabla a mano.

?? Por debajo, ¿MFC cambia lo que hace Windows con los mensajes?
!! No. Sigue siendo el mismo sistema de mensajes de Windows; MFC solo agrega una capa de clases por encima. Las APIs ancla (`GetWindowTextW`, `SendMessageW`) siguen ahí.

:::{nota} Puerta de salida
Podés: (1) reconocer un binario MFC por imports y símbolos; (2) explicar qué es el message map; (3) llegar al handler de un botón por breakpoint en una API de texto y el call stack; (4) señalar la comparación que decide el resultado.
:::

## Fuentes de esta lección

- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_39 TIPS 2 MFC_TIPS 2 MFC.txt|Reversing desde cero, cap. 39}} — el ejercicio MFC «de CITO»: por qué el `WinProc` no está a la vista y qué cambia respecto de usar la API directa.
- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_28 Mensajes de Windows_28 Mensajes de Windows.txt|Reversing desde cero, cap. 28}} — base: `RegisterClassA`, `WinProc`, `WM_COMMAND` y breakpoint sobre el mensaje.

:::{nota} Capas de esta lección
**Contenido observado en CLS:** el contraste API-directa vs. MFC del capítulo 39 y el método de mensajes del 28. **Conocimiento externo:** los nombres del message map (`BEGIN_MESSAGE_MAP`, `ON_BN_CLICKED`, `OnBnClickedButton1`), las DLLs `mfc###u.dll` y `AfxWinInit`. **Recomendación editorial:** los dos caminos para llegar al handler y la práctica con binario propio.
:::
