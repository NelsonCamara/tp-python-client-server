import threading
import socket
import time
import re


# Un thread est un processus qui tourne en parrallèle dans un programme ce qui permet de faire du multitâche
class Client():

    def __init__(self, username, server, port):
        # Création du socket TCP sur de l'IPv4
        self.socket= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Demande de connexion au serveur
        self.socket.connect((server, port))
        # Stcoke le nom et l'envoie au serveur
        self.username= username
        self.send("USERNAME {0}".format(username))
        self.listening= True


    def listener(self):
        # Tant que le client est sur écoute
        while self.listening:
            data= ""
            try:
                # Recois et décode le message reçu du serveur
                data= self.socket.recv(1024).decode('UTF-8')
            except socket.error:
                #On imprime un message d'erreur si on arrive pas à recevoir de la donnée
                print("Unable to receive data")
            self.handle_msg(data)
            time.sleep(0.1)

# fonction d'écoute du client en parrallèle (thread)
    def listen(self):
        # Crée le Thread permettant au client d'écouter le serveur
        self.listen_thread = threading.Thread(target=self.listener)
        # Active le daemon pour que le thread s'arrête dès que le programme principal se termine.
        self.listen_thread.daemon = True
        # lance le thread
        self.listen_thread.start()

# Fonction de l'envoi du message
    def send(self, message):
        try:
            username_result = re.search('^USERNAME (.*)$', message)
            if not username_result:
                message= "{0}: {1}".format(self.username, message)
            self.socket.sendall(message.encode("UTF-8"))

        except socket.error:
            print("unable to send message")
# Fonction coupant la connexion
    def tidy_up(self):
        self.listening = False
        self.socket.close()

# Si le client reçois QUIT comme message, alors il appelle la fonction tidy_up
    def handle_msg(self, data):
        if data=="QUIT":
            self.tidy_up()
        elif data=="":
            self.tidy_up()
        else:
            print(data)


if __name__ == "__main__":
    # demande le nom, le serveur et le port dans lequel se connecte
    username= input("username: ")
    server= input("server: ")
    port= int(input("port: "))
    client= Client(username, server, port)
    client.listen()
# Lis et envoie le message, si le client écrit QUIT alors la communication s'arrête
    message= ""
    while message!="QUIT":
        message= input()
        client.send(message)
