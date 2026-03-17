---
tags:
  - " "
  - Puerto-SSH
  - Puerto-Werkzeug
  - Escalada-Horizontal
---
## 1. Reconocimiento de Puertos con Nmap

Iniciamos la auditoría realizando un escaneo de puertos en todo el rango (65535) para identificar los servicios expuestos en la máquina objetivo.

```Bash
nmap -sC -sV -O -p- <IP_DEL_OBJETIVO>
```

**Resultados Clave:**

| **Puerto**   | **Servicio** | **Versión**                          |
| ------------ | ------------ | ------------------------------------ |
| **22/tcp**   | ssh          | OpenSSH 9.2p1 Debian 2+deb12u5       |
| **5000/tcp** | http         | Werkzeug httpd 2.2.2 (Python 3.11.2) |

El servicio en el puerto 5000 corresponde a **Werkzeug**, un servidor web para aplicaciones Python (frecuentemente Flask). Es importante destacar que las aplicaciones basadas en Werkzeug pueden ser críticamente vulnerables (RCE) si el modo _Debug_ está expuesto, por lo que será nuestro vector principal de análisis.

## 2. Enumeración Web y Obtención de Credenciales

Accedemos al servicio web en el puerto 5000 (`http://<IP_DEL_OBJETIVO>:5000`) y nos encontramos con la página principal de una pizzería.

### 2.1. Panel de Autenticación (Default Credentials)

En la esquina superior derecha identificamos un portal de inicio de sesión (_login_). Como primera prueba en cualquier formulario de autenticación, probamos credenciales por defecto débiles.

- **Usuario:** `admin`
- **Contraseña:** `admin`

La autenticación es exitosa, lo que evidencia una vulnerabilidad de **Credenciales por Defecto**.

![[BaluFood-login.png]]

![[BaluFood-sesion-iniciada.png]]

### 2.2. Fuga de Información

Ya autenticados en la plataforma, procedemos a inspeccionar el código fuente de la página renderizada (`Ctrl+U`).

En el código fuente identificamos un comentario o fragmento de código expuesto accidentalmente que revela las siguientes credenciales de acceso al sistema:

- **Usuario:** `sysadmin`
- **Contraseña:** `backup123`

## 3. Acceso Inicial (SSH)

Con las credenciales del sistema descubiertas en la web, abandonamos la enumeración de Werkzeug y procedemos a conectarnos directamente al servidor mediante SSH.

```Bash
ssh sysadmin@<IP_DEL_OBJETIVO>
# Password: backup123
```

Confirmamos el acceso inicial exitoso.

## 4. Movimiento Lateral (Usuario balulero)

Iniciamos la enumeración local como el usuario `sysadmin`. El objetivo es revisar los archivos del aplicativo web expuesto en el puerto 5000.

### 4.1. Análisis del Código Backend (`app.py`)

Listando los archivos en el directorio actual, encontramos el código fuente principal de la aplicación web: `app.py`. Al leer su contenido, detectamos un dato sensible:

```Bash
cat app.py
```

**Fragmento relevante:**

```Python
app.secret_key = 'cuidaditocuidadin'
```

La clave secreta de Flask/Werkzeug es **`cuidaditocuidadin`**.

### 4.2. Movimiento Lateral

Revisando el archivo `/etc/passwd`, identificamos a otro usuario humano en el sistema llamado **`balulero`**. Basándonos en la posibilidad de reutilización de contraseñas (muy común en entornos CTF y empresariales), intentamos usar la clave secreta de la aplicación web como contraseña para este usuario.

Pivotamos al nuevo usuario:

```Bash
su balulero
# Password: cuidaditocuidadin
```

El movimiento lateral es exitoso.

## 5. Escalada de Privilegios

### 5.1. Enumeración del Historial y `.bashrc`

Consultamos el historial de comandos ejecutados recientemente:

```Bash
history
```

El historial revela que el usuario ha estado interactuando y modificando su archivo de configuración de terminal local (`~/.bashrc`). Procedemos a inspeccionar este archivo oculto:

```Bash
cat ~/.bashrc
```

Al final del archivo, detectamos un alias de terminal configurado por el usuario:

```Bash
alias ser-root='echo chocolate2 | su - root'
```

### 5.2. Obtención de Root

El alias contiene embebida en texto plano la contraseña del usuario `root` (**`chocolate2`**) para automatizar la elevación de privilegios. Extraemos la contraseña y la utilizamos manualmente (o simplemente invocamos el alias).

```Bash
su root
# Password: chocolate2
```

Verificamos el compromiso total de la máquina:

```Bash
whoami
# root
```
