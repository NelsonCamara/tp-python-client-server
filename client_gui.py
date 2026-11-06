from guizero import App, Text, TextBox, PushButton # Pour la fenêtre
from client import Client # Notre client Python

def afficher(texte): # Affiche les messages
    app.after(0, discussion.append, [texte + "\n"]) # Ajoute le message dans la fenêtre

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
Text(app, "Messages") # Titre de la zone des messages
discussion = TextBox(app, multiline=True, width=40, height=10) # Zone des messages reçus
message = TextBox(app)
PushButton(app, text="Envoyer", command=envoyer)
app.display() # Ouvre la fenêtre
