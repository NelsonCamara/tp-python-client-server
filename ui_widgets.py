import tkinter as tk

def create_round_rect(canvas, x1, y1, x2, y2, radius=16, **kwargs):
    points = [
        x1 + radius, y1, x2 - radius, y1, x2, y1,
        x2, y1 + radius, x2, y2 - radius, x2, y2,
        x2 - radius, y2, x1 + radius, y2, x1, y2,
        x1, y2 - radius, x1, y1 + radius, x1, y1
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)

class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command=None, width=110, height=38, radius=19, bg="#FFFFFF", fill="#000000", hover="#2B2D31"):
        super().__init__(parent, width=width, height=height, bg=bg, highlightthickness=0)
        self.command = command
        self.fill = fill
        self.hover = hover
        self.rect = create_round_rect(self, 2, 2, width-2, height-2, radius=radius, fill=fill)
        self.label = self.create_text(width // 2, height // 2, text=text, fill="#FFFFFF", font=("Segoe UI", 10, "bold"))
        
        self.bind("<Enter>", lambda _: self.itemconfig(self.rect, fill=self.hover))
        self.bind("<Leave>", lambda _: self.itemconfig(self.rect, fill=self.fill))
        self.bind("<Button-1>", lambda _: self.command() if self.command else None)

    def set_text(self, text):
        self.itemconfig(self.label, text=text)

class RoundedEntry(tk.Canvas):
    def __init__(self, parent, width=150, height=36, radius=14, default="", bg="#FFFFFF"):
        super().__init__(parent, width=width, height=height, bg=bg, highlightthickness=0)
        create_round_rect(self, 2, 2, width-2, height-2, radius=radius, fill="#EAECEF")
        self.entry = tk.Entry(self, bg="#EAECEF", fg="#000000", insertbackground="#000000", relief=tk.FLAT, font=("Segoe UI", 10, "bold"))
        self.entry.insert(0, default)
        self.entry.place(x=radius, y=8, width=width - (2 * radius), height=20)

    def get(self):
        return self.entry.get().strip()

    def set_state(self, state):
        self.entry.config(state=state)