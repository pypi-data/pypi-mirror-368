# Todo MCP Server

一个用于Cursor集成的Todo任务管理MCP服务器，支持多用户配置。

## ✨ 功能特性

- 🔧 **6个MCP工具**: 创建、查询、更新、删除、搜索任务
- 📊 **3个资源**: 任务统计、最近任务、逾期任务
- 💬 **2个提示**: 任务摘要、优化建议
- 🔐 **多种认证**: 支持Token和用户名密码认证
- 🌐 **多服务器**: 支持连接不同的Todo API服务器

## 📦 安装

通过PyPI安装：

```bash
pip install todo-mcp-server
```

或使用uvx（推荐）：

```bash
uvx todo-mcp-server --help
```

## 🚀 使用方法

### Cursor配置

在 `~/.cursor/mcp.json` 中添加配置：

#### 使用API Token认证
```json
{
  "mcpServers": {
    "my-todo": {
      "command": "uvx",
      "args": [
        "todo-mcp-server",
        "--api-url=https://your-todo-server.com:3000",
        "--api-token=your-secret-token"
      ]
    }
  }
}
```

#### 使用用户名密码认证
```json
{
  "mcpServers": {
    "my-todo": {
      "command": "uvx", 
      "args": [
        "todo-mcp-server",
        "--api-url=https://your-todo-server.com:3000",
        "--username=your-username",
        "--password=your-password"
      ]
    }
  }
}
```

### 命令行参数

| 参数 | 必需 | 描述 | 示例 |
|------|------|------|------|
| `--api-url` | ✅ | Todo API服务器地址 | `https://api.example.com:3000` |
| `--api-token` | 🔄 | API访问令牌 | `abc123...` |
| `--username` | 🔄 | 用户名 | `john.doe` |
| `--password` | 🔄 | 密码 | `secret123` |
| `--timeout` | ❌ | 请求超时时间（默认30秒） | `60` |

注：`--api-token` 或 `--username + --password` 必须提供其中一种。

## 🛠️ 可用工具

在Cursor中，你可以使用以下命令：

- **创建任务**: "帮我创建一个任务：完成项目文档"
- **查看任务**: "显示我的待办任务列表"
- **更新任务**: "将任务1标记为已完成"
- **搜索任务**: "搜索包含'项目'的任务"
- **获取统计**: "显示我的任务统计信息"
- **查看逾期**: "显示所有逾期的任务"

## 🔧 开发

### 本地开发安装

```bash
git clone https://github.com/huangzhenxin/todo-mcp-server.git
cd todo-mcp-server
pip install -e .
```

### 测试

```bash
# 测试MCP服务器
todo-mcp-server --api-url=http://localhost:3000 --api-token=test
```

## 📄 许可证

MIT许可证 - 详见 LICENSE 文件。

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📞 支持

如有问题，请在GitHub上创建Issue：
https://github.com/huangzhenxin/todo-mcp-server/issues