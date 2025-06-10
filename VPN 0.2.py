import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import os

# Fonction pour exécuter la commande avec le fichier sélectionné
def execute_command(file_name):
    command = fr'"C:\\Program Files\\OpenVPN\\bin\\openvpn-gui.exe" --connect {file_name}'
    subprocess.run(command, shell=True)

# Fonction pour déconnecter tous les VPN
def disconnect_all():
    command = r'"C:\\Program Files\\OpenVPN\\bin\\openvpn-gui.exe" --command disconnect_all'
    subprocess.run(command, shell=True)

# Fonction pour rechercher le fichier .ovpn
def search_file():
    partial_name = entry.get().lower()  # Convertir la saisie utilisateur en minuscules
    for root, dirs, files in os.walk(r'C:\Users\WilfriedGoubot\OpenVPN\config'):
        for file in files:
            if partial_name in file.lower() and file.endswith('.ovpn'):  # Convertir le nom du fichier en minuscules
                confirm_popup(file)  # Passer uniquement le nom du fichier
                return
    messagebox.showinfo("Résultat de la recherche", "Aucun fichier trouvé.")

# Fonction pour afficher le pop-up de confirmation
def confirm_popup(file_name):
    result = messagebox.askyesno("Fichier trouvé", f"Fichier trouvé: {file_name}\nVoulez-vous vous connecter?")
    if result:
        execute_command(file_name)

# Créer la fenêtre principale
root = tk.Tk()
root.title("OpenVPN Connection UI")
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

# Créer un frame pour les boutons et le champ de saisie
input_frame = tk.Frame(root)
input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

# Ajouter un champ de saisie
entry = ttk.Entry(input_frame, width=30)
entry.grid(row=0, column=0, padx=10, pady=10, columnspan=2)

# Ajouter un bouton de recherche
search_button = ttk.Button(input_frame, text="Rechercher", command=search_file, style="RoundedButton.TButton")
search_button.grid(row=1, column=0, padx=10, pady=10, columnspan=2)

# Créer trois boutons
#button1 = ttk.Button(input_frame, text="Minimoi", command=lambda: execute_command("Minimoi.ovpn"), style="RoundedButton.TButton")
#button2 = ttk.Button(input_frame, text="Dr Denfer", command=lambda: execute_command("Dr_Denfer.ovpn"), style="RoundedButton.TButton")
button3 = ttk.Button(input_frame, text="Déconnecte VPN", command=disconnect_all, style="RoundedButton.TButton")

# Placer les boutons dans le frame avec le gestionnaire grid
#button1.grid(row=2, column=0, sticky="ew", padx=10, pady=10, columnspan=2)
#button2.grid(row=3, column=0, sticky="ew", padx=10, pady=10, columnspan=2)
button3.grid(row=4, column=0, sticky="ew", padx=10, pady=10, columnspan=2)

# Créer un frame pour le texte
text_frame = tk.Frame(root)
text_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

# Ajouter le texte dans le frame avec wraplength
text_label = tk.Label(text_frame, text="Veuillez suivre la procédure d'authentification adaptée.", font=("Helvetica", 18), justify="center", wraplength=200)
text_label.pack(expand=True)

# Lancer le clignotement du texte
def blink_text():
    current_color = text_label.cget("foreground")
    next_color = "red" if current_color == "black" else "black"
    text_label.config(foreground=next_color)
    root.after(500, blink_text)  # Change la couleur toutes les 500 ms

blink_text()

# Assurer que les colonnes s'étendent
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
input_frame.grid_columnconfigure(0, weight=1)

# Définir une largeur minimale pour les boutons
#button1.config(width=20)
#button2.config(width=20)
button3.config(width=20)

# Exécuter l'application
root.mainloop()