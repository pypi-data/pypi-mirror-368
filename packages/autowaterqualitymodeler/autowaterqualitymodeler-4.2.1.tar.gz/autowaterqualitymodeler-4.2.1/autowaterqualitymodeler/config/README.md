# AutoWaterQualityModeler 特征配置文件使用说明

`features_config.json` 是AutoWaterQualityModeler的核心配置文件，用于定义光谱特征计算方法、模型参数以及不同水体类型下的特征组合。本文档将指导您如何正确配置此文件。

## 配置文件结构

配置文件由四个主要部分组成：
1. 全局模型参数
2. 特征定义库
3. 数据类型特征配置
   - 预警器数据（warning_device）
   - 岸基数据（shore_data）
   - 智水数据（smart_water）

## 一、全局模型参数设置

```json
"model_params": {
  "max_features": "5",  // 最大特征数量
  "min_samples": 1      // 最小样本数量
}
```

| 参数名 | 说明 | 可选值 |
|-------|------|-------|
| max_features | 建模时使用的最大特征数 | 数值或"all"（使用所有特征） |
| min_samples | 建模所需最小样本数 | 正整数（建议≥6） |

## 二、特征定义库配置

特征定义库包含可用于建模的所有光谱特征计算方法：

```json
"features": {
  "F1": {
    "name": "rg_ratio",
    "formula": "ref(B1) / ref(B2)",
    "bands": {
      "B1": 670,
      "B2": 550
    }
  },
  // 更多特征...
}
```

每个特征定义包含：

| 字段 | 说明 | 示例 |
|-----|------|------|
| name | 特征名称 | "rg_ratio" |
| formula | 特征计算公式 | "ref(B1) / ref(B2)" |
| bands | 波段映射（公式中使用的变量） | {"B1": 670, "B2": 550} |

### 支持的计算函数

配置中可以使用以下函数：

- `ref(band)`: 获取指定波长的反射率
- `sum(start_band, end_band)`: 计算波段范围内的积分值
- `mean(start_band, end_band)`: 计算波段范围内的平均值
- `abs(value)`: 计算绝对值
- `tris(x/y/z)`: 计算三刺激值（x、y或z）

### 特征定义示例

```json
"F6": {
  "name": "three_band_model",
  "formula": "(1/ref(B1) - 1/ref(B2)) * ref(B3)",
  "bands": {
    "B1": 665,
    "B2": 708,
    "B3": 753
  }
}
```

## 三、数据类型特征配置

对每种水体类型（warning_device, shore_data, smart_water），可以定义特定的模型参数和各个水质指标的特征组合：

```json
"shore_data": {
  "model_params": {  // 数据类型级别参数，覆盖全局参数
    "max_features": "all",
    "min_samples": 7
  },
  "chla": {  // 叶绿素a指标
    "name": "叶绿素a",
    "model_params": {},  // 指标级别参数，覆盖数据类型参数
    "features": [  // 该指标使用的特征列表
      {
        "feature_id": "F6"  // 引用特征定义库中的特征ID
      },
      {
        "feature_id": "F5",  // 引用特征但重定义波段
        "bands": {
          "B1": 760,
          "B2": 670
        }
      }
    ]
  },
  // 其他水质指标...
}
```

### 每种水体类型下的配置内容

1. **数据类型级别参数**：适用于该水体类型的所有指标
2. **各水质指标配置**：
   - `name`: 指标中文名称
   - `model_params`: 指标特定参数，覆盖数据类型参数
   - `features`: 用于该指标建模的特征列表

### 参数覆盖机制

参数优先级：指标级别 > 数据类型级别 > 全局级别

## 四、配置文件修改步骤

### 添加新特征

1. 在`features`部分添加新特征定义：
   ```json
   "F26": {
     "name": "新特征名称",
     "formula": "计算公式",
     "bands": {
       "B1": 波长1,
       "B2": 波长2
     }
   }
   ```

2. 在相应水体类型和指标下引用新特征：
   ```json
   "features": [
     {
       "feature_id": "F26"
     }
   ]
   ```

### 修改现有特征

1. 可直接修改特征定义库中的公式或波段映射
2. 也可在指标配置中使用原特征ID但重定义波段映射

### 添加新水质指标

在相应的水体类型下添加新指标配置：
```json
"new_parameter": {
  "name": "新指标名称",
  "model_params": {
    "max_features": 3
  },
  "features": [
    {"feature_id": "F1"},
    {"feature_id": "F2"}
  ]
}
```

## 五、配置验证与最佳实践

1. **确保JSON格式有效**：修改后检查文件格式是否正确
2. **避免使用不存在的波长**：确保公式中引用的波长在光谱数据中存在
3. **优先使用已验证的特征**：使用文献中已验证的光谱指数
4. **特征递进筛选**：从基础特征开始，根据相关性依次添加复杂特征
5. **参数合理设置**：
   - `min_samples`应根据数据量合理设置（建议至少6个样本）
   - `max_features`不宜过多（一般3-5个为宜）

## 六、常见问题

1. **为什么部分指标建模失败？**
   - 检查样本量达到`min_samples`要求，但是在计算特征时部分样本的某些特征计算得到NaN或者无穷大、无穷小，此样本会被剔除，导致不再满足该指标`min_samples`要求，甚至可用样本量为0.



## 七、附录：完整配置示例

以下是一个简化的配置示例：

```json
{
  "model_params": {
    "max_features": "5",
    "min_samples": 6
  },
  "features": {
    "F1": {
      "name": "rg_ratio",
      "formula": "ref(B1) / ref(B2)",
      "bands": {
        "B1": 670,
        "B2": 550
      }
    },
    "F2": {
      "name": "three_band_model",
      "formula": "(1/ref(B1) - 1/ref(B2)) * ref(B3)",
      "bands": {
        "B1": 665,
        "B2": 708,
        "B3": 753
      }
    }
  },
  "shore_data": {
    "model_params": {
      "max_features": "all"
    },
    "chla": {
      "name": "叶绿素a",
      "features": [
        {"feature_id": "F1"},
        {"feature_id": "F2"}
      ]
    }
  }
}
```

通过正确配置features_config.json文件，您可以为不同水体类型的各种水质指标定制最合适的特征组合，实现高精度的水质参数预测模型。 