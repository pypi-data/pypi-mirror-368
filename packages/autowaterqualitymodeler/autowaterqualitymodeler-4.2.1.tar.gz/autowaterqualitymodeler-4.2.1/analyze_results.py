"""
分析AutoWaterQualityModeler建模结果
"""

import json
import pandas as pd
import os

def analyze_modeling_results():
    """分析建模结果"""
    
    print("========== 建模结果分析 ==========\n")
    
    # 分析场景1的结果
    model_path1 = "output/models_scenario1.json"
    if os.path.exists(model_path1):
        print("1. 场景1 - 完整数据建模结果分析")
        
        with open(model_path1, 'r') as f:
            models1 = json.load(f)
        
        print(f"   模型类型: {models1.get('type', 'N/A')}")
        
        # 分析具体的模型参数
        param_keys = ['w', 'a', 'b', 'A', 'Range']
        for key in param_keys:
            if key in models1:
                if isinstance(models1[key], list):
                    non_zero_count = sum(1 for x in models1[key] if x != 0)
                    print(f"   {key}: 列表长度={len(models1[key])}, 非零元素={non_zero_count}")
                elif isinstance(models1[key], dict):
                    print(f"   {key}: 包含 {len(models1[key])} 个指标的参数")
                    # 显示每个指标的参数
                    for metric, params in models1[key].items():
                        print(f"      - {metric}: {params}")
    
    # 分析场景2的结果
    model_path2 = "output/models_scenario2.json"
    if os.path.exists(model_path2):
        print("\n2. 场景2 - 部分样本建模结果分析")
        
        with open(model_path2, 'r') as f:
            models2 = json.load(f)
        
        print(f"   模型类型: {models2.get('type', 'N/A')}")
        
        # 分析调整系数
        if 'A' in models2:
            print(f"   调整系数 A:")
            if isinstance(models2['A'], list):
                print(f"      列表长度: {len(models2['A'])}")
                non_zero = [x for x in models2['A'] if x != 0]
                if non_zero:
                    print(f"      非零值示例: {non_zero[:5]}")
            elif isinstance(models2['A'], dict):
                for metric, value in models2['A'].items():
                    print(f"      - {metric}: {value:.6f}")
        
        if 'Range' in models2:
            print(f"   数据范围 Range:")
            if isinstance(models2['Range'], list):
                print(f"      列表长度: {len(models2['Range'])}")
                print(f"      示例: {models2['Range'][:10]}")
            elif isinstance(models2['Range'], dict):
                for metric, range_info in models2['Range'].items():
                    print(f"      - {metric}: {range_info}")
    
    # 分析原始数据
    print("\n3. 数据特征分析")
    
    # 加载数据
    spectrum_data = pd.read_csv("data/ref_data.csv", index_col=0)
    measure_data = pd.read_csv("data/measure_data.csv", index_col=0)
    water_quality_cols = ['chla', 'turbidity', 'ss', 'codcr', 'tp', 'nh3n', 'bga']
    metric_data = measure_data[water_quality_cols]
    
    # 计算相关性
    print("\n   水质参数之间的相关性:")
    corr_matrix = metric_data.corr()
    print(corr_matrix.round(2))
    
    # 分析光谱特征
    print("\n   光谱数据特征:")
    # 计算每个样本的平均反射率
    mean_reflectance = spectrum_data.mean(axis=1)
    print(f"   - 样本平均反射率范围: {mean_reflectance.min():.4f} - {mean_reflectance.max():.4f}")
    
    # 找出反射率变化最大的波段
    std_by_band = spectrum_data.std(axis=0)
    max_std_band = std_by_band.idxmax()
    print(f"   - 反射率变化最大的波段: {max_std_band} nm (标准差={std_by_band[max_std_band]:.4f})")
    
    # 计算光谱与水质参数的相关性（前6个样本）
    spectrum_matched = spectrum_data.iloc[:6]
    print("\n   光谱平均值与水质参数的相关性:")
    mean_spec = spectrum_matched.mean(axis=1)
    for col in water_quality_cols:
        if col in metric_data.columns:
            corr = mean_spec.corr(metric_data[col])
            print(f"   - {col}: {corr:.3f}")
    
    print("\n========== 分析完成 ==========")

if __name__ == "__main__":
    analyze_modeling_results()