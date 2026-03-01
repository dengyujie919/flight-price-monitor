# 航班价格监控系统 - 功能流程说明

## 数据流转架构

```
[Amadeus API] 
    ↓ 采集
[data/raw/*.csv] 
    ↓ 特征工程
[data/processed/*.csv] 
    ↓ 模型训练
[models/*.pkl] 
    ↓ 预测分析
[outputs/reports/]
```

## 核心流程

### 1. 数据采集流程

**触发方式**
手动执行：`python run.py --mode collect`
自动执行：GitHub Actions 每天 UTC 00:00/12:00

**执行逻辑**
[1_collector.py](file:///d:/ai_learn/flight-price-monitor/src/collectors/1_collector.py)
1. 读取环境变量 `AMADEUS_CLIENT_ID`、`AMADEUS_CLIENT_SECRET`
2. 循环查询未来 30 天航班数据（SZX → YIH）
3. 解析 API 响应提取 13 个字段
4. 追加写入 `data/raw/szx_yih_flight_data_cn.csv`

**输出字段**
采集日期、起飞日期、提前天数、航班号、航司、类型、起飞时间、到达时间、总时长、中转地、中转时长、剩余座位、价格

### 2. 特征工程流程

**触发方式**
`python run.py --mode analyze`

**执行逻辑**
[flight_data_analysis.py](file:///d:/ai_learn/flight-price-monitor/src/analyzers/flight_data_analysis.py)
1. 读取原始数据（61,799 条）
2. 时间特征提取
   - 起飞时段（凌晨/上午/下午/晚上）
   - 到达时段
   - 飞行时长（小时）
   - 中转时长（小时）
3. 分类特征编码
   - 价格区间（低/中/高/超高）
   - 座位状态（紧张/正常/充足）
   - 中转次数
4. 衍生指标计算
   - 性价比 = 1000 / (价格 + 飞行时长×10)
   - 时间压力 = 1 / (提前天数 + 1)
   - 效率评分 = 剩余座位 / (飞行时长 + 1)
5. 生成分析报告
   - 统计摘要：均值、中位数、标准差
   - 相关性分析：特征与价格的相关系数
   - 可视化图表：4 张分析图
6. 输出 `data/processed/flight_data_featured.csv`（36 个特征）

**新增特征**
23 个特征：起飞时段、到达时段、飞行时长小时、中转时长小时、价格区间、座位状态、中转次数、性价比、时间压力、效率评分、航司编码、类型编码、起飞时段编码、到达时段编码、中转地编码等

### 3. 模型训练流程

**触发方式**
`python run.py --mode train`

**执行逻辑**
[2_predictor.py](file:///d:/ai_learn/flight-price-monitor/src/predictors/2_predictor.py)
1. 加载特征数据
2. 数据分割：80% 训练集 / 20% 测试集
3. 特征选择：排除非数值列（采集日期、起飞日期等）
4. 模型训练：RandomForestRegressor
   - n_estimators=100
   - random_state=42
5. 模型评估
   - MAE（平均绝对误差）
   - RMSE（均方根误差）
   - R²（决定系数）
6. 特征重要性分析
7. 保存模型至 `models/flight_price_model.pkl`
8. 生成预测对比图 `outputs/figures/prediction_results.png`

**模型性能**
训练集：MAE=0.44元，R²=0.9999
测试集：MAE=0.51元，R²=0.9998

### 4. 购买建议流程

**触发方式**
`python run.py --mode advise`

**执行逻辑**
[3_advisor.py](file:///d:/ai_learn/flight-price-monitor/src/predictors/3_advisor.py)
1. 加载训练好的模型
2. 读取最新航班数据
3. 预测未来价格走势
4. 决策逻辑
   - 当前价格 < 未来 7 天平均预测价格 → 建议立即购买
   - 否则 → 建议等待
5. 计算预期节省金额
6. 输出购买建议报告

### 5. 可视化流程

**触发方式**
`python run.py --mode visualize`

**执行逻辑**
[visualize_trend.py](file:///d:/ai_learn/flight-price-monitor/src/utils/visualize_trend.py)
1. 读取历史价格数据
2. 绘制价格走势图
   - X 轴：提前天数
   - Y 轴：价格
   - 标注最低价时间点
3. 保存至 `outputs/figures/`

### 6. 自动化调度流程

**本地调度**
[scheduler.py](file:///d:/ai_learn/flight-price-monitor/scheduler.py)
- 守护进程模式：`python scheduler.py --mode daemon`
- 单次执行：`python scheduler.py --mode once`
- 检查状态：`python scheduler.py --mode check`

**调度策略**
- 数据采集：每 12 小时
- 数据分析：每 3 天或新增 10,000 条数据
- 模型训练：每 7 天或新增 10,000 条数据

**GitHub Actions 自动化**
[daily_scan.yml](file:///d:/ai_learn/flight-price-monitor/.github/workflows/daily_scan.yml)
1. 定时触发：cron '0 0,12 * * *'
2. 环境配置：Python 3.10 + 依赖安装
3. 执行采集脚本
4. 数据检查：验证文件存在和行数
5. Git 提交：自动提交新数据到仓库
6. 上传日志：保留 30 天

## 配置管理

**全局配置**
[config.py](file:///d:/ai_learn/flight-price-monitor/config.py)
- 路径配置：数据目录、模型目录、输出目录
- API 配置：Amadeus 密钥
- 航线配置：起点 SZX、终点 YIH
- 调度配置：采集周期、训练周期
- 日志配置：日志级别、保留天数

**环境变量**
`.env` 文件
```
AMADEUS_CLIENT_ID=你的密钥
AMADEUS_CLIENT_SECRET=你的密钥
```

## 统一入口

**主脚本**
[run.py](file:///d:/ai_learn/flight-price-monitor/run.py)

**支持模式**
- `collect` 数据采集
- `analyze` 特征工程
- `train` 模型训练
- `advise` 购买建议
- `visualize` 可视化
- `all` 完整流程（analyze + train）

**路径自动适配**
脚本运行时动态替换各模块中的相对路径为绝对路径，确保从任意目录执行都能正确访问文件。

## 安全机制

**密钥保护**
- `.env` 文件排除提交（.gitignore）
- GitHub Secrets 存储 API 密钥
- Actions 运行时注入环境变量

**访问控制**
- API 调用间隔 0.2 秒防止超限
- 数据文件权限限制

**错误处理**
- API 异常捕获和日志记录
- 文件操作失败时保留原始数据
- 模型加载失败时提示重新训练
