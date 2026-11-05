
import tkinter as tk # Pour créer notre fenêtre
import socket # Pour rechercher le serveur
from client import Client # On utilise le client du professeur

client = None # Aucun client connecté au début
ip = "100.66.75.9" # Adresse NetBird du serveur de Salah
port = 59001 # Port utilisé pour le chat

def afficher(texte): # Affiche un message dans le chat
    chat.insert(tk.END, texte + "\n") # Ajoute le message
    chat.see(tk.END) # Descend vers le dernier message

def rechercher(): # Recherche notre serveur NetBird
    liste.delete(0, tk.END) # Vide la liste
    try:
        test = socket.create_connection((ip, port), 2) # Vérifie si le serveur répond
        test.settimeout(2) # Attend maximum 2 secondes
        test.sendall(b"DISCOVER\n") # Demande le nom du serveur
        nom = test.recv(1024).decode("UTF-8") # Récupère la réponse
        test.close() # Ferme la connexion de test

        if nom.startswith("SERVER_NAME "): # Vérifie la réponse du serveur
            liste.insert(tk.END, nom.replace("SERVER_NAME ", "").strip())
        else:
            afficher("Réponse du serveur inconnue")
    except (socket.error, OSError):
        afficher("Serveur introuvable") # Affiche une erreur

def connecter(): # Se connecte au serveur
    global client
    if pseudo.get() == "":
        afficher("Entre ton pseudo")
    elif liste.size() == 0:
        afficher("Recherche un serveur")
    else:
        try:
            client = Client(pseudo.get(), ip, port, lambda texte: fenetre.after(0, afficher, texte))
            client.listen() # Commence à recevoir les messages
            afficher("Connexion lancée")
        except (socket.error, OSError) as erreur:
            afficher("Erreur de connexion : " + str(erreur))

def envoyer(): # Envoie un message
    if client == None:
        afficher("Connecte-toi d'abord")
    elif message.get() == "":
        afficher("Écris un message")
    else:
        try:
            client.send(message.get()) # Envoie le texte au serveur
            message.delete(0, tk.END) # Vide le champ
        except (socket.error, OSError):
            afficher("Impossible d'envoyer le message")

fenetre = tk.Tk() # Crée la fenêtre
fenetre.title("Chat Python - NetBird") # Titre de notre application

tk.Label(fenetre, text="Pseudo").pack()
pseudo = tk.Entry(fenetre) # Champ pour écrire son pseudo
pseudo.pack()

tk.Button(fenetre, text="Rechercher le serveur", command=rechercher).pack()

liste = tk.Listbox(fenetre, height=3) # Affiche les serveurs trouvés
liste.pack()

tk.Button(fenetre, text="Se connecter", command=connecter).pack()

chat = tk.Text(fenetre, height=12, width=45) # Zone de discussion
chat.pack()

tk.Label(fenetre, text="Message").pack()
message = tk.Entry(fenetre, width=40) # Champ pour écrire un message
message.pack()

tk.Button(fenetre, text="Envoyer", command=envoyer).pack()
message.bind("<Return>", lambda event: envoyer()) # Entrée pour envoyer

fenetre.mainloop() # Garde la fenêtre ouverte