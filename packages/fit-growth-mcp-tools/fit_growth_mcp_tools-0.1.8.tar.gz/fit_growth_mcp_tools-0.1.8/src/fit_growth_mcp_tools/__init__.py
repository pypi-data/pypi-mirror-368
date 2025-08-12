#!/usr/bin/env python3
#!/usr/bin/env python3
"""
简化版MCP服务器：向指定端口发送POST请求

这个服务器手动实现了MCP协议，不依赖mcp包，
用于向本地9000端口的服务器发送POST请求。

使用方法：
- 本地运行: python simple_mcp_server.py
- Claude Desktop配置中使用
"""

import asyncio
from datetime import datetime
import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional

import requests

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 目标服务器配置
TARGET_SERVER_URL = "http://9.135.101.171.devcloud.woa.com:8002"

# 从环境变量获取API令牌
SCHEMA_API_TOKEN = os.getenv("SCHEMA_API_TOKEN", "")
SQL_API_TOKEN = os.getenv("SQL_API_TOKEN", "")


class MCPServer:
    """简化的MCP服务器实现"""
    
    def __init__(self):
        self.capabilities = {
            "tools": {"listChanged": True},
            "resources": {},
            "prompts": {}
        }
        
    async def handle_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """处理MCP消息"""
        method = message.get("method")
        params = message.get("params", {})
        message_id = message.get("id")
        
        logger.info(f"收到消息: {method}")
        
        try:
            if method == "initialize":
                return await self.handle_initialize(message_id, params)
            elif method == "notifications/initialized":
                return None  # 不需要响应
            elif method == "tools/list":
                return await self.handle_tools_list(message_id)
            elif method == "tools/call":
                return await self.handle_tool_call(message_id, params)
            elif method == "resources/list":
                return await self.handle_resources_list(message_id)
            elif method == "resources/read":
                return await self.handle_resource_read(message_id, params)
            elif method == "prompts/list":
                return await self.handle_prompts_list(message_id)
            elif method == "prompts/get":
                return await self.handle_prompt_get(message_id, params)
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": message_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
        except Exception as e:
            logger.error(f"处理消息时出错: {e}")
            return {
                "jsonrpc": "2.0",
                "id": message_id,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
    
    async def handle_initialize(self, message_id: int, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理初始化请求"""
        return {
            "jsonrpc": "2.0",
            "id": message_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": self.capabilities,
                "serverInfo": {
                    "name": "SQL Query MCP Server",
                    "version": "1.0.0"
                }
            }
        }
    
    async def handle_tools_list(self, message_id: int) -> Dict[str, Any]:
        """列出可用工具"""
        tools = [
            {
                "name": "get_sql_schema",
                "description": "获取SQL数据口径信息。根据用户需求，分析需要用到的数据表、字段、枚举值、关联方式和易错点等信息",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "用户需要提取的数据需求，比如'查询理财通2025年6月1日的保有量'或'统计理财通2025年6月1日的股混申购金额'"
                        } 
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "execute_sql_query",
                "description": "可执行理财通相关的SQL代码，获取数据结果",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "要执行的SQL代码，比如'select * from user_table where date = '2025-06-01' limit 10'"
                        } 
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "check_server_status",
                "description": "检查目标服务器的状态",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "get_current_time",
                "description": "获取当前系统时间，返回yyyyMMdd HH:mm:SS格式，对于用户涉及“今天“，”昨天“”，”“近xx天”、“上个月”等模糊时间描述时，建议先调用本工具获取当前时间，再由AI推算出具体的日期范围后用于SQL查询",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            }
        ]
        
        return {
            "jsonrpc": "2.0",
            "id": message_id,
            "result": {
                "tools": tools
            }
        }
    
    async def handle_tool_call(self, message_id: int, params: Dict[str, Any]) -> Dict[str, Any]:
        """执行工具调用"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if tool_name == "get_sql_schema":
            result = await self.get_sql_schema(arguments)
        elif tool_name == "execute_sql_query":
            result = await self.execute_sql_query(arguments)
        elif tool_name == "check_server_status":
            result = await self.check_server_status()
        elif tool_name == "get_current_time":
            result = await self.get_current_time()
        else:
            return {
                "jsonrpc": "2.0",
                "id": message_id,
                "error": {
                    "code": -32602,
                    "message": f"Unknown tool: {tool_name}"
                }
            }
        
        return {
            "jsonrpc": "2.0",
            "id": message_id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result, ensure_ascii=False, indent=2)
                    }
                ]
            }
        }
    
    async def handle_resources_list(self, message_id: int) -> Dict[str, Any]:
        """列出可用资源"""
        resources = [
            {
                "uri": "config://server",
                "name": "SQL服务器配置",
                "description": "获取SQL查询服务器的配置信息，包括支持的端点、功能特性和工具说明",
                "mimeType": "application/json"
            }
        ]
        
        return {
            "jsonrpc": "2.0",
            "id": message_id,
            "result": {
                "resources": resources
            }
        }
    
    async def handle_resource_read(self, message_id: int, params: Dict[str, Any]) -> Dict[str, Any]:
        """读取资源内容"""
        uri = params.get("uri")
        
        if uri == "config://server":
            config = {
                "server_name": "SQL Query MCP Server",
                "target_url": TARGET_SERVER_URL,
                "supported_endpoints": ["/api/schema/query", "/api/sql/query", "/health"],
                "request_timeouts": {
                    "schema_query": "60秒",
                    "sql_query": "120秒",
                    "health_check": "10秒"
                },
                "features": [
                    "SQL数据口径查询 - 获取数据表、字段、枚举值等信息",
                    "SQL代码执行 - 执行SQL查询并获取结果",
                    "错误处理和重试机制"
                ],
                "tools": [
                    {
                        "name": "get_sql_schema",
                        "purpose": "根据用户需求分析查询所需要的数据表结构和字段信息"
                    },
                    {
                        "name": "execute_sql_query", 
                        "purpose": "执行SQL代码并返回查询结果"
                    },
                    {
                        "name": "check_server_status",
                        "purpose": "检查后端SQL服务器的运行状态"
                    }
                ]
            }
            content = json.dumps(config, ensure_ascii=False, indent=2)
        else:
            return {
                "jsonrpc": "2.0",
                "id": message_id,
                "error": {
                    "code": -32602,
                    "message": f"Unknown resource: {uri}"
                }
            }
        
        return {
            "jsonrpc": "2.0",
            "id": message_id,
            "result": {
                "contents": [
                    {
                        "uri": uri,
                        "mimeType": "application/json",
                        "text": content
                    }
                ]
            }
        }
    
    async def handle_prompts_list(self, message_id: int) -> Dict[str, Any]:
        """列出可用提示"""
        prompts = [
            {
                "name": "usage_example",
                "description": "生成SQL服务器使用示例的提示",
                "arguments": [
                    {
                        "name": "query_example",
                        "description": "示例业务查询需求",
                        "required": False
                    },
                    {
                        "name": "sql_example",
                        "description": "示例SQL代码",
                        "required": False
                    }
                ]
            }
        ]
        
        return {
            "jsonrpc": "2.0",
            "id": message_id,
            "result": {
                "prompts": prompts
            }
        }
    
    async def handle_prompt_get(self, message_id: int, params: Dict[str, Any]) -> Dict[str, Any]:
        """获取提示内容"""
        name = params.get("name")
        arguments = params.get("arguments", {})
        
        if name == "usage_example":
            schema_example = arguments.get("query_example", "查询理财通2025年6月1日的保有量")
            sql_example = arguments.get("sql_example", "SELECT * FROM user_table WHERE date = '2025-06-01' LIMIT 10")
            
            prompt_text = f"""
以下是如何使用SQL Query MCP Server的示例：

🔍 1. 获取SQL数据口径信息：
   - 工具名称: get_sql_schema
   - 参数:
     * query: "{schema_example}"
   - 功能: 根据业务需求分析所需的数据表、字段、枚举值、关联方式等信息

⚡ 2. 执行SQL查询：
   - 工具名称: execute_sql_query
   - 参数:
     * query: "{sql_example}"
   - 功能: 根据生成的sql，执行SQL代码并返回查询结果

⏰ 3. 获取当前系统时间（时间工具）：
   - 工具名称: get_current_time
   - 无需参数
   - 功能: 获取服务器当前时间。对于用户涉及“近xx天”、“上个月”等模糊时间描述时，建议先调用本工具获取当前时间，再由AI推算出具体的日期范围后用于SQL查询。

🏥 4. 检查服务器状态：
   - 工具名称: check_server_status
   - 无需参数
   - 功能: 检查后端SQL服务器是否正常运行

📊 5. 获取服务器配置：
   - 资源名称: config://server
   - 功能: 查看服务器配置、支持的端点和功能特性

💡 使用建议：
- 先使用 get_sql_schema 了解数据结构，再使用 execute_sql_query 执行查询
- 当用户需求中出现“近xx天”、“上个月”等模糊时间描述时，先调用 get_current_time 获取当前时间，再推算出具体的起止日期
- 支持的后端API端点: {TARGET_SERVER_URL}/api/schema/query 和 {TARGET_SERVER_URL}/api/sql/query
- 请确保目标服务器 ({TARGET_SERVER_URL}) 正在运行并提供SQL服务
"""
        else:
            return {
                "jsonrpc": "2.0",
                "id": message_id,
                "error": {
                    "code": -32602,
                    "message": f"Unknown prompt: {name}"
                }
            }
        
        return {
            "jsonrpc": "2.0",
            "id": message_id,
            "result": {
                "description": "MCP Post Request Server使用示例",
                "messages": [
                    {
                        "role": "user",
                        "content": {
                            "type": "text",
                            "text": prompt_text
                        }
                    }
                ]
            }
        }
    
    async def get_sql_schema(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """获取SQL数据口径信息"""
        query = arguments.get("query", "")
        token = arguments.get("token", SCHEMA_API_TOKEN)
        
        endpoint = "/api/schema/query"
        full_url = f"{TARGET_SERVER_URL}{endpoint}"
        
        request_data = {
            "query": query,
            "extra_result_params": []
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        
        if not token:
            logger.warning("Schema API Token 未设置，请设置环境变量 SCHEMA_API_TOKEN 或在调用时提供token参数")
        
        try:
            logger.info(f"正在向 {full_url} 请求SQL数据口径信息")
            logger.info(f"请求参数: {request_data}")
            
            response = requests.post(full_url, json=request_data, headers=headers, timeout=60.0)
            
            result = {
                "success": True,
                #"status_code": response.status_code,
                #"endpoint": endpoint,
                #"request_data": request_data,
                #"response_time_ms": response.elapsed.total_seconds() * 1000 if response.elapsed else None
            }
            
            try:
                response_data = response.json()
                result["schema_info"] = response_data
                # 如果有特定的answer字段，单独提取
                if isinstance(response_data, dict) and "data" in response_data :
                    result["answer"] = response_data["data"]
                elif isinstance(response_data, dict) and "data" in response_data and "answer" in response_data["data"]:
                    result["answer"] = response_data["data"]["answer"]
            except ValueError:
                result["schema_info"] = response.text
            
            logger.info(f"SQL口径查询成功，状态码: {response.status_code}")
            return result
            
        except requests.exceptions.ConnectionError:
            error_msg = f"连接错误：无法连接到 {full_url}。请确保SQL服务器正在运行。"
            logger.error(error_msg)
            return {
                "success": False,
                "error": "连接错误",
                "message": error_msg,
                "endpoint": endpoint,
                "request_data": request_data,
                "full_url": full_url
            }
        except requests.exceptions.Timeout:
            error_msg = f"请求超时：SQL口径查询超过60秒未响应。"
            logger.error(error_msg)
            return {
                "success": False,
                "error": "请求超时",
                "message": error_msg,
                "endpoint": endpoint,
                "request_data": request_data,
                "full_url": full_url
            }
        except Exception as e:
            error_msg = f"SQL口径查询失败：{str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": "未知错误",
                "message": error_msg,
                "endpoint": endpoint,
                "request_data": request_data,
                "full_url": full_url
            }
    
    async def execute_sql_query(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """执行SQL查询"""
        query = arguments.get("query", "")
        token = arguments.get("token", SQL_API_TOKEN)
        
        endpoint = "/api/sql/query"
        full_url = f"{TARGET_SERVER_URL}{endpoint}"
        
        request_data = {
            "query": query,
            "extra_result_params": []
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        
        if not token:
            logger.warning("SQL API Token 未设置，请设置环境变量 SQL_API_TOKEN 或在调用时提供token参数")
        
        try:
            logger.info(f"正在向 {full_url} 执行SQL查询")
            logger.info(f"SQL查询: {query}")
            logger.info(f"请求参数: {request_data}")
            
            response = requests.post(full_url, json=request_data, headers=headers, timeout=120.0)  # SQL查询可能需要更长时间
            
            result = {
                "success": True,
                #"status_code": response.status_code,
                #"endpoint": endpoint,
                #"sql_query": query,
                #"request_data": request_data,
                #"response_time_ms": response.elapsed.total_seconds() * 1000 if response.elapsed else None
            }
            
            try:
                result["query_result"] = response.text
                #response_data = response.json()
                #result["query_result"] = response_data
                # 如果有特定的answer字段，单独提取
                #if isinstance(response_data, dict) and "data" in response_data :
                #    result["sql_result"] = response_data["data"]
            except ValueError:
                result["query_result"] = response.text
            
            logger.info(f"SQL查询执行成功，状态码: {response.status_code}")
            return result
            
        except requests.exceptions.ConnectionError:
            error_msg = f"连接错误：无法连接到 {full_url}。请确保SQL服务器正在运行。"
            logger.error(error_msg)
            return {
                "success": False,
                "error": "连接错误",
                "message": error_msg,
                "endpoint": endpoint,
                "sql_query": query,
                "request_data": request_data,
                "full_url": full_url
            }
        except requests.exceptions.Timeout:
            error_msg = f"请求超时：SQL查询超过120秒未响应。"
            logger.error(error_msg)
            return {
                "success": False,
                "error": "请求超时",
                "message": error_msg,
                "endpoint": endpoint,
                "sql_query": query,
                "request_data": request_data,
                "full_url": full_url
            }
        except Exception as e:
            error_msg = f"SQL查询执行失败：{str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": "未知错误",
                "message": error_msg,
                "endpoint": endpoint,
                "sql_query": query,
                "request_data": request_data
            }
    
    async def check_server_status(self) -> Dict[str, Any]:
        """检查目标服务器状态"""
        health_url = f"{TARGET_SERVER_URL}/health"
        
        try:
            logger.info(f"正在检查服务器状态: {health_url}")
            
            response = requests.get(health_url, timeout=10.0)
            
            return {
                "success": True,
                "status": "服务器在线",
                "status_code": response.status_code,
                "url": health_url,
                "response_time_ms": response.elapsed.total_seconds() * 1000 if response.elapsed else None
            }
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "status": "服务器离线",
                "message": f"无法连接到 {TARGET_SERVER_URL}",
                "url": health_url
            }
        except Exception as e:
            return {
                "success": False,
                "status": "检查失败",
                "message": str(e),
                "url": health_url
            }
    
    async def get_current_time(self) -> Dict[str, Any]:
        """获取当前系统时间"""
        try:
            current_time = datetime.now()
            formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
            
            logger.info(f"获取当前时间: {formatted_time}")
            
            return {
                "success": True,
                "current_time": formatted_time,
                #"timestamp": current_time.timestamp(),
                #"timezone": str(current_time.astimezone().tzinfo)
            }
        except Exception as e:
            error_msg = f"获取系统时间失败：{str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": "获取时间失败",
                "message": error_msg
            }


async def main_async():
    """主函数 - 运行MCP服务器"""
    logger.info("启动SQL Query MCP Server...")
    logger.info(f"目标SQL服务器: {TARGET_SERVER_URL}")
    logger.info("支持的API端点:")
    logger.info("  - /api/schema/query - 获取SQL数据口径信息")
    logger.info("  - /api/sql/query - 执行SQL查询")
    logger.info("  - /health - 健康检查")
    
    # 检查环境变量配置
    schema_token_status = "✅ 已配置" if SCHEMA_API_TOKEN else "❌ 未配置"
    sql_token_status = "✅ 已配置" if SQL_API_TOKEN else "❌ 未配置"
    logger.info(f"API Token 配置状态:")
    logger.info(f"  - SCHEMA_API_TOKEN: {schema_token_status}")
    logger.info(f"  - SQL_API_TOKEN: {sql_token_status}")
    
    if not SCHEMA_API_TOKEN or not SQL_API_TOKEN:
        logger.warning("部分API Token未配置，可以在调用工具时手动提供token参数")
    
    server = MCPServer()
    
    try:
        while True:
            # 从stdin读取消息
            line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
            if not line:
                break
                
            line = line.strip()
            if not line:
                continue
            
            try:
                message = json.loads(line)
                response = await server.handle_message(message)
                
                if response:
                    # 发送响应到stdout
                    print(json.dumps(response, ensure_ascii=False))
                    sys.stdout.flush()
                    
            except json.JSONDecodeError as e:
                logger.error(f"JSON解析错误: {e}")
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": "Parse error"
                    }
                }
                print(json.dumps(error_response))
                sys.stdout.flush()
                
    except KeyboardInterrupt:
        logger.info("服务器正在关闭...")
    except Exception as e:
        logger.error(f"服务器错误: {e}")


def main():
    """主入口函数，供脚本调用"""
    asyncio.run(main_async())

def __main__():
    """模块直接运行时调用"""
    main()

if __name__ == "__main__":
    main()