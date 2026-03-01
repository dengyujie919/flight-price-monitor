import pandas as pd
from amadeus import Client, ResponseError
from datetime import datetime, timedelta
import os
import time
import re
import sys

# --- 1. 初始化配置 ---
def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

API_KEY = os.environ.get('AMADEUS_CLIENT_ID')
API_SECRET = os.environ.get('AMADEUS_CLIENT_SECRET')

if not API_KEY or not API_SECRET:
    log("❌ 错误：未找到 API 密钥。")
    sys.exit(1)

ORIGIN = 'SZX'        
DESTINATION = 'YIH'   
SCAN_DAYS = 30        
# 使用绝对路径确保数据写入正确位置
# collector 在 src/collectors/ 目录下，需要向上两级到项目根目录
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
FILE_NAME = os.path.join(PROJECT_ROOT, 'data', 'raw', 'szx_yih_flight_data_cn.csv')

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
    total_wait_seconds = 0
    layover_locs = []
    for i in range(len(segments) - 1):
        layover_locs.append(segments[i]['arrival']['iataCode'])
        arr = datetime.strptime(segments[i]['arrival']['at'], "%Y-%m-%dT%H:%M:%S")
        dep = datetime.strptime(segments[i+1]['departure']['at'], "%Y-%m-%dT%H:%M:%S")
        total_wait_seconds += (dep - arr).total_seconds()
    return "/".join(layover_locs), f"{int(total_wait_seconds // 3600)}h{int((total_wait_seconds % 3600) // 60)}m"

# --- 3. 主程序 ---

def run_daily_scan():
    # 关闭 debug 模式，保持清爽
    amadeus = Client(client_id=API_KEY, client_secret=API_SECRET)
    
    fetch_date = datetime.now().strftime('%Y-%m-%d')
    today = datetime.now()
    buffer_data = []

    log(f"🚀 开始采集: {ORIGIN} -> {DESTINATION} (未来 {SCAN_DAYS} 天)")
    log("-" * 50)

    for i in range(1, SCAN_DAYS + 1):
        target_date = (today + timedelta(days=i)).strftime('%Y-%m-%d')
        # 紧凑型进度打印
        progress = f"🔎 [{i:02d}/{SCAN_DAYS}] {target_date}"
        
        try:
            response = amadeus.shopping.flight_offers_search.get(
                originLocationCode=ORIGIN,
                destinationLocationCode=DESTINATION,
                departureDate=target_date,
                adults=1
            )
            
            if not response.data:
                print(f"{progress} -> ℹ️ 无航班", flush=True)
                continue

            daily_flights = []
            for flight in response.data:
                itinerary = flight['itineraries'][0]
                segments = itinerary['segments']
                
                daily_flights.append({
                    '采集日期': fetch_date,
                    '起飞日期': target_date,
                    '提前天数': i,
                    '航班号': segments[0]['carrierCode'] + segments[0]['number'],
                    '航司': flight['validatingAirlineCodes'][0],
                    '类型': "直飞" if len(segments) == 1 else "中转",
                    '起飞时间': segments[0]['departure']['at'].split('T')[1][:5],
                    '到达时间': segments[-1]['arrival']['at'].split('T')[1][:5],
                    '总时长': parse_duration(itinerary['duration']),
                    '中转地': calculate_layover(segments)[0],
                    '中转时长': calculate_layover(segments)[1],
                    '剩余座位': flight['numberOfBookableSeats'],
                    '价格': float(flight['price']['total']),
                    '_dept': segments[0]['departure']['at'],
                    '_arr': segments[-1]['arrival']['at']
                })

            if daily_flights:
                df = pd.DataFrame(daily_flights)
                df = df.sort_values(by='价格').drop_duplicates(subset=['_dept', '_arr'], keep='first')
                df = df.drop(columns=['_dept', '_arr'])
                buffer_data.append(df)
                print(f"{progress} -> ✅ 抓取到 {len(df)} 条数据", flush=True)

        except ResponseError as e:
            print(f"{progress} -> ❌ API错误: {e}", flush=True)
        
        time.sleep(0.2) # 稍微缩短间隔

   # --- 保存逻辑 ---
    if buffer_data:
        final_df = pd.concat(buffer_data, ignore_index=True)
        
        # 检查文件是否已经存在
        file_exists = os.path.isfile(FILE_NAME)
        
        if not file_exists:
            # 如果文件不存在，创建新文件，包含表头
            final_df.to_csv(FILE_NAME, index=False, encoding='utf-8-sig')
            log(f"✨ 首次运行，已创建新文件: {FILE_NAME}")
        else:
            # 如果文件已存在，使用 mode='a' (append) 追加数据
            # header=False 表示不重复写入表头
            final_df.to_csv(FILE_NAME, mode='a', index=False, header=False, encoding='utf-8-sig')
            log(f"💾 数据已追加至现有文件: {FILE_NAME}")
    else:
        log("⚠️ 本次未采集到数据，文件未更新。")
if __name__ == "__main__":
    run_daily_scan()