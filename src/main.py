"""Главный файл приложения Image Merger."""

import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6 import QtGui

# Обеспечиваем доступность пакета src при прямом запуске этого файла
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.ui.main_window import MainWindow
from src.utils.resource_loader import ResourceLoader


def main():
    """Главная функция приложения."""
    app = QApplication(sys.argv)
    
    # Загружаем иконку приложения
    icon_path = ResourceLoader.load_icon()
    if icon_path:
        app.setWindowIcon(QtGui.QIcon(str(icon_path)))
    
    # Настраиваем стиль
    app.setStyle("Fusion")
    
    # Создаем и показываем главное окно
    window = MainWindow()
    window.show()
    
    # Запускаем приложение
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
