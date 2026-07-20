# 🛡️ Resumen: Curso de Ciberseguridad y Privacidad 101 v2

Fuente: [Hixec - Aprende CIBERSEGURIDAD Desde Cero](https://www.youtube.com/watch?v=gzES0MuWqHE)

### Distinciones Clave

| Concepto                    | Definición                                                                     |
| --------------------------- | ------------------------------------------------------------------------------ |
| Seguridad de la Información | Protección de datos en cualquier formato (físico o digital).                   |
| Seguridad Informática       | Protección de la infraestructura física y digital que contiene la información. |
| Ciberseguridad              | Protección de activos digitales y sistemas interconectados en el ciberespacio. |

### La Tríada CIA + (NR + A)

Fundamentos que todo pentester debe evaluar durante una auditoría:

1.Confidencialidad: Solo personal autorizado accede a la información.

2.Integridad: La información no ha sido alterada sin autorización.

3.Disponibilidad: El sistema es accesible cuando se necesita.

4.No Repudio (NR): Garantía de que un mensaje enviado o recibido no puede ser negado.

5.Autenticidad (A): Verificación de la identidad del usuario o sistema.

## Exploit, Payload, 0-Day

Conceptos esenciales para entender el ciclo de un ataque:

•Exploit: Fragmento de software, datos o secuencia de comandos que aprovecha una vulnerabilidad para causar un comportamiento no deseado.

•Payload: La parte del exploit que ejecuta la acción dañina (ej. abrir una reverse shell).

•0-Day (Zero Day): Vulnerabilidad desconocida para el fabricante y para la cual no existe parche. Es el "santo grial" para un atacante.

## Malware y Amenazas

•Virus: Requiere intervención humana para propagarse y se adjunta a archivos.

•Gusano (Worm): Se propaga automáticamente a través de la red explotando vulnerabilidades.

•Troyano: Se disfraza de software legítimo para engañar al usuario.

•Ransomware: Cifra archivos y exige un rescate (foco actual en ataques corporativos).

•Spyware/Adware: Enfocados en espionaje y publicidad intrusiva.

## Gestión de Vulnerabilidades

Un pentester se enfoca en la intersección de estos tres elementos:

1.Amenaza (Threat): Evento potencial que puede causar daño (ej. un hacker, un desastre natural).

2.Vulnerabilidad (Vulnerability): Debilidad en el sistema que puede ser explotada.

3.Riesgo (Risk): La probabilidad de que una amenaza explote una vulnerabilidad multiplicada por el impacto.

Nota: El trabajo del pentester es identificar las vulnerabilidades para reducir el riesgo antes de que una amenaza real las explote.

## Herramientas Prácticas y Metodología

El video menciona herramientas útiles para el día a día y para fases de reconocimiento:

| Herramienta        | Uso en Pentesting / Seguridad                                            |
| ------------------ | ------------------------------------------------------------------------ |
| VirusTotal         | Análisis estático y dinámico de archivos y URLs sospechosas.             |
| Have I Been Pwned  | Verificación de fugas de credenciales (OSINT).                           |
| Mullvad Browser    | Navegación privada y segura, evitando el fingerprinting.                 |
| Expanders (bit.ly) | Verificación del destino real de enlaces acortados para evitar phishing. |

## Certificaciones

•Certificaciones: Referencia al [Security Certification Roadmap de Paul Jerimy](https://pauljerimy.com/security-certification-roadmap/) para elegir certificaciones según el área (Red Team, Blue Team, etc.).

•Laboratorios: Uso de plataformas como TryHackMe para práctica legal y controlada.

# 🛡️ Resumen: Curso de Ciberseguridad y Privacidad 202
Fuente: [Hixec - CONTINÚA Aprendiendo CIBERSEGURIDAD desde CERO](https://www.youtube.com/watch?v=Bz1jX-dH3K8)

## El Mito del "Candadito Verde" (HTTPS)

Concepto crítico para ataques de Phishing y Man-in-the-Middle (MitM):

•El candado indica que la conexión está cifrada (TLS/SSL), no que el sitio sea legítimo.

•Un atacante puede obtener un certificado SSL gratuito (ej. Let's Encrypt) para un sitio de phishing.

•Lección para Pentesting: Siempre verificar el dominio real, no solo el estado de cifrado.

## Ingeniería Social y Phishing

La ingeniería social es la manipulación psicológica para obtener información.

### Tipos de Phishing

| Tipo             | Descripción                                                                     |
| ---------------- | ------------------------------------------------------------------------------- |
| Phishing General | Campañas masivas sin un objetivo específico.                                    |
| Spear Phishing   | Ataques dirigidos a una persona o empresa específica, altamente personalizados. |
| Whaling          | Phishing dirigido a altos ejecutivos (C-level).                                 |
| Vishing          | Realizado mediante llamadas telefónicas                                         |
| Smishing         | Realizado mediante SMS                                                          |
| QRishing         | Realizado mediante código QR                                                    |

### Detección Manual

1.Remitente: Verificar que el dominio del correo coincida exactamente con la empresa oficial.

2.Gramática: Errores ortográficos o lenguaje inusual.

3.Hyperlinks: Pasar el ratón sobre el enlace para ver la URL real en la barra de estado antes de hacer clic.

4.Urgencia: Uso de amenazas o premios inmediatos para forzar una acción rápida.

## Autenticación de Múltiples Factores (MFA)

1.Algo que sabes: Contraseña, PIN, pregunta de seguridad.

2.Algo que tienes: Token físico, correo, smartphone (TOTP), tarjeta inteligente.

3.Algo que eres: Biometría (huella, iris, reconocimiento facial).

Regla de Oro: Usar al menos dos factores de diferentes categorías para maximizar la seguridad.

## Seguridad en Redes y Navegación

Riesgos comunes en entornos de movilidad:

•Wi-Fi Público: Riesgo de ataques Evil Twin y Sniffing. Nunca realizar transacciones sensibles en estas redes.

•VPNs Gratuitas: "Si el producto es gratis, el producto eres tú". Muchas VPNs gratuitas venden datos de tráfico o inyectan publicidad/malware.

•QR Codes: Peligro de Qrising (reemplazo de códigos QR legítimos por maliciosos).

## Herramientas de Análisis de Amenazas

| Herramienta            | Función                                                     |
| ---------------------- | ----------------------------------------------------------- |
| VirusTotal             | Análisis de archivos y URLs sospechosas.                    |
| Talos Intelligence     | Reputación de IPs y dominios (Cisco).                       |
| ExpandURL              | Revelar la URL final de un enlace acortado.                 |
| Phishing Quiz (Google) | Entrenamiento interactivo para detectar correos maliciosos. |


# 🛡️ Resumen: Curso de Ciberseguridad y Privacidad 303

Fuente: [Hixec - Necesitas APRENDER PRIVACIDAD](https://www.youtube.com/watch?v=mgo1CRBaooo)

## Deep Web vs. Dark Web

### Niveles de la Web

| Capa        | Descripción                                                                                 | Acceso                          |
| ----------- | ------------------------------------------------------------------------------------------- | ------------------------------- |
| Surface Web | Contenido indexado por buscadores (Google, Bing).                                           | Navegador estándar.             |
| Deep Web    | Contenido no indexado (bases de datos, correos, intranets). No es necesariamente malicioso. | Autenticación o enlace directo. |
| Dark Web    | Parte de la Deep Web que utiliza protocolos específicos y garantiza anonimato.              | Software especial (Tor, I2P).   |
| Darknet     | Red superpuesta que requiere software, configuración o autorización específica.             | Tor, Freenet, etc.              |

## El Ecosistema Tor (The Onion Router)

Herramienta vital para el anonimato y para acceder a servicios .onion.

- Funcionamiento: Cifrado por capas (como una cebolla) a través de nodos (Entrada, Intermedio, Salida).

- Limitación: El nodo de salida puede ver el tráfico si este no va cifrado (HTTP vs HTTPS).

- Diferencia entre Tor y una VPN:
	La **VPN** cifra tu conexión a través de un único servidor central para darte privacidad y velocidad, ideal para uso diario.
	**Tor** reenvía el tráfico por tres nodos voluntarios distintos para garantizar el anonimato total, siendo mucho más lento pero casi imposible de rastrear

## Anonimato Avanzado: Sistemas Operativos

Para un pentester, el sistema operativo desde el que opera puede comprometer su identidad.

- Tails (The Amnesic Incognito Live System): OS que se ejecuta desde un USB. Todo el tráfico sale por Tor y no deja rastro en el disco duro al apagar.

- Whonix: Sistema basado en dos máquinas virtuales (Gateway y Workstation). El tráfico de la Workstation pasa obligatoriamente por el Gateway (Tor), evitando fugas de IP incluso si la Workstation es comprometida.

## Infraestructura de Privacidad

### 1. Proxies vs. VPNs

- Proxy: Intermediario para aplicaciones específicas. No suele cifrar todo el sistema.

- VPN: Túnel cifrado para todo el tráfico del sistema. Ideal para ocultar la IP al ISP, pero requiere confianza en el proveedor de VPN (ej. ProtonVPN).

### 2. Tipos de proxies 

- Proxy cache: permite que el proxy almacene contenido que posiblemente se solicite a corto plazo, reduciendo el tiempo de respuesta

- Proxy web: permite enviar información a través de este sin necesidad de instalarlo. Precaución ya que nada es gratis y pueden vender tus datos

- Un proxy transparente actúa como un intermediario invisible que intercepta tu tráfico sin que tengas que configurar nada en tu dispositivo. Es útil para filtrar contenido en colegios o empresas, pero es arriesgado porque, al no notar su presencia, alguien podría estar monitoreando o modificando tu actividad sin tu consentimiento.

- Proxy reverso: está situado delante del servidor y actúa como un "escudo" o recepcionista. No es visible para los clientes. Su función es proteger al servidor de ataques, reparte el trabajo entre varias máquinas y acelera la carga de la página.

## Diferencia entre navegador y buscador
- Navegador: software que permite la interpretación de hipertexto y lo muestra de una forma más amigable al usuario. Ejemplo: Google Chrome
- Buscador: sistema cuyo objetivo es encontrar la información solicitada por el usuario. Ejemplo: Google
