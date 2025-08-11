#!/usr/bin/env python3
"""
Todo MCP Server - 核心服务器类
支持多用户配置和认证
"""

import logging
import sys
from typing import Any, Dict, List, Optional

import httpx
from pydantic import BaseModel


class TodoMCPServer:
    """
    Todo MCP服务器 - 支持多用户配置
    严格按照官方MCP规范实现
    """
    
    def __init__(
        self, 
        api_base_url: str,
        auth_headers: Optional[Dict[str, str]] = None,
        timeout: int = 30
    ):
        """初始化MCP服务器
        
        Args:
            api_base_url: Todo API服务器地址
            auth_headers: 认证头信息
            timeout: 请求超时时间（秒）
        """
        self.api_base_url = api_base_url.rstrip('/')
        self.auth_headers = auth_headers or {}
        self.timeout = timeout
        self.client = None
        self.capabilities = {
            "tools": {},
            "resources": {},
            "prompts": {}
        }
        
        # 配置日志到stderr（符合MCP规范）
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            stream=sys.stderr  # MCP服务器日志应该输出到stderr
        )
        self.logger = logging.getLogger("TodoMCPServer")
    
    async def initialize(self) -> None:
        """初始化HTTP客户端"""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "TodoMCPServer/1.0"
        }
        # 合并认证headers
        headers.update(self.auth_headers)
        
        self.client = httpx.AsyncClient(
            base_url=self.api_base_url,
            timeout=self.timeout,
            headers=headers
        )
        
        # 测试连接
        try:
            response = await self.client.get("/health")
            if response.status_code == 200:
                self.logger.info(f"成功连接到Todo API: {self.api_base_url}")
            else:
                self.logger.warning(f"Todo API连接异常，状态码: {response.status_code}")
        except Exception as e:
            self.logger.error(f"无法连接到Todo API: {e}")
    
    async def cleanup(self) -> None:
        """清理资源"""
        if self.client:
            await self.client.aclose()
    
    def get_server_info(self) -> Dict[str, Any]:
        """获取服务器信息（MCP规范要求）"""
        return {
            "name": "todo-mcp-server",
            "version": "1.0.1",
            "protocol_version": "2024-11-05"  # 使用Cursor兼容的版本
        }
    
    def get_capabilities(self) -> Dict[str, Any]:
        """获取服务器能力（MCP规范要求）"""
        return {
            "tools": {
                "list_changed": True  # 支持工具列表变更通知
            },
            "resources": {
                "subscribe": True,  # 支持资源订阅
                "list_changed": True
            },
            "prompts": {
                "list_changed": True
            }
        }
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """列出所有可用工具（MCP规范要求）"""
        return [
            {
                "name": "create_task",
                "description": "创建新的待办任务",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "任务标题"
                        },
                        "description": {
                            "type": "string", 
                            "description": "任务详细描述"
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["low", "medium", "high", "urgent"],
                            "description": "任务优先级"
                        },
                        "due_date": {
                            "type": "string",
                            "format": "date-time",
                            "description": "截止日期 (ISO 8601格式)"
                        }
                    },
                    "required": ["title"]
                }
            },
            {
                "name": "list_tasks",
                "description": "获取任务列表",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "status": {
                            "type": "string",
                            "enum": ["pending", "in_progress", "completed", "cancelled"],
                            "description": "过滤任务状态"
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["low", "medium", "high", "urgent"],
                            "description": "过滤任务优先级"
                        },
                        "limit": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 100,
                            "default": 20,
                            "description": "返回任务数量限制"
                        }
                    }
                }
            },
            {
                "name": "get_task",
                "description": "获取特定任务的详细信息",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "integer",
                            "description": "任务ID"
                        }
                    },
                    "required": ["task_id"]
                }
            },
            {
                "name": "update_task",
                "description": "更新任务信息",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "integer",
                            "description": "任务ID"
                        },
                        "title": {
                            "type": "string",
                            "description": "新的任务标题"
                        },
                        "description": {
                            "type": "string",
                            "description": "新的任务描述"
                        },
                        "status": {
                            "type": "string",
                            "enum": ["pending", "in_progress", "completed", "cancelled"],
                            "description": "新的任务状态"
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["low", "medium", "high", "urgent"],
                            "description": "新的任务优先级"
                        }
                    },
                    "required": ["task_id"]
                }
            },
            {
                "name": "delete_task",
                "description": "删除任务",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "integer",
                            "description": "要删除的任务ID"
                        }
                    },
                    "required": ["task_id"]
                }
            },
            {
                "name": "search_tasks",
                "description": "搜索任务",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "搜索关键词"
                        },
                        "fields": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": ["title", "description"]
                            },
                            "description": "搜索字段范围"
                        }
                    },
                    "required": ["query"]
                }
            }
        ]
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """列出所有可用资源（MCP规范要求）"""
        return [
            {
                "uri": "todo://tasks/stats",
                "name": "任务统计",
                "description": "获取任务统计信息",
                "mimeType": "application/json"
            },
            {
                "uri": "todo://tasks/recent",
                "name": "最近任务",
                "description": "最近创建或更新的任务",
                "mimeType": "application/json"
            },
            {
                "uri": "todo://tasks/overdue",
                "name": "逾期任务",
                "description": "所有逾期任务",
                "mimeType": "application/json"
            }
        ]
    
    def list_prompts(self) -> List[Dict[str, Any]]:
        """列出所有可用提示（MCP规范要求）"""
        return [
            {
                "name": "task_summary",
                "description": "生成任务摘要报告",
                "arguments": [
                    {
                        "name": "period",
                        "description": "时间范围",
                        "required": False
                    }
                ]
            },
            {
                "name": "task_recommendations",
                "description": "任务优化建议"
            }
        ]
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> str:
        """调用指定工具"""
        try:
            if name == "create_task":
                return await self._create_task(**arguments)
            elif name == "list_tasks":
                return await self._list_tasks(**arguments)
            elif name == "get_task":
                return await self._get_task(**arguments)
            elif name == "update_task":
                return await self._update_task(**arguments)
            elif name == "delete_task":
                return await self._delete_task(**arguments)
            elif name == "search_tasks":
                return await self._search_tasks(**arguments)
            else:
                return f"未知工具: {name}"
        except Exception as e:
            self.logger.error(f"调用工具 {name} 时出错: {e}")
            return f"调用工具时出错: {str(e)}"
    
    async def _create_task(self, title: str, description: str = "", priority: str = "medium", due_date: str = None) -> str:
        """创建新任务"""
        # 转换priority为数字
        priority_map = {"low": 0, "medium": 1, "high": 2, "urgent": 3}
        priority_num = priority_map.get(priority.lower(), 1)
        
        payload = {
            "title": title,
            "description": description,
            "priority": priority_num
        }
        if due_date:
            payload["due_date"] = due_date
        
        response = await self.client.post("/api/v1/todo/tasks", json=payload)
        if response.status_code == 201:
            task_data = response.json()
            return f"✅ 任务创建成功！\n任务ID: {task_data['id']}\n标题: {task_data['title']}\n优先级: {task_data['priority']}"
        else:
            return f"❌ 创建任务失败: {response.text}"
    
    async def _list_tasks(self, status: str = None, priority: str = None, limit: int = 20) -> str:
        """获取任务列表"""
        params = {"limit": limit}
        if status:
            params["status"] = status
        if priority:
            params["priority"] = priority
        
        response = await self.client.get("/api/v1/todo/tasks", params=params)
        if response.status_code == 200:
            tasks = response.json()
            if not tasks:
                return "📝 暂无任务"
            
            result = f"📋 任务列表 (共{len(tasks)}个):\n\n"
            for task in tasks:
                status_emoji = {"pending": "⏳", "in_progress": "🔄", "completed": "✅", "cancelled": "❌"}.get(task['status'], "📝")
                priority_emoji = {"low": "🟢", "medium": "🟡", "high": "🟠", "urgent": "🔴"}.get(task['priority'], "⚪")
                result += f"{status_emoji} [{task['id']}] {priority_emoji} {task['title']}\n"
                if task.get('description'):
                    result += f"   💬 {task['description']}\n"
                result += "\n"
            
            return result.strip()
        else:
            return f"❌ 获取任务列表失败: {response.text}"
    
    # 其他工具方法的实现...
    async def _get_task(self, task_id: int) -> str:
        """获取任务详情"""
        response = await self.client.get(f"/api/v1/todo/tasks/{task_id}")
        if response.status_code == 200:
            task = response.json()
            status_emoji = {"pending": "⏳", "in_progress": "🔄", "completed": "✅", "cancelled": "❌"}.get(task['status'], "📝")
            priority_emoji = {"low": "🟢", "medium": "🟡", "high": "🟠", "urgent": "🔴"}.get(task['priority'], "⚪")
            
            result = f"📋 任务详情:\n\n"
            result += f"🆔 ID: {task['id']}\n"
            result += f"📝 标题: {task['title']}\n"
            result += f"{status_emoji} 状态: {task['status']}\n"
            result += f"{priority_emoji} 优先级: {task['priority']}\n"
            
            if task.get('description'):
                result += f"💬 描述: {task['description']}\n"
            if task.get('due_date'):
                result += f"📅 截止日期: {task['due_date']}\n"
            if task.get('created_at'):
                result += f"🕐 创建时间: {task['created_at']}\n"
            
            return result
        else:
            return f"❌ 获取任务详情失败: {response.text}"
    
    async def _update_task(self, task_id: int, **kwargs) -> str:
        """更新任务"""
        # 只传递非空参数
        payload = {k: v for k, v in kwargs.items() if v is not None}
        
        response = await self.client.put(f"/api/v1/todo/tasks/{task_id}", json=payload)
        if response.status_code == 200:
            task = response.json()
            return f"✅ 任务更新成功！\n任务ID: {task['id']}\n标题: {task['title']}\n状态: {task['status']}"
        else:
            return f"❌ 更新任务失败: {response.text}"
    
    async def _delete_task(self, task_id: int) -> str:
        """删除任务"""
        response = await self.client.delete(f"/api/v1/todo/tasks/{task_id}")
        if response.status_code == 200:
            return f"✅ 任务 {task_id} 删除成功！"
        else:
            return f"❌ 删除任务失败: {response.text}"
    
    async def _search_tasks(self, query: str, fields: List[str] = None) -> str:
        """搜索任务"""
        params = {"q": query}
        if fields:
            params["fields"] = ",".join(fields)
        
        response = await self.client.get("/api/v1/todo/tasks/search", params=params)
        if response.status_code == 200:
            tasks = response.json()
            if not tasks:
                return f"🔍 未找到包含 '{query}' 的任务"
            
            result = f"🔍 搜索结果 ('{query}', 共{len(tasks)}个):\n\n"
            for task in tasks:
                status_emoji = {"pending": "⏳", "in_progress": "🔄", "completed": "✅", "cancelled": "❌"}.get(task['status'], "📝")
                priority_emoji = {"low": "🟢", "medium": "🟡", "high": "🟠", "urgent": "🔴"}.get(task['priority'], "⚪")
                result += f"{status_emoji} [{task['id']}] {priority_emoji} {task['title']}\n"
                if task.get('description'):
                    result += f"   💬 {task['description']}\n"
                result += "\n"
            
            return result.strip()
        else:
            return f"❌ 搜索任务失败: {response.text}"