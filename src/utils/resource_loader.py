"""Загрузчик ресурсов приложения."""

import sys
from pathlib import Path
from typing import Optional


class ResourceLoader:
    """Класс для загрузки ресурсов приложения."""
    
    @staticmethod
    def get_resource_path(rel_path: str) -> Path:
        """
        Возвращает абсолютный путь к ресурсу.
        
        Args:
            rel_path: Относительный путь к ресурсу
            
        Returns:
            Абсолютный путь к ресурсу
        """
        if getattr(sys, 'frozen', False):
            # Когда запущен из одного exe через PyInstaller
            base = Path(sys._MEIPASS)
        else:
            # Когда запущен обычный скрипт
            base = Path(__file__).parent.parent.parent
        return base / rel_path
    
    @staticmethod
    def load_icon(icon_name: str = "icon.ico") -> Optional[Path]:
        """
        Загружает иконку приложения.
        
        Args:
            icon_name: Имя файла иконки
            
        Returns:
            Путь к иконке или None если файл не найден
        """
        icon_path = ResourceLoader.get_resource_path(icon_name)
        return icon_path if icon_path.exists() else None
