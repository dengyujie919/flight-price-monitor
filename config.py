"""
航班价格预测系统 - 配置文件
====================================

集中管理所有路径和配置参数。
"""

import os

# 项目根目录
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# 数据目录
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
RAW_DATA_DIR = os.path.join(DATA_DIR, 'raw')
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, 'processed')

# 模型目录
MODELS_DIR = os.path.join(PROJECT_ROOT, 'models')

# 输出目录
OUTPUTS_DIR = os.path.join(PROJECT_ROOT, 'outputs')
FIGURES_DIR = os.path.join(OUTPUTS_DIR, 'figures')
REPORTS_DIR = os.path.join(OUTPUTS_DIR, 'reports')

# 源代码目录
SRC_DIR = os.path.join(PROJECT_ROOT, 'src')
COLLECTORS_DIR = os.path.join(SRC_DIR, 'collectors')
ANALYZERS_DIR = os.path.join(SRC_DIR, 'analyzers')
PREDICTORS_DIR = os.path.join(SRC_DIR, 'predictors')
UTILS_DIR = os.path.join(SRC_DIR, 'utils')

# 数据文件
RAW_DATA_FILE = os.path.join(RAW_DATA_DIR, 'szx_yih_flight_data_cn.csv')
FEATURED_DATA_FILE = os.path.join(PROCESSED_DATA_DIR, 'flight_data_featured.csv')

# 模型文件
MODEL_FILE = os.path.join(MODELS_DIR, 'flight_price_model.pkl')

# 输出文件
PREDICTION_PLOT = os.path.join(FIGURES_DIR, 'prediction_results.png')
ANALYSIS_REPORT = os.path.join(REPORTS_DIR, 'analysis_report.txt')

# API配置
AMADEUS_API_URL = "https://test.api.amadeus.com"
AMADEUS_CLIENT_ID = os.getenv('AMADEUS_CLIENT_ID', '')
AMADEUS_CLIENT_SECRET = os.getenv('AMADEUS_CLIENT_SECRET', '')

# 航线配置
ORIGIN = "SZX"  # 深圳
DESTINATION = "YIH"  # 宜昌

# 扫描配置
SCAN_DAYS = 30  # 扫描未来30天

# 模型配置
MODEL_TYPE = 'random_forest'  # 可选: 'random_forest', 'gradient_boosting'
TEST_SIZE = 0.2
RANDOM_STATE = 42

# 可视化配置
FIGURE_DPI = 300
FIGURE_FORMAT = 'png'

# ========================================
# 调度周期配置
# ========================================

# ========================================
# 调度周期配置
# ========================================
# 基于实际运行情况优化（25天数据，每天~2500条）

# 数据采集周期（小时）
# 实际：每天2次，早晚各一次
# 原因：航班价格变化频繁，已稳定运行25天
COLLECTION_INTERVAL_HOURS = 12
COLLECTION_TIMES = ["08:00", "20:00"]  # 每天采集时间点

# 数据分析周期（天）
# 优化：从每周改为每3天
# 原因：每天2500条数据，3天=7500条，足以产生统计变化
ANALYSIS_INTERVAL_DAYS = 3
ANALYSIS_DAYS = ["Monday", "Thursday"]  # 每周一、周四执行

# 模型训练周期（天）
# 优化：从每2周改为每周
# 原因：每周新增~17500条数据，足以更新模型
TRAINING_INTERVAL_DAYS = 7
TRAINING_DAY = "Sunday"  # 每周日执行

# 模型重新训练阈值（新增数据条数）
# 优化：从5000提高到10000
# 原因：数据增长快，需要更高阈值避免频繁训练
RETRAIN_THRESHOLD = 10000

# ========================================
# 日志配置
# ========================================

# 日志级别：DEBUG, INFO, WARNING, ERROR
LOG_LEVEL = "INFO"

# 日志文件路径
LOG_DIR = os.path.join(PROJECT_ROOT, 'logs')
LOG_FILE = os.path.join(LOG_DIR, 'system.log')

# 日志保留天数
LOG_KEEP_DAYS = 30


def ensure_directories():
    """确保所有必要的目录存在"""
    directories = [
        DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR,
        MODELS_DIR, OUTPUTS_DIR, FIGURES_DIR, REPORTS_DIR
    ]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)

    print("目录结构检查完成")


if __name__ == "__main__":
    print("配置信息:")
    print(f"项目根目录: {PROJECT_ROOT}")
    print(f"原始数据: {RAW_DATA_FILE}")
    print(f"特征数据: {FEATURED_DATA_FILE}")
    print(f"模型文件: {MODEL_FILE}")
    print(f"\n确保目录存在...")
    ensure_directories()
