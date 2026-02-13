@echo off
@chcp 65001
setlocal

set ROOT=%~dp0
cd /d %ROOT%

echo [1/4] 清理旧构建目录...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist bob_win_py.spec del /q bob_win_py.spec

echo [2/4] 安装打包依赖...
python -m pip install --user pyinstaller
if errorlevel 1 (
  echo [ERROR] 安装 PyInstaller 失败。
  exit /b 1
)

set PYI_CMD=python -m PyInstaller
python -c "import PyInstaller" >nul 2>nul
if errorlevel 1 (
  if exist "%APPDATA%\Python\Python313\Scripts\pyinstaller.exe" (
    set PYI_CMD="%APPDATA%\Python\Python313\Scripts\pyinstaller.exe"
  ) else (
    echo [ERROR] 找不到 PyInstaller 入口。请检查 Python 用户脚本目录是否可用。
    exit /b 1
  )
)

echo [3/4] 构建单文件 EXE（含 OCR 模型）...
%PYI_CMD% --noconfirm --clean --onefile --windowed ^
  --name bob_win_py ^
  --exclude-module PyQt5 ^
  --exclude-module PyQt5.QtCore ^
  --exclude-module PyQt5.QtGui ^
  --exclude-module PyQt5.QtWidgets ^
  --exclude-module PyQt6 ^
  --exclude-module PySide2 ^
  --add-data "PyBob\config.default.yaml;." ^
  --add-data "WechatOCR_umi_plugin_full;WechatOCR_umi_plugin_full" ^
  PyBob\main.py

if errorlevel 1 (
  echo [ERROR] 打包失败，请查看上面的错误日志。
  exit /b 1
)

echo [4/4] 完成，输出：dist\bob_win_py.exe
echo 首次运行会在 %%APPDATA%%\PyBob\config.yaml 自动生成默认配置。

endlocal
