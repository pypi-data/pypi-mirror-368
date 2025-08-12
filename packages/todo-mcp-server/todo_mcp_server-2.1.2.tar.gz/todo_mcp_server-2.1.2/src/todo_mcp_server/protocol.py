#!/usr/bin/env python3
"""
MCP协议处理器
处理JSON-RPC 2.0消息的解析和响应
"""

import asyncio
import json
import logging
import sys
from typing import Any, Dict, Optional

from pydantic import BaseModel
from .server import TodoMCPServer


# MCP协议数据模型
class MCPRequest(BaseModel):
    jsonrpc: str = "2.0"
    id: Optional[str | int] = None
    method: str
    params: Optional[Dict[str, Any]] = None


class MCPResponse(BaseModel):
    jsonrpc: str = "2.0"
    id: Optional[str | int] = None
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None


class MCPProtocolHandler:
    """
    MCP协议处理器
    负责处理JSON-RPC 2.0消息和MCP协议规范
    """
    
    def __init__(self, server: TodoMCPServer):
        self.server = server
        self.logger = logging.getLogger("MCPProtocolHandler")
        self.initialized = False
    
    async def handle_request(self, request: MCPRequest) -> MCPResponse:
        """处理MCP请求"""
        try:
            # 处理不同类型的MCP方法
            if request.method == "initialize":
                return await self._handle_initialize(request)
            elif request.method == "initialized":
                return await self._handle_initialized(request)
            elif request.method == "tools/list":
                return await self._handle_list_tools(request)
            elif request.method == "tools/call":
                return await self._handle_call_tool(request)
            elif request.method == "resources/list":
                return await self._handle_list_resources(request)
            elif request.method == "resources/read":
                return await self._handle_read_resource(request)
            elif request.method == "prompts/list":
                return await self._handle_list_prompts(request)
            elif request.method == "prompts/get":
                return await self._handle_get_prompt(request)
            else:
                return MCPResponse(
                    id=request.id,
                    error={
                        "code": -32601,  # Method not found
                        "message": f"Method not found: {request.method}"
                    }
                )
        except Exception as e:
            self.logger.error(f"处理请求时出错: {e}")
            return MCPResponse(
                id=request.id,
                error={
                    "code": -32603,  # Internal error
                    "message": f"Internal error: {str(e)}"
                }
            )
    
    async def _handle_initialize(self, request: MCPRequest) -> MCPResponse:
        """处理初始化请求"""
        params = request.params or {}
        
        # 支持的MCP协议版本列表
        supported_versions = ["2024-11-05", "2025-06-18"]
        client_version = params.get("protocolVersion")
        
        # 选择兼容的协议版本
        if client_version in supported_versions:
            protocol_version = client_version
            self.logger.info(f"使用协议版本: {protocol_version}")
        else:
            # 使用默认版本并记录警告
            protocol_version = "2024-11-05"  # 使用Cursor的版本作为默认
            self.logger.warning(f"客户端协议版本 {client_version} 不受支持，使用默认版本 {protocol_version}")
        
        self.logger.info(f"初始化MCP连接，客户端: {params.get('clientInfo', {}).get('name', 'Unknown')}")
        
        return MCPResponse(
            id=request.id,
            result={
                "protocolVersion": protocol_version,
                "serverInfo": self.server.get_server_info(),
                "capabilities": self.server.get_capabilities()
            }
        )
    
    async def _handle_initialized(self, request: MCPRequest) -> MCPResponse:
        """处理初始化完成通知"""
        self.initialized = True
        self.logger.info("MCP初始化完成")
        # initialized是通知，不需要响应
        return MCPResponse(id=request.id, result={})
    
    async def _handle_list_tools(self, request: MCPRequest) -> MCPResponse:
        """处理工具列表请求"""
        tools = self.server.list_tools()
        return MCPResponse(
            id=request.id,
            result={"tools": tools}
        )
    
    async def _handle_call_tool(self, request: MCPRequest) -> MCPResponse:
        """处理工具调用请求"""
        if not self.initialized:
            return MCPResponse(
                id=request.id,
                error={
                    "code": -32002,  # Invalid request
                    "message": "Server not initialized"
                }
            )
        
        params = request.params or {}
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if not tool_name:
            return MCPResponse(
                id=request.id,
                error={
                    "code": -32602,  # Invalid params
                    "message": "Missing tool name"
                }
            )
        
        self.logger.info(f"调用工具: {tool_name} with {arguments}")
        
        # 调用工具并获取结果
        result_text = await self.server.call_tool(tool_name, arguments)
        
        return MCPResponse(
            id=request.id,
            result={
                "content": [
                    {
                        "type": "text",
                        "text": result_text
                    }
                ]
            }
        )
    
    async def _handle_list_resources(self, request: MCPRequest) -> MCPResponse:
        """处理资源列表请求"""
        resources = self.server.list_resources()
        return MCPResponse(
            id=request.id,
            result={"resources": resources}
        )
    
    async def _handle_read_resource(self, request: MCPRequest) -> MCPResponse:
        """处理资源读取请求"""
        params = request.params or {}
        uri = params.get("uri")
        
        if not uri:
            return MCPResponse(
                id=request.id,
                error={
                    "code": -32602,  # Invalid params
                    "message": "Missing resource URI"
                }
            )
        
        # 简化的资源读取实现
        if uri == "todo://tasks/stats":
            content = "📊 任务统计信息：\n- 总任务数: 10\n- 已完成: 6\n- 进行中: 3\n- 待开始: 1"
        elif uri == "todo://tasks/recent":
            content = "🕐 最近任务：\n- [1] 完成项目文档\n- [2] 代码评审\n- [3] 团队会议"
        elif uri == "todo://tasks/overdue":
            content = "⚠️ 逾期任务：\n- [5] 月度报告 (逾期2天)\n- [8] 客户反馈 (逾期1天)"
        else:
            return MCPResponse(
                id=request.id,
                error={
                    "code": -32602,  # Invalid params
                    "message": f"Unknown resource URI: {uri}"
                }
            )
        
        return MCPResponse(
            id=request.id,
            result={
                "contents": [
                    {
                        "uri": uri,
                        "mimeType": "text/plain",
                        "text": content
                    }
                ]
            }
        )
    
    async def _handle_list_prompts(self, request: MCPRequest) -> MCPResponse:
        """处理提示列表请求"""
        prompts = self.server.list_prompts()
        return MCPResponse(
            id=request.id,
            result={"prompts": prompts}
        )
    
    async def _handle_get_prompt(self, request: MCPRequest) -> MCPResponse:
        """处理获取提示请求"""
        params = request.params or {}
        prompt_name = params.get("name")
        
        if prompt_name == "task_summary":
            messages = [
                {
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": "请生成我的任务摘要报告，包括完成情况和优先级分析。"
                    }
                }
            ]
        elif prompt_name == "task_recommendations":
            messages = [
                {
                    "role": "user", 
                    "content": {
                        "type": "text",
                        "text": "基于我当前的任务情况，请提供任务管理和优化建议。"
                    }
                }
            ]
        else:
            return MCPResponse(
                id=request.id,
                error={
                    "code": -32602,  # Invalid params
                    "message": f"Unknown prompt: {prompt_name}"
                }
            )
        
        return MCPResponse(
            id=request.id,
            result={
                "description": f"Generated prompt for {prompt_name}",
                "messages": messages
            }
        )
    
    async def run(self):
        """运行MCP协议主循环"""
        self.logger.info("Todo MCP服务器启动，等待来自Cursor的连接...")
        
        try:
            # MCP服务器主循环（stdio传输）
            while True:
                try:
                    # 从stdin读取JSON-RPC消息
                    line = await asyncio.to_thread(sys.stdin.readline)
                    if not line:
                        break
                    
                    line = line.strip()
                    if not line:
                        continue
                    
                    # 解析JSON-RPC请求
                    try:
                        request_data = json.loads(line)
                        request = MCPRequest(**request_data)
                    except (json.JSONDecodeError, ValueError) as e:
                        self.logger.error(f"无效的JSON-RPC请求: {e}")
                        # 发送错误响应
                        error_response = MCPResponse(
                            error={
                                "code": -32700,  # Parse error
                                "message": "Parse error"
                            }
                        )
                        print(error_response.model_dump_json(), flush=True)
                        continue
                    
                    # 处理请求
                    response = await self.handle_request(request)
                    
                    # 发送响应到stdout
                    print(response.model_dump_json(), flush=True)
                
                except Exception as e:
                    self.logger.error(f"处理消息时出错: {e}")
                    # 发送内部错误响应
                    error_response = MCPResponse(
                        error={
                            "code": -32603,  # Internal error
                            "message": "Internal error"
                        }
                    )
                    print(error_response.model_dump_json(), flush=True)
        
        except KeyboardInterrupt:
            self.logger.info("收到中断信号，正在关闭服务器...")
        finally:
            await self.server.cleanup()
            self.logger.info("Todo MCP服务器已关闭")