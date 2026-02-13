from __future__ import annotations

from plugins.base import TranslationProvider
from plugins.google_api import GoogleTranslator
from plugins.microsoft_api import MicrosoftTranslator
from plugins.openai_api import OpenAITranslator


DEFAULT_OPENAI_SYSTEM_PROMPT = "你是专业翻译引擎。只输出翻译后的文本，不要解释。保持原文语气和格式。"


class TranslatorManager:
    def __init__(self, config: dict):
        self.config = config

    def _build_one(self, provider: str) -> TranslationProvider:
        provider = (provider or "google").lower()
        if provider == "openai":
            c = self.config.get("openai", {})
            return OpenAITranslator(
                api_key=c.get("api_key", ""),
                base_url=c.get("base_url", "https://api.openai.com/v1"),
                model=c.get("model", "gpt-4o-mini"),
                system_prompt=c.get("system_prompt", DEFAULT_OPENAI_SYSTEM_PROMPT),
                provider_name="openai",
            )
        if provider == "microsoft":
            c = self.config.get("microsoft", {})
            return MicrosoftTranslator(
                subscription_key=c.get("subscription_key", ""),
                region=c.get("region", ""),
                endpoint=c.get("endpoint", "https://api.cognitive.microsofttranslator.com"),
            )
        c = self.config.get("google", {})
        return GoogleTranslator(
            api_key=c.get("api_key", ""),
            endpoint=c.get("endpoint", "https://translation.googleapis.com/language/translate/v2"),
        )

    def build(self) -> TranslationProvider:
        providers = self.build_all()
        return providers[0]

    def build_all(self) -> list[TranslationProvider]:
        providers = self.config.get("providers")
        if not providers:
            providers = [self.config.get("provider", "google")]

        unique = []
        seen = set()
        for item in providers:
            name = (item or "").strip().lower()
            if not name or name in seen:
                continue
            seen.add(name)
            unique.append(name)

        if not unique:
            unique = ["google"]

        built: list[TranslationProvider] = []
        openai_cfg = self.config.get("openai", {})

        for name in unique:
            if name != "openai":
                built.append(self._build_one(name))
                continue

            profiles = openai_cfg.get("profiles", [])
            if isinstance(profiles, list) and profiles:
                for idx, p in enumerate(profiles, start=1):
                    if not isinstance(p, dict):
                        continue
                    if p.get("enabled", True) is False:
                        continue

                    profile_name = (p.get("name") or f"openai-{idx}").strip()
                    built.append(
                        OpenAITranslator(
                            api_key=p.get("api_key", openai_cfg.get("api_key", "")),
                            base_url=p.get("base_url", openai_cfg.get("base_url", "https://api.openai.com/v1")),
                            model=p.get("model", openai_cfg.get("model", "gpt-4o-mini")),
                            system_prompt=p.get("system_prompt", openai_cfg.get("system_prompt", DEFAULT_OPENAI_SYSTEM_PROMPT)),
                            provider_name=f"openai:{profile_name}",
                        )
                    )
            else:
                built.append(self._build_one("openai"))

        return built
