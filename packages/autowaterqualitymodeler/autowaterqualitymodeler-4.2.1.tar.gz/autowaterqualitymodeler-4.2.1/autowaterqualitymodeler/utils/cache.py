"""
缓存管理模块，提供特征计算的缓存功能
"""

import hashlib
import pickle
import os
import logging
import platform
from typing import Any, Callable
from functools import wraps
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class CacheManager:
    """缓存管理器，用于缓存计算结果"""
    
    def __init__(self, cache_dir: str | None = None, enabled: bool = True):
        """
        初始化缓存管理器
        
        Args:
            cache_dir: 缓存目录，None则使用默认目录
            enabled: 是否启用缓存
        """
        self.enabled = enabled
        
        if cache_dir is None:
            # 使用跨平台的用户缓存目录，避免权限问题
            cache_dir = self._get_default_cache_dir()
        
        self.cache_dir = cache_dir
        self._cache = {}  # 内存缓存
        
        # 尝试创建缓存目录，如果失败则禁用文件缓存
        if self.enabled:
            try:
                os.makedirs(self.cache_dir, exist_ok=True)
                self._file_cache_enabled = True
                logger.debug(f"缓存目录创建成功: {self.cache_dir}")
            except (OSError, PermissionError) as e:
                logger.warning(f"无法创建缓存目录 {self.cache_dir}: {e}，将禁用文件缓存，仅使用内存缓存")
                self._file_cache_enabled = False
        else:
            self._file_cache_enabled = False
    
    def _get_default_cache_dir(self) -> str:
        """获取跨平台的默认缓存目录"""
        system = platform.system().lower()
        
        if system == 'windows':
            # Windows: 使用 LOCALAPPDATA 或 APPDATA
            cache_base = os.environ.get('LOCALAPPDATA')
            if not cache_base:
                cache_base = os.environ.get('APPDATA')
            if not cache_base:
                # 降级到用户目录
                cache_base = os.path.expanduser("~")
            cache_dir = os.path.join(cache_base, 'AutoWaterQualityModeler', 'cache')
            
        elif system == 'darwin':  # macOS
            # macOS: 使用 ~/Library/Caches
            cache_dir = os.path.join(
                os.path.expanduser("~"),
                'Library', 'Caches', 'AutoWaterQualityModeler'
            )
            
        else:  # Linux和其他Unix系统
            # Linux: 使用 XDG_CACHE_HOME 或 ~/.cache
            cache_base = os.environ.get('XDG_CACHE_HOME')
            if not cache_base:
                cache_base = os.path.join(os.path.expanduser("~"), '.cache')
            cache_dir = os.path.join(cache_base, 'autowaterqualitymodeler')
        
        return cache_dir
        
    def _generate_key(self, *args, **kwargs) -> str:
        """生成缓存键"""
        # 将参数转换为字符串
        key_parts = []
        
        for arg in args:
            if isinstance(arg, (pd.DataFrame, pd.Series)):
                # 对DataFrame/Series使用shape和数据的hash
                key_parts.append(f"{type(arg).__name__}_{arg.shape}_{pd.util.hash_pandas_object(arg).sum()}")
            elif isinstance(arg, np.ndarray):
                # 对numpy数组使用shape和数据的hash
                key_parts.append(f"ndarray_{arg.shape}_{hash(arg.tobytes())}")
            elif isinstance(arg, (list, dict)):
                # 对列表和字典使用字符串表示
                key_parts.append(str(arg))
            else:
                # 其他类型直接转换为字符串
                key_parts.append(str(arg))
                
        # 添加关键字参数
        for k, v in sorted(kwargs.items()):
            key_parts.append(f"{k}={v}")
            
        # 生成hash
        key_str = "_".join(key_parts)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, key: str) -> Any | None:
        """从缓存获取数据"""
        if not self.enabled:
            return None
            
        # 先检查内存缓存
        if key in self._cache:
            logger.debug(f"从内存缓存命中: {key}")
            return self._cache[key]
            
        # 检查文件缓存（仅在文件缓存启用时）
        if self._file_cache_enabled:
            cache_file = os.path.join(self.cache_dir, f"{key}.pkl")
            if os.path.exists(cache_file):
                try:
                    with open(cache_file, 'rb') as f:
                        data = pickle.load(f)
                    # 同时加载到内存缓存
                    self._cache[key] = data
                    logger.debug(f"从文件缓存命中: {key}")
                    return data
                except Exception as e:
                    logger.warning(f"读取缓存文件失败: {e}")
                    
        return None
    
    def set(self, key: str, value: Any) -> None:
        """设置缓存"""
        if not self.enabled:
            return
            
        # 保存到内存缓存
        self._cache[key] = value
        
        # 保存到文件缓存（仅在文件缓存启用时）
        if self._file_cache_enabled:
            cache_file = os.path.join(self.cache_dir, f"{key}.pkl")
            try:
                with open(cache_file, 'wb') as f:
                    pickle.dump(value, f)
                logger.debug(f"保存到缓存: {key}")
            except Exception as e:
                logger.warning(f"保存缓存文件失败: {e}")
                # 文件写入失败时，禁用文件缓存
                self._file_cache_enabled = False
                logger.warning("文件缓存已禁用，将仅使用内存缓存")
    
    def clear(self) -> None:
        """清空缓存"""
        self._cache.clear()
        
        # 仅在文件缓存启用时清理文件缓存
        if self._file_cache_enabled and os.path.exists(self.cache_dir):
            for file in os.listdir(self.cache_dir):
                if file.endswith('.pkl'):
                    try:
                        os.remove(os.path.join(self.cache_dir, file))
                    except Exception as e:
                        logger.warning(f"删除缓存文件失败: {e}")
                        
        logger.info("缓存已清空")


def cached(cache_manager: CacheManager | None = None):
    """
    缓存装饰器
    
    Args:
        cache_manager: 缓存管理器实例
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 如果没有提供缓存管理器，直接执行函数
            if cache_manager is None or not cache_manager.enabled:
                return func(*args, **kwargs)
                
            # 生成缓存键
            cache_key = cache_manager._generate_key(
                func.__name__, *args, **kwargs
            )
            
            # 尝试从缓存获取
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
                
            # 执行函数
            result = func(*args, **kwargs)
            
            # 保存到缓存
            cache_manager.set(cache_key, result)
            
            return result
            
        return wrapper
    return decorator


# 全局缓存管理器实例
_global_cache_manager = None


def get_global_cache_manager() -> CacheManager:
    """获取全局缓存管理器"""
    global _global_cache_manager
    if _global_cache_manager is None:
        _global_cache_manager = CacheManager()
    return _global_cache_manager


def set_cache_enabled(enabled: bool) -> None:
    """设置缓存是否启用"""
    cache_manager = get_global_cache_manager()
    cache_manager.enabled = enabled
    logger.info(f"缓存已{'启用' if enabled else '禁用'}")