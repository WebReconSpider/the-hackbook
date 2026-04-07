---
tags:
  - " "
  - Puerto-Apache-Httpd
  - WordPress
  - Vulnerabilidad-WordPress
  - Cookie-Hijacking
  - Informa
  - Information-Disclosure
---
## 1. Reconocimiento Inicial

Iniciamos la auditoría con un escaneo de puertos para identificar los servicios expuestos en el servidor objetivo.

```Bash
nmap -sV -O -Pn 172.17.0.2
```

**Resultados Clave:**

- **80/tcp open http:** Apache httpd 2.4.52 (Ubuntu).
- **3000/tcp open ppp?:** Servicio desconocido por Nmap (usualmente asociado a _frontends_ de desarrollo como React/Node).
- **8000/tcp open http:** WSGIServer 0.2 (Python 3.10.12), lo que indica una aplicación web basada en Python.

Para obtener más información del puerto 80, utilizamos la extensión **Wappalyzer**, la cual nos confirma la siguiente tecnológia:

- **Gestor de Contenido:** WordPress versión 6.9.4
- **Lenguaje:** PHP
- **Base de Datos y SO:** MySQL y Ubuntu.
![[Bigwear-wappalyzer.png]]

## 2. Enumeración de WordPress

Con la confirmación de WordPress, procedemos a realizar un escaneo de vulnerabilidades y enumeración de usuarios utilizando `wpscan`.

```Bash
wpscan --url http://172.17.0.2/ -e u,p
```

**Resultados de la Enumeración:**

- Se identifica el archivo `robots.txt`.
- Se descubre el usuario válido: **`admin`**.
- Se encuentra un plugin `pie-register`, cuya versión es 3.7.1.4
- 
_(Nota de Auditoría: ¿Por qué se filtran los usuarios? WordPress, por defecto, tiene habilitada la REST API. Si accedes a la ruta `/wp-json/wp/v2/users/`, el sistema devuelve un JSON con la información de todos los usuarios registrados que han publicado contenido. Cambiando el ID, puedes enumerar toda la base de datos a menos que el administrador bloquee explícitamente este endpoint)._

### 2.1. Análisis de Puertos (Contexto de la Aplicación)

- **Puerto 80 (WordPress):** sirve para gestionar los artículos separándolo de contenido publicitario del frontend

- **Puerto 3000 (Frontend):** Expone la interfaz gráfica de la tienda de ropa "BIGWEAR", construida en React, con catálogos de camisetas y pantalones.
![[Bigwear-3000.png]]
- **Puerto 8000 (Backend API/Django):** Al acceder a este puerto, nos devuelve un error 404 en modo Debug (`DEBUG = True`), lo que supone una vulnerabilidad adicional de _Information Disclosure_. Esta página de error nos filtra todas las rutas de la API interna (`/api/auth/login`, `/api/auth/perfil`, etc.) y nos revela la ruta `/admin/`. Al navegar a `http://172.17.0.2:8000/admin/`, encontramos el portal de administración del backend de la tienda, donde se gestionan productos, y otros datos.
![[Bigwear-8000.png]]

## 3. Explotación (CVE-2025-34077 - Session Hijacking)

En lugar de realizar fuerza bruta contra el panel de login (`/wp-login.php`), buscamos vulnerabilidades en versiones. Encontramos que la versión del plugin es vulnerable a **CVE-2025-34077**. Esta vulnerabilidad permite el secuestro de sesión (_Session Hijacking_) extrayendo las _cookies_ de autenticación sin requerir la contraseña.

Ejecutamos un _exploit_ público (`pie.py` / `simpleRS.py`) contra el objetivo:

```Bash
python3 simpleRS.py http://172.17.0.2
```

**Salida Exitosa:** El _exploit_ logra secuestrar la sesión del usuario con ID 1 (`admin`) y nos devuelve dos _cookies_ críticas:
- `wordpress_a2a379b8590d3431d7153bb3b68da0df`
- `wordpress_logged_in_a2a379b8590d3431d7153bb3b68da0df`

**Inyección de Cookies:** Accedemos a la página principal del sitio. A través de las herramientas de desarrollador del navegador (F12 -> Application -> Cookies), añadimos los nombres y valores de las _cookies_ obtenidas. Al recargar la página, el sistema nos reconoce y nos otorga acceso directo al panel de control (_Dashboard_) como administrador.
![[Bigwear-cookies.png]]

## 4. Obtención de Reverse Shell (RCE)

Con acceso de administrador en WordPress, el objetivo es ejecutar comandos en el servidor subyacente (RCE).
1. Nos dirigimos a la sección de **Plugins** y aprovechamos nuestros privilegios para instalar el plugin **"File Manager"** (Administrador de Archivos).
2. Utilizándolo, navegamos por el directorio web y editamos el archivo `index.php` (o cualquier otro archivo .php).
![[Bigwear-file-manager.png]]
3. Inyectamos un payload de Reverse Shell en PHP.
4. Ponemos un listener en escucha en nuestra máquina atacante (`nc -nlvp 443`) y ejecutamos el archivo modificado navegando hacia él (clic en index.php -> get info -> hacemos clic).
5. Obtenemos acceso al servidor como el usuario de servicio web (`www-data`).

## 5. Post-Explotación y Análisis de Infraestructura

Una vez dentro del servidor, comenzamos la enumeración de directorios para comprender la arquitectura completa de la aplicación, ya que recordamos que había servicios adicionales en los puertos 3000 y 8000.

Navegamos al directorio `/opt/bigwear/backend/` y leemos el código fuente. Localizamos un archivo crítico de configuración llamado `setting.py`.

```Bash
cat /opt/bigwear/backend/setting.py
```

**Fuga de Información (Hardcoded Credentials):**

```Python
# Credenciales del panel de administración  
ADMIN_USERNAME = 'pepe'  
ADMIN_PASSWORD = 'BigWear2024!@#'
```

## 6. Escalada de Privilegios

Intentamos escalar privilegios directamente al usuario `root` del sistema operativo utilizando la contraseña.

```Bash
su root
# Password: BigWear2024!@#
```

La autenticación es exitosa. Hemos logrado comprometer el servidor en su totalidad debido a una mala práctica de gestión de contraseñas.

```Bash
whoami
# root
```

Con las credenciales encontradas, tambien podemos acceder al panel de administración de Django
![[Bigwear-administration.png]]

Aunque la vía lógica parecería comprometer el panel de Django para buscar un nuevo RCE, en las auditorías de seguridad siempre se debe comprobar la **reutilización de contraseñas** (_Password Reuse_).
