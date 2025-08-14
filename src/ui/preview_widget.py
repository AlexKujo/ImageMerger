"""Виджет превью изображений для приложения Image Merger."""

from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PIL import Image

from src.utils.image_converter import ImageConverter


class PreviewWidget:
    """Класс для управления превью изображений."""
    
    def __init__(self, graphics_view: QtWidgets.QGraphicsView):
        """
        Инициализация виджета превью.
        
        Args:
            graphics_view: QGraphicsView для отображения
        """
        self.view = graphics_view
        self.scene = QtWidgets.QGraphicsScene()
        self.view.setScene(self.scene)
        self.view.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
    def show_image(self, pil_img: Image.Image) -> None:
        """
        Отображает PIL изображение в превью.
        
        Args:
            pil_img: PIL изображение для отображения
        """
        if pil_img is None:
            self.clear()
            return
        
        # Получаем размеры viewport
        orig_w, orig_h = pil_img.size
        dpr = self.view.devicePixelRatioF() or 1.0
        vw = int(self.view.viewport().width() * dpr)
        vh = int(self.view.viewport().height() * dpr)
        
        # Вычисляем масштаб
        scale = min(vw / orig_w, vh / orig_h)
        preview_w = int(orig_w * scale)
        preview_h = int(orig_h * scale)
        
        # Создаем превью
        preview = pil_img.resize((preview_w, preview_h), Image.LANCZOS)
        pixmap = ImageConverter.pil_to_qpixmap(preview, dpr)
        
        # Отображаем
        self.scene.clear()
        self.scene.addPixmap(pixmap)
        self.scene.setSceneRect(pixmap.rect().toRectF())
        self.view.resetTransform()
    
    def clear(self) -> None:
        """Очищает превью."""
        self.scene.clear()
        self.view.resetTransform()
    
    def get_viewport(self):
        """Возвращает viewport виджета."""
        return self.view.viewport()
    
    def reset_transform(self) -> None:
        """Сбрасывает трансформации view."""
        self.view.resetTransform()
