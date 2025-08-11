"""
输入验证模块，提供数据验证功能
"""

import pandas as pd
import numpy as np
import logging
from typing import Callable, Any
from functools import wraps

from .exceptions import DataValidationError, InvalidParameterError

logger = logging.getLogger(__name__)


def validate_dataframe(df: pd.DataFrame, 
                      name: str,
                      min_rows: int | None = None,
                      min_cols: int | None = None,
                      required_columns: list[str] | None = None,
                      numeric_only: bool = False) -> None:
    """
    验证DataFrame
    
    Args:
        df: 要验证的DataFrame
        name: DataFrame的名称（用于错误消息）
        min_rows: 最小行数
        min_cols: 最小列数
        required_columns: 必需的列名列表
        numeric_only: 是否只允许数值列
        
    Raises:
        DataValidationError: 验证失败时
    """
    if not isinstance(df, pd.DataFrame):
        raise DataValidationError(f"{name}必须是pandas DataFrame类型")
        
    if df.empty:
        raise DataValidationError(f"{name}为空")
        
    if min_rows is not None and len(df) < min_rows:
        raise DataValidationError(
            f"{name}的行数不足：需要至少{min_rows}行，实际只有{len(df)}行"
        )
        
    if min_cols is not None and len(df.columns) < min_cols:
        raise DataValidationError(
            f"{name}的列数不足：需要至少{min_cols}列，实际只有{len(df.columns)}列"
        )
        
    if required_columns:
        missing_cols = set(required_columns) - set(df.columns)
        if missing_cols:
            raise DataValidationError(
                f"{name}缺少必需的列：{missing_cols}"
            )
            
    if numeric_only:
        non_numeric = df.select_dtypes(exclude=[np.number]).columns.tolist()
        if non_numeric:
            raise DataValidationError(
                f"{name}包含非数值列：{non_numeric}"
            )


def validate_series(series: pd.Series,
                   name: str,
                   min_length: int | None = None,
                   numeric_only: bool = True,
                   no_nan: bool = False) -> None:
    """
    验证Series
    
    Args:
        series: 要验证的Series
        name: Series的名称（用于错误消息）
        min_length: 最小长度
        numeric_only: 是否只允许数值
        no_nan: 是否不允许NaN值
        
    Raises:
        DataValidationError: 验证失败时
    """
    if not isinstance(series, pd.Series):
        raise DataValidationError(f"{name}必须是pandas Series类型")
        
    if series.empty:
        raise DataValidationError(f"{name}为空")
        
    if min_length is not None and len(series) < min_length:
        raise DataValidationError(
            f"{name}的长度不足：需要至少{min_length}，实际只有{len(series)}"
        )
        
    if numeric_only and not pd.api.types.is_numeric_dtype(series):
        raise DataValidationError(f"{name}必须是数值类型")
        
    if no_nan and series.isna().any():
        raise DataValidationError(f"{name}包含NaN值")


def validate_parameter(value: Any,
                      name: str,
                      expected_type: type | None = None,
                      min_value: float | None = None,
                      max_value: float | None = None,
                      allowed_values: list[Any] | None = None) -> None:
    """
    验证参数
    
    Args:
        value: 参数值
        name: 参数名称
        expected_type: 期望的类型
        min_value: 最小值
        max_value: 最大值
        allowed_values: 允许的值列表
        
    Raises:
        InvalidParameterError: 验证失败时
    """
    if expected_type is not None and not isinstance(value, expected_type):
        raise InvalidParameterError(
            name, value, f"类型应为{expected_type.__name__}"
        )
        
    if min_value is not None and value < min_value:
        raise InvalidParameterError(
            name, value, f"值应大于等于{min_value}"
        )
        
    if max_value is not None and value > max_value:
        raise InvalidParameterError(
            name, value, f"值应小于等于{max_value}"
        )
        
    if allowed_values is not None and value not in allowed_values:
        raise InvalidParameterError(
            name, value, f"值应为{allowed_values}之一"
        )


def validate_inputs(*validations):
    """
    输入验证装饰器
    
    Args:
        *validations: 验证函数列表，每个函数接收被装饰函数的参数
        
    Example:
        @validate_inputs(
            lambda self, data, **kwargs: validate_dataframe(data, "输入数据", min_rows=1)
        )
        def process_data(self, data):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 执行所有验证
            for validation in validations:
                try:
                    validation(*args, **kwargs)
                except Exception as e:
                    logger.error(f"函数{func.__name__}的输入验证失败: {e}")
                    raise
                    
            # 执行原函数
            return func(*args, **kwargs)
            
        return wrapper
    return decorator


def ensure_numeric_dataframe(func: Callable) -> Callable:
    """
    确保第一个DataFrame参数是数值类型的装饰器
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if len(args) > 1 and isinstance(args[1], pd.DataFrame):
            df = args[1]
            # 只保留数值列
            numeric_df = df.select_dtypes(include=[np.number])
            if len(numeric_df.columns) < len(df.columns):
                dropped = set(df.columns) - set(numeric_df.columns)
                logger.warning(f"移除了非数值列: {dropped}")
            args = list(args)
            args[1] = numeric_df
            
        return func(*args, **kwargs)
        
    return wrapper