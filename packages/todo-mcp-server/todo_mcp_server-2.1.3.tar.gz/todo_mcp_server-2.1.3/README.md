# Todo MCP Server

一个用于Cursor集成的Todo任务管理MCP服务器，支持多用户配置。

## ✨ 功能特性

- 🔧 **12个MCP工具**: 完整的任务和项目管理功能
- 📊 **3个资源**: 任务统计、最近任务、逾期任务
- 💬 **2个提示**: 任务摘要、优化建议
- 🔐 **多种认证**: 支持Token和用户名密码认证
- 🌐 **多服务器**: 支持连接不同的Todo API服务器
- 🔄 **同步更新**: 与 todo-api 完全同步，支持项目和任务管理

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

### 任务管理
- **创建任务**: "帮我创建一个任务：完成项目文档"
- **查看任务**: "显示我的待办任务列表"
- **更新任务**: "将任务1标记为已完成"
- **删除任务**: "删除任务1"
- **搜索任务**: "搜索包含'项目'的任务"
- **获取任务详情**: "显示任务1的详细信息"

### 项目管理
- **创建项目**: "创建一个新项目：网站重构"
- **查看项目**: "显示我的项目列表"
- **更新项目**: "将项目1状态改为已完成"
- **删除项目**: "删除项目1"
- **获取项目详情**: "显示项目1的详细信息"
- **查看项目任务**: "显示项目1下的所有任务"

### 资源访问
- **获取统计**: "显示我的任务统计信息"
- **查看逾期**: "显示所有逾期的任务"

## 🔄 同步更新

### v1.1.0 更新内容

- ✅ **API路径同步**: 更新为与 todo-api 一致的路径格式
- ✅ **数据结构适配**: 支持 todo-api 的数字优先级和分页机制
- ✅ **项目管理**: 新增完整的项目 CRUD 操作
- ✅ **任务关联**: 支持任务与项目的关联管理
- ✅ **错误处理**: 优化错误处理和状态码检查

### 兼容性

- 与 todo-api v1.0+ 完全兼容
- 支持 PostgreSQL 和 SQLite 数据库
- 保持向后兼容性

## 🔧 开发

### 本地开发安装

```bash
git clone https://github.com/huangzhenxin/todo-mcp-server.git
cd todo-mcp-server
pip install -e .
```

### 测试

运行同步测试：

```bash
python test_sync_update.py
```

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