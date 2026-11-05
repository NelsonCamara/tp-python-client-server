"""
client_gui.py
Point d'entrée de l'application graphique.
Assemble les composants Tkinter (thème moderne blanc, typographie Segoe UI en gras)
et fait le pont avec la couche réseau (NetworkClient).
"""

import tkinter as tk
from tkinter import messagebox
from ui_widgets import RoundedButton, RoundedEntry, create_round_rect
from network_client import NetworkClient

class ChatClientGUI:
    """Contrôleur principal de la vue graphique Tkinter."""

    def __init__(self, root):
        self.root = root
        self.root.title("Chat Client — TP Réseau")
        self.root.geometry("730x640")
        self.root.configure(bg="#F4F5F7")

        # Initialisation du client réseau avec synchronisation thread-safe (root.after)
        self.client = NetworkClient(
            on_message=lambda msg: self.root.after(0, self.append_text, msg),
            on_disconnect=lambda: self.root.after(0, self._handle_disconnect)
        )
        self._build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def _build_ui(self):
        """Construit l'ensemble des éléments de l'interface utilisateur."""
        # 1. Panneau supérieur : Paramètres de connexion
        top = tk.Canvas(self.root, bg="#F4F5F7", highlightthickness=0, height=90)
        top.pack(fill=tk.X, padx=18, pady=(14, 8))
        create_round_rect(top, 2, 2, 690, 86, radius=18, fill="#FFFFFF", outline="#E0E2E6")

        # Champs arrondis préconfigurés
        self.in_ip = RoundedEntry(top, width=145, default="100.66.75.9")
        self.in_ip.place(x=20, y=34)
        self.in_port = RoundedEntry(top, width=75, default="59001")
        self.in_port.place(x=175, y=34)
        self.in_user = RoundedEntry(top, width=130, default="Nelson")
        self.in_user.place(x=260, y=34)

        for text, x in [("IP SERVEUR", 24), ("PORT", 179), ("PSEUDO", 264)]:
            tk.Label(top, text=text, bg="#FFFFFF", fg="#000000", font=("Segoe UI", 9, "bold")).place(x=x, y=12)

        # Bouton Connexion / Déconnexion
        self.btn_conn = RoundedButton(top, "Connexion", self.toggle_connection, width=120)
        self.btn_conn.place(x=410, y=33)

        # Bouton Quitter (fermeture de l'application)
        RoundedButton(top, "Quitter", self.on_close, width=110, fill="#E53935", hover="#C62828").place(x=545, y=33)

        # 2. Zone centrale : Historique du chat
        self.chat_card = tk.Canvas(self.root, bg="#F4F5F7", highlightthickness=0)
        self.chat_card.pack(fill=tk.BOTH, expand=True, padx=18, pady=6)
        
        self.bg_id = create_round_rect(self.chat_card, 2, 2, 690, 390, radius=20, fill="#FFFFFF", outline="#E0E2E6")
        self.chat_card.bind("<Configure>", self._on_resize_chat)

        self.txt = tk.Text(
            self.chat_card, bg="#FFFFFF", fg="#000000", relief=tk.FLAT,
            font=("Segoe UI", 10, "bold"), padx=16, pady=16, state=tk.DISABLED
        )
        self.txt.place(x=12, y=12, relwidth=0.96, relheight=0.93)

        # 3. Panneau inférieur : Capsule de saisie et bouton Envoi
        bottom = tk.Canvas(self.root, bg="#F4F5F7", highlightthickness=0, height=60)
        bottom.pack(fill=tk.X, padx=18, pady=(8, 18))
        create_round_rect(bottom, 2, 2, 555, 48, radius=24, fill="#FFFFFF", outline="#E0E2E6")

        self.in_msg = tk.Entry(bottom, bg="#FFFFFF", fg="#000000", relief=tk.FLAT, font=("Segoe UI", 10, "bold"))
        self.in_msg.place(x=20, y=14, width=515, height=24)
        self.in_msg.bind("<Return>", lambda _: self.send())
        self.in_msg.config(state=tk.DISABLED)

        self.btn_send = RoundedButton(bottom, "Envoyer", self.send, width=110, height=48, radius=24, bg="#F4F5F7")
        self.btn_send.place(x=575, y=2)

    def _on_resize_chat(self, event):
        """Adapte les dimensions du rectangle arrondi lorsque la fenêtre s'étire."""
        self.chat_card.delete(self.bg_id)
        self.bg_id = create_round_rect(
            self.chat_card, 2, 2, event.width - 4, event.height - 4, radius=20, fill="#FFFFFF", outline="#E0E2E6"
        )
        self.chat_card.tag_lower(self.bg_id)

    def append_text(self, text):
        """Ajoute du texte à la zone d'historique en respectant l'état DISABLED."""
        self.txt.config(state=tk.NORMAL)
        self.txt.insert(tk.END, text + "\n")
        self.txt.see(tk.END)
        self.txt.config(state=tk.DISABLED)

    def toggle_connection(self):
        """Bascule entre l'état connecté et déconnecté."""
        if not self.client.is_connected:
            try:
                ip = self.in_ip.get()
                port = int(self.in_port.get())
                user = self.in_user.get()
                self.client.connect(ip, port, user)
                
                # Mise à jour de l'état des entrées
                self.btn_conn.set_text("Déconnexion")
                self.in_ip.set_state(tk.DISABLED)
                self.in_port.set_state(tk.DISABLED)
                self.in_user.set_state(tk.DISABLED)
                self.in_msg.config(state=tk.NORMAL)
                self.in_msg.focus()
                
                self.append_text(f"--- Connecté au serveur ({ip}:{port}) ---")
            except Exception as e:
                messagebox.showerror("Erreur de connexion", f"Impossible d'établir la liaison :\n{e}")
        else:
            self.client.disconnect()
            self._handle_disconnect()

    def _handle_disconnect(self):
        """Réinitialise l'IHM lors d'une déconnexion."""
        self.btn_conn.set_text("Connexion")
        self.in_ip.set_state(tk.NORMAL)
        self.in_port.set_state(tk.NORMAL)
        self.in_user.set_state(tk.NORMAL)
        self.in_msg.delete(0, tk.END)
        self.in_msg.config(state=tk.DISABLED)
        self.append_text("--- Déconnecté du serveur ---")

    def send(self):
        """Récupère le message saisi et le transmet via le socket TCP."""
        msg = self.in_msg.get().strip()
        if msg and self.client.is_connected:
            self.client.send(f"{self.in_user.get()}: {msg}")
            self.in_msg.delete(0, tk.END)

    def on_close(self):
        """Interruption propre avant fermeture de l'UI."""
        self.client.disconnect()
        self.root.destroy()


if __name__ == "__main__":
    app_root = tk.Tk()
    app = ChatClientGUI(app_root)
    app_root.mainloop()