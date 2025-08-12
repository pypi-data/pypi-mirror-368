 
一个用于查询需求分析对应的SQL table scheme信息的模型上下文协议服务器。该服务器包装了原始的get_schema_info API，让AI应用能够通过MCP协议获取SQL表结构信息。

## 主要功能
根据用户查询需求，分析需要用到的数据表、字段、枚举值、关联方式和易错点等信息。

## 可用工具
**analyze_sql_schema** - 分析SQL表结构和数据需求

必需参数：
- user (字符串): 用户信息，用于身份识别和权限控制
- query (字符串): 用户的数据需求描述，例如"我需要查询最近一个月的用户活跃度数据"
- appkey (字符串): API密钥，用于接口认证
 

## 使用示例
- "查询用户最近30天的购买行为数据"
- "分析不同地区的销售业绩情况"  
- "获取商品库存和销量的关联分析"
## 安装

### 使用 PIP
你可以通过 pip 安装 fit-growth-mcp-tools：

```bash
pip install fit-growth-mcp-tools
```

安装完成后，可以使用以下命令作为脚本运行：

```bash
python -m fit_growth_mcp_tools
```
## 配置

### 在各类大模型客户端中 配置  MCP 文件

```json 
{
  "mcpServers": { 
    "fit_data_tool": {
      "disabled": false,
      "command": "python",
      "args": [
       "-m", "fit_growth_mcp_tools"
      ],
      "env": { 
        "SCHEMA_API_TOKEN": "app-xx",
        "SQL_API_TOKEN": "app-xx"
      }
    }
    
  }
}
```
 