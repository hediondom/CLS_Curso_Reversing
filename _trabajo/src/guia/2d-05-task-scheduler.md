---
title: "2D.5 · Task Scheduler: leer tareas y detectar cambios"
description: "Analizar definiciones XML, triggers, acciones, contexto de seguridad y visibilidad de tareas programadas con herramientas de solo lectura. Rama optativa 2D."
etapa: "Etapa 2 · 2D · Windows internals (optativa)"
---

# Task Scheduler: leer tareas y detectar cambios

:::{aviso} Rama optativa 2D
Lección optativa de análisis defensivo. La práctica inspecciona tareas existentes y exporta su definición; no crea, modifica, ejecuta ni oculta tareas.
:::

:::{nota} Propósito
Entender de qué partes se compone una tarea programada y reconstruir, a partir de sus metadatos y XML, **qué se ejecuta, cuándo y bajo qué identidad**. Aprender a separar una configuración poco habitual de una conclusión de compromiso.
:::

**Prerrequisitos**

- *Obligatorios:* registro y contexto de seguridad ([2D.1](2d-01-objetos.html), [2D.3](2d-03-registro.html)).
- *Recomendados:* servicios y SCM ([2D.4](2d-04-servicios.html)); procesos ([1.3](01-procesos.html)).

## Partes de una tarea

Una tarea registrada combina una **acción** con uno o más **triggers** y ajustes. La definición también describe el **principal** (la identidad y el nivel con que se ejecuta) y datos de registro como nombre, autor, descripción y ruta lógica (URI). El XML permite revisar estos elementos juntos.

- **Trigger:** condición temporal o de evento que solicita la ejecución, por ejemplo, un horario o el inicio de sesión.
- **Action:** lo que Task Scheduler ejecuta y sus argumentos. Revisá ruta, firma y relación con el software instalado.
- **Principal / contexto:** cuenta, tipo de inicio de sesión y nivel de ejecución. `RunLevel` no concede privilegios por sí mismo; importa junto con la identidad, sus derechos y la configuración de la tarea.
- **Settings:** habilitación, restricciones, límites y propiedad `Hidden`.
- **RegistrationInfo:** autor, descripción, fecha, URI y otros datos administrativos.

## Visibilidad y auditoría

`Hidden=true` indica que la tarea no se muestra normalmente en la interfaz; no la vuelve invisible para un administrador ni demuestra que sea maliciosa. Una tarea puede ser legítima y poco conocida. Evaluá el conjunto: acción y argumentos, firma y ubicación del ejecutable, trigger, principal, nivel, autor, permisos y coherencia con el software instalado.

La revisión es **de solo lectura**. Podés usar el Programador de tareas para abrir la pestaña de propiedades y exportar el XML, o consultar una tarea específica con herramientas de Windows. No deshabilites ni borres una tarea desconocida durante el análisis; preservá los datos y pedí revisión al administrador responsable.

## Ejemplo trabajado

*(Fragmento **ficticio e incompleto**, solo para aprender a leer campos; no es un XML para registrar.)*

```xml
<RegistrationInfo>
  <Author>CLS Lab</Author>
  <Description>Comprobación local de estado</Description>
</RegistrationInfo>
<Triggers>
  <TimeTrigger><Enabled>false</Enabled></TimeTrigger>
</Triggers>
<Principals>
  <Principal id="Author">
    <UserId>PC-LAB\alumno</UserId>
    <RunLevel>LeastPrivilege</RunLevel>
  </Principal>
</Principals>
<Settings><Hidden>false</Hidden></Settings>
<Actions Context="Author">
  <Exec>
    <Command>C:\CLS-Lab\status.exe</Command>
    <Arguments>--once</Arguments>
  </Exec>
</Actions>
```

Lectura: la acción apunta a un ejecutable local y lleva el argumento `--once`; el trigger está deshabilitado en este fragmento; el principal es un usuario de laboratorio con nivel `LeastPrivilege`; y `Hidden` es falso. Como el ejemplo está incompleto y ficticio, no permite registrar ni evaluar una tarea real.

## Práctica segura: inspección de solo lectura

En una VM de laboratorio o en un equipo donde tengas autorización, elegí una tarea conocida y no crítica del sistema o de una aplicación instalada. No la ejecutes ni cambies su configuración.

1. Abrí sus propiedades en Task Scheduler y anotá nombre/URI, autor, descripción y estado habilitado/deshabilitado.
2. Revisá trigger, acción y argumentos. Confirmá si el archivo existe y consultá su firma sin abrirlo ni ejecutarlo.
3. Anotá principal, tipo de inicio de sesión, nivel de ejecución y si `Hidden` figura en las propiedades o en el XML.
4. Exportá el XML a una carpeta temporal del laboratorio y revisá los mismos campos. Si vas a compartir el informe, quitá nombres de usuario, rutas personales y otros datos privados.
5. Compará la tarea con la documentación del producto o con otra referencia confiable. Si algo no coincide, describilo como **anomalía para investigar**, no como prueba de malware.
6. Eliminá solo la copia exportada si ya no la necesitás. No borres ni deshabilites la tarea analizada.

## Entregable

Una ficha con URI/nombre, autor, trigger, acción y argumentos, principal, nivel, valor `Hidden`, procedencia conocida y fuente usada para la comparación. Cerrá con una conclusión calibrada: normal, no explicado o requiere revisión; indicá qué evidencia falta.

## Preguntas de repaso

?? ¿Qué diferencia hay entre trigger y acción?
!! El trigger define **cuándo** se solicita ejecutar la tarea; la acción define **qué** programa o comando ejecuta Task Scheduler.

?? ¿Qué datos del principal conviene leer?
!! La identidad, el tipo de inicio de sesión y el nivel de ejecución; deben interpretarse junto con los derechos de esa cuenta.

?? ¿`Hidden=true` significa que la tarea es invisible o maliciosa?
!! No. Cambia su visibilidad normal en la interfaz, pero no la oculta a un administrador ni demuestra intención maliciosa.

?? ¿Qué hacés si encontrás una acción o ruta que no reconocés?
!! Registrás los datos, conservás la evidencia y contrastás con una fuente confiable o con el administrador; no ejecutás, deshabilitás ni borrás la tarea durante el análisis.

:::{nota} Puerta de salida (optativa)
Podés explicar trigger, acción, principal y ajustes; leer esos campos en XML; describir el efecto limitado de `Hidden`; y fundamentar una anomalía sin convertirla en una acusación no corroborada.
:::

## Fuentes

- **Conocimiento externo:** [About the Task Scheduler](https://learn.microsoft.com/en-us/windows/win32/taskschd/about-the-task-scheduler), [Tasks](https://learn.microsoft.com/en-us/windows/win32/taskschd/tasks), [Security Contexts for Running Tasks](https://learn.microsoft.com/en-us/windows/win32/taskschd/security-contexts-for-running-tasks), [Task Registration Information](https://learn.microsoft.com/en-us/windows/win32/taskschd/task-registration-information) y [Task Scheduler schema](https://learn.microsoft.com/en-us/windows/win32/taskschd/task-scheduler-schema).
- **Propiedad de visibilidad:** [TaskSettings.Hidden](https://learn.microsoft.com/en-us/windows/win32/taskschd/tasksettings-hidden).
- **Consulta:** [`schtasks.exe`](https://learn.microsoft.com/en-us/windows/win32/taskschd/schtasks).
- **Relación con CLS:** permisos del registro en [2D.3](2d-03-registro.html), contexto de tokens en [2D.1](2d-01-objetos.html) y servicios en [2D.4](2d-04-servicios.html).

:::{nota} Etiquetas
**Observado en CLS:** marco de lectura de configuración y persistencia defensiva. **Conocimiento externo:** Task Scheduler, XML, contextos, triggers y acciones. **Ejemplo ilustrativo:** fragmento ficticio no registrable. **Laboratorio verificado:** no; la práctica propuesta es de inspección de solo lectura.
:::