# Reflected XSS into HTML context with nothing encoded

> [!note]- Enunciado:
> This lab contains a simple reflected cross-site scripting vulnerability in the search functionality.
To solve the lab, perform a cross-site scripting attack that calls the `alert` function.

## 1. Reconocimiento

Al acceder a la aplicación web, encontramos un blog que contiene múltiples publicaciones y una **barra de búsqueda** para filtrar contenido.

![[XSS_reflejado_no_codificado.png]]

## 2. Análisis de Vulnerabilidades (Fuzzing Manual)

### 2.1. Pruebas de Sanitización

Introducimos una cadena de caracteres especiales para comprobar una posible vulnerabilidad.

```
< > ' "
```

### 2.2. Source Code

Al buscarlo, observamos que la URL se actualiza añadiendo nuestra entrada en el parámetro `search`: `https://<lab>.web-security-academy.net/?search=<+>+%26+"+%25+%2F`

La página renderiza el siguiente mensaje en pantalla:

> `0 search results for '< > ' " & $ % /'`

Inspeccionamos el código fuente de la página de respuesta (Viendo el código fuente o interceptando la respuesta con Burp Suite). Observamos que nuestra entrada se refleja directamente dentro d de una etiqueta `<h1>`, **sin ningún tipo de codificación de entidades HTML**. Esto nos confirma una vulnerabilidad de **Cross-Site Scripting Reflejado (Reflected XSS)**

## 3. Explotación (XSS Reflejado)

### 3.1. Inyección del Payload

Podemos explotar esta vulnerabilidad de dos maneras:

**Opción A:** Mediante la interfaz de usuario (Caja de búsqueda) Introducimos directamente nuestro _payload_ en la barra de búsqueda:

```HTML
<script>alert('XSS Reflejado')</script>
```

**Opción B:** Mediante manipulación directa de la URL (Vector de ataque real) Modificamos el parámetro `search` directamente en la barra de direcciones. Este es el formato que un atacante enviaría a una víctima  _phishing_:

```
https://<lab>.web-security-academy.net/?search=<script>alert('XSS Reflejado')</script>
```

El navegador recibe la respuesta, lee las etiquetas y ejecuta la función `alert()`, mostrando una ventana emergente.

**Laboratorio resuelto con éxito.**
