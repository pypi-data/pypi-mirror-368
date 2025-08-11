"""
验证器测试
"""

import pytest
import pandas as pd
import numpy as np
from autowaterqualitymodeler.core.validators import (
    validate_dataframe, validate_series, validate_parameter,
    validate_inputs, ensure_numeric_dataframe
)
from autowaterqualitymodeler.core.exceptions import (
    DataValidationError, InvalidParameterError
)


class TestValidateDataFrame:
    """测试DataFrame验证函数"""
    
    def test_valid_dataframe(self):
        """测试有效的DataFrame"""
        df = pd.DataFrame({
            'col1': [1, 2, 3],
            'col2': [4, 5, 6]
        })
        
        # 不应抛出异常
        validate_dataframe(df, "测试数据")
        
    def test_empty_dataframe(self):
        """测试空DataFrame"""
        df = pd.DataFrame()
        
        with pytest.raises(DataValidationError, match="测试数据为空"):
            validate_dataframe(df, "测试数据")
            
    def test_min_rows(self):
        """测试最小行数验证"""
        df = pd.DataFrame({'col1': [1, 2]})
        
        with pytest.raises(DataValidationError, match="行数不足"):
            validate_dataframe(df, "测试数据", min_rows=3)
            
    def test_required_columns(self):
        """测试必需列验证"""
        df = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})
        
        with pytest.raises(DataValidationError, match="缺少必需的列"):
            validate_dataframe(df, "测试数据", required_columns=['col1', 'col3'])
            
    def test_numeric_only(self):
        """测试纯数值验证"""
        df = pd.DataFrame({
            'numeric': [1, 2, 3],
            'text': ['a', 'b', 'c']
        })
        
        with pytest.raises(DataValidationError, match="包含非数值列"):
            validate_dataframe(df, "测试数据", numeric_only=True)


class TestValidateSeries:
    """测试Series验证函数"""
    
    def test_valid_series(self):
        """测试有效的Series"""
        series = pd.Series([1, 2, 3])
        
        # 不应抛出异常
        validate_series(series, "测试序列")
        
    def test_empty_series(self):
        """测试空Series"""
        series = pd.Series([])
        
        with pytest.raises(DataValidationError, match="测试序列为空"):
            validate_series(series, "测试序列")
            
    def test_no_nan(self):
        """测试NaN值验证"""
        series = pd.Series([1, 2, np.nan])
        
        with pytest.raises(DataValidationError, match="包含NaN值"):
            validate_series(series, "测试序列", no_nan=True)


class TestValidateParameter:
    """测试参数验证函数"""
    
    def test_type_validation(self):
        """测试类型验证"""
        with pytest.raises(InvalidParameterError):
            validate_parameter("text", "参数", expected_type=int)
            
    def test_min_max_validation(self):
        """测试最小/最大值验证"""
        with pytest.raises(InvalidParameterError, match="值应大于等于"):
            validate_parameter(5, "参数", min_value=10)
            
        with pytest.raises(InvalidParameterError, match="值应小于等于"):
            validate_parameter(20, "参数", max_value=10)
            
    def test_allowed_values(self):
        """测试允许值验证"""
        with pytest.raises(InvalidParameterError, match="值应为"):
            validate_parameter("d", "参数", allowed_values=['a', 'b', 'c'])


class TestValidateInputsDecorator:
    """测试输入验证装饰器"""
    
    def test_decorator_with_valid_inputs(self):
        """测试装饰器处理有效输入"""
        @validate_inputs(
            lambda x: validate_parameter(x, "x", expected_type=int, min_value=0)
        )
        def add_one(x):
            return x + 1
            
        result = add_one(5)
        assert result == 6
        
    def test_decorator_with_invalid_inputs(self):
        """测试装饰器处理无效输入"""
        @validate_inputs(
            lambda x: validate_parameter(x, "x", expected_type=int, min_value=0)
        )
        def add_one(x):
            return x + 1
            
        with pytest.raises(InvalidParameterError):
            add_one(-1)


class TestEnsureNumericDataFrame:
    """测试数值DataFrame装饰器"""
    
    def test_numeric_conversion(self):
        """测试数值转换"""
        @ensure_numeric_dataframe
        def process_data(self, df):
            return df
            
        df = pd.DataFrame({
            'numeric': [1, 2, 3],
            'text': ['a', 'b', 'c']
        })
        
        # 创建一个简单的类实例
        class Processor:
            pass
            
        processor = Processor()
        result = process_data(processor, df)
        
        # 应该只保留数值列
        assert 'numeric' in result.columns
        assert 'text' not in result.columns