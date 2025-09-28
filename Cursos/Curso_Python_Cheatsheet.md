# Chuletas de Comandos de Python

## Tipos de Datos y Operadores

| Tipo de Dato            | Ejemplo                |
| ----------------------- | ---------------------- |
| **Enteros (`int`)**     | `numero = 10`          |
| **Flotantes (`float`)** | `decimal = 10.5`       |
| **Cadenas (`str`)**     | `texto = "Hola Mundo"` |
| **Booleanos (`bool`)**  | `es_verdadero = True`  |

### Operadores Aritméticos 

| Operador | Descripción | Ejemplo |
|---|---|---|
| `+` | Suma | `5 + 3` (8) |
| `-` | Resta | `5 - 3` (2) |
| `*` | Multiplicación | `5 * 3` (15) |
| `/` | División (flotante) | `5 / 2` (2.5) |
| `//` | División entera | `5 // 2` (2) |
| `%` | Módulo (resto) | `5 % 2` (1) |
| `**` | Exponenciación | `5 ** 2` (25) |

### Operadores de Comparación

| Operador | Descripción | Ejemplo |
|---|---|---|
| `==` | Igual a | `5 == 5` (True) |
| `!=` | Diferente de | `5 != 3` (True) |
| `<` | Menor que | `5 < 3` (False) |
| `>` | Mayor que | `5 > 3` (True) |
| `<=` | Menor o igual que | `5 <= 5` (True) |
| `>=` | Mayor o igual que | `5 >= 3` (True) |

### Operadores Lógicos

| Operador | Descripción | Ejemplo |
|---|---|---|
| `and` | AND lógico | `True and False` (False) |
| `or` | OR lógico | `True or False` (True) |
| `not` | NOT lógico | `not True` (False) |

### Operadores de Asignación

| Operador | Descripción | Ejemplo |
|---|---|---|
| `=` | Asignación simple | `x = 10` |
| `+=` | Suma y asignación | `x += 5` (x = x + 5) |
| `-=` | Resta y asignación | `x -= 5` (x = x - 5) |
| `*=` | Multiplicación y asignación | `x *= 5` (x = x * 5) |
| `/=` | División y asignación | `x /= 5` (x = x / 5) |
| `%=` | Módulo y asignación | `x %= 5` (x = x % 5) |
| `**=` | Exponenciación y asignación | `x **= 2` (x = x ** 2) |
| `//=` | División entera y asignación | `x //= 2` (x = x // 2) |

## Funciones

| Concepto                   | Descripción                           | Sintaxis / Ejemplo                                                |
| -------------------------- | ------------------------------------- | ----------------------------------------------------------------- |
| **Definición**             | Bloque de código reutilizable.        | `def mi_funcion():` <br> `    print("Hola")`                      |
| **Parámetros**             | Valores que se pasan a la función.    | `def saludo(nombre):` <br> `    print(f"Hola, {nombre}")`         |
| **Retorno**                | Valor que devuelve la función.        | `def suma(a, b):` <br> `    return a + b`                         |
| **Parámetros por Defecto** | Valores predefinidos para parámetros. | `def saludo(nombre="Mundo"):` <br> `    print(f"Hola, {nombre}")` |


## Listas

| Concepto              | Descripción                                                                       | Sintaxis / Ejemplo                                                                                |
| --------------------- | --------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| **Definición**        | Colección ordenada y mutable de elementos.                                        | `mi_lista = [1, "dos", 3.0, True]`                                                                |
| **Acceso por Índice** | Los índices pueden ser positivos (desde 0) o negativos (desde -1 para el último). | `mi_lista[0]` (1) <br> `mi_lista[-1]` (True)                                                      |
| **Slicing**           | Extraer sub-listas.                                                               | `mi_lista[1:3]` (["dos", 3.0]) <br> `mi_lista[:2]` ([1, "dos"]) <br> `mi_lista[2:]` ([3.0, True]) |
| **Unir**              | Unir dos listas                                                                   | Lista3 = Lista1 + Lista2                                                                          |
| Repetición            | Repite la lista `x` veces                                                         | Lista = [1,2,3] * 3                                                                               |


### Métodos de Listas

| Método      | Descripción                                                                         | Parámetros               | Ejemplo                      |
| ----------- | ----------------------------------------------------------------------------------- | ------------------------ | ---------------------------- |
| `append()`  | Añade un elemento al final de la lista.                                             | `valor`                  | `lista.append(5)`            |
| `insert()`  | Inserta un elemento en una posición específica.                                     | `indice, valor`          | `lista.insert(1, "nuevo")`   |
| `extend()`  | Añade los elementos de una lista al final de la lista.                              | `lista`                  | `lista.extend([4, 5])`       |
| `remove()`  | Elimina la primera ocurrencia de un valor.                                          | `valor`                  | `lista.remove("dos")`        |
| `pop()`     | Elimina y devuelve un elemento en un índice dado (o el último si no se especifica). | `indice`<br>Ninguno      | `elemento = lista.pop(0)`    |
| `clear()`   | Elimina todos los elementos de la lista.                                            | Ninguno                  | `lista.clear()`              |
| `index()`   | Devuelve el índice de la primera ocurrencia de un valor.                            | `valor, [inicio], [fin]` | `indice = lista.index(3.0)`  |
| `count()`   | Cuenta el número de ocurrencias de un valor.                                        | `valor`                  | `conteo = lista.count(1)`    |
| `sort()`    | Ordena la lista en su lugar.                                                        | `[key], [reverse]`       | `lista.sort()`               |
| `reverse()` | Invierte el orden de los elementos en la lista en su lugar.                         | Ninguno                  | `lista.reverse()`            |
| `copy()`    | Devuelve una copia superficial de la lista.                                         | Ninguno                  | `nueva_lista = lista.copy()` |
| tuple()     | Convierte una lista en una tupla                                                    | Tupla                    | Tupla = tuple(lista)         |
| in          | Comprobar si un elemento pertenece a la lista                                       | ninguno                  | elemento in lista            |

## Tuplas

| Concepto                 | Descripción                                                                          | Sintaxis / Ejemplo                          |
| ------------------------ | ------------------------------------------------------------------------------------ | ------------------------------------------- |
| **Definición**           | Colección ordenada e **inmutable** de elementos.                                     | `mi_tupla = (1, "dos", 3.0)`                |
| Desempaquetado de tuplas | Declarar la tupla sin paréntesis (ya que no son obligatorios)                        | miTupla = 1,2,3<br>dia, mes, agno = miTupla |
| **Inmutabilidad**        | Una vez creada, no se puede modificar (añadir, eliminar o cambiar elementos).        | `mi_tupla[0] = 5` (Error)                   |
| **Acceso por Índice**    | Similar a las listas.                                                                | `mi_tupla[0]` (1) <br> `mi_tupla[-1]` (3.0) |
| **Slicing**              | Similar a las listas.                                                                | `mi_tupla[1:3]` (("dos", 3.0))              |
| Tupla unitaria           | Importante, para hacer una tupla unitaria, es necesario poner el elemento y una coma | miTupla = ("hola",)                         |

### Métodos de Tuplas

| Método    | Descripción                                              | Parámetros               | Ejemplo                       |
| --------- | -------------------------------------------------------- | ------------------------ | ----------------------------- |
| `count()` | Cuenta el número de ocurrencias de un valor.             | `valor`                  | `conteo = tupla.count(1)`     |
| `index()` | Devuelve el índice de la primera ocurrencia de un valor. | `valor, [inicio], [fin]` | `indice = tupla.index("dos")` |
| list()    | Convierte una tupla en una lista                         | tupla                    | lista = List(tupla)           |
| len()     | Devuelve el número de elementos de una tupla             | tupla                    | longitud = len(tupla)         |
| in        | Comprobar si un elemento pertenece a la tupla            | ninguno                  | elemento in tupla             |
|           |                                                          |                          |                               |

## Diccionarios

| Concepto                 | Descripción                                                                           | Sintaxis / Ejemplo                                                       |     |
| ------------------------ | ------------------------------------------------------------------------------------- | ------------------------------------------------------------------------ | --- |
| **Definición**           | Colección no ordenada de pares clave-valor. Las claves deben ser únicas e inmutables. | `mi_diccionario = {"nombre": "Ana", "edad": 25}`                         |     |
| **Acceso por Clave**     | Acceder al valor asociado a una clave.                                                | `mi_diccionario["nombre"]` ("Ana")                                       |     |
| **Modificación/Adición** | Cambiar el valor de una clave existente o añadir una nueva.                           | `mi_diccionario["edad"] = 26` <br> `mi_diccionario["ciudad"] = "Madrid"` |     |

### Métodos de Diccionarios

| Método     | Descripción                                                                    | Parámetros               | Ejemplo                                          |
| ---------- | ------------------------------------------------------------------------------ | ------------------------ | ------------------------------------------------ |
| `del`      | Elimina el par clave valor                                                     | clave                    | `del diccionario[valor]`                         |
| `get()`    | Devuelve el valor de la clave, o un valor por defecto si la clave no existe.   | `clave, [valor_defecto]` | `edad = diccionario.get("edad", 0)`              |
| `pop()`    | Elimina la clave y devuelve su valor.                                          | `clave, [valor_defecto]` | `nombre = diccionario.pop("nombre")`             |
| `clear()`  | Elimina todos los elementos del diccionario.                                   | Ninguno                  | `diccionario.clear()`                            |
| `keys()`   | Devuelve una vista de las claves del diccionario.                              | Ninguno                  | `claves = diccionario.keys()`                    |
| `values()` | Devuelve una vista de los valores del diccionario.                             | Ninguno                  | `valores = diccionario.values()`                 |
| `items()`  | Devuelve una vista de los pares clave-valor (como tuplas).                     | Ninguno                  | `elementos = diccionario.items()`                |
| `update()` | Actualiza el diccionario con pares clave-valor de otro diccionario o iterable. | `otro_diccionario`       | `diccionario.update({"profesion": "Ingeniera"})` |
| `copy()`   | Devuelve una copia superficial del diccionario.                                | Ninguno                  | `nuevo_diccionario = diccionario.copy()`         |


## Condicionales

| Concepto           | Descripción                                                                            | Sintaxis / Ejemplo                                                                                                                            |
| ------------------ | -------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| if                 | Ejecuta un bloque de código si la condición es verdadera.                              | if condicion: <br>     # Código                                                                                                               |
| else               | Ejecuta un bloque de código si la condición del if es falsa. **Hay que poner ':'**     | if condicion: <br>     # Código si es verdadero <br> else: <br>     # Código si es falso                                                      |
| elif               | Evalúa múltiples condiciones en secuencia.                                             | if condicion1: <br> # Código si condicion1 <br> elif condicion2: <br> # Código si condicion2 <br> else: <br> # Código si ninguna es verdadera |
| Concatenación      | La condición puede tener varias condiciones seguidas. Se evalúa de izquierda a derecha | if 0 < positivo <100: <br>     # Código                                                                                                       |
| Anidamiento        | Permite estructuras condicionales dentro de otras.                                     | if condicion_externa: <br> if condicion_interna: <br> # Código                                                                                |
| Operadores Lógicos | Combinan condiciones (and, or, not).                                                   | if a > 0 and b < 10: <br> # Código                                                                                                            |
| Operador `in`      | Comprueba si el valor está en el conjunto                                              | if variable in conjunto:<br>    # Código                                                                                                      |


## Bucle for

| Concepto            | Descripción                                                                                                                          | Sintaxis / Ejemplo                                                                                                                                                 |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Bucle for           | Itera sobre los elementos de una secuencia (listas, tuplas, cadenas, diccionarios). En cada iteración: elemento = valor de secuencia | for elemento in `[secuencia]:` &nbsp;         # Código a ejecutar por cada  elemento                                                                                 |
| Función range()     | Genera una secuencia de números para iterar.                                                                                         | range(fin): Desde 0 hasta fin-1 <br> range(inicio, fin): Desde inicio hasta fin-1 <br> range(inicio, fin, paso): Desde inicio hasta fin-1, con un paso determinado |
| Iterar con índices  | Acceder a elementos y sus índices simultáneamente.                                                                                   | for i in range(len(lista)): <br> # Usar lista[i]                                                                                                                   |
| Función enumerate() | Devuelve pares (índice, valor) al iterar.                                                                                            | for indice, valor in enumerate(secuencia): <br> # Código                                                                                                           |
| Iterar diccionarios | Recorrer claves, valores o pares clave-valor de un diccionario.                                                                      | for clave in diccionario: <br> for valor in diccionario.values(): <br> for clave, valor in diccionario.items():                                                    |
| Bucles Anidados     | Un bucle dentro de otro bucle. Útil para estructuras de datos multidimensionales.                                                    | for i in range(3): <br> for j in range(3): <br> print(f"({i}, {j})")                                                                                               |

## Bucle while

| Concepto    | Descripción                                     | Sintaxis / Ejemplo                                                                                                  |
| ----------- | ----------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| Bucle while | Se repite mientras una condición sea verdadera. | while condicion: <br> # Código a ejecutar <br> # Asegurarse de que la condición cambie para evitar bucles infinitos |

## Sentencias de Control de Bucle

| Concepto       | Descripción                                                                           | Sintaxis / Ejemplo                                                                                              |
| -------------- | ------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| continue       | Salta el resto del código en la iteración actual y pasa a la siguiente.               | for i in range(5): <br> if i == 2: continue <br> print(i) <br> Output: 0, 1, 3, 4                               |
| pass           | Es una operación nula; no hace nada. Se usa como marcador de posición.                | if condicion: <br> pass <br> else: <br> # Código                                                                |
| else en bucles | El bloque else se ejecuta cuando el bucle termina de forma natural (no por un break). | for i in range(3): <br> print(i) <br> else: <br> print("Bucle terminado") <br> Output: 0, 1, 2, Bucle terminado |


## Tratar entrada de información por teclado

| Concepto | Descripción                                                        | Sintaxis / Ejemplo                      |
| -------- | ------------------------------------------------------------------ | --------------------------------------- |
| input()  | Introducir información por teclado. **El valor SIEMPRE es un str** | entrada = input("Introduce el texto: ") |
| .upper() | Convierte el string en mayuscula                                   | variableString.upper()                  |
| .lower() | Convierte el string en minuscula                                   | variableString.lower()                  |



## Añadir
para seleccionar los n primeros elementos de un array: array[:n]

- `stats.norm(...)`  
    Crea un **objeto distribución normal** en `scipy.stats`.  
    Este objeto se puede parametrizar con:
    
    - `loc` → la **media** μ\muμ.
        
    - `scale` → la **desviación estándar** σ\sigmaσ.
        
    
    🔎 Ejemplo: `stats.norm(loc=2, scale=3)` es una gaussiana N(μ=2,σ=3)N(\mu=2, \sigma=3)N(μ=2,σ=3).
