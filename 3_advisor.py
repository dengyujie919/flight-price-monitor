import pandas as pd
from datetime import datetime, timedelta
import joblib # 用于加载训练好的模型

# 假设你已经训练好了模型并保存为 'flight_model.pkl'
# model = joblib.load('flight_model.pkl') 

# 为了演示，我们先定义一个模拟的预测函数 (等你数据够了就替换成真的模型)
def predict_price_by_days_before(days):
    # 模拟逻辑：提前20-30天最便宜，越临近越贵
    if days > 30: return 800  # 还没降价
    if 20 <= days <= 30: return 500 # 最佳窗口期
    if days < 20: return 500 + (20-days)*50 # 临近起飞疯涨
    return 9999

def get_buying_advice(target_date_str):
    target_date = datetime.strptime(target_date_str, "%Y-%m-%d")
    today = datetime.now()
    
    # 1. 计算今天离起飞还有几天
    days_left_now = (target_date - today).days
    
    if days_left_now <= 0:
        print("这趟飞机已经起飞或就是今天，没法预测了，赶紧买吧！")
        return

    print(f"--- 正在分析 {target_date_str} 的航班 (距离现在还有 {days_left_now} 天) ---")

    # 2. 获取今天的预测价格
    current_pred_price = predict_price_by_days_before(days_left_now)
    print(f"当前预测价格: {current_pred_price} 元")

    # 3. 模拟“未来每一天”的价格变化
    # 我们看看如果不今天买，而是明天、后天...直到起飞前买，价格会由多少？
    future_prices = []
    
    for wait_days in range(1, days_left_now):
        # 如果等 wait_days 天，那么离起飞就只剩 (days_left_now - wait_days) 天了
        future_days_before = days_left_now - wait_days
        predicted_p = predict_price_by_days_before(future_days_before)
        
        check_date = (today + timedelta(days=wait_days)).strftime('%m-%d')
        future_prices.append({
            'wait_days': wait_days,
            'date': check_date,
            'price': predicted_p
        })

    # 4. 寻找最低价
    # 把未来的价格放入 DataFrame 方便查找
    df_future = pd.DataFrame(future_prices)
    
    if df_future.empty:
        print("离起飞太近了，没得选，建议立刻购买！")
        return

    min_price_row = df_future.loc[df_future['price'].idxmin()]
    min_price = min_price_row['price']
    best_wait_days = min_price_row['wait_days']
    best_date = min_price_row['date']

    # 5. 给出建议
    print("-" * 30)
    if min_price < current_pred_price:
        diff = current_pred_price - min_price
        print(f"💡 建议：**再等等！**")
        print(f"预计在 {best_date} (等待 {best_wait_days} 天后) 购买最划算。")
        print(f"届时价格可能为 {min_price} 元，比现在省 {diff} 元。")
    else:
        print(f"🔥 建议：**立刻购买！**")
        print(f"未来的预测价格都比现在高，越等越贵。")

# --- 运行测试 ---
# 假设你想查 2月20日 的票
get_buying_advice('2026-01-25')