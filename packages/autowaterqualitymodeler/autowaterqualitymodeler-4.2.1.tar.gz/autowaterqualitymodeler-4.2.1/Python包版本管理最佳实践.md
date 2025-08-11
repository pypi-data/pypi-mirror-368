# Python包版本管理最佳实践

## 问题背景

在Python包开发中，经常遇到以下版本管理问题：
1. CI/CD构建时版本号自动增加（如v4.0.1变成4.0.2.dev0）
2. 安装后的包`__init__.py`中显示的版本号与实际发布版本不符
3. setuptools_scm在多标签情况下选择错误版本

## 最佳解决方案

### 1. pyproject.toml配置

```toml
[project]
name = "your-package-name"
dynamic = ["version"]
# 其他配置...

[build-system]
requires = ["setuptools>=61.0", "setuptools_scm[toml]>=6.2"]
build-backend = "setuptools.build_meta"

[tool.setuptools_scm]
write_to = "your_package/_version.py"
version_scheme = "python-simplified-semver"
local_scheme = "no-local-version"
```

**关键点：**
- 使用`dynamic = ["version"]`让setuptools_scm管理版本
- 启用`write_to`生成版本文件供开发环境使用
- `local_scheme = "no-local-version"`避免开发版本后缀

### 2. __init__.py版本获取逻辑

```python
# 版本号获取，优先级：包元数据 > _version.py > fallback
try:
    from importlib.metadata import version, PackageNotFoundError
    try:
        __version__ = version("your-package-name")
    except PackageNotFoundError:
        # 开发环境或未安装的包，尝试从_version.py获取
        try:
            from ._version import __version__
        except ImportError:
            __version__ = "0.1.0"  # fallback版本
except ImportError:
    # Python < 3.8，使用importlib_metadata
    try:
        from importlib_metadata import version, PackageNotFoundError
        try:
            __version__ = version("your-package-name")
        except PackageNotFoundError:
            try:
                from ._version import __version__
            except ImportError:
                __version__ = "0.1.0"
    except ImportError:
        # 完全fallback
        try:
            from ._version import __version__
        except ImportError:
            __version__ = "0.1.0"
```

**版本获取优先级：**
1. **包元数据**（安装后）：`importlib.metadata.version()`
2. **_version.py文件**（开发环境）：setuptools_scm生成
3. **fallback版本**（兜底）：固定版本号

### 3. .gitignore配置

```gitignore
# setuptools_scm生成的版本文件
your_package/_version.py
```

避免版本文件被提交到版本控制中，防止版本冲突。

### 4. 标签管理规范

#### 正确的发布流程：
```bash
# 1. 提交代码
git add -A
git commit -m "功能描述"

# 2. 创建标签
git tag v1.0.0

# 3. 推送代码和标签
git push origin main
git push origin v1.0.0
```

#### 避免多标签冲突：
```bash
# 检查当前提交的所有标签
git tag --contains HEAD

# 如果有多个标签，删除不需要的
git tag -d v1.0.0-old
git push origin :refs/tags/v1.0.0-old
```

**重要提醒：** setuptools_scm在同一提交有多个标签时会选择版本号较小的标签。

### 5. CI/CD配置注意事项

#### GitHub Actions示例：
```yaml
name: Build and Publish

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # 获取完整的Git历史，确保标签可见
      
      - name: Build package
        run: python -m build
      
      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          password: ${{ secrets.PYPI_API_TOKEN }}
```

**关键配置：**
- `fetch-depth: 0`：确保CI环境能访问所有Git标签
- 只在标签推送时触发构建

## 工作原理

### 安装前（开发环境）
- setuptools_scm从Git标签读取版本，生成`_version.py`
- `__init__.py`从`_version.py`获取版本号

### 安装后（用户环境）
- `importlib.metadata.version()`从包元数据获取正确版本
- 包元数据版本来自构建时的Git标签
- 用户看到的版本与发布标签完全一致

### 构建时（CI环境）
- setuptools_scm读取Git标签作为包版本
- 不会修改源码，避免版本号漂移
- 生成的包文件名与标签版本一致

## 常见问题解决

### 问题1：CI构建版本号自动增加
**原因：** Git仓库状态不干净或setuptools_scm配置错误  
**解决：** 使用`local_scheme = "no-local-version"`，确保CI环境有完整Git历史

### 问题2：安装后版本号不正确
**原因：** 只依赖静态版本号或_version.py文件  
**解决：** 使用本文档的多级fallback版本获取逻辑

### 问题3：多标签冲突
**原因：** 同一提交有多个标签，setuptools_scm选择较小版本  
**解决：** 清理不需要的标签，确保每个提交只有一个发布标签

## 验证方法

### 本地验证：
```bash
# 检查setuptools_scm识别的版本
python -c "from setuptools_scm import get_version; print(get_version())"

# 检查包导入的版本
python -c "import your_package; print(your_package.__version__)"
```

### 安装后验证：
```bash
pip install your-package==1.0.0
python -c "import your_package; print(your_package.__version__)"
# 应该输出: 1.0.0
```

## 总结

这套方案的核心优势：
1. **自动化**：版本号完全由Git标签驱动，无需手动维护
2. **一致性**：开发、构建、安装各环节版本号保持一致
3. **健壮性**：多级fallback机制确保任何环境都能正常工作
4. **简洁性**：避免复杂的版本管理脚本和手动同步

通过遵循这些最佳实践，可以彻底解决Python包版本管理的常见问题，实现真正的"一次配置，永久有效"。