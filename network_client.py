"""
network_client.py
Couche réseau isolée : gestion socket TCP, découverte UDP et requêtes protocolaires.
"""

import socket
import threading
import time

DISCOVERY_UDP_PORT = 59002

class NetworkClient:
    """Client TCP avec support de scan réseau UDP."""

    def __init__(self, on_message, on_disconnect, on_server_name=None):
        self.sock = None
        self.is_connected = False
        self.on_message = on_message
        self.on_disconnect = on_disconnect
        self.on_server_name = on_server_name

    @staticmethod
    def discover_servers(timeout=1.5, broadcast_ip="255.255.255.255"):
        """
        Scanne le réseau en broadcast UDP et collecte les serveurs actifs.
        Retourne une liste de dictionnaires : [{'ip': ..., 'port': ..., 'name': ...}]
        """
        found_servers = []
        udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        udp_sock.settimeout(timeout)

        targets = [broadcast_ip]
        if broadcast_ip == "255.255.255.255":
            targets.append("100.66.75.255")

        for target in set(targets):
            try:
                udp_sock.sendto(b"CHAT_DISCOVERY_PING", (target, DISCOVERY_UDP_PORT))
            except Exception:
                pass

        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                data, addr = udp_sock.recvfrom(1024)
                parts = data.decode("UTF-8").split(" ", 2)
                if len(parts) >= 3 and parts[0] == "CHAT_DISCOVERY_ACK":
                    server_info = {
                        "ip": addr[0],
                        "port": int(parts[1]),
                        "name": parts[2].strip()
                    }
                    if server_info not in found_servers:
                        found_servers.append(server_info)
            except socket.timeout:
                break
            except Exception:
                break

        udp_sock.close()
        return found_servers

    def connect(self, host, port, username):
        """Établit la connexion TCP et lance l'écoute."""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(4.0)
        self.sock.connect((host, port))
        self.sock.settimeout(None)
        self.is_connected = True
        
        self.sock.sendall(f"USERNAME {username}".encode("UTF-8"))
        threading.Thread(target=self._listen, daemon=True).start()

    def request_server_name(self):
        """Envoie la commande spécifique pour demander le nom du serveur."""
        if self.is_connected and self.sock:
            try:
                self.sock.sendall("GET_SERVER_NAME".encode("UTF-8"))
            except Exception:
                pass

    def _listen(self):
        """Boucle d'écoute arrière-plan."""
        while self.is_connected:
            try:
                data = self.sock.recv(1024).decode("UTF-8")
                if not data or data == "QUIT":
                    break
                
                # Réception de la réponse avec le nom du serveur
                if data.startswith("SERVER_NAME ") and self.on_server_name:
                    s_name = data.replace("SERVER_NAME ", "").strip()
                    self.on_server_name(s_name)
                    continue

                self.on_message(data.strip())
            except Exception:
                break
                
        if self.is_connected:
            self.disconnect()
            self.on_disconnect()

    def send(self, message):
        """Envoi TCP standard."""
        if self.is_connected and self.sock:
            try:
                self.sock.sendall(message.encode("UTF-8"))
            except socket.error:
                pass

    def disconnect(self):
        """Ferme la session proprement."""
        self.is_connected = False
        if self.sock:
            try:
                self.sock.sendall("QUIT".encode("UTF-8"))
            except Exception:
                pass
            try:
                self.sock.close()
            except Exception:
                pass
            self.sock = None