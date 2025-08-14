"""Главное окно приложения Image Merger."""

from PyQt6 import QtWidgets, QtGui
from PyQt6.QtCore import Qt, QTimer
from typing import Dict

from src.core.image_manager import ImageManager
from src.core.file_manager import FileManager
from src.utils.constants import IMAGE_KINDS, DEFAULT_WINDOW_SIZE, DEBOUNCE_TIME, SPLITTER_RATIOS
from src.utils.resource_loader import ResourceLoader
from src.ui.preview_widget import PreviewWidget
from src.ui.drag_drop_handler import DragDropHandler

# Импортируем UI
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
from ui_main_new import Ui_Form


class MainWindow(QtWidgets.QWidget):
    """Главное окно приложения Image Merger."""
    
    def __init__(self):
        """Инициализация главного окна."""
        super().__init__()
        
        # Инициализация UI
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        
        # Настройка окна
        self.resize(*DEFAULT_WINDOW_SIZE)
        self.setWindowTitle("Image Merger")
        
        # Загрузка иконки
        icon_path = ResourceLoader.load_icon()
        if icon_path:
            self.setWindowIcon(QtGui.QIcon(str(icon_path)))
        
        # Инициализация менеджеров
        self.image_manager = ImageManager()
        self.file_manager = FileManager(self)
        self.drag_drop_handler = DragDropHandler(self)
        
        # Инициализация превью виджетов
        self.preview_widgets: Dict[str, PreviewWidget] = {}
        self._setup_preview_widgets()
        
        # Настройка UI элементов
        self._setup_ui_connections()
        self._setup_splitter()
        self._setup_debounce_timer()
        
        # Настройка drag&drop
        self._setup_drag_drop()
    
    def _setup_preview_widgets(self):
        """Настройка виджетов превью."""
        for kind in (*IMAGE_KINDS, 'result'):
            view = getattr(self.ui, f"{kind}preview")
            self.preview_widgets[kind] = PreviewWidget(view)
    
    def _setup_ui_connections(self):
        """Настройка соединений сигналов и слотов."""
        # Кнопки загрузки изображений
        for kind in IMAGE_KINDS:
            btn = getattr(self.ui, f"{kind}button")
            view = getattr(self.ui, f"{kind}preview")
            btn.clicked.connect(lambda _, k=kind: self._load_image_dialog(k))
            
            # Контекстное меню
            view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            view.customContextMenuRequested.connect(
                lambda pos, k=kind: self._show_context_menu(pos, k)
            )
        
        # Кнопка сохранения
        self.ui.savebutton.clicked.connect(self._save_result)
        
        # Обработка изменения размера splitter
        self.ui.splitter.splitterMoved.connect(self._schedule_preview_update)
    
    def _setup_splitter(self):
        """Настройка splitter."""
        self.ui.splitter.setStretchFactor(0, SPLITTER_RATIOS[0])
        self.ui.splitter.setStretchFactor(1, SPLITTER_RATIOS[1])
        self.ui.splitter.setCollapsible(0, False)
        self.ui.splitter.setCollapsible(1, False)
    
    def _setup_debounce_timer(self):
        """Настройка таймера для debounce."""
        self._debounce_timer = QTimer(self)
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.timeout.connect(self._render_all_previews)
        self.resize_pending = False
    
    def _setup_drag_drop(self):
        """Настройка drag&drop."""
        for kind in IMAGE_KINDS:
            viewport = self.preview_widgets[kind].get_viewport()
            self.drag_drop_handler.register_drop_target(
                viewport, 
                lambda path, k=kind: self._load_image_path(k, path)
            )
    
    def _load_image_dialog(self, kind: str):
        """Открывает диалог выбора изображения."""
        path = self.file_manager.open_image_dialog()
        if path:
            self._load_image_path(kind, path)
    
    def _load_image_path(self, kind: str, path):
        """Загружает изображение по пути."""
        if self.image_manager.load_image(kind, path):
            self._show_preview(kind)
            self._try_update_result()
        else:
            self.file_manager.show_error(
                "Ошибка", 
                f"Не удалось загрузить файл: {path}"
            )
    
    def _show_preview(self, kind: str):
        """Показывает превью изображения."""
        img = self.image_manager.get_image(kind)
        self.preview_widgets[kind].show_image(img)
    
    def _try_update_result(self):
        """Пытается обновить результат."""
        if self.image_manager.has_required_images():
            self._update_result()
    
    def _update_result(self):
        """Обновляет результат обработки."""
        result = self.image_manager.process_images()
        if result:
            self.preview_widgets['result'].show_image(result)
    
    def _show_context_menu(self, pos, kind: str):
        """Показывает контекстное меню."""
        menu = QtWidgets.QMenu(self)
        action = menu.addAction("Удалить изображение")
        
        if menu.exec(self.preview_widgets[kind].view.mapToGlobal(pos)) == action:
            self._clear_image(kind)
    
    def _clear_image(self, kind: str):
        """Очищает изображение указанного типа."""
        self.image_manager.remove_image(kind)
        self.preview_widgets[kind].clear()
        
        if self.image_manager.has_required_images():
            self._update_result()
        else:
            self.preview_widgets['result'].clear()
    
    def _save_result(self):
        """Сохраняет результат."""
        result = self.image_manager.get_result()
        if result is None:
            self.file_manager.show_warning(
                "Ошибка", 
                "Необходимо добавить цвет и контур"
            )
            return
        
        default_path = self.image_manager.get_default_save_path()
        save_info = self.file_manager.save_image_dialog(default_path)
        
        if save_info:
            path, format_name = save_info
            self.file_manager.save_image(result, path, format_name)
    
    def _schedule_preview_update(self):
        """Планирует обновление превью."""
        if not self.resize_pending:
            self._debounce_timer.start(DEBOUNCE_TIME)
            self.resize_pending = True
    
    def _render_all_previews(self):
        """Обновляет все превью."""
        self.resize_pending = False
        
        for kind in IMAGE_KINDS:
            img = self.image_manager.get_image(kind)
            self.preview_widgets[kind].show_image(img)
        
        result = self.image_manager.get_result()
        self.preview_widgets['result'].show_image(result)
    
    def resizeEvent(self, event):
        """Обработчик изменения размера окна."""
        super().resizeEvent(event)
        self._schedule_preview_update()
