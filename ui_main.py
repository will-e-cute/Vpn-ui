import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel, QFrame, QMessageBox,
    QSystemTrayIcon, QMenu, QCompleter
)
from PySide6.QtCore import Qt, QTimer, QStringListModel
from PySide6.QtGui import QIcon

try:
    import pyi_splash
    pyi_splash.close()
except Exception:
    pass

from config_manager import ConfigManager
from vpn_manager import VPNManager
from ui_dialogs import SelectionDialog, SettingsDialog, HistoryDialog, AlreadyConnectedDialog

class OpenVPNUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OpenVPN UI")
        self.resize(540, 360)
        self.setMinimumSize(480, 320)

        # Icône de l'application
        self.icon_path = self._get_asset_path("VPN-Gui.ico")
        if os.path.exists(self.icon_path):
            self.app_icon = QIcon(self.icon_path)
            self.setWindowIcon(self.app_icon)
        else:
            self.app_icon = QIcon()

        self.config_mgr = ConfigManager()
        self.current_profile = None
        self.cached_ovpn_files = []
        self.tray_notified_on_close = False

        self._setup_ui()
        self._setup_tray()
        self._refresh_cached_files()

        # Timer pour l'actualisation du statut (toutes les 2 secondes)
        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(2000)

        # Première vérification du statut
        self.update_status()

    def _get_asset_path(self, filename):
        """Récupère le chemin d'un asset, compatible dev et PyInstaller."""
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, filename)
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)

    def _setup_ui(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)

        # 1. CARTE DE STATUT
        self.status_card = QFrame()
        self.status_card.setObjectName("statusCard")
        status_layout = QHBoxLayout(self.status_card)
        status_layout.setContentsMargins(14, 10, 14, 10)

        status_text_layout = QVBoxLayout()
        status_text_layout.setSpacing(2)

        self.lbl_status = QLabel("● VPN : Déconnecté")
        self.lbl_status.setObjectName("statusIndicator")
        self.lbl_status.setStyleSheet("color: #e74c3c; font-size: 14px; font-weight: bold;")

        self.lbl_profile = QLabel("Aucun profil actif")
        self.lbl_profile.setObjectName("profileName")
        self.lbl_profile.setStyleSheet("color: #a6adc8; font-size: 12px;")

        status_text_layout.addWidget(self.lbl_status)
        status_text_layout.addWidget(self.lbl_profile)
        status_layout.addLayout(status_text_layout)

        status_layout.addStretch()

        self.btn_status_details = QPushButton("Détails")
        self.btn_status_details.setObjectName("btnSecondary")
        self.btn_status_details.clicked.connect(self.show_profile_details)
        status_layout.addWidget(self.btn_status_details)

        main_layout.addWidget(self.status_card)

        # 2. ZONE DE RECHERCHE ET AUTOCOMPLÉTION
        search_layout = QHBoxLayout()
        search_layout.setSpacing(8)

        self.search_entry = QLineEdit()
        self.search_entry.setPlaceholderText("Rechercher un profil VPN (ex: PROD, CYCLING...)...")
        self.search_entry.returnPressed.connect(self.search_and_connect)
        search_layout.addWidget(self.search_entry)

        # Autocompléteur intelligent Qt
        self.completer_model = QStringListModel()
        self.completer = QCompleter(self.completer_model, self)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchContains)
        self.completer.activated.connect(self._on_autocomplete_selected)
        self.search_entry.setCompleter(self.completer)

        btn_search = QPushButton("Rechercher")
        btn_search.clicked.connect(self.search_and_connect)
        search_layout.addWidget(btn_search)

        main_layout.addLayout(search_layout)

        # 3. ACTIONS PRINCIPALES
        main_layout.addSpacing(6)
        btn_grid_layout = QVBoxLayout()
        btn_grid_layout.setSpacing(10)

        # Bouton Déconnexion rapide
        self.btn_disconnect = QPushButton("Déconnecter le VPN")
        self.btn_disconnect.setObjectName("btnDisconnect")
        self.btn_disconnect.clicked.connect(self.disconnect_vpn)
        btn_grid_layout.addWidget(self.btn_disconnect)

        # Boutons secondaires (Historique, Paramètres, Rafraîchir)
        secondary_row = QHBoxLayout()
        secondary_row.setSpacing(10)

        btn_history = QPushButton("Historique")
        btn_history.setObjectName("btnSecondary")
        btn_history.clicked.connect(self.show_history)
        secondary_row.addWidget(btn_history)

        btn_settings = QPushButton("Paramètres")
        btn_settings.setObjectName("btnSecondary")
        btn_settings.clicked.connect(self.show_settings)
        secondary_row.addWidget(btn_settings)

        btn_refresh = QPushButton("Rafraîchir")
        btn_refresh.setObjectName("btnSecondary")
        btn_refresh.setToolTip("Rafraîchit la liste des profils du dossier")
        btn_refresh.clicked.connect(self._refresh_cached_files)
        secondary_row.addWidget(btn_refresh)

        btn_grid_layout.addLayout(secondary_row)
        main_layout.addLayout(btn_grid_layout)

        main_layout.addStretch()

    def _setup_tray(self):
        """Initialise l'icône dans la zone de notification (System Tray)."""
        self.tray_icon = QSystemTrayIcon(self.app_icon, self)
        self.tray_icon.setToolTip("OpenVPN UI")

        tray_menu = QMenu()

        act_show = tray_menu.addAction("Afficher OpenVPN UI")
        act_show.triggered.connect(self.restore_window)

        tray_menu.addSeparator()

        self.act_tray_disconnect = tray_menu.addAction("Déconnecter le VPN")
        self.act_tray_disconnect.triggered.connect(self.disconnect_vpn)

        tray_menu.addSeparator()

        act_quit = tray_menu.addAction("Quitter")
        act_quit.triggered.connect(self.quit_app)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self._on_tray_activated)
        self.tray_icon.show()

    def _on_tray_activated(self, reason):
        if reason in (QSystemTrayIcon.Trigger, QSystemTrayIcon.DoubleClick):
            self.restore_window()

    def restore_window(self):
        self.show()
        self.setWindowState(self.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
        self.activateWindow()
        self.raise_()
        self.search_entry.setFocus()

    def closeEvent(self, event):
        """Réduit dans la zone de notification au lieu de quitter brutalement."""
        event.ignore()
        self.hide()
        if not self.tray_notified_on_close:
            self.notify_info(
                "OpenVPN UI",
                "L'application continue de s'exécuter en arrière-plan dans la barre des tâches."
            )
            self.tray_notified_on_close = True

    def quit_app(self):
        self.status_timer.stop()
        self.tray_icon.hide()
        QApplication.instance().quit()

    def _refresh_cached_files(self):
        """Indexe les fichiers .ovpn en mémoire pour une autocomplétion instantanée."""
        search_dir = self.config_mgr.get_search_directory()
        files = []
        if search_dir and os.path.exists(search_dir):
            try:
                for root, _, filenames in os.walk(search_dir):
                    for file in filenames:
                        if file.lower().endswith('.ovpn'):
                            files.append(file)
            except Exception as e:
                print(f"Erreur lors de l'indexation : {e}")

        self.cached_ovpn_files = sorted(list(set(files)))
        self.completer_model.setStringList(self.cached_ovpn_files)

    def _on_autocomplete_selected(self, selected_file):
        if selected_file:
            self.confirm_and_connect(selected_file)

    def search_and_connect(self):
        query = self.search_entry.text().strip().lower()
        if not query:
            return

        search_dir = self.config_mgr.get_search_directory()
        if not search_dir or not os.path.exists(search_dir):
            QMessageBox.critical(
                self,
                "Erreur",
                f"Le dossier de profils configuré n'existe pas :\n{search_dir}\n"
                "Veuillez corriger le chemin dans les Paramètres."
            )
            return

        # Recherche rapide en mémoire dans le cache
        matches = [f for f in self.cached_ovpn_files if query in f.lower()]

        if not matches:
            # Fallback recherche disque au cas où un nouveau fichier aurait été ajouté
            self._refresh_cached_files()
            matches = [f for f in self.cached_ovpn_files if query in f.lower()]

        if not matches:
            QMessageBox.information(
                self,
                "Résultat",
                f"Aucun profil VPN ne correspond à '{query}'."
            )
            return

        if len(matches) == 1:
            self.confirm_and_connect(matches[0])
        else:
            dialog = SelectionDialog(self, matches, self.confirm_and_connect)
            dialog.exec()

    def confirm_and_connect(self, file_name):
        if self.current_profile:
            dialog = AlreadyConnectedDialog(
                self,
                current_profile=self.current_profile,
                target_profile=file_name,
                on_disconnect_and_connect=self._disconnect_then_connect
            )
            dialog.exec()
        else:
            reply = QMessageBox.question(
                self,
                "Confirmation de connexion",
                f"Profil sélectionné :\n<b>{file_name}</b>\n\nSouhaitez-vous vous y connecter ?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.execute_connection(file_name)

    def _disconnect_then_connect(self, file_name):
        VPNManager.disconnect_all()
        # Attendre 1.5 seconde que l'ancien tunnel se ferme puis connecter
        QTimer.singleShot(1500, lambda: self.execute_connection(file_name))

    def execute_connection(self, file_name):
        self.lbl_status.setText("● Connexion en cours...")
        self.lbl_status.setStyleSheet("color: #f39c12; font-size: 14px; font-weight: bold;")
        self.lbl_profile.setText(f"Tentative : {file_name}")

        def on_success(name):
            self.config_mgr.add_to_history(name)
            self.notify_info("VPN Connecté", f"Connexion réussie à {name}")

        def on_error(err_msg):
            self.notify_error("Erreur VPN", err_msg)

        VPNManager.connect(file_name, on_success=on_success, on_error=on_error)
        self.search_entry.clear()

    def disconnect_vpn(self):
        def on_success():
            self.notify_info("VPN Déconnecté", "Toutes les connexions ont été fermées.")

        def on_error(err_msg):
            self.notify_error("Erreur Déconnexion", err_msg)

        VPNManager.disconnect_all(on_success=on_success, on_error=on_error)

    def update_status(self):
        """Vérifie l'état actuel du VPN sans bloquer l'interface."""
        is_conn = VPNManager.is_connected()
        active_prof = VPNManager.get_active_profile() if is_conn else None
        self.current_profile = active_prof

        if is_conn:
            self.lbl_status.setText("● VPN : Connecté")
            self.lbl_status.setStyleSheet("color: #2ecc71; font-size: 14px; font-weight: bold;")
            self.lbl_profile.setText(f"Profil : {active_prof or 'Profil actif (non spécifié)'}")
            self.btn_disconnect.setEnabled(True)
        else:
            self.lbl_status.setText("● VPN : Déconnecté")
            self.lbl_status.setStyleSheet("color: #e74c3c; font-size: 14px; font-weight: bold;")
            self.lbl_profile.setText("Aucun profil actif")
            self.btn_disconnect.setEnabled(False)

    def show_profile_details(self):
        if self.current_profile:
            QMessageBox.information(
                self,
                "Profil VPN Actif",
                f"Profil actuellement connecté :\n<b>{self.current_profile}</b>"
            )
        else:
            QMessageBox.information(
                self,
                "Profil VPN",
                "Aucun profil VPN n'est actuellement connecté."
            )

    def show_history(self):
        dialog = HistoryDialog(self, self.config_mgr, self.confirm_and_connect)
        dialog.exec()

    def show_settings(self):
        dialog = SettingsDialog(self, self.config_mgr, on_directory_changed=lambda _: self._refresh_cached_files())
        dialog.exec()

    def notify_info(self, title, message):
        if self.tray_icon.isVisible():
            self.tray_icon.showMessage(title, message, QSystemTrayIcon.Information, 3000)

    def notify_error(self, title, message):
        if self.tray_icon.isVisible():
            self.tray_icon.showMessage(title, message, QSystemTrayIcon.Critical, 4000)
        else:
            QMessageBox.critical(self, title, message)

def load_stylesheet(app):
    qss_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "style.qss")
    if hasattr(sys, '_MEIPASS'):
        qss_path = os.path.join(sys._MEIPASS, "style.qss")

    if os.path.exists(qss_path):
        try:
            with open(qss_path, "r", encoding="utf-8") as f:
                app.setStyleSheet(f.read())
        except Exception as e:
            print(f"Erreur chargement feuille de style : {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("OpenVPN UI")
    app.setQuitOnLastWindowClosed(False)

    load_stylesheet(app)

    window = OpenVPNUI()
    window.show()

    sys.exit(app.exec())
