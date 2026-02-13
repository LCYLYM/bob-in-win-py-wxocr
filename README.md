# bob-in-win-py-wxocr

这是 **Win 下的 bob**（个人尝试-高响应）：基于 Python 的 Windows 截屏翻译工具，支持热键截图、OCR 识别和多翻译引擎并行翻译。

主要就是做一件事——截图ocr翻译，有预加载保证截图和相应速度，体验还是蛮跟手的，好用。wxocr也好用（别商用，个人玩就好）
后续慢慢改吧hhh
<img width="700" height="574" alt="image" src="https://github.com/user-attachments/assets/83879daa-efbd-47ee-adb9-be6ca10feab4" />

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

本仓库不包含私有配置。

- 模板：`PyBob/config.default.yaml`
- 运行时用户配置：`%APPDATA%/PyBob/config.yaml`

## Release（下载 EXE）

`bob_win_py.exe`  Release  中提供下载。

## 鸣谢

- 模型与插件基础来自：
  - https://github.com/eaeful/WechatOCR_umi_plugin

感谢原项目提供模型与实现基础。
