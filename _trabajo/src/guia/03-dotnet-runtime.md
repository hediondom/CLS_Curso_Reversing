---
title: "Etapa 3 · .NET: runtime, ensamblados y metadatos"
description: "Por qué .NET es una buena primera victoria: código administrado, IL, metadatos y decompiladores."
etapa: "Etapa 3 · .NET como primera victoria"
---

# .NET: runtime, ensamblados y metadatos

:::{nota} Objetivo de la lección
Al terminar vas a poder explicar qué es el CLR, qué contiene un ensamblado .NET, en qué se diferencia el código administrado del nativo y por qué un decompilador puede reconstruir casi el código fuente, y reconocer los límites de Native AOT y C++/CLI mixto.
:::

**Prerrequisitos:** Etapa 2 completa. **Duración sugerida:** 3 horas. Estimación aproximada.

## Una advertencia sobre las fuentes

En CLS **no hay un curso de .NET leído**. Lo que existe es:

- El video 38 de «Videos y material adicional», que explica el código intermedio (MSIL) y por qué OllyDbg no alcanza para analizarlo ({{src:CLS_resultados_intermedios/transcripciones/extraidos/Videos y material adicional Ingenieria Inversa/Videos_Video38_Video38.txt|Videos y material adicional, Video 38}}, 00:00:16).
- El video 40, que usa .NET Reflector para decompilar un binario VB.NET y ver un formulario, un botón y una caja de texto ({{src:CLS_resultados_intermedios/transcripciones/extraidos/Videos y material adicional Ingenieria Inversa/Videos_Video40_Video40.txt|Videos y material adicional, Video 40}}, 00:03:20).
- Títulos de la colección `Teorias_Numeradas` que mencionan .NET/dnSpy, **sin contenido leído**: son contenedores `.zip` que no se abrieron.

Por eso esta etapa combina **contenido observado** (los dos videos) con **conocimiento externo** y **recomendación editorial**. No hay una ficha de un tutorial .NET de CLS porque no se encontró uno legible.

## Qué es .NET

.NET es una plataforma de ejecución. Un programa escrito en C#, VB.NET o F# no se compila directamente a código máquina: se compila a un lenguaje intermedio llamado **IL** (o **MSIL**, *Microsoft Intermediate Language*), y se guarda en un **ensamblado** (un `.exe` o `.dll`) junto con **metadatos**.

Cuando ejecutás el programa, el **CLR** (*Common Language Runtime*) toma el IL, lo compila a código nativo con el **JIT** (*just-in-time compiler*) y lo ejecuta. El resultado es código máquina, pero generado en tiempo de ejecución.

```text
C#  --compilador-->  IL + metadatos  --CLR/JIT-->  código nativo  --> CPU
```

El video 38 lo explica así: los lenguajes .NET no traducen a código nativo sino a un código intermedio, y por eso un debugger nativo como OllyDbg no alcanza para analizarlos (00:00:16–00:01:30).

## El ensamblado por dentro

Un ensamblado .NET es un archivo PE, pero con una diferencia clave: incluye una **cabecera CLR** y una región de metadatos. En .NET Framework, el punto de entrada del PE es un *stub* que llama al runtime (`_CorExeMain` en `mscoree.dll`); en .NET moderno, un host nativo (`apphost`) carga el runtime y lo arranca. En los dos casos, el código que ves en el ensamblado es IL, no el `Main` compilado a máquina.

Contenido típico:

| Parte | Qué guarda |
|---|---|
| **Manifest** | Nombre del ensamblado, versión, cultura, referencias a otros ensamblados |
| **Metadatos** | Tipos, métodos, campos, propiedades, parámetros, atributos |
| **IL** | El código de cada método |
| **Recursos** | Iconos, cadenas, imágenes |
| **Relocaciones / PE** | Lo mínimo para que Windows lo cargue |

Los metadatos son la razón por la que .NET es una "primera victoria": incluyen **nombres**. Un método se llama `CheckPassword`, no `sub_401000`. Un campo se llama `intentos`, no `[ebp-8]`. Salvo que el binario esté ofuscado, el decompilador puede reconstruir una versión muy parecida al código original.

## Código administrado vs nativo

| Aspecto | Nativo (C/C++) | .NET (C#/VB) |
|---|---|---|
| Unidad de ejecución | Código máquina | IL, compilado por JIT |
| Nombres | Se pierden al compilar (salvo PDB) | Quedan en los metadatos |
| Decompilación | Assembly difícil de leer | Casi código fuente |
| Memoria | Manual (malloc/free) | Recolector de basura |
| Portabilidad | Depende de la CPU | El mismo IL corre en varias |
| Herramienta típica | IDA, x64dbg | ILSpy, dnSpy, dotPeek |

### Excepciones al modelo IL/JIT: Native AOT y C++/CLI

El recorrido IL → JIT describe el caso común, no todos los ejecutables relacionados con .NET. **Native AOT** compila IL a código nativo durante la publicación y no usa JIT al arrancar; el resultado es específico de una plataforma y puede ser más difícil de decompilar como IL. En reversing, primero identificá si hay cabecera CLR y metadatos suficientes; no asumas que todo binario hecho con .NET conserva el mismo contenido administrado.

En Native AOT, la reflexión no desaparece por completo, pero debe ser compatible con análisis estático y trimming. Miembros a los que solo se llega mediante nombres construidos en ejecución pueden requerir anotaciones o preservación explícita; de otro modo, el linker puede quitarlos. Native AOT no admite carga dinámica de ensamblados (por ejemplo, Assembly.LoadFile) ni generación de código en runtime (System.Reflection.Emit). Para reversing, ILSpy puede no tener IL recuperable como en un ensamblado JIT; busca código nativo, metadatos/símbolos conservados y llamadas al runtime como evidencias complementarias.

**C++/CLI** puede producir ensamblados de modo mixto, con código nativo y administrado; C++/CLI no es una opción de publicación compatible con Native AOT. Esto introduce dos mecanismos de carga e inicialización y hace relevante el *loader lock*: el código administrado no debe ejecutarse desde `DllMain`. Para el analista, la consecuencia es práctica: un PE puede combinar metadatos CLR con secciones y código nativo; usá herramientas administradas y nativas y documentá qué parte estás observando.

Eso no significa que .NET sea "inseguro" ni que "cualquiera puede ver el código". Significa que la **ofuscación** es la protección habitual: renombrar símbolos, cifrar strings, introducir flujo falso. Analizar un binario ofuscado es más difícil, pero el modelo de ejecución sigue siendo el mismo.

## Herramientas

| Herramienta | Estado | Para qué |
|---|---|---|
| **ILSpy** | Activa, open source | Decompilador de referencia; también `ilspycmd` |
| **dnSpy** | Sin mantenimiento desde hace años | Debugger + decompilador; existen forks como **dnSpyEx** |
| **dotPeek** | Gratis (JetBrains) | Decompilador cómodo |
| **.NET Reflector** | De pago | El histórico que usa el video 40 |
| **ildasm** | Incluido en el SDK de Windows | Volcar IL y metadatos |
| **Visual Studio** | Community gratis | Compilar y depurar tus propios programas |

Para empezar, **ILSpy** alcanza. Si necesitás depurar IL paso a paso, dnSpyEx o el debugger de Visual Studio sobre tu propio código son mejores opciones que un debugger nativo.

:::{aviso} Sobre dnSpy
dnSpy fue durante años la herramienta más usada para analizar .NET. Su desarrollo se detuvo y quedó como proyecto archivado. Existen bifurcaciones mantenidas (por ejemplo dnSpyEx). Si un tutorial viejo te manda a descargar "dnSpy", verificá de dónde lo bajás y qué versión es. Para leer código, ILSpy es más simple y está activo.
:::

## Ejemplo paso a paso: tu primer ensamblado

Si tenés el SDK de .NET instalado, creá un proyecto de consola:

```bash
dotnet new console -n HolaNet
cd HolaNet
dotnet build
```

El código generado es:

```csharp
Console.WriteLine("Hello, World!");
```

Abrí `bin/Debug/net8.0/HolaNet.dll` en ILSpy. Vas a ver:

- El ensamblado `HolaNet`, con versión y referencias.
- La clase `Program`.
- El método `Main`, con su IL.
- La cadena `"Hello, World!"` en el manifiesto de recursos.

**Qué mirar:**

1. El **árbol de tipos** a la izquierda: namespace, clase, métodos.
2. El **panel de IL** (si tu versión lo muestra): las instrucciones del método.
3. El **panel de metadatos**: tokens, firmas, referencias.

Ese recorrido es el equivalente .NET de abrir un `.exe` en IDA: primero la estructura, después el código.

## Práctica

1. Instalá el SDK de .NET y creá un proyecto de consola con una clase y dos métodos.
2. Compilalo en Debug y en Release. Abrí las dos versiones en ILSpy y compará el `Main`.
3. Anotá tres diferencias entre Debug y Release (por ejemplo, variables locales, saltos, llamadas).
4. Buscá una cadena que hayas escrito en el código. ¿Aparece en el ensamblado? ¿En qué forma?
5. Escribí en tu bitácora qué es el CLR, qué es el IL y por qué los metadatos facilitan el análisis.

## Preguntas de repaso

**1. ¿Qué es el CLR?**
El runtime de .NET: carga el ensamblado, compila el IL a código nativo con el JIT y administra memoria, excepciones y seguridad.

**2. ¿Qué diferencia hay entre IL y código máquina?**
El IL es un lenguaje intermedio independiente de la CPU; el código máquina es específico del procesador. El JIT traduce IL a máquina en tiempo de ejecución.

**3. ¿Por qué un decompilador .NET produce código casi fuente?**
Porque los metadatos conservan nombres, tipos, firmas y estructura, y el IL es una representación de alto nivel del programa.

**4. ¿Un binario .NET ofuscado sigue siendo .NET?**
Sí. La ofuscación cambia nombres y estructura, pero el modelo de ejecución (IL + metadatos + CLR) es el mismo.

**5. ¿Qué herramienta usarías para ver el IL de un método?**
ILSpy, ildasm o el panel de IL de un decompilador. Para depurar, dnSpyEx o Visual Studio.

## Antes de avanzar

Tenés que poder:

- Explicar el recorrido C# → IL → JIT → CPU.
- Nombrar las partes de un ensamblado.
- Decir por qué los metadatos hacen más fácil el análisis.
- Abrir un `.dll` propio en ILSpy y encontrar un método.

:::{nota} Puerta de salida
Si podés compilar tu propio programa y encontrarlo en ILSpy con nombres y todo, estás listo para leer IL.
:::

## Fuentes de esta lección

- Microsoft Learn: [Native AOT deployment](https://learn.microsoft.com/en-us/dotnet/core/deploying/native-aot/), [Initialization of mixed assemblies (C++/CLI)](https://learn.microsoft.com/en-us/cpp/dotnet/initialization-of-mixed-assemblies).

- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Videos y material adicional Ingenieria Inversa/Videos_Video38_Video38.txt|Videos y material adicional, Video 38}} — código intermedio, MSIL, VB/C# y límites de OllyDbg.
- {{src:CLS_resultados_intermedios/transcripciones/extraidos/Videos y material adicional Ingenieria Inversa/Videos_Video40_Video40.txt|Videos y material adicional, Video 40}} — .NET Reflector sobre un binario VB.NET.
- {{src:CLS_resultados_intermedios/teorias_numeradas_por_etapa.csv|teorias_numeradas_por_etapa.csv}} — títulos con .NET/dnSpy, **pendientes de revisar** (contenedores no abiertos).

:::{nota} Capas de esta lección
**Contenido observado en CLS:** la explicación del video 38 y el uso de .NET Reflector en el video 40. **Conocimiento externo:** CLR, JIT, metadatos, herramientas actuales, Native AOT (carga dinámica, reflexión y trimming) y ensamblados mixtos C++/CLI. **Recomendación editorial:** el ejemplo con el SDK y la advertencia sobre dnSpy.
:::
