import socket
import threading

class NetworkClient:
    def __init__(self, on_message, on_disconnect):
        self.sock = None
        self.is_connected = False
        self.on_message = on_message
        self.on_disconnect = on_disconnect

    def connect(self, host, port, username):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(4.0)
        self.sock.connect((host, port))
        self.sock.settimeout(None)
        self.is_connected = True
        
        self.sock.sendall(f"USERNAME {username}".encode("UTF-8"))
        threading.Thread(target=self._listen, daemon=True).start()

    def _listen(self):
        while self.is_connected:
            try:
                data = self.sock.recv(1024).decode("UTF-8")
                if not data or data == "QUIT":
                    break
                self.on_message(data.strip())
            except Exception:
                break
        if self.is_connected:
            self.disconnect()
            self.on_disconnect()

    def send(self, message):
        if self.is_connected and self.sock:
            self.sock.sendall(message.encode("UTF-8"))

    def disconnect(self):
        self.is_connected = False
        if self.sock:
            try:
                self.sock.sendall("QUIT".encode("UTF-8"))
                self.sock.close()
            except Exception:
                pass
            self.sock = None