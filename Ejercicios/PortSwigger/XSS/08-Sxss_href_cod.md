# Stored XSS into anchor `href` attribute with double quotes HTML-encoded

> [!note]- Enunciado: 
> Este laboratorio contiene una vulnerabilidad de secuencias de comandos entre sitios (XSS) almacenada en la funcionalidad de comentarios. Para resolverlo, envíe un comentario que llame a la función `alert` cuando se haga clic en el nombre del autor del comentario.

## 1. Reconocimiento

Al acceder a la aplicación web, encontramos un blog con múltiples publicaciones. Al final de cada entrada, existe un formulario para dejar comentarios que solicita varios campos: _Name_ (Nombre), _Email_, _Website_ (Sitio web) y _Comment_ (Comentario).

## 2. Análisis de Vulnerabilidades

### 2.1. Análisis del Contexto

Si rellenamos el campo **Website** con una URL, observamos que el servidor utiliza este dato para convertir el nombre del autor del comentario en un enlace interactivo dentro del DOM:

```HTML
<a href="NUESTRO_SITIO_WEB">Nombre del autor</a>
```

### 2.2. Pruebas de Sanitización

Si intentamos escapar del atributo `href` introduciendo en el campo _Website_ la cadena `test<>"'`, y luego inspeccionamos el código fuente de la página renderizada, observamos lo siguiente:

```HTML
<a href="test&lt;&gt;&quot;'">Nombre</a>
```

El servidor está **codificando en entidades HTML las comillas dobles**. Como resultado, es imposible cerrar el atributo `href=""` o inyectar etiquetas HTML puras como `<script>`.

## 3. Explotación (XSS Almacenado en `href`)

### 3.1. Selección e Inyección del Payload

Dado que estamos atrapados dentro del atributo `href` y no podemos usar comillas dobles ni corchetes, debemos abusar del comportamiento nativo del navegador utilizando el pseudo-protocolo `javascript:`.

Rellenamos el formulario de comentarios y, en el campo **Website**, inyectamos nuestro _payload_:

```
javascript:alert(1)
```

### 3.2. Ejecución Persistente en el Cliente

Al enviar el formulario, el servidor guarda los datos en la base de datos. Si alguna persona hace clic en el nombre del autor, el navegador lee el atributo `href` y, al detectar que comienza con `javascript:`, interpreta el resto de la cadena como código ejecutable en lugar de realizar una petición HTTP, lanzando la función `alert(1)`.

**Laboratorio resuelto.**
