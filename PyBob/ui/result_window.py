from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QPushButton,
    QScrollArea,
    QTextEdit,
    QToolButton,
    QVBoxLayout,
    QWidget,
)


@dataclass
class SectionWidgets:
    container: QFrame
    toggle: QToolButton
    body: QTextEdit


class ResultWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.setMinimumWidth(560)
        self.setMaximumWidth(560)

        self.setStyleSheet(
            "QWidget#root {"
            "background: #111827;"
            "border: 1px solid #374151;"
            "border-radius: 12px;"
            "}"
            "QFrame.section {"
            "background: #1f2937;"
            "border: 1px solid #334155;"
            "border-radius: 10px;"
            "}"
            "QToolButton.sectionTitle {"
            "color: #f9fafb;"
            "font-size: 14px;"
            "font-weight: 700;"
            "background: transparent;"
            "border: none;"
            "padding: 6px 8px;"
            "text-align: left;"
            "}"
            "QPushButton#closeBtn {"
            "color: #e5e7eb;"
            "background: transparent;"
            "border: none;"
            "font-size: 16px;"
            "font-weight: 700;"
            "padding: 2px 6px;"
            "}"
            "QPushButton#closeBtn:hover {"
            "background: #374151;"
            "border-radius: 6px;"
            "}"
            "QTextEdit.sectionBody {"
            "background: #0b1220;"
            "color: #f9fafb;"
            "border: 1px solid #1f2937;"
            "border-radius: 8px;"
            "padding: 8px;"
            "font-size: 13px;"
            "}"
            "QScrollBar:vertical {"
            "background: transparent;"
            "width: 8px;"
            "margin: 6px 2px 6px 2px;"
            "}"
            "QScrollBar::handle:vertical {"
            "background: #64748b;"
            "min-height: 24px;"
            "border-radius: 4px;"
            "}"
            "QScrollBar::handle:vertical:hover {"
            "background: #94a3b8;"
            "}"
            "QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {"
            "height: 0px;"
            "}"
            "QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {"
            "background: transparent;"
            "}"
        )

        self.setObjectName("root")

        root = QVBoxLayout(self)
        root.setContentsMargins(10, 8, 10, 10)
        root.setSpacing(8)

        header = QHBoxLayout()
        header.addStretch(1)
        self.close_btn = QPushButton("×", self)
        self.close_btn.setObjectName("closeBtn")
        self.close_btn.setFixedSize(24, 24)
        self.close_btn.clicked.connect(self.hide)
        header.addWidget(self.close_btn)
        root.addLayout(header)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        root.addWidget(self.scroll_area)

        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setSpacing(8)
        self.scroll_layout.addStretch(1)
        self.scroll_area.setWidget(self.scroll_content)

        self._current_request_id = ""
        self._anchor = QPoint(40, 40)
        self._sections: dict[str, SectionWidgets] = {}

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.hide()
            return
        super().keyPressEvent(event)

    def focusOutEvent(self, event):
        self.hide()
        super().focusOutEvent(event)

    def _clear_sections(self):
        for sec in self._sections.values():
            sec.container.deleteLater()
        self._sections.clear()

    def _make_section(self, key: str, title: str) -> SectionWidgets:
        frame = QFrame(self.scroll_content)
        frame.setObjectName("section")
        frame.setProperty("class", "section")
        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(6, 6, 6, 6)
        frame_layout.setSpacing(6)

        toggle = QToolButton(frame)
        toggle.setObjectName("sectionTitle")
        toggle.setProperty("class", "sectionTitle")
        toggle.setText(title)
        toggle.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        toggle.setArrowType(Qt.ArrowType.DownArrow)
        toggle.setCheckable(True)
        toggle.setChecked(True)

        body = QTextEdit(frame)
        body.setObjectName("sectionBody")
        body.setProperty("class", "sectionBody")
        body.setReadOnly(True)
        body.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        body.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        body.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        body.setMinimumHeight(96)

        def on_toggle(checked: bool):
            body.setVisible(checked)
            toggle.setArrowType(Qt.ArrowType.DownArrow if checked else Qt.ArrowType.RightArrow)
            self._reposition()

        toggle.toggled.connect(on_toggle)

        frame_layout.addWidget(toggle)
        frame_layout.addWidget(body)

        self.scroll_layout.insertWidget(max(0, self.scroll_layout.count() - 1), frame)

        sec = SectionWidgets(container=frame, toggle=toggle, body=body)
        self._sections[key] = sec
        return sec

    def _reposition(self):
        self.resize(560, 460)
        screen = QGuiApplication.primaryScreen().availableGeometry()
        x = self._anchor.x() + 12
        y = self._anchor.y() + 12

        if x + self.width() > screen.right():
            x = self._anchor.x() - self.width() - 12
        if y + self.height() > screen.bottom():
            y = self._anchor.y() - self.height() - 12

        x = max(screen.left() + 8, x)
        y = max(screen.top() + 8, y)

        self.move(x, y)

    def start_request(self, payload: dict):
        self._current_request_id = payload.get("request_id", "")
        self._anchor = payload.get("anchor", QPoint(40, 40))
        self._clear_sections()

        ocr_text = payload.get("ocr_text", "")
        ocr_sec = self._make_section("ocr", "OCR")
        ocr_sec.body.setPlainText(ocr_text or "未识别到文本")
        ocr_sec.body.moveCursor(ocr_sec.body.textCursor().MoveOperation.Start)

        providers = payload.get("providers", [])
        for provider in providers:
            sec = self._make_section(provider, f"{provider}（进行中）")
            sec.body.setPlainText("...")

        self._reposition()
        self.show()
        self.raise_()

    def update_translation(self, payload: dict):
        request_id = payload.get("request_id", "")
        if request_id != self._current_request_id:
            return

        provider = payload.get("provider", "")
        if provider not in self._sections:
            sec = self._make_section(provider, f"{provider}（进行中）")
            sec.body.setPlainText("...")
        sec = self._sections[provider]

        mode = payload.get("mode", "replace")
        text = payload.get("text", "")
        if mode == "append":
            cursor = sec.body.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            cursor.insertText(text)
            sec.body.setTextCursor(cursor)
        else:
            sec.body.setPlainText(text)

        if payload.get("error"):
            status = "失败"
        elif payload.get("done"):
            status = "完成"
        else:
            status = "进行中"
        sec.toggle.setText(f"{provider}（{status}）")

        if payload.get("error"):
            sec.toggle.setChecked(False)
