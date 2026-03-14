## 1. Reconocimiento de Puertos con Nmap

Iniciamos la auditoría con un escaneo completo de puertos y servicios para identificar la superficie de ataque expuesta.

```Bash
nmap -sC -sV -O -p- <IP_DEL_OBJETIVO>
```

**Resultados:**

| **Puerto** | **Servicio** | **Versión**                      |
| ---------- | ------------ | -------------------------------- |
| **22/tcp** | ssh          | OpenSSH 9.6p1 Ubuntu 3ubuntu13.5 |
| **80/tcp** | http         | Apache httpd 2.4.58 (Ubuntu)     |

## 2. Enumeración Web y Obtención de Credenciales

Al acceder al servicio web, comprobamos que solo se muestra la página genérica de Apache ("It works!").

### 2.1. Fuzzing de Directorios

Realizamos una búsqueda de directorios y archivos ocultos para descartar paneles de administración.

```Bash
gobuster dir -u http://<IP_DEL_OBJETIVO> -w /usr/share/wordlists/dirb/common.txt -x html,php,txt
```

La enumeración no devuelve resultados de interés (únicamente el `index.html` y errores 403), por lo que cambiamos el enfoque hacia la inspección directa del sitio.

### 2.2. Fuga de Información en Código Fuente (Source Code)

Inspeccionamos el código fuente HTML de la página principal (`Ctrl+U`). Al final del documento, oculto como un comentario, encontramos el siguiente texto:

Por el patrón de caracteres y el relleno con signos de igual (`==`), identificamos claramente dos cadenas codificadas en **Base64** separadas por dos puntos. Procedemos a decodificarlas en nuestra terminal:

```Bash
echo "ZGFuaWVsYQ==" | base64 -d
# daniela
echo "Zm9jYXJvamE=" | base64 -d
# focaroja
```

Hemos obtenido nuestro primer par de credenciales válidas: **`daniela:focaroja`**.

## 3. Acceso Inicial (SSH)

Utilizamos las credenciales obtenidas para autenticarnos a través del servicio SSH.

```Bash
ssh daniela@<IP_DEL_OBJETIVO>
# Password: focaroja
```

## 4. Movimiento Lateral (Usuario Diego)

Iniciamos la enumeración del sistema listando todos los archivos del directorio de trabajo del usuario actual, incluyendo los ocultos (`-la`).

```Bash
ls -la
```

### 4.1. Enumeración de Archivos Ocultos

Encontramos dos elementos de interés:

1. Una nota en el escritorio (`Desktop/nota`).
2. Un directorio oculto llamado `.secreto`.

Leemos la nota del escritorio:

```Bash
cat Desktop/nota
# Daniela no recuerdo donde guarde la password de root, si la encuentras me dices.
```

Exploramos el directorio oculto:

```Bash
cd .secreto/
ls -la
cat passdiego
# YmFsbGVuYW5lZ3Jh
```

### 4.2. Decodificación y Pivoting

El contenido del archivo `passdiego` vuelve a ser una cadena en Base64. La decodificamos:

```Bash
echo "YmFsbGVuYW5lZ3Jh" | base64 -d
# ballenanegra
```

Dado el nombre del archivo (`passdiego`), la contraseña pertenece al usuario `diego`. Pivotamos a este nuevo usuario iniciando una nueva sesión (o utilizando el comando `su`):

```Bash
ssh diego@<IP_DEL_OBJETIVO>
# Password: ballenanegra
```


## 5. Escalada de Privilegios

Ya autenticados como `diego`, reanudamos la búsqueda exhaustiva de archivos ocultos para localizar la contraseña de root mencionada en la nota inicial.

### 5.1. Evasión de Pistas Falsas (Rabbit Holes)

En el directorio del usuario encontramos una carpeta oculta `.passroot` con un archivo `.pass`.

```Bash
cat .passroot/.pass
# YWNhdGFtcG9jb2VzdGE=
```

Al decodificarlo obtenemos:

```Bash
echo "YWNhdGFtcG9jb2VzdGE=" | base64 -d
# acatampocoesta
```

Esto es un _"rabbit hole"_ (pista falsa). Continuamos la enumeración en directorios de usuario no estándar.

### 5.2. Resolución del Acertijo

Al listar el directorio `.local/share`, descubrimos un archivo de sistema con un nombre peculiar: `.-`.

```Bash
cat .local/share/.-
```

**Contenido del archivo:**

```
password de root
En un mundo de hielo, me muevo sin prisa,
con un pelaje que brilla, como la brisa.
No soy un rey, pero en cuentos soy fiel,
de un color inusual, como el cielo y el martambien.
Soy amigo de los ni~nos, en historias deensue~no.
Quien soy, que en el frio encuentro mi due~no?
```

Resolvemos el acertijo. La respuesta a un oso que vive en el hielo y es de color inusual (cielo y mar) es **osoazul**.

### 5.3. Obtención de Root

Utilizamos la respuesta del acertijo como contraseña para escalar privilegios hacia el usuario `root`.

```Bash
su root
# Password: osoazul
```

Confirmamos el compromiso total de la máquina:

```Bash
whoami
# root
```

