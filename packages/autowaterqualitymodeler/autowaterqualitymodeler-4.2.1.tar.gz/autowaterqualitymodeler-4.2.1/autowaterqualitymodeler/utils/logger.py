"""
日志系统配置模块

提供统一的日志配置功能，支持输出到文件和控制台，增强的日志格式和性能指标记录
"""

import os
import sys
import json
import time
import logging
import logging.handlers
from datetime import datetime
from functools import wraps
import traceback

# 全局日志性能统计
performance_stats = {}

def log_execution_time(logger=None):
    """
    函数执行时间装饰器，记录函数执行时间到日志
    
    Args:
        logger: 日志记录器，如果为None则使用函数模块的默认记录器
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 获取适当的日志记录器
            nonlocal logger
            if logger is None:
                logger = logging.getLogger(func.__module__)
                
            # 记录函数调用信息
            logger.debug(f"调用函数: {func.__name__} 开始")
            
            # 记录开始时间
            start_time = time.time()
            
            try:
                # 执行原函数
                result = func(*args, **kwargs)
                elapsed = time.time() - start_time
                
                # 更新性能统计
                func_key = f"{func.__module__}.{func.__name__}"
                if func_key not in performance_stats:
                    performance_stats[func_key] = {
                        'count': 0, 
                        'total_time': 0, 
                        'min_time': float('inf'), 
                        'max_time': 0
                    }
                
                stats = performance_stats[func_key]
                stats['count'] += 1
                stats['total_time'] += elapsed
                stats['min_time'] = min(stats['min_time'], elapsed)
                stats['max_time'] = max(stats['max_time'], elapsed)
                
                # 记录执行结果
                logger.debug(f"函数 {func.__name__} 执行完成，耗时: {elapsed:.4f}秒")
                return result
            except Exception as e:
                elapsed = time.time() - start_time
                logger.error(
                    f"函数 {func.__name__} 执行失败，耗时: {elapsed:.4f}秒，异常: {e}",
                    exc_info=True
                )
                raise
        return wrapper
    return decorator

def get_performance_stats():
    """获取性能统计信息"""
    result = {}
    for func_key, stats in performance_stats.items():
        if stats['count'] > 0:
            result[func_key] = {
                'count': stats['count'],
                'total_time': stats['total_time'],
                'avg_time': stats['total_time'] / stats['count'],
                'min_time': stats['min_time'],
                'max_time': stats['max_time']
            }
    return result

class JsonFormatter(logging.Formatter):
    """JSON格式的日志格式化器"""
    
    def format(self, record):
        log_data = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # 添加异常信息
        if record.exc_info and record.exc_info[0] is not None:
            log_data['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': traceback.format_exception(*record.exc_info)
            }
            
        # 添加自定义字段
        if hasattr(record, 'data') and getattr(record, 'data', None):
            log_data['data'] = getattr(record, 'data')
            
        return json.dumps(log_data, ensure_ascii=False)

class ContextAdapter(logging.LoggerAdapter):
    """上下文日志适配器，支持添加额外信息"""
    
    def process(self, msg, kwargs):
        # 如果kwargs中有context，将其添加到额外数据中
        if 'context' in kwargs:
            context = kwargs.pop('context')
            if 'extra' not in kwargs:
                kwargs['extra'] = {}
            
            if 'data' not in kwargs['extra']:
                kwargs['extra']['data'] = {}
                
            kwargs['extra']['data'].update(context)
        return msg, kwargs

def setup_logging(log_level=logging.INFO, log_name=None, logs_dir=None, json_format=False, rotate=True, max_bytes=10*1024*1024, backup_count=5, console_output=True):
    """
    配置增强的日志系统
    
    Args:
        log_level: 日志级别，默认INFO
        log_name: 日志文件名前缀，默认为None（使用时间戳）
        logs_dir: 日志文件保存目录，默认为None（使用项目根目录下的logs目录）
        json_format: 是否使用JSON格式记录日志
        rotate: 是否启用日志文件轮转
        max_bytes: 单个日志文件最大字节数
        backup_count: 保存的日志文件备份数量
        console_output: 是否输出到控制台，默认为True
    
    Returns:
        log_file: 日志文件完整路径
    """
    # 获取项目根目录
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    # 创建logs目录（如果不存在）
    if logs_dir is None:
        logs_dir = os.path.join(project_root, 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    
    # 生成日志文件名（使用时间戳）
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if log_name:
        log_file = os.path.join(logs_dir, f"{log_name}_{timestamp}.log")
    else:
        log_file = os.path.join(logs_dir, f"log_{timestamp}.log")
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # 如果已有处理器，先清除
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 选择格式化器
    if json_format:
        formatter = JsonFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(module)s:%(funcName)s:%(lineno)d] - %(message)s'
        )
    
    # 创建文件处理器
    if rotate:
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, 
            maxBytes=max_bytes, 
            backupCount=backup_count,
            encoding='utf-8'
        )
    else:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
    
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    
    # 创建控制台处理器
    if console_output:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # 添加处理器到根日志记录器
    root_logger.addHandler(file_handler)
    if not console_output:
        # 如果不输出到控制台，只添加文件处理器
        logger = logging.getLogger(__name__)
        logger.info(f"日志系统已配置为仅文件输出模式，日志文件: {log_file}")
    else:
        # 添加控制台处理器到根日志记录器
        logger = logging.getLogger(__name__)
        logger.info(f"增强的日志系统已初始化，日志文件: {log_file}")
    
    # 捕获未处理的异常
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            # 正常退出，不记录堆栈跟踪
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        # 记录未捕获的异常
        root_logger.error("未捕获的异常", exc_info=(exc_type, exc_value, exc_traceback))
    
    sys.excepthook = handle_exception
    
    # 输出日志系统初始化信息
    logger = logging.getLogger(__name__)
    logger.info(f"增强的日志系统已初始化，日志文件: {log_file}")
    
    # 创建用于记录性能的定时处理器
    if log_level <= logging.DEBUG:
        # 创建性能日志文件
        perf_log_file = os.path.join(logs_dir, f"performance_{timestamp}.log")
        perf_handler = logging.FileHandler(perf_log_file, encoding='utf-8')
        perf_handler.setLevel(logging.DEBUG)
        perf_handler.setFormatter(formatter)
        
        # 创建性能记录器
        perf_logger = logging.getLogger('performance')
        perf_logger.setLevel(logging.DEBUG)
        perf_logger.addHandler(perf_handler)
        logger.info(f"性能日志文件: {perf_log_file}")
    
    return log_file

def get_logger(name, with_context=False):
    """
    获取日志记录器
    
    Args:
        name: 日志记录器名称
        with_context: 是否启用上下文适配器
    
    Returns:
        logger: 日志记录器
    """
    logger = logging.getLogger(name)
    if with_context:
        return ContextAdapter(logger, {})
    return logger

def log_performance_snapshot():
    """记录当前的性能统计快照"""
    perf_logger = logging.getLogger('performance')
    stats = get_performance_stats()
    
    if stats:
        perf_logger.info(f"性能统计快照: {json.dumps(stats, ensure_ascii=False)}") 