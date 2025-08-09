#!/usr/bin/env python3
"""
API文档生成MCP工具主入口
"""

import asyncio
import sys
from typing import Dict, List, Any
from mcp.server.lowlevel import Server
from mcp.server.fastmcp import FastMCP
from mcp import types
from workflow import workflow_manager
from config import Config

# 初始化FastMCP实例
mcp_server = FastMCP(
    name=Config.TOOL_NAME,
    instructions=Config.TOOL_DESCRIPTION
)

# 创建底层Server实例用于stdio传输
app = Server(Config.TOOL_NAME)

import logging  # 导入logging模块

# 配置日志
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


@mcp_server.tool()
def start_api_doc_workflow(project_path: str = ".", project_type: str = "auto") -> List[types.TextContent]:
    """
    启动API文档生成工作流
    
    Args:
        project_path: 项目根路径，默认为当前目录
        project_type: 项目类型 (java, python, nodejs, go, auto)
        
    Returns:
        工作流启动确认信息
    """
    logging.debug(f"start_api_doc_workflow called with args: project_path={project_path}, project_type={project_type}")
    result = workflow_manager.create_workflow(project_path)
    logging.debug(f"start_api_doc_workflow result: {result}")
    
    # 添加系统提示，指导下一步操作
    system_prompt = """
系统提示：
下一步请分析当前项目结构，识别当前项目所有的Rest API路由控制器、认证拦截器和过滤器的代码文件位置。注意：是要求所有的，不能有遗漏！
分析完成后，请调用 store_project_analysis_result 工具存储分析结果。
需要的参数：
- project_path: 当前项目路径
- analysis_result: 分析得到的项目结构信息，应包含以下内容：
  {
    "routes": ["文件路径列表"],
    "auth_interceptors": ["认证拦截器文件路径列表"],
    "filters": ["过滤器文件路径列表"],
    "controllers": ["控制器文件路径列表"],
    "models": ["数据模型文件路径列表"]
  }

示例调用：
{"name": "store_project_analysis_result", "arguments": {"project_path": ".", "analysis_result": {...}}}
"""
    
    result["system_prompt"] = system_prompt
    return [types.TextContent(type="text", text=str(result))]


@mcp_server.tool()
def store_project_analysis_result(project_path: str, analysis_result: Dict[str, Any]) -> List[types.TextContent]:
    """
    存储项目结构分析结果
    
    Args:
        project_path: 项目根路径
        analysis_result: 项目结构分析结果，包含routes, auth_interceptors, filters, controllers, models等信息
        
    Returns:
        存储确认信息和下一步指导
    """
    logging.debug(f"store_project_analysis_result called with args: project_path={project_path}, analysis_result={analysis_result}")
    
    # 根据项目路径获取工作流实例
    workflow = workflow_manager.get_workflow_by_project_path(project_path)
    if not workflow:
        error_msg = f"未找到项目 {project_path} 对应的工作流实例"
        logging.error(error_msg)
        return [types.TextContent(type="text", text=error_msg)]
    
    # 将分析结果存储到工作流数据中
    workflow.workflow_data["project_analysis_result"] = analysis_result
    workflow.workflow_data["project_path"] = project_path
    
    # 从分析结果中提取所有需要阅读的文件路径
    routes = analysis_result.get("routes", [])
    auth_interceptors = analysis_result.get("auth_interceptors", [])
    filters = analysis_result.get("filters", [])
    controllers = analysis_result.get("controllers", [])
    models = analysis_result.get("models", [])
    
    all_files = routes + auth_interceptors + filters + controllers + models
    
    result = {
        "message": "项目结构分析结果已存储",
        "status": "success",
        "workflow_id": workflow.workflow_data.get("workflow_id"),
        "stored_data": {
            "routes_count": len(routes),
            "auth_interceptors_count": len(auth_interceptors),
            "filters_count": len(filters),
            "controllers_count": len(controllers),
            "models_count": len(models),
            "total_files_count": len(all_files)
        }
    }
    
    # 添加系统提示，指导下一步操作
    system_prompt = f"""
系统提示：
项目结构分析结果已存储。现在需要阅读所有相关的代码文件以提取API元数据信息。

请逐个阅读以下代码文件：
{chr(10).join([f"- {file}" for file in all_files])}

阅读完成后，请调用 store_api_metadata 工具批量存储API元数据信息。
如果文件数量较多，可以分多次调用，但必须确保所有文件都被处理。

需要的参数：
- workflow_id: 当前工作流ID "{workflow.workflow_data.get("workflow_id")}"
- api_metadata_list: API元数据列表，每个元素应包含以下信息：
  {{
    "file_path": "文件路径",
    "apis": [
      {{
        "path": "API路径",
        "method": "HTTP方法",
        "description": "功能描述",
        "class_path": "类路径",
        "auth_required": true/false,
        "parameters": [
          {{
            "name": "参数名",
            "in": "参数位置 (path, query, header, cookie, body)",
            "type": "参数类型",
            "required": true/false,
            "description": "参数描述"
          }}
        ],
        "parameter_models": {{
          "模型名": {{
            "type": "object",
            "properties": {{
              "字段名": {{
                "type": "字段类型",
                "description": "字段描述"
              }}
            }},
            "required": ["必填字段列表"]
          }}
        }},
        "response_structure": {{
          "type": "object",
          "properties": {{
            "字段名": {{
              "type": "字段类型",
              "description": "字段描述"
            }}
          }}
        }},
        "response_models": {{
          "模型名": {{
            "type": "object",
            "properties": {{
              "字段名": {{
                "type": "字段类型",
                "description": "字段描述"
              }}
            }},
            "required": ["必填字段列表"]
          }}
        }},
        "response_examples": [响应示例列表],
        "request_examples": [请求示例列表]
      }}
    ]
  }}

关于parameters、parameter_models、response_structure、response_models四个字段的说明：
1. parameters: 简单参数列表，适用于路径参数、查询参数、请求头参数等
2. parameter_models: 复杂参数模型定义，特别是请求体中的JSON对象结构
3. response_structure: API响应的整体结构描述
4. response_models: 响应中复杂对象的详细结构定义

示例调用：
{{"name": "store_api_metadata", "arguments": {{"workflow_id": "{workflow.workflow_data.get("workflow_id")}", "api_metadata_list": [...]}}}}
"""
    
    result["system_prompt"] = system_prompt
    logging.debug(f"store_project_analysis_result result: {result}")
    return [types.TextContent(type="text", text=str(result))]


@mcp_server.tool()
def store_api_metadata(workflow_id: str, api_metadata_list: List[Dict[str, Any]]) -> List[types.TextContent]:
    """
    存储API元数据信息
    
    Args:
        workflow_id: 工作流ID
        api_metadata_list: API元数据列表
        
    Returns:
        存储确认信息和下一步指导
    """
    logging.debug(f"store_api_metadata called with args: workflow_id={workflow_id}, api_metadata_list={api_metadata_list}")
    
    # 根据工作流ID获取工作流实例
    workflow = workflow_manager.get_workflow(workflow_id)
    if not workflow:
        error_msg = f"未找到工作流ID {workflow_id} 对应的工作流实例"
        logging.error(error_msg)
        return [types.TextContent(type="text", text=error_msg)]
    
    # 将API元数据存储到工作流数据中
    if "api_metadata" not in workflow.workflow_data:
        workflow.workflow_data["api_metadata"] = []
    
    workflow.workflow_data["api_metadata"].extend(api_metadata_list)
    
    stored_count = len(workflow.workflow_data["api_metadata"])
    
    result = {
        "message": f"API元数据已存储，当前共存储 {stored_count} 个文件的元数据",
        "status": "success",
        "workflow_id": workflow_id,
        "stored_count": stored_count
    }
    
    # 添加系统提示，指导下一步操作
    system_prompt = f"""
系统提示：
API元数据已存储。如果还有未处理的代码文件，请继续调用 store_api_metadata 工具存储剩余的API元数据信息。

如果所有文件都已处理完毕，可以开始生成API文档了。请调用 generate_api_documentation 工具生成API文档。
需要的参数：
- workflow_id: 当前工作流ID "{workflow_id}"
- batch_index: 批次索引，用于分批处理大量API，默认为0

示例调用：
{{"name": "generate_api_documentation", "arguments": {{"workflow_id": "{workflow_id}", "batch_index": 0}}}}
"""
    
    result["system_prompt"] = system_prompt
    logging.debug(f"store_api_metadata result: {result}")
    return [types.TextContent(type="text", text=str(result))]


@mcp_server.tool()
def generate_api_documentation(batch_index: int = 0, workflow_id: str = None) -> List[types.TextContent]:
    """
    根据提取的API信息生成Markdown格式的API文档
    
    Args:
        batch_index: 批次索引，用于分批处理大量API
        workflow_id: 工作流ID，用于指定特定的工作流实例
        
    Returns:
        提供给Cursor的API信息，用于生成文档
    """
    logging.debug(f"generate_api_documentation called with args: batch_index={batch_index}, workflow_id={workflow_id}")
    
    # 根据工作流ID获取工作流实例
    if workflow_id:
        workflow = workflow_manager.get_workflow(workflow_id)
    else:
        # 如果没有提供工作流ID，尝试从当前上下文中获取
        # 这里简化处理，实际应用中可能需要更好的上下文管理
        workflow = list(workflow_manager.workflows.values())[0] if workflow_manager.workflows else None
    
    if not workflow:
        error_msg = f"未找到工作流实例"
        logging.error(error_msg)
        return [types.TextContent(type="text", text=error_msg)]
    
    # 获取所有已存储的API元数据并整合
    api_metadata_list = workflow.workflow_data.get("api_metadata", [])
    
    # 提取所有API信息
    all_apis = []
    for metadata in api_metadata_list:
        apis = metadata.get("apis", [])
        all_apis.extend(apis)
    
    # 更新工作流数据中的API路由信息
    workflow.workflow_data["api_routes"] = all_apis
    
    # 获取工作流数据中的API路由信息
    workflow_data = workflow.workflow_data
    api_routes = workflow_data.get("api_routes", [])
    
    # 计算分批信息
    batch_size = 50  # 每批最多处理50个API
    total_apis = len(api_routes)
    # 向上取整计算总批次数，等价于 math.ceil(total_apis / batch_size)
    # 例如：101个API，每批50个 = (101 + 50 - 1) // 50 = 150 // 50 = 3批
    total_batches = (total_apis + batch_size - 1) // batch_size
    
    # 确保批次索引有效
    if batch_index < 0 or batch_index >= total_batches:
        error_msg = f"无效的批次索引: {batch_index}，有效范围: 0-{total_batches-1}"
        logging.error(error_msg)
        return [types.TextContent(type="text", text=error_msg)]
    
    # 计算当前批次的API范围
    start_index = batch_index * batch_size
    end_index = min(start_index + batch_size, total_apis)
    batch_apis = api_routes[start_index:end_index]
    
    # 为每个API的参数添加详细结构
    for api in batch_apis:
        parameters = api.get("parameters", [])
        parameter_models = {}
        
        for param in parameters:
            param_type = param.get("type")
            if param_type and not isinstance(param_type, str):
                # 处理复杂类型（假设param_type是一个字典，包含复杂类型的结构）
                param_model_name = param_type.get("name", "UnknownModel")
                parameter_models[param_model_name] = param_type
        
        if parameter_models:
            api["parameter_models"] = parameter_models
    
    # 准备返回给Cursor的信息
    result = {
        "message": f"请为以下API生成文档 (批次 {batch_index+1}/{total_batches})",
        "command": "generate_api_documentation",
        "workflow_id": workflow_id or workflow_data.get("workflow_id"),
        "batch_info": {
            "batch_index": batch_index,
            "batch_size": len(batch_apis),
            "total_apis": total_apis,
            "total_batches": total_batches,
            "is_last_batch": (batch_index == total_batches - 1)
        },
        "apis": batch_apis,
        "required_format": {
            "api_address": "API地址",
            "class_path": "API所属类路径",
            "description": "API功能描述",
            "auth_required": "API是否需要鉴权",
            "parameters": "参数字段说明",
            "response_structure": "响应数据结构和字段说明",
            "request_example": "请求示例",
            "response_example": "响应示例"
        }
    }
    
    # 添加系统提示，指导下一步操作
    if batch_index < total_batches - 1:
        system_prompt = f"""
系统提示：
还有更多API需要处理。请继续调用 generate_api_documentation 工具处理下一批API。
需要的参数：
- batch_index: 下一批次索引 {batch_index + 1}
- workflow_id: 当前工作流ID "{workflow_id or workflow_data.get("workflow_id")}"

示例调用：
{{"name": "generate_api_documentation", "arguments": {{"batch_index": {batch_index + 1}, "workflow_id": "{workflow_id or workflow_data.get("workflow_id")}"}}}}
"""
    else:
        system_prompt = """
系统提示：
所有API文档已生成。工作流已完成。
"""
        # 工作流完成，清理工作流数据以避免内存泄漏
        workflow_id_to_remove = workflow_id or workflow_data.get("workflow_id")
        if workflow_id_to_remove:
            workflow_manager.remove_workflow(workflow_id_to_remove)
            logging.debug(f"工作流 {workflow_id_to_remove} 已完成并从内存中清理")
    
    result["system_prompt"] = system_prompt
    logging.debug(f"generate_api_documentation result: {result}")
    return [types.TextContent(type="text", text=str(result))]


# 将FastMCP工具注册到底层Server实例
# 这需要手动复制工具定义到底层Server实例
@app.call_tool()
async def call_tool(name: str, arguments: Dict) -> Any:
    # 这里需要将工具调用转发到FastMCP实例
    # 简化实现，直接调用对应的函数
    tool_functions = {
        "start_api_doc_workflow": start_api_doc_workflow,
        "store_project_analysis_result": store_project_analysis_result,
        "store_api_metadata": store_api_metadata,
        "generate_api_documentation": generate_api_documentation,
    }
    
    if name in tool_functions:
        func = tool_functions[name]
        # 检查函数是否为异步函数
        if asyncio.iscoroutinefunction(func):
            return await func(**arguments)
        else:
            return func(**arguments)
    else:
        raise ValueError(f"Unknown tool: {name}")


@app.list_tools()
async def list_tools():
    from mcp.types import Tool
    return [
        Tool(
            name="start_api_doc_workflow",
            description="启动API文档生成工作流",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {"type": "string", "description": "项目根路径，默认为当前目录"},
                    "project_type": {"type": "string", "description": "项目类型 (java, python, nodejs, go, auto)"}
                }
            }
        ),
        Tool(
            name="store_project_analysis_result",
            description="存储项目结构分析结果，包含API路由、认证拦截器、过滤器等文件路径信息",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {"type": "string", "description": "项目根路径"},
                    "analysis_result": {
                        "type": "object", 
                        "description": "项目结构分析结果，包含API路由、认证拦截器、过滤器、控制器和数据模型文件路径信息",
                        "properties": {
                            "routes": {"type": "array", "items": {"type": "string"}, "description": "API路由文件路径列表"},
                            "auth_interceptors": {"type": "array", "items": {"type": "string"}, "description": "认证拦截器文件路径列表"},
                            "filters": {"type": "array", "items": {"type": "string"}, "description": "过滤器文件路径列表"},
                            "controllers": {"type": "array", "items": {"type": "string"}, "description": "控制器文件路径列表"},
                            "models": {"type": "array", "items": {"type": "string"}, "description": "数据模型文件路径列表"}
                        }
                    }
                },
                "required": ["project_path", "analysis_result"]
            }
        ),
        Tool(
            name="store_api_metadata",
            description="存储API元数据信息，包含API路径、方法、参数、响应结构等详细信息",
            inputSchema={
                "type": "object",
                "properties": {
                    "workflow_id": {"type": "string", "description": "工作流ID"},
                    "api_metadata_list": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "file_path": {"type": "string", "description": "文件路径"},
                                "apis": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "path": {"type": "string", "description": "API路径"},
                                            "method": {"type": "string", "description": "HTTP方法"},
                                            "description": {"type": "string", "description": "功能描述"},
                                            "class_path": {"type": "string", "description": "类路径"},
                                            "auth_required": {"type": "boolean", "description": "是否需要鉴权"},
                                            "parameters": {
                                                "type": "array", 
                                                "description": "简单参数列表，适用于路径参数、查询参数、请求头参数等",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "name": {"type": "string", "description": "参数名"},
                                                        "in": {"type": "string", "description": "参数位置 (path, query, header, cookie, body)"},
                                                        "type": {"type": "string", "description": "参数类型"},
                                                        "required": {"type": "boolean", "description": "是否必需"},
                                                        "description": {"type": "string", "description": "参数描述"}
                                                    }
                                                }
                                            },
                                            "parameter_models": {
                                                "type": "object", 
                                                "description": "复杂参数模型定义，特别是请求体中的JSON对象结构"
                                            },
                                            "response_structure": {
                                                "type": "object", 
                                                "description": "API响应的整体结构描述"
                                            },
                                            "response_models": {
                                                "type": "object", 
                                                "description": "响应中复杂对象的详细结构定义"
                                            },
                                            "response_examples": {"type": "array", "description": "响应示例列表"},
                                            "request_examples": {"type": "array", "description": "请求示例列表"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "required": ["workflow_id", "api_metadata_list"]
            }
        ),
        Tool(
            name="generate_api_documentation",
            description="根据提取的API信息生成Markdown格式的API文档，支持分批处理大量API",
            inputSchema={
                "type": "object",
                "properties": {
                    "batch_index": {"type": "integer", "description": "批次索引，用于分批处理大量API，默认为0"},
                    "workflow_id": {"type": "string", "description": "工作流ID，用于指定特定的工作流实例"}
                }
            }
        )
    ]


def main():
    """主函数，支持stdio方式运行"""
    if len(sys.argv) > 1 and sys.argv[1] == "serve":
        # 保持原来的SSE方式运行
        import uvicorn
        from mcp.server.sse import SseServerTransport
        from starlette.applications import Starlette
        from starlette.responses import Response
        from starlette.routing import Mount, Route

        print(f"启动 {Config.TOOL_NAME} 服务...")
        print("使用 SSE 方式运行")
        print("SSE端点: http://localhost:8000/sse")
        print("消息端点: http://localhost:8000/messages/")
        
        # 使用SSE方式运行MCP服务
        sse = SseServerTransport("/messages/")

        async def handle_sse(request):
            async with sse.connect_sse(
                request.scope, request.receive, request._send
            ) as streams:
                await app.run(
                    streams[0], streams[1], app.create_initialization_options()
                )
            return Response()

        starlette_app = Starlette(
            debug=True,
            routes=[
                Route("/sse", endpoint=handle_sse, methods=["GET"]),
                Mount("/messages/", app=sse.handle_post_message),
            ],
        )

        uvicorn.run(starlette_app, host="127.0.0.1", port=8000)
    else:
        # 使用stdio方式运行
        import anyio
        from mcp.server.stdio import stdio_server
        
        print(f"启动 {Config.TOOL_NAME}...")
        print("使用 stdio 方式运行")
        
        async def run_app():
            async with stdio_server() as (read_stream, write_stream):
                await app.run(read_stream, write_stream, app.create_initialization_options())
        
        anyio.run(run_app)


if __name__ == "__main__":
    main()