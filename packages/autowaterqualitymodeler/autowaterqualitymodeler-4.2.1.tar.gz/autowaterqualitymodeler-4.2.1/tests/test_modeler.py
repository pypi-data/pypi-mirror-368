"""
AutoWaterQualityModeler主模块测试
"""

import pytest
import pandas as pd
import numpy as np
from autowaterqualitymodeler.core.modeler import AutoWaterQualityModeler
from autowaterqualitymodeler.core.exceptions import (
    DataValidationError, InvalidParameterError, InsufficientDataError
)


class TestAutoWaterQualityModeler:
    """测试AutoWaterQualityModeler类"""
    
    def test_initialization(self):
        """测试初始化"""
        modeler = AutoWaterQualityModeler()
        
        assert modeler.config.min_wavelength == 400
        assert modeler.config.max_wavelength == 900
        assert modeler.config_manager is not None
        assert modeler.feature_manager is not None
        
    def test_fit_with_valid_data(self, sample_spectrum_data, sample_metric_data):
        """测试使用有效数据进行建模"""
        modeler = AutoWaterQualityModeler()
        
        result = modeler.fit(
            spectrum_data=sample_spectrum_data,
            metric_data=sample_metric_data,
            data_type="aerospot"
        )
        
        assert result is not None
        assert result.model_type in [0, 1]
        assert isinstance(result.models, dict)
        assert isinstance(result.predictions, pd.DataFrame)
        
    def test_fit_with_invalid_data_type(self, sample_spectrum_data, sample_metric_data):
        """测试无效的数据类型"""
        modeler = AutoWaterQualityModeler()
        
        with pytest.raises(InvalidParameterError, match="data_type"):
            modeler.fit(
                spectrum_data=sample_spectrum_data,
                metric_data=sample_metric_data,
                data_type="invalid_type"
            )
            
    def test_fit_with_empty_data(self):
        """测试空数据"""
        modeler = AutoWaterQualityModeler()
        
        empty_spectrum = pd.DataFrame()
        empty_metric = pd.DataFrame()
        
        with pytest.raises(DataValidationError, match="光谱数据为空"):
            modeler.fit(
                spectrum_data=empty_spectrum,
                metric_data=empty_metric
            )
            
    def test_fit_with_non_numeric_data(self):
        """测试非数值数据"""
        modeler = AutoWaterQualityModeler()
        
        # 创建包含文本的DataFrame
        spectrum_data = pd.DataFrame({
            '400': [0.1, 0.2],
            '500': ['a', 'b']  # 非数值
        })
        metric_data = pd.DataFrame({
            'turbidity': [10, 20]
        })
        
        with pytest.raises(DataValidationError, match="光谱数据"):
            modeler.fit(
                spectrum_data=spectrum_data,
                metric_data=metric_data
            )
            
    def test_save_and_load_model(self, sample_spectrum_data, sample_metric_data, temp_dir):
        """测试模型保存和加载"""
        modeler = AutoWaterQualityModeler()
        
        # 建模
        result = modeler.fit(
            spectrum_data=sample_spectrum_data,
            metric_data=sample_metric_data
        )
        
        # 保存模型
        model_path = temp_dir / "test_model.json"
        saved_path = modeler.save_model(result.models, str(model_path))
        
        assert saved_path == str(model_path)
        assert model_path.exists()
        
        # 加载模型
        loaded_models = modeler.load_model(str(model_path))
        assert isinstance(loaded_models, dict)
        
    def test_insufficient_data_error(self):
        """测试数据不足错误"""
        modeler = AutoWaterQualityModeler()
        
        # 创建少量数据
        spectrum_data = pd.DataFrame({
            '400': [0.1, 0.2],
            '500': [0.3, 0.4]
        })
        metric_data = pd.DataFrame({
            'turbidity': [10, 20]
        })
        
        # 这应该触发模型微调，但没有提供origin_merged_data
        with pytest.raises(InsufficientDataError):
            modeler.fit(
                spectrum_data=spectrum_data,
                metric_data=metric_data
            )


class TestProcessingConfig:
    """测试处理配置"""
    
    def test_config_validation(self):
        """测试配置验证"""
        from autowaterqualitymodeler.core.data_structures import ProcessingConfig
        
        # 有效配置
        config = ProcessingConfig()
        # 不应抛出异常（自动调用validate）
        
        # 无效配置
        with pytest.raises(ValueError):
            ProcessingConfig(
                min_wavelength=900,
                max_wavelength=400
            )