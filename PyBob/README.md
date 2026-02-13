# bob_win_py (PyBob)

Windows 截屏翻译 MVP：
- 全局热键 `Alt + D`
- `mss` 截图 + 遮罩选区
- 本地 `WechatOCR_umi_plugin_full` 真调用 OCR
- 可并行 `google / microsoft / openai` 多翻译提供方
- 结果窗固定宽度，仅垂直滚动，分接口可折叠展示

## 快速开始

```powershell
cd PyBob
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

## 配置

运行后会自动在 `%APPDATA%/PyBob/config.yaml` 生成用户配置（不会使用打包前你的本地配置）。

默认模板在 `config.default.yaml`。

主要配置：
- `ocr.plugin_dir` 默认已指向上级目录的 `WechatOCR_umi_plugin_full`
- `translation.providers` 可同时配置多个引擎
- `openai` 采用 OpenAI 兼容 `chat/completions` 格式，支持自定义 `base_url`
- `microsoft` 采用 Translator Text API v3：`/translate?api-version=3.0`
- `google` 支持官方 Cloud Translation API（API key），以及无 key 非官方回退

## 打包为单 EXE（含 OCR 模型）

在仓库根目录执行：

```powershell
build_onefile.bat
```

输出文件：`dist/bob_win_py.exe`

## 已验证调用方式

OCR 使用插件真实调用链：
1. `Api(global_args)`
2. `start({})`
3. `runPath(image_path)`
4. `stop()`

这与 `WechatOCR_umi_plugin_full/WechatOCR_api.py` 的实际实现一致。
