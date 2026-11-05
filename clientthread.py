from socket import socket, error # Permet d'utiliser la connexion et les erreurs
import threading # Permet de gérer plusieurs clients en même temps
import re # Permet de trouver la commande USERNAME
import time # Permet d'attendre un petit moment


class ClientListener(threading.Thread): # Cette classe gère un client connecté

    def __init__(self, server, socket, address): # Cette méthode prépare le thread du client
        super(ClientListener, self).__init__() # On initialise la classe Thread
        self.server= server # On garde le serveur principal
        self.socket= socket # On garde la socket du client
        self.address= address # On garde l'adresse du client
        self.listening= True # Cette variable garde l'écoute active
        self.username= "No username" # Le pseudo sera reçu après la connexion


    def run(self): # Cette méthode se lance avec le thread
        while self.listening: # On continue tant que le client est connecté
            data= "" # On prépare une variable vide
            try: # On essaie de recevoir un message
                data = self.socket.recv(1024).decode('UTF-8') # On reçoit puis on transforme les données en texte
            except error: # Cette partie est utilisée si la réception échoue
                print("Unable to receive data") # On affiche une erreur
            self.handle_msg(data) # On traite le message reçu
            time.sleep(0.1) # On attend un petit moment
        print("Ending client thread for", self.address) # On affiche la fin du thread


    def quit(self): # Cette méthode déconnecte un client
        self.listening = False # On arrête sa boucle d'écoute
        self.socket.close() # On ferme sa socket
        self.server.remove_socket(self.socket) # On retire sa socket de la liste
        self.server.echo("{0} has quit\n".format(self.username)) # On annonce son départ

    def handle_msg(self, data): # Cette méthode traite les commandes et les messages
        print(self.address, "sent :", data) # On affiche ce que le client a envoyé

        if data == "DISCOVER": # On vérifie si le client cherche le serveur
            answer= "SERVER_NAME " + self.server.name # On prépare la réponse avec le nom
            self.socket.sendall(answer.encode("UTF-8")) # On envoie la réponse
            self.listening= False # On arrête cette connexion de recherche
            self.socket.close() # On ferme sa socket
            self.server.remove_socket(self.socket) # On la retire de la liste
            return # On quitte la méthode

        username_result = re.search('^USERNAME (.*)$', data) # On cherche la commande USERNAME
        if username_result: # On vérifie si le client a envoyé son pseudo
            self.username = username_result.group(1) # On garde seulement le pseudo
            self.server.echo("{0} has joined.\n".format(self.username)) # On annonce l'arrivée du client
        elif data == "QUIT": # On vérifie si le client veut quitter
            self.quit() # On déconnecte le client
        elif data == "": # Un texte vide indique que la connexion est fermée
            self.quit() # On déconnecte aussi le client
        else: # Sinon il s'agit d'un message normal
            self.server.echo(data) # On envoie le message à tous les clients
