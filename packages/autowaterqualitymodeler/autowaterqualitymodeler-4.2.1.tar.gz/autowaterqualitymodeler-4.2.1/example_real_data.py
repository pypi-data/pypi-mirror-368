"""
AutoWaterQualityModeler 实际建模用例
使用真实数据测试包的功能
"""

from pandas.core.frame import DataFrame

from typing import LiteralString

import pandas as pd
import os
from autowaterqualitymodeler.core.modeler import AutoWaterQualityModeler

def run_real_data_example():
    """使用真实数据运行建模示例"""
    
    print("========== AutoWaterQualityModeler 实际建模示例 ==========\n")
    
    # 设置数据路径
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    ref_data_path: LiteralString = os.path.join(data_dir, "ref_data.csv")
    measure_data_path: LiteralString = os.path.join(data_dir, "measure_data.csv")
    merged_data_path: LiteralString = os.path.join(data_dir, "merged_data.csv")
    
    # 加载数据
    print("1. 加载数据...")
    
    # 加载光谱数据 (ref_data.csv)
    # 第一列是样本编号，后续列是不同波长的反射率值
    spectrum_data: DataFrame = pd.read_csv(ref_data_path, index_col=0)
    print(f"   - 光谱数据形状: {spectrum_data.shape}")
    print(f"   - 波长范围: {spectrum_data.columns[0]} - {spectrum_data.columns[-1]} nm")
    print(f"   - 样本数量: {len(spectrum_data)}")
    
    # 加载实测水质数据 (measure_data.csv)
    # 包含经纬度和各种水质参数
    measure_data: DataFrame = pd.read_csv(measure_data_path, index_col=0)
    # 只保留水质参数列（去除经纬度）
    water_quality_cols: list[str] = ['chla', 'turbidity', 'ss', 'codcr', 'tp', 'nh3n', 'bga']
    metric_data: DataFrame = measure_data[water_quality_cols]
    print(f"\n   - 水质数据形状: {metric_data.shape}")
    print(f"   - 水质指标: {', '.join(metric_data.columns)}")
    print(f"   - 样本数量: {len(metric_data)}")
    
    # 加载合并数据 (merged_data.csv) - 用于模型微调
    merged_data = pd.read_csv(merged_data_path, index_col=0)
    # 只保留水质参数列
    origin_merged_data = merged_data[water_quality_cols]
    print(f"\n   - 合并数据形状: {origin_merged_data.shape}")
    
    # 创建输出目录
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    print("\n2. 创建建模器...")
    modeler = AutoWaterQualityModeler()
    
    # 场景1: 完整数据建模（所有样本都有光谱和实测数据）
    print("\n3. 场景1 - 完整数据建模")
    print("   使用前6个样本进行建模（光谱数据和实测数据数量匹配）...")
    
    # 只使用前6个样本的光谱数据，与实测数据匹配
    spectrum_data_matched = spectrum_data.iloc[:6]
    
    try:
        result1 = modeler.fit(
            spectrum_data=spectrum_data_matched,
            metric_data=metric_data,
            data_type="aerospot"  # 使用航空高光谱数据类型
        )

        print(f"\n   建模成功!")
        print(f"   - 模型类型: {'自动建模' if result1.model_type == 1 else '模型微调'}")
        print(f"   - 成功建模的指标: {list(result1.models.keys())}")
        print(f"   - 预测结果形状: {result1.predictions.shape}")
        
        # 保存模型
        model_path1 = os.path.join(output_dir, "models_scenario1.json")
        saved_path1 = modeler.save_model(result1.models, model_path1)
        print(f"   - 模型已保存到: {saved_path1}")
        
            
    except Exception as e:
        print(f"   建模失败: {e}")
    
    # 场景2: 部分样本建模（只有部分样本有实测数据）
    print("\n\n4. 场景2 - 部分样本建模")
    print("   模拟只有前5个样本有实测数据的情况...")
    
    # 取前5个样本的实测数据
    partial_metric_data = metric_data.iloc[:5]
    # 匹配的索引
    matched_idx = list(range(5))
    
    try:
        result2 = modeler.fit(
            spectrum_data=spectrum_data,  # 所有样本的光谱数据
            metric_data=partial_metric_data,  # 只有5个样本的实测数据
            data_type="aerospot",
            matched_idx=matched_idx,  # 指定匹配的索引
            origin_merged_data=origin_merged_data  # 提供合并数据用于模型微调
        )
        
        print(f"\n   建模成功!")
        print(f"   - 模型类型: {'自动建模' if result2.model_type == 1 else '模型微调'}")
        print(f"   - 成功建模的指标: {list(result2.models.keys())}")
        print(f"   - 训练样本预测结果形状: {result2.predictions.shape}")
        if result2.has_all_predictions():
            print(f"   - 所有样本预测结果形状: {result2.all_predictions.shape}")
        
        # 保存模型
        model_path2 = os.path.join(output_dir, "models_scenario2.json")
        saved_path2 = modeler.save_model(result2.models, model_path2)
        print(f"   - 模型已保存到: {saved_path2}")
        
    except Exception as e:
        print(f"   建模失败: {e}")
    

    
    # 显示数据统计信息
    print("\n\n6. 数据统计信息")
    print("\n   水质参数统计:")
    print(metric_data.describe().round(2))
    
    # 计算光谱数据的平均反射率
    mean_spectrum = spectrum_data.mean(axis=0)
    print(f"\n   平均光谱反射率范围: {mean_spectrum.min():.4f} - {mean_spectrum.max():.4f}")
    
    print("\n\n========== 建模示例完成 ==========")

if __name__ == "__main__":
    # 确保在正确的目录下运行
    if not os.path.exists(os.path.join(os.path.dirname(__file__), "data")):
        print("错误: 请在包含 'data' 目录的位置运行此脚本")
        print("当前工作目录:", os.getcwd())
    else:
        run_real_data_example()