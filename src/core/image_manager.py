"""Менеджер изображений для приложения Image Merger."""

from pathlib import Path
from typing import Dict, Optional, Tuple
from PIL import Image

from src.utils.constants import IMAGE_KINDS
from src.core.image_processor import ImageProcessor


class ImageManager:
    """Класс для управления загруженными изображениями."""
    
    def __init__(self):
        """Инициализация менеджера изображений."""
        self.image_paths: Dict[str, Optional[Path]] = {k: None for k in IMAGE_KINDS}
        self.pil_images: Dict[str, Image.Image] = {}
        self._last_result: Optional[Image.Image] = None
    
    def load_image(self, kind: str, path: Path) -> bool:
        """
        Загружает изображение указанного типа.
        
        Args:
            kind: Тип изображения (color, highlight, outline)
            path: Путь к файлу изображения
            
        Returns:
            True если загрузка успешна, False иначе
        """
        if kind not in IMAGE_KINDS:
            return False
        
        try:
            img = Image.open(path).convert("RGB")
            self.pil_images[kind] = img
            self.image_paths[kind] = path
            return True
        except Exception:
            return False
    
    def remove_image(self, kind: str) -> None:
        """
        Удаляет изображение указанного типа.
        
        Args:
            kind: Тип изображения для удаления
        """
        if kind in IMAGE_KINDS:
            self.pil_images.pop(kind, None)
            self.image_paths[kind] = None
    
    def get_image(self, kind: str) -> Optional[Image.Image]:
        """
        Возвращает изображение указанного типа.
        
        Args:
            kind: Тип изображения
            
        Returns:
            PIL изображение или None
        """
        return self.pil_images.get(kind)
    
    def get_image_path(self, kind: str) -> Optional[Path]:
        """
        Возвращает путь к изображению указанного типа.
        
        Args:
            kind: Тип изображения
            
        Returns:
            Путь к файлу или None
        """
        return self.image_paths.get(kind)
    
    def has_required_images(self) -> bool:
        """
        Проверяет наличие обязательных изображений.
        
        Returns:
            True если есть color и outline изображения
        """
        return (
            self.image_paths['color'] is not None and 
            self.image_paths['outline'] is not None
        )
    
    def process_images(self) -> Optional[Image.Image]:
        """
        Обрабатывает все загруженные изображения.
        
        Returns:
            Обработанное изображение или None
        """
        if not self.has_required_images():
            return None
        
        # Конвертируем в OpenCV формат
        color_cv = ImageProcessor.pil_to_cv2(self.pil_images['color'])
        outline_cv = ImageProcessor.pil_to_cv2(self.pil_images['outline'])
        highlight_cv = None
        
        if 'highlight' in self.pil_images:
            highlight_cv = ImageProcessor.pil_to_cv2(self.pil_images['highlight'])
        
        # Обрабатываем изображения
        result_cv = ImageProcessor.process_images(color_cv, outline_cv, highlight_cv)
        
        # Конвертируем обратно в PIL
        self._last_result = ImageProcessor.cv2_to_pil(result_cv)
        return self._last_result
    
    def get_result(self) -> Optional[Image.Image]:
        """
        Возвращает последний результат обработки.
        
        Returns:
            Обработанное изображение или None
        """
        return self._last_result
    
    def get_default_save_path(self) -> Path:
        """
        Возвращает путь по умолчанию для сохранения.
        
        Returns:
            Путь для сохранения
        """
        if self.image_paths['color']:
            return self.image_paths['color'].with_suffix('.jpg')
        return Path.cwd() / 'result.jpg'
    
    def clear_all(self) -> None:
        """Очищает все изображения."""
        self.image_paths = {k: None for k in IMAGE_KINDS}
        self.pil_images.clear()
        self._last_result = None
