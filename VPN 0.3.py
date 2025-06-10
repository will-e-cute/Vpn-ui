import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import os
import json

# Chemin du fichier de configuration
config_file = 'config.json'

# Charger la configuration
def load_config():
    default_directory = os.path.join(os.environ['USERPROFILE'], 'OpenVPN', 'config')
    if os.path.exists(config_file):
        with open(config_file, 'r') as file:
            return json.load(file)
    return {"search_directory": default_directory}

# Sauvegarder la configuration
def save_config(config):
    with open(config_file, 'w') as file:
        json.dump(config, file)

# Charger la configuration
config = load_config()

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
    for root, dirs, files in os.walk(config["search_directory"]):
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

# Fonction pour ouvrir la fenêtre de configuration
def open_settings():
    def set_directory():
        directory = filedialog.askdirectory()
        if directory:
            config["search_directory"] = directory
            save_config(config)
            current_dir_label.config(text=f"Répertoire actuel : {directory}")
            messagebox.showinfo("Paramètres", f"Répertoire de recherche défini sur: {directory}")

    settings_window = tk.Toplevel(root)
    settings_window.title("Paramètres")
    settings_window.geometry("500x120")

    current_dir_label = tk.Label(settings_window, text=f"Répertoire actuel : {config['search_directory']}", font=("Helvetica", 12))
    current_dir_label.pack(pady=10)

    set_dir_button = ttk.Button(settings_window, text="Définir le répertoire de recherche", command=set_directory)
    set_dir_button.pack(pady=20)

# Créer la fenêtre principale
root = tk.Tk()
root.title("OpenVPN Connection UI")
root.geometry("320x250")  # Définir la taille de la fenêtre

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

# Créer un frame pour les boutons
button_frame = tk.Frame(root)
button_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

# Ajouter un bouton de recherche
search_button = ttk.Button(button_frame, text="Rechercher", command=search_file, style="RoundedButton.TButton")
search_button.grid(row=0, column=0, padx=10, pady=5)

# Ajouter un bouton pour déconnecter les VPN
button3 = ttk.Button(button_frame, text="Déconnecte VPN", command=disconnect_all, style="RoundedButton.TButton")
button3.grid(row=1, column=0, padx=10, pady=5)

# Ajouter un bouton de paramètres en bas à droite
settings_button = ttk.Button(button_frame, text="Paramètres", command=open_settings, style="RoundedButton.TButton")
settings_button.grid(row=2, column=0, padx=10, pady=5)

# Fixer la largeur des boutons à 250 pixels
search_button.config(width=30)
button3.config(width=30)
settings_button.config(width=30)

# Assurer que les colonnes s'étendent
root.grid_columnconfigure(0, weight=1)
input_frame.grid_columnconfigure(0, weight=1)
button_frame.grid_columnconfigure(0, weight=1)

# Exécuter l'application
root.mainloop()