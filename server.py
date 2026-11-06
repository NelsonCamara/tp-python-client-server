import socket # Permet de créer la connexion du serveur
import sys # Permet d'arrêter le programme s'il y a une erreur
import time # Permet d'attendre un petit moment
from clientthread import ClientListener # On récupère la classe qui gère un client


class Server(): # Cette classe représente le serveur

    def __init__(self, port): # Cette méthode prépare le serveur
        self.name= "Server Messagerie CFA INSTA - Saïd, Nelson, Salah" # Nom affiché pendant la recherche
        self.listener= socket.socket(socket.AF_INET, socket.SOCK_STREAM) # On crée la connexion du serveur
        self.listener.bind(('', port)) # On associe la socket au port
        self.listener.listen(1) # On met le serveur en attente
        print("Listening on port", port) # On affiche le port utilisé
        self.clients_sockets= [] # Liste des clients connectés

    def run(self): # Cette méthode contient la boucle principale
        while True: # Le serveur continue toujours d'attendre
            print("listening new customers") # On indique que le serveur attend un client
            try: # On essaie d'accepter une connexion
                (client_socket, client_adress) = self.listener.accept() # On récupère la socket et l'adresse du client
            except socket.error: # Cette partie est utilisée en cas d'erreur réseau
                sys.exit("Cannot connect clients") # On arrête le programme
            self.clients_sockets.append(client_socket) # On ajoute la socket à la liste
            print("Start the thread for client:", client_adress) # On affiche l'adresse du client
            client_thread= ClientListener(self, client_socket, client_adress) # On crée le thread du client
            client_thread.start() # On démarre le thread
            time.sleep(0.1) # On attend un petit moment

    def remove_socket(self, socket): # Cette méthode retire un client
        self.clients_sockets.remove(socket) # On supprime sa socket de la liste

    def echo(self, data): # Cette méthode diffuse un message
        print("echoing:", data) # On affiche le message dans le terminal
        for sock in self.clients_sockets: # On parcourt tous les clients
            try: # On essaie d'envoyer le message
                sock.sendall(data.encode("UTF-8")) # On transforme le texte en octets et on l'envoie
            except socket.error: # Cette partie est utilisée si l'envoi échoue
                print("Cannot send the message") # On affiche une erreur


if __name__ == "__main__": # Ce bloc se lance si on exécute server.py
    server= Server(59001) # On crée le serveur sur le port 59001
    server.run() # On démarre le serveur