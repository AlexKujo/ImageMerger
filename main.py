"""Альтернативная точка входа в приложение Image Merger."""

import sys
from pathlib import Path

# Добавляем src в путь для импортов
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Импортируем и запускаем
from src.main import main

if __name__ == "__main__":
    main()
