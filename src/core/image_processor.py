"""Обработчик изображений для приложения Image Merger."""

import cv2
import numpy as np
from PIL import Image
from typing import Optional

from src.utils.constants import (
    RED_HSV_RANGES, 
    BLACK_THRESHOLD, 
    FADE_WEIGHT, 
    OUTLINE_DARKEN_FACTOR
)


class ImageProcessor:
    """Класс для обработки изображений с применением эффектов."""
    
    @staticmethod
    def apply_highlight(color: np.ndarray, highlight: np.ndarray) -> np.ndarray:
        """
        Применяет эффект подсветки к цветному изображению.
        
        Args:
            color: Цветное изображение в формате BGR
            highlight: Изображение подсветки в формате BGR
            
        Returns:
            Обработанное изображение
        """
        hsv = cv2.cvtColor(highlight, cv2.COLOR_BGR2HSV)
        
        # Создаем маску для красных областей
        red_mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
        for lower, upper in RED_HSV_RANGES:
            mask = cv2.inRange(hsv, lower, upper)
            red_mask = cv2.bitwise_or(red_mask, mask)
        
        # Создаем затемненную версию
        white_bg = np.full_like(color, 255)
        faded = cv2.addWeighted(color, FADE_WEIGHT, white_bg, FADE_WEIGHT, 0)
        
        # Применяем подсветку
        result = faded.copy()
        result[red_mask > 0] = color[red_mask > 0]
        
        return result
    
    @staticmethod
    def apply_outline(image: np.ndarray, outline: np.ndarray) -> np.ndarray:
        """
        Применяет эффект контура к изображению.
        
        Args:
            image: Исходное изображение в формате BGR
            outline: Изображение контура в формате BGR
            
        Returns:
            Обработанное изображение
        """
        gray = cv2.cvtColor(outline, cv2.COLOR_BGR2GRAY)
        black_mask = cv2.inRange(gray, 0, BLACK_THRESHOLD)
        
        if np.any(black_mask):
            image[black_mask > 0] = (
                image[black_mask > 0] * OUTLINE_DARKEN_FACTOR
            ).astype(np.uint8)
        
        return image
    
    @staticmethod
    def process_images(
        color: np.ndarray, 
        outline: np.ndarray, 
        highlight: Optional[np.ndarray] = None
    ) -> np.ndarray:
        """
        Обрабатывает изображения, применяя все эффекты.
        
        Args:
            color: Цветное изображение
            outline: Изображение контура
            highlight: Изображение подсветки (опционально)
            
        Returns:
            Финальное обработанное изображение
        """
        result = color.copy()
        
        # Применяем подсветку если есть
        if highlight is not None:
            result = ImageProcessor.apply_highlight(result, highlight)
        
        # Применяем контур
        result = ImageProcessor.apply_outline(result, outline)
        
        return result
    
    @staticmethod
    def pil_to_cv2(pil_img: Image.Image) -> np.ndarray:
        """
        Конвертирует PIL изображение в OpenCV формат (BGR).
        
        Args:
            pil_img: PIL изображение
            
        Returns:
            OpenCV изображение в формате BGR
        """
        return np.array(pil_img)[:, :, ::-1]
    
    @staticmethod
    def cv2_to_pil(cv2_img: np.ndarray) -> Image.Image:
        """
        Конвертирует OpenCV изображение (BGR) в PIL формат.
        
        Args:
            cv2_img: OpenCV изображение в формате BGR
            
        Returns:
            PIL изображение
        """
        rgb_img = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
        return Image.fromarray(rgb_img)
