"""
自动水质建模器主模块，提供一键式建模功能
"""

import json
import logging
import os
from datetime import datetime

import pandas as pd

from ..models.builder import ModelBuilder
from ..preprocessing.spectrum_processor import SpectrumProcessor

# 导入项目组件
from .config_manager import ConfigManager
from .data_structures import ModelingResult, ProcessingConfig
from .exceptions import (
    DataValidationError,
    InsufficientDataError,
    InvalidParameterError,
    ModelingError,
)
from .feature_manager import FeatureManager
from .modeling_strategies import AutoModelingStrategy, TuningStrategy
from .validators import validate_dataframe, validate_inputs

# 获取模块日志记录器
logger = logging.getLogger(__name__)


class AutoWaterQualityModeler:
    """自动水质建模器，支持一键式建模流程"""

    def __init__(
        self,
        config_path: str | None = None,
        min_wavelength: int = 400,
        max_wavelength: int = 900,
        smooth_window: int = 11,
        smooth_order: int = 3,
    ):
        """
        初始化自动水质建模器

        Args:
            config_path: 特征配置文件路径
            min_wavelength: 最小波长
            max_wavelength: 最大波长
            smooth_window: 平滑窗口大小
            smooth_order: 平滑多项式阶数
        """
        # 创建处理配置
        self.config = ProcessingConfig(
            min_wavelength=min_wavelength,
            max_wavelength=max_wavelength,
            smooth_window=smooth_window,
            smooth_order=smooth_order,
        )

        # 创建组件
        self.config_manager = ConfigManager(config_path)
        self.feature_manager = FeatureManager(self.config_manager)
        self.processor = SpectrumProcessor(
            min_wavelength=min_wavelength,
            max_wavelength=max_wavelength,
            smooth_window=smooth_window,
            smooth_order=smooth_order,
        )
        self.model_builder = ModelBuilder()

        # 创建建模策略
        self.auto_strategy = AutoModelingStrategy(
            self.feature_manager, self.model_builder
        )
        self.tuning_strategy = TuningStrategy(self.model_builder)

    @validate_inputs(
        lambda self, spectrum_data, metric_data, *args, **kwargs: validate_dataframe(
            spectrum_data, "光谱数据", min_rows=1, numeric_only=True
        ),
        lambda self, spectrum_data, metric_data, *args, **kwargs: validate_dataframe(
            metric_data, "实测数据", min_rows=1, numeric_only=True
        ),
    )
    def fit(
        self,
        spectrum_data: pd.DataFrame,
        metric_data: pd.DataFrame,
        data_type: str = "aerospot",
        matched_idx: list[int] | None = None,
        origin_merged_data: pd.DataFrame | None = None,
    ) -> ModelingResult:
        """
        一键式建模流程

        Args:
            spectrum_data: 光谱数据DataFrame（列名为波段，每行是一条光谱样本）
            metric_data: 实测值DataFrame（每列是一个水质指标）
            data_type: 数据类型，必须是支持的数据类型之一
            matched_idx: 匹配的索引，如果为None则使用全部数据
            origin_merged_data: 原始合并数据，用于模型微调

        Returns:
            ModelingResult: 统一的建模结果对象
        """
        try:
            # 更新配置
            self.config.data_type = data_type

            # 验证数据类型
            supported_types = self.config_manager.DATA_TYPES
            if data_type not in supported_types:
                raise InvalidParameterError(
                    "data_type", data_type, f"必须是 {supported_types} 之一"
                )

            logger.info(f"开始建模，数据类型: {data_type}")

            # 获取模型参数
            model_params = self.config_manager.get_model_params(data_type)
            self.config.min_samples = model_params.get("min_samples", 6)
            self.config.max_features = model_params.get("max_features", 5)

            # 预处理光谱数据
            try:
                processed_spectrum = self.processor.preprocess(spectrum_data)
            except Exception as e:
                raise DataValidationError(f"光谱数据预处理失败: {e}")

            # 准备实测数据
            filter_metric_data = self._prepare_metric_data(metric_data)

            # 验证过滤后的数据
            if filter_metric_data.empty:
                raise DataValidationError("过滤后的实测数据为空")

            # 准备合并数据
            try:
                merged_data = self._prepare_merged_data(
                    origin_merged_data, filter_metric_data, matched_idx
                )
            except ValueError as e:
                raise DataValidationError(str(e))

            # 选择建模策略
            if self._should_use_auto_modeling(filter_metric_data):
                logger.info(f"样本量：{len(filter_metric_data)}，采用自动建模")

                # 当使用匹配索引时，不需要验证整体数据一致性
                # 因为auto_strategy.build会在内部处理匹配索引
                if matched_idx is None:
                    # 只在没有匹配索引时验证数据一致性
                    validation = self.auto_strategy.validate_inputs(
                        processed_spectrum, filter_metric_data
                    )
                    if not validation.is_valid:
                        raise DataValidationError(
                            f"自动建模输入验证失败: {'; '.join(validation.errors)}"
                        )

                result = self.auto_strategy.build(
                    processed_spectrum,
                    filter_metric_data,
                    self.config,
                    matched_idx=matched_idx,
                )
            else:
                logger.info(f"样本量：{len(filter_metric_data)}，采用模型微调")

                if merged_data is None:
                    raise InsufficientDataError(
                        required=self.config.min_samples, actual=len(filter_metric_data)
                    )

                # 准备所有样本的合并数据
                all_merged_data = None
                if matched_idx is not None and origin_merged_data is not None:
                    all_merged_data = origin_merged_data.drop(
                        ["index", "latitude", "longitude"], axis=1, errors="ignore"
                    )

                # 验证策略输入
                validation = self.tuning_strategy.validate_inputs(
                    merged_data, filter_metric_data
                )
                if not validation.is_valid:
                    raise DataValidationError(
                        f"模型微调输入验证失败: {'; '.join(validation.errors)}"
                    )

                result = self.tuning_strategy.build(
                    merged_data,
                    filter_metric_data,
                    self.config,
                    all_merged_data=all_merged_data,
                )

            # 格式化模型结果
            try:
                result.models = self._format_result(
                    result.models,
                    result.model_type,
                    filter_metric_data,
                )
            except Exception as e:
                logger.error(f"格式化结果失败: {e}")
                # 继续返回未格式化的结果

            return result

        except (DataValidationError, InvalidParameterError, InsufficientDataError) as e:
            # 这些是预期的错误，记录并抛出
            logger.error(f"建模失败: {e}")
            raise

        except Exception as e:
            # 未预期的错误，包装为ModelingError
            logger.error(f"建模过程发生未预期错误: {e}", exc_info=True)
            raise ModelingError(f"建模失败: {e}")

    def _prepare_metric_data(self, metric_data: pd.DataFrame) -> pd.DataFrame:
        """准备实测数据，过滤不需要的列"""
        return metric_data.drop(
            ["index", "latitude", "longitude"], axis=1, errors="ignore"
        )

    def _prepare_merged_data(
        self,
        origin_merged_data: pd.DataFrame | None,
        filter_metric_data: pd.DataFrame,
        matched_idx: list[int] | None,
    ) -> pd.DataFrame | None:
        """准备合并数据"""
        if origin_merged_data is None:
            return None

        if matched_idx is not None:
            filter_merged_data = origin_merged_data.drop(
                ["index", "latitude", "longitude"], axis=1, errors="ignore"
            )
            merged_data = filter_merged_data.iloc[matched_idx]
            merged_data.index = filter_metric_data.index
            return merged_data
        else:
            # 判断样本量是否一致
            if len(origin_merged_data) != len(filter_metric_data):
                raise ValueError("origin_merged_data和metric_data的样本量不一致")
            return origin_merged_data

    def _should_use_auto_modeling(self, metric_data: pd.DataFrame) -> bool:
        """判断是否应该使用自动建模策略"""
        return len(metric_data) >= self.config.min_samples

    def _format_result(
        self, result: dict, model_type: int, merged_data: pd.DataFrame
    ) -> dict:
        """格式化模型结果为标准输出格式"""
        if model_type not in [0, 1]:
            raise ValueError("model_type 必须是 0 或 1")

        # 从配置文件获取参数
        index = self.config_manager.get_water_quality_params()
        columns = self.config_manager.get_feature_stations()

        # 如果配置文件中没有，使用默认值
        if not index:
            index = [
                "turbidity",
                "ss",
                "sd",
                "do",
                "codmn",
                "codcr",
                "chla",
                "tn",
                "tp",
                "chroma",
                "nh3n",
            ]
        if not columns:
            columns = [f"STZ{i}" for i in range(1, 26)]

        # 创建水质参数系数矩阵
        w_coefficients = pd.DataFrame(0.0, index=index, columns=columns, dtype=float)
        a_coefficients = pd.DataFrame(0.0, index=index, columns=columns, dtype=float)
        b_coefficients = pd.DataFrame(0.0, index=index, columns=columns, dtype=float)
        A_coefficients = pd.DataFrame(1.0, index=index, columns=["A"], dtype=float)

        Range_coefficients = pd.DataFrame(
            0.0, index=index, columns=["m", "n"], dtype=float
        )

        # 解析result并填充系数矩阵
        if result:
            if model_type == 1:
                try:
                    logger.info("开始解析建模结果并填充系数矩阵")

                    # 遍历result中的每个水质参数
                    for param_key, param_data in result.items():
                        # 检查参数是否在系数矩阵的索引中
                        if param_key in w_coefficients.index:
                            # 遍历每个测站的数据
                            for station_key, station_data in param_data.items():
                                # 检查测站是否在系数矩阵的列中
                                if station_key in w_coefficients.columns:
                                    # 根据三级key将系数填入对应的矩阵

                                    if "w" in station_data:
                                        w_coefficients.loc[param_key, station_key] = (
                                            station_data["w"]
                                        )
                                    if "a" in station_data:
                                        a_coefficients.loc[param_key, station_key] = (
                                            station_data["a"]
                                        )
                                    if "b" in station_data:
                                        b_coefficients.loc[param_key, station_key] = (
                                            station_data["b"]
                                        )

                    logger.info("系数矩阵填充完成")
                except Exception as e:
                    logger.error(f"填充系数矩阵时出错: {str(e)}")
            elif model_type == 0:
                try:
                    logger.info("开始解析模型微调结果并只填充A系数矩阵")

                    for param_key, param_data in result.items():
                        if param_key in A_coefficients.index:
                            A_coefficients.loc[param_key, "A"] = param_data
                except Exception as e:
                    logger.error(f"填充系数矩阵时出错: {str(e)}")

        # 将系数矩阵转换为列表
        format_result = dict()
        # 将系数矩阵展开成一维列表
        format_result["type"] = model_type
        if model_type == 1:
            format_result["w"] = w_coefficients.values.T.flatten().tolist()
            format_result["a"] = a_coefficients.values.T.flatten().tolist()
            format_result["b"] = b_coefficients.values.flatten().tolist()
        format_result["A"] = A_coefficients.values.flatten().tolist()

        # 获取各指标上下限，并填充到Range_coefficients中
        for index in Range_coefficients.index:
            if index in merged_data.columns:
                min_value = merged_data[index].min()
                max_value = merged_data[index].max()
                if min_value == max_value:
                    logger.warning(
                        f"指标：{index} 上下限相同，无法计算范围系数，可能是样本量太少：{len(merged_data)}"
                    )
                # 指标范围下限
                Range_down = max(0, min_value - merged_data[index].std() * 3)
                Range_coefficients.loc[index, "m"] = Range_down

                # 指标范围上限
                Range_up = max_value + merged_data[index].std() * 3
                Range_coefficients.loc[index, "n"] = Range_up

                logger.info(
                    f"{index}的Range为实测值最小值-3倍标准差，最大值+3倍标准差：{Range_down} - {Range_up}"
                )

        format_result["Range"] = Range_coefficients.values.flatten().tolist()

        return format_result

    def save_model(self, models: dict, output_path: str | None = None) -> str:
        """
        保存模型到文件

        Args:
            models: 模型字典
            output_path: 输出路径，如果为None则自动生成

        Returns:
            str: 保存的文件路径
        """
        if output_path is None:
            # 生成默认路径
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = os.path.join(
                os.path.dirname(__file__), "..", "output", "models"
            )
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f"model_{timestamp}.json")

        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # 保存模型
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(models, f, ensure_ascii=False, indent=2)

        logger.info(f"模型已保存到: {output_path}")
        return output_path
