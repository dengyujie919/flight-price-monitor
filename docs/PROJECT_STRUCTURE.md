# 项目文件结构

## 📁 完整目录树

```
predict/
│
├── 📂 data/                          # 数据目录
│   ├── 📂 raw/                       # 原始数据
│   │   └── 📄 szx_yih_flight_data_cn.csv (61,797条记录)
│   │
│   └── 📂 processed/                 # 处理后的数据
│       └── 📄 flight_data_featured.csv (36个特征)
│
├── 📂 models/                        # 模型文件
│   └── 📄 flight_price_model.pkl (35MB)
│
├── 📂 outputs/                       # 输出结果
│   ├── 📂 figures/                   # 图表
│   │   └── 📊 prediction_results.png
│   │
│   └── 📂 reports/                   # 分析报告
│       └── 📂 analysis_output/
│           ├── 📝 analysis_report.txt
│           ├── 📊 price_analysis.png
│           ├── 📊 time_analysis.png
│           ├── 📊 correlation_heatmap.png
│           └── 📊 comprehensive_analysis.png
│
├── 📂 src/                           # 源代码
│   ├── 🐍 __init__.py
│   │
│   ├── 📂 collectors/                # 数据采集模块
│   │   ├── 🐍 __init__.py
│   │   └── 📄 1_collector.py
│   │
│   ├── 📂 analyzers/                 # 数据分析模块
│   │   ├── 🐍 __init__.py
│   │   └── 📄 flight_data_analysis.py
│   │
│   ├── 📂 predictors/                # 预测模块
│   │   ├── 🐍 __init__.py
│   │   ├── 📄 2_predictor.py
│   │   └── 📄 3_advisor.py
│   │
│   └── 📂 utils/                     # 工具模块
│       ├── 🐍 __init__.py
│       └── 📄 visualize_trend.py
│
├── 📂 docs/                          # 文档目录
│   └── 📄 PROJECT_STRUCTURE.md
│
├── 📄 config.py                      # 配置文件 ⭐
├── 📄 run.py                         # 主运行脚本 ⭐
├── 📄 requirements.txt               # 依赖包列表
├── 🔐 .env                           # 环境变量
├── 🚫 .gitignore                     # Git忽略文件
└── 📖 README.md                      # 项目说明
```

## 📊 文件统计

| 类型 | 数量 | 说明 |
|------|------|------|
| Python脚本 | 9 | 包括主脚本和各功能模块 |
| 数据文件 | 2 | 原始数据和特征数据 |
| 模型文件 | 1 | 训练好的随机森林模型 |
| 图表文件 | 5 | 各类分析可视化图表 |
| 配置文件 | 3 | config.py, requirements.txt, .env |
| 文档文件 | 2 | README.md, PROJECT_STRUCTURE.md |

## 🔄 数据流程图

```
原始数据采集
    ↓
data/raw/szx_yih_flight_data_cn.csv
    ↓
[特征工程] src/analyzers/flight_data_analysis.py
    ↓
data/processed/flight_data_featured.csv
    ↓
[模型训练] src/predictors/2_predictor.py
    ↓
models/flight_price_model.pkl
    ↓
[价格预测] src/predictors/2_predictor.py
    ↓
outputs/figures/prediction_results.png
```

## 🎯 快速查找

### 数据文件位置
- 原始数据: `data/raw/`
- 处理后数据: `data/processed/`

### 模型文件位置
- 训练好的模型: `models/`

### 输出结果位置
- 图表: `outputs/figures/`
- 报告: `outputs/reports/`

### 源代码位置
- 数据采集: `src/collectors/`
- 数据分析: `src/analyzers/`
- 价格预测: `src/predictors/`
- 工具函数: `src/utils/`

## 💡 使用建议

1. **运行完整流程**: 使用 `python run.py --all`
2. **单独运行模块**: 使用 `python run.py --mode [模式]`
3. **直接运行脚本**: 进入对应目录直接运行Python文件
4. **修改配置**: 编辑 `config.py` 文件
5. **查看帮助**: 运行 `python run.py --help`

## 📝 注意事项

- 所有路径都在 `config.py` 中集中管理
- 使用 `run.py` 可以自动处理路径问题
- 建议不要手动移动文件，以免破坏路径引用
- 定期清理 `outputs/` 目录以节省空间
