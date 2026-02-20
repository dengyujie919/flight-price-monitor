"""
航班价格预测系统 - 主运行脚本
====================================

统一入口脚本，用于运行系统的各个模块。

使用方法:
    python run.py --mode [analyze|train|predict|advise|collect]
    或
    python run.py --all

示例:
    python run.py --mode analyze    # 数据分析
    python run.py --mode train      # 训练模型
    python run.py --mode predict    # 预测价格
    python run.py --mode collect    # 采集数据
    python run.py --mode advise     # 获取购买建议
    python run.py --all             # 运行完整流程
"""

import os
import sys
import argparse
import subprocess

# 添加项目根目录到Python路径
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

# 路径配置
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
RAW_DATA_DIR = os.path.join(DATA_DIR, 'raw')
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, 'processed')
MODELS_DIR = os.path.join(PROJECT_ROOT, 'models')
OUTPUTS_DIR = os.path.join(PROJECT_ROOT, 'outputs')
SRC_DIR = os.path.join(PROJECT_ROOT, 'src')


def run_collector():
    """运行数据采集器"""
    print("\n" + "="*80)
    print("运行数据采集器...")
    print("="*80 + "\n")

    script_path = os.path.join(SRC_DIR, 'collectors', '1_collector.py')
    if os.path.exists(script_path):
        subprocess.run([sys.executable, script_path])
    else:
        print(f"错误: 找不到文件 {script_path}")


def run_analyzer():
    """运行数据分析器"""
    print("\n" + "="*80)
    print("运行数据分析器...")
    print("="*80 + "\n")

    script_path = os.path.join(SRC_DIR, 'analyzers', 'flight_data_analysis.py')

    if not os.path.exists(script_path):
        print(f"错误: 找不到文件 {script_path}")
        return

    # 修改脚本中的路径引用
    import fileinput
    import shutil

    # 创建备份
    backup_path = script_path + '.bak'
    if not os.path.exists(backup_path):
        shutil.copy2(script_path, backup_path)

    # 更新数据文件路径
    raw_data_file = os.path.join(RAW_DATA_DIR, 'szx_yih_flight_data_cn.csv')
    output_dir = os.path.join(OUTPUTS_DIR, 'reports')
    featured_output = os.path.join(PROCESSED_DATA_DIR, 'flight_data_featured.csv')

    # 读取并临时修改脚本
    with open(script_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 临时替换路径
    original_content = content
    content = content.replace(
        "data_file = 'szx_yih_flight_data_cn.csv'",
        f"data_file = r'{raw_data_file}'"
    )
    content = content.replace(
        "featured_output = 'flight_data_featured.csv'",
        f"featured_output = r'{featured_output}'"
    )
    content = content.replace(
        "output_dir = 'analysis_output'",
        f"output_dir = r'{output_dir}'"
    )

    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(content)

    try:
        subprocess.run([sys.executable, script_path])
    finally:
        # 恢复原始内容
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(original_content)


def run_predictor():
    """运行预测器（训练和预测）"""
    print("\n" + "="*80)
    print("运行预测器...")
    print("="*80 + "\n")

    script_path = os.path.join(SRC_DIR, 'predictors', '2_predictor.py')

    if not os.path.exists(script_path):
        print(f"错误: 找不到文件 {script_path}")
        return

    # 修改脚本中的路径引用
    import shutil

    # 创建备份
    backup_path = script_path + '.bak'
    if not os.path.exists(backup_path):
        shutil.copy2(script_path, backup_path)

    # 读取并临时修改脚本
    with open(script_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 临时替换路径
    original_content = content

    # 更新数据文件路径
    data_file = os.path.join(PROCESSED_DATA_DIR, 'flight_data_featured.csv')
    model_file = os.path.join(MODELS_DIR, 'flight_price_model.pkl')
    prediction_plot = os.path.join(OUTPUTS_DIR, 'figures', 'prediction_results.png')

    content = content.replace(
        "data_file = 'flight_data_featured.csv'",
        f"data_file = r'{data_file}'"
    )
    content = content.replace(
        "model_file = 'flight_price_model.pkl'",
        f"model_file = r'{model_file}'"
    )
    content = content.replace(
        "save_path='prediction_results.png'",
        f"save_path=r'{prediction_plot}'"
    )

    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(content)

    try:
        subprocess.run([sys.executable, script_path])
    finally:
        # 恢复原始内容
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(original_content)


def run_advisor():
    """运行购买建议器"""
    print("\n" + "="*80)
    print("运行购买建议器...")
    print("="*80 + "\n")

    script_path = os.path.join(SRC_DIR, 'predictors', '3_advisor.py')
    if os.path.exists(script_path):
        subprocess.run([sys.executable, script_path])
    else:
        print(f"错误: 找不到文件 {script_path}")


def run_visualize():
    """运行可视化工具"""
    print("\n" + "="*80)
    print("运行可视化工具...")
    print("="*80 + "\n")

    script_path = os.path.join(SRC_DIR, 'utils', 'visualize_trend.py')
    if os.path.exists(script_path):
        subprocess.run([sys.executable, script_path])
    else:
        print(f"错误: 找不到文件 {script_path}")


def run_all():
    """运行完整流程：分析 -> 训练 -> 预测"""
    print("\n" + "="*80)
    print("运行完整流程...")
    print("="*80)

    # 1. 数据分析
    run_analyzer()

    # 2. 训练和预测
    run_predictor()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='航班价格预测系统 - 统一运行入口',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python run.py --mode analyze     # 数据分析和特征工程
  python run.py --mode train       # 训练模型
  python run.py --mode predict     # 预测价格
  python run.py --mode collect     # 采集数据
  python run.py --mode advise      # 获取购买建议
  python run.py --mode visualize   # 生成可视化
  python run.py --all              # 运行完整流程
        """
    )

    parser.add_argument(
        '--mode',
        type=str,
        choices=['analyze', 'train', 'predict', 'collect', 'advise', 'visualize', 'all'],
        default='all',
        help='运行模式'
    )

    args = parser.parse_args()

    # 根据模式运行对应的函数
    mode_functions = {
        'collect': run_collector,
        'analyze': run_analyzer,
        'train': run_predictor,
        'predict': run_predictor,
        'advise': run_advisor,
        'visualize': run_visualize,
        'all': run_all
    }

    mode_functions[args.mode]()

    print("\n" + "="*80)
    print("运行完成！")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
