---
tags:
  - " "
  - Puerto-SSH
  - Puerto-Apache-Httpd
  - Vulnerabilidad-XSS
  - Binario-Env-Suid
---
## 1. Reconocimiento de Puertos con Nmap

Iniciamos la auditoría de seguridad realizando un escaneo de puertos y servicios para identificar la superficie de ataque expuesta por la máquina objetivo.

```Bash
nmap -sC -sV -O <IP_DEL_OBJETIVO>
```

**Resultados:**

|**Puerto**|**Estado**|**Servicio**|**Versión**|
|---|---|---|---|
|**22/tcp**|Open|ssh|OpenSSH 9.2p1 Debian|
|**80/tcp**|Open|http|Apache httpd 2.4.62 (Debian)|

El servidor web en el puerto 80 nos indica en su título que aloja un "Laboratorio de Cross-Site Scripting (XSS)".

## 2. Enumeración Web y Pruebas XSS

Al acceder a `http://<IP_DEL_OBJETIVO>`, confirmamos que la aplicación web está diseñada como un entorno de pruebas interactivo compuesto por 4 laboratorios para explotar vulnerabilidades XSS. El aplicativo indica que, tras superar los 4 retos, se proporcionarán credenciales válidas para el servicio SSH.
![[Reflection_Inicio.png]]

### 2.1. Laboratorio 1: XSS Reflejado (Reflected XSS)

Comenzamos comprobando si la aplicación sanitiza las etiquetas HTML básicas realizando una prueba de **HTML Injection**:

- **Payload:** `<h1> Hola </h1>`

Al verificar que el texto se renderiza como un encabezado HTML, confirmamos que la entrada no está siendo filtrada. Procedemos a inyectar código JavaScript malicioso.

- **Payload XSS:** `<img src=x onerror=alert("XSS")>`

El código se ejecuta exitosamente. Observamos que el payload queda reflejado directamente en la URL a través de una petición GET: `http://<IP_DEL_OBJETIVO>/laboratorio1/?input=%3Cimg+src%3Dx+onerror%3Dalert%28%22XSS%22%29%3E`

**Impacto del XSS Reflejado:** Este tipo de vulnerabilidad requiere interacción del usuario (ingeniería social). Si un atacante convence a una víctima para que haga clic en este enlace manipulado, el script se ejecutará en el navegador de la víctima. Esto permite ataques críticos como:

- **Robo de Cookies (Session Hijacking):** Permite al atacante suplantar la sesión del usuario.
- **Redirecciones Maliciosas:** Enviar al usuario a sitios de _phishing_.
- **Keylogging:** Registrar las pulsaciones de teclado del usuario en esa página.

![[Reflection_XSS_Reflejado.png]]

### 2.2. Laboratorio 2: XSS Almacenado (Stored XSS)

En este segundo laboratorio, inyectamos el mismo payload:

- **Payload:** `<img src=x onerror=alert("XSS")>`

**Diferencia Fundamental con el Laboratorio 1:** A diferencia del XSS Reflejado, donde el código malicioso viaja en la URL de la petición, en este caso el payload se **guarda en la base de datos** del servidor (XSS Almacenado o Persistente). Como resultado, el código no aparece en la URL, sino que se inyecta permanentemente en la página. **Cualquier usuario** que visite este recurso en el futuro ejecutará el código malicioso automáticamente, sin necesidad de hacer clic en un enlace manipulado. Esto hace que el XSS Almacenado sea mucho más peligroso y de mayor alcance.

![[Reflection_XSS_Almacenado.png]]

### 2.3. Laboratorio 3: Manipulación de Parámetros Restringidos

Este laboratorio presenta un formulario basado en listas desplegables (Dropdowns), lo que aparentemente impide introducir texto libre.

Sin embargo, las restricciones en el lado del cliente (frontend) siempre pueden ser evadidas. Al realizar una selección legítima, observamos que los valores viajan por la URL mediante parámetros GET: `http://<IP_DEL_OBJETIVO>/laboratorio3/?opcion1=ValorA&opcion2=ValorX&opcion3=Opcion1`

Interceptamos o modificamos directamente la URL para inyectar nuestro payload en uno de los parámetros:

`http://<IP_DEL_OBJETIVO>/laboratorio3/?opcion1=<img src=x onerror=alert("XSS")>&opcion2=ValorX&opcion3=Opcion1`

El XSS se ejecuta correctamente.
_Nota:_ Si los parámetros no viajaran por la URL (método POST), esta misma técnica se realizaría interceptando la petición HTTP con **Burp Suite**, modificando el cuerpo de la petición antes de enviarla al servidor.

![[Reflection_XSS_Dropdowns.png]]

### 2.4. Laboratorio 4: Inyección por Parámetro Específico

La aplicación nos proporciona una pista directa: debemos enviar un parámetro específico llamado `?data`. Concatenamos el parámetro en la URL junto a nuestro payload para completar el último reto:

`http://<IP_DEL_OBJETIVO>/laboratorio4/?data=<img src=x onerror=alert("XSS")>`

## 3. Acceso Inicial (SSH)

Tras completar con éxito los 4 laboratorios, la aplicación web nos revela las credenciales de acceso al sistema, cumpliendo con la premisa inicial.

Utilizamos estas credenciales para autenticarnos a través del servicio SSH.

```Bash
ssh usuario@<IP_DEL_OBJETIVO>
# (Contraseña obtenida en el aviso web)
```

![[Reflection_Aviso.png]]

## 4. Escalada de Privilegios

### 4.1. Enumeración de Binarios SUID

Una vez dentro del sistema, nuestro objetivo es escalar a `root`. Comenzamos buscando archivos que posean el bit SUID (Set Owner User ID up on execution) activado. Estos binarios se ejecutan temporalmente con los privilegios de su propietario (root).

```Bash
find / -perm -4000 -user root 2>/dev/null
```

**Salida Relevante:**

```
/usr/bin/chfn  
/usr/bin/chsh  
/usr/bin/env  <-- VULNERABLE
/usr/bin/gpasswd  
/usr/bin/mount  
...
```

Identificamos que el binario `/usr/bin/env` tiene permisos SUID.

### 4.2. Explotación de `env` (GTFOBins)

El comando `env` se utiliza para ejecutar otro programa en un entorno modificado. Cuando posee el bit SUID, podemos utilizarlo para invocar una shell (`/bin/sh`). Al añadir el flag `-p` (privilegiado), le indicamos a la shell que no restablezca el ID de usuario efectivo, permitiéndonos heredar los privilegios de root del binario `env`.

Ejecutamos el comando de explotación:

```Bash
/usr/bin/env /bin/sh -p
```

Verificamos el éxito de la escalada:

```Bash
whoami
# root
```
