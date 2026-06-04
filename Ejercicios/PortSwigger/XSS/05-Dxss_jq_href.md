# DOM XSS in jQuery anchor href attribute sink using location.search source

> [!note]- Enunciado: 
> Este laboratorio contiene una vulnerabilidad de secuencias de comandos entre sitios (XSS) basada en el DOM en la página de envío de comentarios (_Submit feedback_). La aplicación utiliza la función selectora de jQuery `$()` para encontrar un elemento de anclaje (enlace) y cambia su atributo `href` utilizando datos extraídos de `location.search`. Para resolver el laboratorio, realice un ataque que llame a la función `print()` (o `alert()`) en el navegador de la víctima.

## 1. Reconocimiento

Al acceder a la aplicación web, encontramos un blog con múltiples publicaciones y una barra de búsqueda.

![[Pasted image 20260420120841.png]]

Durante la navegación, comprobamos que los comentarios y publicaciones estándar sanitizan correctamente todas las entradas. Si introducimos caracteres especiales, el servidor los codifica en entidades HTML, mitigando inyecciones directas o almacenadas:

```HTML
<p>test&lt;&gt;&apos;&quot;</p>
```

Sin embargo, al hacer clic en la sección de **"Submit feedback"** (Enviar comentarios), observamos que la URL cambia y añade un parámetro de enrutamiento: `https://<lab>.web-security-academy.net/feedback?returnPath=/`

## 2. Análisis de Vulnerabilidades (Source & Sink)

### 2.1. Análisis del Parámetro `returnPath`

El parámetro `returnPath=/` se utiliza habitualmente para generar un botón o enlace de "Volver" (`Back`), redirigiendo al usuario a la página anterior una vez que ha enviado su comentario.

Si inspeccionamos el código fuente o el comportamiento del DOM en la página `/feedback`, descubrimos que un _script_ de jQuery captura este parámetro de la URL (el **Source**: `location.search`) y lo asigna dinámicamente al atributo `href` de la etiqueta `<a>` que conforma el botón de retroceso (el **Sink**).

Como no existe validación sobre el formato de la URL proporcionada en `returnPath`, nos encontramos ante una vulnerabilidad de **DOM XSS**.

## 3. Explotación (DOM XSS en atributo `href`)

### 3.1. Selección e Inyección del Payload

Para explotar una inyección dentro de un atributo `href`, no podemos utilizar directamente etiquetas `<script>`, ya que el contexto es un enlace. En su lugar, abusamos del pseudo-protocolo `javascript:`.

Cuando un navegador intenta navegar hacia una URL que empieza con `javascript:`, en lugar de realizar una petición de red, interpreta el resto de la cadena como código JavaScript ejecutable.

Modificamos el parámetro en la barra de direcciones con nuestro _payload_:

```
https://<lab>.web-security-academy.net/feedback?returnPath=javascript:print()
```

### 3.2. Ejecución en el Cliente

Al cargar la página modificada, el código jQuery del cliente procesa la URL y actualiza el botón de retroceso en el DOM para que luzca así:

```HTML
<a href="javascript:print()">Back</a>
```

Para detonar el _payload_, simulamos la interacción de la víctima haciendo clic en el enlace "Back". El navegador interpreta el pseudo-protocolo y ejecuta la función `print()`, abriendo el cuadro de diálogo de impresión del sistema.

**Laboratorio resuelto**
