# AutoWaterQualityModeler

自动水质光谱建模工具，提供一键式水质建模、预测和评估功能。

## 特性

- **一键式建模**：根据光谱数据和实测值自动构建水质模型
- **多种特征**：支持多种光谱特征，包括波段反射率、波段组合、色度特征等
- **自动特征选择**：根据相关性自动选择最佳特征组合
- **多种模型**：支持幂函数模型和线性模型
- **模型微调**：当样本量不足时，可以使用微调模式
- **模型评估**：提供多种评估指标，如R2、RMSE、MAE、MAPE等
- **命令行接口**：提供友好的命令行接口，方便用户使用

## 安装

### 从PyPI安装

```bash
pip install autowaterqualitymodeler
```

### 从源码安装

```bash
git clone https://github.com/yourusername/AutoWaterQualityModeler.git
cd AutoWaterQualityModeler
pip install -e .
```

## 快速开始

### Python API 使用

```python
from autowaterqualitymodeler import AutoWaterQualityModeler
import pandas as pd

# 加载数据
spectrum_data = pd.read_csv("data/ref_data.csv", index_col=0)
metric_data = pd.read_csv("data/measure_data.csv", index_col=0)

# 创建建模器
modeler = AutoWaterQualityModeler()

# 建模
results = modeler.fit(
    spectrum_data=spectrum_data,
    metric_data=metric_data,
    data_type="aerospot"
)

# 解析结果
if len(results) == 3:
    model_dict, pred_df, all_pred_df = results
else:
    model_dict, pred_df = results

# 保存模型
model_path = modeler.save_model(model_dict, "output/models.json")

# 加载模型并预测
loaded_model = modeler.load_model(model_path)
predictions = modeler.predict(spectrum_data, loaded_model)
```

### 命令行使用

建模：

```bash
# 基本建模
autowaterquality model -s data/ref_data.csv -m data/measure_data.csv -o output/

# 指定数据类型和参数
autowaterquality model -s data/ref_data.csv -m data/measure_data.csv \
    -t aerospot --min-wavelength 450 --max-wavelength 850 -o output/
```

预测：

```bash
autowaterquality predict -s new_spectrum.csv -model output/models.json -o predictions.csv
```

查看帮助：

```bash
autowaterquality --help
autowaterquality model --help
```

## 数据格式

### 光谱数据 (CSV格式)

| Index | 400  | 410  | 420  | ... | 900  |
|-------|------|------|------|-----|------|
| S001  | 0.12 | 0.13 | 0.14 | ... | 0.45 |
| S002  | 0.11 | 0.12 | 0.13 | ... | 0.44 |

- 第一列为样本索引
- 列名为波长值（单位：nm）
- 值为反射率（0-1之间）

### 水质数据 (CSV格式)

| Index | Chl-a | Turbidity | TSS  | ... |
|-------|-------|-----------|------|-----|
| S001  | 12.5  | 8.3       | 15.2 | ... |
| S002  | 10.8  | 7.9       | 14.6 | ... |

- 第一列为样本索引（需与光谱数据对应）
- 列名为水质参数名称
- 值为实测水质参数值

## 项目结构

```
autowaterqualitymodeler/
│
├── core/                     # 核心组件
│   ├── __init__.py
│   ├── modeler.py            # 主入口类
│   ├── feature_manager.py    # 特征管理
│   └── config_manager.py     # 配置管理
│
├── preprocessing/            # 数据预处理
│   ├── __init__.py
│   └── spectrum_processor.py # 光谱数据预处理
│
├── features/                 # 特征计算
│   ├── __init__.py
│   └── calculator.py         # 特征计算器
│
├── models/                   # 模型构建
│   ├── __init__.py
│   └── builder.py            # 模型构建器
│
├── utils/                    # 工具函数
│   ├── __init__.py
│   ├── logger.py             # 日志工具
│   └── encryption.py         # 加密工具
│
├── config/                   # 配置文件
│   └── features_config.json  # 特征配置
│
├── resources/                # 资源文件
│   ├── D65xCIE.xlsx          # 三刺激值系数
│   └── CIE_README.txt        # 说明文档
│
└── cli/                      # 命令行接口
    ├── __init__.py
    └── commands.py           # 命令行工具
```

## 高级功能

### 模型微调

当新样本数量较少时，可以使用历史数据进行模型微调：

```python
# 使用历史数据微调模型
results = modeler.fit(
    spectrum_data=new_spectrum_data,  # 少量新数据
    metric_data=new_metric_data,
    data_type="aerospot",
    matched_idx=new_data_indices,     # 新数据的索引
    origin_merged_data=historical_data # 历史完整数据
)
```

### 自定义特征

可以通过修改配置文件来定义自定义特征：

```json
{
  "aerospot": {
    "turbidity": {
      "features": [
        {
          "name": "custom_feature",
          "formula": "(800-670)/(800+670)",
          "type": "normalized_difference"
        }
      ]
    }
  }
}
```

## 开发

### 环境设置

```bash
# 克隆仓库
git clone https://github.com/yourusername/AutoWaterQualityModeler.git
cd AutoWaterQualityModeler

# 安装开发依赖
pip install -e ".[dev]"
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_spectrum_processor.py

# 查看测试覆盖率
pytest --cov=autowaterqualitymodeler
```

### 代码风格

```bash
# 格式化代码
black autowaterqualitymodeler/

# 检查代码风格
flake8 autowaterqualitymodeler/

# 类型检查
mypy autowaterqualitymodeler/
```

## 贡献

欢迎贡献代码！请遵循以下步骤：

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 作者

周元琦 (zyq1034378361@gmail.com)

## 致谢

感谢所有贡献者和使用者的支持！

## 更新日志

详见 [CHANGELOG.md](CHANGELOG.md)