"""
特征计算模块，提供光谱特征公式解析和计算功能
"""

import pandas as pd
import numpy as np
import ast
import logging
from typing import Callable

# 获取模块日志记录器
logger = logging.getLogger(__name__)

class FeatureCalculator:
    """特征计算器，支持公式解析和计算"""
    
    def __init__(self, tris_coeff: pd.DataFrame | None = None):
        """
        初始化特征计算器
        
        Args:
            tris_coeff: 三刺激值系数表，用于颜色特征计算
        """
        self.logger = logger
        self.tris_coeff = tris_coeff  # 三刺激值系数表
        
        # 注册支持的函数
        self.functions = self._register_functions()
    
    def _register_functions(self) -> dict[str, Callable]:
        """
        注册支持的函数
        
        Returns:
            Dict[str, Callable]: 函数名到函数的映射
        """
        return {
            'sum': self._sum,
            'mean': self._mean,
            'abs': self._abs,
            'ref': self._ref,  # 获取单个波段的反射率
            'tris': self._tris,  # 计算三刺激值
            'diff': self._diff,  # 计算波长间差异
            'ratio': self._ratio,  # 计算波长间比率
            'norm': self._norm,  # 归一化值
            'log': self._log,  # 对数变换
        }
    
    def calculate_feature(self, spectrum_data: pd.DataFrame, feature_definition: dict) -> pd.Series:
        """
        根据特征定义计算单个特征
        
        Args:
            spectrum_data: 光谱数据DataFrame
            feature_definition: 特征定义字典，包含name和formula字段
            
        Returns:
            pd.Series: 计算的特征值
        """
        formula = feature_definition.get('formula')
        name = feature_definition.get('name')
        band_map = feature_definition.get('bands', {})
        
        if not name or not formula:
            return pd.Series()
        
        try:
            expr = formula
            for band, wavelength in band_map.items():
                expr = expr.replace(band, str(wavelength))
            result = self.evaluate(expr, spectrum_data)
            result.name = name
            return result
        except Exception as e:
            self.logger.error(f"计算特征 {name} 失败: {e}", exc_info=True)
            return pd.Series()
            

    
    def calculate_features(self, spectrum_data: pd.DataFrame, feature_definitions: list[dict]) -> pd.DataFrame:
        """
        根据多个特征定义计算特征
        
        Args:
            spectrum_data: 光谱数据DataFrame
            feature_definitions: 特征定义列表
            
        Returns:
            pd.DataFrame: 计算的特征数据
        """
        features = pd.DataFrame(index=spectrum_data.index)
        
        for feature_def in feature_definitions:
            feature = self.calculate_feature(spectrum_data, feature_def)
            if not feature.empty:
                features[feature.name] = feature
        
        return features
    
    def evaluate(self, expression: str, data: pd.DataFrame) -> pd.Series:
        """
        解析并计算表达式
        
        Args:
            expression: 特征公式
            data: 光谱数据
            
        Returns:
            pd.Series: 计算结果
        """
        try:
            # 保存数据引用
            self.data = data
            self.columns = set(data.columns.astype(float))
            
            # 解析表达式
            result = self._eval(ast.parse(expression, mode='eval').body)
            
            # 确保返回Series
            if isinstance(result, pd.Series):
                return result
            else:
                # 如果是标量，返回带有数据索引的Series
                return pd.Series(result, index=data.index)
        except Exception as e:
            self.logger.error(f"表达式 '{expression}' 计算失败: {e}", exc_info=True)
            raise ValueError(f"表达式 '{expression}' 计算失败: {e}")
    
    def _eval(self, node):
        """
        递归解析表达式
        
        Args:
            node: AST节点
            
        Returns:
            pd.Series或标量: 解析结果
        """
        if isinstance(node, ast.BinOp):  # 处理二元运算 + - * /
            left = self._eval(node.left)
            right = self._eval(node.right)
            
            if isinstance(node.op, ast.Add):
                return left + right
            elif isinstance(node.op, ast.Sub):
                return left - right
            elif isinstance(node.op, ast.Mult):
                return left * right
            elif isinstance(node.op, ast.Div):
                # 防止除零错误
                if isinstance(right, pd.Series):
                    zero_mask = right == 0
                    if zero_mask.any():
                        self.logger.warning("除法运算中检测到除数为零，将替换为NaN")
                        right = right.copy()
                        right[zero_mask] = np.nan
                return left / right
            elif isinstance(node.op, ast.Pow):
                return left ** right
            else:
                self.logger.error(f"不支持的运算符: {type(node.op).__name__}")
                raise ValueError(f"不支持的运算符: {type(node.op).__name__}")
                
        elif isinstance(node, ast.Call):  # 处理函数调用
            if not isinstance(node.func, ast.Name):
                self.logger.error("不支持的函数调用格式")
                raise ValueError("不支持的函数调用格式")
            func_name = node.func.id.lower()
            if func_name not in self.functions:
                self.logger.error(f"不支持的函数: {func_name}")
                raise ValueError(f"不支持的函数: {func_name}")
                
            # 处理tris函数，它需要一个特殊的字符参数
            if func_name == 'tris':
                if len(node.args) != 1 or not isinstance(node.args[0], ast.Name):
                    self.logger.error("tris() 需要一个参数 'x', 'y' 或 'z'")
                    raise ValueError("tris() 需要一个参数 'x', 'y' 或 'z'")
                arg = node.args[0].id  # 获取参数名
                return self.functions[func_name](arg)
                
            # 处理其他函数
            args = [self._eval(arg) for arg in node.args]
            return self.functions[func_name](*args)
            
        elif isinstance(node, ast.Constant):  # Python 3.8+
            return node.value
            
        elif isinstance(node, ast.Name):  # 处理变量名
            var_name = node.id
            try:
                # 尝试将变量名转为波长值
                band = float(var_name)
                if band in self.columns:
                    return self.data[band]
                else:
                    nearest_band = min(self.columns, key=lambda x: abs(x - band))
                    self.logger.warning(f"波长 {band} 不存在，使用最接近的波长 {nearest_band}")
                    return self.data[nearest_band]
            except ValueError:
                # 如果不是数字，可能是 x, y, z
                if var_name in ['x', 'y', 'z']:
                    return var_name
                else:
                    self.logger.error(f"无效的变量名: {var_name}")
                    raise ValueError(f"无效的变量名: {var_name}")
                    
        elif isinstance(node, ast.UnaryOp):  # 处理一元运算符
            operand = self._eval(node.operand)
            
            if isinstance(node.op, ast.USub):  # 负号
                return -operand
            elif isinstance(node.op, ast.UAdd):  # 正号
                return operand
            else:
                self.logger.error(f"不支持的一元运算符: {type(node.op).__name__}")
                raise ValueError(f"不支持的一元运算符: {type(node.op).__name__}")
                
        else:
            self.logger.error(f"不支持的表达式类型: {type(node).__name__}")
            raise ValueError(f"不支持的表达式类型: {type(node).__name__}")
    
    # 以下是支持的函数实现
    
    def _sum(self, start_band, end_band):
        """计算波段范围内的和"""
        start_band = float(start_band)
        end_band = float(end_band)
        
        if start_band not in self.columns and end_band not in self.columns:
            self.logger.error(f"波段范围 {start_band}-{end_band} 无效")
            raise ValueError(f"波段范围 {start_band}-{end_band} 无效")
            
        cols = [col for col in self.data.columns if start_band <= float(col) <= end_band]
        if not cols:
            self.logger.error(f"波段范围 {start_band}-{end_band} 内没有数据")
            raise ValueError(f"波段范围 {start_band}-{end_band} 内没有数据")
            
        return self.data[cols].sum(axis=1)

    def _mean(self, start_band, end_band):
        """计算波段范围内的均值"""
        start_band = float(start_band)
        end_band = float(end_band)
        
        if start_band not in self.columns and end_band not in self.columns:
            self.logger.error(f"波段范围 {start_band}-{end_band} 无效")
            raise ValueError(f"波段范围 {start_band}-{end_band} 无效")
            
        cols = [col for col in self.data.columns if start_band <= float(col) <= end_band]
        if not cols:
            self.logger.error(f"波段范围 {start_band}-{end_band} 内没有数据")
            raise ValueError(f"波段范围 {start_band}-{end_band} 内没有数据")
            
        return self.data[cols].mean(axis=1)

    def _abs(self, value):
        """计算绝对值"""
        return abs(value)

    def _ref(self, band):
        """获取指定波段的反射率"""
        band = float(band)
        
        if band in self.columns:
            return self.data[band]
        else:
            # 找最接近的波段
            nearest_band = min(self.columns, key=lambda x: abs(x - band))
            self.logger.warning(f"波长 {band} 不存在，使用最接近的波长 {nearest_band}")
            return self.data[nearest_band]

    def _tris(self, channel):
        """计算三刺激值"""
        if channel not in ["x", "y", "z"]:
            self.logger.error(f"tris() 参数必须是 'x', 'y' 或 'z'，收到: {channel}")
            raise ValueError("tris() 参数必须是 'x', 'y' 或 'z'")
            
        if self.tris_coeff is None or self.tris_coeff.empty:
            self.logger.error("未加载三刺激值系数表")
            raise ValueError("未加载三刺激值系数表")
            
        index = {"x": 0, "y": 1, "z": 2}[channel]  # 选择对应的系数行
        coef = self.tris_coeff.iloc[index]  # 取出三刺激值系数
        
        # 选取需要的波段范围
        valid_bands = [col for col in self.data.columns 
                      if col in coef.index or float(col) in coef.index]
        if not valid_bands:
            self.logger.error("当前光谱数据与三刺激值系数表波段不匹配")
            raise ValueError("当前光谱数据与三刺激值系数表波段不匹配")
            
        # 计算三刺激值
        result = pd.Series(0.0, index=self.data.index)
        for band in valid_bands:
            if band in coef.index:
                coef_value = coef[band]
            else:
                coef_value = coef[float(band)]
            result += self.data[band] * coef_value
            
        return result
    
    def _diff(self, band1, band2):
        """计算两个波段的差值"""
        band1 = float(band1)
        band2 = float(band2)
        
        band1_ref = self._ref(band1)
        band2_ref = self._ref(band2)
        
        return band1_ref - band2_ref
    
    def _ratio(self, band1, band2):
        """计算两个波段的比值"""
        band1 = float(band1)
        band2 = float(band2)
        
        band1_ref = self._ref(band1)
        band2_ref = self._ref(band2)
        
        # 防止除零
        zero_mask = band2_ref == 0
        if zero_mask.any():
            self.logger.warning(f"ratio({band1}, {band2}) 中存在除数为零的情况")
            band2_ref = band2_ref.copy()
            band2_ref[zero_mask] = np.nan
        
        return band1_ref / band2_ref
    
    def _norm(self, value, min_val, max_val):
        """归一化值到指定范围"""
        try:
            min_val = float(min_val)
            max_val = float(max_val)
            
            if isinstance(value, pd.Series):
                # 线性归一化
                range_val = max_val - min_val
                if range_val == 0:
                    self.logger.warning(f"归一化范围为零: {min_val}-{max_val}")
                    return pd.Series(min_val, index=value.index)
                
                value_min = value.min()
                value_max = value.max()
                value_range = value_max - value_min
                
                if value_range == 0:
                    self.logger.warning("输入数据范围为零，无法归一化")
                    return pd.Series(min_val, index=value.index)
                
                normalized = (value - value_min) / value_range * range_val + min_val
                return normalized
            else:
                # 标量值，直接返回
                return value
                
        except Exception as e:
            self.logger.error(f"归一化失败: {e}")
            if isinstance(value, pd.Series):
                return pd.Series(np.nan, index=value.index)
            return np.nan
    
    def _log(self, value, base=10):
        """对数变换"""
        try:
            base = float(base)
            
            if base <= 0:
                self.logger.error(f"对数的底数必须大于0: {base}")
                if isinstance(value, pd.Series):
                    return pd.Series(np.nan, index=value.index)
                return np.nan
            
            if isinstance(value, pd.Series):
                # 检查负值和零值
                invalid_mask = value <= 0
                if invalid_mask.any():
                    self.logger.warning(f"对数变换中检测到{invalid_mask.sum()}个非正值，将替换为NaN")
                    value = value.copy()
                    value[invalid_mask] = np.nan
                
                return np.log(value) / np.log(base)
            else:
                # 标量值
                if value <= 0:
                    self.logger.warning(f"对数变换的输入值必须大于0: {value}")
                    return np.nan
                return np.log(value) / np.log(base)
                
        except Exception as e:
            self.logger.error(f"对数变换失败: {e}")
            if isinstance(value, pd.Series):
                return pd.Series(np.nan, index=value.index)
            return np.nan 