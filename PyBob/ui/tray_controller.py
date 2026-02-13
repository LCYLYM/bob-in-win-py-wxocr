from __future__ import annotations

import time

from PySide6.QtCore import QObject
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QMenu, QStyle, QSystemTrayIcon


class TrayController(QObject):
    def __init__(self, app, on_open_settings, on_exit):
        super().__init__()
        style = app.style()
        icon = style.standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)

        self.tray = QSystemTrayIcon(icon)
        self.tray.setToolTip("Bob for Windows")

        menu = QMenu()
        self.settings_action = QAction("设置")
        self.quit_action = QAction("退出")
        menu.addAction(self.settings_action)
        menu.addSeparator()
        menu.addAction(self.quit_action)

        self.tray.setContextMenu(menu)
        self.settings_action.triggered.connect(on_open_settings)
        self.quit_action.triggered.connect(on_exit)
        self.tray.activated.connect(self._on_activated)
        self._open_settings = on_open_settings
        self._last_activate = 0.0

    def _on_activated(self, reason):
        now = time.monotonic()
        if now - self._last_activate < 0.35:
            return
        self._last_activate = now

        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self._open_settings()

    def show(self):
        self.tray.show()
        self.tray.showMessage("Bob", "已在后台运行，按快捷键开始截图翻译", QSystemTrayIcon.MessageIcon.Information, 1800)

    def hide(self):
        self.tray.hide()
