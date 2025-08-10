# API文档生成MCP工具使用示例

## 基本用法

### 1. 启动工作流

在Cursor中调用MCP工具：

```
/start_api_doc_workflow project_path="."
```

### 2. 分析项目结构

```
/analyze_project_structure project_path="."
```

### 3. 获取分析结果

```
/get_analysis_result
```

### 4. 检索API路由

```
/retrieve_api_routes
```

### 5. 阅读代码文件

```
/read_api_code_files
```

### 6. 获取阅读结果

```
/get_reading_result
```

### 7. 提取API信息

```
/extract_api_info
```

### 8. 生成API文档

```
/generate_api_documentation
```

### 9. 检查文档完整性

```
/check_documentation_completeness
```

### 10. 更新API文档

```
/update_api_documentation
```

## 完整工作流示例

以下是一个完整的自动化工作流示例：

1. 用户触发文档生成:
   ```
   /start_api_doc_workflow project_path="/path/to/project"
   ```

2. 工具分析项目结构:
   ```
   /analyze_project_structure project_path="/path/to/project"
   ```

3. 获取分析结果:
   ```
   /get_analysis_result
   ```

4. 根据分析结果检索API路由:
   ```
   /retrieve_api_routes analysis_result={...}
   ```

5. 阅读相关代码文件:
   ```
   /read_api_code_files file_paths=["src/controllers/UserController.java", ...]
   ```

6. 获取阅读结果:
   ```
   /get_reading_result
   ```

7. 提取API信息:
   ```
   /extract_api_info code_reading_result={...}
   ```

8. 生成API文档:
   ```
   /generate_api_documentation api_info={...}
   ```

9. 检查文档完整性:
   ```
   /check_documentation_completeness api_doc="..." api_info={...}
   ```

10. 如有需要，更新文档:
    ```
    /update_api_documentation completeness_check_result={...}
    ```

## 生成的API文档示例

工具会生成如下格式的Markdown文档：

```markdown
# API文档

## 用户管理

### 获取用户列表
- **API地址**: `GET /api/users`
- **所属类**: `UserController`
- **功能描述**: 获取系统中的用户列表
- **是否需要鉴权**: 是

#### 请求参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| page | integer | 否 | 页码，默认为1 |
| size | integer | 否 | 每页大小，默认为10 |

#### 响应数据结构
| 字段名 | 类型 | 描述 |
|--------|------|------|
| id | long | 用户ID |
| name | string | 用户姓名 |
| email | string | 用户邮箱 |

#### 请求示例
```http
GET /api/users?page=1&size=10
Authorization: Bearer <token>
```

#### 响应示例
```json
[
  {
    "id": 1,
    "name": "张三",
    "email": "zhangsan@example.com"
  }
]
```
```

## 工作流状态监控

可以随时检查工作流状态：

```
/get_workflow_status
```

返回示例：
```json
{
  "project_path": "/path/to/project",
  "status": "generating_documentation",
  "current_step": "编写API文档",
  "progress": "5/8"
}
```