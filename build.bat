@echo off
chcp 65001 >nul
echo ========================================================
echo Compilation de OpenVPN_UI avec PyInstaller / auto-py-to-exe
echo ========================================================

call .venv\Scripts\activate
pyinstaller --noconfirm --onefile --windowed --icon "VPN-Gui.ico" --name "OpenVPN_UI" --add-data "style.qss;." --add-data "VPN-Gui.ico;." --add-data "Splash.jpg;." --splash "Splash.jpg" --hidden-import "psutil" --clean "ui_main.py"

echo.
echo ========================================================
echo Terminé ! L'exécutable est disponible dans dist\OpenVPN_UI.exe
echo ========================================================
pause
