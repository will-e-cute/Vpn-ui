import tkinter as tk
from tkinter import ttk
import subprocess

# Fonction pour exécuter la commande
def execute_command1():
    command = r'"C:\\Program Files\\OpenVPN\\bin\\openvpn-gui.exe" --connect Minimoi.ovpn'
    subprocess.run(command, shell=True)

def execute_command2():
    command = r'"C:\\Program Files\\OpenVPN\\bin\\openvpn-gui.exe" --connect Dr_Denfer.ovpn'
    subprocess.run(command, shell=True)

def execute_command3():
    command = r'"C:\\Program Files\\OpenVPN\\bin\\openvpn-gui.exe" --command disconnect_all'
    subprocess.run(command, shell=True)

# Fonction pour faire clignoter le texte
def blink_text():
    current_color = text_label.cget("foreground")
    next_color = "red" if current_color == "black" else "black"
    text_label.config(foreground=next_color)
    root.after(500, blink_text)  # Change la couleur toutes les 500 ms

# Créer la fenêtre principale
root = tk.Tk()
root.title("OpenVPN Command Executor")
root.geometry("500x200")  # Définir la taille de la fenêtre

# Créer un style pour les boutons arrondis
style = ttk.Style()
style.configure("RoundedButton.TButton",
                relief="flat",
                borderwidth=0,
                background="#4cafa5",
                foreground="black",
                font=("Helvetica", 12, "bold"),
                padding=7)
style.map("RoundedButton.TButton",
          background=[("active", "#4cafa5")],
          relief=[("pressed", "sunken")])

# Créer un frame pour le texte
text_frame = tk.Frame(root)
text_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

# Ajouter le texte dans le frame avec wraplength
text_label = tk.Label(text_frame, text="Veuillez suivre la procédure d'authentification adaptée.", font=("Helvetica", 18), justify="center", wraplength=200)
text_label.pack(expand=True)

# Lancer le clignotement du texte
blink_text()

# Créer un frame pour les boutons
button_frame = tk.Frame(root)
button_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

# Créer trois boutons
button1 = ttk.Button(button_frame, text="Minimoi", command=execute_command1, style="RoundedButton.TButton")
button2 = ttk.Button(button_frame, text="Dr Denfer", command=execute_command2, style="RoundedButton.TButton")
button3 = ttk.Button(button_frame, text="Déconnecte VPN", command=execute_command3, style="RoundedButton.TButton")

# Placer les boutons dans le frame avec le gestionnaire grid
button1.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
button2.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
button3.grid(row=2, column=0, sticky="ew", padx=10, pady=10)

# Assurer que les colonnes s'étendent
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
button_frame.grid_columnconfigure(0, weight=1)

# Définir une largeur minimale pour les boutons
button1.config(width=20)
button2.config(width=20)
button3.config(width=20)

# Exécuter l'application
root.mainloop()
