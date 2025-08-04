# Obsession
## 1. Reconocimiento de Puertos con Nmap

Realizamos un escaneo con `nmap` para detectar puertos abiertos y sus versiones. 

```bash
nmap -sC -sV --open <IP_DEL_OBJETIVO>
```

**Resultados Clave:**

*   `21/tcp open ftp vsftpd 3.0.5`: El puerto 21 está abierto y ejecuta el servidor FTP vsftpd versión 3.0.5. El escaneo también indica que el **login anónimo está permitido** (`ftp-anon: Anonymous FTP login allowed`).
*   `22/tcp open ssh OpenSSH 9.6p1 Ubuntu`
*   `80/tcp open http Apache httpd 2.4.58 ((Ubuntu))`

La posibilidad de acceso FTP anónimo es una pista importante para el acceso inicial.

## 2. Enumeración Web

Al visitar la página web (`http://<IP_DEL_OBJETIVO>`) y revisar su contenido o código fuente, encontramos una pista: "-- Utilizando el mismo usuario para todos mis servicios, podré recordarlo fácilmente --". 

En la página aparece varias veces `russoski`  por lo que es un posible usuario.
## 3. Enumeración FTP Anónima

### 2.1. Listado de Archivos FTP

Al conectarnos al FTP de forma anónima, observamos dos archivos:

*   `chat-gonza.txt`
*   `pendientes.txt`

Descargamos ambos archivos para analizarlos con el comando `get`.

### 2.2. Análisis de Archivos

*   **`chat-gonza.txt`**: Contiene una conversación con tres posibles usuarios: russoski y gonza y Nagore
*   **`pendientes.txt`**: `Cambiar algunas configuraciones de mi equipo, creo que tengo ciertos permisos habilitados que no son del todo seguros..`


## 4. Obtención de Credenciales y Acceso Inicial

Con el nombre de usuario `russoski` y la pista de reutilización de contraseñas, intentamos un ataque de fuerza bruta contra el servicio FTP para obtener la contraseña.

### 4.1. Fuerza Bruta con Hydra (FTP)

Utilizamos `hydra` para intentar adivinar la contraseña del usuario `russoski` en el servicio FTP.

```bash
hydra -l russoski -P /path/to/wordlist/rockyou.txt -u ftp://<IP_DEL_OBJETIVO>
```

**Resultado Clave:**

*   `[21][ftp] host: <IP_DEL_OBJETIVO> login: russoski password: iloveme`

Esto nos proporciona la contraseña para el usuario `russoski`: **iloveme**.

vemos varios archivos y una foto, los obtenemos con el comando `get` y los inspeccionamos. No hay información relevante. Utilizamos steghide y exiftool para vuscar información oculta dentro de la imagen, pero sin éxito.
### 4.2. Conexión SSH con Credenciales Reutilizadas

Dado que el usuario `russoski` reutiliza contraseñas, intentamos usar las mismas credenciales (`russoski:iloveme`) para acceder al servicio SSH.

```bash
ssh russoski@<IP_DEL_OBJETIVO>
# Contraseña: iloveme
```

Hemos obtenido acceso inicial al sistema.

## 5. Escalada de Privilegios

Una vez que hemos obtenido acceso SSH como el usuario `russoski`, el objetivo es escalar privilegios a `root`.

### 5.1. Verificación de Permisos Sudo

Verificamos qué comandos puede ejecutar el usuario `russoski` con `sudo` sin necesidad de contraseña. Esto se hace con el comando :
```bash
sudo -l
```

**Resultados Clave:**

*   `User russoski may run the following commands on ...: (root) NOPASSWD: /usr/bin/vim`

Esto significa que el usuario `russoski` puede ejecutar el binario `/usr/bin/vim` como `root` sin necesidad de introducir su contraseña. 

### 5.2. Abuso de Vim con Sudo para Obtener Shell de Root

Consultamos [GTFOBins](https://gtfobins.github.io/gtfobins/vim/#sudo) para la técnica específica.

Para obtener un shell de `root`, ejecutamos `vim` con un comando que nos permita ejecutar un shell directamente.

```bash
sudo -u root /usr/bin/vim -c ":!/bin/sh"
```

El comando `whoami` confirmará que hemos escalado exitosamente a `root`.

```bash
whoami
# root
```
