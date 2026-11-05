import tkinter as tk # On utilise Tkinter pour faire la fenêtre
import socket # On utilise socket pour chercher les serveurs
import re # On utilise re pour trouver le nom du serveur
from client import Client # On récupère le client du professeur
client= None # Le client sera créé après la connexion
servers= [] # Cette liste garde les serveurs trouvés

def find_servers(port): # Cette fonction cherche les serveurs du groupe
    addresses= ["100.66.75.9", "100.66.223.231", "100.66.57.123"] # On met les trois adresses NetBird
    found= [] # On prépare une liste vide
    for address in addresses: # On essaie chaque adresse
        try: # On essaie de se connecter
            test= socket.socket(socket.AF_INET, socket.SOCK_STREAM) # On crée une connexion
            test.settimeout(1) # On attend une seconde maximum
            test.connect((address, port)) # On se connecte à cette adresse
            test.sendall("DISCOVER".encode("UTF-8")) # On demande le nom du serveur
            answer= test.recv(1024).decode("UTF-8") # On reçoit la réponse
            test.close() # On ferme la connexion de recherche
            name_result= re.search('^SERVER_NAME (.*)$', answer) # On cherche le nom dans la réponse
            if name_result: # On vérifie si un nom est trouvé
                found.append((name_result.group(1), address)) # On garde le nom et l'adresse
        except socket.error: # Cette partie est utilisée si le serveur ne répond pas
            pass # On passe à l'adresse suivante
    return found # On renvoie les serveurs trouvés
def show(text): # Cette fonction affiche un message
    chat.insert(tk.END, text + "\n") # On ajoute le message dans le chat
    chat.see(tk.END) # On montre le dernier message

def search(): # Cette fonction cherche les serveurs
    global servers # On utilise la liste créée plus haut
    servers= find_servers(59001) # On lance la recherche sur le port 59001
    server_list.delete(0, tk.END) # On vide la liste affichée
    for server in servers: # On parcourt les serveurs trouvés
        server_list.insert(tk.END, server[0]) # On affiche le nom du serveur

def connect(event=None): # Cette fonction connecte le client
    global client # On utilise le client créé plus haut
    choice= server_list.curselection() # On récupère le serveur choisi
    if choice: # On vérifie qu'un serveur est choisi
        address= servers[choice[0]][1] # On récupère son adresse
        client= Client(username.get(), address, 59001, lambda text: root.after(0, show, text)) # On crée le client
        client.listen() # On commence à recevoir les messages
        show("Connecté au serveur") # On affiche que la connexion fonctionne
        message.focus_set() # On place le curseur dans le champ Message

def send(): # Cette fonction envoie un message
    text= message.get() # On récupère le message écrit
    if client and text != "": # On vérifie le client et le message
        client.send(text) # On envoie le message
        message.delete(0, tk.END) # On vide le champ Message

root= tk.Tk() # On crée la fenêtre
tk.Label(root, text="Pseudo").pack() # On affiche le texte Pseudo
username= tk.Entry(root) # On crée le champ du pseudo
username.pack() # On place le champ dans la fenêtre
tk.Button(root, text="Rechercher", command=search).pack() # On crée le bouton Rechercher
server_list= tk.Listbox(root) # On crée la liste des serveurs
server_list.pack() # On place la liste dans la fenêtre
server_list.bind("<Double-Button-1>", connect) # Un double clic lance la connexion
chat= tk.Text(root, height=10) # On crée la zone des messages
chat.pack() # On place la zone des messages
tk.Label(root, text="Message").pack() # On affiche le texte Message
message= tk.Entry(root) # On crée le champ du message
message.pack() # On place le champ dans la fenêtre
message.bind("<Return>", lambda event: send()) # La touche Entrée envoie le message
tk.Button(root, text="Envoyer", command=send).pack() # On crée le bouton Envoyer
root.after(500, search) # On lance la recherche après une petite attente
root.mainloop() # On laisse la fenêtre ouverte
