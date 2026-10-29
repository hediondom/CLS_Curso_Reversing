---
title: "6.6 · Mitigaciones de Windows para drivers"
description: "Verificar firma, Secure Boot, HVCI/VBS, App Control (WDAC) y vulnerable driver blocklist; mapear cada control a su función, cómo leer su estado sin cambiarlo y sus límites."
etapa: "Etapa 6 · Kernel y drivers (rama optativa)"
---

# Mitigaciones de Windows para drivers

:::{aviso} Solo observación
La práctica consulta el estado vigente. No deshabilites Secure Boot, HVCI, WDAC, firma de drivers ni driver blocklist para que una muestra cargue. No apliques políticas ni actives modos de prueba en el equipo principal.
:::

:::{nota} Propósito
Relacionar controles de integridad y política con el riesgo de drivers vulnerables, y evitar confundir “activo” con “cobertura total”. Al terminar deberías poder leer el estado real de cada control en una VM, distinguir “configurado” de “en ejecución” y escribir qué protege y qué no.
:::

**Prerrequisitos**

- *Obligatorios:* [6.1 arquitectura](6-01-arquitectura-kernel.html), [6.4 revisión](6-04-revision-driver.html).
- *Recomendados:* 2D.1 tokens, Etapa 0 snapshots y nociones de Secure Boot.

## Qué protege cada control

- **Firma de driver**: ayuda a establecer origen/integridad aceptable bajo política de carga; no demuestra ausencia de bugs.
- **Secure Boot**: protege la cadena de arranque con verificación de componentes firmados; política y soporte dependen del hardware/firmware.
- **VBS/HVCI (Memory Integrity)**: usa virtualización para aislar decisiones de integridad de código del kernel y restringir código ejecutable en kernel.
- **WDAC/App Control**: permite definir qué software/drivers pueden ejecutarse según política.
- **Vulnerable driver blocklist**: bloquea un conjunto de drivers conocidos vulnerables; versión, habilitación y excepciones dependen de la versión/política.

Se complementan y pueden afectar compatibilidad. La configuración cambia entre Windows cliente/servidor y administración organizacional; registra build y fuente consultada.

## Firma de drivers: qué exige hoy la política

Desde Windows 10 versión 1607, con Secure Boot activo, Windows no carga drivers de kernel **nuevos** que no estén firmados a través del portal de hardware de Microsoft. La documentación lista excepciones para drivers con firma cruzada (equipos actualizados desde versiones anteriores, Secure Boot desactivado y certificados emitidos antes de una fecha de corte). Para probar en clientes existe la firma por **atestación**, y para laboratorio, la firma de **prueba**, que requiere un modo de arranque específico.

Consecuencias para el análisis: “está firmado” dice **quién** y **bajo qué programa** se firmó; no dice que el código sea correcto ni benigno. Un driver vulnerable legítimamente firmado sigue siendo vulnerable: para eso existe la blocklist. Y un sistema en modo de firma de prueba tiene una política de carga distinta, que hay que anotar si la VM lo usa.

## Integridad de memoria (HVCI) y VBS

La integridad de memoria, también llamada HVCI, ejecuta la integridad de código del kernel dentro del entorno aislado de VBS (con el hipervisor de Windows) y restringe asignaciones de memoria del kernel que podrían usarse para comprometerlo; también protege, entre otras cosas, el mapa de bits de CFG de los drivers. Microsoft advierte que hay drivers incompatibles y que activarla puede causar fallos de arranque, por eso en esta lección **solo se consulta**.

Cómo leer el estado, sin cambiarlo:

- `Get-CimInstance -ClassName Win32_DeviceGuard -Namespace root\Microsoft\Windows\DeviceGuard` (PowerShell elevado).
- `msinfo32`: las características de VBS aparecen al final del Resumen del sistema.

Campos de `Win32_DeviceGuard` que importan:

| Campo | Qué dice | Valores clave |
|---|---|---|
| `VirtualizationBasedSecurityStatus` | Si VBS está habilitada y corriendo | 0 no habilitada · 1 habilitada pero **no** corriendo · 2 habilitada y corriendo |
| `SecurityServicesConfigured` | Qué servicios están **configurados** | contiene 2 si la integridad de memoria está configurada |
| `SecurityServicesRunning` | Qué servicios están **corriendo** | contiene 2 si la integridad de memoria está corriendo |
| `CodeIntegrityPolicyEnforcementStatus` | Aplicación de la política de integridad de código | 0 apagada · 1 auditoría · 2 aplicada |
| `AvailableSecurityProperties` | Capacidades de hardware disponibles | hipervisor, Secure Boot, protección DMA, MBEC/GMET… |

La distinción entre **configurado** y **corriendo** es la que más errores evita: una política puede pedir HVCI y el sistema no poder ejecutarlo (por hardware, por un driver incompatible o, como documenta Microsoft para ciertas VM de Azure, por la opción de Secure Boot elegida).

## Vulnerable driver blocklist

Según la documentación vigente, desde la actualización 2022 de Windows 11 la blocklist está habilitada por defecto y puede activarse o desactivarse desde Seguridad de Windows; también se aplica cuando están activos la integridad de memoria, Smart App Control o el modo S (salvo en Windows Server 2016). Se actualiza trimestralmente y llega además con las actualizaciones mensuales.

Límites que Microsoft declara: la lista **no garantiza** bloquear todo driver vulnerable, y la versión incluida en el sistema suele ser **menos completa** que la descargable, porque algunas entradas se retienen para no romper compatibilidad. Si se aplica la versión descargable como política de App Control, el registro *CodeIntegrity/Operational* registra el evento 3099 con el nombre e identificador de la política: es una forma de **verificar** qué política está cargada sin cambiar nada.

## Secure Boot y App Control

**Secure Boot** verifica que los componentes de arranque estén firmados por autoridades confiables del firmware; su estado aparece en `msinfo32` (“Estado de arranque seguro”). Es requisito de varias de las otras protecciones y condición de la política de firma descrita arriba.

**App Control for Business** (antes WDAC) define qué código puede ejecutarse, incluidos drivers, y puede estar en modo **auditoría** (registra lo que bloquearía) o **aplicado**. Para el análisis, una política en auditoría no protege: solo deja evidencia.

## Ejemplo trabajado

*(Matriz ficticia para discusión, no estado de una máquina.)*

| Señal | Control relacionado | Qué no concluye |
|---|---|---|
| HVCI activo | integridad de código en kernel | que todo driver sea libre de fallos |
| paquete firmado | política de firma | que el código sea benigno |
| driver en blocklist | bloqueo por política | que todos los vulnerables estén listados |

Lectura de una VM de laboratorio (ilustrativa):

| Control | Estado leído | Fuente | Lectura prudente |
|---|---|---|---|
| Secure Boot | Activado | `msinfo32` | La política de firma estricta aplica a drivers nuevos |
| VBS | `VirtualizationBasedSecurityStatus = 2` | `Win32_DeviceGuard` | VBS habilitada y corriendo |
| Integridad de memoria | Configurada: sí (2); corriendo: sí (2) | `Win32_DeviceGuard` | HVCI efectiva en este arranque |
| Blocklist | Activada en Seguridad de Windows | Interfaz | Aplica la versión incluida en el sistema, no necesariamente la más reciente |
| App Control | Sin política propia; solo la del sistema | Registro *CodeIntegrity* | No hay lista de permitidos de la organización |

## Práctica de solo lectura

En la VM, consulta Windows Security / System Information y la política administrada disponible. Registra build/edición, estado informado de Secure Boot/VBS/HVCI y fuente de la blocklist. Si la política está oculta por organización, anota “no disponible”; no cambies ajustes ni instales drivers para probarla.

1. Ejecutá la consulta de `Win32_DeviceGuard` y anotá los campos de la tabla, distinguiendo configurado de corriendo.
2. Anotá el estado de Secure Boot desde `msinfo32` y si la VM usa algún modo de firma de prueba.
3. Revisá en el Visor de eventos el registro *CodeIntegrity/Operational* solo para leer qué políticas están cargadas.

## Entregable

Matriz control–estado–fuente–alcance–límite, con la distinción configurado/corriendo para VBS y HVCI. Incluí fecha/build y no publiques identificadores del equipo.

## Repaso

?? ¿Firma significa que el driver es seguro?
!! No. Indica una propiedad de identidad/integridad bajo una política de confianza, no corrección ni ausencia de comportamiento malicioso.

?? ¿La blocklist cubre cualquier driver vulnerable?
!! No. Es una lista mantenida con criterios y actualizaciones; hay límites de versión y compatibilidad.

?? `SecurityServicesConfigured` contiene 2 pero `SecurityServicesRunning` no. ¿Qué significa?
!! Que la integridad de memoria está pedida por configuración pero no está corriendo en este arranque; no protege.

?? ¿Qué exige la política de firma desde Windows 10 1607 con Secure Boot activo?
!! Que los drivers de kernel nuevos estén firmados a través del portal de Microsoft, con las excepciones documentadas.

?? ¿Protege una política de App Control en modo auditoría?
!! No bloquea: solo registra lo que bloquearía.

?? ¿Qué hacer si una prueba requiere desactivar controles?
!! No hacerlo en el equipo principal; si el entorno de laboratorio no está aprobado y documentado, abandonar la carga y continuar con análisis estático.

:::{nota} Puerta optativa
Podés explicar qué aporta firma, Secure Boot, HVCI/VBS, App Control y blocklist, leer su estado sin modificarlos, distinguir configurado de corriendo y declarar estado/fuente/límites.
:::

:::{nota} Lo que queda fuera
Diseñar o desplegar políticas de App Control, la arquitectura interna de VBS y del kernel seguro, Credential Guard, Kernel DMA Protection y los procesos de firma del portal de hardware no se desarrollan.
:::

## Fuentes

- Microsoft Learn: [Driver security checklist](https://learn.microsoft.com/en-us/windows-hardware/drivers/driversecurity/driver-security-checklist), [HVCI compatible code](https://learn.microsoft.com/en-us/windows-hardware/drivers/driversecurity/driver-security-checklist#implement-hvci-compatible-code), [Microsoft recommended driver block rules](https://learn.microsoft.com/en-us/windows/security/application-security/application-control/app-control-for-business/design/microsoft-recommended-driver-block-rules), [Windows Defender Application Control](https://learn.microsoft.com/en-us/windows/security/application-security/application-control/windows-defender-application-control/).
- Microsoft Learn, estado y firma: [Enable memory integrity (incluye Win32_DeviceGuard)](https://learn.microsoft.com/en-us/windows/security/hardware-security/enable-virtualization-based-protection-of-code-integrity), [Driver Signing Policy](https://learn.microsoft.com/en-us/windows-hardware/drivers/install/kernel-mode-code-signing-policy--windows-vista-and-later-), [The TESTSIGNING boot configuration option](https://learn.microsoft.com/en-us/windows-hardware/drivers/install/the-testsigning-boot-configuration-option), [Secure Boot](https://learn.microsoft.com/en-us/windows-hardware/design/device-experiences/oem-secure-boot).

:::{nota} Etiquetas
**Observado en CLS:** mitigaciones de user mode como contexto. **Conocimiento externo:** política de firma, VBS/HVCI y lectura de su estado, blocklist, Secure Boot y App Control. **Ejemplo ilustrativo:** matrices ficticias. **Laboratorio verificado:** no; consulta en solo lectura.
:::
