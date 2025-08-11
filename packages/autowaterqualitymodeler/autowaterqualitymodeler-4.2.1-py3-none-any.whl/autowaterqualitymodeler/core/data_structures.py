"""数据结构定义模块，提供统一的数据类型。

该模块定义了 AutoWaterQualityModeler 中使用的所有核心数据结构，
包括模型结果、配置参数、验证结果等。所有数据类都使用 @dataclass 装饰器，
提供了自动的初始化方法、repr 方法等功能。
"""

from dataclasses import dataclass, field
from typing import Any
import pandas as pd


@dataclass
class ModelResult:
    """单个模型的结果。
    
    存储单个模型的类型、参数、评估指标和公式字符串。
    
    Attributes:
        model_type: 模型类型，'power' 表示幂函数模型，'linear' 表示线性模型
        parameters: 模型参数字典，如 {'a': 1.5, 'b': 0.8}
        metrics: 评估指标字典，包含 'r2'、'rmse'、'corr' 等
        formula: 模型公式的字符串表示，如 'y = 1.5 * x^0.8'
    """
    model_type: str
    parameters: dict[str, float]
    metrics: dict[str, float]
    formula: str
    
    def __post_init__(self) -> None:
        """验证模型类型和参数。"""
        if self.model_type not in ['power', 'linear']:
            raise ValueError(f"Invalid model_type: {self.model_type}. Must be 'power' or 'linear'")
    
    def to_dict(self) -> dict[str, Any]:
        """转换为字典格式。
        
        Returns:
            包含模型信息的字典
        """
        return {
            'type': self.model_type,
            'params': self.parameters,
            'metrics': self.metrics,
            'formula': self.formula
        }


@dataclass
class FeatureModel:
    """特征模型结果。
    
    存储单个特征的幂函数模型参数和权重。
    
    Attributes:
        feature_name: 特征名称
        weight: 特征权重（0-1之间），表示该特征在组合模型中的贡献度
        a: 幂函数模型参数 a (y = a * x^b)
        b: 幂函数模型参数 b (y = a * x^b)
    """
    feature_name: str
    weight: float
    a: float
    b: float
    
    def __post_init__(self) -> None:
        """验证权重范围。"""
        if not 0 <= self.weight <= 1:
            raise ValueError(f"Weight must be between 0 and 1, got {self.weight}")
    
    def to_dict(self) -> dict[str, float]:
        """转换为字典格式。
        
        Returns:
            包含权重和参数的字典
        """
        return {
            'w': self.weight,
            'a': self.a,
            'b': self.b
        }


@dataclass
class MetricModelResult:
    """单个水质指标的建模结果。
    
    存储特定水质指标的建模结果，包括所选特征和模型性能。
    
    Attributes:
        metric_name: 水质指标名称（如 'chla', 'turbidity'）
        features: 选择的特征模型列表
        correlation: 模型预测值与实测值的相关系数
        rmse: 均方根误差
        n_features: 使用的特征数量
    """
    metric_name: str
    features: list[FeatureModel]
    correlation: float
    rmse: float
    n_features: int
    
    def __post_init__(self) -> None:
        """验证特征数量一致性。"""
        if self.n_features != len(self.features):
            raise ValueError(f"n_features ({self.n_features}) doesn't match actual features count ({len(self.features)})")
    
    def to_dict(self) -> dict[str, dict[str, float]]:
        """转换为字典格式。
        
        Returns:
            特征名到特征参数的映射字典
        """
        return {
            feature.feature_name: feature.to_dict() 
            for feature in self.features
        }


@dataclass
class ModelingResult:
    """建模结果的统一数据结构。
    
    存储完整的建模结果，包括模型字典和预测值。
    
    Attributes:
        model_type: 模型类型，0 表示微调，1 表示自动建模
        models: 指标名到模型的映射字典
        predictions: 匹配样本的预测结果 DataFrame
        all_predictions: 所有样本的预测结果 DataFrame（可选）
        metadata: 额外的元数据信息
    """
    model_type: int
    models: dict[str, Any]
    predictions: pd.DataFrame
    all_predictions: pd.DataFrame | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        """初始化后处理，确保 DataFrame 不为 None。"""
        if self.predictions is None:
            self.predictions = pd.DataFrame()
        if self.all_predictions is None:
            self.all_predictions = pd.DataFrame()
        
        # 验证模型类型
        if self.model_type not in [0, 1]:
            raise ValueError(f"Invalid model_type: {self.model_type}. Must be 0 (tuning) or 1 (auto)")
            
    def has_all_predictions(self) -> bool:
        """检查是否有所有样本的预测结果。
        
        Returns:
            如果有所有样本的预测结果返回 True
        """
        return self.all_predictions is not None and not self.all_predictions.empty


@dataclass
class ProcessingConfig:
    """数据处理配置。
    
    定义光谱数据处理的各项参数。
    
    Attributes:
        min_wavelength: 最小波长（nm）
        max_wavelength: 最大波长（nm）
        smooth_window: Savitzky-Golay 平滑窗口大小（必须为奇数）
        smooth_order: Savitzky-Golay 平滑多项式阶数
        min_samples: 建模所需的最小样本数
        max_features: 特征选择时的最大特征数
        data_type: 数据类型标识
    """
    min_wavelength: int = 400
    max_wavelength: int = 900
    smooth_window: int = 11
    smooth_order: int = 3
    min_samples: int = 6
    max_features: int = 5
    data_type: str = "aerospot"
    
    def __post_init__(self) -> None:
        """自动调用验证方法。"""
        self.validate()
    
    def validate(self) -> None:
        """验证配置参数的合理性。
        
        Raises:
            ValueError: 当参数不合理时
        """
        if self.min_wavelength >= self.max_wavelength:
            raise ValueError("min_wavelength must be less than max_wavelength")
        if self.smooth_window < 3:
            raise ValueError("smooth_window must be at least 3")
        if self.smooth_window % 2 == 0:
            raise ValueError("smooth_window must be odd")
        if self.smooth_order >= self.smooth_window:
            raise ValueError("smooth_order must be less than smooth_window")
        if self.min_samples < 3:
            raise ValueError("min_samples must be at least 3")
        if self.max_features < 1:
            raise ValueError("max_features must be at least 1")


@dataclass
class ValidationResult:
    """数据验证结果。
    
    用于存储数据验证的结果，包括错误和警告信息。
    
    Attributes:
        is_valid: 验证是否通过
        errors: 错误信息列表
        warnings: 警告信息列表
    """
    is_valid: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    
    def add_error(self, message: str) -> None:
        """添加错误信息并标记验证失败。
        
        Args:
            message: 错误信息
        """
        self.errors.append(message)
        self.is_valid = False
        
    def add_warning(self, message: str) -> None:
        """添加警告信息（不影响验证结果）。
        
        Args:
            message: 警告信息
        """
        self.warnings.append(message)
    
    def get_summary(self) -> str:
        """获取验证结果摘要。
        
        Returns:
            包含所有错误和警告的格式化字符串
        """
        summary = []
        if self.errors:
            summary.append(f"Errors ({len(self.errors)}):")
            summary.extend(f"  - {error}" for error in self.errors)
        if self.warnings:
            summary.append(f"Warnings ({len(self.warnings)}):")
            summary.extend(f"  - {warning}" for warning in self.warnings)
        return "\n".join(summary) if summary else "Validation passed"