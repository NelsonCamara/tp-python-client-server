from guizero import App, Text, TextBox, PushButton # Pour la fenêtre
from client import Client # Notre client Python

def afficher(texte): # Affiche les messages
    print(texte) # Dans le terminal

def connecter(): # Connexion au serveur
    global client
    client = Client(pseudo.value, "100.66.75.9", 59001, afficher)
    client.listen() # Reçoit les messages

def envoyer(): # Envoie un message
    if message.value:
        client.send(message.value) # Envoie le texte
    else: print("Écris un message")

app = App("Chat Python") # Crée la fenêtre
Text(app, "Pseudo")
pseudo = TextBox(app)
PushButton(app, text="Connexion", command=connecter)
message = TextBox(app)
PushButton(app, text="Envoyer", command=envoyer)
app.display() # Ouvre la fenêtre
