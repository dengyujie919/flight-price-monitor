# ✈️ 机票价格监控与预测系统

基于 Amadeus API 的智能机票价格追踪、预测和购买建议系统。

## 📋 项目简介

本项目通过实时采集机票数据，利用机器学习算法预测价格走势，并提供购买时机建议，帮助用户在最佳时间购买机票，节省出行成本。

**监控航线**：深圳 (SZX) → 宜昌 (YIH)

## 🛠️ 功能特性

### 1. **数据采集** (`1_collector.py`)
- 实时抓取指定航线的航班信息
- 提取关键数据：价格、剩余座位、航班号、航空公司等
- 自动保存到 CSV 文件进行历史记录

### 2. **价格预测** (`2_predictor.py`)
- 使用随机森林回归算法 (Random Forest Regressor)
- 基于历史数据预测未来价格
- 考虑因素：提前天数、航空公司等

### 3. **购买建议** (`3_advisor.py`)
- 分析当前价格与未来预测价格
- 给出"立即购买"或"等待"的建议
- 标注最佳购买时机和预期节省金额

### 4. **每日扫描** (`daily_scanner.py`)
- 批量扫描未来 30 天的航班数据
- 自动去重处理代码共享航班
- 支持中转航班信息提取
- 生成中文友好的 CSV 数据文件

### 5. **数据可视化** (`visualize_trend.py`)
- 生成价格走势图
- 分析购票策略（提前天数 vs 价格）
- 自动标注最低价时间点

## 🚀 快速开始

### 环境要求

- Python 3.7+
- Amadeus API 密钥（[申请地址](https://developers.amadeus.com/)）

### 安装依赖

```bash
pip install pandas numpy scikit-learn matplotlib seaborn python-dotenv amadeus
```

### 配置步骤

1. **创建 `.env` 文件**：
```env
AMADEUS_CLIENT_ID=你的API密钥
AMADEUS_CLIENT_SECRET=你的API密钥
```

2. **修改配置**（如果需要）：
   - 在脚本中修改 `ORIGIN` 和 `DESTINATION` 来监控不同航线
   - 调整 `SCAN_DAYS` 来改变扫描天数范围

### 运行程序

**单次采集数据**：
```bash
python 1_collector.py
```

**批量扫描未来30天**：
```bash
python daily_scanner.py
```

**训练模型并预测**（需要先有历史数据）：
```bash
python 2_predictor.py
```

**获取购买建议**：
```bash
python 3_advisor.py
```

**生成可视化图表**：
```bash
python visualize_trend.py
```

## 📊 数据文件

- `flight_data_detailed.csv` - 单次采集的详细航班数据
- `szx_yih_flight_data_cn.csv` - 批量扫描的中文格式数据
- `flight_data.csv` - 用于训练模型的历史数据

## 🔧 技术栈

- **数据采集**：Amadeus API
- **数据处理**：Pandas, NumPy
- **机器学习**：Scikit-learn (Random Forest Regressor)
- **可视化**：Matplotlib, Seaborn
- **环境配置**：python-dotenv

## 📈 使用建议

1. **数据积累**：建议先运行 `daily_scanner.py` 几天，积累足够的历史数据
2. **模型训练**：有足够数据后，运行 `2_predictor.py` 训练预测模型
3. **定期检查**：每天运行采集脚本，更新数据
4. **购买决策**：结合预测结果和建议，选择最佳购买时机

## 📝 注意事项

- Amadeus API 有调用频率限制，建议在请求之间添加适当的延迟
- 剩余座位数 `numberOfBookableSeats` 最大显示为 9（代表 9 个及以上）
- 价格预测的准确性取决于历史数据的质量和数量
- 建议结合多个数据源进行综合判断

## 🎯 未来优化方向

- [ ] 支持多航线监控
- [ ] 添加价格预警功能（邮件/微信通知）
- [ ] 优化预测算法（尝试时间序列模型）
- [ ] 添加 Web 界面
- [ ] 支持更多航空公司数据源

## 👨‍💻 作者

**yuyu** - [GitHub](https://github.com/dengyujie919)

## 📄 许可证

MIT License

---

**💡 提示**：机票价格受多种因素影响，预测结果仅供参考，请结合实际情况做出购买决策。
