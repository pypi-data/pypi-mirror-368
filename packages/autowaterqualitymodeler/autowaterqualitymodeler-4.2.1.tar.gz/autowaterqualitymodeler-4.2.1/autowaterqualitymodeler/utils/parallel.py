"""
并行处理工具模块，提供并行计算支持
"""

import logging
import pandas as pd
from typing import Any, Callable
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from functools import partial
import multiprocessing as mp

logger = logging.getLogger(__name__)


class ParallelProcessor:
    """并行处理器，支持多进程和多线程处理"""
    
    def __init__(self, n_workers: int | None = None, use_process: bool = True):
        """
        初始化并行处理器
        
        Args:
            n_workers: 工作进程/线程数，None表示使用CPU核心数
            use_process: 是否使用进程池，False则使用线程池
        """
        if n_workers is None:
            n_workers = mp.cpu_count()
        self.n_workers: int = min(n_workers, mp.cpu_count())
        self.use_process: bool = use_process
        
    def process_metrics(self, 
                       func: Callable[[str], Any],
                       metrics: list[str],
                       *args: Any,
                       **kwargs: Any) -> dict[str, Any]:
        """
        并行处理多个指标
        
        Args:
            func: 处理单个指标的函数
            metrics: 指标列表
            *args: 传递给func的位置参数
            **kwargs: 传递给func的关键字参数
            
        Returns:
            Dict[str, Any]: 指标名到结果的映射
        """
        results = {}
        
        # 如果只有一个指标，直接处理
        if len(metrics) <= 1:
            for metric in metrics:
                try:
                    result = func(metric, *args, **kwargs)
                    if result is not None:
                        results[metric] = result
                except Exception as e:
                    logger.error(f"处理指标 {metric} 失败: {e}")
            return results
        
        # 选择执行器
        Executor = ProcessPoolExecutor if self.use_process else ThreadPoolExecutor
        
        # 并行处理
        with Executor(max_workers=self.n_workers) as executor:
            # 创建部分函数
            process_func = partial(self._process_metric_wrapper, func, args, kwargs)
            
            # 提交任务
            future_to_metric = {
                executor.submit(process_func, metric): metric 
                for metric in metrics
            }
            
            # 收集结果
            for future in as_completed(future_to_metric):
                metric = future_to_metric[future]
                try:
                    result = future.result()
                    if result is not None:
                        results[metric] = result
                    logger.debug(f"成功处理指标: {metric}")
                except Exception as e:
                    logger.error(f"处理指标 {metric} 失败: {e}", exc_info=True)
                    
        return results
    
    @staticmethod
    def _process_metric_wrapper(func: Callable[[str], Any], args: tuple[Any, ...], kwargs: dict[str, Any], metric: str) -> Any:
        """包装函数，用于并行处理"""
        return func(metric, *args, **kwargs)
    
    def parallel_feature_calculation(self,
                                   calculator_func: Callable[[pd.DataFrame, list[dict[str, Any]]], pd.DataFrame],
                                   spectrum_data: pd.DataFrame,
                                   feature_definitions: list[dict[str, Any]],
                                   batch_size: int = 10) -> pd.DataFrame:
        """
        并行计算特征
        
        Args:
            calculator_func: 特征计算函数
            spectrum_data: 光谱数据
            feature_definitions: 特征定义列表
            batch_size: 批处理大小
            
        Returns:
            pd.DataFrame: 计算的特征数据
        """
        # 如果特征数量较少，直接计算
        if len(feature_definitions) <= batch_size:
            return calculator_func(spectrum_data, feature_definitions)
        
        # 分批处理
        features_list = []
        
        Executor = ProcessPoolExecutor if self.use_process else ThreadPoolExecutor
        with Executor(max_workers=self.n_workers) as executor:
            # 分批提交任务
            futures = []
            for i in range(0, len(feature_definitions), batch_size):
                batch = feature_definitions[i:i + batch_size]
                future = executor.submit(calculator_func, spectrum_data, batch)
                futures.append(future)
            
            # 收集结果
            for future in as_completed(futures):
                try:
                    batch_features = future.result()
                    features_list.append(batch_features)
                except Exception as e:
                    logger.error(f"特征计算失败: {e}", exc_info=True)
        
        # 合并结果
        if features_list:
            return pd.concat(features_list, axis=1)
        else:
            return pd.DataFrame(index=spectrum_data.index)


def parallel_model_building(metrics: list[str],
                          build_func: Callable[[str], Any],
                          n_workers: int | None = None) -> dict[str, Any]:
    """
    并行构建多个指标的模型
    
    Args:
        metrics: 指标列表
        build_func: 模型构建函数，接受指标名作为第一个参数
        n_workers: 工作进程数
        
    Returns:
        Dict[str, Any]: 指标名到模型结果的映射
    """
    processor = ParallelProcessor(n_workers=n_workers, use_process=True)
    return processor.process_metrics(build_func, metrics)