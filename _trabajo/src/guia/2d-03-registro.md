---
title: "2D.3 · Registro de Windows: hives, permisos, WOW64 y análisis defensivo"
description: "Qué es el registro, cómo se organiza en hives, permisos y redirección WOW64, y cómo observar cambios y persistencia de forma defensiva. Rama optativa 2D."
etapa: "Etapa 2 · 2D · Windows internals (optativa)"
---

# Registro de Windows: hives, permisos, WOW64 y análisis defensivo

:::{aviso} Rama optativa 2D
Lección de la [rama optativa 2D](../2d.html). Defensiva: **observar y detectar** cambios en el registro; no crear persistencia encubierta.
:::

:::{nota} Propósito
Entender cómo está organizado el registro (hives, claves, valores), quién puede escribir dónde (permisos), la redirección **WOW64** para apps de 32 bits, y cómo **observar** qué toca un programa propio (configuración y persistencia) con evidencia.
:::

**Prerrequisitos**

- *Obligatorios:* objetos y ACL ([2D.1](2d-01-objetos.html)), procesos ([1.3](01-procesos.html)).
- *Recomendados:* malware estático ([5.1](05-malware.html)).

## Hives y organización

El registro es una base jerárquica de **claves** (carpetas) y **valores** (datos tipados). Las cinco raíces predefinidas (`HKLM`, `HKCU`, `HKCR`, `HKU`, `HKCC`) no corresponden todas a archivos físicos uno a uno: los **hives** son unidades cargadas desde archivos como `SYSTEM`, `SOFTWARE` y el `NTUSER.DAT` de cada usuario; algunas raíces son alias o vistas. `HKCU` apunta al hive del usuario actual; `HKCR` combina las clases de máquina y usuario (`HKLM\Software\Classes` y `HKCU\Software\Classes`); `HKCC` representa la configuración de hardware actual. **Conocimiento externo** (Microsoft Learn).

Zonas que importan en el análisis defensivo:

- **Persistencia:** `...\CurrentVersion\Run`/`RunOnce` (en `HKLM` y `HKCU`), servicios (`HKLM\SYSTEM\CurrentControlSet\Services`), y otras claves de autoarranque.
- **Configuración de apps:** cada programa suele guardar lo suyo bajo `HKCU\Software\<Fabricante>\<App>`.

## Permisos

Cada clave es un **objeto asegurable** con su DACL (como viste en [2D.1](2d-01-objetos.html)). Por eso `HKLM` (de máquina) normalmente requiere administrador y `HKCU` (del usuario) lo puede escribir el propio usuario. Una clave de autoarranque con permisos **demasiado abiertos** (escribible por usuarios sin privilegio) es una debilidad a **reportar**.

## Redirección WOW64

Un proceso de **32 bits** en Windows de 64 bits usa la vista de 32 bits para determinadas claves. Por ejemplo, `HKLM\Software` está redirigida en las versiones actuales de Windows: una app x86 que acceda a `HKLM\Software\BlocLab` puede aparecer en la vista de 32 bits que Regedit muestra bajo `HKLM\Software\WOW6432Node\BlocLab`. **No todas las claves se redirigen**; algunas son compartidas, y el resultado depende de la clave y de la versión de Windows. Para un caso real, consultá la tabla oficial de claves afectadas y no agregues `WOW6432Node` a mano en código nuevo.

## Observar cambios (defensivo)

- **Diferencial:** **Regshot** saca un snapshot antes y después de ejecutar; te da la lista exacta de claves/valores creados o cambiados.
- **En vivo:** **Process Monitor** con filtro de operaciones de registro (`RegSetValue`, `RegCreateKey`) muestra quién tocó qué y cuándo, con el stack.

## Ejemplo trabajado

*(Ejemplo **ilustrativo**: salida resumida de Regshot sobre una app de laboratorio; valores construidos.)*

```text
Regshot — diff antes/después de correr bloc_lab.exe (x86) en la VM:
  Valores agregados:
    HKCU\Software\BlocLab\Settings\Theme = "dark"        ← su config propia (vista compartida)
    HKLM\Software\WOW6432Node\BlocLab\Build = "lab-1"    ← vista x86 de HKLM\Software (app 32-bit)
  (sin cambios en HKLM ni en claves Run)
```

Lectura: la app guardó su configuración de usuario en `HKCU` y, en este ejemplo, escribió también en la vista x86 de su clave de máquina `HKLM\Software`. El diff aparece resumido con la ruta física `WOW6432Node`; el acceso de la app fue a la vista lógica de 32 bits. **No** tocó `Run`: el ejemplo no muestra cambios de autoarranque. Es una ilustración de las vistas, no una regla aplicable a cualquier clave.

## Práctica segura

En tu VM, con un **programa propio** que guarde configuración en el registro:

1. **Regshot:** snapshot → corré el programa → segundo snapshot → *compare*. Anotá qué claves/valores agregó.
2. Si es de 32 bits, confirmá la **redirección WOW64** (aparece bajo `WOW6432Node`).
3. En Regedit, abrí **Permisos** de la clave propia y observá su **DACL**. No cambies permisos. `icacls` trabaja con archivos y no es la herramienta para inspeccionar claves del registro.
4. Confirmá que la práctica no cambió claves de autoarranque. Si necesitás practicar la lectura de una clave `Run`, usá una captura o exportación de ejemplo; no la crees ni la modifiques en el equipo.

## Entregable

Lista de claves/valores de configuración que tu programa propio creó o modificó (con su tipo), si hubo redirección WOW64, y una observación de permisos de una clave propia. Incluí evidencia de que no cambiaste claves de autoarranque.

## Preguntas de repaso

?? ¿Qué es un hive y cómo se relaciona con `HKCU`/`HKLM`?
!! Una unidad lógica de datos del registro que Windows carga y respalda, por ejemplo, con `NTUSER.DAT` o `SOFTWARE`. Las raíces predefinidas no son todas archivos ni hives uno a uno: `HKCU` apunta al usuario actual y `HKCR` es una vista combinada.

?? ¿Por qué `HKLM` suele requerir administrador y `HKCU` no?
!! Por la **DACL** de cada clave: las de máquina (`HKLM`) conceden escritura a administradores; el hive del usuario (`HKCU`) lo puede escribir el propio usuario. Son objetos asegurables.

?? Una app de 32 bits dice escribir en `HKLM\Software\Foo` pero no la ves ahí. ¿Dónde está?
!! Si esa clave está entre las afectadas, la app x86 accede a la vista de 32 bits y Regedit de 64 bits suele mostrarla bajo `HKLM\Software\WOW6432Node\Foo`. Hay que confirmar el comportamiento para la clave concreta: WOW64 también tiene claves compartidas.

?? ¿Cómo obtenés la lista exacta de lo que tocó un programa en el registro?
!! Con un **diferencial** (Regshot: snapshot antes/después) o en vivo con **Process Monitor** filtrando operaciones de registro. El diff te da claves/valores agregados o cambiados.

?? ¿Qué hace "peligrosa" a una clave de autoarranque?
!! Que su **DACL** permita escribir a usuarios sin privilegio: cualquiera podría poner algo que se ejecute al inicio. Es una debilidad a **reportar**, no a aprovechar.

:::{nota} Puerta de salida (optativa)
Podés: (1) explicar hives y las vistas `HKCU`/`HKLM`/`HKCR`; (2) relacionar permisos de clave con su DACL; (3) reconocer la redirección WOW64; (4) sacar con Regshot/Procmon la lista de cambios de un programa propio y dejar el sistema limpio.
:::

## Fuentes

- **Conocimiento externo** (Microsoft Learn): [Registry Hives](https://learn.microsoft.com/en-us/windows/win32/sysinfo/registry-hives), [Structure of the Registry](https://learn.microsoft.com/en-us/windows/win32/sysinfo/structure-of-the-registry), [Registry Key Security and Access Rights](https://learn.microsoft.com/en-us/windows/win32/sysinfo/registry-key-security-and-access-rights), [Registry Redirector (WOW64)](https://learn.microsoft.com/en-us/windows/win32/winprog64/registry-redirector) y [Registry Keys Affected by WOW64](https://learn.microsoft.com/en-us/windows/win32/winprog64/shared-registry-keys).
- **Tie con CLS:** objetos asegurables y DACL en [2D.1](2d-01-objetos.html); la persistencia por `Run` también aparece como IOC en la rama de malware.

:::{nota} Etiquetas
**Observado en CLS:** solo el marco de ACL (2D.1) y la noción de persistencia. **Conocimiento externo:** estructura del registro, permisos y WOW64. **Ejemplo ilustrativo:** el diff de Regshot. **Laboratorio verificado:** ninguno en esta edición; la práctica se hace sobre un programa propio en tu VM, con limpieza.
:::
