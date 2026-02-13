from __future__ import annotations

import httpx

from plugins.base import TranslationProvider


class MicrosoftTranslator(TranslationProvider):
    def __init__(
        self,
        subscription_key: str,
        region: str,
        endpoint: str = "https://api.cognitive.microsofttranslator.com",
        timeout_seconds: float = 20.0,
    ):
        self.subscription_key = subscription_key
        self.region = region
        self.endpoint = endpoint.rstrip("/")
        self.timeout_seconds = timeout_seconds

    @property
    def name(self) -> str:
        return "microsoft"

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        if not self.subscription_key:
            raise ValueError("Microsoft Translator key 未配置")

        params = {
            "api-version": "3.0",
            "to": target_lang,
        }
        if source_lang and source_lang != "auto":
            params["from"] = source_lang

        headers = {
            "Ocp-Apim-Subscription-Key": self.subscription_key,
            "Ocp-Apim-Subscription-Region": self.region,
            "Content-Type": "application/json; charset=UTF-8",
        }
        body = [{"text": text}]
        url = f"{self.endpoint}/translate"

        with httpx.Client(timeout=self.timeout_seconds) as client:
            response = client.post(url, params=params, headers=headers, json=body)
            response.raise_for_status()
            data = response.json()

        return data[0]["translations"][0]["text"].strip()
