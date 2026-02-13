from __future__ import annotations

import keyboard
from pynput import keyboard as pynput_keyboard


class HotkeyListener:
    def __init__(self, hotkey: str, callback):
        self.hotkey = hotkey
        self.callback = callback
        self._hotkey_handler = None
        self._pynput_listener = None
        self._backend = None

    @staticmethod
    def _to_pynput_hotkey(hotkey: str) -> str:
        key = hotkey.lower().replace(" ", "")
        key = key.replace("ctrl", "<ctrl>")
        key = key.replace("alt", "<alt>")
        key = key.replace("shift", "<shift>")
        key = key.replace("win", "<cmd>")
        return key

    def start(self):
        if self._backend is not None:
            return

        pynput_hotkey = self._to_pynput_hotkey(self.hotkey)
        try:
            self._pynput_listener = pynput_keyboard.GlobalHotKeys({pynput_hotkey: self.callback})
            self._pynput_listener.start()
            self._backend = "pynput"
            print(f"[Hotkey] 已注册 ({self._backend}): {self.hotkey}")
            return
        except Exception as exc:
            print(f"[Hotkey] pynput 注册失败，回退 keyboard: {exc}")

        self._hotkey_handler = keyboard.add_hotkey(self.hotkey, self.callback)
        self._backend = "keyboard"
        print(f"[Hotkey] 已注册 ({self._backend}): {self.hotkey}")

    def stop(self):
        if self._backend == "pynput" and self._pynput_listener is not None:
            self._pynput_listener.stop()
            self._pynput_listener = None
            self._backend = None
            return

        if self._backend == "keyboard" and self._hotkey_handler is not None:
            keyboard.remove_hotkey(self._hotkey_handler)
            self._hotkey_handler = None
            self._backend = None
