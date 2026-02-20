# 🚀 GitHub Actions 快速配置

## ✅ 已完成配置

以下功能已配置完成并推送到GitHub：

### 1. 自动数据采集
- ⏰ **时间**: 每天2次（北京时间 08:00 和 20:00）
- 📊 **数据**: 自动采集并上传到GitHub
- 🔄 **自动化**: GitHub Actions自动运行

### 2. 数据存储
```
data/raw/szx_yih_flight_data_cn.csv  ← 原始数据（自动上传）
```

## 📋 待配置步骤

### ⚠️ 重要：设置GitHub Secrets

您需要在GitHub仓库中添加Amadeus API密钥：

**步骤**：

1. 打开仓库：https://github.com/dengyujie919/flight-price-monitor

2. 进入 **Settings** → **Secrets and variables** → **Actions**

3. 点击 **New repository secret** 添加密钥：

   ```
   Name: AMADEUS_CLIENT_ID
   Value: 你的API密钥ID
   ```

   点击 **Add secret**

4. 再次点击 **New repository secret** 添加第二个密钥：

   ```
   Name: AMADEUS_CLIENT_SECRET
   Value: 你的API密钥Secret
   ```

   点击 **Add secret**

### 验证配置

添加密钥后，可以手动触发一次采集进行测试：

1. 进入仓库的 **Actions** 页面
2. 选择 **Flight Data Auto Collection** 工作流
3. 点击 **Run workflow** 按钮
4. 选择 `main` 分支
5. 点击 **Run workflow**（绿色按钮）
6. 等待运行完成，查看结果

## 📊 查看采集数据

采集成功后，可以在仓库中查看数据文件：

```
https://github.com/dengyujie919/flight-price-monitor/blob/main/data/raw/szx_yih_flight_data_cn.csv
```

## 🔄 自动运行

配置完成后，系统会自动：

- ✅ 每天 08:00 采集一次
- ✅ 每天 20:00 采集一次
- ✅ 自动上传数据到仓库
- ✅ 生成运行日志

## 📝 提交信息格式

每次自动提交的格式：

```
📊 Auto-update flight data: 2026-02-20 12:00:00

📡 采集时间: 2026-02-20 12:00:00 UTC
🔄 Trigger: GitHub Actions

Co-Authored-By: GitHub Actions <github-actions[bot]@users.noreply.github.com>
```

## 🔍 监控运行

**查看最近运行**：
```
https://github.com/dengyujie919/flight-price-monitor/actions
```

**查看具体日志**：
1. 点击任意一次工作流运行
2. 展开 **collect-flight-data** 任务
3. 查看各步骤的详细输出

## ⚡ 本地运行

如需在本地运行采集：

```bash
# 方式一：使用主运行脚本
python run.py --mode collect

# 方式二：直接运行采集脚本
python src/collectors/1_collector.py

# 方式三：使用调度器
python scheduler.py --mode once
```

## 📚 详细文档

- [GitHub Actions 完整指南](docs/GITHUB_ACTIONS_GUIDE.md)
- [项目调度周期指南](docs/SCHEDULE_GUIDE.md)
- [项目主文档](README.md)

## 🆘 常见问题

### Q: 采集失败了怎么办？
A: 检查以下项：
1. GitHub Secrets是否正确设置
2. Amadeus API密钥是否有效
3. Actions日志中的错误信息

### Q: 如何修改采集时间？
A: 编辑 `.github/workflows/daily_scan.yml` 中的cron表达式

### Q: 数据会丢失吗？
A: 不会。每次采集都会追加到CSV文件并提交到GitHub，有完整的版本历史

### Q: 仓库会变得很大吗？
A: 会逐渐增长。每月约增加15MB，建议定期归档旧数据

---

**配置完成后，系统将全自动运行！** 🎉

更新日期: 2026-02-20
