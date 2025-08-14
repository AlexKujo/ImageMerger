"""Константы приложения Image Merger."""

from typing import Tuple

# Типы изображений
IMAGE_KINDS = ("color", "highlight", "outline")

# Настройки UI
DEFAULT_WINDOW_SIZE = (800, 600)
DEBOUNCE_TIME = 250
SPLITTER_RATIOS = (1, 3)

# Настройки изображений
DEFAULT_QUALITY = 95
DEFAULT_DPI: Tuple[int, int] = (300, 300)
SUPPORTED_FORMATS = "Images (*.png *.jpg *.jpeg)"
SAVE_FORMATS = "JPEG (*.jpg);;PNG (*.png)"

# Настройки обработки изображений
RED_HSV_RANGES = [
    ((0, 120, 70), (10, 255, 255)),    # Нижний красный диапазон
    ((170, 120, 70), (180, 255, 255))  # Верхний красный диапазон
]
BLACK_THRESHOLD = 10
FADE_WEIGHT = 0.5
OUTLINE_DARKEN_FACTOR = 0.5
