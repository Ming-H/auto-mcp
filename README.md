# AutoMCP

自动从 API 文档生成 MCP (Model Context Protocol) Server 代码的工具。

## 功能特性

- 支持从 OpenAPI/Swagger 规范生成 MCP Server
- 支持 Python (FastMCP) 和 TypeScript (@modelcontextprotocol/sdk)
- 简单易用的命令行界面
- 生成的代码开箱即用

## 安装

```bash
pip install auto-mcp
```

或使用 Poetry:

```bash
poetry add auto-mcp
```

## 使用方法

### 从 OpenAPI 规范生成

```bash
auto-mcp generate --spec openapi.yaml --lang python --output ./my-mcp
```

### 从 URL 生成

```bash
auto-mcp generate --url https://api.example.com/docs.json --lang typescript
```

### 初始化新项目

```bash
auto-mcp init my-project
```

## 项目结构

```
auto_mcp/
├── core/
│   ├── parser.py       # API 文档解析
│   ├── generator.py    # MCP 代码生成
│   ├── validator.py    # 代码验证
│   └── types.py        # 类型定义
├── templates/
│   ├── python_server.py.j2
│   └── typescript_server.ts.j2
└── cli.py              # 命令行工具
```

## 开发

```bash
# 安装开发依赖
poetry install

# 运行测试
poetry run pytest

# 代码格式化
poetry run black auto_mcp/
poetry run ruff check auto_mcp/
```

## 示例

查看 `examples/` 目录获取更多示例。

## License

MIT
