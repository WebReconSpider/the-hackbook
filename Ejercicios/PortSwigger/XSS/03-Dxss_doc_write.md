# Lab: DOM XSS in `document.write` sink using source `location.search`

> [!note]- Enunciado: 
> Este laboratorio contiene una vulnerabilidad de secuencias de comandos entre sitios (XSS) basada en el DOM en la funcionalidad de seguimiento de consultas de búsqueda. Utiliza la función JavaScript `document.write`, que escribe datos en la página. La función `document.write` se llama con datos de `location.search`, que puedes controlar mediante la URL del sitio web. Para resolver este laboratorio, realice un ataque de secuencias de comandos entre sitios que llame a la función `alert`.

## 1. Reconocimiento

Al acceder a la aplicación web, encontramos un blog que contiene múltiples publicaciones y una **barra de búsqueda** para filtrar el contenido.

![[Pasted image 20260417130050.png]]

Al realizar una búsqueda de prueba, observamos que el término introducido se refleja en la URL a través del parámetro `search` (`https://<lab>.web-security-academy.net/?search=hola`).

## 2. Análisis de Vulnerabilidades (Source & Sink)

Introducimos una cadena de caracteres especiales (`test<>"'`) para comprobar el nivel de sanitización. Al inspeccionar el comportamiento de la página, descubrimos cómo se procesa nuestra entrada.

### 2.1. Diferencia entre Reflected XSS y DOM XSS

En un **XSS Reflejado**, el backend (servidor) coge la entrada de la URL y la imprime directamente en el HTML de la respuesta. En un **DOM XSS**, el servidor no incrusta directamente el payload. En su lugar, es un script de JavaScript que se ejecuta en el navegador (cliente) el que lee los datos de una fuente controlable (el **Source**, en este caso `window.location.search`) y los procesa de forma insegura pasándolos a una función de ejecución (el **Sink**, en este caso `document.write()`).

### 2.2. Análisis del Código Cliente

Revisando el código fuente JavaScript de la página, encontramos la lógica de seguimiento de búsquedas:

```JavaScript
var query = (new URLSearchParams(window.location.search)).get('search');
if(query) {
    document.write('<img src="/resources/images/tracker.gif?searchTerms='+query+'">');
}
```

Nuestra entrada no está sanitizada. El _script_ la inserta directamente dentro del atributo `src` de una etiqueta `<img>`.

## 3. Explotación (DOM XSS)

### 3.1. Inyección del Payload

Para explotar esta vulnerabilidad, debemos inyectar un _payload_ que primero "escape" del atributo de la imagen y de la etiqueta actual, para luego introducir nuestro propio código.

Modificamos el parámetro `search` en la URL con el siguiente _payload_:

```
"><script>alert('DOM XSS')</script>
```

### 3.2. Ejecución en el Cliente

Al recargar la URL, el JavaScript del cliente ejecuta el `document.write` con nuestra entrada, alterando el DOM para que quede de la siguiente manera:

```HTML
<img src="/resources/images/tracker.gif?searchTerms="><script>alert('DOM XSS')</script>">
```

El navegador procesa este nuevo DOM modificado, cierra la etiqueta de imagen original y ejecuta la etiqueta `<script>` inyectada, mostrando la ventana emergente.

**Laboratorio resuelto**
