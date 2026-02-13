from __future__ import annotations

import json
import sys
import threading
from pathlib import Path


def main():
    base_dir = Path(__file__).resolve().parent
    plugin_dir = (base_dir / "../WechatOCR_umi_plugin_full").resolve()
    image_path = (base_dir.parent / "ocr测试图片.png").resolve()

    sys.path.insert(0, str(plugin_dir / "third_party_libs"))
    from wechat_ocr.ocr_manager import OcrManager

    done = threading.Event()
    box = {"result": None}

    def cb(img_path: str, result: dict):
        box["result"] = result
        done.set()

    manager = OcrManager(str(plugin_dir / "path"))
    manager.SetExePath(str(plugin_dir / "path" / "WeChatOCR" / "WeChatOCR.exe"))
    manager.SetUsrLibDir(str(plugin_dir / "path"))
    manager.SetOcrResultCallback(cb)
    manager.StartWeChatOCR()

    try:
        manager.DoOCRTask(str(image_path))
        if not done.wait(timeout=15):
            raise TimeoutError("OCR callback timeout")
        raw = box["result"]
        print("[RAW OCR RESULT KEYS]", list(raw.keys()))
        print("[FIRST ITEM KEYS]", list((raw.get("ocrResult") or [{}])[0].keys()))
        print("[RAW OCR JSON]")
        print(json.dumps(raw, ensure_ascii=False, indent=2)[:6000])
    finally:
        manager.KillWeChatOCR()


if __name__ == "__main__":
    main()
