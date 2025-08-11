"""
集成测试
"""

import pytest
import pandas as pd
import numpy as np
import os
from autowaterqualitymodeler.core.modeler import AutoWaterQualityModeler


class TestIntegration:
    """端到端集成测试"""
    
    def test_full_modeling_pipeline(self, temp_dir):
        """测试完整的建模流程"""
        # 创建更大的测试数据集
        n_samples = 20
        wavelengths = list(range(400, 901, 10))
        
        # 创建光谱数据
        spectrum_data = pd.DataFrame()
        for wl in wavelengths:
            spectrum_data[wl] = np.random.uniform(0.1, 0.8, n_samples)
            
        # 创建水质指标数据（与光谱数据有一定相关性）
        base_values = np.random.uniform(0, 1, n_samples)
        metric_data = pd.DataFrame({
            'turbidity': 10 + 40 * base_values + np.random.normal(0, 5, n_samples),
            'ss': 20 + 80 * base_values + np.random.normal(0, 10, n_samples),
            'chla': 5 + 15 * base_values + np.random.normal(0, 2, n_samples),
            'tn': 1 + 4 * base_values + np.random.normal(0, 0.5, n_samples),
            'tp': 0.1 + 0.4 * base_values + np.random.normal(0, 0.05, n_samples)
        })
        
        # 确保所有值为正
        metric_data = metric_data.abs()
        
        # 创建建模器
        modeler = AutoWaterQualityModeler()
        
        # 执行建模
        result = modeler.fit(
            spectrum_data=spectrum_data,
            metric_data=metric_data,
            data_type="aerospot"
        )
        
        # 验证结果
        assert result is not None
        assert result.model_type == 1  # 自动建模
        assert len(result.models) > 0
        assert not result.predictions.empty
        
        # 测试保存模型
        model_path = os.path.join(temp_dir, "integration_test_model.json")
        saved_path = modeler.save_model(result.models, model_path)
        assert os.path.exists(saved_path)
        
        # 测试加载模型
        loaded_models = modeler.load_model(saved_path)
        assert loaded_models is not None
        
    def test_modeling_with_matched_indices(self):
        """测试使用匹配索引的建模"""
        # 创建数据
        n_total = 30
        n_matched = 20
        wavelengths = list(range(400, 901, 50))
        
        # 所有样本的光谱数据
        all_spectrum = pd.DataFrame()
        for wl in wavelengths:
            all_spectrum[wl] = np.random.uniform(0.1, 0.8, n_total)
            
        # 匹配样本的索引
        matched_idx = list(range(n_matched))
        
        # 只有匹配样本的实测数据
        metric_data = pd.DataFrame({
            'turbidity': np.random.uniform(10, 50, n_matched),
            'ss': np.random.uniform(20, 100, n_matched)
        })
        
        # 创建合并数据（模拟预测值）
        origin_merged_data = pd.DataFrame({
            'turbidity': np.random.uniform(8, 48, n_total),
            'ss': np.random.uniform(18, 98, n_total)
        })
        
        # 建模
        modeler = AutoWaterQualityModeler()
        result = modeler.fit(
            spectrum_data=all_spectrum,
            metric_data=metric_data,
            matched_idx=matched_idx,
            origin_merged_data=origin_merged_data
        )
        
        # 验证结果
        assert result is not None
        assert result.has_all_predictions()
        assert len(result.predictions) == n_matched
        assert len(result.all_predictions) == n_total
        
    def test_parallel_processing(self):
        """测试并行处理功能"""
        # 创建包含多个指标的数据
        n_samples = 15
        wavelengths = list(range(400, 901, 20))
        
        spectrum_data = pd.DataFrame()
        for wl in wavelengths:
            spectrum_data[wl] = np.random.uniform(0.1, 0.8, n_samples)
            
        # 创建10个水质指标
        metric_data = pd.DataFrame()
        for i in range(10):
            metric_data[f'metric_{i}'] = np.random.uniform(1, 100, n_samples)
            
        # 使用并行处理建模
        modeler = AutoWaterQualityModeler()
        result = modeler.fit(
            spectrum_data=spectrum_data,
            metric_data=metric_data
        )
        
        # 验证所有指标都有模型
        assert len(result.models) > 0
        assert len(result.predictions.columns) > 0