from __future__ import annotations

import argparse
from pathlib import Path

import mss
import mss.tools

from services.ocr_engine import WechatOCRService


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", type=str, default="", help="指定测试图片路径")
    args = parser.parse_args()

    base_dir = Path(__file__).resolve().parent
    workspace_dir = base_dir.parent
    plugin_dir = (base_dir / "../WechatOCR_umi_plugin_full").resolve()
    temp_img = base_dir / ".tmp" / "ocr_test_capture.png"
    temp_img.parent.mkdir(parents=True, exist_ok=True)

    input_image = Path(args.image).resolve() if args.image else None
    default_image = workspace_dir / "ocr测试图片.png"

    if input_image and input_image.exists():
        image_to_test = input_image
    elif default_image.exists():
        image_to_test = default_image
    else:
        with mss.mss() as sct:
            monitor = {"left": 100, "top": 100, "width": 800, "height": 300}
            shot = sct.grab(monitor)
            mss.tools.to_png(shot.rgb, shot.size, output=str(temp_img))
        image_to_test = temp_img

    print(f"[OCR INPUT] {image_to_test}")

    ocr = WechatOCRService(plugin_dir=plugin_dir)
    ocr.start()
    try:
        text = ocr.recognize(image_to_test)
        print("[OCR RESULT]")
        print(text or "<empty>")
    finally:
        ocr.stop()


if __name__ == "__main__":
    main()
