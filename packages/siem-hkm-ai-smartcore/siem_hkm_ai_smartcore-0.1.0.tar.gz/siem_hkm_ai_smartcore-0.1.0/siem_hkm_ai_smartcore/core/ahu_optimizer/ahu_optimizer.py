import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from docutils.nodes import classifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.multioutput import MultiOutputRegressor
from sklearn.metrics import mean_squared_error, r2_score
from pythermalcomfort.models import pmv_ppd_ashrae
from tqdm import tqdm
import warnings
import asyncio
import BAC0
import random
import csv
import time
import os
from BAC0.scripts.script_runner import run
from datetime import datetime
from sklearn.svm import SVR
import xgboost as xgb
from sklearn.model_selection import GridSearchCV
import re
from typing import Dict, Any, List, Tuple

# 忽略警告
warnings.filterwarnings('ignore')
sns.set(style="whitegrid")
plt.rcParams.update({'font.size': 12})



class Ahu_Optimizor:
    def __init__(self, data_path, show_occupancy=True):
        """
        热舒适度预测器
        
        参数:
        data_path -- 数据文件路径
        show_occupancy -- 是否在可视化中显示人员计数(默认True)
        """
        self.data_path = data_path
        self.show_occupancy = show_occupancy
        self.df = None
        self.X_train, self.X_test, self.y_train, self.y_test = None, None, None, None
        self.scaler = StandardScaler()
        self.model = None
        self.predictions = None
        self.pmv_results = None
        self.tci_results = None
        self.curr_pmv = None
        
        # 全局变量管理文件序列
        self.non_exist_list = []
        self.current_file_index = 1
        self.current_row_count = 0
        self.csv_filename = "bacnet_data_log_1.csv"

    
    def preprocess_point_name(self, target: list[list[str]] = None, feature: list[list[str]] = None,path: str = None) -> Tuple[list[str], list[str]]:
        """
        Preprocess point names by selecting relevant columns based on target and feature keywords.
        """
        if target is None:
            target = []
        t_cols = [col for col in self.df.columns if any(t in col for t in target)]
        if feature is None:
            feature = []
        f_cols = [col for col in self.df.columns if any(f in col for f in feature)]
        return t_cols, f_cols

    
    def load_and_preprocess_data(self, target: List[str] = None,  feature: List[str] = None,  path: str = None , proportion:int = 0.8)-> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Load CSV data and perform preprocessing, generating training and test sets based on target and feature columns
        only complete match accept
        
        Args:
            target: List of target variable keywords  e.g., ["temperature", "humidity"].Defaults to empty list if not provided.
            feature: List of feature variable keywords  e.g., ["energy", "light"] Defaults to empty list if not provided.
            path: Path to the CSV file. If None, uses the instance's data_path attribute.
            proportion: the proportion of data used to train(0<proportion<1)
            
        Returns:
            Tuple (X_train, X_test, y_train, y_test) containing:
            - Training feature set
            - Test feature set
            - Training target set
            - Test target set
            
        Raises:
            FileNotFoundError: When the CSV file path does not exist
            ValueError: When target or feature columns are empty after filtering
        """
        # Set default path
        if path is None:
            path = self.data_path  # Assuming self.data_path is defined in the class
        
        # Initialize default values for parameters
        if target is None:
            target = []
        if feature is None:
            feature = []
        
        print("Loading data...")
        try:
            self.df = pd.read_csv(path)
        except FileNotFoundError:
            raise FileNotFoundError(f"CSV file not found: {path}")
        
        # Process datetime column
        if 'DateTime' in self.df.columns:
            self.df['DateTime'] = pd.to_datetime(self.df['DateTime'], errors='coerce')
            if self.df['DateTime'].isna().any():
                print("Warning: Some DateTime values are invalid and have been converted to NaT")
            self.df.sort_values('DateTime', inplace=True)
            # Extract timestamp (hour*100 + minute)
            self.df['timestamp'] = self.df['DateTime'].dt.hour * 100 + self.df['DateTime'].dt.minute
        else:
            print("Warning: 'DateTime' column not found in data, skipping time processing")
        
        print("Filtering target and feature columns...")
        
        # 1. Filter target columns (columns containing any target keyword)
        target_cols = [col for col in self.df.columns if col in target]
        if not target_cols and target:  # If target specified but no matching columns found
            raise ValueError(f"No columns matching target keywords {target}")
        self.target_cols = list(set(target_cols))  # Remove duplicates
        
        # 2. Filter feature columns (columns containing any feature keyword)
        if feature:
            feature_cols = [col for col in self.df.columns if col in feature]
            if not feature_cols: 
                raise ValueError(f"No columns matching feature keywords {feature}")
        else:
            # If no features specified, use all non-target columns as features
            feature_cols = [col for col in self.df.columns if col not in self.target_cols]
        self.feature_cols = list(set(feature_cols))  # Remove duplicates
        
        # Calculate average occupancy (assuming "vs121_cols" is a defined list of column names)
        if hasattr(self, 'vs121_cols') and all(col in self.df.columns for col in self.vs121_cols):
            self.df['occupancy_mean'] = self.df[self.vs121_cols].mean(axis=1)
            # Add new feature to feature columns
            self.feature_cols.append('occupancy_mean')
            self.feature_cols = list(set(self.feature_cols))  # Remove duplicates
        else:
            print("Warning: Valid 'vs121_cols' columns not found, skipping average occupancy calculation")
        
        # Prepare feature and target data
        X = self.df[self.feature_cols].copy()
        y = self.df[self.target_cols].copy()

        X_scaled = X  # Temporarily disable standardization, enable as needed

        if proportion <= 0 or proportion >= 1:
            raise ValueError("Proportion must be between 0 and 1")
        print(f"Splitting dataset ({100*proportion}% training, {100 - 100*proportion}% testing)...")
        split_idx = int(proportion * len(X_scaled))
        self.X_train, self.X_test = X_scaled.iloc[:split_idx], X_scaled.iloc[split_idx:]
        self.y_train, self.y_test = y.iloc[:split_idx], y.iloc[split_idx:]
        
        # Save dates for later analysis if available
        if 'DateTime' in self.df.columns:
            self.dates_train, self.dates_test = self.df['DateTime'].iloc[:split_idx], self.df['DateTime'].iloc[split_idx:]
        
        print(f"Training set size: {len(self.X_train)} rows, Test set size: {len(self.X_test)} rows")
        
        return self.X_train, self.X_test, self.y_train, self.y_test
    
    def train_model(self,selected_model =MultiOutputRegressor ,base_model = xgb.XGBRegressor(max_depth=3, min_child_weight=5, learning_rate=0.1,n_estimators=100,randam_state=42)):
        """
        train model
        
        Args:
            selected_model: The model selection strategy (default: MultiOutputRegressor)
            base_model: The base model to be used (default: XGBRegressor)
        """
        
        
        
        
        
        print("训练多输出回归模型...")
        # 包装为多输出模型
        self.model =selected_model(base_model)
        # 训练模型
        self.model.fit(self.X_train, self.y_train)
        # 评估训练集性能
        train_preds = self.model.predict(self.X_train)
        train_r2 = r2_score(self.y_train, train_preds, multioutput='variance_weighted')
        print(f"训练集 R² 分数: {train_r2:.4f}")
    
    def predict_and_evaluate(self):
        """
        predict and evaluate
        """
        print("在测试集上进行预测...")
        self.predictions = self.model.predict(self.X_test)
        
        # 评估测试集性能
        mse = mean_squared_error(self.y_test, self.predictions, multioutput='raw_values')
        r2 = r2_score(self.y_test, self.predictions, multioutput='variance_weighted')
        
        # 打印每个房间的误差
        print("\n房间温度预测性能 (每个房间):")
        for i, col in enumerate(self.y_test.columns):
            print(f"{col}: MSE = {mse[i]:.4f}")
        
        print(f"\n总体加权R²分数: {r2:.4f}")
        
        # 保存预测结果
        self.df_pred = pd.DataFrame(self.predictions, columns=self.y_test.columns, index=self.y_test.index)
        self.df_pred['DateTime'] = self.dates_test.values
        self.df_pred = self.df_pred.set_index('DateTime')
        
        # 添加实际值用于比较
        self.df_actual = self.y_test.copy()
        self.df_actual['DateTime'] = self.dates_test.values
        self.df_actual = self.df_actual.set_index('DateTime')

    def write_to_csv(self, data_row):
        """将一行数据写入当前CSV文件。遇到ERROR则用上一行对应列数据替换，仅替换ERROR项"""
        global current_row_count

        # 如果文件不存在，创建文件并写入表头
        is_new_file = not os.path.exists(self.csv_filename)

        # 检查是否有上一行数据缓存，没有则初始化
        if not hasattr(self, 'last_row'):
            self.last_row = None

        # 替换ERROR为上一行对应列数据
        row_to_write = []
        for i, val in enumerate(data_row):
            if val == "ERROR" and self.last_row is not None:
                row_to_write.append(self.last_row[i])
            else:
                row_to_write.append(val)

        with open(self.csv_filename, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            # 新文件写入表头
            if is_new_file:
                writer.writerow(["timestamp"] + self.device_names)
            # 写入数据行
            writer.writerow(row_to_write)

        self.current_row_count += 1
        print(f"已写入第 {self.current_row_count} 行数据到 {self.csv_filename}")

        # 只有当前行没有ERROR时才更新last_row，否则用替换后的row_to_write更新
        self.last_row = row_to_write
    
    def run_func_pipeline(self):
        """
        运行完整的预测分析流程
        """
        self.load_and_preprocess_data()
        self.train_model()
        asyncio.run(self.receiver())
        #self.predict_curr_data()

        self.adjust_temp()
        asyncio.run(self.changer())
        #time.sleep(30)
        
if __name__ == "__main__":
    predictor = Ahu_Optimizor(data_path="merged_VAV_sensor_output.csv",show_occupancy=True)
    while True:
        predictor.run_func_pipeline()
        print("Wait for 15 minutes...")