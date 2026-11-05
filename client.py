"""
client.py
Client console interactif (CLI) conforme au sujet de base.
Prend en charge :
- L'auto-détection UDP des serveurs sur le réseau (Option 1)
- L'interrogation et l'affichage du nom du serveur via GET_SERVER_NAME (Option 2)
"""

import threading
import socket
import time
import re

DISCOVERY_UDP_PORT = 59002


def discover_servers_cli(timeout=1.5):
    """
    Envoie un ping broadcast UDP pour détecter les serveurs actifs.
    Retourne la liste des serveurs sous la forme [{'ip': ..., 'port': ..., 'name': ...}].
    """
    found = []
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    udp_sock.settimeout(timeout)

    targets = ["255.255.255.255", "100.66.75.255"]
    for target in targets:
        try:
            udp_sock.sendto(b"CHAT_DISCOVERY_PING", (target, DISCOVERY_UDP_PORT))
        except Exception:
            pass

    start = time.time()
    while time.time() - start < timeout:
        try:
            data, addr = udp_sock.recvfrom(1024)
            parts = data.decode("UTF-8").split(" ", 2)
            if len(parts) >= 3 and parts[0] == "CHAT_DISCOVERY_ACK":
                item = {"ip": addr[0], "port": int(parts[1]), "name": parts[2].strip()}
                if item not in found:
                    found.append(item)
        except socket.timeout:
            break
        except Exception:
            break

    udp_sock.close()
    return found


class Client:
    """Gère la connexion TCP, l'écoute concurrente et l'envoi de messages console."""

    def __init__(self, username, server, port):
        self.username = username
        self.server_ip = server
        self.port = port
        self.server_name = "Inconnu"
        self.listening = True

        # Création et raccordement du socket TCP
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((server, port))

        # Identification protocolaire
        self.send("USERNAME {0}".format(username))

    def listener(self):
        """Boucle de réception exécutée dans un thread d'arrière-plan."""
        while self.listening:
            data = ""
            try:
                data = self.socket.recv(1024).decode('UTF-8')
            except socket.error:
                if self.listening:
                    print("\n[Réseau] Connexion interrompue par le serveur.")
                break

            self.handle_msg(data)
            time.sleep(0.05)

    def listen(self):
        """Lance le thread d'écoute en tâche de fond (daemon)."""
        self.listen_thread = threading.Thread(target=self.listener, daemon=True)
        self.listen_thread.start()

    def send(self, message):
        """Formate et transmet un message sur le socket TCP."""
        try:
            # Ne pas préfixer les commandes internes du protocole
            is_cmd = message.startswith("USERNAME ") or message == "GET_SERVER_NAME" or message == "QUIT"
            if not is_cmd:
                message = "{0}: {1}".format(self.username, message)
            self.socket.sendall(message.encode("UTF-8"))
        except socket.error:
            print("\n[Erreur] Impossible d'expédier le message.")

    def tidy_up(self):
        """Ferme les flux et libère les ressources réseau."""
        if not self.listening:
            return
        self.listening = False
        try:
            self.socket.close()
        except Exception:
            pass

    def handle_msg(self, data):
        """Traite les réceptions ou commandes renvoyées par le serveur."""
        if not data or data == "QUIT":
            self.tidy_up()
            return

        # Option 2 : Interception du nom de serveur renvoyé
        if data.startswith("SERVER_NAME "):
            self.server_name = data.replace("SERVER_NAME ", "").strip()
            print(f"\n[Info Serveur] Vous êtes connecté à : {self.server_name}")
            return

        # Affichage standard des messages diffusés
        print(data)


if __name__ == "__main__":
    print("=" * 50)
    print("      TP CLIENT-SERVEUR CHAT — CONSOLE (CLI)      ")
    print("=" * 50)

    username = input("Votre pseudo : ").strip()
    while not username:
        username = input("Le pseudo ne peut être vide : ").strip()

    # Option 1 : Détection automatique des serveurs
    print("\nRecherche automatique de serveurs sur le réseau...")
    servers = discover_servers_cli(timeout=1.5)

    server_ip = ""
    port = 59001

    if servers:
        print(f"{len(servers)} serveur(s) détecté(s) :")
        for i, s in enumerate(servers, start=1):
            print(f"  [{i}] {s['name']} — {s['ip']}:{s['port']}")
        print("  [0] Saisir manuellement une adresse")

        choix = input("\nVotre choix [1] : ").strip()
        if not choix:
            choix = "1"

        if choix.isdigit() and 1 <= int(choix) <= len(servers):
            selection = servers[int(choix) - 1]
            server_ip = selection["ip"]
            port = selection["port"]
        else:
            server_ip = input("Adresse IP du serveur : ").strip()
            port = int(input("Port [59001] : ").strip() or 59001)
    else:
        print("Aucun serveur détecté automatiquement (ou UDP filtré).")
        server_ip = input("Adresse IP du serveur (ex: 100.66.75.9) : ").strip()
        port = int(input("Port [59001] : ").strip() or 59001)

    print(f"\nConnexion à {server_ip}:{port} en cours...")
    try:
        client = Client(username, server_ip, port)
        client.listen()
        
        # Option 2 : Demande immédiate du nom de la machine hôte
        client.send("GET_SERVER_NAME")
    except Exception as e:
        print(f"Échec de la connexion : {e}")
        exit(1)

    print("\n--- Tapez vos messages (ou 'QUIT' pour quitter, '/name' pour le nom du serveur) ---")
    message = ""
    while message != "QUIT" and client.listening:
        try:
            message = input()
            if not message:
                continue
            if message == "/name":
                client.send("GET_SERVER_NAME")
            elif message == "QUIT":
                client.send("QUIT")
                client.tidy_up()
                break
            else:
                client.send(message)
        except (KeyboardInterrupt, EOFError):
            client.send("QUIT")
            client.tidy_up()
            break

    print("Déconnexion effectuée.")