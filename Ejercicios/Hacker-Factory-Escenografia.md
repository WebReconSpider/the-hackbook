## 1. Reconocimiento y Extracción Inicial

Comenzamos el reto con un archivo de presentación de PowerPoint (`presentacion.pptx`). En el análisis forense, es fundamental recordar que los archivos con formato Office Open XML (`.docx`, `.xlsx`, `.pptx`) son, en su estructura subyacente, archivos comprimidos en formato ZIP.

Verificamos el tipo de archivo real utilizando el comando `file`:

```Bash
file presentacion.pptx
# presentacion.pptx: Zip archive data, at least v2.0 to extract
```

Procedemos a descomprimir el documento para analizar los recursos incrustados. Es recomendable usar el flag `-d` para extraer el contenido en un directorio ordenado y no ensuciar el espacio de trabajo:

```Bash
unzip presentacion.pptx -d presentacion_ext
```

Al explorar los archivos extraídos, nos dirigimos al directorio donde habitualmente se almacenan los recursos multimedia de la presentación. En la ruta `presentacion_ext/ppt/media/` encontramos los siguientes archivos clave para los retos:

- `1.png`
- `2.jpg`
- `3.jpg`
- `Live is a race.jpg`

## 2. Reto 1: Esteganografía en Audio (Espectrograma)

El primer archivo se llama `1.png`. Sin embargo, en ciberseguridad nunca debemos confiar en las extensiones de los archivos. Verificamos su firma real (Magic Bytes):

```Bash
file 1.png 
# 1.png: RIFF (little-endian) data, WAVE audio, Microsoft PCM, 16 bit, mono 44100 Hz
```

La salida confirma que se trata de un archivo de audio WAVE disfrazado de imagen. Para buscar información oculta en frecuencias de audio (esteganografía acústica), procedemos a visualizar su espectrograma.

**Método A: Uso de Audacity**

1. Abrimos el archivo renombrado (`1.wav`) en la herramienta Audacity.
2. En las opciones de la pista, cambiamos la vista de "Forma de onda" a "Espectrograma".
3. Ajustamos el zoom vertical y horizontal para revelar el texto oculto en las frecuencias.

![[Pasted image 20260724183229.png]]

**Método B: Decodificador Web (SSTV / Spectrograph)** De forma alternativa, utilizamos una herramienta de análisis de espectro en línea (como `[https://spectrograph.dippanbhusal.tech/](https://spectrograph.dippanbhusal.tech/)`). Al cargar el archivo en el módulo de decodificación (Decoder), la representación gráfica del sonido revela claramente el texto.

![[Pasted image 20260724183416.png]]

- **Flag 1 obtenida:** `AMO A LOS GATITOS`

## 3. Reto 2: Análisis de Metadatos

El segundo archivo es `2.jpg`. El vector más común y rápido para inspeccionar imágenes en retos CTF es revisar sus metadatos EXIF. Utilizando la herramienta `exiftool`, volcamos la información del archivo:

```Bash
exiftool 2.jpg
```

Revisando las etiquetas de salida (como _Comment_, _Description_ o campos personalizados), identificamos directamente la segunda bandera en texto claro.

- **Flag 2 obtenida:** `FLAG{VIVA_ESPAÑA}`

## 4. Reto 3: Fuerza Bruta y Extracción (Stegseek / Steghide)

Para el archivo `3.jpg`, sospechamos de la presencia de un archivo incrustado mediante la herramienta `steghide`. Dado que no poseemos una contraseña, realizamos un ataque de diccionario utilizando `stegseek` apoyándonos en el popular diccionario `rockyou.txt`.

```Bash
stegseek 3.jpg /usr/share/wordlists/rockyou.txt
```

**Resultado de Stegseek:**

```
[i] Found passphrase: "password123"
[i] Original filename: "flag.txt".
[i] Extracting to "3.jpg.out".
```

`Stegseek` rompe la contraseña (`password123`) y automáticamente extrae el archivo oculto como `3.jpg.out`.

Alternativamente, habiendo descubierto la contraseña, la extracción manual con `steghide` se realizaría así:

```Bash
steghide extract -sf 3.jpg -p "password123"
```

Leemos el contenido del archivo de texto extraído (`flag.txt` o `3.jpg.out`):

```Bash
cat flag.txt
# FLAG{EMULADORPS5}
```

- **Flag 3 obtenida:** `FLAG{EMULADORPS5}`

## 5. Reto 4: Esteganografía Multicapa (OpenPuff)

El objetivo final es revelar el contenido oculto en la imagen `'Live is a race.jpg'`.

La pista radica en el uso de la herramienta **OpenPuff**, un software de esteganografía avanzado que permite dividir la clave de descifrado en múltiples contraseñas. Dado que es un binario de Windows, lo ejecutamos en nuestro entorno Linux a través de `wine`:

```Bash
wine OpenPuff.exe
```

**Proceso de Extracción:**

1. En la interfaz principal de OpenPuff, seleccionamos la opción de extracción (**Unhide**).

2. El programa nos solicita contraseñas (A, B y C). Introducimos las tres _flags_ recolectadas en los pasos anteriores:
    - **Clave A:** `AMO A LOS GATITOS`
    - **Clave B:** `FLAG{VIVA_ESPAÑA}`
    - **Clave C:** `FLAG{EMULADORPS5}`

3. Cargamos el archivo `'Live is a race.jpg'` como portador (Carrier) y procedemos a completar la decodificación.

Al finalizar, la herramienta desencripta y extrae exitosamente el payload final, completando el escenario.






-------
ruta al reto: https://github.com/Hacker-Factory-CTF-Team

tenemos un pptx con 4 retos de escenografía
1. descomprimir el documento office (es un .zip por debajo) `unzip presentacion.pptx` 

file presentacion.pptx    
presentacion.pptx: Zip archive data


en el directorio `ppt/media` encontramos los retos `1.png, 2.jpg, 3.jpg ,'Live is a race.jpg'` 

## Reto 1
aunque la terminación es `.png`, el comando file demustra que realmente es un audio
``` 
file 1.png               
1.png: RIFF (little-endian) data, WAVE audio
```

### Audacity

abrimos el archivo. en `...` activamos `espectograma`. modificamos el zoom y podemos observar la flag `AMO A LOS GATITOS` 


### SSTV.PRO
accedemos a `https://spectrograph.dippanbhusal.tech/` -> Decoder -> seleccionamos el archivo y encontramos el texto
![[Pasted image 20260724183416.png]]

## Reto 2

leemos los metadatos del jpg `exiftool 2.jpg` y encontramos la flag `FLAG{VIVA_ESPAÑA}` 

## Reto 3

utilizamos stegseek para probar fuerza bruta con un diccionario

``` 
stegseek 3.jpg /usr/share/wordlists/rockyou.txt                     
  
[i] Found passphrase: "password123"  
[i] Original filename: "flag.txt".  
[i] Extracting to "3.jpg.out".
``` 

ahora que hemos encontrado un archivo oculto y la contraseña, usamos steghide
```
steghide extract -sf 3.jpg -p "password123"       
anot� los datos extra�dos e/"flag.txt".


cat flag.txt    
FLAG{EMULADORPS5}
```

## Reto 4

ya temos las 3 flag. el reto final es usarlas simultaneamente para obtener el contenido del archivo `'Live is a race.jpg'` 

`wine OpenPuff.exe`. Seleccionamos `Unhide`, colocamos las 3 contraseñas, seleccionamos el archivo y completamos el reto
