$WS = New-Object -ComObject WScript.Shell
$SC = $WS.CreateShortcut("$env:USERPROFILE\Desktop\成本估算软件.lnk")
$SC.TargetPath = "C:\Users\zx18y\.qclaw\workspace\cost-estimation-android\启动成本估算软件.bat"
$SC.WorkingDirectory = "C:\Users\zx18y\.qclaw\workspace\cost-estimation-android"
$SC.Description = "成本估算软件 - Kivy桌面版"
$SC.IconLocation = "D:\Python\python.exe,0"
$SC.Save()
Write-Host "桌面快捷方式已创建！"
