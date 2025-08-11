"""
测试光谱处理器模块
"""
import pytest
import numpy as np
import pandas as pd
from autowaterqualitymodeler.preprocessing.spectrum_processor import SpectrumProcessor


class TestSpectrumProcessor:
    """测试SpectrumProcessor类"""
    
    @pytest.fixture
    def processor(self):
        """创建测试用的处理器实例"""
        return SpectrumProcessor(
            min_wavelength=400,
            max_wavelength=900,
            smooth_window=5,
            smooth_order=2
        )
    
    @pytest.fixture
    def sample_spectrum_data(self):
        """创建测试用的光谱数据"""
        # 创建波长从400到900的测试数据
        wavelengths = np.arange(400, 901, 50)
        n_samples = 5
        
        # 创建随机光谱数据
        np.random.seed(42)
        data = np.random.rand(n_samples, len(wavelengths)) * 0.5 + 0.2
        
        # 创建DataFrame
        df = pd.DataFrame(data, columns=[str(w) for w in wavelengths])
        df.index = [f"sample_{i}" for i in range(n_samples)]
        
        return df
    
    def test_processor_initialization(self, processor):
        """测试处理器初始化"""
        assert processor.min_wavelength == 400
        assert processor.max_wavelength == 900
        assert processor.smooth_window == 5
        assert processor.smooth_order == 2
    
    def test_filter_wavelengths(self, processor, sample_spectrum_data):
        """测试波长过滤功能"""
        # 设置更窄的波长范围
        processor.min_wavelength = 450
        processor.max_wavelength = 850
        
        # 使用正确的方法名
        filtered_data = processor._filter_wavelength(sample_spectrum_data)
        
        # 检查过滤后的波长范围
        wavelengths = [float(col) for col in filtered_data.columns]
        assert min(wavelengths) >= 450
        assert max(wavelengths) <= 850
        assert filtered_data.shape[0] == sample_spectrum_data.shape[0]
    
    def test_filter_anomalies(self, processor, sample_spectrum_data):
        """测试异常值过滤"""
        # 添加一些异常值
        data_with_outlier = sample_spectrum_data.copy()
        data_with_outlier.iloc[0, 5] = 10.0  # 添加一个大于1的值
        data_with_outlier.iloc[1, 3] = -0.5  # 添加一个小于0的值
        
        # 过滤异常值
        filtered_data = processor._filter_anomalies(data_with_outlier)
        
        # 检查异常值是否被处理
        assert (filtered_data >= 0).all().all()  # 所有值应该非负
        assert (filtered_data <= 1.0).all().all() or filtered_data.max().max() < 10.0  # 异常值应该被处理
    
    def test_preprocess(self, processor, sample_spectrum_data):
        """测试完整的预处理流程"""
        processed_data = processor.preprocess(sample_spectrum_data)
        
        # 检查输出格式
        assert isinstance(processed_data, pd.DataFrame)
        
        # 检查形状是否正确
        assert processed_data.shape[0] == sample_spectrum_data.shape[0]
        
        # 检查波长是否为整数且在指定范围内
        wavelengths = processed_data.columns.values
        assert wavelengths.min() >= processor.min_wavelength
        assert wavelengths.max() <= processor.max_wavelength
        
        # 检查波长间隔是否为1
        if len(wavelengths) > 1:
            assert np.all(np.diff(wavelengths) == 1)
    
    def test_empty_data_handling(self, processor):
        """测试空数据处理"""
        empty_df = pd.DataFrame()
        
        # 预期应该引发异常，因为空DataFrame无法处理
        with pytest.raises(Exception):
            processor.preprocess(empty_df)
    
    def test_resample_spectrum(self, processor, sample_spectrum_data):
        """测试光谱重采样"""
        # 测试重采样功能
        resampled_data = processor._resample_spectrum(sample_spectrum_data)
        
        # 检查输出
        assert isinstance(resampled_data, pd.DataFrame)
        assert resampled_data.shape[0] == sample_spectrum_data.shape[0]
        
        # 检查波长是否为整数值
        wavelengths = resampled_data.columns.values
        assert all(isinstance(wl, (int, np.integer)) or wl == int(wl) for wl in wavelengths)
        
        # 检查波长间隔是否为1
        if len(wavelengths) > 1:
            assert np.all(np.diff(wavelengths) == 1)
    
    def test_smooth_spectrum(self, processor):
        """测试光谱平滑"""
        # 创建带噪声的光谱数据
        wavelengths = np.arange(400, 901, 1)
        n_samples = 3
        
        # 创建平滑的基础信号
        base_signal = np.sin(np.linspace(0, 4*np.pi, len(wavelengths))) * 0.2 + 0.5
        
        # 添加噪声
        np.random.seed(42)
        noise = np.random.normal(0, 0.02, (n_samples, len(wavelengths)))
        data = base_signal + noise
        
        # 创建DataFrame
        df = pd.DataFrame(data, columns=wavelengths)
        
        # 应用平滑
        smoothed_data = processor._smooth_spectrum(df)
        
        # 检查输出
        assert isinstance(smoothed_data, pd.DataFrame)
        assert smoothed_data.shape == df.shape
        
        # 平滑后的数据应该有更小的标准差（噪声减少）
        original_std = df.std(axis=1).mean()
        smoothed_std = smoothed_data.std(axis=1).mean()
        # 由于是对列（波长维度）进行平滑，应该检查行内的变化
        original_diff = df.diff(axis=1).abs().mean().mean()
        smoothed_diff = smoothed_data.diff(axis=1).abs().mean().mean()
        assert smoothed_diff < original_diff  # 平滑后相邻值的差异应该更小
    
    def test_invalid_wavelength_range(self, processor):
        """测试无效的波长范围"""
        # 创建波长范围完全在处理范围外的数据
        wavelengths = np.arange(1000, 1101, 10)
        data = np.random.rand(3, len(wavelengths))
        df = pd.DataFrame(data, columns=wavelengths)
        
        # 处理数据，期望抛出异常
        with pytest.raises(Exception):
            processor.preprocess(df)
    
    def test_mixed_wavelength_types(self, processor):
        """测试混合波长类型（字符串和数字）"""
        # 创建混合类型的列名
        df = pd.DataFrame({
            '400': [0.3, 0.4, 0.5],
            '450.5': [0.35, 0.45, 0.55],
            500: [0.4, 0.5, 0.6],
            '600.0': [0.45, 0.55, 0.65]
        })
        
        # 处理应该能够处理混合类型
        processed = processor.preprocess(df)
        
        assert isinstance(processed, pd.DataFrame)
        assert not processed.empty