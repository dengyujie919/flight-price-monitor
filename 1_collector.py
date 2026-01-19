import pandas as pd
from amadeus import Client, ResponseError
from datetime import datetime
import os
from dotenv import load_dotenv

# 1. 加载密钥
load_dotenv() 
API_KEY = os.getenv('AMADEUS_CLIENT_ID')     
API_SECRET = os.getenv('AMADEUS_CLIENT_SECRET')

# --- 配置区域 ---
ORIGIN = 'SZX'               # 深圳
DESTINATION = 'YIH'          # 宜昌
DATE = '2026-01-23'          # 目标日期
# ----------------

def fetch_and_save():
    # 检查密钥是否存在
    if not API_KEY or not API_SECRET:
        print("错误：未找到 API 密钥，请检查 .env 文件。")
        return

    amadeus = Client(client_id=API_KEY, client_secret=API_SECRET)

    try:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 正在搜索 {DATE} SZX -> YIH 的余票和价格...")
        
        response = amadeus.shopping.flight_offers_search.get(
            originLocationCode=ORIGIN,
            destinationLocationCode=DESTINATION,
            departureDate=DATE,
            adults=1
        )

        data_list = []
        if not response.data:
            print("未找到航班信息。")
            return

        for flight in response.data:
            # --- 核心修改：提取剩余座位数 ---
            # Amadeus 返回的 numberOfBookableSeats 通常最大显示为 9 (代表9个及以上)
            seats_left = flight['numberOfBookableSeats']
            
            price = float(flight['price']['total'])
            airline = flight['validatingAirlineCodes'][0]
            flight_number = flight['itineraries'][0]['segments'][0]['number'] # 提取航班号，区分不同航班
            
            # 计算提前天数
            days_before = (datetime.strptime(DATE, "%Y-%m-%d") - datetime.now()).days
            
            data_list.append({
                'fetch_date': datetime.now().strftime('%Y-%m-%d %H:%M'), # 记录抓取时间
                'flight_number': flight_number, # 新增：航班号 (如 ZH9123)
                'days_before': days_before,
                'airline': airline,
                'seats_left': seats_left,       # 新增：剩余座位
                'price': price
            })

        # --- 保存数据 ---
        df = pd.DataFrame(data_list)
        file_name = 'flight_data_detailed.csv' # 换了个文件名，避免和旧格式冲突
        
        # 智能表头处理
        if not os.path.exists(file_name):
            df.to_csv(file_name, index=False)
            print(f"新建文件并保存了 {len(df)} 条数据 (含座位信息)。")
        else:
            df.to_csv(file_name, mode='a', header=False, index=False)
            print(f"成功追加 {len(df)} 条数据。")
            
            # --- 简单的数据透视 (让你看一眼现在的行情) ---
            print("\n--- 当前最低价 Top 3 ---")
            print(df[['flight_number', 'seats_left', 'price']].sort_values(by='price').head(3))

    except ResponseError as error:
        print(f"API 报错: {error}")

if __name__ == "__main__":
    fetch_and_save()