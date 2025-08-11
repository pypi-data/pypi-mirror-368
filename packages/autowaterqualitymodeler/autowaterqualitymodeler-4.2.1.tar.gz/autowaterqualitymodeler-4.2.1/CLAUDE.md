# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

AutoWaterQualityModeler 是一个基于光谱数据的水质建模Python包，提供自动化的水质预测模型构建和评估功能。主要应用于水质监测和环境科学研究。

## 常用开发命令

### 环境设置
```bash
# 安装开发依赖
pip install -e ".[dev]"

# 或使用uv（推荐）
just sync
```

### 测试
```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_modeler.py

# 运行带覆盖率的测试
pytest --cov=autowaterqualitymodeler

# 排除慢速测试
pytest -m "not slow"

# 只运行单元测试
pytest -m "unit"

# 运行集成测试
pytest -m "integration"
```

### 代码质量检查
```bash
# 代码格式化
black autowaterqualitymodeler/
isort autowaterqualitymodeler/

# 类型检查
mypy autowaterqualitymodeler/

# 代码风格检查
flake8 autowaterqualitymodeler/
```

### 构建和打包
```bash
# 使用标准方式构建
python -m build

# 使用uv构建（推荐）
just build

# 清理构建文件
just clean
```

### CLI使用
```bash
# 建模
autowaterquality model -s data/ref_data.csv -m data/measure_data.csv -o output/

# 预测
autowaterquality predict -s new_spectrum.csv -model output/models.json -o predictions.csv
```

## 核心架构

### 主要模块职责
- **core/modeler.py**: 主入口类 `AutoWaterQualityModeler`，提供完整建模流程
- **core/feature_manager.py**: 特征管理和自动选择
- **preprocessing/spectrum_processor.py**: 光谱数据预处理（平滑、筛选）
- **features/calculator.py**: 计算各种光谱特征（波段比值、色度等）
- **models/builder.py**: 模型构建和评估
- **cli/**: 命令行接口实现

### 数据流
1. 光谱数据预处理 → 特征计算 → 特征选择 → 模型构建 → 评估和优化
2. 支持两种数据类型：`aerospot`（反射率）和 `field`（实地数据）
3. 自动化特征选择基于统计指标和相关性分析

### 配置系统
- `config/features_config.json`: 特征计算配置
- `config/system_config.json`: 系统参数配置
- 支持运行时配置修改和自定义特征定义

### 模型类型
- **PowerModel**: 幂函数模型（主要用于波段比值特征）
- **LinearModel**: 线性模型（用于复杂特征组合）
- 自动选择最优模型类型和参数

## 测试策略

### 测试标记
- `unit`: 单元测试，测试单个函数或方法
- `integration`: 集成测试，测试完整工作流程
- `slow`: 慢速测试，包含大量计算的测试

### 数据依赖
测试使用 `tests/conftest.py` 中的fixtures提供模拟数据，包括：
- 光谱数据（波长350-900nm）
- 实测水质指标
- 预配置的建模参数

## 重要注意事项

### 数据要求
- 光谱数据：CSV格式，行为样本，列为波长
- 实测数据：CSV格式，行为样本，列为水质指标
- 索引必须匹配以进行正确的数据关联

### 缓存系统
- **跨平台缓存目录**：
  - Windows: `%LOCALAPPDATA%\AutoWaterQualityModeler\cache`
  - macOS: `~/Library/Caches/AutoWaterQualityModeler`
  - Linux: `~/.cache/autowaterqualitymodeler`
- **权限处理**：自动降级机制，权限不足时禁用文件缓存，仅使用内存缓存
- 支持内存和磁盘双重缓存，确保在任何环境下都能正常运行
- 无权限问题：即使无法创建缓存目录也不会导致程序崩溃

### 性能优化
- 使用 `utils/cache.py` 进行结果缓存
- 多进程并行特征计算
- 大数据集分批处理

### 安全性
- 敏感数据使用 `utils/encryption.py` 加密
- 不在日志中记录原始数据
- 配置文件不包含敏感信息

## 发布流程

版本管理使用 `setuptools_scm`，通过Git标签自动生成版本号：

```bash
# 创建版本标签
git tag v1.0.0
git push origin v1.0.0

# 自动触发GitHub Actions构建和发布到PyPI
```