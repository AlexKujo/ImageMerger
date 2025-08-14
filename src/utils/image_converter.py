"""Конвертер изображений между различными форматами."""

from PyQt6 import QtGui
from PIL import Image
from PIL.ImageQt import ImageQt


class ImageConverter:
    """Класс для конвертации изображений между PIL и Qt форматами."""
    
    @staticmethod
    def pil_to_qimage(pil_img: Image.Image) -> QtGui.QImage:
        """
        Конвертирует PIL изображение в Qt QImage.
        
        Args:
            pil_img: PIL изображение
            
        Returns:
            Qt QImage
        """
        return ImageQt(pil_img).copy()
    
    @staticmethod
    def pil_to_qpixmap(pil_img: Image.Image, device_pixel_ratio: float = 1.0) -> QtGui.QPixmap:
        """
        Конвертирует PIL изображение в Qt QPixmap.
        
        Args:
            pil_img: PIL изображение
            device_pixel_ratio: Коэффициент пикселей устройства
            
        Returns:
            Qt QPixmap
        """
        qimage = ImageConverter.pil_to_qimage(pil_img)
        pixmap = QtGui.QPixmap.fromImage(qimage)
        pixmap.setDevicePixelRatio(device_pixel_ratio)
        return pixmap
