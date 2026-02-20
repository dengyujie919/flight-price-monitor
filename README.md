# ✈️ 机票价格监控与预测系统

基于 Amadeus API 的智能机票价格追踪、预测和购买建议系统。

## 📋 项目简介

本项目通过实时采集机票数据，利用机器学习算法预测价格走势，并提供购买时机建议，帮助用户在最佳时间购买机票，节省出行成本。

**监控航线**：深圳 (SZX) → 宜昌 (YIH)

## 📁 项目结构

```
predict/
├── data/                          # 数据目录
│   ├── raw/                       # 原始数据
│   │   └── szx_yih_flight_data_cn.csv
│   └── processed/                 # 处理后的数据
│       └── flight_data_featured.csv
│
├── models/                        # 模型文件
│   └── flight_price_model.pkl
│
├── outputs/                       # 输出结果
│   ├── figures/                   # 图表
│   │   └── prediction_results.png
│   └── reports/                   # 分析报告
│       ├── analysis_report.txt
│       ├── price_analysis.png
│       ├── time_analysis.png
│       ├── correlation_heatmap.png
│       └── comprehensive_analysis.png
│
├── src/                           # 源代码
│   ├── collectors/                # 数据采集
│   │   └── 1_collector.py
│   ├── analyzers/                 # 数据分析
│   │   └── flight_data_analysis.py
│   ├── predictors/                # 预测模型
│   │   ├── 2_predictor.py
│   │   └── 3_advisor.py
│   └── utils/                     # 工具函数
│       └── visualize_trend.py
│
├── docs/                          # 文档
├── config.py                      # 配置文件
├── run.py                         # 主运行脚本 ⭐
├── requirements.txt               # 依赖包
├── .env                           # 环境变量
└── README.md                      # 项目说明
```

## 🛠️ 功能特性

### 1. **数据采集** (`src/collectors/1_collector.py`)
- 实时抓取指定航线的航班信息
- 提取关键数据：价格、剩余座位、航班号、航空公司等
- 自动保存到 CSV 文件进行历史记录

### 2. **价格预测** (`src/predictors/2_predictor.py`) ⭐ 已升级
- 使用随机森林回归算法 (Random Forest Regressor)
- 基于历史数据和丰富的特征工程预测未来价格
- 考虑因素：
  - 提前天数、航空公司
  - 飞行时长、中转时长、中转次数
  - 剩余座位、起飞时段
  - 性价比、时间压力、效率评分
- 模型性能：MAE < 1元, R² > 0.999

### 3. **数据分析和特征工程** (`src/analyzers/flight_data_analysis.py`) 🆕
- 读取原始航班数据（61,797条记录）
- 提取 **23个新特征**：
  - 时间特征：起飞时段、到达时段、飞行时长、中转时长
  - 分类特征：价格区间、座位状态、中转次数
  - 衍生特征：性价比、时间压力、效率评分
- 生成完整的分析报告和可视化图表
- 输出特征数据集：`flight_data_featured.csv`

### 4. **购买建议** (`src/predictors/3_advisor.py`)
- 分析当前价格与未来预测价格
- 给出"立即购买"或"等待"的建议
- 标注最佳购买时机和预期节省金额

### 5. **数据可视化** (`src/utils/visualize_trend.py`)
- 生成价格走势图
- 分析购票策略（提前天数 vs 价格）
- 自动标注最低价时间点

## 🚀 快速开始

### 环境要求

- Python 3.7+
- Amadeus API 密钥（[申请地址](https://developers.amadeus.com/)）

### 安装依赖

```bash
pip install -r requirements.txt
```

或手动安装：

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
   编辑 `config.py` 修改航线配置和扫描参数

### 运行程序

#### 方式一：使用主运行脚本 ⭐ 推荐

```bash
# 数据分析和特征工程
python run.py --mode analyze

# 训练模型并预测
python run.py --mode train

# 采集数据
python run.py --mode collect

# 获取购买建议
python run.py --mode advise

# 生成可视化图表
python run.py --mode visualize

# 运行完整流程（分析 + 训练 + 预测）
python run.py --all
```

#### 方式二：直接运行各模块

```bash
# 数据采集
python src/collectors/1_collector.py

# 数据分析和特征工程
python src/analyzers/flight_data_analysis.py

# 训练模型并预测
python src/predictors/2_predictor.py

# 获取购买建议
python src/predictors/3_advisor.py

# 生成可视化图表
python src/utils/visualize_trend.py
```

## 📊 数据文件说明

### 原始数据
- **位置**: `data/raw/szx_yih_flight_data_cn.csv`
- **说明**: 批量扫描的中文格式数据（61,797条记录）
- **字段**: 采集日期、起飞日期、提前天数、航班号、航司、类型、起飞时间、到达时间、总时长、中转地、中转时长、剩余座位、价格

### 特征工程数据
- **位置**: `data/processed/flight_data_featured.csv`
- **说明**: 特征工程后的数据（36个特征 = 13个原始 + 23个新增）
- **用途**: 用于机器学习模型训练

### 模型文件
- **位置**: `models/flight_price_model.pkl`
- **说明**: 训练好的随机森林模型
- **性能**: MAE=0.51元, R²=0.9998

### 分析报告
- **位置**: `outputs/reports/`
- **内容**:
  - `analysis_report.txt` - 详细文本报告
  - `price_analysis.png` - 价格分析图表
  - `time_analysis.png` - 时间特征分析
  - `correlation_heatmap.png` - 特征相关性热力图
  - `comprehensive_analysis.png` - 综合分析图

## 🔧 技术栈

- **数据采集**：Amadeus API
- **数据处理**：Pandas, NumPy
- **机器学习**：Scikit-learn (Random Forest Regressor)
- **可视化**：Matplotlib, Seaborn
- **环境配置**：python-dotenv

## 📈 数据洞察

### 价格分析
- 平均价格: 700.87 元
- 价格区间: 328.64 - 2,977.68 元
- 中位数: 596.59 元

### 航司市场份额
- CZ (南方航空): 44.9%
- MU (东方航空): 23.5%
- HU (海南航空): 10.1%
- ZH: 7.5%
- CA (国航): 6.2%

### 时间特征
- 平均飞行时长: 12.41 小时
- 所有航班都需要中转（100%）
- 80.98% 需要 2 次中转

### 预订模式
- 平均提前预订: 15.65 天
- 范围: 1-30 天

## 🎯 模型性能

### 训练集性能
- **MAE**: 0.44 元
- **RMSE**: 3.14 元
- **R²**: 0.9999

### 测试集性能
- **MAE**: 0.51 元
- **RMSE**: 4.56 元
- **R²**: 0.9998

### 特征重要性（Top 5）
1. **价格区间**: 64.87%
2. **性价比**: 11.86%
3. **航司**: 10.63%
4. **剩余座位**: 6.09%
5. **效率评分**: 5.84%

## 💡 使用建议

1. **数据积累**：建议先运行数据采集几天，积累足够的历史数据
2. **特征工程**：运行 `python run.py --mode analyze` 进行特征提取和分析
3. **模型训练**：有足够数据后，运行 `python run.py --mode train` 训练预测模型
4. **定期检查**：每天运行数据采集脚本，更新数据
5. **购买决策**：结合预测结果和建议，选择最佳购买时机

### 预测示例

| 场景 | 提前天数 | 剩余座位 | 预测价格 |
|------|---------|---------|---------|
| 提前30天，座位充足 | 30 | 9 | 352.11 元 |
| 提前3天，座位紧张 | 3 | 1 | 806.27 元 |
| 提前15天，中等情况 | 15 | 5 | 518.40 元 |

## 📝 配置说明

所有配置集中在 `config.py` 文件中：

```python
# 航线配置
ORIGIN = "SZX"      # 出发地
DESTINATION = "YIH"  # 目的地

# 扫描配置
SCAN_DAYS = 30      # 扫描未来天数

# 模型配置
MODEL_TYPE = 'random_forest'  # 模型类型
TEST_SIZE = 0.2              # 测试集比例
```

## 📝 注意事项

- Amadeus API 有调用频率限制，建议在请求之间添加适当的延迟
- 剩余座位数 `numberOfBookableSeats` 最大显示为 9（代表 9 个及以上）
- 价格预测的准确性取决于历史数据的质量和数量
- 建议结合多个数据源进行综合判断

## 🚀 未来优化方向

- [ ] 支持多航线监控
- [ ] 添加价格预警功能（邮件/微信通知）
- [ ] 优化预测算法（尝试 XGBoost、LightGBM）
- [ ] 添加时间序列分析功能
- [ ] 实现 Web 界面
- [ ] 支持更多航空公司数据源
- [ ] 实时价格监控和预测

## 📞 获取帮助

```bash
# 查看运行脚本帮助
python run.py --help

# 检查配置
python config.py
```

## 👨‍💻 作者

**yuyu** - [GitHub](https://github.com/dengyujie919)

## 📄 许可证

MIT License

---

**💡 提示**：机票价格受多种因素影响，预测结果仅供参考，请结合实际情况做出购买决策。
