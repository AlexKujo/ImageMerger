"""Обработчик drag&drop для приложения Image Merger."""

from pathlib import Path
from typing import Callable, Dict, Any
from PyQt6.QtCore import QObject, QEvent
from PyQt6.QtGui import QDragEnterEvent, QDragMoveEvent, QDropEvent
from PyQt6.QtWidgets import QWidget


class DragDropHandler(QObject):
    """Класс для обработки drag&drop операций."""
    
    def __init__(self, parent: QWidget):
        """
        Инициализация обработчика drag&drop.
        
        Args:
            parent: Родительский виджет
        """
        super().__init__(parent)
        self.parent = parent
        self.drop_callbacks: Dict[QWidget, Callable[[Path], None]] = {}
    
    def register_drop_target(self, widget: QWidget, callback: Callable[[Path], None]) -> None:
        """
        Регистрирует виджет как цель для drop.
        
        Args:
            widget: Виджет для регистрации
            callback: Функция обратного вызова при drop
        """
        widget.setAcceptDrops(True)
        widget.installEventFilter(self)
        self.drop_callbacks[widget] = callback
    
    def unregister_drop_target(self, widget: QWidget) -> None:
        """
        Удаляет регистрацию виджета как цели для drop.
        
        Args:
            widget: Виджет для удаления регистрации
        """
        if widget in self.drop_callbacks:
            widget.removeEventFilter(self)
            del self.drop_callbacks[widget]
    
    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        """
        Фильтр событий для обработки drag&drop.
        
        Args:
            obj: Объект события
            event: Событие
            
        Returns:
            True если событие обработано, False иначе
        """
        if obj in self.drop_callbacks:
            if isinstance(event, QDragEnterEvent) and event.mimeData().hasUrls():
                event.acceptProposedAction()
                return True
            
            if isinstance(event, QDragMoveEvent) and event.mimeData().hasUrls():
                event.acceptProposedAction()
                return True
            
            if isinstance(event, QDropEvent) and event.mimeData().hasUrls():
                self._handle_drop(obj, event)
                event.acceptProposedAction()
                return True
        
        return super().eventFilter(obj, event)
    
    def _handle_drop(self, widget: QWidget, event: QDropEvent) -> None:
        """
        Обрабатывает событие drop.
        
        Args:
            widget: Виджет, на который произошел drop
            event: Событие drop
        """
        callback = self.drop_callbacks.get(widget)
        if callback is None:
            return
        
        # Обрабатываем первый URL из списка
        urls = event.mimeData().urls()
        if urls:
            file_path = Path(urls[0].toLocalFile())
            if file_path.is_file():
                callback(file_path)
