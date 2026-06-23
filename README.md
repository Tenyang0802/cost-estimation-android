# Android Kivy版开发报告 - 2026-06-18 21:49

## 项目结构

```
cost-estimation-android/
├── main.py              # Kivy主应用 (62KB, 所有屏幕类)
├── data_manager.py      # 数据管理 + 计算逻辑 (18KB, 移植自桌面版)
├── cost_data.json       # 默认数据文件 (已复制)
├── buildozer.spec       # Android打包配置
└── README.md            # 本文件
```

## 已完成的屏幕

### 1. 仪表盘 (DashboardScreen)
- 顶部信息栏：版本号、月产能、总费用
- 快速统计卡片：产能、总费用、工资总计
- 8个功能模块入口网格（2列布局）
- 一键跳转到各功能页面

### 2. 生产管理 (ProductionScreen)
- **月产能设置**：输入月产能(kg)，保存后联算工资
- **基本生产效率**：
  - 工作时间和天数设置
  - 模式切换：A模式（手动输入）/ B模式（参考项目）
  - A模式：手动输入产量/小时(kg)
  - B模式：添加/删除参考项目，自动计算平均效率
  - 当前效率实时显示

### 3. 费用管理 (CostsScreen)
- **固定费用**：添加/删除/显示固定费用项目
- **管理员费用**：添加/删除（含数量计算总价）
- **电费**：输入单价(元/kg)
- 费用汇总显示

### 4. 工资管理 (WagesScreen)
- 三个子标签切换：搬运工/生产线/包装人员
- **搬运工**：姓名+基本工资，自动计算修正工资
- **生产线**：姓名+基本工资+额外元/时+满勤奖，自动计算实际工资
- **包装人员**：姓名+基本工资+职位补贴+满勤奖，自动计算校准工资

### 5. 包装设置 (PackagingScreen)
- 包装系数：上月工资+产量自动计算
- 包装费用：包装膜/纸箱费用输入

### 6. 原材料库 (MaterialsScreen)
- 添加/删除原材料（名称+价格kg）
- 自动检测重复名称
- 卡片式列表展示

### 7. 产品配方 (ProductsScreen)
- 添加/选择产品
- 投料产出比设置
- 配料列表：添加/删除配料
- 自动计算原材料成本

### 8. 最终计算 (FinalCalcScreen)
- 成本汇总：固定费用+管理员+电费+三工资
- 每kg均摊费用
- 各产品成本明细

### 9. 数据分析 (AnalysisScreen)
- 产能-成本分析（5个产能点）
- 成本占比分析（百分比）
- 原材料敏感性分析（选原料+步长+次数）

## 技术架构

### 设计模式
- **屏幕导航**：Kivy ScreenManager + SlideTransition
- **数据层**：DataManager（移植自桌面版，Android路径适配）
- **UI组件**：自定义卡片(CardBox)、标签(SubHeader/SectionTitle)、信息行(InfoRow)
- **配色方案**：现代蓝色主题（#3390E6主色 + #19BF8C辅助色）

### 关键适配
1. **文件存储**：Android使用 `app_storage_path()`，桌面使用脚本目录
2. **图表**：当前用列表展示数据替代matplotlib图表（减轻APK体积）
3. **操作方式**：触摸友好的大按钮和输入框
4. **数据持久化**：直接读写JSON文件（与桌面版兼容）

### 计算逻辑
DataManager 100%移植自桌面版 V2.4，所有公式一致：
- 搬运工工资公式 ✅
- 生产线员工工资公式 ✅
- 包装人员工资公式 ✅
- 总费用=固定+管理+电费+三工资 ✅
- total_costs_at_capacity ✅
- 敏感性分析 ✅

## 打包说明

### 环境要求
- Python 3.x
- Buildozer + Python-for-Android
- Android SDK/NDK (API 33+, NDK 25b)

### 打包命令
```bash
cd cost-estimation-android
buildozer android debug
```

### 输出
- APK文件：`bin/costestimation-1.0-arm64-v8a-debug.apk`
- 可直接安装到Android 8.0+设备

## 下一步计划

1. **测试阶段**：
   - 在Android设备上运行测试
   - 检查所有功能是否完整
   - 修复可能的兼容性问题

2. **优化阶段**：
   - 添加图表功能（如果APK大小允许）
   - 优化触摸交互体验
   - 添加数据导出功能

3. **分发阶段**：
   - 使用debug keystore签名
   - 直接分享APK文件
   - 不需要上架商店

# Trigger rebuild
