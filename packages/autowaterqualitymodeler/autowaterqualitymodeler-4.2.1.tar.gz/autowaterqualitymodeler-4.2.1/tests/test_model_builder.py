"""
测试模型构建器模块
"""
import pytest
import numpy as np
import pandas as pd
from autowaterqualitymodeler.models.builder import ModelBuilder


class TestModelBuilder:
    """测试ModelBuilder类"""
    
    @pytest.fixture
    def builder(self):
        """创建测试用的构建器实例"""
        return ModelBuilder()
    
    @pytest.fixture
    def sample_data(self):
        """创建测试用的数据"""
        np.random.seed(42)
        n_samples = 50
        
        # 创建特征数据
        x = np.random.rand(n_samples) * 10 + 0.1  # 确保为正值
        # 创建目标值（幂函数关系 + 噪声）
        y = 2.5 * (x ** 0.8) + np.random.randn(n_samples) * 0.5
        y = np.abs(y)  # 确保为正值
        
        return x, y
    
    def test_builder_initialization(self, builder):
        """测试构建器初始化"""
        assert builder is not None
        # 检查私有方法存在
        assert hasattr(builder, 'tune_linear')

    def test_tune_linear(self, builder):
        """测试线性调整功能"""
        # 创建预测值和实测值
        predicted = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])
        measured = pd.Series([0.9, 2.1, 2.9, 4.2, 4.8])
        
        # 进行线性调整
        tuning_factor = builder.tune_linear(predicted, measured)
        
        # 检查返回值
        assert tuning_factor is not None
        assert isinstance(tuning_factor, (float, np.floating))
        assert tuning_factor > 0  # 调整系数应该为正
    
    def test_tune_linear_with_missing_data(self, builder):
        """测试带缺失值的线性调整"""
        # 创建带缺失值的数据
        predicted = pd.Series([1.0, 2.0, np.nan, 4.0, 5.0])
        measured = pd.Series([0.9, np.nan, 2.9, 4.2, 4.8])
        
        # 进行线性调整
        tuning_factor = builder.tune_linear(predicted, measured)
        
        # 应该能够处理缺失值
        assert tuning_factor is not None or len(predicted.dropna()) < 2