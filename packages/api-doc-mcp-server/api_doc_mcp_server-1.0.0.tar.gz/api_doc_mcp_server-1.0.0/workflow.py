"""
API文档生成工作流编排器
负责指挥和监督整个API文档生成过程
"""

import hashlib
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class APIRouteInfo:
    """
    API路由信息数据结构
    用于存储单个API路由的详细信息
    """
    # API唯一标识符（基于路径和方法生成MD5）
    id: str
    
    # API基本信息
    path: str                    # API路径
    method: str                  # HTTP方法 (GET, POST, PUT, DELETE等)
    description: str             # API功能描述
    class_path: str              # API所属类路径
    
    # 鉴权信息
    auth_required: bool          # 是否需要鉴权
    
    # 参数信息
    parameters: List[Dict[str, Any]]  # 参数字段列表，每个参数包含name, type, required, description等
    parameter_models: Dict[str, Any]  # 参数数据模型定义（如请求体的JSON结构）
    
    # 响应信息
    response_structure: Dict[str, Any]  # 响应数据结构
    response_models: Dict[str, Any]     # 响应数据模型定义
    response_examples: List[Dict[str, Any]]  # 响应示例列表
    
    # 请求示例
    request_examples: List[Dict[str, Any]]   # 请求示例列表
    
    # 生成状态信息
    generated: bool              # 文档是否已生成
    checked: bool               # 是否已检查完整性
    
    # 完整的原始API数据
    api_data: Dict[str, Any]    # 完整的API数据


class APIDocWorkflowOrchestrator:
    """
    API文档生成工作流编排器
    """
    
    def __init__(self):
        self.current_step = 0
        self.workflow_steps = [
            "开始工作流",
            "分析项目结构",
            "检索API路由和相关代码文件",
            "阅读相关代码文件",
            "编写API文档",
            "检查API文档完整性",
            "补充遗漏内容",
            "工作流结束"
        ]
        self.workflow_data = {}
        
    def start_workflow(self, project_path: str = ".") -> Dict[str, Any]:
        """
        启动API文档生成工作流
        
        Args:
            project_path: 项目根路径
            
        Returns:
            工作流启动状态
        """
        # 生成工作流ID，使用项目绝对路径的MD5值
        abs_path = os.path.abspath(project_path)
        workflow_id = hashlib.md5(abs_path.encode('utf-8')).hexdigest()
        
        self.current_step = 0
        self.workflow_data = {
            "workflow_id": workflow_id,
            "project_path": project_path,
            "status": "started",
            "current_step": self.workflow_steps[self.current_step],
            "progress": f"{self.current_step}/{len(self.workflow_steps)}",
            "api_routes": []  # 存储API路由列表，包含每个API的元数据和生成状态
        }
        
        return {
            "message": f"API文档生成工作流已启动，当前步骤: {self.workflow_steps[self.current_step]}",
            "workflow_data": self.workflow_data
        }
        


# 工作流管理器，用于管理多个工作流实例
class WorkflowManager:
    """
    工作流管理器
    用于管理多个API文档生成工作流实例
    """
    
    def __init__(self):
        # 通过工作流ID管理多个工作流实例
        self.workflows: Dict[str, APIDocWorkflowOrchestrator] = {}
    
    def create_workflow(self, project_path: str = ".") -> Dict[str, Any]:
        """
        创建新的工作流实例
        
        Args:
            project_path: 项目根路径
            
        Returns:
            工作流启动状态和工作流ID
        """
        # 生成工作流ID
        abs_path = os.path.abspath(project_path)
        workflow_id = hashlib.md5(abs_path.encode('utf-8')).hexdigest()
        
        # 创建新的工作流实例
        workflow = APIDocWorkflowOrchestrator()
        self.workflows[workflow_id] = workflow
        
        # 启动工作流
        result = workflow.start_workflow(project_path)
        return result
    
    def get_workflow(self, workflow_id: str) -> Optional[APIDocWorkflowOrchestrator]:
        """
        根据工作流ID获取工作流实例
        
        Args:
            workflow_id: 工作流ID
            
        Returns:
            工作流实例或None（如果不存在）
        """
        return self.workflows.get(workflow_id)
    
    def get_workflow_by_project_path(self, project_path: str) -> Optional[APIDocWorkflowOrchestrator]:
        """
        根据项目路径获取工作流实例
        
        Args:
            project_path: 项目路径
            
        Returns:
            工作流实例或None（如果不存在）
        """
        abs_path = os.path.abspath(project_path)
        workflow_id = hashlib.md5(abs_path.encode('utf-8')).hexdigest()
        return self.workflows.get(workflow_id)
    
    def remove_workflow(self, workflow_id: str) -> bool:
        """
        移除工作流实例
        
        Args:
            workflow_id: 工作流ID
            
        Returns:
            是否成功移除
        """
        if workflow_id in self.workflows:
            del self.workflows[workflow_id]
            return True
        return False


# 全局工作流管理器实例
workflow_manager = WorkflowManager()