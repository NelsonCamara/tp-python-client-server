import tkinter as tk
from tkinter import messagebox
from ui_widgets import RoundedButton, RoundedEntry, create_round_rect
from network_client import NetworkClient

class ChatClientGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat Client")
        self.root.geometry("730x640")
        self.root.configure(bg="#F4F5F7")

        self.client = NetworkClient(
            on_message=lambda msg: self.root.after(0, self.append_text, msg),
            on_disconnect=lambda: self.root.after(0, self._handle_disconnect)
        )
        self._build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def _build_ui(self):
        # 1. Barre de connexion
        top = tk.Canvas(self.root, bg="#F4F5F7", highlightthickness=0, height=90)
        top.pack(fill=tk.X, padx=18, pady=(14, 8))
        create_round_rect(top, 2, 2, 690, 86, radius=18, fill="#FFFFFF", outline="#E0E2E6")

        self.in_ip = RoundedEntry(top, width=145, default="100.66.75.9")
        self.in_ip.place(x=20, y=34)
        self.in_port = RoundedEntry(top, width=75, default="59001")
        self.in_port.place(x=175, y=34)
        self.in_user = RoundedEntry(top, width=130, default="Nelson")
        self.in_user.place(x=260, y=34)

        for text, x in [("IP SERVEUR", 24), ("PORT", 179), ("PSEUDO", 264)]:
            tk.Label(top, text=text, bg="#FFFFFF", font=("Segoe UI", 9, "bold")).place(x=x, y=12)

        self.btn_conn = RoundedButton(top, "Connexion", self.toggle_connection, width=120)
        self.btn_conn.place(x=410, y=33)
        RoundedButton(top, "Quitter", self.on_close, width=110, fill="#E53935", hover="#C62828").place(x=545, y=33)

        # 2. Zone de messages
        self.chat_card = tk.Canvas(self.root, bg="#F4F5F7", highlightthickness=0)
        self.chat_card.pack(fill=tk.BOTH, expand=True, padx=18, pady=6)
        self.bg_id = create_round_rect(self.chat_card, 2, 2, 690, 390, radius=20, fill="#FFFFFF", outline="#E0E2E6")
        self.chat_card.bind("<Configure>", lambda e: (self.chat_card.delete(self.bg_id),
            setattr(self, 'bg_id', create_round_rect(self.chat_card, 2, 2, e.width-4, e.height-4, radius=20, fill="#FFFFFF", outline="#E0E2E6")),
            self.chat_card.tag_lower(self.bg_id)))

        self.txt = tk.Text(self.chat_card, bg="#FFFFFF", fg="#000000", relief=tk.FLAT, font=("Segoe UI", 10, "bold"), padx=16, pady=16)
        self.txt.place(x=12, y=12, relwidth=0.96, relheight=0.93)

        # 3. Zone de saisie
        bottom = tk.Canvas(self.root, bg="#F4F5F7", highlightthickness=0, height=60)
        bottom.pack(fill=tk.X, padx=18, pady=(8, 16))
        create_round_rect(bottom, 2, 2, 555, 48, radius=24, fill="#FFFFFF", outline="#E0E2E6")

        self.in_msg = tk.Entry(bottom, bg="#FFFFFF", relief=tk.FLAT, font=("Segoe UI", 10, "bold"))
        self.in_msg.place(x=20, y=14, width=515, height=24)
        self.in_msg.bind("<Return>", lambda _: self.send())
        RoundedButton(bottom, "Envoyer", self.send, width=110, height=48, radius=24, bg="#F4F5F7").place(x=575, y=2)

    def append_text(self, text):
        self.txt.config(state=tk.NORMAL)
        self.txt.insert(tk.END, text + "\n")
        self.txt.see(tk.END)
        self.txt.config(state=tk.DISABLED)

    def toggle_connection(self):
        if not self.client.is_connected:
            try:
                self.client.connect(self.in_ip.get(), int(self.in_port.get()), self.in_user.get())
                self.btn_conn.set_text("Déconnexion")
                self.append_text(f"--- Connecté à {self.in_ip.get()} ---")
            except Exception as e:
                messagebox.showerror("Erreur", f"Connexion impossible :\n{e}")
        else:
            self.client.disconnect()
            self._handle_disconnect()

    def _handle_disconnect(self):
        self.btn_conn.set_text("Connexion")
        self.append_text("--- Déconnecté ---")

    def send(self):
        msg = self.in_msg.get().strip()
        if msg and self.client.is_connected:
            self.client.send(f"{self.in_user.get()}: {msg}")
            self.in_msg.delete(0, tk.END)

    def on_close(self):
        self.client.disconnect()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatClientGUI(root)
    root.mainloop()