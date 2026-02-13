from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QRect, QSize
from PySide6.QtGui import QGuiApplication, QPixmap


class ScreenCapture:
    def __init__(self, temp_dir: Path):
        self.temp_dir = temp_dir
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self._last_fullscreen = QPixmap()

    def capture_fullscreen_pixmap(self) -> QPixmap:
        screen = QGuiApplication.primaryScreen()
        if screen is None:
            raise RuntimeError("无法获取主屏幕")
        self._last_fullscreen = screen.grabWindow(0)
        return self._last_fullscreen

    def save_region(self, rect: QRect, view_size: QSize, filename: str = "capture.png") -> Path:
        if self._last_fullscreen.isNull():
            self.capture_fullscreen_pixmap()

        if view_size.width() <= 0 or view_size.height() <= 0:
            raise RuntimeError("无效的预览尺寸")

        sx = self._last_fullscreen.width() / view_size.width()
        sy = self._last_fullscreen.height() / view_size.height()

        left = max(0, int(round(rect.left() * sx)))
        top = max(0, int(round(rect.top() * sy)))
        width = max(1, int(round(rect.width() * sx)))
        height = max(1, int(round(rect.height() * sy)))

        output = self.temp_dir / filename
        region = QRect(left, top, width, height)
        cropped = self._last_fullscreen.copy(region)
        if not cropped.save(str(output), "PNG"):
            raise RuntimeError("截图保存失败")
        return output
