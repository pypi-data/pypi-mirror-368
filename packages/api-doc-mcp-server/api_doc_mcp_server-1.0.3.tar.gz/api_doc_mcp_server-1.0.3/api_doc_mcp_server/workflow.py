"""
工作流定义模块
"""

import uuid
from typing import Dict, Any, Optional


class WorkflowManager:
    """工作流管理器"""
    
    def __init__(self):
        # 存储所有工作流实例
        self.workflows: Dict[str, Workflow] = {}
        # 存储项目路径到工作流ID的映射
        self.project_path_to_workflow_id: Dict[str, str] = {}
    
    def create_workflow(self, project_path: str = ".") -> Dict[str, Any]:
        """
        为指定项目路径创建新的工作流实例
        
        Args:
            project_path: 项目路径
            
        Returns:
            工作流信息
        """
        # 为工作流生成唯一ID
        workflow_id = str(uuid.uuid4())
        
        # 创建新的工作流实例
        workflow = Workflow(workflow_id, project_path)
        
        # 存储工作流实例
        self.workflows[workflow_id] = workflow
        self.project_path_to_workflow_id[project_path] = workflow_id
        
        return {
            "message": "API文档生成工作流已启动",
            "status": "success",
            "workflow_id": workflow_id,
            "project_path": project_path
        }
    
    def get_workflow(self, workflow_id: str) -> Optional['Workflow']:
        """
        根据工作流ID获取工作流实例
        
        Args:
            workflow_id: 工作流ID
            
        Returns:
            工作流实例或None
        """
        return self.workflows.get(workflow_id)
    
    def get_workflow_by_project_path(self, project_path: str) -> Optional['Workflow']:
        """
        根据项目路径获取工作流实例
        
        Args:
            project_path: 项目路径
            
        Returns:
            工作流实例或None
        """
        workflow_id = self.project_path_to_workflow_id.get(project_path)
        if workflow_id:
            return self.workflows.get(workflow_id)
        return None
    
    def remove_workflow(self, workflow_id: str) -> bool:
        """
        移除工作流实例
        
        Args:
            workflow_id: 工作流ID
            
        Returns:
            是否成功移除
        """
        if workflow_id in self.workflows:
            workflow = self.workflows[workflow_id]
            project_path = workflow.project_path
            
            # 从映射中移除
            if project_path in self.project_path_to_workflow_id:
                del self.project_path_to_workflow_id[project_path]
            
            # 从工作流字典中移除
            del self.workflows[workflow_id]
            return True
        return False


class Workflow:
    """工作流实例"""
    
    def __init__(self, workflow_id: str, project_path: str):
        self.workflow_id = workflow_id
        self.project_path = project_path
        self.workflow_data: Dict[str, Any] = {}


# 创建全局工作流管理器实例
workflow_manager = WorkflowManager()