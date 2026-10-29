---
title: "2D.1 · Objetos, handles, tokens, privilegios e integridad"
description: "El modelo de objetos de Windows: handles, el token de acceso (SIDs, privilegios, nivel de integridad) y las ACL. Reconocer contexto de seguridad en el análisis. Rama optativa 2D."
etapa: "Etapa 2 · 2D · Windows internals (optativa)"
---

# Objetos, handles, tokens, privilegios e integridad

:::{aviso} Rama optativa 2D
Lección de la [rama optativa 2D](../2d.html), fuera del recorrido obligatorio. Defensiva: entender el contexto de seguridad para **analizar**, no para escalar privilegios.
:::

:::{nota} Propósito
Entender cómo Windows modela el acceso: todo es un **objeto** al que se llega por **handle**, y lo que un proceso puede hacer lo define su **token** (SIDs, privilegios, nivel de integridad) contra la **ACL** del objeto. Saber leer ese contexto en Process Explorer/WinDbg.
:::

**Prerrequisitos**

- *Obligatorios:* procesos e hilos ([1.3](01-procesos.html)), debugger ([2.6](02-debugger.html)).
- *Recomendados:* anti-análisis/PEB ([2.15](02-anti-analisis.html)), WinDbg ([2.19](02-windbg-heap.html)).

## El modelo de objetos

En Windows casi todo recurso del kernel —procesos, hilos, archivos, claves de registro, eventos, secciones— es un **objeto** gestionado por el *Object Manager*. Un proceso no toca el objeto directamente: pide un **handle** (un índice en su tabla de handles privada) y opera a través de él. Cada handle guarda, además, los **permisos concedidos** (access mask) con los que se abrió. **Conocimiento externo** (Microsoft Learn).

Para el análisis, los handles abiertos de un proceso son una **radiografía de qué toca**: qué archivos, qué claves, qué objetos de sincronización (un **mutex** con nombre suele ser el "ya estoy corriendo" de un malware).

## El token de acceso

Cuando un proceso quiere hacer algo sobre un objeto, Windows compara el **token** del proceso con la **ACL** del objeto. El token contiene:

- **SID de usuario y grupos:** quién sos y a qué grupos pertenecés.
- **Privilegios:** capacidades con nombre (`SeDebugPrivilege`, `SeBackupPrivilege`, `SeLoadDriverPrivilege`…) que el token puede tener **habilitadas** o solo presentes.
- **Nivel de integridad (IL):** Low / Medium / High / System. Con la política obligatoria predeterminada de Windows, un proceso de IL bajo normalmente no puede escribir en objetos de IL mayor (no es una regla universal para toda operación; también intervienen las etiquetas y políticas del objeto). Es una de las barreras usadas por sandboxes.

## ACL: quién puede qué

Un objeto asegurable tiene un **descriptor de seguridad** con su **DACL** (lista de ACEs: a qué SID se permite/niega qué acceso) y su **SACL** (auditoría). El chequeo de acceso recorre la DACL con el token del que pide. Para el reversing defensivo: una DACL **demasiado permisiva** en un servicio, una clave o un objeto con nombre es una debilidad a **reportar** (no a explotar).

## Ejemplo trabajado

*(Ejemplo **ilustrativo**: vista típica de Process Explorer / `!token` en WinDbg; valores construidos.)*

```text
bloc_lab.exe (PID 4312)   Integrity: Medium       ← editor de texto propio de laboratorio
  Token:
    User:  PC\lab  (S-1-5-21-...-1001)
    Grupos: BUILTIN\Users, ...
    Privilegios (habilitados en MAYÚSCULA):
       SeChangeNotifyPrivilege (ON)   SeShutdownPrivilege (off)
       SeDebugPrivilege (off)         ← presente pero deshabilitado
  Handles (extracto):
    0x0F8  File   C:\Users\lab\Documents\notas.txt              (el archivo que abriste)
    0x120  Key    HKCU\Software\BlocLab\Settings                (su propia config)
    0x134  Mutant \Sessions\1\BaseNamedObjects\BlocLab_SingleInstance
```

Lectura: proceso propio de integridad **Medium**, con `SeDebugPrivilege` **presente pero apagado** (no está usando debug de otros procesos ahora). Los handles muestran el documento que abriste, su **propia** clave de configuración y un **mutex** de instancia única. En un análisis real, el nombre del mutex o una ruta son **pistas** a corroborar, no evidencia por sí solos.

## Práctica segura

En tu VM, con un **programa propio** (o Process Explorer sobre uno benigno):

1. Con **Process Explorer**, abrí un proceso propio y mirá su cuenta y sus **handles**. Para los grupos y privilegios de tu sesión, ejecutá `whoami /all`; anotá cuáles figuran habilitados y cuáles no.
2. Identificá handles a un archivo, una clave y un objeto con nombre (evento/mutex). Si el proceso no tiene uno de esos objetos, anotalo: no hace falta crearlo para completar la observación.
3. Compará el token del proceso propio con el de la sesión solo si ambos pertenecen a la misma cuenta y nivel de integridad; no eleves privilegios para la práctica.
4. Mirá la **DACL** de un objeto propio (p. ej. `icacls` sobre un archivo tuyo) y explicá quién tiene qué.

## Entregable

Una ficha del proceso: nivel de integridad, privilegios habilitados, 3–5 handles relevantes (con qué objeto) y una observación sobre la DACL de uno de esos objetos. Solo observación, sin modificar permisos.

## Preguntas de repaso

?? ¿Qué es un handle y qué guarda además del objeto?
!! Un índice en la **tabla de handles** privada del proceso que apunta a un objeto del kernel; guarda también la **access mask** (los permisos con que se abrió). El proceso opera por el handle, no sobre el objeto directo.

?? ¿Qué define lo que un proceso puede hacer sobre un objeto?
!! La comparación de su **token** (SIDs, privilegios, nivel de integridad) contra la **DACL** del objeto. Si la DACL no concede el acceso pedido para ese SID, se rechaza.

?? ¿Qué diferencia hay entre un privilegio "presente" y uno "habilitado"?
!! Presente = el token lo tiene en su lista; habilitado = está **activo** ahora. Muchos privilegios potentes vienen presentes pero deshabilitados y hay que habilitarlos para usarlos; en el análisis te fijás cuáles están **ON**.

?? ¿Para qué sirve el nivel de integridad?
!! Es una barrera: un proceso de integridad **baja** no puede escribir en objetos de integridad **mayor**. Es la base de los sandboxes (p. ej. el del navegador).

?? ¿Por qué un mutex con nombre es interesante al analizar, y qué cuidado hay que tener?
!! Suele ser el mecanismo de **instancia única** ("ya estoy corriendo"), así que es una **pista** útil. Pero su nombre **por sí solo no es un IOC**: un nombre genérico puede coincidir con software legítimo; sirve como indicio a **corroborar** con más contexto.

:::{nota} Puerta de salida (optativa)
Podés: (1) explicar el modelo objeto/handle/access-mask; (2) leer un token (SIDs, privilegios ON/off, integridad); (3) relacionar token + DACL en un chequeo de acceso; (4) sacar evidencia (handles, mutex) de un proceso propio sin modificarlo.
:::

## Fuentes

- **Conocimiento externo** (Microsoft Learn; páginas concretas): [Handles and Objects](https://learn.microsoft.com/en-us/windows/win32/sysinfo/handles-and-objects), [Process Explorer](https://learn.microsoft.com/en-us/sysinternals/downloads/process-explorer), [Access Tokens](https://learn.microsoft.com/en-us/windows/win32/secauthz/access-tokens), [Privileges](https://learn.microsoft.com/en-us/windows/win32/secauthz/privileges), [Mandatory Integrity Control](https://learn.microsoft.com/en-us/windows/win32/secauthz/mandatory-integrity-control) y [Access Control Lists](https://learn.microsoft.com/en-us/windows/win32/secauthz/access-control-lists). No se citan versiones ni valores reales: el ejemplo es ilustrativo.
- **Tie con CLS:** la lectura del **PEB** y el contexto de proceso aparecen en [2.15 Anti-análisis](02-anti-analisis.html); el robo de token en kernel se menciona (de forma ofensiva, fuera de alcance) en los tutes 49–69 del Curso IDA, que acá **no** se usan como guía.

:::{nota} Etiquetas
**Observado en CLS:** solo el PEB/contexto de 2.15 (referencia). **Conocimiento externo:** todo el modelo de seguridad. **Ejemplo ilustrativo:** la vista de token/handles. **Laboratorio verificado:** ninguno en esta edición (no hay binario compilado con datos reales); la práctica se hace sobre procesos propios en tu VM.
:::
