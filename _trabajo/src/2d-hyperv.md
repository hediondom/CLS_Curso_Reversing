---
title: "Extensión optativa · Hyper-V y virtualización"
description: "Introducción conceptual a la arquitectura Hyper-V, VMBus y particiones; diferenciación frente a VMCS/EPT, sin técnicas de evasión."
---

# Extensión optativa · Hyper-V y virtualización

:::{aviso} Extensión separada
No integra el núcleo de 2D, no es prerrequisito de la Etapa 6 ni forma parte de la aprobación del curso. El objetivo es comprender la arquitectura y los límites de observación; no implementar evasión anti-VM.
:::

## Conceptos

Hyper-V usa un hypervisor y particiones. La **root partition** administra recursos y aloja componentes de administración; las **child partitions** ejecutan sistemas invitados. VMBus ofrece comunicación entre particiones. Los **VSP** del lado root proveen servicios sintéticos y los **VSC** del guest los consumen. Esta arquitectura no es lo mismo que una CPU virtual aislada ni describe todos los detalles internos de un hypervisor.

**VMCS** (Intel) y **EPT** (Intel) / **NPT** (AMD) son estructuras/mecanismos de virtualización dependientes del procesador. Se mencionan como conceptos de lectura avanzada: no son componentes de VMBus ni hacen falta para analizar el curso.

Una aplicación puede observar características del entorno virtual por motivos legítimos —compatibilidad, diagnóstico, soporte—. El ejercicio consiste en describir esas señales y sus falsos positivos, no en modificar o esconderlas.

## Ejemplo trabajado

*(Diagrama conceptual, no salida de un equipo.)*

```text
Guest / child partition: app -> VSC
                          ⇅ VMBus
Root partition:          VSP -> recursos del host
Hypervisor:              aislamiento y planificación de particiones
CPU:                     soporte de virtualización (VT-x/AMD-V)
```

Si un binario detecta un adaptador sintético o servicios de integración, eso sugiere un entorno virtual pero no revela por sí solo su configuración de seguridad ni prueba evasión.

## Práctica conceptual

En un host o VM donde Hyper-V ya esté habilitado y tengas autorización, abrí la documentación y la vista de propiedades/configuración disponible. Dibuja root/child, VSC/VSP y VMBus; registra dos señales de virtualización de una aplicación didáctica y explica una alternativa legítima para cada una. No alteres el hypervisor, Secure Boot, VM settings ni el comportamiento de la aplicación.

## Entregable y repaso

Entregá el diagrama y una tabla señal–evidencia–explicación alternativa–límite.

?? ¿VMBus es lo mismo que VMCS?
!! No. VMBus conecta servicios sintéticos entre particiones Hyper-V; VMCS es una estructura de virtualización asociada a Intel VT-x.

?? ¿Una señal de VM prueba que el programa evade análisis?
!! No. Puede servir a diagnóstico o compatibilidad; hace falta observar la decisión y el contexto.

:::{nota} Puerta optativa
Podés describir root/child, VSP/VSC/VMBus y diferenciarlo de VMCS/EPT/NPT, con límites de lo que una señal permite inferir.
:::

## Fuentes

- Microsoft Learn: [Hyper-V Architecture](https://learn.microsoft.com/en-us/virtualization/hyper-v-on-windows/reference/hyper-v-architecture), [Hyper-V on Windows](https://learn.microsoft.com/en-us/virtualization/hyper-v-on-windows/).
- Intel: [Intel 64 and IA-32 Software Developer Manuals](https://www.intel.com/content/www/us/en/developer/articles/technical/intel-sdm.html). AMD: [AMD64 Architecture Programmer's Manual](https://www.amd.com/en/search/documentation/hub.html).

:::{nota} Etiquetas
**Observado en CLS:** conceptos de detección de VM en 2B son solo contexto. **Conocimiento externo:** arquitectura Hyper-V y extensiones CPU. **Ejemplo ilustrativo:** diagrama. **Laboratorio verificado:** no; lectura conceptual.
:::
