## 1. Reconocimiento Inicial con Nmap

Realizamos un escaneo exhaustivo con `nmap` para detectar puertos abiertos, sus versiones y el sistema operativo. Esto nos proporciona una visión general de los servicios expuestos y posibles vulnerabilidades asociadas a sus versiones.

```bash
nmap -O -sC -sV <IP_DEL_OBJETIVO>
```

**Resultados Clave:**

*   `80/tcp open http Apache` El título de la página (`Upload here your file`) es una pista clara sobre la funcionalidad principal del sitio.

![SubirArchivo](https://github.com/WebReconSpider/the-hackbook/blob/main/Ejercicios/DockerLabs/2Facil/Imagenes/Upload_SubirArchivo.png)

### 1.2. Análisis de la Página Web con WhatWeb

Utilizamos `whatweb` para obtener más información sobre la tecnología utilizada en la página web. Esta herramienta escaneará la URL y reportará tecnologías, versiones y otros detalles.

```bash
whatweb <IP_DEL_OBJETIVO>
```

**Resultado:**
*   `Apache/2.4.52` en `Ubuntu Linux`.

### 1.3. Fuzzing Web con Gobuster

Realizamos un fuzzing de directorios con `gobuster` para descubrir rutas ocultas o archivos interesantes en el servidor web. Esto nos ayuda a mapear la estructura del sitio y encontrar posibles puntos de entrada.

```bash
gobuster dir -w /path/to/wordlist/directory-list-lowercase-2.3-medium.txt -u http://<IP_DEL_OBJETIVO>
```

**Resultados Relevantes:**

*   `/uploads`: Este directorio es crucial, ya que su nombre sugiere que es donde se almacenan los archivos subidos.
## 2. Explotación de la Vulnerabilidad de Carga de Archivos

La presencia de una funcionalidad de carga de archivos y un directorio `/uploads` accesible es una señal de una posible vulnerabilidad de carga de archivos sin restricciones, que puede llevar a la ejecución remota de código (RCE).

### 2.1. Creación de una Reverse Shell en PHP

Para obtener una shell inversa, crearemos un archivo PHP que, al ser ejecutado en el servidor, se conectará a nuestra máquina atacante. Utilizaremos un script de reverse shell PHP estándar, como el de `pentestmonkey`.

Descargar el script y modificar la dirección IP (`$ip`) a la IP de tu máquina atacante (Kali Linux) y el puerto (`$port`) al puerto que usarás para escuchar la conexión (por ejemplo, 443).

### 2.2. Carga del Archivo Malicioso

Utilizamos la interfaz de carga de archivos en `http://<IP_DEL_OBJETIVO>/` para subir nuestro `reverseShell.php` modificado. Si la carga es exitosa, el servidor responderá con un mensaje de confirmación como `The file reverseShell.php has been uploaded.`

### 2.3. Obtención de la Reverse Shell

1.  **Configurar el Listener:** En tu máquina atacante (Kali Linux), abre una terminal y configura un `netcat` listener en el puerto que especificaste en el script PHP (por ejemplo, 443).

    ```bash
    nc -lvnp 443
    ```

2.  **Ejecutar el Archivo Cargado:** Navega en tu navegador a la URL donde se cargó el archivo PHP: `http://<IP_DEL_OBJETIVO>/uploads/reverseShell.php`. Al acceder a esta URL, el servidor ejecutará el script PHP, lo que activará la conexión inversa a tu listener de `netcat`.

Deberías ver una conexión entrante en tu terminal de `netcat`.

```bash
whoami
www-data
```

Confirmamos que hemos obtenido una shell como el usuario `www-data`, que es el usuario bajo el que se ejecuta el servidor web Apache.

### 2.4. Tratamiento de la TTY (Opcional pero Recomendado)

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

## 3. Escalada de Privilegios

Una vez que tenemos una shell como `www-data`, el objetivo es escalar privilegios a `root`.

### 3.1. Verificación de Permisos Sudo

Verificamos qué comandos puede ejecutar el usuario actual con `sudo` sin necesidad de contraseña. Esto se hace con el comando `sudo -l`.

```bash
sudo -l
```

**Resultados Clave:**

*   `(root) NOPASSWD: /usr/bin/env`

Esto significa que el usuario `www-data` puede ejecutar el binario `/usr/bin/env` como `root` sin necesidad de introducir su contraseña. El comando `env` se utiliza para ejecutar un programa en un entorno modificado, y puede ser abusado para escalar privilegios si está mal configurado en `sudo`.

### 3.2. Abuso de `env` para Obtener Root

Según GTFOBins, cuando `env` tiene permisos `NOPASSWD` en `sudo`, se puede abusar de él para ejecutar una shell con privilegios de `root`.

```bash
sudo -u root /usr/bin/env /bin/sh
```

Al ejecutar este comando, obtendremos una shell con privilegios de `root`.

```bash
whoami
# root
```

Confirmamos que hemos escalado exitosamente a `root`.
