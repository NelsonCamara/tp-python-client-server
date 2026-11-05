"""
client_gui.py
Interface graphique utilisateur (IHM) basée sur les composants natifs Tkinter.
Prend en charge :
- L'architecture MVC/SoC avec NetworkClient
- La recherche automatique des serveurs en UDP (Option 1)
- La récupération et l'affichage dynamique du nom du serveur (Option 2)
"""

import tkinter as tk
from tkinter import messagebox, ttk, Toplevel, Listbox
import threading
from network_client import NetworkClient

class ChatClientGUI:
    """Contrôleur de l'interface graphique native."""

    def __init__(self, root):
        self.root = root
        self.root.title("Chat Client — TP Réseau")
        self.root.geometry("680x540")
        self.root.minsize(500, 400)

        # Couche réseau découplée
        self.client = NetworkClient(
            on_message=lambda msg: self.root.after(0, self.append_text, msg),
            on_disconnect=lambda: self.root.after(0, self._handle_disconnect),
            on_server_name=lambda name: self.root.after(0, self._update_server_name, name)
        )

        self._build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def _build_ui(self):
        """Construit les éléments d'interface avec les widgets natifs de Tkinter."""
        # 1. Barre de configuration supérieure (LabelFrame standard)
        top_frame = tk.LabelFrame(self.root, text=" Paramètres de connexion ", padx=10, pady=8)
        top_frame.pack(fill=tk.X, padx=10, pady=5)

        # Ligne d'entrées
        tk.Label(top_frame, text="IP Serveur :").grid(row=0, column=0, sticky=tk.W, padx=4, pady=2)
        self.entry_ip = tk.Entry(top_frame, width=16)
        self.entry_ip.insert(0, "100.66.75.9")
        self.entry_ip.grid(row=0, column=1, padx=4, pady=2)

        tk.Label(top_frame, text="Port :").grid(row=0, column=2, sticky=tk.W, padx=4, pady=2)
        self.entry_port = tk.Entry(top_frame, width=8)
        self.entry_port.insert(0, "59001")
        self.entry_port.grid(row=0, column=3, padx=4, pady=2)

        tk.Label(top_frame, text="Pseudo :").grid(row=0, column=4, sticky=tk.W, padx=4, pady=2)
        self.entry_user = tk.Entry(top_frame, width=14)
        self.entry_user.insert(0, "Nelson")
        self.entry_user.grid(row=0, column=5, padx=4, pady=2)

        # Boutons d'action
        self.btn_scan = tk.Button(top_frame, text="Détecter", command=self.scan_servers_async)
        self.btn_scan.grid(row=0, column=6, padx=6, pady=2)

        self.btn_conn = tk.Button(top_frame, text="Connexion", command=self.toggle_connection, width=11)
        self.btn_conn.grid(row=0, column=7, padx=4, pady=2)

        self.btn_quit = tk.Button(top_frame, text="Quitter", command=self.on_close)
        self.btn_quit.grid(row=0, column=8, padx=4, pady=2)

        # 2. Zone d'historique centrale
        center_frame = tk.Frame(self.root)
        center_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.scroll = tk.Scrollbar(center_frame)
        self.scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.txt = tk.Text(center_frame, wrap=tk.WORD, yscrollcommand=self.scroll.set, state=tk.DISABLED)
        self.txt.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scroll.config(command=self.txt.yview)

        # 3. Zone d'envoi inférieure
        bottom_frame = tk.Frame(self.root)
        bottom_frame.pack(fill=tk.X, padx=10, pady=(5, 10))

        self.entry_msg = tk.Entry(bottom_frame, state=tk.DISABLED)
        self.entry_msg.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
        self.entry_msg.bind("<Return>", lambda _: self.send())

        self.btn_send = tk.Button(bottom_frame, text="Envoyer", command=self.send, width=10, state=tk.DISABLED)
        self.btn_send.pack(side=tk.RIGHT)

    def append_text(self, text):
        """Insère un message dans la console d'affichage."""
        self.txt.config(state=tk.NORMAL)
        self.txt.insert(tk.END, text + "\n")
        self.txt.see(tk.END)
        self.txt.config(state=tk.DISABLED)

    # --- Option 1 : Auto-détection UDP ---
    def scan_servers_async(self):
        self.append_text("--- Recherche de serveurs actifs sur le réseau... ---")
        threading.Thread(target=self._scan_thread, daemon=True).start()

    def _scan_thread(self):
        servers = NetworkClient.discover_servers(timeout=1.5)
        self.root.after(0, self._show_discovered_servers, servers)

    def _show_discovered_servers(self, servers):
        if not servers:
            self.append_text("--- Aucun serveur détecté en broadcast ---")
            messagebox.showinfo("Détection", "Aucun serveur actif trouvé.")
            return

        win = Toplevel(self.root)
        win.title("Serveurs Détectés")
        win.geometry("340x220")
        win.transient(self.root)
        win.grab_set()

        tk.Label(win, text="Double-cliquez pour choisir un serveur :").pack(padx=8, pady=6)
        
        listbox = Listbox(win)
        listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=4)

        for s in servers:
            listbox.insert(tk.END, f"{s['name']} — {s['ip']}:{s['port']}")

        def select():
            sel = listbox.curselection()
            if sel:
                chosen = servers[sel[0]]
                self.entry_ip.delete(0, tk.END)
                self.entry_ip.insert(0, chosen["ip"])
                self.entry_port.delete(0, tk.END)
                self.entry_port.insert(0, str(chosen["port"]))
                self.append_text(f"--- Sélectionné : {chosen['name']} ({chosen['ip']}:{chosen['port']}) ---")
                win.destroy()

        listbox.bind("<Double-Button-1>", lambda _: select())
        tk.Button(win, text="Sélectionner", command=select).pack(pady=6)

    # --- Gestion de connexion ---
    def toggle_connection(self):
        if not self.client.is_connected:
            try:
                ip = self.entry_ip.get().strip()
                port = int(self.entry_port.get().strip())
                user = self.entry_user.get().strip()
                if not user:
                    messagebox.showwarning("Attention", "Le pseudo ne peut pas être vide.")
                    return

                self.client.connect(ip, port, user)

                # Verrouillage des paramètres et activation du chat
                self.btn_conn.config(text="Déconnexion")
                self.entry_ip.config(state=tk.DISABLED)
                self.entry_port.config(state=tk.DISABLED)
                self.entry_user.config(state=tk.DISABLED)
                self.entry_msg.config(state=tk.NORMAL)
                self.btn_send.config(state=tk.NORMAL)
                self.entry_msg.focus()

                self.append_text(f"--- Connecté au serveur ({ip}:{port}) ---")
                # Option 2 : Demande immédiate du nom du serveur
                self.client.request_server_name()

            except Exception as e:
                messagebox.showerror("Erreur de connexion", f"Connexion impossible :\n{e}")
        else:
            self.client.disconnect()
            self._handle_disconnect()

    def _update_server_name(self, name):
        """Mise à jour suite au retour de l'Option 2."""
        self.root.title(f"Chat Client — Connecté à [{name}]")
        self.append_text(f"--- Nom du serveur : {name} ---")

    def _handle_disconnect(self):
        self.root.title("Chat Client — TP Réseau")
        self.btn_conn.config(text="Connexion")
        self.entry_ip.config(state=tk.NORMAL)
        self.entry_port.config(state=tk.NORMAL)
        self.entry_user.config(state=tk.NORMAL)
        self.entry_msg.delete(0, tk.END)
        self.entry_msg.config(state=tk.DISABLED)
        self.btn_send.config(state=tk.DISABLED)
        self.append_text("--- Déconnecté du serveur ---")

    def send(self):
        msg = self.entry_msg.get().strip()
        if msg and self.client.is_connected:
            self.client.send(f"{self.entry_user.get()}: {msg}")
            self.entry_msg.delete(0, tk.END)

    def on_close(self):
        self.client.disconnect()
        self.root.destroy()


if __name__ == "__main__":
    app_root = tk.Tk()
    app = ChatClientGUI(app_root)
    app_root.mainloop()