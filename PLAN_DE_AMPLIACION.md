# Plan de Ampliación y Presupuesto de Paginación — Tomo II (Fase 2)



**Proyecto:** Manual Técnico y Guía de Laboratorio de Ingeniería Inversa y Kernel Internals en Windows x64  

**Alcance del Documento:** Cierre de Fase 2 (Lecciones Nuevas + Ampliaciones In-Situ) y Auditoría de Límite Editorial  

**Restricción Editorial Máxima:** **200 páginas** (formato maquetado A4, tipografía técnica 10 pt, interlineado 1.15, densidad media de 430 palabras equivalentes por página considerando bloques de código, volcados de WinDbg y tablas de estructuras).



---



## 1. Resumen Ejecutivo



El presente plan consolida todas las incorporaciones de la **Fase 2** sobre el **Tomo II** asegurando la cobertura completa de las arquitecturas defensivas y de auditoría modernas de Windows 10/11 x64 sin exceder el tope estricto de **200 páginas**.



* **Páginas Base del Tomo II (previas a Fase 2, incluyendo ajustes de Fase 1):** 146,0 páginas.

* **Impacto de las 5 Lecciones Nuevas de Fase 2 (`2d-16`, `2d-17`, `6-08`, `6-09`, `6-10`):** +31,5 páginas.

* **Impacto de las 3 Ampliaciones de Lecciones Existentes (`2d-10`, `2d-12`, `2d-14`):** +6,5 páginas.

* **Anexo de Fe de Erratas Cruzada (Tomo I / Tomo II) e Índice Analítico:** +3,5 páginas.

* **Total Consolidado del Tomo II:** **187,5 páginas** (188 páginas cerradas).

* **Margen de Seguridad Restante bajo el Límite de 200 Páginas:** **12,0 páginas (6,0 % de reserva)**.



---



## 2. Desglose Detallado de Paginación por Componente



### 2.1. Inventario Base y Ampliaciones sobre Archivos Existentes (Módulos 2D y 6)



| Identificador de Archivo | Estado en Fase 2 | Páginas Base | Páginas Añadidas (Fase 2) | Total Lección (Págs.) | Contenido Incorporado en Fase 2 |

| :--- | :--- | :---: | :---: | :---: | :--- |

| Resto de Lecciones Base (`2d-01` a `2d-09`, `2d-11`, `2d-13`, `2d-15`, `6-01` a `6-07`) | Auditadas en Fase 1 | 128,0 | 0,0 | **128,0** | Correcciones de erratas y precisión de símbolos de Fase 1 (sin expansión neta de paginado). |

| `2d-10-ipc.html` | **Ampliada** | 6,0 | **+2,0** | **8,0** | Sección 5: Inspección práctica de puertos ALPC con `handle64.exe -a` y extensión `!alpc` (`/lpc`, `/p`, `/c`, `/m`) en WinDbg. |

| `2d-12-etw.html` | **Ampliada** | 6,5 | **+2,5** | **9,0** | Sección 5: `Microsoft-Windows-Threat-Intelligence` (ETWti), protección PPL Antimalware, tabla `EtwTiLog*` e inspección de `nt!EtwThreatIntProvRegHandle`. |

| `2d-14-win32k-shadow.html` | **Ampliada** | 5,5 | **+2,0** | **7,5** | Sección 5: Mitigación *Win32k System Call Lockdown* (`DisallowWin32kSystemCalls`), corte en `PsConvertToGuiThread` y flag en `_EPROCESS`. |

| **Subtotal Base + Ampliaciones** | — | **146,0** | **+6,5** | **152,5** | — |



### 2.2. Nuevas Lecciones Incorporadas en Fase 2



| Identificador de Archivo | Módulo | Estado | Extensión Estimada (Págs.) | Desglose de Secciones para Control de Densidad |

| :--- | :---: | :--- | :---: | :--- |

| `2d-16-hyper-v.html` | 2D | Completada (Entrega previa) | **6,5** | Arquitectura Hyper-V Root/Child Partition, VMCS, SLAT (EPT/NPT), VMBus e hiperllamadas (`vmcall`). |

| `2d-17-vbs-profundo.html` | 2D | **Completada (Esta entrega)** | **6,5** | Ortogonalidad Ring vs VTL (VTL 0 / VTL 1), `securekernel.exe`, transición `HvCallVtlCall`, HVCI (`skci.dll` + W^X en EPT) y Trustlets IUM (`lsaiso.exe`). |

| `6-08-wfp.html` | 6 | Completada (Entrega previa) | **6,0** | Windows Filtering Platform (WFP), Base Filtering Engine (BFE), Callout Drivers en Ring 0, capas ALE y auditoría de filtros. |

| `6-09-kcfg-isa.html` | 6 | Completada (Entrega previa) | **6,0** | kCFG (`_guard_dispatch_icall_fptr`), bitmap CFG, XFG (Extended Flow Guard) y CET / Hardware Shadow Stacks en modo kernel (`CR4.CET`). |

| `6-10-kernel-fuzzing.html` | 6 | **Completada (Esta entrega)** | **6,5** | Superficie IOCTL (`METHOD_BUFFERED`, `IN/OUT_DIRECT`, `METHOD_NEITHER`), Driver Verifier + Special Pool a nivel de PTE, WTF (Snapshots) y kAFL/Nyx (Intel PT). |

| **Subtotal Lecciones Nuevas** | — | — | **+31,5** | — |



### 2.3. Elementos Editoriales de Cierre (Anexos y Fe de Erratas)



| Componente | Páginas Estimadas | Justificación |

| :--- | :---: | :--- |

| Anexo A: Fe de Erratas Cruzada (Tomo I → Tomo II) | **2,0** | Documenta las 6 correcciones técnicas del Tomo I sin alterar el artefacto cerrado del Tomo I. |

| Índice General y Glosario de Estructuras NT | **1,5** | Referencia rápida de símbolos WinDbg y estructuras (`_EPROCESS`, `_KTHREAD`, `_IRP`, `_ALPC_PORT`). |

| **Subtotal Anexos** | **+3,5** | — |



---



## 3. Justificación Técnica para No Exceder el Límite de 200 Páginas



Para mantener el volumen total en **187,5 páginas** (12,5 páginas por debajo del límite máximo de 200 páginas) sin sacrificar rigor técnico ni omitir estructuras del kernel, se han aplicado cuatro criterios de ingeniería editorial:



1. **Eliminación de Redundancia entre `2d-16-hyper-v.html` y `2d-17-vbs-profundo.html`:**  

   Los fundamentos de virtualización asistida por hardware (estructuras VMCS, configuración básica de tablas EPT/NPT y mecánica general de `VMEXIT`) se explican una única vez en `2d-16-hyper-v.html`. La lección `2d-17-vbs-profundo.html` referencia directamente dicha base y dedica el 100 % de su espacio a la separación de tablas EPT entre VTL 0 y VTL 1, `securekernel.exe`, `skci.dll` (HVCI) y los procesos IUM (`lsaiso.exe`), ahorrando aproximadamente 4 páginas de duplicación teórica.



2. **Uso de Tablas Estructurales Compactas en Lugar de Volcados Crudos Completos:**  

   En lugar de incluir salidas completas de `dt nt!_EPROCESS` o `dt nt!_ALPC_PORT` (que ocupan entre 3 y 5 páginas por estructura debido a sus más de 200 campos), todos los laboratorios utilizan filtros de campos específicos en WinDbg (por ejemplo, `dt nt!_EPROCESS <Addr> MitigationFlagsValues.DisableWin32kSystemCalls` o `dt nt!_ETW_GUID_ENTRY <Addr> Guid ProviderEnableInfo`), reduciendo la huella visual de cada salida de consola a 6–15 líneas con máxima relación señal/ruido.



3. **Consolidación de Métodos de Fuzzing en `6-10-kernel-fuzzing.html`:**  

   Se unificaron el análisis estático/dinámico de despacho IOCTL, la amplificación de fallos con *Special Pool* y los dos paradigmas modernos de fuzzing (emulación por snapshots con WTF y cobertura asistida por hardware con Intel PT / kAFL) en una única lección cohesiva de 6,5 páginas en lugar de desdoblarla en dos capítulos separados.



4. **Declaración Estandarizada de Laboratorios No Ejecutados en Vivo:**  

   Todos los bloques prácticos que requieren infraestructura específica de hipervisor anidado, Intel PT o compilación de drivers firmados en modo test incluyen el metadato estandarizado `Laboratorio verificado: no; requiere VM/toolchain`, presentando directamente los comandos exactos de reproducción y la salida esperada de referencia sin extenderse en tutoriales de instalación de máquinas virtuales que ya forman parte de los prerrequisitos documentados en el Tomo I.

---

## 4. Veredicto Editorial y Cierre de Fase 2

- **Límite físico estricto del Tomo II:** 200 páginas (formato 17x24 / A4 maquetado).
- **Paginación base previa:** 146,0 páginas.
- **Incremento lecciones nuevas (2D.16, 2D.17, 6.8, 6.9, 6.10):** +35,0 páginas.
- **Incremento ampliaciones in-situ (2D.10, 2D.12, 2D.14):** +6,5 páginas.
- **Paginación total proyectada:** **187,5 páginas** (188 páginas físicas en pliegos pares de imprenta).
- **Margen de reserva disponible:** 12,5 páginas de holgura de seguridad.
- **Regla de oro de preservación:** El Tomo I se mantiene 100 % inalterado (410 páginas fijas; trazabilidad en `ERRATAS_TOMO_II.md`).
- **Estado de Fase 2:** ✅ APROBADO PARA MAQUETACIÓN E IMPRESIÓN.
