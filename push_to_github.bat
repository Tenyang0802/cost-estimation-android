@echo off
REM ============================================================
REM 一键提交到GitHub + 自动打包APK
REM 使用方法：
REM  1. 打开 https://github.com/new 创建新仓库（Public）
REM  2. 复制仓库URL（如 https://github.com/你的用户名/仓库名.git）
REM  3. 运行本脚本，粘贴URL
REM  4. 去 https://github.com/你的用户名/仓库名/actions 下载APK
REM ============================================================

set /p REPO_URL="请输入GitHub仓库URL: "

cd /d "C:\Users\zx18y\.qclaw\workspace\cost-estimation-android"

echo 正在添加远程仓库...
git remote add origin %REPO_URL%

echo 正在推送到GitHub...
git push -u origin main

echo.
echo ============================================================
echo  上传成功！
echo.
echo  下一步：去GitHub自动打包APK
echo  地址: %REPO_URL:/actions%
echo.
echo  进入Actions页面 -> 点击"Build APK" -> 等待完成
echo  -> 下载 cost-estimation-apk.zip
echo  解压后得到 costestimation-1.0-arm64-v8a-debug.apk
echo  直接传到手机安装即可！
echo ============================================================
pause
