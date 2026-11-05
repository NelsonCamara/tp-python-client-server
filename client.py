"""
client.py
Client de chat en ligne de commande (CLI).
Gère la saisie interactive dans le terminal et l'écoute asynchrone des messages via un thread démon.
"""

import threading
import socket
import time
import re

class Client:
    """Gère la connexion TCP, l'écoute concurrente et l'envoi de messages console."""

    def __init__(self, username, server, port):
        # Création du socket TCP IPv4
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Connexion au serveur distant
        self.socket.connect((server, port))
        self.username = username
        # Envoi de la commande d'identification protocolaire
        self.send("USERNAME {0}".format(username))
        self.listening = True

    def listener(self):
        """Boucle de réception exécutée dans un thread séparé."""
        while self.listening:
            data = ""
            try:
                data = self.socket.recv(1024).decode('UTF-8')
            except socket.error:
                print("Unable to receive data")
            self.handle_msg(data)
            time.sleep(0.1)

    def listen(self):
        """Lance le thread d'écoute en mode daemon pour ne pas bloquer l'arrêt du script."""
        self.listen_thread = threading.Thread(target=self.listener)
        self.listen_thread.daemon = True
        self.listen_thread.start()

    def send(self, message):
        """Formate et transmet un message sur le réseau."""
        try:
            # Ne préfixe pas le pseudo si c'est la commande système USERNAME
            username_result = re.search('^USERNAME (.*)$', message)
            if not username_result:
                message = "{0}: {1}".format(self.username, message)
            self.socket.sendall(message.encode("UTF-8"))
        except socket.error:
            print("unable to send message")

    def tidy_up(self):
        """Ferme proprement le socket et interrompt la boucle d'écoute."""
        self.listening = False
        self.socket.close()

    def handle_msg(self, data):
        """Analyse les messages entrants reçus du serveur."""
        if data == "QUIT" or data == "":
            self.tidy_up()
        else:
            print(data)


if __name__ == "__main__":
    # Saisie interactive des paramètres de connexion
    username = input("username: ")
    server = input("server: ")
    port = int(input("port: "))
    
    # Connexion et démarrage de l'écoute en tâche de fond
    client = Client(username, server, port)
    client.listen()

    # Boucle d'envoi jusqu'à saisie de QUIT
    message = ""
    while message != "QUIT":
        message = input()
        client.send(message)