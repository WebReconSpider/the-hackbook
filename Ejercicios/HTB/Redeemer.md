Comprobamos la conexion con 
```bash
ping 10.129.4.24
```

Comprobamos los puertos abiertos con Nmap  (con opción -sV para ver la versión de FTP) (-O para saber el SO)
```bash
nmap -O -sCV -p- 10.129.4.24
```
Salida:
6379/tcp open  redis   Redis key-value store 5.0.7

nos conectamos al servidor Redis con el comando
```
redis-cli -h 10.129.4.24
```
Una vez accedemos, podemos ver información y estadisticas con `info`

![[Redeemer-redis-cli.png]]
Únicamente hay una BD, la seleccionamos scon `select 0`. Listamos todas las claves de la base con: `keys *`
![[Redeemer-keys.png]]
Podemos ver el contenido con el comando `get <nombre>`
![[Redeemer-flag.png]]

--- 
>[!Question] Which TCP port is open on the machine?
>6379

>[!Question] Which service is running on the port that is open on the machine?
>redis

>[!Question] What type of database is Redis? Choose from the following options: (i) In-memory Database, (ii) Traditional Database
> In-memory Database

>[!Question] Which command-line utility is used to interact with the Redis server? Enter the program name you would enter into the terminal without any arguments.
> redis-cli

>[!Question] Which flag is used with the Redis command-line utility to specify the hostname?
> -h

>[!Question] Once connected to a Redis server, which command is used to obtain the information and statistics about the Redis server?
> info

>[!Question] What is the version of the Redis server being used on the target machine?
> 5.0.7

>[!Question] Which command is used to select the desired database in Redis?
>select

>[!Question] How many keys are present inside the database with index 0?
>4

>[!Question] Which command is used to obtain all the keys in a database?
>keys *

>[!Question] Submit root flag
> 03eld2b376c37ab3f5319922053953eb
