"""
核心模块 - 提供主要的建模功能
"""

from .modeler import AutoWaterQualityModeler
from .config_manager import ConfigManager
from .feature_manager import FeatureManager

__all__ = ['AutoWaterQualityModeler', 'ConfigManager', 'FeatureManager']