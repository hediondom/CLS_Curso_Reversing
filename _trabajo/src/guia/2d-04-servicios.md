---
title: "2D.4 · Servicios: SCM, ciclo de vida, cuentas y auditoría"
description: "Cómo administra Windows sus servicios, cómo leer su ciclo de vida y configuración, y cómo auditar un servicio didáctico propio sin explotar permisos ni tocar servicios del sistema. Rama optativa 2D."
etapa: "Etapa 2 · 2D · Windows internals (optativa)"
---

# Servicios: SCM, ciclo de vida, cuentas y auditoría

:::{aviso} Rama optativa 2D
Lección optativa y defensiva. La práctica usa únicamente un servicio propio en una VM descartable; no modifica servicios de Windows ni intenta abusar de permisos.
:::

:::{nota} Propósito
Entender qué registra y controla el **Service Control Manager (SCM)**, seguir los estados de un servicio y leer su cuenta, ruta y permisos. Distinguir un servicio con ejecutable propio de uno hospedado como DLL, y terminar la práctica dejando la VM en el estado inicial.
:::

**Prerrequisitos**

- *Obligatorios:* objetos, tokens y ACL ([2D.1](2d-01-objetos.html)); registro de Windows ([2D.3](2d-03-registro.html)).
- *Recomendados:* procesos ([1.3](01-procesos.html)) y conceptos de depuración ([2.19](02-windbg-heap.html)).

## Qué controla el SCM

El **SCM** es el componente que mantiene el registro de servicios instalados, los inicia bajo demanda o al arrancar Windows, conserva sus estados y entrega solicitudes de control. Los programas administrativos consultan o cambian el servicio mediante las API del SCM; el registro contiene también datos asociados en `HKLM\SYSTEM\CurrentControlSet\Services\<nombre>`. Para este curso, consultá la configuración por las herramientas del SCM: **no edites a mano** las claves de un servicio.

Un servicio Win32 no es “una DLL que corre sola”. El programa de servicio contiene el punto de entrada y una función `ServiceMain`; el SCM se comunica con ese programa mediante el dispatcher y el handler de controles. Un ejecutable de consola cualquiera no cumple esa interfaz y no se convierte en servicio por registrarlo.

## Tipo de servicio, tipo de inicio y estado

Son conceptos distintos:

- **Tipo:** `own` (proceso propio) o `share` (programa de servicio compartido). Los tipos `kernel` y `filesys` corresponden a drivers y quedan fuera de esta lección.
- **Tipo de inicio:** `demand` es inicio manual; `auto` inicia con Windows; `delayed-auto` lo inicia más tarde; `disabled` impide iniciarlo. `boot` y `system` son opciones de inicio para drivers, no para el servicio didáctico de esta práctica.
- **Estado actual:** `STOPPED`, `START_PENDING`, `RUNNING`, `STOP_PENDING` o `PAUSED`. El tipo de inicio describe cuándo puede arrancar; el estado describe qué está pasando ahora.

Al entrar en `ServiceMain`, el programa registra su handler de controles y comunica estados al SCM. Durante una inicialización larga informa que el inicio sigue pendiente; al detenerse, procesa la solicitud y notifica el estado final.

## Ejecutables y servicios hospedados

Un servicio puede ejecutarse en un proceso propio o compartir un programa anfitrión. Windows usa `svchost.exe` para hospedar algunos de sus servicios; la organización de los grupos y procesos varía según la versión y la configuración. `svchost.exe` es un componente del sistema, no una plantilla para registrar servicios propios.

Algunos servicios hospedados cargan una DLL indicada por su configuración, que suele aparecer como `ServiceDll` bajo `Parameters`. Esto se analiza **en lectura**: el valor permite relacionar servicio, proceso anfitrión y módulo. No se cambia el valor ni se reemplaza la DLL. Para comprender el mecanismo, consultá la documentación de programas de servicio y el artículo de agrupación de `svchost`; no supongas que todos los servicios usan este modelo.

## Cuenta y permisos

Cada servicio se ejecuta con un token asociado a una cuenta. `LocalSystem` tiene privilegios amplios; `LocalService` y `NetworkService` tienen perfiles distintos y más limitados. Un servicio bien configurado usa la cuenta de menor privilegio que necesite.

La DACL del **objeto servicio** controla quién puede consultarlo, iniciarlo, detenerlo o cambiar su configuración. Es distinta de la ACL del ejecutable y de sus carpetas. Para una auditoría defensiva, registrá si la ruta existe, quién puede modificar sus archivos y qué permisos tienen las cuentas sobre el objeto servicio. Un permiso de cambio de configuración tiene impacto alto porque permite alterar los datos que el SCM usa; documentá una asignación excesiva, pero no la pruebes ni la aproveches.

## Ejemplo trabajado

*(Ejemplo **ilustrativo**, no observado en un Windows real. Los nombres y valores son de un servicio ficticio de laboratorio.)*

```text
Nombre: CLSLabSvc
Tipo: own-process (servicio Win32)
Tipo de inicio: demand (manual)
Estado: STOPPED
Cuenta: NT AUTHORITY\LocalService
ImagePath: C:\CLS-Lab\SvcLab.exe
Objeto servicio: Administrators — control; Users — lectura
Carpeta del binario: solo administradores pueden modificarla
```

Lectura: es un servicio didáctico de proceso propio, detenido y de inicio manual. La cuenta elegida tiene menos privilegios que `LocalSystem`; la ruta y los permisos son coherentes con esa práctica. Esta ficha no demuestra que un servicio real sea seguro: cada hallazgo debe corroborarse con la configuración efectiva y el contexto del equipo.

## Práctica segura: servicio propio y limpieza

Realizá el ejercicio solo en una VM descartable con snapshot. Se requiere un `SvcLab.exe` propio, compilado como **servicio Win32** (con dispatcher, `ServiceMain` y handler); un ejecutable de consola genérico no sirve. La guía no incluye un binario compilado ni verificó esta práctica en esta edición.

**Materiales y resultado esperado:** VM/build registrados, snapshot recuperable, `sc.exe`, AccessChk de Sysinternals y el binario propio identificado por hash. El resultado esperado es registrar un servicio manual, verlo pasar a `RUNNING` y `STOPPED`, y confirmar que desaparece después de solicitar su eliminación. Guardá el build de Windows, hash, salidas de consulta y evidencia de limpieza; no se fija una versión de herramienta que no se haya probado.

**Paso 1 — Preparar.** Prepará `C:\CLS-Lab` y colocá allí el binario propio. No uses una ruta de red ni un servicio de Windows.

**Paso 2 — Registrar.** En una consola elevada de la VM, registrá el servicio con inicio manual y una cuenta de menor privilegio:

   ```bat
   sc.exe create CLSLabSvc binPath= "C:\CLS-Lab\SvcLab.exe" start= demand obj= "NT AUTHORITY\LocalService"
   ```

**Paso 3 — Inspeccionar.** Consultá su configuración y estado; auditá la DACL del objeto servicio sin modificarla:

   ```bat
   sc.exe qc CLSLabSvc
   sc.exe query CLSLabSvc
   accesschk.exe -v -c CLSLabSvc
   ```

**Paso 4 — Probar el ciclo de vida.** Iniciá y detené solo `CLSLabSvc`. Observá los cambios de estado y anotá la cuenta y la ruta reportadas.

**Paso 5 — Limpiar.** Detené el servicio si sigue activo y solicitá eliminar únicamente el servicio de laboratorio:

   ```bat
   sc.exe stop CLSLabSvc
   sc.exe delete CLSLabSvc
   sc.exe query CLSLabSvc
   ```

   `sc.exe delete` puede dejarlo marcado para borrar si todavía está activo o si hay una consola con un handle abierto. Cerrá `services.msc` y las herramientas que lo estén consultando; esperá a que desaparezca o revertí el snapshot. Confirmá que `sc.exe query CLSLabSvc` ya no encuentra el servicio y recién entonces borrá `C:\CLS-Lab`.

No cambies permisos, configuración ni cuenta de otros servicios. Si no tenés un binario propio que implemente el contrato de servicio, hacé el análisis como ejercicio de lectura con la ficha ilustrativa y dejá constancia de esa limitación.

## Entregable

Una ficha con tipo, inicio, estado, cuenta, ruta, resultado de la inspección de permisos y evidencia de limpieza. Indicá si trabajaste con un servicio compilado o solo con el ejemplo ilustrativo. No incluyas datos personales de la VM.

## Preguntas de repaso

?? ¿Qué responsabilidad tiene el SCM?
!! Mantiene el registro de servicios, los inicia, conserva su estado y envía solicitudes de control.

?? ¿En qué se diferencian el tipo de inicio y el estado?
!! El tipo de inicio determina cuándo puede comenzar; el estado indica si está detenido, iniciándose, activo, deteniéndose o pausado.

?? ¿Un ejecutable de consola se vuelve servicio al registrarlo?
!! No. El programa debe implementar el dispatcher de servicios, `ServiceMain` y el handler de controles.

?? ¿Qué diferencia hay entre el objeto servicio y los permisos del archivo ejecutable?
!! La DACL del objeto controla operaciones sobre el servicio; la ACL del archivo y sus carpetas controla quién puede leer, ejecutar o modificar esos archivos. Se auditan por separado.

?? ¿Qué significa que `sc.exe delete` no lo haya quitado inmediatamente?
!! Puede estar marcado para eliminación porque sigue activo o porque otro programa conserva un handle. Cerrá las consolas que lo consultan, esperá y verificá su ausencia antes de borrar los archivos.

:::{nota} Puerta de salida (optativa)
Podés explicar SCM, `ServiceMain`, tipo de inicio y estado; leer cuenta, ruta y permisos; distinguir un proceso propio de un servicio hospedado; y demostrar que el servicio de prueba desapareció o declarar que solo completaste el ejercicio ilustrativo.
:::

## Fuentes

- **Conocimiento externo:** [Service Control Manager](https://learn.microsoft.com/en-us/windows/win32/services/service-control-manager), [Service Programs](https://learn.microsoft.com/en-us/windows/win32/services/service-programs), [ServiceMain](https://learn.microsoft.com/en-us/windows/win32/services/service-servicemain-function), [Service User Accounts](https://learn.microsoft.com/en-us/windows/win32/services/service-user-accounts) y [Service Security and Access Rights](https://learn.microsoft.com/en-us/windows/win32/services/service-security-and-access-rights).
- **Herramientas:** [`sc.exe create`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/sc-create), [`sc.exe delete`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/sc-delete) y [AccessChk](https://learn.microsoft.com/en-us/sysinternals/downloads/accesschk).
- **Hospedaje:** [Service host grouping in Windows](https://learn.microsoft.com/en-us/windows/application-management/svchost-service-refactoring). Los detalles de agrupación dependen de la versión de Windows.
- **Relación con CLS:** ACL y token en [2D.1](2d-01-objetos.html); representación del registro en [2D.3](2d-03-registro.html).

:::{nota} Etiquetas
**Observado en CLS:** marco de token/ACL (2D.1) y referencia al registro (2D.3). **Conocimiento externo:** SCM, estados, cuentas y servicios hospedados. **Ejemplo ilustrativo:** ficha de `CLSLabSvc`. **Laboratorio verificado:** no; requiere un binario propio compilado como servicio.
:::
