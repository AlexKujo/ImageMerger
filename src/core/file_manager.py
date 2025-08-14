"""Менеджер файлов для приложения Image Merger."""

from pathlib import Path
from typing import Optional, Tuple
from PyQt6.QtWidgets import QFileDialog, QMessageBox, QWidget

from src.utils.constants import SUPPORTED_FORMATS, SAVE_FORMATS, DEFAULT_QUALITY, DEFAULT_DPI


class FileManager:
    """Класс для работы с файлами и диалогами."""
    
    def __init__(self, parent_widget: QWidget):
        """
        Инициализация менеджера файлов.
        
        Args:
            parent_widget: Родительский виджет для диалогов
        """
        self.parent = parent_widget
        self.last_directory: Path = Path.home()
    
    def open_image_dialog(self, title: str = "Выбрать изображение") -> Optional[Path]:
        """
        Открывает диалог выбора изображения.
        
        Args:
            title: Заголовок диалога
            
        Returns:
            Путь к выбранному файлу или None
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self.parent,
            title,
            str(self.last_directory),
            SUPPORTED_FORMATS
        )
        
        if file_path:
            path = Path(file_path)
            self.last_directory = path.parent
            return path
        
        return None
    
    def save_image_dialog(self, default_path: Path) -> Optional[Tuple[Path, str]]:
        """
        Открывает диалог сохранения изображения.
        
        Args:
            default_path: Путь по умолчанию
            
        Returns:
            Кортеж (путь, формат) или None
        """
        save_path, selected_filter = QFileDialog.getSaveFileName(
            self.parent,
            "Сохранить результат",
            str(default_path),
            SAVE_FORMATS
        )
        
        if save_path:
            path = Path(save_path)
            # Определяем формат по расширению
            format_name = 'PNG' if path.suffix.lower() == '.png' else 'JPEG'
            return path, format_name
        
        return None
    
    def save_image(self, image, path: Path, format_name: str) -> bool:
        """
        Сохраняет изображение в файл.
        
        Args:
            image: PIL изображение для сохранения
            path: Путь для сохранения
            format_name: Формат файла (PNG или JPEG)
            
        Returns:
            True если сохранение успешно, False иначе
        """
        try:
            if format_name == 'PNG':
                image.save(path, format=format_name, dpi=DEFAULT_DPI)
            else:  # JPEG
                image.save(
                    path, 
                    format=format_name, 
                    quality=DEFAULT_QUALITY, 
                    subsampling=0, 
                    dpi=DEFAULT_DPI
                )
            return True
        except Exception as e:
            QMessageBox.critical(
                self.parent, 
                "Ошибка", 
                f"Не удалось сохранить файл: {e}"
            )
            return False
    
    def show_error(self, title: str, message: str) -> None:
        """
        Показывает диалог ошибки.
        
        Args:
            title: Заголовок диалога
            message: Сообщение об ошибке
        """
        QMessageBox.critical(self.parent, title, message)
    
    def show_warning(self, title: str, message: str) -> None:
        """
        Показывает диалог предупреждения.
        
        Args:
            title: Заголовок диалога
            message: Сообщение предупреждения
        """
        QMessageBox.warning(self.parent, title, message)
    
    def show_info(self, title: str, message: str) -> None:
        """
        Показывает информационный диалог.
        
        Args:
            title: Заголовок диалога
            message: Информационное сообщение
        """
        QMessageBox.information(self.parent, title, message)
