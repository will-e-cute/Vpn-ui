import json
import os
import shutil
from collections import deque

APP_DIR = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), 'OpenVPN_UI')
CONFIG_FILE = os.path.join(APP_DIR, 'config.json')
LOCAL_CONFIG_FILE = 'config.json'
HISTORY_SIZE = 8

class ConfigManager:
    def __init__(self):
        os.makedirs(APP_DIR, exist_ok=True)
        self._migrate_old_config_if_needed()
        self.config = self.load_config()
        self.history = deque(self.config.get("history", []), maxlen=HISTORY_SIZE)

    def _migrate_old_config_if_needed(self):
        """Migre l'ancien config.json local vers %APPDATA%/OpenVPN_UI s'il existe."""
        if not os.path.exists(CONFIG_FILE) and os.path.exists(LOCAL_CONFIG_FILE):
            try:
                shutil.copy2(LOCAL_CONFIG_FILE, CONFIG_FILE)
            except IOError:
                pass

    def load_config(self):
        default_dir = os.path.join(
            os.environ.get('USERPROFILE', os.path.expanduser('~')),
            'OpenVPN',
            'config'
        )
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if not isinstance(data, dict):
                        data = {}
                    if "search_directory" not in data:
                        data["search_directory"] = default_dir
                    if "history" not in data:
                        data["history"] = []
                    return data
            except (json.JSONDecodeError, IOError):
                pass
        return {"search_directory": default_dir, "history": []}

    def save_config(self):
        self.config["history"] = list(self.history)
        temp_file = CONFIG_FILE + ".tmp"
        try:
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            if os.path.exists(CONFIG_FILE):
                os.replace(temp_file, CONFIG_FILE)
            else:
                os.rename(temp_file, CONFIG_FILE)
        except IOError as e:
            print(f"Erreur lors de la sauvegarde de la configuration : {e}")
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except OSError:
                    pass

    def get_search_directory(self):
        return self.config.get("search_directory", "")

    def set_search_directory(self, directory):
        self.config["search_directory"] = directory
        self.save_config()

    def add_to_history(self, file_path_or_name):
        # Stocker uniquement le nom de fichier pour la cohérence
        file_name = os.path.basename(file_path_or_name)
        if file_name in self.history:
            self.history.remove(file_name)
        self.history.appendleft(file_name)
        self.save_config()

    def get_history(self):
        return list(self.history)

    def clear_history(self):
        self.history.clear()
        self.save_config()
