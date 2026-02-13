from __future__ import annotations

import json

import httpx

from plugins.base import TranslationProvider


class OpenAITranslator(TranslationProvider):
    def __init__(
        self,
        api_key: str,
        base_url: str,
        model: str,
        system_prompt: str,
        provider_name: str = "openai",
        timeout_seconds: float = 20.0,
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.system_prompt = system_prompt
        self.provider_name = provider_name
        self.timeout_seconds = timeout_seconds

    @property
    def name(self) -> str:
        return self.provider_name

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        if not self.api_key:
            raise ValueError("OpenAI API key 未配置")

        user_prompt = (
            f"将下面文本从 {source_lang or 'auto'} 翻译为 {target_lang}：\n\n{text}"
        )

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.2,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        url = f"{self.base_url}/chat/completions"

        with httpx.Client(timeout=self.timeout_seconds) as client:
            response = client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

        return data["choices"][0]["message"]["content"].strip()

    def supports_stream(self) -> bool:
        return True

    def translate_stream(self, text: str, source_lang: str, target_lang: str, on_delta) -> str:
        if not self.api_key:
            raise ValueError("OpenAI API key 未配置")

        user_prompt = f"将下面文本从 {source_lang or 'auto'} 翻译为 {target_lang}：\n\n{text}"

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.2,
            "stream": True,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        url = f"{self.base_url}/chat/completions"

        chunks = []
        timeout = httpx.Timeout(connect=10.0, read=60.0, write=20.0, pool=10.0)
        with httpx.Client(timeout=timeout) as client:
            with client.stream("POST", url, json=payload, headers=headers) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if not line:
                        continue
                    if not line.startswith("data:"):
                        continue

                    data_text = line[5:].strip()
                    if data_text == "[DONE]":
                        break

                    try:
                        data = json.loads(data_text)
                    except json.JSONDecodeError:
                        continue

                    choices = data.get("choices") or []
                    if not choices:
                        continue
                    delta = (choices[0].get("delta") or {}).get("content")
                    if delta:
                        chunks.append(delta)
                        on_delta(delta)

        return "".join(chunks).strip()
