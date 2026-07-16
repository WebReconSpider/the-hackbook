# Meow

Comprobamos la conexion con 
```bash
ping 10.129.39.71
```

Comprobamos los puertos abiertos con Nmap
```bash
nmap -O -sCV -p- 10.129.39.71
```
Salida:
23/tcp open  telnet  Linux telnetd

![image.png](Meow-NMAP.png)

Realizar conexión via telnet:
```bash
telnet 10.129.39.71
```

Necesitamos las credenciales, en los sistemas linux, el nombre de la cuenta administrador es root. Probamos: “root” y accedemos

![image.png](Meow-telnet.png)

Comprobamos los archivos existentes en la ruta actual:
```bash
root@Meow:~# ls -la
total 36
drwx------  5 root root 4096 Jun 18  2021 .
drwxr-xr-x 20 root root 4096 Jul  7  2021 ..
lrwxrwxrwx  1 root root    9 Jun  4  2021 .bash_history -> /dev/null
-rw-r--r--  1 root root 3132 Oct  6  2020 .bashrc
drwx------  2 root root 4096 Apr 21  2021 .cache
-rw-r--r--  1 root root   33 Jun 17  2021 flag.txt          <--
drwxr-xr-x  3 root root 4096 Apr 21  2021 .local
-rw-r--r--  1 root root  161 Dec  5  2019 .profile
-rw-r--r--  1 root root   75 Mar 26  2021 .selected_editor
drwxr-xr-x  3 root root 4096 Apr 21  2021 snap

```

Comprobamos el contenido del archivo con el comando
```bash 
cat flag.txt

b40abdfe23665f766f9c61ecba8a4c19
```

---

>[!Question] What does the acronym VM stand for?
> virtual machine

>[!Question] What tool do we use to interact with the operating system in order to issue commands via the command line, such as the one to start our VPN connection? It's also known as a console or shell.
>terminal

>[!Question] What service do we use to form our VPN connection into HTB labs?
> openvpn

>[!Question] What tool do we use to test our connection to the target with an ICMP echo request?
> ping

>[!Question] What is the name of the most common tool for finding open ports on a target?
> nmap

>[!Question] What service do we identify on port 23/tcp during our scans?
> telnet

>[!Question] What username is able to log into the target over telnet with a blank password?
> root

>[!Question] Submit root flag
> b40abdfe23665f766f9c61ecba8a4c19
