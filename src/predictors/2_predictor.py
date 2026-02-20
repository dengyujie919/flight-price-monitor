"""
航班价格预测器
====================

基于历史航班数据训练机器学习模型，用于预测航班价格。

功能：
1. 加载特征数据集
2. 训练随机森林回归模型
3. 评估模型性能
4. 进行价格预测
5. 可视化预测结果

作者：自动化分析系统
版本：2.0
更新日期：2026-02-20
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import LabelEncoder
import warnings
import pickle
import os

warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False


class FlightPricePredictor:
    """航班价格预测器类"""

    def __init__(self, model_type='random_forest'):
        """
        初始化预测器

        参数:
            model_type: 模型类型 ('random_forest' 或 'gradient_boosting')
        """
        self.model_type = model_type
        self.model = None
        self.feature_columns = None
        self.label_encoders = {}
        self.scaler = None

        print(f"初始化航班价格预测器 (模型: {model_type})")

    def load_data(self, filepath):
        """
        加载特征数据集

        参数:
            filepath: CSV文件路径

        返回:
            DataFrame: 加载的数据
        """
        print(f"正在加载数据: {filepath}")
        df = pd.read_csv(filepath, encoding='utf-8-sig')
        print(f"数据加载成功: {df.shape[0]} 行 x {df.shape[1]} 列")
        return df

    def prepare_features(self, df, target_column='价格'):
        """
        准备训练特征

        参数:
            df: 原始数据框
            target_column: 目标列名

        返回:
            X: 特征矩阵
            y: 目标变量
        """
        print("\n准备训练特征...")

        # 选择数值型特征
        numerical_features = [
            '提前天数', '剩余座位', '飞行时长_分钟',
            '中转时长_分钟', '中转次数', '性价比',
            '时间压力', '效率评分'
        ]

        # 选择可用的数值特征
        available_numerical = [col for col in numerical_features if col in df.columns]

        # 分类特征
        categorical_features = ['航司', '起飞时段', '价格区间', '座位状态']
        available_categorical = [col for col in categorical_features if col in df.columns]

        print(f"数值特征 ({len(available_numerical)}): {available_numerical}")
        print(f"分类特征 ({len(available_categorical)}): {available_categorical}")

        # 创建特征矩阵
        X = df[available_numerical + available_categorical].copy()

        # 编码分类特征
        for col in available_categorical:
            if col not in self.label_encoders:
                self.label_encoders[col] = LabelEncoder()
                # 处理可能的新值
                X[col] = self.label_encoders[col].fit_transform(X[col].astype(str))
            else:
                # 使用已保存的编码器
                X[col] = self.label_encoders[col].transform(X[col].astype(str))

        # 目标变量
        y = df[target_column]

        self.feature_columns = X.columns.tolist()

        print(f"特征准备完成: {X.shape}")
        return X, y

    def train(self, X, y, test_size=0.2):
        """
        训练模型

        参数:
            X: 特征矩阵
            y: 目标变量
            test_size: 测试集比例

        返回:
            dict: 训练结果和评估指标
        """
        print(f"\n开始训练模型 (测试集比例: {test_size})...")

        # 划分训练集和测试集
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )

        print(f"训练集: {X_train.shape[0]} 样本")
        print(f"测试集: {X_test.shape[0]} 样本")

        # 创建模型
        if self.model_type == 'random_forest':
            self.model = RandomForestRegressor(
                n_estimators=100,
                max_depth=15,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            )
        elif self.model_type == 'gradient_boosting':
            self.model = GradientBoostingRegressor(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                random_state=42
            )
        else:
            raise ValueError(f"不支持的模型类型: {self.model_type}")

        # 训练模型
        print("正在训练...")
        self.model.fit(X_train, y_train)
        print("模型训练完成!")

        # 评估模型
        results = self.evaluate_model(X_train, X_test, y_train, y_test)

        return results

    def evaluate_model(self, X_train, X_test, y_train, y_test):
        """
        评估模型性能

        返回:
            dict: 评估指标
        """
        print("\n模型评估:")

        # 预测
        y_train_pred = self.model.predict(X_train)
        y_test_pred = self.model.predict(X_test)

        # 计算指标
        metrics = {
            'train': {
                'mae': mean_absolute_error(y_train, y_train_pred),
                'rmse': np.sqrt(mean_squared_error(y_train, y_train_pred)),
                'r2': r2_score(y_train, y_train_pred)
            },
            'test': {
                'mae': mean_absolute_error(y_test, y_test_pred),
                'rmse': np.sqrt(mean_squared_error(y_test, y_test_pred)),
                'r2': r2_score(y_test, y_test_pred)
            }
        }

        # 打印结果
        print(f"\n训练集性能:")
        print(f"  MAE: {metrics['train']['mae']:.2f} 元")
        print(f"  RMSE: {metrics['train']['rmse']:.2f} 元")
        print(f"  R2: {metrics['train']['r2']:.4f}")

        print(f"\n测试集性能:")
        print(f"  MAE: {metrics['test']['mae']:.2f} 元")
        print(f"  RMSE: {metrics['test']['rmse']:.2f} 元")
        print(f"  R2: {metrics['test']['r2']:.4f}")

        # 特征重要性
        if hasattr(self.model, 'feature_importances_'):
            feature_importance = pd.DataFrame({
                'feature': self.feature_columns,
                'importance': self.model.feature_importances_
            }).sort_values('importance', ascending=False)

            print(f"\n特征重要性 (Top 10):")
            for idx, row in feature_importance.head(10).iterrows():
                print(f"  {row['feature']}: {row['importance']:.4f}")

            metrics['feature_importance'] = feature_importance

        return metrics

    def predict(self, input_data):
        """
        预测航班价格

        参数:
            input_data: 输入数据 (字典或DataFrame)

        返回:
            float: 预测价格
        """
        if isinstance(input_data, dict):
            input_df = pd.DataFrame([input_data])
        else:
            input_df = input_data.copy()

        # 确保所有必需的特征都存在
        for col in self.feature_columns:
            if col not in input_df.columns:
                input_df[col] = 0  # 默认值

        # 选择特征列
        X = input_df[self.feature_columns]

        # 编码分类特征
        for col, encoder in self.label_encoders.items():
            if col in X.columns:
                # 处理未见过的类别
                if X[col].dtype == 'object':
                    unique_values = set(X[col].unique())
                    known_values = set(encoder.classes_)
                    unknown_values = unique_values - known_values

                    if unknown_values:
                        # 将未知值替换为最常见的类别
                        most_common = encoder.classes_[0]
                        X[col] = X[col].apply(lambda x: most_common if x not in known_values else x)

                X[col] = encoder.transform(X[col].astype(str))

        # 预测
        prediction = self.model.predict(X)

        return prediction[0]

    def predict_batch(self, input_data):
        """
        批量预测

        参数:
            input_data: 输入数据 (DataFrame)

        返回:
            array: 预测价格数组
        """
        predictions = []
        for idx, row in input_data.iterrows():
            pred = self.predict(row.to_dict())
            predictions.append(pred)
        return np.array(predictions)

    def save_model(self, filepath):
        """保存模型到文件"""
        model_data = {
            'model': self.model,
            'feature_columns': self.feature_columns,
            'label_encoders': self.label_encoders,
            'model_type': self.model_type
        }
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        print(f"模型已保存: {filepath}")

    def load_model(self, filepath):
        """从文件加载模型"""
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)

        self.model = model_data['model']
        self.feature_columns = model_data['feature_columns']
        self.label_encoders = model_data['label_encoders']
        self.model_type = model_data['model_type']
        print(f"模型已加载: {filepath}")

    def plot_predictions(self, y_true, y_pred, save_path=None):
        """
        绘制预测结果

        参数:
            y_true: 真实值
            y_pred: 预测值
            save_path: 保存路径
        """
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))

        # 散点图：预测值 vs 真实值
        axes[0].scatter(y_true, y_pred, alpha=0.5, s=10)
        axes[0].plot([y_true.min(), y_true.max()], [y_true.min(), y_true.max()],
                    'r--', lw=2, label='完美预测线')
        axes[0].set_xlabel('真实价格 (元)')
        axes[0].set_ylabel('预测价格 (元)')
        axes[0].set_title('预测值 vs 真实值')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)

        # 残差图
        residuals = y_pred - y_true
        axes[1].scatter(y_true, residuals, alpha=0.5, s=10)
        axes[1].axhline(y=0, color='r', linestyle='--', lw=2)
        axes[1].set_xlabel('真实价格 (元)')
        axes[1].set_ylabel('残差 (预测值 - 真实值)')
        axes[1].set_title('残差分布')
        axes[1].grid(True, alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"图表已保存: {save_path}")

        plt.show()


def main():
    """主函数：完整的训练和预测流程"""

    print("="*80)
    print("航班价格预测系统")
    print("="*80)

    # 1. 创建预测器实例
    predictor = FlightPricePredictor(model_type='random_forest')

    # 2. 加载数据
    data_file = 'flight_data_featured.csv'
    if not os.path.exists(data_file):
        print(f"\n错误: 数据文件不存在 - {data_file}")
        print("请先运行特征工程脚本生成特征数据")
        return

    df = predictor.load_data(data_file)

    # 3. 准备特征
    X, y = predictor.prepare_features(df, target_column='价格')

    # 4. 训练模型
    results = predictor.train(X, y, test_size=0.2)

    # 5. 保存模型
    model_file = 'flight_price_model.pkl'
    predictor.save_model(model_file)

    # 6. 示例预测
    print("\n" + "="*80)
    print("示例预测")
    print("="*80)

    # 创建几个测试场景
    test_scenarios = [
        {
            'name': '场景1: 提前30天购买，航班充足',
            'data': {
                '提前天数': 30,
                '剩余座位': 9,
                '飞行时长_分钟': 600,
                '中转时长_分钟': 120,
                '中转次数': 1,
                '航司': 'CZ',
                '起飞时段': '上午',
                '价格区间': '低价(<400)',
                '座位状态': '充足(>9)',
                '性价比': 50,
                '时间压力': 0.03,
                '效率评分': 0.8
            }
        },
        {
            'name': '场景2: 提前3天购买，座位紧张',
            'data': {
                '提前天数': 3,
                '剩余座位': 1,
                '飞行时长_分钟': 750,
                '中转时长_分钟': 200,
                '中转次数': 2,
                '航司': 'MU',
                '起飞时段': '晚上',
                '价格区间': '高价(>800)',
                '座位状态': '紧张(<=2)',
                '性价比': 200,
                '时间压力': 0.25,
                '效率评分': 0.3
            }
        },
        {
            'name': '场景3: 提前15天购买，中等情况',
            'data': {
                '提前天数': 15,
                '剩余座位': 5,
                '飞行时长_分钟': 700,
                '中转时长_分钟': 180,
                '中转次数': 1,
                '航司': 'HU',
                '起飞时段': '下午',
                '价格区间': '中价(500-600)',
                '座位状态': '较少(3-5)',
                '性价比': 100,
                '时间压力': 0.06,
                '效率评分': 0.6
            }
        }
    ]

    for scenario in test_scenarios:
        print(f"\n{scenario['name']}")
        print("-" * 50)
        pred_price = predictor.predict(scenario['data'])
        print(f"预测价格: {pred_price:.2f} 元")

    # 7. 可视化预测结果
    print("\n生成可视化图表...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    y_test_pred = predictor.model.predict(X_test)
    predictor.plot_predictions(y_test, y_test_pred, save_path='prediction_results.png')

    print("\n" + "="*80)
    print("预测任务完成!")
    print("="*80)
    print(f"\n生成文件:")
    print(f"  1. {model_file} - 训练好的模型")
    print(f"  2. prediction_results.png - 预测结果可视化")
    print()


if __name__ == "__main__":
    main()
