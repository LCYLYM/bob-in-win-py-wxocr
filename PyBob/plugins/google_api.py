from __future__ import annotations

import httpx

from plugins.base import TranslationProvider


class GoogleTranslator(TranslationProvider):
    def __init__(self, api_key: str, endpoint: str = "https://translation.googleapis.com/language/translate/v2", timeout_seconds: float = 20.0):
        self.api_key = api_key
        self.endpoint = endpoint.rstrip("/")
        self.timeout_seconds = timeout_seconds

    @property
    def name(self) -> str:
        return "google"

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        if not self.api_key:
            return self._translate_unofficial(text, source_lang, target_lang)

        params = {
            "key": self.api_key,
            "q": text,
            "target": target_lang,
            "format": "text",
        }
        if source_lang and source_lang != "auto":
            params["source"] = source_lang

        with httpx.Client(timeout=self.timeout_seconds) as client:
            response = client.post(self.endpoint, params=params)
            response.raise_for_status()
            data = response.json()

        translations = data.get("data", {}).get("translations", [])
        if not translations:
            raise RuntimeError("Google 翻译返回为空")
        return (translations[0].get("translatedText") or "").strip()

    def _translate_unofficial(self, text: str, source_lang: str, target_lang: str) -> str:
        params = {
            "client": "gtx",
            "sl": source_lang if source_lang and source_lang != "auto" else "auto",
            "tl": target_lang,
            "dt": "t",
            "q": text,
        }
        url = "https://translate.googleapis.com/translate_a/single"

        with httpx.Client(timeout=self.timeout_seconds) as client:
            response = client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

        if not isinstance(data, list) or not data or not isinstance(data[0], list):
            raise RuntimeError("Google 非官方翻译返回结构异常")

        parts = []
        for seg in data[0]:
            if isinstance(seg, list) and seg and isinstance(seg[0], str):
                parts.append(seg[0])
        result = "".join(parts).strip()
        if not result:
            raise RuntimeError("Google 非官方翻译返回为空")
        return result
