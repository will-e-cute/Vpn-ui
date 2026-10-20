import os
import subprocess
import threading
import shutil
import psutil

if os.name == 'nt':
    CREATE_NO_WINDOW = 0x08000000
else:
    CREATE_NO_WINDOW = 0

class VPNManager:
    KNOWN_GUI_PATHS = [
        r"C:\Program Files\OpenVPN\bin\openvpn-gui.exe",
        r"C:\Program Files (x86)\OpenVPN\bin\openvpn-gui.exe",
    ]

    @classmethod
    def get_gui_path(cls):
        """Trouve le chemin vers openvpn-gui.exe dynamiquement."""
        # 1. Vérifier si un processus openvpn-gui.exe est déjà en cours d'exécution
        for proc in psutil.process_iter(['name', 'exe']):
            try:
                if proc.info['name'] and proc.info['name'].lower() == 'openvpn-gui.exe':
                    exe = proc.info.get('exe')
                    if exe and os.path.exists(exe):
                        return exe
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        # 2. Vérifier les chemins d'installation standards
        for path in cls.KNOWN_GUI_PATHS:
            if os.path.exists(path):
                return path

        # 3. Vérifier dans le PATH
        which_path = shutil.which("openvpn-gui.exe")
        if which_path:
            return which_path

        return None

    @classmethod
    def connect(cls, file_name, on_success=None, on_error=None):
        """Lance la connexion OpenVPN pour le profil spécifié en arrière-plan."""
        gui_path = cls.get_gui_path()
        if not gui_path:
            if on_error:
                on_error("OpenVPN GUI est introuvable. Veuillez vérifier son installation.")
            return

        def run():
            try:
                subprocess.run(
                    [gui_path, "--connect", file_name],
                    check=True,
                    creationflags=CREATE_NO_WINDOW
                )
                if on_success:
                    on_success(file_name)
            except subprocess.CalledProcessError as e:
                if on_error:
                    on_error(f"Erreur d'exécution OpenVPN : code {e.returncode}")
            except Exception as e:
                if on_error:
                    on_error(f"Échec de la connexion : {str(e)}")

        threading.Thread(target=run, daemon=True).start()

    @classmethod
    def disconnect_all(cls, on_success=None, on_error=None):
        """Déconnecte toutes les sessions VPN en cours."""
        gui_path = cls.get_gui_path()
        if not gui_path:
            if on_error:
                on_error("OpenVPN GUI est introuvable.")
            return

        def run():
            try:
                subprocess.run(
                    [gui_path, "--command", "disconnect_all"],
                    check=True,
                    creationflags=CREATE_NO_WINDOW
                )
                if on_success:
                    on_success()
            except subprocess.CalledProcessError as e:
                if on_error:
                    on_error(f"Erreur lors de la déconnexion : code {e.returncode}")
            except Exception as e:
                if on_error:
                    on_error(f"Échec de la déconnexion : {str(e)}")

        threading.Thread(target=run, daemon=True).start()

    @staticmethod
    def is_connected():
        """
        Détermine si un VPN est actif en vérifiant l'existence du processus openvpn.exe.
        Instantané (<1ms) grâce à psutil, sans lancer de sous-processus.
        """
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'] and proc.info['name'].lower() == 'openvpn.exe':
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return False

    @staticmethod
    def get_active_profile():
        """
        Détecte le nom du profil VPN actif (.ovpn) depuis la ligne de commande
        du processus openvpn.exe en cours d'exécution.
        """
        for proc in psutil.process_iter(['name', 'cmdline']):
            try:
                if proc.info['name'] and proc.info['name'].lower() == 'openvpn.exe':
                    cmdline = proc.info.get('cmdline') or []
                    for i, arg in enumerate(cmdline):
                        if '.ovpn' in arg.lower():
                            return os.path.basename(arg).strip('"')
                        if arg.lower() == '--config' and i + 1 < len(cmdline):
                            return os.path.basename(cmdline[i + 1]).strip('"')
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return None
