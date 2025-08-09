"""
MCP服务器配置文件
"""

import os

class Config:
    # 工具配置
    TOOL_NAME = "API文档生成工具"
    TOOL_DESCRIPTION = "自动化编排API文档生成工作流"

    # 支持的项目类型
    SUPPORTED_PROJECT_TYPES = [
        "java",
        "python",
        "nodejs",
        "go"
    ]

    # 文档格式配置
    DOC_FORMAT = "markdown"

    # 默认忽略的路径
    DEFAULT_IGNORE_PATHS = [
        "node_modules",
        ".git",
        "__pycache__",
        ".idea",
        ".vscode"
    ]