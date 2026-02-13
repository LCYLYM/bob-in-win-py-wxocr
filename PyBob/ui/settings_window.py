from __future__ import annotations

from copy import deepcopy
import yaml

from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)


class SettingsDialog(QDialog):
    def __init__(self, config: dict, on_save):
        super().__init__()
        self.setWindowTitle("Bob 设置")
        self.setMinimumWidth(520)
        self._on_save = on_save
        self._config = deepcopy(config)

        root = QVBoxLayout(self)

        basic_group = QGroupBox("基础")
        basic_form = QFormLayout(basic_group)
        self.hotkey = QLineEdit(self._config.get("app", {}).get("hotkey", "alt+d"))
        self.source_lang = QLineEdit(self._config.get("translation", {}).get("source_lang", "auto"))
        self.target_lang = QLineEdit(self._config.get("translation", {}).get("target_lang", "zh-CN"))
        providers = self._config.get("translation", {}).get("providers")
        if not providers:
            providers = [self._config.get("translation", {}).get("provider", "google")]

        providers_row = QHBoxLayout()
        self.chk_google = QCheckBox("Google")
        self.chk_microsoft = QCheckBox("Microsoft")
        self.chk_openai = QCheckBox("OpenAI")
        self.chk_google.setChecked("google" in [p.lower() for p in providers])
        self.chk_microsoft.setChecked("microsoft" in [p.lower() for p in providers])
        self.chk_openai.setChecked("openai" in [p.lower() for p in providers])
        providers_row.addWidget(self.chk_google)
        providers_row.addWidget(self.chk_microsoft)
        providers_row.addWidget(self.chk_openai)
        providers_row.addStretch(1)

        basic_form.addRow("快捷键", self.hotkey)
        basic_form.addRow("翻译引擎", providers_row)
        basic_form.addRow("源语言", self.source_lang)
        basic_form.addRow("目标语言", self.target_lang)
        root.addWidget(basic_group)

        openai_group = QGroupBox("OpenAI")
        openai_form = QFormLayout(openai_group)
        openai_cfg = self._config.get("translation", {}).get("openai", {})
        self.openai_key = QLineEdit(openai_cfg.get("api_key", ""))
        self.openai_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.openai_base = QLineEdit(openai_cfg.get("base_url", "https://api.openai.com/v1"))
        self.openai_model = QLineEdit(openai_cfg.get("model", "gpt-4o-mini"))
        self.openai_system_prompt = QTextEdit(openai_cfg.get("system_prompt", "你是专业翻译引擎。只输出翻译后的文本，不要解释。保持原文语气和格式。"))
        self.openai_system_prompt.setMinimumHeight(72)

        profiles = openai_cfg.get("profiles", [])
        profiles_text = yaml.safe_dump(profiles, allow_unicode=True, sort_keys=False).strip() if profiles else "[]"
        self.openai_profiles = QTextEdit(profiles_text)
        self.openai_profiles.setPlaceholderText("YAML list, 例如:\n- name: gpt-4o-mini\n  enabled: true\n  model: gpt-4o-mini\n  base_url: https://api.openai.com/v1\n  api_key: ''\n  system_prompt: 你是专业翻译引擎")
        self.openai_profiles.setMinimumHeight(120)

        openai_form.addRow("API Key", self.openai_key)
        openai_form.addRow("Base URL", self.openai_base)
        openai_form.addRow("Model", self.openai_model)
        openai_form.addRow("System Prompt", self.openai_system_prompt)
        openai_form.addRow("Profiles(YAML)", self.openai_profiles)
        root.addWidget(openai_group)

        ms_group = QGroupBox("Microsoft Translator")
        ms_form = QFormLayout(ms_group)
        ms_cfg = self._config.get("translation", {}).get("microsoft", {})
        self.ms_key = QLineEdit(ms_cfg.get("subscription_key", ""))
        self.ms_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.ms_region = QLineEdit(ms_cfg.get("region", ""))
        self.ms_endpoint = QLineEdit(ms_cfg.get("endpoint", "https://api.cognitive.microsofttranslator.com"))
        ms_form.addRow("Subscription Key", self.ms_key)
        ms_form.addRow("Region", self.ms_region)
        ms_form.addRow("Endpoint", self.ms_endpoint)
        root.addWidget(ms_group)

        google_group = QGroupBox("Google Cloud Translation")
        google_form = QFormLayout(google_group)
        google_cfg = self._config.get("translation", {}).get("google", {})
        self.google_key = QLineEdit(google_cfg.get("api_key", ""))
        self.google_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.google_endpoint = QLineEdit(google_cfg.get("endpoint", "https://translation.googleapis.com/language/translate/v2"))
        google_form.addRow("API Key", self.google_key)
        google_form.addRow("Endpoint", self.google_endpoint)
        root.addWidget(google_group)

        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        cancel_btn = QPushButton("取消")
        save_btn = QPushButton("保存")
        cancel_btn.clicked.connect(self.reject)
        save_btn.clicked.connect(self._save)
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(save_btn)
        root.addLayout(btn_row)

    def _save(self):
        new_cfg = deepcopy(self._config)
        new_cfg.setdefault("app", {})
        new_cfg.setdefault("translation", {})
        new_cfg["app"]["hotkey"] = self.hotkey.text().strip() or "alt+d"

        trans = new_cfg["translation"]
        selected = []
        if self.chk_google.isChecked():
            selected.append("google")
        if self.chk_microsoft.isChecked():
            selected.append("microsoft")
        if self.chk_openai.isChecked():
            selected.append("openai")
        if not selected:
            selected = ["google"]

        trans["providers"] = selected
        trans["provider"] = selected[0]
        trans["source_lang"] = self.source_lang.text().strip() or "auto"
        trans["target_lang"] = self.target_lang.text().strip() or "zh-CN"

        trans.setdefault("openai", {})
        trans["openai"]["api_key"] = self.openai_key.text().strip()
        trans["openai"]["base_url"] = self.openai_base.text().strip() or "https://api.openai.com/v1"
        trans["openai"]["model"] = self.openai_model.text().strip() or "gpt-4o-mini"
        trans["openai"]["system_prompt"] = self.openai_system_prompt.toPlainText().strip() or "你是专业翻译引擎。只输出翻译后的文本，不要解释。保持原文语气和格式。"

        raw_profiles = self.openai_profiles.toPlainText().strip() or "[]"
        try:
            parsed_profiles = yaml.safe_load(raw_profiles)
            if parsed_profiles is None:
                parsed_profiles = []
            if not isinstance(parsed_profiles, list):
                raise ValueError("Profiles 必须是 YAML 列表")
        except Exception as exc:
            raise ValueError(f"OpenAI Profiles YAML 解析失败: {exc}")
        trans["openai"]["profiles"] = parsed_profiles

        trans.setdefault("microsoft", {})
        trans["microsoft"]["subscription_key"] = self.ms_key.text().strip()
        trans["microsoft"]["region"] = self.ms_region.text().strip()
        trans["microsoft"]["endpoint"] = self.ms_endpoint.text().strip() or "https://api.cognitive.microsofttranslator.com"

        trans.setdefault("google", {})
        trans["google"]["api_key"] = self.google_key.text().strip()
        trans["google"]["endpoint"] = self.google_endpoint.text().strip() or "https://translation.googleapis.com/language/translate/v2"

        try:
            self._on_save(new_cfg)
        except Exception as exc:
            QMessageBox.critical(self, "保存失败", str(exc))
            return

        self.accept()
