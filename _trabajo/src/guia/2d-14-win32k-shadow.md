---
title: "2D.14 · El Subsistema Gráfico en Modo Kernel (win32k) y la Tabla de Servicios Sombra"
description: "Arquitectura de win32kbase.sys y win32kfull.sys, despacho a través de KeServiceDescriptorTableShadow, callbacks de kernel a usuario (KeUserModeCallback) y mitigaciones Win32k Lockdown."
etapa: "Etapa 2 · 2D · Windows internals (optativa)"
---

# El Subsistema Gráfico en Modo Kernel (win32k) y la Tabla de Servicios Sombra

:::{nota} Propósito y Relevancia
En la arquitectura de Windows, el modo kernel no solo alberga los servicios de sistema estándar del ejecutivo y del gestor de memoria (`ntoskrnl.exe`). También aloja el subsistema de ventanas, interfaz gráfica y gestión de dispositivos de entrada (**GDI y USER**). Este subsistema está implementado en controladores de sistema especiales (`win32kbase.sys`, `win32kfull.sys` y el driver legado `win32k.sys`). Con más de 1.200 llamadas al sistema que históricamente han constituido la mayor superficie de ataques de escalada local de privilegios (LPE) en Windows, su análisis es obligatorio para cualquier investigador de seguridad.
:::

---

## 1. Descomposición de Win32k y Arquitectura Modular

En versiones antiguas de Windows (hasta Windows 7 y 8.1), toda la lógica gráfica residía en un único driver monolítico de gran tamaño: `win32k.sys`. Desde Windows 10, Microsoft refactorizó el subsistema en módulos especializados para reducir el acoplamiento y mejorar la telemetría:

```text
+─────────────────────────────────────────────────────────────────────────────+
|                         ESPACIO DE USUARIO (x64)                            |
|  [ user32.dll ]               [ gdi32.dll / gdi32full.dll ]                 |
|         │                                    │                              |
|         ▼                                    ▼                              |
|  [ win32u.dll ] ─── (Stubs de syscall gráfica: 0x1000 + Servicio)           |
+─────────────────────────────────────────────────────────────────────────────+
                                       │ (syscall)
+──────────────────────────────────────┼──────────────────────────────────────+
|                         ESPACIO DE KERNEL (x64)                             |
|                                      ▼                                      |
|  KeServiceDescriptorTableShadow [Índice 1: Descriptor de Servicios Win32k]  |
|                                      │                                      |
|         ┌────────────────────────────┴─────────────────────────────┐        |
|         ▼                                                          ▼        |
|  win32kbase.sys                                             win32kfull.sys  |
|  (Gestión de memoria gráfica,                               (Lógica pesada: |
|   handles de ventana, threads GUI,                          mensajes WM_*,  |
|   DirectComposition y primitivas base)                      renderizado GDI)|
+─────────────────────────────────────────────────────────────────────────────+
```

### El Módulo de Transición en Modo Usuario: `win32u.dll`
Históricamente, las funciones de `user32.dll` (como `CreateWindowExW`) invocaban directamente la instrucción `syscall`. En Windows 10 y 11 modernos, Microsoft centralizó todos los stubs de llamadas al sistema gráficas dentro de una DLL de bajo nivel llamada **`win32u.dll`**. Cualquier llamada de alto nivel en `user32.dll` o `gdi32.dll` pasa primero por un stub `NtUser*` o `NtGdi*` dentro de `win32u.dll`.

---

## 2. Despacho por la Tabla Sombra: `KeServiceDescriptorTableShadow`

En la Lección 2.15 vimos cómo las llamadas al sistema nativas (`NtOpenProcess`, `NtAllocateVirtualMemory`) se despachan mediante la tabla global exportada `KeServiceDescriptorTable`. Sin embargo, los servicios gráficos utilizan una tabla extendida no exportada: **`KeServiceDescriptorTableShadow`**.

### Estructura de la Tabla Sombra
La estructura contiene un arreglo de dos descriptores de servicio (`KSERVICE_TABLE_DESCRIPTOR`):
- **Entrada 0 (Servicios Nativos del Kernel):** Apunta a las funciones `ntoskrnl.exe` (`Nt*` clásicas con SSN `0x0000` a `0x0200+`).
- **Entrada 1 (Servicios Gráficos Win32k):** Apunta a las funciones despachadas por `win32kbase.sys` y `win32kfull.sys`.

### Conversión de Números de Servicio (SSN Gráfico)
Las syscalls de Win32k poseen un bit indicador activo (`0x1000`). Cuando una instrucción `syscall` se ejecuta con `EAX = 0x1000 + N`:
1. El despachador `nt!KiSystemCall64` comprueba si el número de servicio excede `0x0FFF`.
2. Si es así, verifica si el hilo actual ya ha sido promovido a **GUI Thread** (es decir, si el campo `KTHREAD->Win32Thread` en `GS:[0x188]` no es nulo).
3. Si el hilo es estándar, el kernel invoca `nt!PsConvertToGuiThread` para asignar el stack de kernel extendido requerido por win32k (un stack de 64 KB en lugar del stack estándar de 24 KB).
4. El kernel toma la entrada 1 de `KeServiceDescriptorTableShadow` y salta a la función correspondiente indexando el offset `N` en la tabla de despacho.

---

## 3. El Fenómeno Crítico: Inversión de Control con `KeUserModeCallback`

La razón principal por la cual Win32k ha sido la mayor fuente histórica de vulnerabilidades de kernel (Use-After-Free y elevación de privilegios) es su necesidad de interactuar con el espacio de usuario mientras procesa llamadas de kernel:

### Mecánica de Inversión
Cuando una función en modo kernel dentro de `win32kfull.sys` necesita notificar a una ventana (por ejemplo, para ejecutar un hook de ventana global o despachar un mensaje `WM_NCCREATE`), el kernel no puede ejecutar la función de ventana directamente en modo kernel.
1. El driver de kernel invoca **`nt!KeUserModeCallback`**.
2. Esta función guarda el estado actual del stack de kernel, prepara un frame de retorno hacia el modo usuario y salta a la rutina `ntdll!KiUserCallbackDispatcher` en el proceso.
3. El código de usuario procesa el mensaje (ejecutando callbacks como `__ClientLoadLibrary`).
4. Al concluir, el modo usuario invoca la syscall nativa `NtCallbackReturn` para devolver el control al driver de kernel en el punto exacto donde se suspendió.

### El Riesgo de Seguridad (Race Conditions y Reentrancia)
Durante el tiempo en que el control está en espacio de usuario a través de `KeUserModeCallback`, el proceso puede ejecutar código malicioso que destruya o libere la ventana o el objeto GDI (`DestroyWindow`) sobre el cual el kernel estaba operando. Cuando el control regresa a `win32kfull.sys`, si el driver asume que el objeto sigue existiendo en el puntero original sin revalidar su estado de bloqueo, se produce un fallo clásico de **Use-After-Free (UAF)** en espacio de kernel.

---

## 4. Mitigaciones Modernas: Win32k Lockdown

Para neutralizar esta inmensa superficie de ataque, Microsoft introdujo en Windows 10/11 la política **Win32k System Call Disablement Policy** (también conocida como **Win32k Lockdown**):
- Mediante la API `SetProcessMitigationPolicy` con la clase `ProcessSystemCallDisablePolicy`, un proceso puede auto-despojarse permanentemente del derecho de invocar llamadas a la tabla sombra.
- Procesos altamente expuestos a contenido no confiable (como los procesos de renderizado de Google Chrome, Microsoft Edge y sandboxes de visualización) activan esta mitigación. Si un exploit intenta invocar cualquier syscall gráfica (`0x1000+`), el despachador de kernel lanza inmediatamente una excepción de violación de acceso y termina el proceso.

### Inspección en WinDbg
```text
$$ Inspeccionar si un proceso tiene deshabilitadas las llamadas a Win32k
dt nt!_EPROCESS <ProcessAddress> MitigationFlags
$$ El bit 0x04 (DisallowWin32kSystemCalls) indica que el proceso tiene Win32k bloqueado
```
