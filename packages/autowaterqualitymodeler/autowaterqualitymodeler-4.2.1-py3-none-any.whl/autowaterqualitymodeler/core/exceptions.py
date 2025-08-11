"""
异常定义模块，提供自定义异常类
"""

from typing import Any


class AutoWaterQualityError(Exception):
    """AutoWaterQualityModeler基础异常类"""
    
    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class DataValidationError(AutoWaterQualityError):
    """数据验证错误"""
    pass


class ConfigurationError(AutoWaterQualityError):
    """配置错误"""
    pass


class ModelingError(AutoWaterQualityError):
    """建模错误"""
    pass


class FeatureCalculationError(AutoWaterQualityError):
    """特征计算错误"""
    pass


class FileOperationError(AutoWaterQualityError):
    """文件操作错误"""
    pass


class EncryptionError(AutoWaterQualityError):
    """加密/解密错误"""
    pass


class InsufficientDataError(ModelingError):
    """数据不足错误"""
    
    def __init__(self, required: int, actual: int, metric: str | None = None):
        message = f"数据不足：需要至少{required}个样本，实际只有{actual}个"
        if metric:
            message = f"指标'{metric}'的{message}"
        super().__init__(message, {
            'required_samples': required,
            'actual_samples': actual,
            'metric': metric
        })


class InvalidParameterError(AutoWaterQualityError):
    """无效参数错误"""
    
    def __init__(self, param_name: str, param_value: Any, expected: str):
        message = f"参数'{param_name}'的值'{param_value}'无效，期望：{expected}"
        super().__init__(message, {
            'parameter': param_name,
            'value': param_value,
            'expected': expected
        })


class ProcessingError(AutoWaterQualityError):
    """数据处理错误"""
    pass