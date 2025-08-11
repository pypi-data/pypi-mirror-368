# RagFlow MCP Server

一个用于与RagFlow知识库系统交互的MCP（Model Context Protocol）服务器。

## 功能特性

- 📋 **数据集管理**: 列出、创建数据集
- 📄 **文档管理**: 列出、创建、下载文档
- 📝 **内容管理**: 创建文本块（chunks）到文档
- 🔍 **智能检索**: 在知识库中搜索相关内容
- 🚀 **自动检测**: 自动查找文档所属数据集

## 安装

```bash
# 安装依赖
pip install fastmcp requests httpx

# 或者安装包
pip install ragflow-mcp
```

## MCP 客户端配置

在你的MCP客户端配置文件中添加以下配置：

### 方式1: 使用uvx运行（推荐）

```json
{
  "mcpServers": {
    "ragflow_mcp": {
      "command": "uvx",
      "args": [
        "ragflow-mcp",
        "--address", "your-ragflow-server.com",
        "--api-key", "your-api-key-here",
        "--dataset-id", "your-default-dataset-id",
        "--dataset-name", "你的默认数据集名称"
      ]
    }
  }
}
```

### 方式2: 使用本地开发版本

```json
{
  "mcpServers": {
    "ragflow_mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/ragflow_mcp/src",
        "run",
        "mcp_server_stdio.py",
        "--address", "your-ragflow-server.com",
        "--api-key", "your-api-key-here",
        "--dataset-id", "your-default-dataset-id",
        "--dataset-name", "你的默认数据集名称"
      ]
    }
  }
}
```

### 方式3: 使用Python直接运行

```json
{
  "mcpServers": {
    "ragflow_mcp": {
      "command": "python",
      "args": [
        "/path/to/ragflow_mcp/src/mcp_server_stdio.py",
        "--address", "your-ragflow-server.com",
        "--api-key", "your-api-key-here",
        "--dataset-id", "your-default-dataset-id",
        "--dataset-name", "你的默认数据集名称"
      ]
    }
  }
}
```

## 参数说明

| 参数 | 必需 | 说明 | 示例 |
|------|------|------|------|
| `--address` | ✅ | RagFlow服务器地址 | `ragflow.example.com` |
| `--api-key` | ✅ | RagFlow API密钥 | `ragflow-xxxxx` |
| `--dataset-id` | ❌ | 默认数据集ID | `abc123def456` |
| `--dataset-name` | ❌ | 默认数据集名称 | `我的知识库` |

## 可用工具

### 1. list_all_datasets
列出所有可用的数据集

### 2. list_all_documents  
列出指定数据集下的所有文档

### 3. create_new_dataset
创建新的数据集

### 4. create_empty_document
创建空白文档

### 5. create_chunk_to_document
向文档添加内容块

### 6. search_chunks
搜索相关内容

### 7. download_document
下载文档

## 配置示例

### Claude Desktop 配置示例

```json
{
  "mcpServers": {
    "ragflow_mcp": {
      "command": "uvx",
      "args": [
        "ragflow-mcp",
        "--address", "ragflow.iepose.cn",
        "--api-key", "ragflow-g4ZTU4ZjM4YTAwMTExZWZhZjkyMDI0Mm",
        "--dataset-id", "c3303d4ee45611ef9b610242ac180003",
        "--dataset-name", "第二大脑"
      ]
    }
  }
}
```

## 安全注意事项

- ⚠️ **API密钥安全**: 确保API密钥不会被意外泄露
- 🔐 **访问权限**: 只配置你有权访问的RagFlow服务器
- 📝 **配置保护**: 注意保护包含敏感信息的配置文件

## 故障排除

### 连接失败
检查服务器地址和API密钥是否正确：
```bash
python src/mcp_server_stdio.py --address your-server --api-key your-key
```

### 权限错误
确保API密钥有足够的权限访问指定的数据集。

### 配置问题
确保所有必需参数都已正确传递。