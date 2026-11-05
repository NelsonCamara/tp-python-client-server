"""
network_client.py
Couche réseau isolée : gère le socket TCP client, la communication en arrière-plan
via un thread dédié et les rappels asynchrones (callbacks) vers l'interface.
"""

import socket
import threading

class NetworkClient:
    """Client TCP gérant la connexion, l'écoute concurrente et l'émission des trames."""

    def __init__(self, on_message, on_disconnect):
        """
        :param on_message: Callback appelée lors de la réception d'un message entrant
        :param on_disconnect: Callback appelée lors de la fermeture inattendue du socket
        """
        self.sock = None
        self.is_connected = False
        self.on_message = on_message
        self.on_disconnect = on_disconnect

    def connect(self, host, port, username):
        """
        Établit la connexion TCP au serveur hôte et lance le thread de réception.
        """
        # Création d'un socket flux IPv4/TCP
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(4.0)  # Timeout court pour éviter le gel en cas d'hôte injoignable
        self.sock.connect((host, port))
        self.sock.settimeout(None)  # Rétablissement du mode bloquant standard
        self.is_connected = True
        
        # Identification initiale selon le protocole convenu
        self.sock.sendall(f"USERNAME {username}".encode("UTF-8"))
        
        # Thread d'écoute daemon : se termine automatiquement si l'UI est fermée
        threading.Thread(target=self._listen, daemon=True).start()

    def _listen(self):
        """Boucle de réception exécutée en tâche de fond pour ne pas figer l'UI."""
        while self.is_connected:
            try:
                data = self.sock.recv(1024).decode("UTF-8")
                # Si data est vide, le serveur a coupé la communication TCP
                if not data or data == "QUIT":
                    break
                self.on_message(data.strip())
            except Exception:
                break
                
        # Déconnexion propre si la boucle est rompue
        if self.is_connected:
            self.disconnect()
            self.on_disconnect()

    def send(self, message):
        """Transmet une chaîne de caractères encodée en UTF-8 sur le socket TCP."""
        if self.is_connected and self.sock:
            try:
                self.sock.sendall(message.encode("UTF-8"))
            except socket.error:
                pass

    def disconnect(self):
        """Ferme la socket TCP et informe le serveur du départ."""
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