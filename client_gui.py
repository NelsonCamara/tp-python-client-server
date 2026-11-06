import tkinter as tk # On utilise Tkinter pour la fenêtre
import socket # On utilise socket pour chercher le serveur
from client import Client # On récupère le client du professeur

client= None # Aucun client n'est connecté au début
server_ip= None # Aucun serveur n'est trouvé au début

def ajouter(texte): # Cette fonction ajoute un message
    chat.insert(tk.END, texte + "\n") # On affiche le message dans le chat
    chat.see(tk.END) # On montre le dernier message

def afficher(texte): # Cette fonction reçoit un message
    fenetre.after(0, ajouter, texte) # On demande à la fenêtre de l'afficher

def rechercher(): # Cette fonction cherche le serveur
    global server_ip # On utilise l'adresse créée plus haut
    liste.delete(0, tk.END) # On vide la liste
    try: # On essaie de joindre le serveur
        test= socket.create_connection(("100.66.75.9", 59001), 2) # On crée une connexion de test
        test.sendall(b"DISCOVER") # On demande le nom du serveur
        nom= test.recv(1024).decode("UTF-8") # On reçoit la réponse
        test.close() # On ferme la connexion de test
        if nom.startswith("SERVER_NAME "): # On vérifie la réponse
            server_ip= "100.66.75.9" # On garde l'adresse du serveur
            liste.insert(tk.END, nom.replace("SERVER_NAME ", "")) # On affiche son nom
        else: print("Réponse du serveur inconnue") # On affiche une erreur
    except socket.error: print("Serveur introuvable") # On affiche une erreur

def connecter(): # Cette fonction connecte le client
    global client # On utilise le client créé plus haut
    if pseudo.get() == "": print("Écris un pseudo") # On vérifie le pseudo
    elif not liste.curselection(): print("Choisis un serveur") # On vérifie le choix
    else: # Sinon on essaie la connexion
        try: # On essaie de créer le client
            client= Client(pseudo.get(), server_ip, 59001, afficher) # On crée le client
            client.listen() # On commence à recevoir les messages
            print("Connecté au serveur") # On confirme la connexion
        except socket.error: print("Impossible de se connecter") # On affiche une erreur

def envoyer(): # Cette fonction envoie un message
    if client == None: print("Connecte-toi au serveur") # On vérifie la connexion
    elif message.get() == "": print("Écris un message") # On vérifie le message
    else: # Sinon on envoie le message
        client.send(message.get()) # On envoie le texte
        message.delete(0, tk.END) # On vide le champ

fenetre= tk.Tk() # On crée la fenêtre
tk.Label(fenetre, text="Pseudo").pack() # On affiche Pseudo
pseudo= tk.Entry(fenetre) # On crée le champ Pseudo
pseudo.pack() # On place le champ Pseudo
tk.Button(fenetre, text="Rechercher", command=rechercher).pack() # On crée le bouton Rechercher
liste= tk.Listbox(fenetre, height=3) # On crée la liste des serveurs
liste.pack() # On place la liste
tk.Button(fenetre, text="Connexion", command=connecter).pack() # On crée le bouton Connexion
chat= tk.Text(fenetre, height=10, width=40) # On crée la zone du chat
chat.pack() # On place la zone du chat
tk.Label(fenetre, text="Message").pack() # On affiche Message
message= tk.Entry(fenetre, width=40) # On crée le champ Message
message.pack() # On place le champ Message
tk.Button(fenetre, text="Envoyer", command=envoyer).pack() # On crée le bouton Envoyer
message.bind("<Return>", lambda event: envoyer()) # La touche Entrée envoie le message
fenetre.mainloop() # On garde la fenêtre ouverte
