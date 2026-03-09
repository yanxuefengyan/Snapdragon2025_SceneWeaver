# -*- coding: utf-8 -*-
"""
SceneWeaver 打包配置文件
"""

from PyInstaller.utils.hooks import collect_data_files
from PyInstaller.utils.hooks import collect_submodules

# 应用名称
name = "SceneWeaver"

# 应用版本
version = "1.0.0"

# 主程序文件
main_script = "src/main.py"

# 图标文件（可选）
# icon = 'icon.ico'

# 数据文件收集
datas = []

# 隐藏导入
hiddenimports = [
    'pygame',
    'pygame.locals',
    'tkinter',
    'tkinter.filedialog',
    'tkinter.messagebox',
    'json',
    'os',
    'sys',
    'pathlib',
    'math',
    'codecs',
]

# 排除不需要的模块
excludes = [
    'matplotlib',
    'numpy',  # 如果不使用可以排除
    'scipy',
    'pandas',
]

# 二进制文件
binaries = []

# 参数集合
a = Analysis(
    [main_script],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # 不显示控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # 可以设置图标
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=name,
)
