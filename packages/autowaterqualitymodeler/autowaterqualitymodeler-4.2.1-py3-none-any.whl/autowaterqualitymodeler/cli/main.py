"""
CLI 主入口模块
"""

from .commands import main

# 为 setuptools 入口点提供 cli 函数
cli = main

if __name__ == '__main__':
    main()