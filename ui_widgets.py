"""
ui_widgets.py
Module fournissant des composants graphiques Tkinter personnalisés avec coins arrondis.
Utilise l'interpolation de courbes vectorielles (Canvas create_polygon avec smooth=True).
"""

import tkinter as tk

def create_round_rect(canvas, x1, y1, x2, y2, radius=16, **kwargs):
    """
    Trace un rectangle aux coins arrondis sur un Canvas Tkinter.
    
    :param canvas: Instance du Canvas hôte
    :param x1, y1: Coordonnées du coin supérieur gauche
    :param x2, y2: Coordonnées du coin inférieur droit
    :param radius: Rayon de courbure des angles en pixels
    :param kwargs: Options graphiques transmises à create_polygon (fill, outline, etc.)
    :return: Identifiant de l'objet graphique créé sur le canvas
    """
    # Liste ordonnée de points définissant les sommets et points de contrôle de Bézier
    points = [
        x1 + radius, y1,
        x2 - radius, y1,
        x2, y1,
        x2, y1 + radius,
        x2, y2 - radius,
        x2, y2,
        x2 - radius, y2,
        x1 + radius, y2,
        x1, y2,
        x1, y2 - radius,
        x1, y1 + radius,
        x1, y1
    ]
    # smooth=True applique une spline pour adoucir les angles
    return canvas.create_polygon(points, smooth=True, **kwargs)


class RoundedButton(tk.Canvas):
    """Bouton interactif avec coins arrondis, typographie Segoe UI et gestion du survol."""

    def __init__(self, parent, text, command=None, width=110, height=38, radius=19, bg="#FFFFFF", fill="#000000", hover="#2B2D31"):
        super().__init__(parent, width=width, height=height, bg=bg, highlightthickness=0)
        self.command = command
        self.fill = fill
        self.hover = hover
        
        # Tracé du fond arrondi du bouton
        self.rect = create_round_rect(self, 2, 2, width - 2, height - 2, radius=radius, fill=fill)
        # Libellé centré
        self.label = self.create_text(width // 2, height // 2, text=text, fill="#FFFFFF", font=("Segoe UI", 10, "bold"))
        
        # Événements souris pour l'interactivité (hover et clic)
        self.bind("<Enter>", lambda _: self.itemconfig(self.rect, fill=self.hover))
        self.bind("<Leave>", lambda _: self.itemconfig(self.rect, fill=self.fill))
        self.bind("<Button-1>", lambda _: self.command() if self.command else None)

    def set_text(self, text):
        """Met à jour le texte affiché sur le bouton."""
        self.itemconfig(self.label, text=text)


class RoundedEntry(tk.Canvas):
    """Champ de texte encapsulé dans une capsule aux angles arrondis."""

    def __init__(self, parent, width=150, height=36, radius=14, default="", bg="#FFFFFF"):
        super().__init__(parent, width=width, height=height, bg=bg, highlightthickness=0)
        # Fond arrondi gris clair
        create_round_rect(self, 2, 2, width - 2, height - 2, radius=radius, fill="#EAECEF")
        
        # Champ Entry natif sans bordure dure (relief FLAT) positionné à l'intérieur
        self.entry = tk.Entry(
            self, bg="#EAECEF", fg="#000000", insertbackground="#000000",
            relief=tk.FLAT, font=("Segoe UI", 10, "bold")
        )
        self.entry.insert(0, default)
        self.entry.place(x=radius, y=8, width=width - (2 * radius), height=20)

    def get(self):
        """Retourne la valeur saisie nettoyée des espaces superflus."""
        return self.entry.get().strip()

    def set_state(self, state):
        """Active ou désactive l'édition du champ (tk.NORMAL / tk.DISABLED)."""
        self.entry.config(state=state)