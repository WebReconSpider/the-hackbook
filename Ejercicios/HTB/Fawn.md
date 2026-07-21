# Fawn

Comprobamos la conexion con 
```bash
ping 10.129.39.79
```

Comprobamos los puertos abiertos con Nmap  (con opción -sV para ver la versión de FTP) (-O para saber el SO)
```bash
nmap -O -sCV -p- 10.129.39.79
```
Salida:
21/tcp open  ftp     vsftpd 3.0.3
Además nos indica que se puede realizar un acceso anónimo

![[Fawn-nmap.png]]

hacemos un login (sin usar una cuenta) con “anonymous” y “”

![image.png](Fawn-ftp.png)

listamos los archivos con “ls”
```
-rw-r--r--    1 0        0              32 Jun 04  2021 flag.txt
```

5º obtenemos el archivo con “get nombre”

6º Para comprobar el contenido del documento: primero nos salimos de la conexión FTP con “exit” y luego ejecutamos “cat nombre”
Salida: `035db21c881520061c53e0536e44f815`


---
>[!Question] What does the 3-letter acronym FTP stand for?
> File Transfer Protocol

>[!Question] Which port does the FTP service listen on usually?
> 21

>[!Question] FTP sends data in the clear, without any encryption. What acronym is used for a later protocol designed to provide similar functionality to FTP but securely, as an extension of the SSH protocol?
> SFTP

>[!Question] What is the command we can use to send an ICMP echo request to test our connection to the target?
> ping

>[!Question] From your scans, what version is FTP running on the target?
> vsftpd 3.0.3

>[!Question] From your scans, what OS type is running on the target?
> Unix

>[!Question] What is the command we need to run in order to display the 'ftp' client help menu?
> ftp -?

>[!Question] What is username that is used over FTP when you want to log in without having an account?
> anonymous

>[!Question] What is the response code we get for the FTP message 'Login successful'?
> 230

>[!Question] There are a couple of commands we can use to list the files and directories available on the FTP server. One is dir. What is the other that is a common way to list files on a Linux system.
> ls

>[!Question] What is the command used to download the file we found on the FTP server?
> get

>[!Question] Submit root flag
> 035db21c881520061c53e0536e44f815