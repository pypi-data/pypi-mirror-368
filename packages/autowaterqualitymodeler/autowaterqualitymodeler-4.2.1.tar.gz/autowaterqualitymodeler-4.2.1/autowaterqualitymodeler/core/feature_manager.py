"""特征管理模块，连接配置管理和特征计算。

该模块提供了特征定义、计算、重要性评估和选择的完整工作流。
主要功能包括：
- 基于配置文件的特征定义管理
- 光谱特征计算（波段反射率、波段组合、色度特征等）
- 基于幂函数模型的特征重要性评估
- 特征选择和排序
"""

from __future__ import annotations
import pandas as pd
import numpy as np
import os
import logging
from typing import Union, TYPE_CHECKING

if TYPE_CHECKING:
    from .config_manager import ConfigManager

# 导入项目组件
from ..features.calculator import FeatureCalculator
from ..utils.cache import get_global_cache_manager

# 避免循环导入
if not TYPE_CHECKING:
    from .config_manager import ConfigManager

# 获取模块日志记录器
logger = logging.getLogger(__name__)

class FeatureManager:
    """特征管理器，处理特征定义和计算。
    
    该类负责：
    1. 管理特征配置和定义
    2. 计算各种光谱特征
    3. 评估特征重要性
    4. 执行特征选择
    
    Attributes:
        config_manager: 配置管理器实例
        tris_coeff: 三刺激值系数表（用于色度特征计算）
        calculator: 特征计算器实例
        cache_manager: 缓存管理器实例
    """
    
    def __init__(self, config_manager: 'ConfigManager', tris_coeff_path: str | None = None) -> None:
        """初始化特征管理器。
        
        设置配置管理器，加载三刺激值系数表，并初始化特征计算器和缓存管理器。
        
        Args:
            config_manager: 配置管理器实例，用于加载特征定义
            tris_coeff_path: 三刺激值系数表路径，如果为None则使用默认路径
        """
        self.config_manager = config_manager
        
        # 加载三刺激值系数表
        self.tris_coeff = self._load_tris_coefficients(tris_coeff_path)
        
        # 创建特征计算器
        self.calculator = FeatureCalculator(tris_coeff=self.tris_coeff)
        
        # 获取缓存管理器
        self.cache_manager = get_global_cache_manager()
    
    def _load_tris_coefficients(self, tris_coeff_path: str | None = None) -> pd.DataFrame:
        """加载三刺激值系数表。
        
        加载CIE标准D65光源下的三刺激值系数表，用于计算色度特征。
        
        Args:
            tris_coeff_path: 三刺激值系数表路径，如果为None则使用默认路径
            
        Returns:
            pd.DataFrame: 三刺激值系数表，行索引为波长，列为X、Y、Z系数
            
        Note:
            如果加载失败，将返回空DataFrame并记录警告日志。
        """
        try:
            # 如果未提供路径，使用默认路径
            if tris_coeff_path is None:
                tris_coeff_path = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                    'resources', 
                    'D65xCIE.xlsx'
                )
            
            # 加载三刺激值系数表
            tris_coeff = pd.read_excel(tris_coeff_path, header=0, index_col=0)
            logger.info(f"成功加载三刺激值系数表: {tris_coeff_path}")
            return tris_coeff
            
        except Exception as e:
            logger.warning(f"加载三刺激值系数表失败: {e}", exc_info=True)
            # 返回空DataFrame
            return pd.DataFrame()
    
    def calculate_features(self, spectrum_data: pd.DataFrame, data_type: str, metric_name: str) -> pd.DataFrame:
        """计算指定数据类型和指标的特征。
        
        根据配置文件中的特征定义，计算光谱数据的各种特征。
        支持缓存以提高重复计算的效率。
        
        Args:
            spectrum_data: 光谱数据DataFrame，行为样本，列为波长
            data_type: 数据类型（如 'aerospot', 'shore_data' 等）
            metric_name: 水质指标名称（如 'chla', 'turbidity' 等）
            
        Returns:
            pd.DataFrame: 计算的特征数据，行为样本，列为特征名
            
        Example:
            >>> features = manager.calculate_features(spectrum_df, 'aerospot', 'chla')
        """
        cache_key = None
        # 如果缓存启用，先尝试从缓存获取
        if self.cache_manager and self.cache_manager.enabled:
            cache_key = self.cache_manager._generate_key(
                'calculate_features', spectrum_data, data_type, metric_name
            )
            cached_result = self.cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
        
        # 计算特征
        result = self._calculate_features_impl(spectrum_data, data_type, metric_name)
        
        # 保存到缓存
        if self.cache_manager and self.cache_manager.enabled and cache_key is not None:
            self.cache_manager.set(cache_key, result)
            
        return result
    
    def _calculate_features_impl(self, spectrum_data: pd.DataFrame, data_type: str, metric_name: str) -> pd.DataFrame:
        """特征计算的实际实现。
        
        内部方法，执行实际的特征计算逻辑。
        
        Args:
            spectrum_data: 光谱数据DataFrame
            data_type: 数据类型
            metric_name: 指标名称
            
        Returns:
            pd.DataFrame: 计算的特征数据
            
        Note:
            如果计算失败或找不到特征定义，将返回空DataFrame。
        """
        try:
            # 获取特征定义
            feature_definitions = self.config_manager.get_feature_definitions(data_type, metric_name)
            
            if not feature_definitions:
                logger.warning(f"未找到 {data_type} 下 {metric_name} 指标的特征定义")
                return pd.DataFrame(index=spectrum_data.index)
            
            # 计算特征
            features = self.calculator.calculate_features(spectrum_data, feature_definitions)
            
            if features.empty:
                logger.warning(f"{metric_name} 指标的特征计算结果为空")
                
            return features
            
        except Exception as e:
            logger.error(f"计算 {data_type} 下 {metric_name} 指标的特征时出错: {e}", exc_info=True)
            return pd.DataFrame(index=spectrum_data.index)
    
    def get_feature_importance(self, features: pd.DataFrame, target: pd.Series) -> dict[str, dict[str, float]]:
        """计算特征重要性（基于幂函数模型 y = a*x^b 的拟合效果）。
        
        对每个特征使用幂函数模型进行拟合，根据拟合效果评估特征重要性。
        
        Args:
            features: 特征数据DataFrame，行为样本，列为特征
            target: 目标变量Series，水质指标的实测值
            
        Returns:
            dict[str, dict[str, float]]: 特征重要性字典，结构为：
                {
                    '特征名': {
                        'a': 幂函数参数a,
                        'b': 幂函数参数b,
                        'corr': 相关系数,
                        'rmse': 均方根误差,
                        'r2': 决定系数
                    }
                }
                
        Note:
            只处理正值数据（幂函数模型的要求）。
            至少需要3个有效数据点才能进行拟合。
        """
        try:
            if features.empty:
                return {}
                
            importance = {}
            
            
            # 计算每个特征的重要性
            for feature_name in features.columns:
                # 去除缺失值和负值（幂函数模型的限制）
                valid_mask = (features[feature_name] > 0) & (target > 0) & (~features[feature_name].isna()) & (~target.isna())
                if valid_mask.sum() < 3:  # 至少需要3个点才能拟合模型
                    logger.warning(f"特征 {feature_name} 的有效数据点少于3个，无法拟合模型")
                    continue
                
                x = features.loc[valid_mask, feature_name].values
                y = target.loc[valid_mask].values

                # 记录原始数据范围
                logger.info(f"特征：{feature_name} 拟合数据范围 - x: {x.min()}-{x.max()}, y: {y.min()}-{y.max()}")
                
                try:
                    # 拟合幂函数模型
                    params = self.perform_power_fitting(x, y)
                    if params:
                        a, b, corr, rmse, r2 = params
                        importance[feature_name] = {
                        'a': float(a), 'b': float(b), 'corr': float(corr), 
                        'rmse': float(rmse), 'r2': float(r2)
                    }

                except Exception as e:
                    logger.error(f"拟合特征 {feature_name} 失败: {e}", exc_info=True)
            
            return importance
            
        except Exception as e:
            logger.error(f"计算特征重要性时出错: {e}", exc_info=True)
            return {}


    def perform_power_fitting(self, x_valid: np.ndarray, y_valid: np.ndarray, 
                            initial_guess: list[float] | None = None) -> tuple[float, float, float, float, float] | None:
        """执行幂函数拟合: y = a * x^b。
        
        使用非线性最小二乘法拟合幂函数模型，并计算拟合质量指标。
        
        Args:
            x_valid: 自变量数组（特征值）
            y_valid: 因变量数组（目标值）
            initial_guess: 参数初始猜测值 [a, b]，默认为 [1.0, 1.0]
            
        Returns:
            tuple[float, float, float, float, float] | None: 
                拟合成功返回 (a, b, corr, rmse, r2)，其中：
                - a, b: 幂函数参数
                - corr: 相关系数
                - rmse: 均方根误差
                - r2: 决定系数
                拟合失败返回 None
                
        Note:
            使用参数约束防止极端值：
            - a ∈ [-100000, 100000]
            - b ∈ [-50, 50]
        """
        from scipy.optimize import curve_fit
        from scipy.stats import pearsonr
        import warnings
        
        # 定义拟合函数并捕获警告
        def fit_function(x: np.ndarray, a: float, b: float) -> np.ndarray:
            # 捕获幂运算中的警告并记录参数值
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                result = a * np.power(x, b)
                
                # 如果有警告产生，则记录参数信息
                if len(w) > 0 and issubclass(w[-1].category, RuntimeWarning):
                    # 记录产生警告时的参数值
                    logger.warning(f"幂运算溢出警告! 参数值: a={a}, b={b}")
                    logger.warning(f"x值范围: {x.min() if hasattr(x, 'min') else np.min(x)} - {x.max() if hasattr(x, 'max') else np.max(x)}")
                    
                    # 寻找导致溢出的具体x值
                    problem_indices = np.isnan(result) | np.isinf(result)
                    if np.any(problem_indices):
                        problem_x = x[problem_indices]
                        logger.warning(f"导致问题的x值: {problem_x[:10]} ...")
            
            return result
        
        try:
            
            
            # 初始猜测值
            if initial_guess is None:
                initial_guess = [1.0, 1.0]
            
            # 设置参数约束，防止产生极端参数值
            # a参数通常不需要太大，b参数应该在合理范围内
            bounds = (
                [0.000001, -50],  # 下限：a可以为负，但b不应过度负值
                [100000, 50]     # 上限：限制a和b的绝对值
            )
            
            # 执行拟合，添加参数约束
            popt, pcov = curve_fit(
                fit_function, 
                x_valid, 
                y_valid, 
                p0=initial_guess, 
                maxfev=10000, 
                method='trf',   # 使用trust-region方法支持边界约束
                bounds=bounds
            )
            
            # 获取参数
            a, b = popt

            # 检查参数是否接近边界
            if abs(a) > bounds[1][0] * 0.9 or abs(b) > bounds[1][1] * 0.9:
                logger.warning(f"拟合参数接近边界值，可能需要扩大参数范围: a={a}, b={b}")
            
            # 计算参数估计的标准误差
            perr = np.sqrt(np.diag(pcov))
            logger.info(f"拟合参数: a={a}±{perr[0]}, b={b}±{perr[1]}")
            
            # 计算预测值
            y_pred = fit_function(x_valid, a, b)
            
            # 计算评价指标
            # 在调用pearsonr之前添加检查
            if len(set(y_valid)) > 1 and len(set(y_pred)) > 1:
                corr_coef, _ = pearsonr(y_valid, y_pred)
            else:
                # 当输入为常量时的处理
                logger.error("无法计算相关系数：输入数组是常量，导致相关系数为NaN，手动设置为0.1")
                corr_coef = 0.1  # 设置为一个不为0的数
            rmse = np.sqrt(np.mean((y_pred - y_valid) ** 2))
            ss_res = np.sum((y_valid - y_pred) ** 2)
            ss_tot = np.sum((y_valid - np.mean(y_valid)) ** 2)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
            
            # 记录拟合质量
            logger.info(f"拟合质量: 相关系数={corr_coef:.4f}, RMSE={rmse:.4f}, R²={r_squared:.4f}")
            
            return (float(a), float(b), float(corr_coef), float(rmse), float(r_squared))
        except Exception as e:
            logger.error(f"拟合失败: {e}", exc_info=True)
            return None
    
    def select_top_features(self, features: pd.DataFrame, target: pd.Series, 
                           top_n: Union[int, str] = 'all') -> list[tuple[str, dict[str, float]]]:
        """根据重要性选择前N个特征。
        
        计算所有特征的重要性，并按相关系数绝对值排序选择。
        
        Args:
            features: 特征数据DataFrame
            target: 目标变量Series
            top_n: 选择的特征数量，可以是整数或 'all'（选择所有）
            
        Returns:
            list[tuple[str, dict[str, float]]]: 选择的特征列表，
                每个元素为 (特征名, 重要性指标字典)
                
        Raises:
            ValueError: 当 top_n 参数无效时
            
        Example:
            >>> selected = manager.select_top_features(features, target, top_n=5)
            >>> for name, metrics in selected:
            ...     print(f"{name}: corr={metrics['corr']:.3f}")
        """
        try:
            # 计算特征重要性
            importance = self.get_feature_importance(features, target)
            
            if not importance:
                return []
                
            # 按重要性排序
            sorted_features = sorted(importance.items(), 
                                key=lambda x: abs(x[1]['corr']), 
                                reverse=True)
            
            if isinstance(top_n, int):
                # 选择前N个特征
                selected = sorted_features[:top_n]
            elif top_n == 'all':
                selected = sorted_features
            else:
                raise ValueError("top_n 必须是数字或 'all'")
            
            return selected
        except Exception as e:
            logger.error(f"选择特征时出错: {e}", exc_info=True)
            return []
    