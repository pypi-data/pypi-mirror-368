#!/usr/bin/env python3
"""
Todo MCP Server - FastMCP版本

基于FastMCP框架的现代化Todo管理MCP服务器
支持任务的创建、查询、更新、删除等完整功能

Usage:
    todo-mcp-server --api-url=http://localhost:3000 --api-token=your-token

Features:
    - 6个工具：创建、列表、获取、更新、删除、搜索任务
    - 3个资源：任务详情、任务列表、健康状态
    - 2个提示：任务创建助手、任务总结模板
    - 多种认证：Bearer Token、Basic Auth、Gateway Headers
    - 自动协议版本兼容
"""

import argparse
import asyncio
import logging
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any

import httpx
from fastmcp import FastMCP
from pydantic import BaseModel, Field

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ===== FastMCP服务器初始化 =====
mcp = FastMCP("Todo Management System")

# ===== 数据模型 =====
class TaskModel(BaseModel):
    """任务数据模型"""
    id: int
    title: str
    description: str = ""
    status: str = "pending"
    priority: int = 1
    due_date: Optional[str] = None
    created_at: str
    updated_at: str

class TaskCreateRequest(BaseModel):
    """创建任务请求模型"""
    title: str = Field(description="任务标题")
    description: str = Field(default="", description="任务详细描述")
    priority: str = Field(default="medium", description="任务优先级：low, medium, high, urgent")
    due_date: Optional[str] = Field(default=None, description="截止日期 (ISO 8601格式)")

class TaskUpdateRequest(BaseModel):
    """更新任务请求模型"""
    task_id: int = Field(description="任务ID")
    title: Optional[str] = Field(default=None, description="新的任务标题")
    description: Optional[str] = Field(default=None, description="新的任务描述")
    status: Optional[str] = Field(default=None, description="新的任务状态：pending, in_progress, completed, cancelled")
    priority: Optional[str] = Field(default=None, description="新的任务优先级：low, medium, high, urgent")

# ===== 全局配置 =====
class TodoAPIClient:
    """Todo API客户端"""
    
    def __init__(self, api_url: str, auth_headers: Dict[str, str], timeout: int = 30):
        self.api_url = api_url.rstrip('/')
        self.auth_headers = auth_headers
        self.timeout = timeout
        self.client = httpx.AsyncClient(
            headers=auth_headers,
            timeout=timeout,
            follow_redirects=True
        )
        logger.info(f"📡 连接到: {self.api_url}")
        
    async def close(self):
        """关闭HTTP客户端"""
        if self.client:
            await self.client.aclose()
    
    async def health_check(self) -> bool:
        """检查API健康状态"""
        try:
            response = await self.client.get(f"{self.api_url}/todo-api/v1/public/health")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"健康检查失败: {e}")
            return False

# 全局API客户端实例
api_client: Optional[TodoAPIClient] = None

def create_auth_headers(args) -> Dict[str, str]:
    """创建认证头"""
    headers = {}
    if args.api_token:
        # 使用Bearer Token认证（适用于apikey端点）
        headers["Authorization"] = f"Bearer {args.api_token}"
        logger.info("🔐 认证方式: Bearer Token")
    elif args.username and args.password:
        import base64
        credentials = base64.b64encode(f"{args.username}:{args.password}".encode()).decode()
        headers["Authorization"] = f"Basic {credentials}"
        logger.info("🔐 认证方式: Basic Auth")
    return headers

# ===== MCP工具定义 =====

@mcp.tool()
async def create_task(title: str, description: str = "", priority: str = "medium", due_date: Optional[str] = None) -> str:
    """创建新的待办任务
    
    Args:
        title: 任务标题
        description: 任务详细描述
        priority: 任务优先级 (low, medium, high, urgent)
        due_date: 截止日期 (ISO 8601格式)
    
    Returns:
        创建结果的详细信息
    """
    if not api_client:
        return "❌ API客户端未初始化"
    
    # 转换优先级字符串为数字
    priority_map = {"low": 0, "medium": 1, "high": 2, "urgent": 3}
    priority_num = priority_map.get(priority.lower(), 1)
    
    payload = {
        "title": title,
        "description": description,
        "priority": priority_num
    }
    
    if due_date:
        payload["due_date"] = due_date
    
    try:
        response = await api_client.client.post(
            f"{api_client.api_url}/todo-api/v1/apikey/tasks",
            json=payload
        )
        
        if response.status_code == 201:
            task_data = response.json()
            return f"✅ 任务创建成功！\n任务ID: {task_data['id']}\n标题: {task_data['title']}\n优先级: {task_data['priority']}"
        else:
            return f"❌ 创建任务失败: {response.text}"
            
    except Exception as e:
        return f"❌ 创建任务异常: {str(e)}"

@mcp.tool()
async def list_tasks(status: Optional[str] = None, priority: Optional[str] = None, limit: int = 20) -> str:
    """获取任务列表
    
    Args:
        status: 过滤任务状态 (pending, in_progress, completed, cancelled)
        priority: 过滤任务优先级 (low, medium, high, urgent)
        limit: 返回任务数量限制 (1-100)
    
    Returns:
        任务列表的格式化字符串
    """
    if not api_client:
        return "❌ API客户端未初始化"
    
    # 构建查询参数
    params = {"limit": min(limit, 100)}
    if status:
        params["status"] = status
    if priority:
        priority_map = {"low": 0, "medium": 1, "high": 2, "urgent": 3}
        if priority.lower() in priority_map:
            params["priority"] = priority_map[priority.lower()]
    
    try:
        response = await api_client.client.get(
            f"{api_client.api_url}/todo-api/v1/apikey/tasks",
            params=params
        )
        
        if response.status_code == 200:
            data = response.json()
            # 处理分页格式的API响应
            if isinstance(data, dict) and 'items' in data:
                tasks = data['items']
                total = data.get('total', len(tasks))
            else:
                tasks = data if isinstance(data, list) else []
                total = len(tasks)
            
            if not tasks:
                return "📝 没有找到任务"
            
            result = f"📋 找到 {len(tasks)} 个任务 (共{total}个):\n\n"
            for task in tasks:
                priority_labels = ["低", "中", "高", "紧急"]
                priority_label = priority_labels[task.get('priority', 1)]
                
                result += f"🆔 ID: {task['id']}\n"
                result += f"📌 标题: {task['title']}\n"
                result += f"📊 状态: {task['status']}\n"
                result += f"⚡ 优先级: {priority_label}\n"
                if task.get('due_date'):
                    result += f"⏰ 截止日期: {task['due_date']}\n"
                result += f"📅 创建时间: {task['created_at']}\n\n"
            
            return result
        else:
            return f"❌ 获取任务失败: {response.text}"
            
    except Exception as e:
        return f"❌ 获取任务异常: {str(e)}"

@mcp.tool()  
async def get_task(task_id: int) -> str:
    """获取特定任务的详细信息
    
    Args:
        task_id: 任务ID
    
    Returns:
        任务详细信息的格式化字符串
    """
    if not api_client:
        return "❌ API客户端未初始化"
    
    try:
        response = await api_client.client.get(
            f"{api_client.api_url}/todo-api/v1/apikey/tasks/{task_id}"
        )
        
        if response.status_code == 200:
            task = response.json()
            priority_labels = ["低", "中", "高", "紧急"]
            priority_label = priority_labels[task.get('priority', 1)]
            
            result = f"📋 任务详情:\n\n"
            result += f"🆔 ID: {task['id']}\n"
            result += f"📌 标题: {task['title']}\n"
            result += f"📝 描述: {task.get('description', '无')}\n"
            result += f"📊 状态: {task['status']}\n"
            result += f"⚡ 优先级: {priority_label}\n"
            if task.get('due_date'):
                result += f"⏰ 截止日期: {task['due_date']}\n"
            result += f"📅 创建时间: {task['created_at']}\n"
            result += f"🔄 更新时间: {task['updated_at']}\n"
            
            return result
        elif response.status_code == 404:
            return f"❌ 任务 {task_id} 不存在"
        else:
            return f"❌ 获取任务失败: {response.text}"
            
    except Exception as e:
        return f"❌ 获取任务异常: {str(e)}"

@mcp.tool()
async def update_task(task_id: int, title: Optional[str] = None, description: Optional[str] = None, 
                     status: Optional[str] = None, priority: Optional[str] = None) -> str:
    """更新任务信息
    
    Args:
        task_id: 任务ID
        title: 新的任务标题
        description: 新的任务描述
        status: 新的任务状态 (pending, in_progress, completed, cancelled)
        priority: 新的任务优先级 (low, medium, high, urgent)
    
    Returns:
        更新结果的详细信息
    """
    if not api_client:
        return "❌ API客户端未初始化"
    
    # 构建更新数据
    payload = {}
    if title is not None:
        payload["title"] = title
    if description is not None:
        payload["description"] = description
    if status is not None:
        payload["status"] = status
    if priority is not None:
        priority_map = {"low": 0, "medium": 1, "high": 2, "urgent": 3}
        payload["priority"] = priority_map.get(priority.lower(), 1)
    
    if not payload:
        return "❌ 没有提供要更新的字段"
    
    try:
        response = await api_client.client.put(
            f"{api_client.api_url}/todo-api/v1/apikey/tasks/{task_id}",
            json=payload
        )
        
        if response.status_code == 200:
            task_data = response.json()
            return f"✅ 任务更新成功！\n任务ID: {task_data['id']}\n标题: {task_data['title']}\n状态: {task_data['status']}"
        elif response.status_code == 404:
            return f"❌ 任务 {task_id} 不存在"
        else:
            return f"❌ 更新任务失败: {response.text}"
            
    except Exception as e:
        return f"❌ 更新任务异常: {str(e)}"

@mcp.tool()
async def delete_task(task_id: int) -> str:
    """删除任务
    
    Args:
        task_id: 要删除的任务ID
    
    Returns:
        删除结果信息
    """
    if not api_client:
        return "❌ API客户端未初始化"
    
    try:
        response = await api_client.client.delete(
            f"{api_client.api_url}/todo-api/v1/apikey/tasks/{task_id}"
        )
        
        if response.status_code == 200:
            return f"✅ 任务 {task_id} 删除成功"
        elif response.status_code == 404:
            return f"❌ 任务 {task_id} 不存在"
        else:
            return f"❌ 删除任务失败: {response.text}"
            
    except Exception as e:
        return f"❌ 删除任务异常: {str(e)}"

@mcp.tool()
async def search_tasks(query: str, fields: Optional[List[str]] = None) -> str:
    """搜索任务
    
    Args:
        query: 搜索关键词
        fields: 搜索字段范围 (title, description)
    
    Returns:
        搜索结果的格式化字符串
    """
    if not api_client:
        return "❌ API客户端未初始化"
    
    params = {"q": query}
    if fields:
        params["fields"] = ",".join(fields)
    
    try:
        response = await api_client.client.get(
            f"{api_client.api_url}/todo-api/v1/apikey/tasks/search",
            params=params
        )
        
        if response.status_code == 200:
            data = response.json()
            # 处理分页格式的API响应
            if isinstance(data, dict) and 'items' in data:
                tasks = data['items']
                total = data.get('total', len(tasks))
            else:
                tasks = data if isinstance(data, list) else []
                total = len(tasks)
            
            if not tasks:
                return f"🔍 没有找到包含 '{query}' 的任务"
            
            result = f"🔍 搜索 '{query}' 找到 {len(tasks)} 个任务 (共{total}个):\n\n"
            for task in tasks:
                priority_labels = ["低", "中", "高", "紧急"]
                priority_label = priority_labels[task.get('priority', 1)]
                
                result += f"🆔 ID: {task['id']}\n"
                result += f"📌 标题: {task['title']}\n"
                result += f"📊 状态: {task['status']}\n"
                result += f"⚡ 优先级: {priority_label}\n\n"
            
            return result
        else:
            return f"❌ 搜索任务失败: {response.text}"
            
    except Exception as e:
        return f"❌ 搜索任务异常: {str(e)}"

# ===== MCP资源定义 =====

@mcp.resource("todo://task/{task_id}")
async def get_task_resource(task_id: str) -> str:
    """获取任务资源数据"""
    if not api_client:
        return "API客户端未初始化"
    
    try:
        task_id_int = int(task_id)
        response = await api_client.client.get(
            f"{api_client.api_url}/todo-api/v1/apikey/tasks/{task_id_int}"
        )
        
        if response.status_code == 200:
            return response.text
        else:
            return f"获取任务失败: {response.text}"
            
    except Exception as e:
        return f"获取任务异常: {str(e)}"

@mcp.resource("todo://tasks")
async def get_tasks_resource() -> str:
    """获取任务列表资源"""
    if not api_client:
        return "API客户端未初始化"
    
    try:
        response = await api_client.client.get(
            f"{api_client.api_url}/todo-api/v1/apikey/tasks",
            params={"limit": 50}
        )
        
        if response.status_code == 200:
            return response.text
        else:
            return f"获取任务列表失败: {response.text}"
            
    except Exception as e:
        return f"获取任务列表异常: {str(e)}"

@mcp.resource("todo://health")
async def get_health_resource() -> str:
    """获取系统健康状态"""
    if not api_client:
        return '{"status": "error", "message": "API客户端未初始化"}'
    
    try:
        response = await api_client.client.get(f"{api_client.api_url}/todo-api/v1/public/health")
        if response.status_code == 200:
            return response.text
        else:
            return f'{{"status": "error", "message": "健康检查失败: {response.text}"}}'
            
    except Exception as e:
        return f'{{"status": "error", "message": "健康检查异常: {str(e)}"}}'

# ===== MCP提示定义 =====

@mcp.prompt("task_creation_helper")
async def task_creation_helper(context: str = "") -> str:
    """任务创建助手提示模板
    
    Args:
        context: 相关上下文信息
    
    Returns:
        格式化的提示文本
    """
    return f"""
你是一个专业的任务管理助手。请帮助用户创建结构化的待办任务。

上下文信息: {context}

在创建任务时，请考虑以下要素：
1. 📌 标题：简洁明确的任务名称
2. 📝 描述：详细的任务说明和要求
3. ⚡ 优先级：根据重要性和紧急性设置（low/medium/high/urgent）
4. ⏰ 截止日期：如果有时间要求，设置合理的截止日期

请确保：
- 标题不超过100个字符
- 描述提供足够的执行细节
- 优先级设置合理
- 截止日期格式正确（ISO 8601格式）

现在请基于用户需求创建任务。
"""

@mcp.prompt("task_summary")
async def task_summary_prompt(tasks_data: str) -> str:
    """任务总结提示模板
    
    Args:
        tasks_data: 任务数据JSON字符串
    
    Returns:
        格式化的总结提示
    """
    return f"""
请分析以下任务数据并生成专业的任务总结报告：

任务数据：
{tasks_data}

请提供以下内容的总结：
1. 📊 任务概览：总数量、状态分布
2. ⚡ 优先级分析：各优先级任务数量
3. 📈 进度分析：完成率、待处理数量
4. ⚠️ 风险提醒：逾期任务、高优先级待处理任务
5. 💡 建议：基于当前状态的行动建议

请以清晰、专业的方式组织信息，使用合适的表情符号增强可读性。
"""

# ===== 主程序 =====

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="Todo MCP Server powered by FastMCP",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 使用API Token认证
  todo-mcp-server --api-url=https://my-todo.com:3000 --api-token=abc123

  # 使用用户名密码认证
  todo-mcp-server --api-url=https://my-todo.com:3000 --username=john --password=secret

  # 本地开发
  todo-mcp-server --api-url=http://localhost:3000 --api-token=dev-token

Cursor配置示例:
  {
    "mcpServers": {
      "my-todo": {
        "command": "uvx",
        "args": [
          "todo-mcp-server",
          "--api-url=https://your-server.com:3000",
          "--api-token=your-token"
        ]
      }
    }
  }
        """
    )
    
    parser.add_argument("--api-url", required=True, help="Todo API服务器URL (例: https://your-server.com:3000)")
    parser.add_argument("--api-token", help="API访问令牌 (Bearer Token认证)")
    parser.add_argument("--username", help="用户名 (Basic认证)")
    parser.add_argument("--password", help="密码 (Basic认证)")
    parser.add_argument("--timeout", type=int, default=30, help="HTTP请求超时时间（秒，默认30）")
    parser.add_argument("--version", action="version", version="%(prog)s 2.0.2")
    parser.add_argument("--debug", action="store_true", help="启用调试日志")
    
    return parser.parse_args()

async def initialize_api_client(args):
    """初始化API客户端"""
    global api_client
    
    auth_headers = create_auth_headers(args)
    api_client = TodoAPIClient(args.api_url, auth_headers, args.timeout)
    
    # 健康检查
    logger.info("⏱️ 超时时间: %d秒", args.timeout)
    logger.info("正在进行健康检查...")
    
    if await api_client.health_check():
        logger.info("✅ 成功连接到Todo API: %s", args.api_url)
    else:
        logger.error("❌ 无法连接到Todo API: %s", args.api_url)
        sys.exit(1)

def main():
    """主函数"""
    args = parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("🐛 调试模式已启用")
    
    print("🚀 启动Todo MCP服务器 (FastMCP版)")
    
    # 同步初始化API客户端
    asyncio.run(initialize_api_client(args))
    
    print("等待来自Cursor的连接...")
    
    # 启动FastMCP服务器（同步调用）
    mcp.run()

def cli_main():
    """CLI入口点（供setuptools使用）"""
    try:
        main()
    except KeyboardInterrupt:
        logger.info("👋 服务器关闭")
        sys.exit(0)
    except Exception as e:
        logger.error("❌ 启动失败: %s", e)
        sys.exit(1)

if __name__ == "__main__":
    cli_main()