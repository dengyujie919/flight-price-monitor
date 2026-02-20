# GitHub Actions 自动采集指南

## 📖 概述

本系统使用GitHub Actions实现航班数据的自动采集和上传，无需本地运行脚本。

## ⚙️ 配置步骤

### 1. 设置 GitHub Secrets

在GitHub仓库中添加Amadeus API密钥：

1. 打开仓库页面
2. 进入 **Settings** → **Secrets and variables** → **Actions**
3. 点击 **New repository secret**
4. 添加以下两个密钥：

```
AMADEUS_CLIENT_ID = 你的API密钥ID
AMADEUS_CLIENT_SECRET = 你的API密钥Secret
```

### 2. 工作流配置

工作流文件位于：`.github/workflows/daily_scan.yml`

**采集时间**：
- 每天2次自动采集
- 北京时间：08:00 和 20:00
- UTC时间：00:00 和 12:00

**触发方式**：
1. ✅ **定时触发** - 每天2次自动运行
2. ✅ **手动触发** - 在GitHub页面点击"Run workflow"
3. ✅ **代码推送** - 推送代码时自动运行（用于测试）

## 🚀 使用方式

### 方式一：自动采集（推荐）

工作流会按照设定时间自动运行：
```
00:00 UTC  (北京时间 08:00)  ← 早晨采集
12:00 UTC  (北京时间 20:00)  ← 晚上采集
```

### 方式二：手动触发

1. 进入GitHub仓库
2. 点击 **Actions** 标签
3. 选择 **Flight Data Auto Collection** 工作流
4. 点击 **Run workflow** 按钮
5. 选择分支（通常为main）
6. 点击绿色 **Run workflow** 按钮

### 方式三：本地测试

```bash
# 运行一次采集
python run.py --mode collect

# 或直接运行采集脚本
python src/collectors/1_collector.py
```

## 📊 数据管理

### 数据存储位置

```
data/
└── raw/
    └── szx_yih_flight_data_cn.csv  ← 原始数据（自动上传）
```

### 数据提交到GitHub

- ✅ **原始数据** - 自动提交到仓库
- ❌ **模型文件** - 不提交（在.gitignore中）
- ❌ **输出文件** - 不提交（在.gitignore中）

### 查看历史数据

```bash
# 查看数据提交历史
git log --oneline -- data/raw/szx_yih_flight_data_cn.csv

# 查看特定日期的数据
git show <commit-hash>:data/raw/szx_yih_flight_data_cn.csv
```

## 🔍 监控和日志

### 查看运行状态

1. 进入GitHub仓库
2. 点击 **Actions** 标签
3. 查看最近的工作流运行记录

### 查看运行日志

1. 点击具体的工作流运行
2. 展开 **collect-flight-data** 任务
3. 查看各个步骤的详细日志

### 下载采集日志

工作流会保存采集日志为artifacts，保留30天：
- 数据文件
- 系统日志

## 📈 数据统计

### 查看数据量

```bash
# 查看当前数据行数
wc -l data/raw/szx_yih_flight_data_cn.csv

# 查看文件大小
du -h data/raw/szx_yih_flight_data_cn.csv

# 查看数据统计
python -c "
import pandas as pd
df = pd.read_csv('data/raw/szx_yih_flight_data_cn.csv')
print(f'总记录数: {len(df):,}')
print(f'采集日期范围: {df[\"采集日期\"].min()} 至 {df[\"采集日期\"].max()}')
print(f'唯一采集天数: {df[\"采集日期\"].nunique()}')
"
```

## ⚠️ 注意事项

### API限制

- Amadeus API有调用频率限制
- 如果采集失败，检查GitHub Actions日志
- 确认API密钥有效且有足够配额

### 数据冲突

- GitHub Actions会自动拉取最新代码
- 使用`--strategy-option=theirs`处理冲突
- 本地修改前建议先`git pull`

### 存储空间

- CSV文件会持续增长
- 每月增加约15MB
- 仓库较大时克隆可能变慢

## 🛠️ 故障排查

### 采集失败

**问题**：工作流运行失败

**检查步骤**：
1. 确认GitHub Secrets已正确设置
2. 查看Actions日志中的错误信息
3. 验证Amadeus API密钥是否有效
4. 检查API配额是否用尽

### 数据未提交

**问题**：采集成功但数据未上传

**检查步骤**：
1. 查看Actions日志确认执行步骤
2. 检查"Commit and push"步骤的输出
3. 确认.gitignore未忽略数据文件
4. 验证仓库写入权限

### 时间不准确

**问题**：采集时间与预期不符

**说明**：
- GitHub Actions使用UTC时间
- 北京时间 = UTC + 8小时
- 当前设置：00:00 UTC = 北京时间 08:00

## 📝 更新工作流

如需修改采集时间或频率：

1. 编辑 `.github/workflows/daily_scan.yml`
2. 修改cron表达式：
   ```yaml
   schedule:
     - cron: '分 时 日 月 周'
   ```
3. 提交并推送到GitHub

**常用cron示例**：
```yaml
# 每天1次（早晨）
- cron: '0 0 * * *'

# 每天2次（早+晚）
- cron: '0 0,12 * * *'

# 每6小时1次
- cron: '0 */6 * * *'

# 每周一早上
- cron: '0 0 * * 1'
```

## 🔗 相关链接

- [GitHub Actions文档](https://docs.github.com/en/actions)
- [Amadeus API文档](https://developers.amadeus.com/)
- [Cron表达式生成器](https://crontab.guru/)

## 💡 最佳实践

1. ✅ **定期检查Actions运行状态**
2. ✅ **监控API调用次数**
3. ✅ **定期本地备份数据**
4. ✅ **查看提交历史验证数据**
5. ✅ **设置邮件通知工作流状态**

---

**更新日期**: 2026-02-20
**版本**: v2.0
