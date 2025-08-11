"""
测试配置文件
"""

import pytest
import sys
import os
import logging

# 将项目根目录添加到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 配置测试日志
logging.basicConfig(level=logging.DEBUG)


@pytest.fixture
def sample_spectrum_data():
    """提供示例光谱数据"""
    import pandas as pd
    import numpy as np
    
    # 创建示例数据
    wavelengths = list(range(400, 901, 10))
    n_samples = 10
    
    data = {}
    for wl in wavelengths:
        # 生成随机反射率数据（0-1之间）
        data[wl] = np.random.uniform(0.1, 0.9, n_samples)
    
    return pd.DataFrame(data)


@pytest.fixture
def sample_metric_data():
    """提供示例水质指标数据"""
    import pandas as pd
    import numpy as np
    
    n_samples = 10
    
    data = {
        'turbidity': np.random.uniform(5, 50, n_samples),
        'ss': np.random.uniform(10, 100, n_samples),
        'chla': np.random.uniform(1, 20, n_samples),
        'tn': np.random.uniform(0.5, 5, n_samples),
        'tp': np.random.uniform(0.05, 0.5, n_samples)
    }
    
    return pd.DataFrame(data)


@pytest.fixture
def config_manager():
    """提供配置管理器实例"""
    from autowaterqualitymodeler.core.config_manager import ConfigManager
    return ConfigManager()


@pytest.fixture
def processing_config():
    """提供处理配置"""
    from autowaterqualitymodeler.core.data_structures import ProcessingConfig
    return ProcessingConfig()


@pytest.fixture
def temp_dir(tmp_path):
    """提供临时目录"""
    return tmp_path