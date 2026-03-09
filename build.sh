#!/bin/bash
# SceneWeaver 打包脚本 (Linux/Mac)

echo "============================================================"
echo "SceneWeaver 打包脚本"
echo "============================================================"
echo ""

echo "[1/4] 检查 PyInstaller..."
python3 -c "import PyInstaller" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "[错误] PyInstaller 未安装，正在安装..."
    pip3 install pyinstaller
else
    echo "[OK] PyInstaller 已安装"
fi
echo ""

echo "[2/4] 清理旧的构建文件..."
rm -rf build dist *.spec
echo "[OK] 清理完成"
echo ""

echo "[3/4] 开始打包..."
echo "这可能需要几分钟，请耐心等待..."
echo ""

pyinstaller --name="SceneWeaver" \
    --windowed \
    --onefile \
    --icon=NONE \
    --add-data "src:src" \
    --hidden-import pygame \
    --hidden-import tkinter \
    --hidden-import tkinter.filedialog \
    --hidden-import tkinter.messagebox \
    --hidden-import json \
    --hidden-import os \
    --hidden-import sys \
    --hidden-import pathlib \
    --hidden-import math \
    --hidden-import codecs \
    --exclude-module matplotlib \
    --noconfirm \
    src/main.py

echo ""
echo "[4/4] 打包完成！"
echo ""

if [ -f "dist/SceneWeaver" ]; then
    echo "============================================================"
    echo "✅ 打包成功！"
    echo "============================================================"
    echo "可执行文件位置：dist/SceneWeaver"
    echo "文件大小：$(ls -lh dist/SceneWeaver | awk '{print $5}')"
    echo "============================================================"
    echo ""
    echo "现在可以运行以下命令测试："
    echo "  ./dist/SceneWeaver"
    echo ""
else
    echo "============================================================"
    echo "❌ 打包失败！"
    echo "============================================================"
    echo "请检查上方的错误信息"
    echo "============================================================"
fi
