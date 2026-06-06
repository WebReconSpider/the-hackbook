# DOM XSS in jQuery selector sink using a hashchange event

> [!note]- Enunciado: 
> Este laboratorio contiene una vulnerabilidad de secuencias de comandos entre sitios (XSS) reflejada en la funcionalidad de seguimiento de consultas de búsqueda, donde se codifican los corchetes angulares. La reflexión se produce dentro de una cadena de JavaScript. Para resolver este laboratorio, realice un ataque de secuencias de comandos entre sitios que salga de la cadena de JavaScript y llame a la función `alert`.

## 1. Reconocimiento

Al acceder a la aplicación web, identificamos un blog que incluye una barra de búsqueda

![[Pasted image 20260422110423.png]]

Realizamos una búsqueda de prueba introduciendo una cadena con caracteres especiales (`test<>'"`) para evaluar cómo la aplicación maneja nuestra entrada. Observamos que el resultado se refleja directamente en la URL: `https://<lab>.web-security-academy.net/?search=test<>%27"`

## 2. Análisis de Vulnerabilidades
### 2.1. Pruebas de Sanitización

Intentamos realizar una inyección HTML clásica utilizando el _payload_: `<script>alert(1)</script>` (o variaciones como `<img src=x onerror=alert(1)>`).

### 2.2. Source Code

Al revisar el código fuente de la respuesta devuelta por el servidor, observamos por qué falló la inyección HTML. El servidor procesa nuestra búsqueda de la siguiente manera:

```HTML
<script>
    var searchTerms = '&lt;img src=x onerror=alert(1)&gt;';
    document.write('<img src="/resources/images/tracker.gif?searchTerms='+encodeURIComponent(searchTerms)+'">');
</script>   
```

**Análisis del contexto:** 
1. La aplicación **sí está sanitizando** los corchetes angulares (`<` y `>`), convirtiéndolos en sus entidades HTML (`&lt;` y `&gt;`). Esto impide la inyección de nuevas etiquetas HTML
2. Sin embargo, nuestra entrada se refleja directamente **dentro de una cadena de texto (string)** en un bloque de código JavaScript existente (`var searchTerms = 'NUESTRA_ENTRADA';`)
3. El servidor no está escapando las comillas simples (`'`)

Esto confirma una vulnerabilidad de **XSS Reflejado en contexto de JavaScript**

## 3. Explotación (Evasión de Cadena JS)

### 3.1. Diseño e Inyección del Payload

Dado que estamos inyectando datos directamente dentro de una variable de JavaScript, no necesitamos corchetes angulares. Nuestro objetivo es "escapar" de la declaración de la cadena, introducir nuestra propia instrucción JavaScript, y comentar el resto del código original para evitar errores de sintaxis que bloqueen la ejecución.

Construimos el siguiente _payload_:

```JavaScript
'; alert(1); //
```

Inyectamos este _payload_ en la barra de búsqueda (o directamente en el parámetro `?search=` de la URL).

### 3.2. Ejecución en el Cliente

Al procesar la solicitud, el servidor inyecta nuestro _payload_ en la plantilla de la respuesta. El bloque de código resultante en el documento que recibe el navegador queda estructurado así:

```JavaScript
<script>
    var searchTerms = ''; alert(1); //';
    document.write('<img src="/resources/images/tracker.gif?searchTerms='+encodeURIComponent(searchTerms)+'">');
</script> 
```

**Mecánica de la explotación:**

- El primer `'` cierra la cadena de la variable `searchTerms`.
- El punto y coma `;` finaliza esa instrucción.
- `alert(1);` se ejecuta como una instrucción JavaScript válida e independiente.
- Los caracteres `//` comentan la comilla de cierre original y el punto y coma del servidor (`';`), evitando que el navegador arroje un `Uncaught SyntaxError` que detendría el _script_.

Al cargarse la página, el navegador interpreta el código de forma secuencial y dispara la ventana emergente.

**Laboratorio resuelto**