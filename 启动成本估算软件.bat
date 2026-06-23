@echo off
title 成本估算软件

REM 使用正确的Python路径（已安装Kivy的）
set PYTHON=D:\Python\python.exe
set APP=C:\Users\zx18y\.qclaw\workspace\cost-estimation-android\main.py

echo 正在启动成本估算软件...
echo Python: %PYTHON%
echo.

if not exist %PYTHON% (
    echo [错误] 找不到Python：%PYTHON%
    echo 请检查D:\Python是否存在
    pause
    exit /b 1
)

if not exist %APP% (
    echo [错误] 找不到应用文件：%APP%
    pause
    exit /b 1
)

REM 启动Kivy应用
%PYTHON% %APP%

REM 如果出错则暂停显示错误信息
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [程序已退出，错误代码：%ERRORLEVEL%]
    echo 请查看日志：%%USERPROFILE%%\.kivy\logs\
    pause
)
