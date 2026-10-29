---
title: "2D.13 · Integrador Windows internals"
description: "Analizar un programa didáctico propio desde identidad y memoria hasta configuración, COM, IPC, excepciones y telemetría, reuniendo las fichas de evidencia de 2D en un informe; documentar y limpiar."
etapa: "Etapa 2 · 2D · Windows internals (optativa)"
---

# Integrador Windows internals

:::{aviso} Optativo y acotado
Usá una aplicación propia o didáctica, sin malware ni software ajeno. El integrador no crea persistencia: no instala un servicio, no registra tareas ni consumidores WMI y no cambia permisos.
:::

:::{nota} Propósito
Unir conceptos de objetos, memoria, registro, COM, IPC, excepciones y telemetría en un informe reproducible que distinga evidencia de hipótesis.
:::

**Prerrequisitos**

- *Obligatorios:* 2D.1, 2D.2 y 2D.3, más las lecciones de los mecanismos que use tu caso (por ejemplo 2D.6 y 2D.7 si usás COM, 2D.10 si usás IPC, 2D.12 si capturás ETW).
- *Recomendados:* 2D completa y 2C; no requiere 2D.8/DCOM ni modificar configuraciones de seguridad.

## Caso de laboratorio

Elegí una aplicación didáctica con un flujo inocuo y observable, idealmente propia. Definí de antemano qué datos se recopilan y qué sistemas quedan fuera. Modelo sugerido: leer una clave de configuración propia, consultar una interfaz COM propia, intercambiar un mensaje de estado por IPC y emitir un evento ETW propio. No agregar autoarranque ni ejecución automática.

## Fichas que reúne el informe

Cada lección de 2D dejó una herramienta de registro. El integrador no inventa otra: reúne las que correspondan a tu caso. Las marcadas como obligatorias son el mínimo; el resto se agrega si tu programa usa ese mecanismo.

| Lección | Ficha o tabla | En el integrador |
|---|---|---|
| [2D.1](2d-01-objetos.html) | Token, privilegios e integridad del proceso | Obligatoria |
| [2D.2](2d-02-memoria-loader.html) | Módulos y regiones relevantes | Obligatoria |
| [2D.3](2d-03-registro.html) | Clave propia leída y vista consultada (usuario/máquina, 32/64) | Obligatoria |
| [2D.6](2d-06-com-interfaces.html) | Apartamento de cada hilo, tabla slot/offset/método, puntero directo o proxy | Si usás COM |
| [2D.7](2d-07-com-activacion.html) | Observación/inferencia de la activación (servidor, `ThreadingModel`, manifiesto) | Si usás COM |
| [2D.9](2d-09-wmi.html) | Ficha de evidencia WMI | Solo si inspeccionás suscripciones **existentes**; el integrador no crea ninguna |
| [2D.10](2d-10-ipc.html) | Revisión del pipe (ACL, primera instancia, remotos, modo, impersonación) | Si usás IPC |
| [2D.11](2d-11-excepciones.html) | Cronología de excepción con primera/segunda oportunidad | Si tu caso incluye una excepción controlada |
| [2D.12](2d-12-etw.html) | Ficha de la sesión ETW (nivel, keywords, pérdidas, decodificación) | Obligatoria si capturás ETW |

DCOM (2D.8), servicios (2D.4) y tareas (2D.5) quedan fuera del integrador: exigirían habilitar acceso remoto o crear persistencia.

## Ejemplo trabajado

*(Escenario construido para enseñar el método; no es una observación real ni una muestra del corpus.)*

BlocLab es una aplicación propia que lee su clave `HKCU\Software\BlocLab`, consulta una interfaz COM local y devuelve `READY` por un named pipe. El recorrido de análisis puede documentarse así:

```text
Paso 1 — proceso: BlocLab.exe, PID 4120; token estándar del usuario de laboratorio.
Paso 2 — configuración: valor Mode="demo" leído desde HKCU\Software\BlocLab.
Paso 3 — COM: el cliente solicita IID_IFakeStatus al CLSID propio {11111111-2222-3333-4444-555555555555};
         hilo cliente STA; servidor in-proc ThreadingModel=Both -> puntero directo (vtable en el módulo propio).
Paso 4 — IPC: el cliente abre \\.\pipe\BlocLabStatus y recibe READY;
         pipe creado con FILE_FLAG_FIRST_PIPE_INSTANCE y PIPE_REJECT_REMOTE_CLIENTS; ACL al logon SID.
Paso 5 — telemetría: el provider BlocLab emite StatusQuery con resultado READY;
         sesión propia, nivel informativo, 0 eventos perdidos.
Conclusión acotada: esta ejecución coincide con el flujo documentado por el programa.
Alternativa: una capa proxy podría intermediar COM; el evento ETW por sí solo no identifica al lector del pipe.
Limpieza: detener app, cerrar sesión ETW, borrar traza temporal y comparar/revertir snapshot.
```

La cadena proceso → configuración → interfaz → canal → evento es una **hipótesis de recorrido** que se valida correlacionando observaciones. La coincidencia temporal entre COM y ETW no demuestra causalidad; conserva timestamps y anota qué herramienta produjo cada dato.

## Práctica

1. Registra VM/build, programa, hash del binario propio y snapshot base.
2. Capturá solo una ejecución; observá token, módulo/segmento relevante, acceso a configuración y flujo IPC/COM que esté documentado. Completá las fichas de la tabla de arriba que correspondan.
3. Si añadís ETW, limita la traza al provider propio, detené la sesión y evita conservar payloads sensibles.
4. No ejecutes acciones desconocidas, no cambies servicio/tarea/consumidor ni DACL de componentes del sistema.
5. Cierra procesos, elimina traces/capturas temporales y comprueba las claves/archivos creados por tu programa. Revierte snapshot si el estado no coincide con el inicial.

## Entregable

Informe con alcance, mapa de componentes, evidencias fechadas, tabla observación/interpretación/alternativas, límites, hashes del material propio y checklist de limpieza firmado por quien realizó el lab. Como anexos, las fichas de 2D que aplicaron (al menos las obligatorias), cada una con su fecha y la herramienta que produjo cada dato.

## Repaso

?? ¿Qué convierte una observación en una conclusión sólida?
!! Repetibilidad, fuente/contexto, evidencia correlacionada y consideración de explicaciones alternativas.

?? ¿Por qué el integrador evita autoarranque?
!! No hace falta para demostrar los conceptos y agrega cambios persistentes difíciles de limpiar y revisar.

?? ¿Por qué el integrador no incluye DCOM ni suscripciones WMI nuevas?
!! Porque demostrarlos exigiría habilitar acceso remoto o crear persistencia, y el integrador no cambia la seguridad ni deja configuraciones permanentes.

?? ¿Cuándo se considera terminado?
!! Cuando el informe es reproducible, sus límites están declarados y cada cambio temporal se eliminó o la VM se revirtió.

:::{nota} Puerta optativa 2D
Entregás un análisis acotado, basado en evidencia, y demostración de limpieza. No se aprueba por cantidad de herramientas usadas.
:::

## Fuentes

- Documentación primaria enlazada en [2D.1](2d-01-objetos.html), [2D.2](2d-02-memoria-loader.html), [2D.3](2d-03-registro.html), [2D.6](2d-06-com-interfaces.html), [2D.7](2d-07-com-activacion.html), [2D.9](2d-09-wmi.html), [2D.10](2d-10-ipc.html), [2D.11](2d-11-excepciones.html) y [2D.12](2d-12-etw.html).
- **CLS:** método de análisis e informe en [Etapa 4](04-informe.html).

:::{nota} Etiquetas
**Observado en CLS:** método de análisis e informe. **Conocimiento externo:** integración Windows internals. **Ejemplo ilustrativo:** plantilla BlocLab. **Laboratorio verificado:** no; caso a construir con software propio.
:::
