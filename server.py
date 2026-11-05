import socket # Permet de créer des connexions réseau TCP/IP
import sys #utilisé pour sortir du programme
import time # Permet de faire une pause dans le programme
from clientthread import ClientListener # Gère les communications avec chaque client

class Server(): # Classe principale du serveur

    def __init__(self, port): # Initialise le serveur avec un port
        self.listener= socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Crée une socket IPv4 en TCP
        self.listener.bind(('', port)) # Écoute sur toutes les interfaces réseau du PC
        self.listener.listen(1) # Met le serveur en écoute avec une file d'attente de 1 connexion
        print("Listening on port", port) # Affiche le port utilisé
        self.clients_sockets= [] # Liste des clients connectés

    def run(self): # Fonction principale du serveur
        while True: # Boucle infinie pour accepter les connexions
            print("listening new customers") # Attend un nouveau client
            try: # Essaie d'accepter une connexion
                (client_socket, client_adress) = self.listener.accept() # Récupère la socket et l'adresse du client
            except socket.error: # Si une erreur réseau survient
                sys.exit("Cannot connect clients") # Arrête le programme
            self.clients_sockets.append(client_socket) # Ajoute le client à la liste
            print("Start the thread for client:", client_adress) # Affiche l'adresse du client
            client_thread= ClientListener(self, client_socket, client_adress) # Crée un thread pour gérer le client
            client_thread.start() # Démarre le thread du client
            time.sleep(0.1) # Attend 0,1 seconde

    def remove_socket(self, socket): # Supprime un client déconnecté
        self.clients_sockets.remove(socket) # Retire sa socket de la liste

    def echo(self, data): # Envoie un message à tous les clients
        print("echoing:", data) # Affiche le message dans le terminal
        for sock in self.clients_sockets: # Parcourt les clients connectés
            try: # Essaie d'envoyer le message
                sock.sendall(data.encode("UTF-8")) # Convertit en UTF-8 et transmet via TCP
            except socket.error: # Si l'envoi échoue
                print("Cannot send the message") # Affiche une erreur


if __name__ == "__main__": # Exécute le code si le fichier est lancé directement
    server= Server(59001) # Crée le serveur sur le port TCP 59001
    server.run() # Démarre le serveur
