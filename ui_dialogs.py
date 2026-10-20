import os
import subprocess
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QFileDialog, QLineEdit, QMessageBox
)
from PySide6.QtCore import Qt

class BaseDialog(QDialog):
    def __init__(self, parent=None, title=""):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setModal(True)

class SelectionDialog(BaseDialog):
    """Dialogue affiché lorsqu'une recherche renvoie plusieurs fichiers .ovpn."""
    def __init__(self, parent, files, on_select_callback):
        super().__init__(parent, "Sélection du profil VPN")
        self.files = files
        self.on_select_callback = on_select_callback
        self.resize(550, 350)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        info_label = QLabel(f"Plusieurs profils trouvés ({len(files)}). Sélectionnez celui à utiliser :")
        layout.addWidget(info_label)

        # Filtre rapide
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Filtrer parmi les résultats...")
        self.filter_input.textChanged.connect(self._filter_list)
        layout.addWidget(self.filter_input)

        self.list_widget = QListWidget()
        for f in self.files:
            self.list_widget.addItem(f)
        self.list_widget.itemDoubleClicked.connect(self._on_item_double_clicked)
        layout.addWidget(self.list_widget)

        btn_layout = QHBoxLayout()
        btn_cancel = QPushButton("Annuler")
        btn_cancel.setObjectName("btnSecondary")
        btn_cancel.clicked.connect(self.reject)

        btn_select = QPushButton("Se connecter")
        btn_select.clicked.connect(self._on_select_clicked)

        btn_layout.addStretch()
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_select)
        layout.addLayout(btn_layout)

    def _filter_list(self, text):
        query = text.lower()
        self.list_widget.clear()
        for f in self.files:
            if query in f.lower():
                self.list_widget.addItem(f)

    def _on_item_double_clicked(self, item):
        self.on_select_callback(item.text())
        self.accept()

    def _on_select_clicked(self):
        current_item = self.list_widget.currentItem()
        if current_item:
            self.on_select_callback(current_item.text())
            self.accept()
        else:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner un profil dans la liste.")

class SettingsDialog(BaseDialog):
    """Dialogue de configuration du dossier de recherche des profils."""
    def __init__(self, parent, config_manager, on_directory_changed=None):
        super().__init__(parent, "Paramètres")
        self.config_manager = config_manager
        self.on_directory_changed = on_directory_changed
        self.resize(550, 220)

        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(20, 20, 20, 20)

        title_label = QLabel("Répertoire de recherche des fichiers .ovpn :")
        layout.addWidget(title_label)

        path_layout = QHBoxLayout()
        self.path_input = QLineEdit()
        self.path_input.setText(self.config_manager.get_search_directory())
        self.path_input.setReadOnly(True)
        path_layout.addWidget(self.path_input)

        btn_browse = QPushButton("Parcourir...")
        btn_browse.setObjectName("btnSecondary")
        btn_browse.clicked.connect(self._browse_directory)
        path_layout.addWidget(btn_browse)
        layout.addLayout(path_layout)

        # Boutons d'action
        btn_layout = QHBoxLayout()
        btn_open_folder = QPushButton("Ouvrir dans l'Explorateur")
        btn_open_folder.setObjectName("btnSecondary")
        btn_open_folder.clicked.connect(self._open_in_explorer)
        btn_layout.addWidget(btn_open_folder)

        btn_layout.addStretch()

        btn_close = QPushButton("Fermer")
        btn_close.setObjectName("btnSecondary")
        btn_close.clicked.connect(self.accept)
        btn_layout.addWidget(btn_close)

        layout.addLayout(btn_layout)

    def _browse_directory(self):
        current = self.path_input.text()
        chosen = QFileDialog.getExistingDirectory(self, "Sélectionner le dossier des profils OpenVPN", current)
        if chosen:
            chosen = os.path.normpath(chosen)
            self.path_input.setText(chosen)
            self.config_manager.set_search_directory(chosen)
            if self.on_directory_changed:
                self.on_directory_changed(chosen)
            QMessageBox.information(self, "Succès", f"Dossier de recherche mis à jour :\n{chosen}")

    def _open_in_explorer(self):
        directory = self.path_input.text()
        if os.path.exists(directory):
            subprocess.run(["explorer", directory], shell=True)
        else:
            QMessageBox.warning(self, "Erreur", "Le dossier spécifié n'existe pas.")

class HistoryDialog(BaseDialog):
    """Dialogue affichant l'historique des connexions récentes."""
    def __init__(self, parent, config_manager, on_select_callback):
        super().__init__(parent, "Historique des connexions")
        self.config_manager = config_manager
        self.on_select_callback = on_select_callback
        self.resize(550, 320)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        layout.addWidget(QLabel("Connexions VPN récentes (double-cliquez pour vous connecter) :"))

        self.list_widget = QListWidget()
        history = self.config_manager.get_history()
        for f in history:
            self.list_widget.addItem(f)
        self.list_widget.itemDoubleClicked.connect(self._on_item_double_clicked)
        layout.addWidget(self.list_widget)

        btn_layout = QHBoxLayout()
        btn_clear = QPushButton("Effacer l'historique")
        btn_clear.setObjectName("btnDisconnect")
        btn_clear.clicked.connect(self._clear_history)
        btn_layout.addWidget(btn_clear)

        btn_layout.addStretch()

        btn_connect = QPushButton("Se connecter")
        btn_connect.clicked.connect(self._on_connect_clicked)
        btn_layout.addWidget(btn_connect)

        layout.addLayout(btn_layout)

    def _on_item_double_clicked(self, item):
        self.on_select_callback(item.text())
        self.accept()

    def _on_connect_clicked(self):
        current_item = self.list_widget.currentItem()
        if current_item:
            self.on_select_callback(current_item.text())
            self.accept()
        else:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner un profil.")

    def _clear_history(self):
        reply = QMessageBox.question(
            self,
            "Confirmation",
            "Voulez-vous vraiment effacer l'historique des connexions ?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.config_manager.clear_history()
            self.list_widget.clear()

class AlreadyConnectedDialog(BaseDialog):
    """Dialogue affiché lorsqu'un VPN est déjà actif."""
    def __init__(self, parent, current_profile, target_profile, on_disconnect_and_connect):
        super().__init__(parent, "VPN déjà connecté")
        self.target_profile = target_profile
        self.on_disconnect_and_connect = on_disconnect_and_connect
        self.resize(450, 160)

        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(20, 20, 20, 20)

        label_msg = QLabel(
            f"Un VPN est déjà actif (<b>{current_profile or 'Profil inconnu'}</b>).<br>"
            f"Voulez-vous vous déconnecter et basculer vers <b>{target_profile}</b> ?"
        )
        label_msg.setWordWrap(True)
        layout.addWidget(label_msg)

        btn_layout = QHBoxLayout()
        btn_cancel = QPushButton("Annuler")
        btn_cancel.setObjectName("btnSecondary")
        btn_cancel.clicked.connect(self.reject)

        btn_switch = QPushButton("Déconnecter et continuer")
        btn_switch.clicked.connect(self._confirm_switch)

        btn_layout.addStretch()
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_switch)
        layout.addLayout(btn_layout)

    def _confirm_switch(self):
        self.accept()
        self.on_disconnect_and_connect(self.target_profile)
