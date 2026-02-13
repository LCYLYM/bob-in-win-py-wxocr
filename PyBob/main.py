import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from core.kernel import Kernel
from ui.settings_window import SettingsDialog
from ui.tray_controller import TrayController


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("bob_win_py")
    app.setQuitOnLastWindowClosed(False)

    base_dir = Path(__file__).resolve().parent
    kernel = Kernel(base_dir=base_dir)
    settings_dialog = None

    def open_settings():
        nonlocal settings_dialog

        if settings_dialog is not None and settings_dialog.isVisible():
            settings_dialog.raise_()
            settings_dialog.activateWindow()
            return

        settings_dialog = SettingsDialog(kernel.config, on_save=kernel.apply_settings)
        settings_dialog.finished.connect(lambda _: setattr_holder())
        settings_dialog.open()

    def setattr_holder():
        nonlocal settings_dialog
        settings_dialog = None

    tray = TrayController(app, on_open_settings=open_settings, on_exit=app.quit)
    tray.show()

    app.aboutToQuit.connect(kernel.stop)
    app.aboutToQuit.connect(tray.hide)
    kernel.start()
    try:
        return app.exec()
    finally:
        kernel.stop()


if __name__ == "__main__":
    raise SystemExit(main())
