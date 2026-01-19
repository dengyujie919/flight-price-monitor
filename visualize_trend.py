import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import platform

# --- 1. 配置中文字体 (最关键的一步) ---
# 否则图表上的中文会变成方框
system_name = platform.system()
if system_name == "Windows":
    plt.rcParams['font.sans-serif'] = ['SimHei']  # Windows 黑体
elif system_name == "Darwin":
    plt.rcParams['font.sans-serif'] = ['Arial Unicode MS'] # Mac 通用中文
else:
    plt.rcParams['font.sans-serif'] = ['WenQuanYi Micro Hei'] # Linux

plt.rcParams['axes.unicode_minus'] = False # 解决负号显示问题

# --- 2. 读取数据 ---
FILE_NAME = 'szx_yih_flight_data_cn.csv' # 确保文件名和你生成的一致

try:
    df = pd.read_csv(FILE_NAME)
    print(f"✅ 成功读取 {len(df)} 条数据")
except FileNotFoundError:
    print(f"❌ 没找到文件 {FILE_NAME}，请先运行采集脚本！")
    exit()

# 数据预处理
# 确保价格是数字
df['价格'] = pd.to_numeric(df['价格'], errors='coerce')
# 转换日期格式
df['起飞日期'] = pd.to_datetime(df['起飞日期'])

# --- 图表 1: 未来 30 天价格走势 (哪天飞最便宜？) ---
plt.figure(figsize=(12, 6))

# 找出每一天起飞的最低价 (去重，只看每天的最低门槛)
min_price_per_day = df.groupby('起飞日期')['价格'].min().reset_index()

# 画折线图
sns.lineplot(data=min_price_per_day, x='起飞日期', y='价格', marker='o', color='#1f77b4', linewidth=2.5)

# 标出最低价的点
min_row = min_price_per_day.loc[min_price_per_day['价格'].idxmin()]
plt.annotate(f"最低: {min_row['价格']}元\n({min_row['起飞日期'].strftime('%m-%d')})", 
             xy=(min_row['起飞日期'], min_row['价格']), 
             xytext=(0, 20), textcoords='offset points',
             arrowprops=dict(arrowstyle="->", color='red'),
             color='red', fontweight='bold')

plt.title('未来30天航班最低价格走势 (深圳 -> 宜昌)', fontsize=15)
plt.xlabel('起飞日期', fontsize=12)
plt.ylabel('最低票价 (元)', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.6)
plt.xticks(rotation=45)
plt.tight_layout()

print("📊正在生成：价格走势图...")
plt.show()

# --- 图表 2: 价格 vs 提前天数 (提前多久买划算？) ---
# 注意：这张图需要你有较多数据时才更有意义
plt.figure(figsize=(10, 6))

# 画散点图，看看"提前天数"和"价格"的关系
sns.scatterplot(data=df, x='提前天数', y='价格', alpha=0.6, hue='类型')

# 画一条拟合趋势线 (看看整体是涨还是跌)
sns.regplot(data=df, x='提前天数', y='价格', scatter=False, color='red', line_kws={'linestyle':'--'})

plt.title('购票策略分析：提前天数 vs 价格分布', fontsize=15)
plt.xlabel('提前预订天数 (离起飞还有几天)', fontsize=12)
plt.ylabel('票价 (元)', fontsize=12)
plt.gca().invert_xaxis() # 让 x 轴从大到小 (30 -> 1)，符合"随着时间流逝"的感觉
plt.grid(True, alpha=0.3)

print("📊正在生成：购票策略图...")
plt.show()