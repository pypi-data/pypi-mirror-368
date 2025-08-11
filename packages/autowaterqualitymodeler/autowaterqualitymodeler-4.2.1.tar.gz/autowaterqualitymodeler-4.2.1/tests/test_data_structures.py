"""
数据结构测试
"""

import pytest
import pandas as pd
import numpy as np
from autowaterqualitymodeler.core.data_structures import (
    ModelResult, FeatureModel, MetricModelResult, ModelingResult,
    ProcessingConfig, ValidationResult
)


class TestModelResult:
    """测试ModelResult数据类"""
    
    def test_model_result_creation(self):
        """测试ModelResult创建"""
        result = ModelResult(
            model_type='power',
            parameters={'a': 1.0, 'b': 2.0},
            metrics={'r2': 0.95, 'rmse': 0.1},
            formula='y = 1.0 * x^2.0'
        )
        
        assert result.model_type == 'power'
        assert result.parameters['a'] == 1.0
        assert result.metrics['r2'] == 0.95
        
    def test_model_result_to_dict(self):
        """测试ModelResult转换为字典"""
        result = ModelResult(
            model_type='linear',
            parameters={'a': 2.0, 'b': 1.0},
            metrics={'r2': 0.9, 'rmse': 0.2},
            formula='y = 2.0 * x + 1.0'
        )
        
        data = result.to_dict()
        assert data['type'] == 'linear'
        assert data['params']['a'] == 2.0
        assert data['metrics']['rmse'] == 0.2


class TestModelingResult:
    """测试ModelingResult数据类"""
    
    def test_modeling_result_creation(self):
        """测试ModelingResult创建"""
        predictions = pd.DataFrame({'metric1': [1, 2, 3]})
        result = ModelingResult(
            model_type=1,
            models={'metric1': {'a': 1.0}},
            predictions=predictions
        )
        
        assert result.model_type == 1
        assert result.models['metric1']['a'] == 1.0
        assert len(result.predictions) == 3
        
    def test_has_all_predictions(self):
        """测试has_all_predictions方法"""
        # 没有all_predictions
        result1 = ModelingResult(
            model_type=1,
            models={},
            predictions=pd.DataFrame()
        )
        assert not result1.has_all_predictions()
        
        # 有all_predictions
        result2 = ModelingResult(
            model_type=1,
            models={},
            predictions=pd.DataFrame(),
            all_predictions=pd.DataFrame({'metric1': [1, 2, 3]})
        )
        assert result2.has_all_predictions()


class TestProcessingConfig:
    """测试ProcessingConfig数据类"""
    
    def test_default_values(self):
        """测试默认值"""
        config = ProcessingConfig()
        
        assert config.min_wavelength == 400
        assert config.max_wavelength == 900
        assert config.smooth_window == 11
        assert config.smooth_order == 3
        assert config.data_type == "aerospot"
        
    def test_validation(self):
        """测试验证方法"""
        # 有效配置
        config1 = ProcessingConfig()
        # 不应抛出异常（自动调用validate）
        
        # 无效配置 - 波长范围
        with pytest.raises(ValueError, match="min_wavelength must be less than max_wavelength"):
            ProcessingConfig(min_wavelength=900, max_wavelength=400)
            
        # 无效配置 - 平滑窗口
        with pytest.raises(ValueError, match="smooth_window must be at least 3"):
            ProcessingConfig(smooth_window=2)


class TestValidationResult:
    """测试ValidationResult数据类"""
    
    def test_initial_state(self):
        """测试初始状态"""
        result = ValidationResult(is_valid=True)
        
        assert result.is_valid
        assert len(result.errors) == 0
        assert len(result.warnings) == 0
        
    def test_add_error(self):
        """测试添加错误"""
        result = ValidationResult(is_valid=True)
        
        result.add_error("测试错误")
        assert not result.is_valid
        assert len(result.errors) == 1
        assert result.errors[0] == "测试错误"
        
    def test_add_warning(self):
        """测试添加警告"""
        result = ValidationResult(is_valid=True)
        
        result.add_warning("测试警告")
        assert result.is_valid  # 警告不影响有效性
        assert len(result.warnings) == 1
        assert result.warnings[0] == "测试警告"