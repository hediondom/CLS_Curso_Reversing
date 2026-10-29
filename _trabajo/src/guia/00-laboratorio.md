---
title: "Etapa 0 · Un laboratorio que podés romper sin miedo"
description: "Cómo armar un entorno aislado, con snapshots y trazabilidad, para practicar reversing sin exponer tus datos."
etapa: "Etapa 0 · Laboratorio y método"
---

# Un laboratorio que podés romper sin miedo

:::{nota} Objetivo de la lección
Al terminar vas a poder armar una máquina virtual aislada, tomar una snapshot, transferir un programa de práctica sin compartir carpetas y registrar su hash antes y después de analizarlo. Ese es el piso de todo lo que sigue.
:::

**Prerrequisitos:** ninguno. **Duración sugerida:** 4 a 6 horas, casi todas de trabajo práctico. Es una estimación aproximada de esta guía, no una duración declarada por el material de CLS.

## Por qué el laboratorio va primero

Reversing significa ejecutar y observar programas que no escribiste. A veces son programas de práctica inofensivos; otras veces son binarios de origen desconocido. La diferencia entre aprender y arruinar tu máquina está en **dónde** los ejecutás.

Un laboratorio de reversing tiene una regla simple: **lo que se rompe, se descarta; lo que importa, vive afuera**. El programa sospechoso corre en una máquina virtual (VM) que podés borrar y recrear. Tus documentos, tus cuentas, tus claves y tus carpetas compartidas se quedan en el host, fuera del alcance.

El curso de CLS usa esta idea desde el principio. En el capítulo 01, Solid abre un ejecutable de práctica en x64dbg y explica que el debugger sirve para ver el comportamiento de un programa **mientras está corriendo en memoria** ({{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_01 x64dbg primeros pasos_01 x64dbg primeros pasos.txt|Reversing desde cero, cap. 01}}, 00:00:26). Para observar hay que ejecutar. Por eso el entorno importa.

:::{aviso} Lo que este curso no hace
No vas a ejecutar adjuntos del chat, cracks, keygens, instaladores desconocidos ni muestras en cuarentena. Tampoco vas a analizar malware dinámicamente en tu máquina personal. Las prácticas usan **programas propios**, software abierto o crackmes diseñados para aprender, y siempre dentro de la VM.
:::

## Las tres capas: host, hipervisor e invitado

Conviene fijar tres palabras que vas a ver todo el tiempo:

| Capa | Qué es | Ejemplos | Qué va adentro |
|---|---|---|---|
| **Host** (anfitrión) | Tu computadora real | Windows 11, tu notebook | Tus documentos, cuentas, claves |
| **Hipervisor** | El programa que crea y administra máquinas virtuales | VirtualBox, VMware Workstation Player, Hyper-V | La configuración de las VMs |
| **Guest** (invitado) | El sistema operativo que corre dentro de la VM | Windows 10/11, Linux | Las herramientas de análisis y las muestras |

El guest es descartable. El host no. Todo lo que hagas para "compartir" entre ambos —carpetas compartidas, portapapeles bidireccional, unidades de red, USB— es un puente, y los puentes se cruzan en las dos direcciones.

:::{peligro} El error más común
Crear la VM, activar "carpeta compartida" para pasar el programa, ejecutarlo y descubrir que el malware cifró la carpeta del host. Si necesitás pasar un archivo, usá una imagen ISO de solo lectura o una unidad extraíble virtual que montás, copiás y desmontás. Nunca una carpeta compartida permanente.
:::

## Reglas de diseño del laboratorio

Estas reglas son **recomendación editorial** de la guía, basadas en prácticas estándar de análisis seguro. No salen de un archivo de CLS; se apoyan en el principio de aislamiento que el propio material usa cuando analiza binarios.

1. **Una VM por objetivo.** Si analizás dos programas distintos, usá dos snapshots o dos VMs. Así sabés qué cambió cada uno.
2. **Snapshot limpia antes de empezar.** La snapshot se toma con el sistema actualizado, sin la muestra y sin conexión a tu red personal. Ese es tu "punto cero".
3. **Red host-only o NAT sin acceso a la LAN.** La VM no debe ver tus otras computadoras ni tus unidades de red. Si el programa necesita internet, evaluá si de verdad lo necesita; para un crackme, no.
4. **Sin credenciales reales.** Dentro de la VM usá una cuenta local descartable, sin tus contraseñas, sin tu correo, sin tus tokens.
5. **Sin carpetas compartidas ni portapapeles bidireccional.** Si el hipervisor lo permite, desactivalos explícitamente.
6. **Herramientas instaladas desde el inicio.** x64dbg, un editor hexadecimal, Python, un desensamblador. Instalarlas después de la muestra contamina la línea base.
7. **Registro desde el minuto cero.** Anotá qué VM, qué snapshot, qué archivo, qué hash y qué hiciste.

## Ejemplo paso a paso: laboratorio mínimo con VirtualBox

Voy a mostrar el procedimiento con VirtualBox porque es gratuito y multiplataforma. Los conceptos se trasladan a VMware o Hyper-V; los nombres de los botones cambian.

### Paso 1. Crear la VM

1. Descargá VirtualBox desde el sitio oficial y una imagen ISO de Windows 10/11 desde Microsoft. **No** uses imágenes "preactivadas" ni ISOs de origen dudoso: son un riesgo y además complican la trazabilidad.
2. Creá una VM nueva: 4 GB de RAM, 2 CPUs y un disco virtual de 60 GB. Para reversing de programas de práctica alcanza.
3. Instalá el sistema operativo. Cuando termine, aplicá las actualizaciones y reiniciá.

**Por qué:** una VM con recursos suficientes evita que el debugger se trabe y que confundas un problema de rendimiento con un comportamiento del programa.

### Paso 2. Aislar la red

En la configuración de la VM, revisá la pestaña **Red**:

- Adaptador 1: **NAT** o **Host-only**. Nat permite salir a internet; host-only solo habla con el host.
- Desactivá el adaptador puente (bridged): ese conecta la VM directamente a tu red local.
- En **General > Avanzado**, desactivá el portapapeles compartido y el arrastrar y soltar.
- En **Carpetas compartidas**, no agregues ninguna.

**Por qué:** el adaptador puente es el que convierte una VM en otro dispositivo de tu red. Para analizar un crackme no lo necesitás.

### Paso 3. Tomar la snapshot "limpia"

1. Apagá la VM correctamente (no la suspendas).
2. En VirtualBox, seleccioná la VM y usá **Instantáneas > Tomar instantánea**.
3. Nombrala `00-limpia-sin-muestra` y escribí una descripción con la fecha.

**Por qué:** una snapshot guarda el estado del disco. Si algo sale mal, restaurás y volvés exactamente al punto anterior. No es un backup de tus archivos del host; es el estado de la VM.

### Paso 4. Preparar la transferencia sin puentes

Para pasar un programa de práctica:

1. Creá una imagen ISO con el archivo. En Windows podés usar `oscdimg` o una herramienta gráfica; en Linux, `genisoimage`.
2. Montá la ISO en la VM como unidad de CD/DVD, copiá el archivo al disco del guest y **desmontá** la ISO.
3. Verificá el hash dentro del guest y comparalo con el del host.

En PowerShell, el comando es:

```powershell
Get-FileHash -Algorithm SHA256 .\programa.exe
```

Salida típica (el hash es inventado a modo de ejemplo):

```
Algorithm       Hash                                                                   Path
---------       ----                                                                   ----
SHA256          A1B2C3D4E5F60718293A4B5C6D7E8F90123456789ABCDEF0123456789ABCDEF0       C:\lab\programa.exe
```

**Por qué el hash:** dos archivos con el mismo SHA-256 son, en la práctica, el mismo archivo. Si el hash del host y el del guest coinciden, sabés que la transferencia no alteró nada. Si no coinciden, no analices: primero entendé por qué cambió.

### Paso 5. Ejecutar y volver atrás

1. Confirmá que estás en la snapshot `00-limpia-sin-muestra`.
2. Anotá en tu bitácora: fecha, nombre del archivo, hash, herramienta y objetivo.
3. Ejecutá el programa **solo si es propio, abierto o un crackme de práctica**.
4. Al terminar, apagá la VM y restaurá la snapshot. No reutilices el estado "sucio" para la próxima muestra.

**Por qué:** restaurar no es opcional. Un programa puede dejar archivos, claves de registro o servicios corriendo. La snapshot te devuelve al punto conocido.

## Qué muestra CLS y qué corregimos

En CLS hay un ejemplo real de laboratorio con dos VMs: el video 37 de «Videos y material adicional» analiza el malware Shelter dentro de una VM con Windows 7 de 32 bits, y usa otra VM con Kali Linux para simular el ataque ({{src:CLS_resultados_intermedios/transcripciones/extraidos/Videos y material adicional Ingenieria Inversa/Videos_Video37_Video37.txt|Video 37, introducción}}, 00:00:00–00:00:40).

Ese video **sí ejecuta el malware** y monta un reverse shell dentro de las VMs. La separación en máquinas virtuales es correcta como idea, pero el curso no convierte eso en una práctica recomendada: para esta guía, Shelter es un **caso de estudio observado**, no una tarea. Si querés analizar malware, la rama defensiva de la Etapa 5 te muestra cómo hacer triage estático y por qué no se empieza ejecutando.

También conviene registrar una diferencia de criterio: el inventario del proyecto aclara que, durante su confección, **no se movió, extrajo ni ejecutó ningún archivo** ({{src:CLS_resultados_intermedios/inventario_limpio/LEEME.md|Inventario limpio, LEEME}}). Esa es la conducta que esta guía adopta para el corpus: leer, listar y citar; no ejecutar.

## Práctica: tu laboratorio en una página

Hacé esto y guardá el resultado. Es el primer entregable del curso.

1. Creá la VM con las reglas de arriba.
2. Tomá la snapshot limpia.
3. Escribí tu propio programa de prueba. El más simple: un `.exe` que pida una palabra y muestre "hola" si es `clase`. Compilalo en el guest (o en el host y pasalo por ISO).
4. Calculá el SHA-256 en el host y en el guest. Pegá ambos en la bitácora.
5. Ejecutalo en x64dbg si ya lo instalaste; si no, ejecutalo suelto y anotá qué pasa.
6. Restaurá la snapshot y verificá que el archivo que copiaste ya no está.

:::{practica} Entregable mínimo
Un archivo `bitacora.md` con: nombre de la VM, snapshot usada, programa, hash del host, hash del guest, red configurada, qué hiciste y qué observaste. Sin ese registro, la práctica no cuenta como terminada.
:::

## Preguntas de repaso

**1. ¿Qué diferencia hay entre una snapshot y un backup?**
Una snapshot guarda el estado de la VM en un momento; sirve para volver atrás después de un experimento. Un backup es una copia de tus datos para recuperarlos si se pierden. La snapshot no protege tus archivos del host y no reemplaza un backup.

**2. El inventario marca un archivo como `util`. ¿Alcanza para ejecutarlo?**
No. `util` es una clasificación de catálogo, no un certificado de seguridad, calidad ni vigencia. La decisión de ejecutar depende de qué es el archivo, de dónde salió y de si tenés permiso para analizarlo.

**3. ¿Por qué se desactiva la carpeta compartida?**
Porque es un canal bidireccional entre guest y host. Un programa con comportamiento malicioso puede leer, cifrar o borrar archivos del host a través de ese canal. La ISO de solo lectura evita esa vía.

**4. ¿Para qué sirve comparar el hash antes y después de copiar?**
Para detectar alteraciones en la transferencia y para identificar el archivo sin ambigüedad. Si los hashes no coinciden, el archivo que analizás no es el que creías.

**5. ¿La VM alcanza para analizar cualquier muestra?**
No. Una VM mal configurada puede tener acceso a la red local, al portapapeles o a carpetas compartidas. Además, algunas muestras detectan la VM y cambian de comportamiento. Para empezar, alcanza con programas propios y crackmes; para malware real hace falta un laboratorio dedicado y procedimientos que esta guía no cubre en la Etapa 0.

## Antes de avanzar

Tenés que poder:

- Explicar con tus palabras la diferencia entre host, hipervisor y guest.
- Crear una VM, aislarla de la red local y tomar una snapshot.
- Transferir un archivo sin carpeta compartida y verificar su SHA-256 en ambos lados.
- Describir qué harías si un programa deja el sistema raro: apagar, restaurar, revisar la bitácora.

:::{nota} Puerta de salida de la Etapa 0
Si no podés mostrar tu `bitacora.md` con los dos hashes y la snapshot, no pases a la lección siguiente. El resto del curso asume que tenés un entorno donde equivocarte no cuesta caro.
:::

## Fuentes de esta lección

- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Reversing desde cero (Ricardo y Solid)/Ricardo Narvaja y Solid - Reversing desde cero_01 x64dbg primeros pasos_01 x64dbg primeros pasos.txt|Reversing desde cero, cap. 01 (x64dbg primeros pasos)}} — qué hace un debugger y por qué se ejecuta el programa.
- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Videos y material adicional Ingenieria Inversa/Videos_Video37_Video37.txt|Videos y material adicional, Video 37}} — ejemplo observado de laboratorio con dos VMs y ejecución de malware; se cita como caso, no como modelo.
- {{src:CLS_resultados_intermedios/inventario_limpio/LEEME.md|Inventario limpio, LEEME}} — criterio de no ejecutar ni extraer archivos durante el inventario.
- {{src:CLS_Guia/FUENTES_Y_LIMITES.md|Fuentes y límites de esta edición}} — criterios de alcance y seguridad.

:::{nota} Sobre las capas de esta lección
**Contenido observado en CLS:** el uso de VMs en el video 37 y el criterio de no ejecución del inventario. **Conocimiento externo:** funcionamiento de hipervisores, snapshots y hashes. **Recomendación editorial:** las siete reglas de diseño y el procedimiento paso a paso.
:::

