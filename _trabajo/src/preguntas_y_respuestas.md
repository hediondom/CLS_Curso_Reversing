---
title: "Preguntas y respuestas por etapa"
description: "Repaso con respuestas razonadas para comprobar el aprendizaje antes de avanzar."
---

# Preguntas y respuestas por etapa

Usá esta página como autoevaluación. Respondé primero con tus palabras y después abrí la respuesta. Lo importante no es acertar: es poder **justificar** la respuesta con un ejemplo o una evidencia.

## Etapa 0 · Laboratorio y método

?? ¿Qué diferencia hay entre una snapshot y un backup?
!! Una snapshot guarda el estado de la VM en un momento y permite volver atrás después de un experimento. Un backup es una copia de tus datos para recuperarlos si se pierden. La snapshot no protege los archivos del host y no reemplaza un backup.

?? ¿Para qué sirve calcular el SHA-256 de un programa?
!! Para identificarlo sin ambigüedad: dos archivos con el mismo hash son, en la práctica, el mismo archivo. También sirve para detectar duplicados y para verificar que la transferencia entre host y guest no alteró el contenido.

?? El inventario marca un archivo como `util`. ¿Alcanza para ejecutarlo?
!! No. `util` es una clasificación de catálogo, no un certificado de seguridad, calidad ni vigencia. Antes de ejecutar hay que saber qué es, de dónde salió y si tenés permiso para analizarlo.

?? ¿Por qué se desactiva la carpeta compartida en la VM?
!! Porque es un canal bidireccional entre guest y host. Un programa con comportamiento malicioso puede leer, cifrar o borrar archivos del host a través de ese canal. Para pasar un archivo se usa una ISO de solo lectura o una unidad temporal que se monta y se desmonta.

?? ¿Qué red conviene usar en la VM de análisis?
!! Host-only o NAT sin acceso a la LAN. El adaptador puente conecta la VM directamente a tu red local y amplía el alcance de cualquier incidente. Para un crackme no hace falta red.

?? ¿Qué haces si un programa deja la VM en un estado raro?
!! Detener la VM (no suspenderla), desconectarla de la red desde el hipervisor, restaurar la snapshot limpia, revisar el host y anotar qué pasó. Si hubo exposición de credenciales, cambiarlas.

?? ¿Se puede analizar malware en la VM del curso?
!! No en la Etapa 0. La rama de malware de esta guía es estática y defensiva; la ejecución de muestras requiere un laboratorio dedicado, protocolo y propósito defensivo. El video 37 de CLS ejecuta Shelter, pero se cita como caso observado, no como práctica recomendada.

?? ¿Por qué el laboratorio va antes que el assembly?
!! Porque todo lo que sigue implica ejecutar programas que no escribiste. Sin un entorno donde equivocarte sea barato, el primer error puede costar datos personales. El laboratorio es el piso de seguridad del curso.

## Etapa 1 · Fundamentos

?? ¿Por qué `0xFB` puede valer 251 o −5?
!! Porque el patrón de bits es el mismo. Si se interpreta sin signo, vale 251; si se interpreta con signo en complemento a dos, vale −5. El tipo del dato y la instrucción que lo usa deciden la interpretación.

?? ¿Cómo se guarda `0x0A0B0C0D` en memoria little-endian?
!! Como `0D 0C 0B 0A`: el byte menos significativo va en la dirección más baja. Para leerlo como número hay que invertir el orden.

?? Con Image Base `0x400000`, VA `0x401040`, header `0x1000` y `.text` en `0x400`, ¿cuál es el file offset?
!! `0x401040 − 0x400000 = 0x1040`; `0x1040 − 0x1000 = 0x40`; `0x40 + 0x400 = 0x440`. El offset es `0x440`.

?? En 32 bits, ¿dónde están los argumentos de una función?
!! En el stack, apilados de derecha a izquierda por el llamador. Después del `call` y del prólogo, el primer argumento suele estar en `[EBP+8]`, el segundo en `[EBP+0xC]`, etc.

?? En 64 bits, ¿dónde están los primeros cuatro argumentos?
!! En `RCX`, `RDX`, `R8` y `R9`. El resto va al stack, después de 32 bytes de shadow space que reserva el llamador.

?? ¿Qué es la IAT y por qué importa?
!! Es la tabla de direcciones de imports que el cargador completa con las funciones de las DLLs. Un `call dword ptr [dirección]` pasa por la IAT; si entendés eso, entendés por qué una llamada a `MessageBoxA` no tiene una dirección fija.

?? ¿Qué diferencia hay entre stack y heap?
!! El stack es LIFO, lo administra el procesador con `push`/`pop` y llamadas, y su vida está atada a la función. El heap se pide en tiempo de ejecución (`malloc`, `new`), no tiene orden LIFO y su vida la administra el programa o el runtime.

?? ¿El curso de Python de CLS enseña Python?
!! No. Las 55 transcripciones son un curso de lógica y fundamentos de programación con pseudocódigo y ejemplos en Basic, Pascal y C. No contienen código Python ejecutable y usan Python 2.5.1 como referencia de 2007. Sirven como base de lógica, no como curso de Python.

?? ¿Qué indica `Magic = 0x20B` en un PE?
!! Que la cabecera opcional es PE32+, es decir, un binario de 64 bits. `0x10B` corresponde a PE32 (32 bits).

?? ¿Por qué el mismo código compilado en Debug y Release se ve distinto?
!! Porque el compilador aplica optimizaciones: elimina variables, reordena, inlinea funciones y simplifica condiciones. Debug prioriza la depuración; Release, el rendimiento. Para aprender conviene Debug; para analizar un binario real, asumí Release.

## Etapa 2 · Introducción al reversing

?? ¿`mov eax, 0` activa `ZF`?
!! No. `mov` es una transferencia de datos y no actualiza flags. Para activar `ZF` hace falta una operación aritmética o lógica con resultado cero, como `sub eax, eax` o `xor eax, eax`.

?? ¿Qué diferencia hay entre `CF` y `OF`?
!! `CF` indica acarreo o desborde en una interpretación **sin signo**; `OF`, en una interpretación **con signo**. El mismo resultado puede activar uno, otro o ambos.

?? Con `EAX = 0xFFFFFFFF` y `CMP EAX, 2`, ¿salta `JA` o `JG`?
!! `JA` salta, porque como número sin signo `0xFFFFFFFF` es el máximo. `JG` no salta, porque como número con signo es −1, menor que 2.

?? ¿Qué guarda `call` en el stack?
!! La dirección de la instrucción siguiente al `call`, llamada return address. `ret` la saca y salta ahí.

?? ¿Quién limpia los argumentos en `cdecl` y en `stdcall`?
!! En `cdecl`, el llamador, con un `add esp, N` después del `call`. En `stdcall`, la función llamada, con `ret N`.

?? ¿Qué diferencia hay entre F7 y F8?
!! Las dos ejecutan la instrucción actual. F7 entra a las funciones; F8 las ejecuta sin detenerse dentro. F8 no saltea la función: la corre completa.

?? ¿Cuántos breakpoints de hardware hay y de quién son?
!! Cuatro (`DR0`–`DR3`) por hilo, porque los registros de depuración son parte del contexto de cada hilo. El capítulo 07 dice "por proceso"; la afirmación correcta es por hilo.

?? ¿Qué byte usa un breakpoint por software?
!! `0xCC`, la instrucción `INT3`. El debugger lo coloca en lugar del byte original y lo restaura al detenerse.

?? ¿IDA y x64dbg son lo mismo?
!! No. IDA es un desensamblador estático: analiza el archivo sin ejecutarlo. x64dbg es un debugger: ejecuta el programa y muestra su estado. Se complementan.

?? ¿Cómo sincronizás IDA con el debugger si ASLR cambia la base?
!! Rebaseando IDA a la base que muestra el debugger (`Edit → Segments → Rebase program`) o comparando por file offset (`Ctrl+Shift+G` en el debugger, `Jump to file offset` en IDA). Las direcciones absolutas no sirven si la base cambió.

?? ¿Qué hace `LEA` y en qué se diferencia de `MOV`?
!! `LEA` calcula una dirección efectiva y la guarda sin leer memoria. `MOV` con corchetes lee el contenido de esa dirección. `lea eax, [ebx+4]` da la dirección; `mov eax, [ebx+4]` da el valor guardado ahí.

?? ¿Por qué un `call` a una API se ve como `call dword ptr [dirección]`?
!! Porque es un `call` indirecto: no salta a la dirección entre corchetes, sino al puntero que está guardado ahí. Ese puntero es una entrada de la IAT que el cargador completó con la dirección real de la API.

?? ¿Cuál es el error más común al leer un salto condicional?
!! Leerlo como "si se cumple la condición, salta al bloque bueno". Muchas veces el salto va al bloque de error y es la **negación** de la condición. Hay que preguntar qué camino toma el programa cuando el salto se produce y qué camino cuando no.

?? Ves registros `xmm` e instrucciones terminadas en `sd`/`ss`. ¿Qué significa?
!! Es punto flotante con SSE: `sd` es un `double`, `ss` un `float`. Los argumentos `double` en x64 viajan en `xmm0…`, y una comparación usa `ucomisd` + un salto sin signo (y a veces un `jp` por el caso `NaN`).

?? Aparece `lea eax, [rax+rax*4]`. ¿Es un acceso a memoria?
!! No. Es una multiplicación por 5 (`x + x*4`): una optimización (*strength reduction*). `lea` se usa acá para aritmética, no para leer memoria.


?? En un binario MSVC x64, ¿dónde está el RTTI de una clase y por qué no se lee como puntero?
!! En `vtable[-1]` hay un puntero al Complete Object Locator, cuyos campos en x64 son RVA: hay que sumarles la base de la imagen. Ver 2.18.

?? Un slot de vtable lleva a `sub rcx, 10h` y a un salto. ¿Qué es?
!! Un adjustor thunk de herencia múltiple: convierte el `this` de un subobjeto base en el del objeto completo. Ver 2.18.

?? Un binario importa solo `LoadLibraryA` y `GetProcAddress` pero hace mucho más. ¿Qué buscás?
!! Resolución dinámica de APIs: las cadenas con nombres de funciones, un recorrido del PEB y de la tabla de exports, o constantes de 32 bits comparadas contra un hash de cada nombre. Ver 2.14.

?? La ventana de strings está casi vacía en un programa que muestra mensajes. ¿Qué causas revisás?
!! Cadenas UTF-16 no incluidas en la búsqueda, cadenas con longitud sin `0` final, cadenas armadas en el stack y cadenas cifradas. Ver IDA y 2.10.

?? Todos los bloques de una función vuelven al mismo punto, que compara una variable. ¿Qué es y cómo se lee?
!! Flujo aplanado: se reconstruye la tabla estado → bloque → estado siguiente para recuperar el orden real. Ver 2.10.

?? Un binario tiene Rich header y `vcruntime140.dll` pero rutas `src/main.rs`. ¿Qué es?
!! Probablemente Rust con el target `-msvc`: una sola pista no alcanza para decidir el lenguaje. Ver 2.13.

?? ¿Por qué el bit de hipervisor de `CPUID` no prueba que el equipo sea virtual?
!! Porque un Windows con Hyper-V o VBS activo corre sobre un hipervisor también en una máquina física. Ver 2.15.

?? En un UPX de 64 bits no hay `popad`. ¿Cómo llegás al OEP?
!! Con un breakpoint de memoria en ejecución sobre la región que estaba vacía: se dispara en la primera instrucción ejecutada ahí. Ver 2.17.

?? Un diff muestra trescientas funciones cambiadas. ¿Cómo encontrás el parche?
!! Descartando el ruido repartido por todo el binario (compilador, optimizaciones, direcciones) y buscando el cambio concentrado: un bloque nuevo con comparación y salida temprana. Ver 2.20.

?? ¿Qué cambia en el proceso cuando lo instrumentás con Frida?
!! Se inyecta una biblioteca y se reescribe el inicio de las funciones enganchadas; un programa con anti-análisis puede notarlo. Ver 2.21.

## Etapa 3 · .NET

?? ¿Qué es el CLR?
!! El runtime de .NET: carga el ensamblado, compila el IL a código nativo con el JIT y administra memoria, excepciones y seguridad.

?? ¿Qué diferencia hay entre IL y código máquina?
!! El IL es un lenguaje intermedio independiente de la CPU; el código máquina es específico del procesador. El JIT traduce IL a máquina en tiempo de ejecución.

?? ¿Por qué un decompilador .NET produce código casi fuente?
!! Porque los metadatos conservan nombres, tipos, firmas y estructura, y el IL es una representación de alto nivel. Salvo ofuscación, el decompilador puede reconstruir una versión muy parecida.

?? ¿Qué hace `cgt` en IL?
!! Compara los dos valores del tope de la pila y empuja 1 si el primero es mayor que el segundo, 0 si no. Es una comparación, no un salto.

?? ¿Qué se pierde al compilar en Release?
!! Variables locales, líneas y algunas simplificaciones que el compilador aplica. Los nombres de tipos y métodos se conservan, salvo ofuscación.

?? ¿El decompilador devuelve el código fuente original?
!! No. Reconstruye una lógica equivalente. Puede aplicar De Morgan, reordenar retornos, cambiar nombres y simplificar expresiones. Sirve para entender, no para copiar.

?? ¿La ofuscación impide analizar un binario .NET?
!! No. Lo hace más difícil. El IL y los metadatos siguen ahí; hay que verificar la reconstrucción con ejecución controlada.

?? ¿dnSpy sigue siendo la herramienta recomendada?
!! dnSpy dejó de recibir mantenimiento y quedó archivado. Existen bifurcaciones mantenidas (dnSpyEx), pero para leer código ILSpy es más simple y está activo. Verificá siempre el origen de la descarga.

## Etapa 4 · Práctica guiada

?? ¿Cuál es la diferencia entre una hipótesis y una observación?
!! La hipótesis es una afirmación que hacés antes de confirmar; la observación es lo que el debugger te muestra. La hipótesis se contrasta con la observación y se corrige si falla.

?? ¿Qué hace reproducible un informe?
!! Que incluya el binario identificado por hash, el entorno y las versiones de las herramientas, los pasos y los valores observados. Con eso, otra persona puede repetir el experimento.

?? ¿Por qué el hash es parte del informe?
!! Porque identifica sin ambigüedad el archivo analizado. Si el hash cambia, el informe ya no aplica a ese archivo.

?? ¿En qué se diferencian encoding, cifrado y hashing?
!! El encoding (base64, hex) no tiene clave y cualquiera lo revierte; el cifrado usa una clave y sin ella no se recupera el texto; el hashing (MD5, SHA) es de una sola vía. En Windows, mirá primero los imports: si usa CryptoAPI (`advapi32`) o CNG (`bcrypt`), un breakpoint en esas APIs te muestra los datos en claro.

?? ¿Cuándo NO se ejecuta un programa?
!! Cuando no tenés permiso, no podés contenerlo o no necesitás el comportamiento dinámico. También cuando está en cuarentena o excluido. En esos casos se analiza estático y se documenta.

?? Si un programa detecta el debugger y se cierra, ¿qué significa?
!! Que tiene protecciones anti-análisis o que su comportamiento depende del entorno. Es un dato para documentar, no un obstáculo para "saltar". En esta guía se estudia para reconocerlo, no para evadir protecciones comerciales.

?? ¿Qué hacés primero si una muestra resulta sospechosa?
!! Triage estático: hash, tipo, secciones, imports, strings, reglas YARA. No se ejecuta en el host. Si corresponde, se deriva a un laboratorio dedicado.

?? ¿Qué pasos seguís si algo sale mal en el laboratorio?
!! Detener la VM, desconectar la red, restaurar la snapshot, revisar el host, anotar qué pasó, reportar si hubo exposición y cambiar las credenciales que pudieron quedar expuestas.

?? ¿Qué es una divulgación responsable?
!! Reportar la vulnerabilidad en privado al proveedor, darle tiempo para corregir, no publicar el exploit antes de acuerdo y no acceder a datos de terceros. El plazo habitual es de unos 90 días.

?? ¿Análisis estático o dinámico primero?
!! Depende del caso. Para un programa con strings claras, el estático orienta rápido; para confirmar un valor concreto, el dinámico es más directo. Lo habitual es alternar, empezando por el estático cuando no podés ejecutar.

?? Querés reconstruir el formato de archivo de un programa propio. ¿Cómo confirmás la tabla de campos?
!! Cambiando un byte por vez sobre copias para ver qué validación falla, y con un lector independiente que obtenga los mismos valores que el programa. Ver 4.1.

## Etapa 5 · Ramas opcionales

?? ¿Cuál es el primer paso del análisis de malware?
!! El triage estático: hash, tipo, secciones, imports, strings, entropía y reglas de detección. No se ejecuta la muestra en el host.

?? ¿El stack canary corrige un desborde?
!! No. Detecta que se pisó el valor antes del return address y aborta. El defecto sigue estando; para corregirlo hay que validar el tamaño de la copia (`strncpy`, `snprintf`, `fgets`).

?? ¿IDAPython funciona en IDA Free?
!! Depende de la versión. Históricamente IDA Free no incluía Python; las versiones recientes agregaron capacidades. Si no está, usá Ghidra o automatizá con `pefile`/`capstone`.

?? ¿La Etapa 6 de kernel y drivers es obligatoria?
!! No. Es una rama optativa posterior, con prerrequisitos técnicos específicos y laboratorios solo en VM descartable. Las Etapas 0–4 siguen siendo el recorrido base.

?? ¿Se puede desempaquetar un protector comercial en este curso?
!! No. Esta guía explica qué es un empacador y cómo se reconoce, pero no enseña a eludir protecciones comerciales. Esa práctica queda fuera del marco legal y ético.

?? ¿Qué hago si terminé las etapas 0 a 4?
!! Elegí **una** rama, completá su práctica y documentala. No acumules temas: acumulá evidencia. Después volvé a las fichas y actualizá tu seguimiento.

## 2D y Etapa 6 · ramas optativas

?? ¿Tengo que completar toda 2D para entrar a Etapa 6?
!! No. Para drivers se requieren solo las bases indicadas: objetos/tokens (2D.1), memoria/loader (2D.2) y excepciones/debugging (2D.11), además de C, assembly, memoria/sincronización y WinDbg. 2C es recomendada.

?? ¿Puedo probar un driver en mi Windows principal?
!! No. La carga y Driver Verifier se limitan a una VM descartable con snapshot. Si la configuración vigente impide cargar el driver de prueba sin rebajar protecciones, se completa análisis estático.

?? ¿La Etapa 6 exige aprender COM o Task Scheduler?
!! No. No son prerrequisitos para el trabajo de drivers; sus lecciones siguen siendo ramas optativas independientes.

?? Un objeto COM agrega el free-threaded marshaler. ¿Hay proxy al pasarlo a otro proceso?
!! Sí. El FTM solo evita el proxy entre apartamentos del mismo proceso; hacia otro proceso delega en el marshaling estándar. Ver 2D.6.

?? ¿Por qué una búsqueda del CLSID en el registro puede no encontrar una clase que igual se activa?
!! Porque pudiste mirar la vista equivocada (usuario/máquina, 32/64 bits) o la clase se declara en un manifiesto y se resuelve sin registro. Ver 2D.7.

?? DCOM activa bien pero la primera llamada falla con `0x800706BA`. ¿Es un problema de permisos?
!! No necesariamente: también encaja un firewall que deja pasar el puerto 135 del mapeador pero no el puerto dinámico del servidor. Ver 2D.8.

?? ¿`WITHIN 30` y `GROUP WITHIN 30` en una consulta WQL hacen lo mismo?
!! No. El primero fija un intervalo de sondeo; el segundo agrupa eventos y entrega uno agregado. Ver 2D.9.

?? Un servidor de named pipe no usa `FILE_FLAG_FIRST_PIPE_INSTANCE`. ¿Qué riesgo hay que revisar?
!! Que otro proceso haya creado el pipe antes y actúe como servidor; la bandera hace fallar la creación si el nombre ya existe. Ver 2D.10.

?? ¿Una excepción de primera oportunidad en el depurador indica un fallo?
!! No. Solo la segunda oportunidad indica que nadie la manejó. Ver 2D.11.

?? Falta un evento ETW esperado. ¿Qué descartás antes de concluir que no hubo actividad?
!! Que el provider estuviera habilitado con el nivel y las keywords adecuados, que el canal o la sesión estuvieran activos y que no hubiera eventos perdidos. Ver 2D.12.

?? ¿Qué no puede hacer una rutina de driver a `DISPATCH_LEVEL`?
!! Esperar con intervalo no nulo ni acceder a memoria paginable. Ver 6.1.

?? Con `METHOD_NEITHER`, ¿por qué `ProbeForRead` no alcanza?
!! Porque solo valida rango y alineación en ese momento; el contenido puede cambiar después y cada acceso debe protegerse y capturarse una vez. Ver 6.4.

?? En un 0xD1, ¿qué parámetro llevás a `ln`?
!! El cuarto, la dirección de la instrucción que accedió a memoria, para ver la función. Ver 6.3.

?? ¿En qué orden ven una operación varios minifilters?
!! Los preoperation, de mayor a menor altitud; los postoperation, en orden inverso. Ver 6.5.

?? `Win32_DeviceGuard` dice que la integridad de memoria está configurada pero no corriendo. ¿Protege?
!! No en ese arranque: lo que cuenta es `SecurityServicesRunning`. Ver 6.6.
