from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from pathlib import Path
from uuid import uuid4

from PySide6.QtCore import QObject, QPoint, QRect, Signal
from PySide6.QtGui import QGuiApplication

from core.capture import ScreenCapture
from core.config import load_or_create_user_config, save_config
from core.hotkey import HotkeyListener
from core.text_process import normalize_text
from plugins.manager import TranslatorManager
from services.ocr_engine import WechatOCRService
from ui.overlay import CaptureOverlay
from ui.result_window import ResultWindow


class Kernel(QObject):
    _request_start_signal = Signal(object)
    _translation_update_signal = Signal(object)
    _copy_ocr_signal = Signal(str)
    _hotkey_signal = Signal()

    def __init__(self, base_dir: Path):
        super().__init__()
        self.base_dir = base_dir
        default_config_path = self.base_dir / "config.default.yaml"
        self.config, self.config_path = load_or_create_user_config(default_config_path)

        self.capture = ScreenCapture(self.base_dir / ".tmp")
        self.overlay = CaptureOverlay()
        self.result = ResultWindow()

        plugin_dir = self._resolve_plugin_dir(self.config.get("ocr", {}).get("plugin_dir", "../WechatOCR_umi_plugin_full"))
        self.ocr_service = WechatOCRService(
            plugin_dir=plugin_dir,
            wechat_ocr_dir=self.config["ocr"].get("wechat_ocr_dir", ""),
            wechat_dir=self.config["ocr"].get("wechat_dir", ""),
        )

        self.translators = TranslatorManager(self.config["translation"]).build_all()
        self.ocr_executor = ThreadPoolExecutor(max_workers=3, thread_name_prefix="bob-ocr")
        self.translation_executor = ThreadPoolExecutor(max_workers=12, thread_name_prefix="bob-trans")
        self.hotkey = HotkeyListener(self.config["app"].get("hotkey", "alt+d"), self._on_hotkey)

        self.overlay.selectionFinished.connect(self._on_selection_finished)
        self._request_start_signal.connect(self.result.start_request)
        self._translation_update_signal.connect(self.result.update_translation)
        self._copy_ocr_signal.connect(self._copy_ocr_to_clipboard)
        self._hotkey_signal.connect(self._open_overlay)

    def _copy_ocr_to_clipboard(self, text: str):
        clipboard = QGuiApplication.clipboard()
        if clipboard is not None:
            clipboard.setText(text or "")

    def _resolve_plugin_dir(self, configured_path: str) -> Path:
        candidates = []
        if configured_path:
            candidates.append((self.base_dir / configured_path).resolve())

        candidates.append((self.base_dir / "../WechatOCR_umi_plugin_full").resolve())
        candidates.append((self.base_dir / "WechatOCR_umi_plugin_full").resolve())

        for candidate in candidates:
            if (candidate / "WechatOCR_api.py").exists():
                return candidate

        raise RuntimeError("未找到 WechatOCR_umi_plugin_full 目录，请检查配置")

    def start(self):
        self.ocr_service.start()
        self.hotkey.start()

    def stop(self):
        self.hotkey.stop()
        self.ocr_executor.shutdown(wait=False)
        self.translation_executor.shutdown(wait=False)
        self.ocr_service.stop()

    def _on_hotkey(self):
        self._hotkey_signal.emit()

    def _open_overlay(self):
        self.result.hide()
        background = self.capture.capture_fullscreen_pixmap()
        self.overlay.start(background)

    def _on_selection_finished(self, rect: QRect, anchor: QPoint):
        request_id = uuid4().hex
        future = self.ocr_executor.submit(self._ocr_stage, rect)

        def done_callback(f):
            try:
                ocr_text = f.result()
            except Exception as exc:
                self._request_start_signal.emit(
                    {
                        "request_id": request_id,
                        "anchor": anchor,
                        "ocr_text": f"OCR失败：{exc}",
                        "providers": [],
                    }
                )
                return

            providers = [provider.name for provider in self.translators]
            self._request_start_signal.emit(
                {
                    "request_id": request_id,
                    "anchor": anchor,
                    "ocr_text": ocr_text or "未识别到文本",
                    "providers": providers,
                }
            )
            self._copy_ocr_signal.emit(ocr_text or "")

            if not ocr_text:
                return

            source_lang = self.config["translation"].get("source_lang", "auto")
            target_lang = self.config["translation"].get("target_lang", "zh-CN")
            for provider in self.translators:
                self.translation_executor.submit(
                    self._translate_stage,
                    request_id,
                    provider,
                    ocr_text,
                    source_lang,
                    target_lang,
                )

        future.add_done_callback(done_callback)

    def _ocr_stage(self, rect: QRect) -> str:
        image_path = self.capture.save_region(rect, self.overlay.size())
        ocr_text = self.ocr_service.recognize(image_path)
        clean_text = normalize_text(ocr_text)
        return clean_text

    def _translate_stage(self, request_id: str, provider, text: str, source_lang: str, target_lang: str):
        provider_name = provider.name

        try:
            if provider.supports_stream():
                def on_delta(delta: str):
                    self._translation_update_signal.emit(
                        {
                            "request_id": request_id,
                            "provider": provider_name,
                            "mode": "append",
                            "text": delta,
                            "done": False,
                        }
                    )

                final_text = provider.translate_stream(text, source_lang, target_lang, on_delta)
                if final_text:
                    self._translation_update_signal.emit(
                        {
                            "request_id": request_id,
                            "provider": provider_name,
                            "mode": "replace",
                            "text": final_text,
                            "done": True,
                        }
                    )
                else:
                    self._translation_update_signal.emit(
                        {
                            "request_id": request_id,
                            "provider": provider_name,
                            "mode": "replace",
                            "text": "",
                            "done": True,
                        }
                    )
                return

            translated = provider.translate(text=text, source_lang=source_lang, target_lang=target_lang)
            self._translation_update_signal.emit(
                {
                    "request_id": request_id,
                    "provider": provider_name,
                    "mode": "replace",
                    "text": translated,
                    "done": True,
                }
            )
        except Exception as exc:
            self._translation_update_signal.emit(
                {
                    "request_id": request_id,
                    "provider": provider_name,
                    "mode": "replace",
                    "text": f"翻译失败：{exc}",
                    "done": True,
                    "error": True,
                }
            )

    def apply_settings(self, new_config: dict):
        self.config = deepcopy(new_config)
        save_config(self.config_path, self.config)

        self.hotkey.stop()
        self.hotkey = HotkeyListener(self.config.get("app", {}).get("hotkey", "alt+d"), self._on_hotkey)
        self.hotkey.start()

        self.translators = TranslatorManager(self.config.get("translation", {})).build_all()
