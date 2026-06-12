# Reflected XSS into a JavaScript string with angle brackets HTML encoded

> [!note]- Enunciado: 
> Este laboratorio contiene una vulnerabilidad de secuencias de comandos entre sitios reflejada en la funcionalidad de seguimiento de consultas de búsqueda, donde se codifican los corchetes angulares. La reflexión se produce dentro de una cadena de JavaScript. Para resolver este laboratorio, realice un ataque de secuencias de comandos entre sitios que salga de la cadena de JavaScript y llame a la función `alert`.

## 1. Reconocimiento

Al acceder a la aplicación web, encontramos un blog que cuenta con una funcionalidad de **búsqueda**. Al buscar un término, este se refleja en la URL a través del parámetro `search`.

## 2. Análisis de Vulnerabilidades

### 2.1. Análisis del Contexto

Realizamos una búsqueda con la cadena de prueba `test<>'` e inspeccionamos el código fuente de la respuesta. Observamos que la entrada se refleja dentro de un bloque de código JavaScript, directamente asignada a una variable de texto:

```JavaScript
var searchTerms = 'test&lt;&gt;\'';
```

### 2.2. Pruebas de Sanitización

El servidor codifica en entidades HTML los corchetes angulares (`<` pasa a `&lt;`), lo que impide inyectar etiquetas HTML como `<script>`. Sin embargo, **no escapa las comillas simples (`'`)**.

## 3. Explotación (Evasión de Cadena JS)

### 3.1. Selección e Inyección del Payload

Para escapar de la variable de tipo _string_ sin romper la sintaxis del programa, inyectamos un payload en la barra de búsqueda que cierre la comilla inicial, ejecute la alerta y vuelva a abrir una comilla para empalmar con el código del servidor:

```JavaScript
'-alert(1)-'
```

También funciona `'; alert(1); //`)

### 3.2. Ejecución en el Cliente

Al enviar la solicitud, el servidor procesa el payload y lo inserta en la respuesta, estructurando el código de la siguiente manera:

```JavaScript
<script>
    var searchTerms = ''-alert(1)-'';
     ...
</script> 
```

El navegador del cliente interpreta la instrucción en JavaScript: al intentar realizar una operación matemática de resta entre dos cadenas vacías `''` y la función `alert(1)`, primero evalúa y ejecuta la función, disparando la ventana emergente.

**Laboratorio resuelto**
