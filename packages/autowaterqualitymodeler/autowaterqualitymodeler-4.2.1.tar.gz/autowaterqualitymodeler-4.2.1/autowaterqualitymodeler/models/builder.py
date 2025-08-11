"""
模型构建模块，提供模型拟合和评估功能
"""

import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error
import logging
from typing import Dict
import warnings

# 获取模块日志记录器
logger = logging.getLogger(__name__)

class ModelBuilder:
    """模型构建器，处理模型拟合和评估"""
    
    def __init__(self):
        """初始化模型构建器"""
        self.logger = logger
    
    def tune_linear(self, predicted: pd.Series, measured: pd.Series) -> float | None:
        """
        通过线性回归微调模型
        
        Args:
            predicted: 预测值
            measured: 实测值
            
        Returns:
            Dict: 调整后的模型参数
        """
        try:
            # 去除缺失值
            valid_data = pd.concat([predicted, measured], axis=1).dropna()
            
            if len(valid_data) < 2:
                self.logger.warning("有效数据点少于2个，无法进行线性调整")
                return None
            
            x = valid_data.iloc[:, 0].to_numpy().reshape(-1, 1)  # 预测值
            y = valid_data.iloc[:, 1].to_numpy()  # 实测值
            
            # 拟合线性模型（强制通过原点）
            model = LinearRegression(fit_intercept=False)
            model.fit(x, y)
            
            # 获取系数
            a = model.coef_[0]
            
            # 计算预测值
            y_pred = model.predict(x)
            
            # 计算评估指标
            r2 = r2_score(y, y_pred)
            rmse = np.sqrt(mean_squared_error(y, y_pred))
            
            # 记录拟合结果到日志
            logger.info(f"指标 {measured.name} 拟合完成: 系数 = {a:.4f}, "f"R² = {r2:.4f}, RMSE = {rmse:.4f}, 样本数 = {len(valid_data)}")
            return a
            
        except Exception as e:
            self.logger.error(f"线性调整失败: {e}", exc_info=True)
            return None
    