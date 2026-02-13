from __future__ import annotations

from PySide6.QtCore import QPoint, QRect, Qt, Signal
from PySide6.QtGui import QColor, QGuiApplication, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QWidget


class CaptureOverlay(QWidget):
    selectionFinished = Signal(QRect, QPoint)
    canceled = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMouseTracking(True)

        self._background = QPixmap()
        self._preview = QPixmap()
        self._dragging = False
        self._start = QPoint()
        self._end = QPoint()

    def start(self, background: QPixmap):
        self._background = background
        self._dragging = False
        self._start = QPoint()
        self._end = QPoint()
        screen = QGuiApplication.primaryScreen()
        if screen is not None:
            self.setGeometry(screen.geometry())
        self._preview = self._background.scaled(
            self.size(),
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.showFullScreen()
        self.raise_()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.hide()
            self.canceled.emit()
            return
        super().keyPressEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            self._start = event.pos()
            self._end = event.pos()
            self.update()
            return
        if event.button() == Qt.MouseButton.RightButton:
            self.hide()
            self.canceled.emit()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._dragging:
            self._end = event.pos()
            self.update()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._dragging and event.button() == Qt.MouseButton.LeftButton:
            self._dragging = False
            self._end = event.pos()
            rect = QRect(self._start, self._end).normalized()
            self.hide()
            if rect.width() >= 8 and rect.height() >= 8:
                self.selectionFinished.emit(rect, event.globalPosition().toPoint())
            else:
                self.canceled.emit()
            return
        super().mouseReleaseEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        if not self._preview.isNull():
            painter.drawPixmap(self.rect(), self._preview)

        painter.fillRect(self.rect(), QColor(0, 0, 0, 120))

        rect = QRect(self._start, self._end).normalized()
        if rect.width() > 0 and rect.height() > 0:
            painter.drawPixmap(rect, self._preview, rect)
            painter.setPen(QPen(QColor(0, 180, 255), 2))
            painter.drawRect(rect)

        painter.end()
