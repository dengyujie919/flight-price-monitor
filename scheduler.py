"""
航班价格预测系统 - 自动化调度器
====================================

自动化运行数据采集、分析和模型训练任务。

功能：
- 自动数据采集（每天2次）
- 自动数据分析（每3天）
- 自动模型训练（每周）
- 不清理历史数据（保留所有数据）

支持模式:
1. 一次性运行所有任务
2. 定时循环运行（守护进程）
3. 检查并运行到期任务

使用方法:
    python scheduler.py --mode once       # 运行一次所有到期任务
    python scheduler.py --mode daemon     # 守护进程模式
    python scheduler.py --mode check      # 仅检查状态
"""

import os
import sys
import time
import argparse
import logging
from datetime import datetime, timedelta
import pandas as pd

# 添加项目根目录到路径
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

# 导入配置
from config import *

# 设置日志
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class TaskScheduler:
    """任务调度器"""

    def __init__(self):
        self.state_file = os.path.join(PROJECT_ROOT, 'scheduler_state.json')
        self.state = self.load_state()

    def load_state(self):
        """加载调度状态"""
        import json
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"无法加载状态文件: {e}")

        # 默认状态
        return {
            'last_collection': None,
            'last_analysis': None,
            'last_training': None,
            'data_count': 0
        }

    def save_state(self):
        """保存调度状态"""
        import json
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存状态失败: {e}")

    def should_run_collection(self):
        """检查是否应该运行数据采集"""
        if self.state['last_collection'] is None:
            return True

        last_time = datetime.fromisoformat(self.state['last_collection'])
        hours_since = (datetime.now() - last_time).total_seconds() / 3600

        return hours_since >= COLLECTION_INTERVAL_HOURS

    def should_run_analysis(self):
        """检查是否应该运行数据分析"""
        if self.state['last_analysis'] is None:
            return True

        last_time = datetime.fromisoformat(self.state['last_analysis'])
        days_since = (datetime.now() - last_time).days

        # 检查时间间隔
        if days_since >= ANALYSIS_INTERVAL_DAYS:
            return True

        # 检查数据量阈值
        new_data_count = self.get_new_data_count()
        if new_data_count >= RETRAIN_THRESHOLD:
            logger.info(f"新数据量达到阈值: {new_data_count} >= {RETRAIN_THRESHOLD}")
            return True

        return False

    def should_run_training(self):
        """检查是否应该运行模型训练"""
        if self.state['last_training'] is None:
            return True

        last_time = datetime.fromisoformat(self.state['last_training'])
        days_since = (datetime.now() - last_time).days

        # 检查时间间隔
        if days_since >= TRAINING_INTERVAL_DAYS:
            return True

        # 检查数据量阈值
        new_data_count = self.get_new_data_count()
        if new_data_count >= RETRAIN_THRESHOLD:
            logger.info(f"新数据量达到训练阈值: {new_data_count} >= {RETRAIN_THRESHOLD}")
            return True

        return False

    def get_new_data_count(self):
        """获取新增数据量"""
        try:
            if os.path.exists(FEATURED_DATA_FILE):
                df = pd.read_csv(FEATURED_DATA_FILE)
                current_count = len(df)

                if self.state['data_count'] > 0:
                    return current_count - self.state['data_count']
                else:
                    return current_count
        except Exception as e:
            logger.error(f"获取数据量失败: {e}")

        return 0

    def run_collection(self):
        """运行数据采集"""
        logger.info("="*60)
        logger.info("开始数据采集任务")
        logger.info("="*60)

        try:
            from run import run_collector
            run_collector()

            self.state['last_collection'] = datetime.now().isoformat()
            self.save_state()

            logger.info("✅ 数据采集完成")
            return True

        except Exception as e:
            logger.error(f"❌ 数据采集失败: {e}")
            return False

    def run_analysis(self):
        """运行数据分析"""
        logger.info("="*60)
        logger.info("开始数据分析任务")
        logger.info("="*60)

        try:
            from run import run_analyzer
            run_analyzer()

            # 更新数据量
            if os.path.exists(FEATURED_DATA_FILE):
                df = pd.read_csv(FEATURED_DATA_FILE)
                self.state['data_count'] = len(df)

            self.state['last_analysis'] = datetime.now().isoformat()
            self.save_state()

            logger.info("✅ 数据分析完成")
            return True

        except Exception as e:
            logger.error(f"❌ 数据分析失败: {e}")
            return False

    def run_training(self):
        """运行模型训练"""
        logger.info("="*60)
        logger.info("开始模型训练任务")
        logger.info("="*60)

        try:
            from run import run_predictor
            run_predictor()

            self.state['last_training'] = datetime.now().isoformat()
            self.save_state()

            logger.info("✅ 模型训练完成")
            return True

        except Exception as e:
            logger.error(f"❌ 模型训练失败: {e}")
            return False

    def check_and_run(self):
        """检查并运行到期任务"""
        logger.info("\n" + "="*60)
        logger.info(f"任务调度检查 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("="*60)

        tasks_run = 0

        # 检查数据采集
        if self.should_run_collection():
            logger.info("\n📡 [数据采集] 任务到期，开始执行...")
            if self.run_collection():
                tasks_run += 1
        else:
            last = datetime.fromisoformat(self.state['last_collection'])
            next_run = last + timedelta(hours=COLLECTION_INTERVAL_HOURS)
            logger.info(f"📡 [数据采集] 下次运行: {next_run.strftime('%Y-%m-%d %H:%M')}")

        # 检查数据分析
        if self.should_run_analysis():
            logger.info("\n📊 [数据分析] 任务到期，开始执行...")
            if self.run_analysis():
                tasks_run += 1
        else:
            last = datetime.fromisoformat(self.state['last_analysis']) if self.state['last_analysis'] else datetime.now()
            next_run = last + timedelta(days=ANALYSIS_INTERVAL_DAYS)
            logger.info(f"📊 [数据分析] 下次运行: {next_run.strftime('%Y-%m-%d')}")

        # 检查模型训练
        if self.should_run_training():
            logger.info("\n🤖 [模型训练] 任务到期，开始执行...")
            if self.run_training():
                tasks_run += 1
        else:
            last = datetime.fromisoformat(self.state['last_training']) if self.state['last_training'] else datetime.now()
            next_run = last + timedelta(days=TRAINING_INTERVAL_DAYS)
            logger.info(f"🤖 [模型训练] 下次运行: {next_run.strftime('%Y-%m-%d')}")

        logger.info(f"\n✅ 本次检查完成，运行了 {tasks_run} 个任务")

        return tasks_run

    def show_status(self):
        """显示当前状态"""
        print("\n" + "="*60)
        print("调度器状态")
        print("="*60)

        print(f"\n📡 数据采集:")
        if self.state['last_collection']:
            last = datetime.fromisoformat(self.state['last_collection'])
            next_run = last + timedelta(hours=COLLECTION_INTERVAL_HOURS)
            print(f"  上次运行: {last.strftime('%Y-%m-%d %H:%M')}")
            print(f"  下次运行: {next_run.strftime('%Y-%m-%d %H:%M')}")
        else:
            print(f"  状态: 未运行过")

        print(f"\n📊 数据分析:")
        if self.state['last_analysis']:
            last = datetime.fromisoformat(self.state['last_analysis'])
            next_run = last + timedelta(days=ANALYSIS_INTERVAL_DAYS)
            print(f"  上次运行: {last.strftime('%Y-%m-%d')}")
            print(f"  下次运行: {next_run.strftime('%Y-%m-%d')}")
        else:
            print(f"  状态: 未运行过")

        print(f"\n🤖 模型训练:")
        if self.state['last_training']:
            last = datetime.fromisoformat(self.state['last_training'])
            next_run = last + timedelta(days=TRAINING_INTERVAL_DAYS)
            print(f"  上次运行: {last.strftime('%Y-%m-%d')}")
            print(f"  下次运行: {next_run.strftime('%Y-%m-%d')}")
        else:
            print(f"  状态: 未运行过")

        print(f"\n📈 数据统计:")
        print(f"  当前数据量: {self.state['data_count']:,} 条")
        if os.path.exists(FEATURED_DATA_FILE):
            df = pd.read_csv(FEATURED_DATA_FILE)
            print(f"  实际数据量: {len(df):,} 条")

        print("\n" + "="*60)

    def run_daemon(self, interval_minutes=60):
        """守护进程模式"""
        logger.info("🚀 启动守护进程模式...")
        logger.info(f"⏰ 检查间隔: {interval_minutes} 分钟")
        logger.info("按 Ctrl+C 停止\n")

        try:
            while True:
                self.check_and_run()

                # 等待下次检查
                logger.info(f"\n💤 等待 {interval_minutes} 分钟后进行下次检查...")
                time.sleep(interval_minutes * 60)

        except KeyboardInterrupt:
            logger.info("\n\n⏹️  收到停止信号，退出守护进程")
        except Exception as e:
            logger.error(f"守护进程错误: {e}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='航班价格预测系统 - 自动化调度器',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--mode',
        type=str,
        choices=['once', 'daemon', 'check'],
        default='once',
        help='运行模式'
    )

    parser.add_argument(
        '--interval',
        type=int,
        default=60,
        help='守护进程检查间隔（分钟）'
    )

    args = parser.parse_args()

    # 创建调度器
    scheduler = TaskScheduler()

    # 执行相应模式
    if args.mode == 'once':
        scheduler.check_and_run()

    elif args.mode == 'check':
        scheduler.show_status()

    elif args.mode == 'daemon':
        scheduler.run_daemon(args.interval)


if __name__ == "__main__":
    main()
