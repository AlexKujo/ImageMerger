from PyQt6 import QtGui, QtWidgets
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QDragEnterEvent, QDragMoveEvent, QDropEvent
from PyQt6.QtWidgets import QApplication, QFileDialog, QMessageBox
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from PIL.ImageQt import ImageQt

from ui_main_new import Ui_Form

def pil_to_qimage(pil_img: Image.Image) -> QtGui.QImage:
    return ImageQt(pil_img).copy()

def resource_path(rel_path: str) -> Path:
    if getattr(sys, 'frozen', False):
        base = Path(sys._MEIPASS)
    else:
        base = Path(__file__).parent
    return base / rel_path

class ImageProcessor:
    @staticmethod
    def apply_highlight(color: np.ndarray, highlight: np.ndarray) -> np.ndarray:
        hsv = cv2.cvtColor(highlight, cv2.COLOR_BGR2HSV)
        mask1 = cv2.inRange(hsv, (0, 120, 70), (10, 255, 255))
        mask2 = cv2.inRange(hsv, (170, 120, 70), (180, 255, 255))
        red_mask = cv2.bitwise_or(mask1, mask2)
        white_bg = np.full_like(color, 255)
        faded = cv2.addWeighted(color, 0.5, white_bg, 0.5, 0)
        result = faded.copy()
        result[red_mask > 0] = color[red_mask > 0]
        return result

    @staticmethod
    def apply_outline(image: np.ndarray, outline: np.ndarray) -> np.ndarray:
        gray = cv2.cvtColor(outline, cv2.COLOR_BGR2GRAY)
        black_mask = cv2.inRange(gray, 0, 10)
        if np.any(black_mask):
            image[black_mask > 0] = (image[black_mask > 0] * 0.5).astype(np.uint8)
        return image

class ImageMergeApp(QtWidgets.QWidget):
    KINDS = ("color", "highlight", "outline")

    DEBOUNCE_TIME = 250
    DEFAULT_QUALITY = 95
    DEFAULT_DPI = (300, 300)

    def __init__(self) -> None:
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.resize(800, 600)

        self.setWindowIcon(QtGui.QIcon("icon.ico"))

        self.last_dir: Path = Path.home()
        self.image_paths: dict[str, Path | None] = {k: None for k in self.KINDS}
        self.pil_images: dict[str, Image.Image] = {}
        self._last_result: Image.Image | None = None

        self.scenes = {}
        self.viewports = {}
        for kind in (*self.KINDS, 'result'):
            view = getattr(self.ui, f"{kind}preview")
            scene = QtWidgets.QGraphicsScene(self)
            view.setScene(scene)
            view.setAlignment(Qt.AlignmentFlag.AlignCenter)
            vp = view.viewport()
            vp.setAcceptDrops(True)
            vp.installEventFilter(self)
            self.scenes[kind] = scene
            self.viewports[vp] = kind

        for kind in self.KINDS:
            btn = getattr(self.ui, f"{kind}button")
            view = getattr(self.ui, f"{kind}preview")
            btn.clicked.connect(lambda _, k=kind, v=view: self.load_image_dialog(k, v))
            view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            view.customContextMenuRequested.connect(
                lambda pos, k=kind, v=view: self.show_context_menu(pos, k, v)
            )

        self.ui.savebutton.clicked.connect(self.save_result)
        self.ui.splitter.splitterMoved.connect(self.schedule_preview_update)

        self._debounce_timer = QTimer(self)
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.timeout.connect(self.render_all_previews)
        self.resize_pending = False
        self.refresh_time = self.DEBOUNCE_TIME

        self.ui.splitter.setStretchFactor(0, 1)
        self.ui.splitter.setStretchFactor(1, 3)

        self.ui.splitter.setCollapsible(0, False)
        self.ui.splitter.setCollapsible(1, False)

    def eventFilter(self, obj, event):
        # принимаем dragEnter и dragMove только для смены курсора
        if obj in self.viewports:
            if isinstance(event, QDragEnterEvent) and event.mimeData().hasUrls():
                event.acceptProposedAction()
                return True
            if isinstance(event, QDragMoveEvent) and event.mimeData().hasUrls():
                event.acceptProposedAction()
                return True
            # загрузка только при drop (отпускании мыши)
            if isinstance(event, QDropEvent) and event.mimeData().hasUrls():
                kind = self.viewports[obj]
                view = getattr(self.ui, f"{kind}preview")
                for url in event.mimeData().urls():
                    path = Path(url.toLocalFile())
                    if path.is_file():
                        self.load_image_path(kind, view, path)
                        break
                event.acceptProposedAction()
                return True
        return super().eventFilter(obj, event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.schedule_preview_update()

    def schedule_preview_update(self):
        if not self.resize_pending:
            self._debounce_timer.start(self.refresh_time)
            self.resize_pending = True

    def render_all_previews(self):
        self.resize_pending = False
        for kind, scene in self.scenes.items():
            view = getattr(self.ui, f"{kind}preview")
            img = self.pil_images.get(kind) if kind in self.KINDS else self._last_result
            if img:
                self._show_preview(img, view, kind)

    def load_image_dialog(self, kind: str, view: QtWidgets.QGraphicsView):
        path_str, _ = QFileDialog.getOpenFileName(
            self, "Выбрать изображение", str(self.last_dir), "Images (*.png *.jpg *.jpeg)"
        )
        if path_str:
            self.load_image_path(kind, view, Path(path_str))

    def load_image_path(self, kind: str, view: QtWidgets.QGraphicsView, path: Path):
        try:
            img = Image.open(path).convert("RGB")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить файл: {e}")
            return
        self.last_dir = path.parent
        self.pil_images[kind] = img
        self.image_paths[kind] = path
        self._show_preview(img, view, kind)
        self.try_update_result()

    def try_update_result(self):
        if self.image_paths['color'] and self.image_paths['outline']:
            self.update_result()

    def update_result(self) -> None:
        color = np.array(self.pil_images['color'])[:, :, ::-1]
        result = color.copy()
        if 'highlight' in self.pil_images:
            hl = np.array(self.pil_images['highlight'])[:, :, ::-1]
            result = ImageProcessor.apply_highlight(color, hl)
        ol = np.array(self.pil_images['outline'])[:, :, ::-1]
        result = ImageProcessor.apply_outline(result, ol)
        self._last_result = Image.fromarray(cv2.cvtColor(result, cv2.COLOR_BGR2RGB))
        self._show_preview(self._last_result, self.ui.resultpreview, 'result')

    def show_context_menu(self, pos, kind, view):
        menu = QtWidgets.QMenu(view)
        action = menu.addAction("Удалить изображение")
        if menu.exec(view.mapToGlobal(pos)) == action:
            self.clear_image(kind)

    def clear_image(self, kind: str):
        self.pil_images.pop(kind, None)
        self.image_paths[kind] = None
        self.scenes[kind].clear()
        getattr(self.ui, f"{kind}preview").resetTransform()
        if self.image_paths['color'] and self.image_paths['outline']:
            self.update_result()
        else:
            self._last_result = None
            self.scenes['result'].clear()

    def _show_preview(self, pil_img: Image.Image, view: QtWidgets.QGraphicsView, kind: str) -> None:
        orig_w, orig_h = pil_img.size
        dpr = view.devicePixelRatioF() or 1.0
        vw, vh = int(view.viewport().width()*dpr), int(view.viewport().height()*dpr)
        scale = min(vw/orig_w, vh/orig_h)
        preview = pil_img.resize((int(orig_w*scale), int(orig_h*scale)), Image.LANCZOS)
        qim = pil_to_qimage(preview)
        pix = QPixmap.fromImage(qim)
        pix.setDevicePixelRatio(dpr)
        scene = self.scenes[kind]
        scene.clear(); scene.addPixmap(pix); scene.setSceneRect(pix.rect().toRectF())
        view.resetTransform()
        

    def save_result(self) -> None:
        if self._last_result is None:
            QMessageBox.warning(self, "Ошибка", "Необходимо добавить цвет и контур")
            return
        default = self.image_paths['color'].with_suffix('.jpg') if self.image_paths['color'] else Path.cwd()/ 'result.jpg'
        save_str, _ = QFileDialog.getSaveFileName(self, "Сохранить результат", str(default), "JPEG (*.jpg);;PNG (*.png)")
        if save_str:
            out = Path(save_str); fmt = 'PNG' if out.suffix.lower()=='.png' else 'JPEG'
            self._last_result.save(out, format=fmt, quality=self.DEFAULT_QUALITY, subsampling=0, dpi=self.DEFAULT_DPI)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    icon_file = resource_path("icon.ico")
    app.setWindowIcon(QtGui.QIcon(str(icon_file)))

    app.setStyle("Fusion")
    window = ImageMergeApp()
    window.setWindowTitle("Image Merger")
    window.setWindowIcon(QtGui.QIcon(str(icon_file)))
    window.show()
    sys.exit(app.exec())
