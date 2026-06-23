@echo off
title CostEstimator

set PYTHON=D:\Python\python.exe
set APP=C:\Users\zx18y\.qclaw\workspace\cost-estimation-android\main.py

echo Starting Cost Estimator...
echo Python: %PYTHON%
echo.

if not exist %PYTHON% (
    echo ERROR: Python not found at %PYTHON%
    pause
    exit /b 1
)

if not exist %APP% (
    echo ERROR: App not found at %APP%
    pause
    exit /b 1
)

%PYTHON% %APP%

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo App exited with code: %ERRORLEVEL%
    echo Check logs: %%USERPROFILE%%\.kivy\logs\
    pause
)
