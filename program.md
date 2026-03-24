# AutoMCP - Program Specification

## 项目概述

AutoMCP 是一个自动化工具，用于从 API 文档生成 MCP (Model Context Protocol) Server 代码。

## 核心功能

### 1. 输入源支持
- OpenAPI/Swagger 规范文件 (JSON/YAML)
- API 文档 URL (自动抓取和解析)
- 自然语言功能描述

### 2. 解析能力
- 提取 API 端点、方法、路径
- 解析请求参数（路径参数、查询参数、请求体）
- 识别返回值结构和类型
- 处理认证机制

### 3. 代码生成
- Python Server (基于 FastMCP)
- TypeScript Server (基于 @modelcontextprotocol/sdk)

### 4. 输出结果
- 完整的 MCP Server 项目结构
- 可直接运行的代码
- 自动生成的类型定义
- 配置文件

## 项目架构

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

## 技术栈

- **语言**: Python 3.11+
- **模板引擎**: Jinja2
- **依赖管理**: Poetry
- **API 解析**: OpenAPI Spec Validator
- **代码生成**: FastMCP (Python), @modelcontextprotocol/sdk (TS)

## CLI 接口设计

```bash
# 从 OpenAPI 规范生成
auto-mcp generate --spec openapi.yaml --lang python --output ./my-mcp

# 从 URL 生成
auto-mcp generate --url https://api.example.com/docs.json --lang typescript

# 验证生成的代码
auto-mcp validate ./my-mcp

# 初始化新项目
auto-mcp init my-project
```

## 核心模块设计

### 1. Parser (parser.py)
- `OpenAPIParser`: 解析 OpenAPI 3.x 规范
- `DocumentationParser`: 从 HTML/Markdown 提取 API 信息
- `SchemaParser`: 解析 JSON Schema 类型

### 2. Generator (generator.py)
- `PythonMCPGenerator`: 生成 Python FastMCP 服务器
- `TypeScriptMCPGenerator`: 生成 TypeScript MCP 服务器
- `TemplateEngine`: Jinja2 模板渲染引擎

### 3. Validator (validator.py)
- `CodeValidator`: 验证生成的代码语法
- `MCPValidator`: 检查 MCP 协议兼容性

### 4. Types (types.py)
- `APISpec`: API 规范数据结构
- `Endpoint`: API 端点定义
- `Parameter`: 参数定义
- `MCPServerConfig`: MCP 服务器配置

## 实现计划

### Phase 1: 核心解析器
- [ ] OpenAPI 3.x 解析器
- [ ] 基础类型映射
- [ ] Schema 验证

### Phase 2: 代码生成器
- [ ] Python FastMCP 生成器
- [ ] TypeScript MCP SDK 生成器
- [ ] Jinja2 模板系统

### Phase 3: CLI 工具
- [ ] 命令行参数解析
- [ ] 文件输出处理
- [ ] 进度显示

### Phase 4: 验证和测试
- [ ] 代码语法验证
- [ ] 端到端测试
- [ ] 示例服务器

## 评估标准

1. **正确性**: 生成的代码符合 MCP 协议规范
2. **可用性**: 生成的服务器可直接运行
3. **完整性**: 支持常见 API 模式和类型
4. **可扩展性**: 易于添加新的语言支持

## 示例用例

生成一个天气 API 的 MCP Server:
```bash
auto-mcp generate --spec weather_api.yaml --lang python
```

输出:
```
weather_mcp/
├── pyproject.toml
├── README.md
├── weather_mcp/
│   ├── __init__.py
│   └── server.py
└── requirements.txt
```
