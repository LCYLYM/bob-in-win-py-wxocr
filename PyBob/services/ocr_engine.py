from __future__ import annotations

import sys
import threading
import importlib
from pathlib import Path
from typing import Dict, Optional


class WechatOCRService:
    def __init__(self, plugin_dir: Path, wechat_ocr_dir: str = "", wechat_dir: str = ""):
        self.plugin_dir = plugin_dir
        self.wechat_ocr_dir = wechat_ocr_dir
        self.wechat_dir = wechat_dir
        self._ocr_manager = None
        self._results: Dict[str, dict] = {}
        self._events: Dict[str, threading.Event] = {}
        self._lock = threading.Lock()
        self._started = False

    def start(self):
        plugin_path = str(self.plugin_dir)
        if plugin_path not in sys.path:
            sys.path.insert(0, plugin_path)
        third_party_path = str(self.plugin_dir / "third_party_libs")
        if third_party_path not in sys.path:
            sys.path.insert(0, third_party_path)

        ocr_module = importlib.import_module("wechat_ocr.ocr_manager")
        OcrManager = getattr(ocr_module, "OcrManager")

        current_dir = self.plugin_dir
        default_wechat_ocr = current_dir / "path" / "WeChatOCR" / "WeChatOCR.exe"
        default_wechat_dir = current_dir / "path"

        exe_path = self.wechat_ocr_dir or str(default_wechat_ocr)
        usr_dir = self.wechat_dir or str(default_wechat_dir)

        self._ocr_manager = OcrManager(usr_dir)
        self._ocr_manager.SetExePath(exe_path)
        self._ocr_manager.SetUsrLibDir(usr_dir)
        self._ocr_manager.SetOcrResultCallback(self._ocr_callback)
        self._ocr_manager.StartWeChatOCR()
        self._started = True

    def _ocr_callback(self, img_path: str, results: dict):
        event = None
        with self._lock:
            self._results[img_path] = results
            event = self._events.get(img_path)
        if event is not None:
            event.set()

    def stop(self):
        if self._ocr_manager is not None:
            self._ocr_manager.KillWeChatOCR()
            self._ocr_manager = None
        self._started = False

    def recognize(self, image_path: Path) -> str:
        if not self._started or self._ocr_manager is None:
            raise RuntimeError("OCR 服务未启动")

        img_path = str(image_path.resolve())
        event = threading.Event()

        with self._lock:
            self._events[img_path] = event
            self._results.pop(img_path, None)

        try:
            self._ocr_manager.DoOCRTask(img_path)
            if not event.wait(timeout=12):
                raise RuntimeError("OCR 失败: 识别超时")

            with self._lock:
                result = self._results.pop(img_path, None)

            if result is None:
                raise RuntimeError("OCR 失败: 未返回结果")
        finally:
            with self._lock:
                self._events.pop(img_path, None)

        lines = []
        for item in result.get("ocrResult", []):
            text = (item.get("text") or "").strip()
            if text:
                lines.append(text)
        return "\n".join(lines)
