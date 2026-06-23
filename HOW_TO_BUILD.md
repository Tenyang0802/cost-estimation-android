# 如何一键打包APK（无需安装任何环境）

## 方法：GitHub Action 自动打包（推荐，5分钟搞定）

### 第1步：创建GitHub仓库
1. 打开 https://github.com/new
2. 仓库名填: `cost-estimation-android`
3. 选 **Public**（免费的Action配额）
4. 点 **Create repository**

### 第2步：推送代码
双击运行 `push_to_github.bat`，粘贴仓库URL即可推送

### 第3步：下载APK
1. 打开 https://github.com/你的用户名/cost-estimation-android/actions
2. 点击 **Build APK** 工作流
3. 等3-5分钟（黄色⚡转绿色✅）
4. 点击 **cost-estimation-apk** 下载
5. 解压得到 `.apk` 文件，传到手机安装！

## 已包含的文件
| 文件 | 说明 |
|------|------|
| `main.py` | Kivy主程序（9个功能屏幕） |
| `data_manager.py` | 全部计算逻辑 |
| `cost_data.json` | 默认数据 |
| `buildozer.spec` | 打包配置 |
| `.github/workflows/build-apk.yml` | GitHub自动打包脚本 |

## 安装说明
- 下载APK后直接传到Android手机
- 设置中允许"安装未知来源应用"
- 点击APK文件安装即可使用
