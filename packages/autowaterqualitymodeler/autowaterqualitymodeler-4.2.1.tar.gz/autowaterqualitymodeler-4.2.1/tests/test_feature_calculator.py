"""
测试特征计算器模块
"""
import pytest
import numpy as np
import pandas as pd
from autowaterqualitymodeler.features.calculator import FeatureCalculator


class TestFeatureCalculator:
    """测试FeatureCalculator类"""
    
    @pytest.fixture
    def calculator(self):
        """创建测试用的计算器实例"""
        return FeatureCalculator()
    
    @pytest.fixture
    def sample_spectrum_df(self):
        """创建测试用的光谱DataFrame"""
        # 创建波长和反射率数据
        wavelengths = np.arange(400, 901, 10)
        n_samples = 5
        
        # 创建DataFrame，列为波长，行为样本
        data = {}
        for wl in wavelengths:
            data[float(wl)] = np.random.rand(n_samples) * 0.5 + 0.1
            
        return pd.DataFrame(data)
    
    def test_band_reflectance(self, calculator, sample_spectrum_df):
        """测试波段反射率计算"""
        # 使用新API计算500nm处的反射率
        feature_def = {
            'name': 'R500',
            'formula': 'ref(500)'
        }
        
        result = calculator.calculate_feature(sample_spectrum_df, feature_def)
        
        assert isinstance(result, pd.Series)
        assert len(result) == len(sample_spectrum_df)
        assert result.name == 'R500'
        assert (result >= 0).all() and (result <= 1).all()  # 反射率应该在0-1之间
    
    def test_band_ratio(self, calculator, sample_spectrum_df):
        """测试波段比值计算"""
        # 计算 R(500)/R(600) 比值
        feature_def = {
            'name': 'Ratio_500_600',
            'formula': 'ratio(500, 600)'
        }
        
        result = calculator.calculate_feature(sample_spectrum_df, feature_def)
        
        assert isinstance(result, pd.Series)
        assert len(result) == len(sample_spectrum_df)
        assert result.name == 'Ratio_500_600'
        # 排除NaN值后检查
        valid_results = result.dropna()
        assert (valid_results > 0).all()  # 比值应该为正数
    
    def test_band_difference(self, calculator, sample_spectrum_df):
        """测试波段差值计算"""
        # 计算 R(600) - R(500)
        feature_def = {
            'name': 'Diff_600_500',
            'formula': 'diff(600, 500)'
        }
        
        result = calculator.calculate_feature(sample_spectrum_df, feature_def)
        
        assert isinstance(result, pd.Series)
        assert len(result) == len(sample_spectrum_df)
        assert result.name == 'Diff_600_500'
        # 差值可以为正或负
    
    def test_band_sum(self, calculator, sample_spectrum_df):
        """测试波段求和计算"""
        # 计算 R(500) + R(600)
        feature_def = {
            'name': 'Sum_500_600',
            'formula': 'ref(500) + ref(600)'
        }
        
        result = calculator.calculate_feature(sample_spectrum_df, feature_def)
        
        assert isinstance(result, pd.Series)
        assert len(result) == len(sample_spectrum_df)
        assert result.name == 'Sum_500_600'
        assert (result > 0).all()  # 求和应该为正数
    
    def test_normalized_difference(self, calculator, sample_spectrum_df):
        """测试归一化差值计算"""
        # 计算 (R(800) - R(670)) / (R(800) + R(670))
        feature_def = {
            'name': 'NDVI',
            'formula': '(ref(800) - ref(670)) / (ref(800) + ref(670))'
        }
        
        result = calculator.calculate_feature(sample_spectrum_df, feature_def)
        
        assert isinstance(result, pd.Series)
        assert len(result) == len(sample_spectrum_df)
        assert result.name == 'NDVI'
        # 排除NaN值后检查
        valid_results = result.dropna()
        assert (valid_results >= -1).all() and (valid_results <= 1).all()  # 归一化差值应该在-1到1之间
    
    def test_three_band_index(self, calculator, sample_spectrum_df):
        """测试三波段指数计算"""
        # 计算 (R(700) - R(670)) / (R(700) + R(670)) * R(800)
        feature_def = {
            'name': 'ThreeBandIndex',
            'formula': '((ref(700) - ref(670)) / (ref(700) + ref(670))) * ref(800)'
        }
        
        result = calculator.calculate_feature(sample_spectrum_df, feature_def)
        
        assert isinstance(result, pd.Series)
        assert len(result) == len(sample_spectrum_df)
        assert result.name == 'ThreeBandIndex'
    
    def test_invalid_wavelength(self, calculator, sample_spectrum_df):
        """测试无效波长处理"""
        # 测试超出范围的波长 - 应该使用最接近的波长
        feature_def = {
            'name': 'R1000',
            'formula': 'ref(1000)'
        }
        
        # 不应该引发异常，而是使用最接近的波长
        result = calculator.calculate_feature(sample_spectrum_df, feature_def)
        
        assert isinstance(result, pd.Series)
        assert len(result) == len(sample_spectrum_df)
        assert result.name == 'R1000'
        # 结果应该等于最大波长的值
        assert (result == sample_spectrum_df[900.0]).all()
    
    def test_complex_formula(self, calculator, sample_spectrum_df):
        """测试复杂公式计算"""
        # 测试包含多种运算的复杂公式
        feature_def = {
            'name': 'ComplexFeature',
            'formula': '(ref(500) + ref(600)) / 2 * (1 - ref(700))'
        }
        
        result = calculator.calculate_feature(sample_spectrum_df, feature_def)
        
        assert isinstance(result, pd.Series)
        assert len(result) == len(sample_spectrum_df)
        assert result.name == 'ComplexFeature'
    
    def test_sum_function(self, calculator, sample_spectrum_df):
        """测试sum函数"""
        # 计算波段范围内的和
        feature_def = {
            'name': 'Sum_500_700',
            'formula': 'sum(500, 700)'
        }
        
        result = calculator.calculate_feature(sample_spectrum_df, feature_def)
        
        assert isinstance(result, pd.Series)
        assert len(result) == len(sample_spectrum_df)
        assert result.name == 'Sum_500_700'
        assert (result > 0).all()
    
    def test_mean_function(self, calculator, sample_spectrum_df):
        """测试mean函数"""
        # 计算波段范围内的均值
        feature_def = {
            'name': 'Mean_500_700',
            'formula': 'mean(500, 700)'
        }
        
        result = calculator.calculate_feature(sample_spectrum_df, feature_def)
        
        assert isinstance(result, pd.Series)
        assert len(result) == len(sample_spectrum_df)
        assert result.name == 'Mean_500_700'
        assert (result > 0).all()
    
    def test_abs_function(self, calculator, sample_spectrum_df):
        """测试abs函数"""
        # 计算绝对值
        feature_def = {
            'name': 'Abs_Diff',
            'formula': 'abs(ref(500) - ref(600))'
        }
        
        result = calculator.calculate_feature(sample_spectrum_df, feature_def)
        
        assert isinstance(result, pd.Series)
        assert len(result) == len(sample_spectrum_df)
        assert result.name == 'Abs_Diff'
        assert (result >= 0).all()  # 绝对值应该非负
    
    def test_log_function(self, calculator, sample_spectrum_df):
        """测试log函数"""
        # 计算对数
        feature_def = {
            'name': 'Log_R500',
            'formula': 'log(ref(500))'
        }
        
        result = calculator.calculate_feature(sample_spectrum_df, feature_def)
        
        assert isinstance(result, pd.Series)
        assert len(result) == len(sample_spectrum_df)
        assert result.name == 'Log_R500'
    
    def test_calculate_features_batch(self, calculator, sample_spectrum_df):
        """测试批量特征计算"""
        feature_definitions = [
            {'name': 'R500', 'formula': 'ref(500)'},
            {'name': 'R600', 'formula': 'ref(600)'},
            {'name': 'NDVI', 'formula': '(ref(800) - ref(670)) / (ref(800) + ref(670))'},
            {'name': 'Ratio_500_600', 'formula': 'ratio(500, 600)'}
        ]
        
        result = calculator.calculate_features(sample_spectrum_df, feature_definitions)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == len(sample_spectrum_df)
        assert len(result.columns) == 4
        assert all(col in result.columns for col in ['R500', 'R600', 'NDVI', 'Ratio_500_600'])