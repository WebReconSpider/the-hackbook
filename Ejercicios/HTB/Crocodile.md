Comprobamos la conexion con 
```bash
ping 10.129.6.138
```

Comprobamos los puertos abiertos con Nmap
```bash
nmap -O -sCV -p- 10.129.6.138
```
Salida:
21/tcp open  ftp     vsftpd 3.0.3
ftp-anon: Anonymous FTP login allowed (FTP code 230)
80/tcp open  http    Apache httpd 2.4.41 ((Ubuntu))

pueto 80:
![[Crocodile-Puerto80.png]]

Puerto 21: Accedemos de forma anonima
```
ftp 10.129.6.138
anonymous
```

Descargamos los 2 archivos que hay
![[Crocodile-ftp.png]]

```
cat allowed.userlist
aron
pwnmeow
egotisticalsw
admin
```

```
cat allowed.userlist.passwd 
root
Supersecretpassword1
@BaASD&9032123sADS
rKXM59ESxesUFHAd
```

Realizamos fuzzing web para buscar directorios ocultos:
``` 
gobuster dir -u http://10.129.6.138 -w /usr/share/wordlists/dirbuster/directory-list-2.3-small.txt -x html,txt,php

index.html           (Status: 200) [Size: 58565]
login.php            (Status: 200) [Size: 1577]
assets               (Status: 301) [Size: 313] [--> http://10.129.6.138/assets/]
css                  (Status: 301) [Size: 310] [--> http://10.129.6.138/css/]
js                   (Status: 301) [Size: 309] [--> http://10.129.6.138/js/]
logout.php           (Status: 302) [Size: 0] [--> login.php]
config.php           (Status: 200) [Size: 0]
fonts                (Status: 301) [Size: 312] [--> http://10.129.6.138/fonts/]
dashboard            (Status: 301) [Size: 316] [--> http://10.129.6.138/dashboard/]
```

Accedemos a `http://10.129.6.138/login.php` 
Probamos las posibles combinaciones de usuario/contraseña. Accedemos usando: admin/rKXM59ESxesUFHAd

![[Crocodile-flag.png]]
c7110277ac44d78b6a9fff2232434d16

>[!Question] What Nmap scanning switch employs the use of default scripts during a scan?
> -sC

>[!Question] What service version is found to be running on port 21?
> vsftpd 3.0.3

>[!Question] What FTP code is returned to us for the "Anonymous FTP login allowed" message?
> 230

>[!Question] After connecting to the FTP server using the ftp client, what username do we provide when prompted to log in anonymously?
> anonymous

>[!Question] After connecting to the FTP server anonymously, what command can we use to download the files we find on the FTP server?
> get

>[!Question] What is one of the higher-privilege sounding usernames in 'allowed.userlist' that we download from the FTP server?
> admin

>[!Question] What version of Apache HTTP Server is running on the target host?
>Apache httpd 2.4.41

>[!Question] What switch can we use with Gobuster to specify we are looking for specific filetypes?
>-x

>[!Question] Which PHP file can we identify with directory brute force that will provide the opportunity to authenticate to the web service?
> login.php

>[!Question] Submit Flag
> c7110277ac44d78b6a9fff2232434d16