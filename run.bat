@echo off
title SceneWeaver - AIGC实景导演
echo ========================================
echo SceneWeaver - AIGC实景导演 启动脚本
echo ========================================
echo.

REM 检查Python环境
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到Python环境
    echo 请确保已安装Python 3.8或更高版本
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 显示Python版本
for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo 检测到: %PYTHON_VERSION%

REM 检查虚拟环境
if not exist "venv" (
    echo 创建虚拟环境...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo 虚拟环境创建失败，请手动创建或直接安装依赖
        goto install_deps
    )
)

REM 激活虚拟环境
echo 激活虚拟环境...
call venv\Scripts\activate.bat

:install_deps
REM 安装依赖
echo 安装项目依赖...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo 依赖安装失败，请检查网络连接和权限
    pause
    exit /b 1
)

REM 运行环境检查
echo 运行环境检查...
python check_environment.py
echo.

REM 询问用户选择运行模式
echo 请选择运行模式:
echo 1. 简化演示 (推荐新手)
echo 2. 完整程序
echo 3. 基础测试
echo 4. 开发模式 (调试)
echo 5. 退出
echo.

set /p choice=请输入选择 (1-5): 

if "%choice%"=="1" (
    echo 启动简化演示...
    python demo_simple.py
) else if "%choice%"=="2" (
    echo 启动完整程序...
    python src\main.py
) else if "%choice%"=="3" (
    echo 运行基础测试...
    python test_basic.py
) else if "%choice%"=="4" (
    echo 启动开发模式...
    python src\main.py --debug
) else if "%choice%"=="5" (
    echo 退出程序
    goto end
) else (
    echo 无效选择，启动简化演示...
    python demo_simple.py
)

:end
echo.
echo 程序已退出
pause