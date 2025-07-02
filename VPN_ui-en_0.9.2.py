import json
import os
import subprocess
import threading
import tkinter as tk
from collections import deque
from tkinter import messagebox, filedialog

import customtkinter as ctk

CONFIG_FILE = 'config.json'
HISTORY_SIZE = 8
VPN_SUBNET = "10.255.0.1"  # À adapter selon la configuration de votre VPN


def load_config():
    default_directory = os.path.join(os.environ['USERPROFILE'], 'OpenVPN', 'config')
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as file:
            return json.load(file)
    return {"search_directory": default_directory, "history": []}


def disconnect_all():
    command = r'"C:\\Program Files\\OpenVPN\\bin\\openvpn-gui.exe" --command disconnect_all'
    threading.Thread(target=lambda: subprocess.run(command, shell=True)).start()


class OpenVPNUI:
    def __init__(self, master):
        self.status_button = None
        self.entry = None
        self.master = master
        self.master.title("OpenVPN Connection UI")
        self.master.geometry("300x280")
        self.config = load_config()
        self.history = deque(self.config.get("history", []), maxlen=HISTORY_SIZE)
        self.current_profile = None  # Pour stocker le profil actuellement connecté
        self.create_ui()
        self.master.after(100, self.entry.focus_set)
        self.update_status()

    def save_config(self):
        self.config["history"] = list(self.history)
        with open(CONFIG_FILE, 'w') as file:
            json.dump(self.config, file)

    def create_ui(self):
        button_kwargs = {
            "fg_color": "#4cafa5",
            "hover_color": "#3e8e87",
            "border_width": 0,
            "corner_radius": 5,
            "font": ("Helvetica", 12, "bold"),
            "text_color": "black"
        }

        input_frame = ctk.CTkFrame(self.master)
        input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.entry = ctk.CTkEntry(input_frame, width=40)
        self.entry.grid(row=0, column=0, padx=10, pady=10, columnspan=2, sticky="ew")
        self.entry.focus_set()
        self.entry.bind("<Return>", lambda event: self.search_file())

        button_frame = ctk.CTkFrame(self.master)
        button_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        ctk.CTkButton(button_frame, text="Search", command=self.search_file, **button_kwargs).grid(row=0, column=0, padx=10, pady=5)
        ctk.CTkButton(button_frame, text="VPN disconnect", command=disconnect_all, **button_kwargs).grid(row=1, column=0, padx=10, pady=5)
        ctk.CTkButton(button_frame, text="Setting", command=self.open_settings, **button_kwargs).grid(row=2, column=0, padx=10, pady=5)
        ctk.CTkButton(button_frame, text="History", command=self.show_history, **button_kwargs).grid(row=3, column=0, padx=10, pady=5)

        self.master.grid_columnconfigure(0, weight=1)
        input_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(0, weight=1)

        self.status_button = ctk.CTkButton(
            self.master,
            text="VPN : ...",
            command=self.show_profile_popup,
            fg_color="#4cafa5",
            hover_color="#3e8e87",
            border_width=0,
            corner_radius=5,
            font=("Helvetica", 11, "bold"),
            text_color="black"
        )
        self.status_button.grid(row=2, column=0, padx=10, pady=(5, 10), sticky="ew")

    def execute_command(self, file_name):
        command = fr'"C:\\Program Files\\OpenVPN\\bin\\openvpn-gui.exe" --connect {file_name}'
        threading.Thread(target=lambda: subprocess.run(command, shell=True)).start()
        self.add_to_history(file_name)

    def add_to_history(self, file_name):
        if file_name in self.history:
            self.history.remove(file_name)
        self.history.appendleft(file_name)
        self.save_config()

    def search_file(self):
        partial_name = self.entry.get().lower()
        found_files = []
        for root, dirs, files in os.walk(self.config["search_directory"]):
            for file in files:
                if partial_name in file.lower() and file.endswith('.ovpn'):
                    found_files.append(file)
        if found_files:
            if len(found_files) == 1:
                self.confirm_popup(found_files[0])
            else:
                self.select_file_popup(found_files)
        else:
            messagebox.showinfo("Search result", "Nothing found ", parent=self.master)

    def confirm_popup(self, file_name):
        # Ajout de la gestion de l'état connecté
        if self.current_profile:
            self.show_already_connected_popup(file_name)
        else:
            result = messagebox.askyesno("File found", f"File: {file_name}\nWould you like to connect?", parent=self.master)
            if result:
                self.execute_command(file_name)

    def show_already_connected_popup(self, file_name):
        popup = ctk.CTkToplevel(self.master)
        popup.title("VPN already connected")
        popup.geometry("350x120")
        popup.attributes("-topmost", True)
        popup.grab_set()
        popup.focus_force()

        label = ctk.CTkLabel(popup, text="VPN already connected.\nWhat do you want to do?", font=("Helvetica", 12))
        label.pack(pady=15)

        button_frame = ctk.CTkFrame(popup)
        button_frame.pack(pady=5)

        def disconnect_and_continue():
            popup.destroy()
            disconnect_all()
            # Attendre un peu que la déconnexion soit effective avant de reconnecter
            self.master.after(2000, lambda: self.execute_command(file_name))

        def abort():
            popup.destroy()

        ctk.CTkButton(button_frame, text="Disconnect and continue", command=disconnect_and_continue, fg_color="#4cafa5", hover_color="#3e8e87").pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="Abort", command=abort, fg_color="#d50000", hover_color="#b71c1c").pack(side="left", padx=10)

    def select_file_popup(self, files):
        selection_window = ctk.CTkToplevel(self.master)
        selection_window.title("File selection")
        selection_window.geometry("700x300")
        selection_window.attributes("-topmost", True)
        selection_window.focus_force()
        selection_window.grab_set()

        label = ctk.CTkLabel(selection_window, text="Several files found. Please select the one to use:")
        label.pack(pady=10)

        listbox = tk.Listbox(selection_window, selectmode=tk.SINGLE, width=100)
        for file in files:
            listbox.insert(tk.END, file)
        listbox.pack(pady=10)

        def on_select(event=None):
            selected_file = listbox.get(tk.ACTIVE)
            selection_window.destroy()
            self.confirm_popup(selected_file)

        listbox.bind('<Double-Button-1>', on_select)
        button_kwargs = {
            "fg_color": "#4cafa5",
            "hover_color": "#3e8e87",
            "border_width": 0,
            "corner_radius": 5,
            "font": ("Helvetica", 12, "bold"),
            "text_color": "black"
        }
        ctk.CTkButton(selection_window, text="Select", command=on_select, **button_kwargs).pack(pady=10)

    def open_settings(self):
        settings_window = ctk.CTkToplevel(self.master)
        settings_window.title("Settings")
        settings_window.geometry("500x120")
        settings_window.attributes("-topmost", True)
        settings_window.grab_set()
        settings_window.focus_force()
        current_dir_label = ctk.CTkLabel(settings_window, text=f"Current directory : {self.config['search_directory']}", font=("Helvetica", 12))
        current_dir_label.pack(pady=10)

        def set_directory():
            directory = filedialog.askdirectory(parent=settings_window)
            if directory:
                self.config["search_directory"] = directory
                self.save_config()
                current_dir_label.config(text=f"Current directory : {directory}")
                messagebox.showinfo("Settings", f"Search directory set to: {directory}", parent=settings_window)

        button_kwargs = {
            "fg_color": "#4cafa5",
            "hover_color": "#3e8e87",
            "border_width": 0,
            "corner_radius": 5,
            "font": ("Helvetica", 12, "bold"),
            "text_color": "black"
        }
        ctk.CTkButton(settings_window, text="Set search directory", command=set_directory, **button_kwargs).pack(pady=20)

    def show_history(self, on_select=None):
        history_window = ctk.CTkToplevel(self.master)
        history_window.title("Connection History")
        history_window.geometry("600x200")
        history_window.attributes("-topmost", True)
        history_window.grab_set()
        history_window.focus_force()
        label = ctk.CTkLabel(history_window, text="Recent VPN Connections:")
        label.pack(pady=10)
        listbox = tk.Listbox(history_window, selectmode=tk.SINGLE, width=90)
        for file in self.history:
            listbox.insert(tk.END, file)
        listbox.pack(pady=10)

        def on_select(event=None):
            selected_file = listbox.get(tk.ACTIVE)
            history_window.destroy()
            self.confirm_popup(selected_file)
            
        listbox.bind('<Double-Button-1>', on_select)
        button_kwargs = {
            "fg_color": "#4cafa5",
            "hover_color": "#3e8e87",
            "border_width": 0,
            "corner_radius": 5,
            "font": ("Helvetica", 12, "bold"),
            "text_color": "black"
        }
        ctk.CTkButton(history_window, text="Connect", command=on_select, **button_kwargs).pack(pady=10)

    def update_status(self):
        try:
            output = subprocess.check_output("route print", shell=True, encoding='utf-8', errors='ignore')
            if VPN_SUBNET in output:
                status_text = "VPN : CONNECTÉ"
                fg_color = "#00C853"  # vert
                if self.history:
                    self.current_profile = self.history[0]
                else:
                    self.current_profile = None
            else:
                status_text = "VPN : DÉCONNECTÉ"
                fg_color = "#D50000"  # rouge
                self.current_profile = None
        except Exception as e:
            status_text = f"VPN : Erreur ({e})"
            fg_color = "grey"
            self.current_profile = None
        self.status_button.configure(text=status_text, fg_color=fg_color)
        self.master.after(2000, self.update_status)

    def show_profile_popup(self):
        if self.current_profile:
            messagebox.showinfo("Profil VPN", f"Profil connecté : {self.current_profile}", parent=self.master)
        else:
            messagebox.showinfo("Profil VPN", "Aucun profil connecté", parent=self.master)

if __name__ == "__main__":
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    root = ctk.CTk()
    app = OpenVPNUI(root)
    root.mainloop()
