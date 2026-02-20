"""
航班数据分析和特征提取脚本
分析 szx_yih_flight_data_cn.csv 数据集
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

def load_data(filepath):
    """加载CSV数据"""
    df = pd.read_csv(filepath, encoding='utf-8-sig')
    print(f"数据集形状: {df.shape}")
    print(f"\n数据集前5行:")
    print(df.head())
    return df

def basic_statistics(df):
    """基础统计分析"""
    print("\n" + "="*80)
    print("基础统计信息")
    print("="*80)

    print("\n数据类型:")
    print(df.dtypes)

    print("\n缺失值统计:")
    print(df.isnull().sum())

    print("\n数值型字段统计:")
    print(df.describe())

    print("\n分类字段统计:")
    categorical_cols = ['航司', '类型', '中转地']
    for col in categorical_cols:
        if col in df.columns:
            print(f"\n{col} 分布:")
            print(df[col].value_counts().head(10))

def feature_engineering(df):
    """特征工程和特征提取"""
    print("\n" + "="*80)
    print("特征工程")
    print("="*80)

    df_new = df.copy()

    # 1. 时间特征提取
    print("\n[1] 提取时间特征...")

    # 转换日期列
    df_new['采集日期'] = pd.to_datetime(df_new['采集日期'])
    df_new['起飞日期'] = pd.to_datetime(df_new['起飞日期'])

    # 提取日期特征
    df_new['采集_星期'] = df_new['采集日期'].dt.dayofweek
    df_new['采集_月份'] = df_new['采集日期'].dt.month
    df_new['采集_日期'] = df_new['采集日期'].dt.day

    df_new['起飞_星期'] = df_new['起飞日期'].dt.dayofweek
    df_new['起飞_月份'] = df_new['起飞日期'].dt.month
    df_new['起飞_日期'] = df_new['起飞日期'].dt.day

    # 2. 起飞和到达时间特征
    print("[2] 处理起飞和到达时间...")
    df_new['起飞小时'] = pd.to_datetime(df_new['起飞时间'], format='%H:%M').dt.hour
    df_new['到达小时'] = pd.to_datetime(df_new['到达时间'], format='%H:%M').dt.hour

    # 时间段分类
    def get_time_period(hour):
        if 6 <= hour < 12:
            return '上午'
        elif 12 <= hour < 18:
            return '下午'
        elif 18 <= hour < 24:
            return '晚上'
        else:
            return '凌晨'

    df_new['起飞时段'] = df_new['起飞小时'].apply(get_time_period)
    df_new['到达时段'] = df_new['到达小时'].apply(get_time_period)

    # 3. 飞行时长特征（转换为分钟）
    print("[3] 计算飞行时长...")
    def parse_duration(duration_str):
        """解析时长字符串，返回分钟数"""
        if '小时' in duration_str:
            parts = duration_str.replace('小时', 'h').replace('分', 'm').split('h')
            hours = int(parts[0])
            minutes = int(parts[1].replace('m', '')) if 'm' in parts[1] else 0
            return hours * 60 + minutes
        return 0

    df_new['飞行时长_分钟'] = df_new['总时长'].apply(parse_duration)

    # 4. 中转时长特征（转换为分钟）
    print("[4] 计算中转时长...")
    def parse_transfer_duration(duration_str):
        """解析中转时长，返回分钟数"""
        if pd.isna(duration_str) or duration_str == '':
            return 0
        duration_str = str(duration_str).lower().replace('h', '').replace('m', '')
        if ' ' in duration_str:
            parts = duration_str.split()
            if len(parts) == 2:
                return int(parts[0]) * 60 + int(parts[1])
        return 0

    df_new['中转时长_分钟'] = df_new['中转时长'].apply(parse_transfer_duration)

    # 5. 中转特征
    print("[5] 提取中转特征...")
    # 中转次数（通过中转地计算）
    df_new['中转次数'] = df_new['中转地'].apply(lambda x: len(str(x).split('/')) if pd.notna(x) else 0)

    # 是否有中转
    df_new['是否有中转'] = (df_new['中转次数'] > 0).astype(int)

    # 6. 航司特征
    print("[6] 编码航司特征...")
    # 主要航司标识
    top_airlines = df_new['航司'].value_counts().head(5).index.tolist()
    df_new['主要航司'] = df_new['航司'].apply(lambda x: 1 if x in top_airlines else 0)

    # 7. 价格特征
    print("[7] 分析价格特征...")
    df_new['价格_百元'] = df_new['价格'] / 100

    # 价格分段
    price_bins = [0, 400, 500, 600, 800, 10000]
    price_labels = ['低价(<400)', '中低价(400-500)', '中价(500-600)', '中高价(600-800)', '高价(>800)']
    df_new['价格区间'] = pd.cut(df_new['价格'], bins=price_bins, labels=price_labels)

    # 8. 座位特征
    print("[8] 分析座位特征...")
    # 剩余座位分类
    def seat_category(seats):
        if seats <= 2:
            return '紧张(<=2)'
        elif seats <= 5:
            return '较少(3-5)'
        elif seats <= 9:
            return '中等(6-9)'
        else:
            return '充足(>9)'

    df_new['座位状态'] = df_new['剩余座位'].apply(seat_category)

    # 9. 性价比特征（价格/座位）
    print("[9] 计算性价比特征...")
    df_new['性价比'] = df_new['价格'] / (df_new['剩余座位'] + 1)  # 加1避免除0

    # 10. 时间压力特征（提前天数的倒数）
    print("[10] 计算时间压力特征...")
    df_new['时间压力'] = 1 / (df_new['提前天数'] + 1)

    # 11. 综合效率评分
    print("[11] 计算综合效率评分...")
    # 标准化各项指标
    df_new['时长标准化'] = (df_new['飞行时长_分钟'] - df_new['飞行时长_分钟'].min()) / (df_new['飞行时长_分钟'].max() - df_new['飞行时长_分钟'].min())
    df_new['价格标准化'] = (df_new['价格'] - df_new['价格'].min()) / (df_new['价格'].max() - df_new['价格'].min())

    # 效率评分：时长越短、价格越低、座位越多越好
    df_new['效率评分'] = 1 - (df_new['时长标准化'] * 0.4 + df_new['价格标准化'] * 0.4 - (df_new['剩余座位'] / df_new['剩余座位'].max()) * 0.2)

    print(f"\n特征工程完成！新增特征数量: {len(df_new.columns) - len(df.columns)}")
    print(f"新数据集形状: {df_new.shape}")

    return df_new

def exploratory_analysis(df, df_featured):
    """探索性数据分析和可视化"""
    print("\n" + "="*80)
    print("探索性数据分析")
    print("="*80)

    # 创建输出目录
    import os
    output_dir = 'analysis_output'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 1. 价格分布分析
    print("\n[1] 价格分布分析...")
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))

    # 价格直方图
    axes[0, 0].hist(df['价格'], bins=30, edgecolor='black', alpha=0.7)
    axes[0, 0].set_title('价格分布直方图')
    axes[0, 0].set_xlabel('价格 (元)')
    axes[0, 0].set_ylabel('频数')

    # 价格箱线图
    axes[0, 1].boxplot(df['价格'])
    axes[0, 1].set_title('价格箱线图')
    axes[0, 1].set_ylabel('价格 (元)')

    # 按航司的价格分布
    airline_prices = df.groupby('航司')['价格'].mean().sort_values(ascending=False).head(10)
    axes[1, 0].barh(range(len(airline_prices)), airline_prices.values)
    axes[1, 0].set_yticks(range(len(airline_prices)))
    axes[1, 0].set_yticklabels(airline_prices.index)
    axes[1, 0].set_title('各航司平均价格')
    axes[1, 0].set_xlabel('平均价格 (元)')

    # 提前天数 vs 价格
    axes[1, 1].scatter(df['提前天数'], df['价格'], alpha=0.5)
    axes[1, 1].set_title('提前天数 vs 价格')
    axes[1, 1].set_xlabel('提前天数')
    axes[1, 1].set_ylabel('价格 (元)')

    plt.tight_layout()
    plt.savefig(f'{output_dir}/price_analysis.png', dpi=300, bbox_inches='tight')
    print(f"保存: {output_dir}/price_analysis.png")
    plt.close()

    # 2. 时间特征分析
    print("[2] 时间特征分析...")
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))

    # 起飞时段分布
    if '起飞时段' in df_featured.columns:
        df_featured['起飞时段'].value_counts().plot(kind='bar', ax=axes[0, 0])
        axes[0, 0].set_title('起飞时段分布')
        axes[0, 0].set_xlabel('起飞时段')
        axes[0, 0].set_ylabel('航班数')
        axes[0, 0].tick_params(axis='x', rotation=45)

    # 飞行时长分布
    if '飞行时长_分钟' in df_featured.columns:
        axes[0, 1].hist(df_featured['飞行时长_分钟'], bins=30, edgecolor='black', alpha=0.7)
        axes[0, 1].set_title('飞行时长分布')
        axes[0, 1].set_xlabel('飞行时长 (分钟)')
        axes[0, 1].set_ylabel('频数')

    # 中转次数分布
    if '中转次数' in df_featured.columns:
        df_featured['中转次数'].value_counts().sort_index().plot(kind='bar', ax=axes[1, 0])
        axes[1, 0].set_title('中转次数分布')
        axes[1, 0].set_xlabel('中转次数')
        axes[1, 0].set_ylabel('航班数')
        axes[1, 0].tick_params(axis='x', rotation=0)

    # 剩余座位分布
    axes[1, 1].hist(df['剩余座位'], bins=20, edgecolor='black', alpha=0.7)
    axes[1, 1].set_title('剩余座位分布')
    axes[1, 1].set_xlabel('剩余座位数')
    axes[1, 1].set_ylabel('频数')

    plt.tight_layout()
    plt.savefig(f'{output_dir}/time_analysis.png', dpi=300, bbox_inches='tight')
    print(f"保存: {output_dir}/time_analysis.png")
    plt.close()

    # 3. 相关性分析
    print("[3] 相关性分析...")
    numerical_cols = ['提前天数', '剩余座位', '价格', '飞行时长_分钟', '中转时长_分钟', '中转次数', '性价比']
    numerical_cols = [col for col in numerical_cols if col in df_featured.columns]

    if len(numerical_cols) > 1:
        correlation_matrix = df_featured[numerical_cols].corr()

        plt.figure(figsize=(10, 8))
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0,
                    square=True, linewidths=1, cbar_kws={"shrink": 0.8})
        plt.title('特征相关性热力图')
        plt.tight_layout()
        plt.savefig(f'{output_dir}/correlation_heatmap.png', dpi=300, bbox_inches='tight')
        print(f"保存: {output_dir}/correlation_heatmap.png")
        plt.close()

    # 4. 综合分析图
    print("[4] 生成综合分析图...")
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))

    # 航司市场份额
    if '航司' in df.columns:
        df['航司'].value_counts().head(10).plot(kind='pie', ax=axes[0, 0], autopct='%1.1f%%')
        axes[0, 0].set_title('航司市场份额 (前10)')
        axes[0, 0].set_ylabel('')

    # 价格区间分布
    if '价格区间' in df_featured.columns:
        df_featured['价格区间'].value_counts().plot(kind='bar', ax=axes[0, 1])
        axes[0, 1].set_title('价格区间分布')
        axes[0, 1].set_xlabel('价格区间')
        axes[0, 1].set_ylabel('航班数')
        axes[0, 1].tick_params(axis='x', rotation=45)

    # 座位状态分布
    if '座位状态' in df_featured.columns:
        df_featured['座位状态'].value_counts().plot(kind='bar', ax=axes[1, 0])
        axes[1, 0].set_title('座位状态分布')
        axes[1, 0].set_xlabel('座位状态')
        axes[1, 0].set_ylabel('航班数')
        axes[1, 0].tick_params(axis='x', rotation=45)

    # 效率评分分布
    if '效率评分' in df_featured.columns:
        axes[1, 1].hist(df_featured['效率评分'], bins=30, edgecolor='black', alpha=0.7)
        axes[1, 1].set_title('效率评分分布')
        axes[1, 1].set_xlabel('效率评分')
        axes[1, 1].set_ylabel('频数')

    plt.tight_layout()
    plt.savefig(f'{output_dir}/comprehensive_analysis.png', dpi=300, bbox_inches='tight')
    print(f"保存: {output_dir}/comprehensive_analysis.png")
    plt.close()

    return output_dir

def generate_summary_report(df, df_featured, output_dir):
    """生成分析摘要报告"""
    print("\n" + "="*80)
    print("生成分析报告")
    print("="*80)

    report_path = f'{output_dir}/analysis_report.txt'

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("航班数据分析报告\n")
        f.write("="*80 + "\n\n")

        # 1. 数据概览
        f.write("一、数据概览\n")
        f.write("-"*80 + "\n")
        f.write(f"数据集大小: {df.shape[0]} 行 x {df.shape[1]} 列\n")
        f.write(f"数据采集时间范围: {df['采集日期'].min()} 至 {df['采集日期'].max()}\n")
        f.write(f"航班起飞时间范围: {df['起飞日期'].min()} 至 {df['起飞日期'].max()}\n\n")

        # 2. 价格分析
        f.write("二、价格分析\n")
        f.write("-"*80 + "\n")
        f.write(f"平均价格: {df['价格'].mean():.2f} 元\n")
        f.write(f"价格中位数: {df['价格'].median():.2f} 元\n")
        f.write(f"最低价格: {df['价格'].min():.2f} 元\n")
        f.write(f"最高价格: {df['价格'].max():.2f} 元\n")
        f.write(f"价格标准差: {df['价格'].std():.2f} 元\n\n")

        # 3. 航司分析
        f.write("三、航司分析\n")
        f.write("-"*80 + "\n")
        f.write(f"航司数量: {df['航司'].nunique()}\n")
        f.write(f"\n航司航班数量排名 (前5):\n")
        for i, (airline, count) in enumerate(df['航司'].value_counts().head(5).items(), 1):
            f.write(f"  {i}. {airline}: {count} 个航班\n")
        f.write(f"\n航司平均价格排名 (前5):\n")
        for i, (airline, price) in enumerate(df.groupby('航司')['价格'].mean().sort_values(ascending=False).head(5).items(), 1):
            f.write(f"  {i}. {airline}: {price:.2f} 元\n\n")

        # 4. 时间特征分析
        if '飞行时长_分钟' in df_featured.columns:
            f.write("四、时间特征分析\n")
            f.write("-"*80 + "\n")
            f.write(f"平均飞行时长: {df_featured['飞行时长_分钟'].mean()/60:.2f} 小时\n")
            f.write(f"最短飞行时长: {df_featured['飞行时长_分钟'].min()/60:.2f} 小时\n")
            f.write(f"最长飞行时长: {df_featured['飞行时长_分钟'].max()/60:.2f} 小时\n\n")

        # 5. 中转分析
        if '中转次数' in df_featured.columns:
            f.write("五、中转分析\n")
            f.write("-"*80 + "\n")
            f.write(f"中转航班占比: {(df_featured['中转次数'] > 0).sum() / len(df) * 100:.2f}%\n")
            f.write(f"\n中转次数分布:\n")
            for transfer_count, count in df_featured['中转次数'].value_counts().sort_index().items():
                f.write(f"  {transfer_count} 次中转: {count} 个航班 ({count/len(df)*100:.2f}%)\n")
            f.write("\n")

        # 6. 座位分析
        f.write("六、座位分析\n")
        f.write("-"*80 + "\n")
        f.write(f"平均剩余座位: {df['剩余座位'].mean():.2f}\n")
        f.write(f"最少剩余座位: {df['剩余座位'].min()}\n")
        f.write(f"最多剩余座位: {df['剩余座位'].max()}\n")
        if '座位状态' in df_featured.columns:
            f.write(f"\n座位状态分布:\n")
            for status, count in df_featured['座位状态'].value_counts().items():
                f.write(f"  {status}: {count} 个航班 ({count/len(df)*100:.2f}%)\n")
        f.write("\n")

        # 7. 提前预订分析
        f.write("七、提前预订分析\n")
        f.write("-"*80 + "\n")
        f.write(f"平均提前天数: {df['提前天数'].mean():.2f} 天\n")
        f.write(f"最短提前天数: {df['提前天数'].min()} 天\n")
        f.write(f"最长提前天数: {df['提前天数'].max()} 天\n\n")

        # 8. 提取的特征列表
        f.write("八、特征工程总结\n")
        f.write("-"*80 + "\n")
        f.write(f"原始特征数量: {len(df.columns)}\n")
        f.write(f"新增特征数量: {len(df_featured.columns) - len(df.columns)}\n")
        f.write(f"总特征数量: {len(df_featured.columns)}\n\n")
        f.write("新增特征列表:\n")
        new_features = set(df_featured.columns) - set(df.columns)
        for i, feature in enumerate(sorted(new_features), 1):
            f.write(f"  {i}. {feature}\n")

        f.write("\n" + "="*80 + "\n")
        f.write("报告生成完毕\n")
        f.write("="*80 + "\n")

    print(f"分析报告已保存: {report_path}")
    return report_path

def main():
    """主函数"""
    print("\n" + "="*80)
    print("航班数据分析和特征提取系统")
    print("="*80 + "\n")

    # 数据文件路径
    data_file = 'szx_yih_flight_data_cn.csv'

    # 1. 加载数据
    print("步骤 1: 加载数据...")
    df = load_data(data_file)

    # 2. 基础统计分析
    print("\n步骤 2: 基础统计分析...")
    basic_statistics(df)

    # 3. 特征工程
    print("\n步骤 3: 特征工程...")
    df_featured = feature_engineering(df)

    # 4. 保存特征数据
    print("\n步骤 4: 保存特征数据...")
    featured_output = 'flight_data_featured.csv'
    df_featured.to_csv(featured_output, index=False, encoding='utf-8-sig')
    print(f"特征数据已保存: {featured_output}")

    # 5. 探索性数据分析和可视化
    print("\n步骤 5: 探索性数据分析和可视化...")
    output_dir = exploratory_analysis(df, df_featured)

    # 6. 生成分析报告
    print("\n步骤 6: 生成分析报告...")
    report_path = generate_summary_report(df, df_featured, output_dir)

    print("\n" + "="*80)
    print("分析完成!")
    print("="*80)
    print(f"\n生成文件:")
    print(f"  1. {featured_output} - 特征数据集")
    print(f"  2. {output_dir}/price_analysis.png - 价格分析图")
    print(f"  3. {output_dir}/time_analysis.png - 时间特征分析图")
    print(f"  4. {output_dir}/correlation_heatmap.png - 相关性热力图")
    print(f"  5. {output_dir}/comprehensive_analysis.png - 综合分析图")
    print(f"  6. {report_path} - 分析报告")
    print("\n")

if __name__ == "__main__":
    main()
