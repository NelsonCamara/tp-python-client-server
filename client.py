import threading # On utilise un thread pour recevoir les messages
import socket # On utilise socket pour se connecter au serveur
import time # On utilise time pour attendre un petit moment
import re # On utilise re pour trouver la commande USERNAME

class Client(): # Cette classe représente un client

    def __init__(self, username, server, port, display=print): # Cette partie prépare le client
        self.socket= socket.socket(socket.AF_INET, socket.SOCK_STREAM) # On crée la connexion
        self.socket.connect((server, port)) # On se connecte au serveur
        self.username= username # On garde le pseudo
        self.display= display # On garde la façon d'afficher les messages
        self.send("USERNAME {0}".format(username)) # On envoie le pseudo au serveur
        self.listening= True # On indique que le client écoute

    def listener(self): # Cette fonction reçoit les messages
        while self.listening: # On continue tant que le client écoute
            data= "" # On prépare une variable vide
            try: # On essaie de recevoir un message
                data= self.socket.recv(1024).decode('UTF-8') # On reçoit le message
            except socket.error: # Cette partie est utilisée s'il y a une erreur
                print("Unable to receive data") # On affiche le problème
            self.handle_msg(data) # On traite le message reçu
            time.sleep(0.1) # On attend un petit moment

    def listen(self): # Cette fonction démarre l'écoute
        self.listen_thread = threading.Thread(target=self.listener) # On crée le thread
        self.listen_thread.daemon = True # Le thread s'arrête avec le programme
        self.listen_thread.start() # On démarre le thread

    def send(self, message): # Cette fonction envoie un message
        try: # On essaie d'envoyer le message
            username_result = re.search('^USERNAME (.*)$', message) # On cherche la commande USERNAME
            if not username_result: # On vérifie si ce n'est pas la commande USERNAME
                message= "{0}: {1}".format(self.username, message) # On ajoute le pseudo
            self.socket.sendall(message.encode("UTF-8")) # On envoie le message
        except socket.error: # Cette partie est utilisée s'il y a une erreur
            print("unable to send message") # On affiche le problème

    def tidy_up(self): # Cette fonction ferme le client
        self.listening = False # On arrête l'écoute
        self.socket.close() # On ferme la connexion

    def handle_msg(self, data): # Cette fonction traite un message reçu
        if data=="QUIT": # On vérifie si le serveur demande de quitter
            self.tidy_up() # On ferme le client
        elif data=="": # On vérifie si la connexion est fermée
            self.tidy_up() # On ferme aussi le client
        else: # Sinon le message est normal
            self.display(data) # On affiche le message

if __name__ == "__main__": # Cette partie se lance avec client.py
    username= input("username: ") # On demande le pseudo
    server= input("server: ") # On demande l'adresse du serveur
    port= int(input("port: ")) # On demande le port
    client= Client(username, server, port) # On crée le client
    client.listen() # On démarre l'écoute
    message= "" # On prépare le message
    while message!="QUIT": # On continue jusqu'à QUIT
        message= input() # On demande un message
        client.send(message) # On envoie le message
