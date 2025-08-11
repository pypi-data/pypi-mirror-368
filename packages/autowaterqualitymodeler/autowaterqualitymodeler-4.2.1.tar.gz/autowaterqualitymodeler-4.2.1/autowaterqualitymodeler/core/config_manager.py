"""
配置管理模块，提供特征配置文件的加载和访问功能
"""

import json
import os
import logging
from typing import Any
from .exceptions import ConfigurationError, FileOperationError

# 获取模块日志记录器
logger = logging.getLogger(__name__)

class ConfigManager:
    """配置管理器，处理特征配置文件加载和访问"""
    
    # 默认支持的数据类型
    DATA_TYPES = ["warning_device", "shore_data", "smart_water", "aerospot"]
    
    def __init__(self, config_path: str | None = None, system_config_path: str | None = None):
        """
        初始化配置管理器
        
        Args:
            config_path: 特征配置文件路径，如果为None，则使用默认路径
            system_config_path: 系统配置文件路径，如果为None，则使用默认路径
        """
        # 加载特征配置
        if config_path is None:
            # 使用默认配置文件路径
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                'config', 
                'features_config.json'
            )
            logger.info(f"使用默认配置文件: {config_path} (存在: {os.path.exists(config_path)})")
            
        self.config_path = config_path
        self.config = self._load_config(config_path)
        
        # 加载系统配置
        if system_config_path is None:
            system_config_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                'config', 
                'system_config.json'
            )
            
        self.system_config = self._load_system_config(system_config_path)
    
    def _load_config(self, config_path: str) -> dict:
        """
        加载特征配置文件
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            Dict: 加载的配置对象
            
        Raises:
            FileOperationError: 文件读取失败时
            ConfigurationError: 配置文件格式错误时
        """
        if not os.path.exists(config_path):
            raise FileOperationError(
                f"配置文件不存在: {config_path}", 
                {"file_path": config_path}
            )
            
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            raise ConfigurationError(
                f"配置文件JSON格式错误: {config_path}",
                {"file_path": config_path, "error": str(e)}
            )
        except IOError as e:
            raise FileOperationError(
                f"读取配置文件失败: {config_path}",
                {"file_path": config_path, "error": str(e)}
            )
        
        # 验证配置文件格式
        if not isinstance(config, dict):
            raise ConfigurationError(
                "配置文件根元素必须是字典类型",
                {"file_path": config_path, "actual_type": type(config).__name__}
            )
            
        # 检查必需的数据类型
        missing_types = [dt for dt in self.DATA_TYPES if dt not in config]
        if missing_types:
            logger.warning(f"配置文件中缺少以下数据类型: {missing_types}")
            # 为缺失类型创建空配置
            for dt in missing_types:
                config[dt] = {}
                
        logger.info(f"成功加载配置文件: {config_path}")
        return config
    
    def _load_system_config(self, config_path: str) -> dict:
        """
        加载系统配置文件
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            Dict: 加载的系统配置对象
            
        Raises:
            FileOperationError: 文件读取失败时
            ConfigurationError: 配置文件格式错误时
        """
        # 系统配置文件是可选的，如果不存在则使用默认配置
        if not os.path.exists(config_path):
            logger.info(f"系统配置文件不存在: {config_path}，使用默认配置")
            return self._get_default_system_config()
            
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                system_config = json.load(f)
        except json.JSONDecodeError:
            logger.warning(f"系统配置文件JSON格式错误: {config_path}，使用默认配置")
            return self._get_default_system_config()
        except IOError:
            logger.warning(f"读取系统配置文件失败: {config_path}，使用默认配置")
            return self._get_default_system_config()
            
        if not isinstance(system_config, dict):
            logger.warning("系统配置文件根元素必须是字典类型，使用默认配置")
            return self._get_default_system_config()
            
        logger.info(f"成功加载系统配置文件: {config_path}")
        return system_config
    
    def _get_default_system_config(self) -> dict:
        """获取默认系统配置"""
        return {
            "system": {
                "encryption": {
                    "password": "water_quality_analysis_key",
                    "salt": "water_quality_salt",
                    "enabled": False
                },
                "cache": {
                    "enabled": True,
                    "ttl": 3600,
                    "max_size": 1000
                },
                "parallel": {
                    "enabled": True,
                    "max_workers": 4
                }
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            },
            "water_quality_params": [
                "turbidity", "ss", "sd", "do", "codmn", 
                "codcr", "chla", "tn", "tp", "chroma", "nh3n"
            ],
            "feature_stations": [f"STZ{i}" for i in range(1, 20)]
        }
    
    def get_system_config(self, *keys) -> Any:
        """
        获取系统配置值
        
        Args:
            *keys: 配置键的路径，例如 ('system', 'encryption', 'password')
            
        Returns:
            Any: 配置值，如果键不存在则返回None
        """
        config = self.system_config
        for key in keys:
            if isinstance(config, dict) and key in config:
                config = config[key]
            else:
                return None
        return config
    
    def get_water_quality_params(self) -> list[str]:
        """
        获取水质参数列表
        
        Returns:
            List[str]: 水质参数名称列表
        """
        params = self.get_system_config("water_quality_params")
        return params if isinstance(params, list) else []
    
    def get_feature_stations(self) -> list[str]:
        """
        获取特征站点列表
        
        Returns:
            List[str]: 特征站点名称列表
        """
        stations = self.get_system_config("feature_stations")
        return stations if isinstance(stations, list) else []
    
    def get_feature_definitions(self, data_type: str, metric_name: str) -> list[dict]:
        """
        获取指定数据类型和指标的特征定义
        
        Args:
            data_type: 数据类型，必须是DATA_TYPES中的一种
            metric_name: 指标名称
            
        Returns:
            List[Dict]: 特征定义列表
            
        Raises:
            ConfigurationError: 数据类型无效时
        """
        if data_type not in self.DATA_TYPES:
            logger.warning(f"不支持的数据类型: {data_type}")
            return []
            
        # 尝试获取数据类型下的指标特征
        if data_type in self.config and metric_name in self.config[data_type]:
            features = self.config[data_type][metric_name].get("features", [])
            logger.debug(f"找到 {data_type} 下 {metric_name} 指标的 {len(features)} 个特征定义")
        elif data_type in self.config and "default" in self.config[data_type]:
            features = self.config[data_type]["default"].get("features", [])
            logger.debug(f"{data_type} 下 {metric_name} 指标采用默认的 {len(features)} 个特征")
        else:
            logger.warning(f"未找到 {data_type} 下 {metric_name} 指标的特征定义")
            return []
        
        # 获取完整的特征定义
        full_definitions = []
        for ref in features:
            if "feature_id" not in ref:
                logger.warning(f"特征引用缺少feature_id: {ref}")
                continue
                
            feature_id = ref["feature_id"]
            
            # 获取基础特征定义
            if "features" in self.config and feature_id in self.config["features"]:
                base_definition = self.config["features"][feature_id].copy()
                
                # 如果有自定义波段映射，则合并
                if "bands" in ref:
                    base_definition["bands"] = ref["bands"]
                    
                full_definitions.append(base_definition)
            else:
                logger.warning(f"未找到特征ID为 {feature_id} 的定义")
        
        return full_definitions

    def get_model_params(self, data_type: str | None = None, metric_name: str | None = None) -> dict:
        """
        获取模型参数，根据优先级依次尝试：指标级别 > 数据类型级别 > 全局级别
        
        Args:
            data_type: 数据类型，如果为None则只返回全局参数
            metric_name: 指标名称，如果为None则返回数据类型级别的参数
            
        Returns:
            Dict: 合并后的模型参数
        """
        model_params = {}
        
        # 1. 获取全局模型参数（最低优先级）
        global_params = self.config.get("model_params", {})
        model_params.update(global_params)
        
        # 2. 获取数据类型级别的模型参数（中等优先级）
        if data_type and data_type in self.config:
            data_type_params = self.config[data_type].get("model_params", {})
            if data_type_params:
                model_params.update(data_type_params)
        
        # 3. 获取指标级别的模型参数（最高优先级）
        if data_type and metric_name and data_type in self.config and metric_name in self.config[data_type]:
            metric_params = self.config[data_type][metric_name].get("model_params", {})
            if metric_params:
                model_params.update(metric_params)
        
        return model_params
    
    def get_supported_metrics(self, data_type: str) -> list[str]:
        """
        获取指定数据类型支持的指标列表
        
        Args:
            data_type: 数据类型
            
        Returns:
            List[str]: 支持的指标列表
        """
        if data_type not in self.DATA_TYPES:
            logger.warning(f"不支持的数据类型: {data_type}")
            return []
            
        if data_type in self.config:
            # 过滤掉model_params键，它不是指标
            metrics = [key for key in self.config[data_type].keys() if key != "model_params"]
            return metrics
        
        return [] 