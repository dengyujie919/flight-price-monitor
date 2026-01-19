import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

#  1. 模拟生成历史数据
# 假设规律：离起飞越近(days_before越小)，价格越贵
def create_mock_data():
    np.random.seed(42)
    n_samples = 1000
    
    days_before = np.random.randint(1, 60, n_samples) # 提前1-60天
    airline_codes = np.random.choice([0, 1, 2], n_samples) # 假设有3家航司
    
    # 模拟价格公式：基础价 + (60 - 提前天数)*10 + 随机波动
    prices = 500 + (60 - days_before) * 10 + np.random.normal(0, 50, n_samples)
    
    return pd.DataFrame({
        'days_before': days_before,
        'airline': airline_codes,
        'price': prices
    })

# --- 2. 训练模型 ---
print("正在生成模拟数据并训练模型...")
data = pd.read_csv('flight_data.csv') # 如果你有真实 csv，用 pd.read_csv('flight_data.csv') 替换这行

# 特征与目标
X = data[['days_before', 'airline']]
y = data['price']

# 训练
model = RandomForestRegressor(n_estimators=100)
model.fit(X, y)
print("模型训练完成！")

# --- 3. 进行预测 ---
print("-" * 30)
print("开始预测...")

# 假设我想查：提前 3 天买，航司代码为 1 的机票价格
input_data = [[3, 1]] 
predicted_price = model.predict(input_data)

print(f"预测情况：提前 3 天购买，预计价格为：{predicted_price[0]:.2f} 元")

# 对比一下：提前 50 天买
cheap_input = [[50, 1]]
cheap_price = model.predict(cheap_input)
print(f"预测情况：提前 50 天购买，预计价格为：{cheap_price[0]:.2f} 元")