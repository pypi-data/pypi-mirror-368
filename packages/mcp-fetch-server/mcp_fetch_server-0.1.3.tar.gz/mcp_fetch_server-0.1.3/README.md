# MCP Server Fetch

一个简单的MCP服务器，用于获取网页内容。

## 功能

- 获取指定URL的网页内容
- 支持提取纯文本内容
- 支持使用CSS选择器提取特定内容
- 提供REST API接口
- 可作为MCP服务器集成到智能体平台

## 安装

```bash
pip install mcp_fetch_server
```

## 使用方法

### 命令行启动

```bash
mcp_fetch_server --host 0.0.0.0 --port 8000
```

### API使用

启动服务器后，可以通过以下方式使用API：

```bash
curl -X POST "http://localhost:8000/fetch" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://example.com", "extract_text": true}'
```

### 在智能体平台中配置

在智能体平台的配置文件中添加以下内容：

```json
{
  "mcpServers": {
    "Fetch": {
      "command": "uvx",
      "args": [
        "mcp_fetch_server"
      ],
      "env": {}
    }
  }
}
```

## API文档

启动服务器后，访问 `http://localhost:8000/docs` 可查看完整的API文档。

## 开发

### 安装开发依赖

```bash
pip install -e .
```

### 运行测试

```bash
python -m pytest
```

## 许可证

MIT