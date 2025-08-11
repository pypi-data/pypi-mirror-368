"""
模型构建策略模块，实现不同的建模策略
"""

import pandas as pd
import numpy as np
import logging
from abc import ABC, abstractmethod

from .data_structures import (
    ModelingResult, ProcessingConfig, ValidationResult
)
from .feature_manager import FeatureManager
from ..models.builder import ModelBuilder
from ..utils.parallel import ParallelProcessor

logger = logging.getLogger(__name__)


class ModelingStrategy(ABC):
    """建模策略的抽象基类"""
    
    @abstractmethod
    def build(self, 
              spectrum_data: pd.DataFrame, 
              metric_data: pd.DataFrame,
              config: ProcessingConfig,
              **kwargs) -> ModelingResult:
        """执行建模"""
        pass
        
    @abstractmethod
    def validate_inputs(self, 
                       spectrum_data: pd.DataFrame, 
                       metric_data: pd.DataFrame) -> ValidationResult:
        """验证输入数据"""
        pass


class AutoModelingStrategy(ModelingStrategy):
    """自动建模策略"""
    
    def __init__(self, feature_manager: FeatureManager, model_builder: ModelBuilder):
        self.feature_manager = feature_manager
        self.model_builder = model_builder
        
    def validate_inputs(self, 
                       spectrum_data: pd.DataFrame, 
                       metric_data: pd.DataFrame) -> ValidationResult:
        """验证输入数据"""
        result = ValidationResult(is_valid=True)
        
        # 检查数据是否为空
        if spectrum_data.empty:
            result.add_error("光谱数据为空")
        if metric_data.empty:
            result.add_error("实测数据为空")
            
        # 检查样本数量是否一致
        if len(spectrum_data) != len(metric_data):
            result.add_error(f"光谱数据({len(spectrum_data)}条)与实测数据({len(metric_data)}条)样本数不一致")
            
        # 检查是否有有效的数值列
        if len(spectrum_data.select_dtypes(include=[np.number]).columns) == 0:
            result.add_error("光谱数据中没有数值列")
            
        return result
        
    def build(self, 
              spectrum_data: pd.DataFrame, 
              metric_data: pd.DataFrame,
              config: ProcessingConfig,
              matched_idx: list[int] | None = None,
              use_parallel: bool = False,
              **kwargs) -> ModelingResult:
        """执行自动建模"""
        models_dict = {}
        pred_dict = pd.DataFrame(index=metric_data.index)
        all_pred_dict = pd.DataFrame(index=spectrum_data.index) if matched_idx is not None else None
        
        # 获取指标列表
        metrics = metric_data.columns.tolist()
        
        if use_parallel and len(metrics) > 1:
            # 使用并行处理
            logger.info(f"使用并行处理构建 {len(metrics)} 个指标的模型")
            
            # 创建并行处理器
            processor = ParallelProcessor(use_process=False)
            
            # 定义单个指标的处理函数
            def process_single_metric(metric_name: str) -> dict | None:
                try:
                    return self._build_metric_model(
                        spectrum_data, 
                        metric_data[metric_name].dropna() if isinstance(metric_data[metric_name], pd.Series) else metric_data[metric_name],
                        config,
                        metric_name,
                        matched_idx
                    )
                except Exception as e:
                    logger.error(f"构建{metric_name}模型失败: {e}", exc_info=True)
                    return None
            
            # 并行处理
            results = processor.process_metrics(
                process_single_metric,
                metrics,
                # 注意：参数已经在process_single_metric中绑定
            )
            
            # 整理结果
            for metric_name, result in results.items():
                if result:
                    models_dict[metric_name] = result['model']
                    pred_dict[metric_name] = result['predictions']
                    
                    if matched_idx is not None and 'all_predictions' in result and all_pred_dict is not None:
                        all_pred_dict[metric_name] = result['all_predictions']
        else:
            # 串行处理
            logger.info(f"使用串行处理构建 {len(metrics)} 个指标的模型")
            
            for metric_name in metrics:
                # 如果该指标所有值都相同，则跳过
                if metric_data[metric_name].nunique() == 1:
                    logger.error(f"{metric_name}所有值相同，无法建模，跳过！！！！\n")
                    continue
                try:
                    result = self._build_metric_model(
                        spectrum_data, 
                        metric_data[metric_name].dropna() if isinstance(metric_data[metric_name], pd.Series) else metric_data[metric_name],
                        config,
                        metric_name,
                        matched_idx
                    )
                    
                    if result:
                        models_dict[metric_name] = result['model']
                        pred_dict[metric_name] = result['predictions']
                        
                        if matched_idx is not None and 'all_predictions' in result and all_pred_dict is not None:
                            all_pred_dict[metric_name] = result['all_predictions']
                            
                except Exception as e:
                    logger.error(f"构建{metric_name}模型失败: {e}", exc_info=True)
                    continue
                
        return ModelingResult(
            model_type=1,
            models=models_dict,
            predictions=pred_dict,
            all_predictions=all_pred_dict
        )
        
    def _build_metric_model(self, 
                           spectrum_data: pd.DataFrame,
                           metric_series: pd.Series,
                           config: ProcessingConfig,
                           metric_name: str,
                           matched_idx: list[int] | None = None) -> dict | None:
        """为单个指标构建模型"""
        # 计算特征
        features = self.feature_manager.calculate_features(
            spectrum_data, 
            config.data_type, 
            metric_name
        )
        
        if features.empty:
            logger.warning(f"指标 {metric_name} 的特征计算结果为空")
            return None
            
        # 处理匹配索引
        if matched_idx is not None:
            matched_features = features.iloc[matched_idx].copy()
            matched_features.index = metric_series.index
            working_features = matched_features
        else:
            working_features = features
            
        # 选择特征
        selected_models = self.feature_manager.select_top_features(
            working_features, 
            metric_series, 
            config.max_features
        )
        
        if not selected_models:
            logger.warning(f"指标 {metric_name} 无法选择有效特征")
            return None
            
        # 构建组合模型
        best_combination = self._find_best_combination(
            selected_models,
            working_features,
            metric_series,
            features if matched_idx is not None else None
        )
        
        return best_combination
        
    def _find_best_combination(self,
                              selected_models: list,
                              working_features: pd.DataFrame,
                              metric_series: pd.Series,
                              all_features: pd.DataFrame | None = None) -> dict | None:
        """找到最佳的特征组合"""
        best_combination = None
        best_corr = 0
        
        # 尝试不同数量的特征组合
        for n in range(1, len(selected_models) + 1):
            combination = self._evaluate_combination(
                selected_models[:n],
                working_features,
                metric_series,
                all_features
            )
            
            if combination and combination['corr'] > best_corr:
                best_corr = combination['corr']
                best_combination = combination
                
        return best_combination
        
    def _evaluate_combination(self,
                             selected_features: list,
                             working_features: pd.DataFrame,
                             metric_series: pd.Series,
                             all_features: pd.DataFrame | None = None) -> dict | None:
        """评估特征组合的效果"""
        # 计算权重
        total_weight = sum(abs(f[1]['corr']) for f in selected_features)
        weights = {f[0]: abs(f[1]['corr']) / total_weight for f in selected_features}
        
        # 计算预测值
        predictions = self._calculate_predictions(
            selected_features,
            working_features,
            weights
        )
        
        if predictions is None or predictions.empty:
            return None
            
        # 计算评估指标
        y_true = metric_series.loc[predictions.index]
        corr = np.corrcoef(predictions, y_true)[0, 1]
        rmse = np.sqrt(np.mean((predictions - y_true) ** 2))
        
        result = {
            'model': {
                feature_name: {
                    'w': weights[feature_name],
                    'a': params['a'],
                    'b': params['b']
                }
                for feature_name, params in selected_features
            },
            'predictions': predictions,
            'corr': corr,
            'rmse': rmse,
            'n_features': len(selected_features)
        }
        
        # 如果需要计算所有样本的预测
        if all_features is not None:
            all_predictions = self._calculate_predictions(
                selected_features,
                all_features,
                weights
            )
            result['all_predictions'] = all_predictions
            
        return result
        
    def _calculate_predictions(self,
                              selected_features: list,
                              features: pd.DataFrame,
                              weights: dict[str, float]) -> pd.Series | None:
        """计算加权预测值"""
        inverted_values = {}
        
        for feature_name, params in selected_features:
            x_data = features[feature_name].dropna()
            x_data = x_data[x_data > 0]
            
            # Handle both Series and ndarray
            x_values = x_data.values if hasattr(x_data, 'values') else x_data
            inverted = params['a'] * np.power(x_values, params['b'])
            inverted_values[feature_name] = pd.Series(inverted, index=x_data.index)
            
        if not inverted_values:
            return None
            
        # 找到共同索引
        common_indices = set.intersection(*[set(series.index) for series in inverted_values.values()])
        
        if not common_indices:
            return None
            
        common_indices_list = list(common_indices)
        weighted_result = pd.Series(0, index=common_indices_list)
        
        for feature_name in inverted_values:
            weighted_result += inverted_values[feature_name].loc[common_indices_list] * weights[feature_name]
            
        return weighted_result


class TuningStrategy(ModelingStrategy):
    """模型微调策略"""
    
    def __init__(self, model_builder: ModelBuilder):
        self.model_builder = model_builder
        
    def validate_inputs(self, 
                       spectrum_data: pd.DataFrame, 
                       metric_data: pd.DataFrame) -> ValidationResult:
        """验证输入数据"""
        result = ValidationResult(is_valid=True)
        
        # 这里spectrum_data实际上是merged_data（预测值）
        if spectrum_data.empty:
            result.add_error("预测数据为空")
        if metric_data.empty:
            result.add_error("实测数据为空")
            
        # 检查是否有共同的列
        common_cols = set(spectrum_data.columns) & set(metric_data.columns)
        if not common_cols:
            result.add_error("预测数据和实测数据没有共同的指标")
            
        return result
        
    def build(self, 
              merged_data: pd.DataFrame,  # 这里实际上是预测值数据
              metric_data: pd.DataFrame,
              config: ProcessingConfig,
              all_merged_data: pd.DataFrame | None = None,
              **kwargs) -> ModelingResult:
        """执行模型微调"""
        models_dict = {}
        pred_dict = pd.DataFrame(index=metric_data.index)
        all_pred_dict: pd.DataFrame | None = pd.DataFrame(index=all_merged_data.index) if all_merged_data is not None else None
        
        # 遍历每个指标
        for metric_name in metric_data.columns:
            if metric_name not in merged_data.columns:
                logger.warning(f"指标 {metric_name} 不在预测数据中，跳过")
                continue
                
            # 获取实测值和预测值
            measured = metric_data[metric_name].dropna()
            predicted = merged_data[metric_name].loc[measured.index]
            
            # 微调模型
            tuned_A = self.model_builder.tune_linear(predicted, measured)
            
            if tuned_A is None:
                logger.warning(f"指标 {metric_name} 模型微调失败")
                continue
                
            # 保存结果
            models_dict[metric_name] = tuned_A
            
            # 计算调整后的预测值
            adjusted_pred = tuned_A * predicted
            adjusted_pred.name = metric_name
            pred_dict[metric_name] = adjusted_pred
            
            # 计算所有样本的预测值
            if all_merged_data is not None and metric_name in all_merged_data.columns and all_pred_dict is not None:
                all_adjusted = tuned_A * all_merged_data[metric_name]
                all_adjusted.name = metric_name
                all_pred_dict[metric_name] = all_adjusted
                
        # 将负值替换为NaN
        pred_dict = pred_dict.where(pred_dict >= 0, np.nan)
        if all_pred_dict is not None and not all_pred_dict.empty:
            all_pred_dict = all_pred_dict.where(all_pred_dict >= 0, np.nan)
            
        return ModelingResult(
            model_type=0,
            models=models_dict,
            predictions=pred_dict,
            all_predictions=all_pred_dict
        )