
from socket import socket # Importe la classe socket pour les communications réseau
import threading # Permet de gérer plusieurs clients simultanément avec des threads
import re # Permet de rechercher des commandes dans les messages
import time # Permet d'ajouter une pause dans le programme

class ClientListener(threading.Thread): # Classe qui gère chaque client dans un thread indépendant

    def __init__(self, server, socket, address): # Initialise le thread avec le serveur, la socket et l'adresse du client
        super(ClientListener, self).__init__() # Initialise la classe parente Thread
        self.server= server # Référence au serveur principal
        self.socket= socket # Socket TCP utilisée pour communiquer avec le client
        self.address= address # Adresse IP et port du client connecté
        self.listening= True # Indique que le thread doit continuer à écouter
        self.username= "No username" # Nom par défaut du client avant son identification

    def run(self): # Fonction exécutée au démarrage du thread
        while self.listening: # Continue tant que le client est connecté
            data= "" # Initialise la variable contenant le message reçu
            try: # Tente de recevoir les données du client
                data = self.socket.recv(1024).decode('UTF-8') # Reçoit jusqu'à 1024 octets et décode en UTF-8
            except socket.error: # Gère les erreurs de réception réseau
                print("Unable to receive data") # Affiche un message d'erreur
            self.handle_msg(data) # Analyse et traite le message reçu
            time.sleep(0.1) # Attend 0,1 seconde avant la prochaine réception
        print("Ending client thread for", self.address) # Indique la fin du thread client
 
    def quit(self): # Gère la déconnexion du client
        self.listening = False # Arrête la boucle d'écoute
        self.socket.close() # Ferme la connexion TCP du client
        self.server.remove_socket(self.socket) # Supprime le client de la liste du serveur
        self.server.echo("{0} has quit\n".format(self.username)) # Informe les autres clients de son départ

    def handle_msg(self, data): # Analyse les messages et commandes envoyés par le client
        print(self.address, "sent :", data) # Affiche l'adresse du client et son message
        username_result = re.search('^USERNAME (.*)$', data) # Vérifie si le message contient la commande USERNAME
        if username_result: # Si le client envoie son nom d'utilisateur
            self.username = username_result.group(1) # Enregistre le nom d'utilisateur
            self.server.echo("{0} has joined.\n".format(self.username)) # Informe les clients de son arrivée
        elif data == "QUIT": # Vérifie si le client demande à quitter
            self.quit() # Déconnecte proprement le client
        elif data == "": # Vérifie si la connexion est fermée ou si aucune donnée n'a été reçue
            self.quit() # Déconnecte le client
        else: # Si le message ne correspond à aucune commande
            self.server.echo(data) # Transmet le message à tous les clients connectés
