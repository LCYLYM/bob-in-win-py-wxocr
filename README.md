# bob-in-win-py-wxocr

这是 **Win 下的 bob**：基于 Python 的 Windows 截屏翻译工具，支持热键截图、OCR 识别和多翻译引擎并行翻译。

## 功能

- 全局热键截图（默认 `Alt + D`）
- WeChat OCR 本地模型识别
- 多翻译引擎：`google / microsoft / openai`
- 结果窗口分引擎展示

## 仓库结构

- `PyBob/`：主程序源码
- `WechatOCR_umi_plugin_full/`：OCR 插件与模型
- `build_onefile.bat`：一键打包脚本
- `bob_win_py.spec`：PyInstaller 配置

## 运行（源码）

```powershell
cd PyBob
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

## 配置

本仓库不包含你的私有配置。

- 模板：`PyBob/config.default.yaml`
- 运行时用户配置：`%APPDATA%/PyBob/config.yaml`

## Release（下载 EXE）

`bob_win_py.exe` 不放进 Git 仓库（文件较大），在 GitHub Release 的 Assets 中提供下载。

## 鸣谢

- 模型与插件基础来自：
  - https://github.com/eaeful/WechatOCR_umi_plugin

感谢原项目提供模型与实现基础。
