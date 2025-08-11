"""
AutoWaterQualityModeler - 自动水质光谱建模工具

提供了一键式水质建模、预测和评估功能。
"""

# 版本号获取，优先级：包元数据 > _version.py > fallback
try:
    from importlib.metadata import version, PackageNotFoundError
    try:
        __version__ = version("autowaterqualitymodeler")
    except PackageNotFoundError:
        # 开发环境或未安装的包，尝试从_version.py获取
        try:
            from ._version import __version__
        except ImportError:
            __version__ = "0.1.0"  # fallback版本
except ImportError:
    # Python < 3.8，使用importlib_metadata
    try:
        from importlib_metadata import version, PackageNotFoundError
        try:
            __version__ = version("autowaterqualitymodeler")
        except PackageNotFoundError:
            try:
                from ._version import __version__
            except ImportError:
                __version__ = "0.1.0"
    except ImportError:
        # 完全fallback
        try:
            from ._version import __version__
        except ImportError:
            __version__ = "0.1.0"

# 导出主要类
from .core.modeler import AutoWaterQualityModeler
from .preprocessing.spectrum_processor import SpectrumProcessor
from .features.calculator import FeatureCalculator
from .models.builder import ModelBuilder

__all__ = [
    'AutoWaterQualityModeler',
    'SpectrumProcessor',
    'FeatureCalculator',
    'ModelBuilder',
    '__version__'
] 