@echo off
chcp 65001 >nul
echo ============================================================
echo SceneWeaver 打包脚本
echo ============================================================
echo.

echo [1/4] 检查 PyInstaller...
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo [错误] PyInstaller 未安装，正在安装...
    pip install pyinstaller
) else (
    echo [OK] PyInstaller 已安装
)
echo.

echo [2/4] 清理旧的构建文件...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "*.spec" del /q "*.spec"
echo [OK] 清理完成
echo.

echo [3/4] 开始打包...
echo 这可能需要几分钟，请耐心等待...
echo.

pyinstaller --name="SceneWeaver" ^
    --windowed ^
    --onefile ^
    --icon=NONE ^
    --add-data "src;src" ^
    --hidden-import pygame ^
    --hidden-import tkinter ^
    --hidden-import tkinter.filedialog ^
    --hidden-import tkinter.messagebox ^
    --hidden-import json ^
    --hidden-import os ^
    --hidden-import sys ^
    --hidden-import pathlib ^
    --hidden-import math ^
    --hidden-import codecs ^
    --exclude-module matplotlib ^
    --noconfirm ^
    src/main.py

echo.
echo [4/4] 打包完成！
echo.

if exist "dist\SceneWeaver.exe" (
    echo ============================================================
    echo ✅ 打包成功！
    echo ============================================================
    echo 可执行文件位置：dist\SceneWeaver.exe
    echo 文件大小：
    for %%A in ("dist\SceneWeaver.exe") do echo   %%~zA 字节
    echo ============================================================
    echo.
    echo 现在可以运行以下命令测试：
    echo   dist\SceneWeaver.exe
    echo.
) else (
    echo ============================================================
    echo ❌ 打包失败！
    echo ============================================================
    echo 请检查上方的错误信息
    echo ============================================================
)

pause
