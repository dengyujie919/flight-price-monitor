import pandas as pd
from amadeus import Client, ResponseError
from datetime import datetime, timedelta
import os
import time
import re
import sys

# --- 1. 初始化配置 ---
# 强制开启打印同步，防止 GitHub Actions 日志缓冲
def log(msg):
    print(f"{msg}", flush=True)

# 仅从环境变量读取，GitHub Actions 会注入这些变量
API_KEY = os.environ.get('AMADEUS_CLIENT_ID')
API_SECRET = os.environ.get('AMADEUS_CLIENT_SECRET')

# 如果你想在本地运行，请取消下面两行的注释并填入你的 Key
# API_KEY = "你的KEY"
# API_SECRET = "你的SECRET"

if not API_KEY or not API_SECRET:
    log("❌ 错误：环境变量中未找到 API 密钥。")
    sys.exit(1)

ORIGIN = 'SZX'        
DESTINATION = 'YIH'   
SCAN_DAYS = 30        
FILE_NAME = 'szx_yih_flight_data_cn.csv'

# --- 2. 辅助工具函数 ---

def parse_duration(iso_duration):
    if not iso_duration: return ""
    hours = re.search(r'(\d+)H', iso_duration)
    minutes = re.search(r'(\d+)M', iso_duration)
    h_str = f"{hours.group(1)}小时" if hours else ""
    m_str = f"{minutes.group(1)}分" if minutes else ""
    return h_str + m_str

def calculate_layover(segments):
    if len(segments) < 2: return "无", "0"
    layover_locs = []
    total_wait_seconds = 0
    for i in range(len(segments) - 1):
        loc = segments[i]['arrival']['iataCode']
        layover_locs.append(loc)
        arrival_time = datetime.strptime(segments[i]['arrival']['at'], "%Y-%m-%dT%H:%M:%S")
        next_dept_time = datetime.strptime(segments[i+1]['departure']['at'], "%Y-%m-%dT%H:%M:%S")
        total_wait_seconds += (next_dept_time - arrival_time).total_seconds()
    return "/".join(layover_locs), f"{int(total_wait_seconds // 3600)}小时{int((total_wait_seconds % 3600) // 60)}分"

# --- 3. 主程序 ---

def run_daily_scan():
    log(f"🚀 脚本启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 增加调试日志级别，这会强制 SDK 输出它的所有动作
    amadeus = Client(
        client_id=API_KEY, 
        client_secret=API_SECRET,
        log_level='debug' 
    )
    
    fetch_date = datetime.now().strftime('%Y-%m-%d')
    today = datetime.now()
    buffer_data = []

    log(f"📡 监控航线: {ORIGIN} -> {DESTINATION} (未来 {SCAN_DAYS} 天)")
    log("-" * 40)

    for i in range(1, SCAN_DAYS + 1):
        target_date_str = (today + timedelta(days=i)).strftime('%Y-%m-%d')
        log(f"🔎 [{i}/{SCAN_DAYS}] 正在搜索: {target_date_str}...")
        
        try:
            # 增加一个简单的重试逻辑或等待
            response = amadeus.shopping.flight_offers_search.get(
                originLocationCode=ORIGIN,
                destinationLocationCode=DESTINATION,
                departureDate=target_date_str,
                adults=1
            )
            
            if not response.data:
                log("   ⚠️ 无航班记录")
                continue

            daily_flights = []
            for flight in response.data:
                price = float(flight['price']['total'])
                airline = flight['validatingAirlineCodes'][0]
                seats_left = flight['numberOfBookableSeats']
                itinerary = flight['itineraries'][0]
                segments = itinerary['segments']
                
                dept_full = segments[0]['departure']['at']
                arr_full = segments[-1]['arrival']['at']

                daily_flights.append({
                    '采集日期': fetch_date,
                    '起飞日期': target_date_str,
                    '提前天数': i,
                    '航班号': segments[0]['carrierCode'] + segments[0]['number'],
                    '航司': airline,
                    '类型': "直飞" if len(segments) == 1 else "中转",
                    '起飞时间': dept_full.split('T')[1][:5],
                    '到达时间': arr_full.split('T')[1][:5],
                    '总时长': parse_duration(itinerary['duration']),
                    '中转地': calculate_layover(segments)[0],
                    '中转时长': calculate_layover(segments)[1],
                    '剩余座位': seats_left,
                    '价格': price,
                    '_dept_full': dept_full,
                    '_arr_full': arr_full
                })

            if daily_flights:
                df_daily = pd.DataFrame(daily_flights)
                df_daily = df_daily.sort_values(by='价格').drop_duplicates(subset=['_dept_full', '_arr_full'], keep='first')
                df_daily = df_daily.drop(columns=['_dept_full', '_arr_full'])
                buffer_data.append(df_daily)
                log(f"   ✅ 成功提取 {len(df_daily)} 条航班信息")

        except ResponseError as error:
            log(f"   ❌ API调用失败: {error}")
        except Exception as e:
            log(f"   ❌ 程序异常: {e}")
        
        time.sleep(0.5) # 稍微快一点

    if buffer_data:
        final_df = pd.concat(buffer_data, ignore_index=True)
        final_df.to_csv(FILE_NAME, index=False, encoding='utf-8-sig')
        log(f"\n🎉 任务完成！数据已保存至 {FILE_NAME}")
    else:
        log("\n⚠️ 遍历结束，未采集到任何数据。")

if __name__ == "__main__":
    run_daily_scan()