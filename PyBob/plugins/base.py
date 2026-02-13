from __future__ import annotations

from abc import ABC, abstractmethod


class TranslationProvider(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        raise NotImplementedError

    def supports_stream(self) -> bool:
        return False

    def translate_stream(self, text: str, source_lang: str, target_lang: str, on_delta) -> str:
        result = self.translate(text=text, source_lang=source_lang, target_lang=target_lang)
        if result:
            on_delta(result)
        return result
