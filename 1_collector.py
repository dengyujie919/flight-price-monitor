import pandas as pd
from amadeus import Client, ResponseError
from datetime import datetime, timedelta
import os
import time
import re
from dotenv import load_dotenv

# --- 1. 初始化配置 ---
load_dotenv()
API_KEY = os.getenv('AMADEUS_CLIENT_ID')
API_SECRET = os.getenv('AMADEUS_CLIENT_SECRET')

ORIGIN = 'SZX'        
DESTINATION = 'YIH'   
SCAN_DAYS = 30        
FILE_NAME = 'szx_yih_flight_data_cn.csv' # 中文版数据文件

# --- 2. 辅助工具函数：处理时间格式 ---

def parse_duration(iso_duration):
    """
    将 API 返回的 PT2H35M 格式转换为 '2小时35分'
    """
    if not iso_duration:
        return ""
    # 使用正则提取小时(H)和分钟(M)
    hours = re.search(r'(\d+)H', iso_duration)
    minutes = re.search(r'(\d+)M', iso_duration)
    
    h_str = f"{hours.group(1)}小时" if hours else ""
    m_str = f"{minutes.group(1)}分" if minutes else ""
    return h_str + m_str

def calculate_layover(segments):
    """
    计算中转信息
    返回: (中转地字符串, 中转总时长字符串)
    """
    if len(segments) < 2:
        return "无", "0"
    
    layover_locs = []
    total_wait_seconds = 0
    
    # 遍历每一段，计算上一段到达和下一段起飞的差值
    for i in range(len(segments) - 1):
        # 上一段的到达机场即为中转地
        loc = segments[i]['arrival']['iataCode']
        layover_locs.append(loc)
        
        # 计算等待时间
        arrival_time = datetime.strptime(segments[i]['arrival']['at'], "%Y-%m-%dT%H:%M:%S")
        next_dept_time = datetime.strptime(segments[i+1]['departure']['at'], "%Y-%m-%dT%H:%M:%S")
        
        wait_seconds = (next_dept_time - arrival_time).total_seconds()
        total_wait_seconds += wait_seconds

    # 格式化输出
    loc_str = "/".join(layover_locs) # 如果有多次中转，用 / 隔开
    
    # 将秒转换为小时分钟
    wait_h = int(total_wait_seconds // 3600)
    wait_m = int((total_wait_seconds % 3600) // 60)
    time_str = f"{wait_h}小时{wait_m}分"
    
    return loc_str, time_str

# --- 3. 主程序 ---

def run_daily_scan():
    if not API_KEY or not API_SECRET:
        print("❌ 错误：未找到 .env 密钥。")
        return

    amadeus = Client(client_id=API_KEY, client_secret=API_SECRET)
    fetch_date = datetime.now().strftime('%Y-%m-%d')
    today = datetime.now()
    
    print(f"🚀 [中文增强版] 开始采集 {fetch_date} 的数据")
    print(f"📡 监控航线: {ORIGIN} -> {DESTINATION}")
    print("-" * 60)

    buffer_data = []

    for i in range(1, SCAN_DAYS + 1):
        target_date_obj = today + timedelta(days=i)
        target_date_str = target_date_obj.strftime('%Y-%m-%d')
        
        print(f"   正在搜索: {target_date_str} (提前 {i} 天)...", end="")
        
        try:
            response = amadeus.shopping.flight_offers_search.get(
                originLocationCode=ORIGIN,
                destinationLocationCode=DESTINATION,
                departureDate=target_date_str,
                adults=1
            )
            
            if not response.data:
                print(" [无航班]")
                continue

            daily_flights = []
            
            for flight in response.data:
                # 提取基础数据
                price = float(flight['price']['total'])
                airline = flight['validatingAirlineCodes'][0]
                seats_left = flight['numberOfBookableSeats']
                
                # 提取航段信息
                itinerary = flight['itineraries'][0]
                segments = itinerary['segments']
                
                # 1. 飞行总时长 (API直接提供)
                total_duration_str = parse_duration(itinerary['duration'])
                
                # 2. 计算中转详情
                layover_loc, layover_time = calculate_layover(segments)
                
                # 3. 判断是否直飞
                flight_type = "直飞" if len(segments) == 1 else "中转"
                
                # 4. 获取起降时间 (用于去重)
                dept_time = segments[0]['departure']['at']
                arr_time = segments[-1]['arrival']['at']
                
                # 5. 格式化时间显示 (把 2026-02-01T14:30:00 变成 14:30)
                dept_time_readable = dept_time.split('T')[1][:5]
                arr_time_readable = arr_time.split('T')[1][:5]
                
                # 6. 航班号
                flight_number = segments[0]['carrierCode'] + segments[0]['number']

                # 构建中文数据字典
                daily_flights.append({
                    '采集日期': fetch_date,
                    '起飞日期': target_date_str,
                    '提前天数': i,
                    '航班号': flight_number,
                    '航司': airline,
                    '类型': flight_type,
                    '起飞时间': dept_time_readable,
                    '到达时间': arr_time_readable,
                    '总时长': total_duration_str,
                    '中转地': layover_loc,
                    '中转时长': layover_time,
                    '剩余座位': seats_left,
                    '价格': price,
                    # 下面这两个隐藏字段用于技术去重，保存时可以考虑去掉
                    '_dept_full': dept_time,
                    '_arr_full': arr_time
                })

            # --- 合并代码共享 (去重逻辑) ---
            if daily_flights:
                df_daily = pd.DataFrame(daily_flights)
                
                # 按价格排序，保留最便宜的
                df_daily = df_daily.sort_values(by='价格', ascending=True)
                # 根据 完整起飞时间 和 完整到达时间 去重
                df_daily = df_daily.drop_duplicates(subset=['_dept_full', '_arr_full'], keep='first')
                
                # 删除辅助列 (不想存到CSV里的列)
                df_daily = df_daily.drop(columns=['_dept_full', '_arr_full'])
                
                buffer_data.append(df_daily)
                print(f" ✅ 已存 {len(df_daily)} 条")
            else:
                print(" [0 条]")

        except ResponseError as error:
            print(f" ❌ API 报错: {error}")
        except Exception as e:
            print(f" ❌ 错误: {e}")
            
        time.sleep(1) 

    # --- 保存 ---
    if buffer_data:
        final_df = pd.concat(buffer_data, ignore_index=True)
        
        # 按照 起飞日期 和 价格 排序，看着更舒服
        final_df = final_df.sort_values(by=['起飞日期', '价格'])
        
        if not os.path.exists(FILE_NAME):
            final_df.to_csv(FILE_NAME, index=False, encoding='utf-8-sig') # utf-8-sig 防止Excel打开中文乱码
            print(f"\n✨ 新建文件: {FILE_NAME}")
        else:
            final_df.to_csv(FILE_NAME, mode='a', header=False, index=False, encoding='utf-8-sig')
            print(f"\n💾 追加数据到: {FILE_NAME}")
    else:
        print("\n⚠️ 本次无数据")

if __name__ == "__main__":
    run_daily_scan()