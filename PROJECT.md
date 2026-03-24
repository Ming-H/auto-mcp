# AutoMCP 项目文档

## 项目概述

AutoMCP 是一个自动化工具，用于从 API 文档（OpenAPI/Swagger 规范）生成 MCP (Model Context Protocol) Server 代码。

### 核心目标

- 解析 OpenAPI 3.x 规范文档
- 生成符合 MCP 协规范的 Python (FastMCP) 和 TypeScript 服务器代码
- 提供开箱即用的 MCP 服务器实现
- 支持命令行工具和编程 API

## 系统架构

```
┌─────────────────────────────────────────────────────────────────────┐
│                          AutoMCP 系统架构                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────┐      ┌──────────┐      ┌──────────┐                  │
│  │  CLI     │─────▶│  Parser  │─────▶│ Generator│                  │
│  │          │      │          │      │          │                  │
│  │  - init  │      │ OpenAPI  │      │ Python   │                  │
│  │  - gen   │      │ 3.x      │      │ TS       │                  │
│  │  - val   │      │          │      │          │                  │
│  └──────────┘      └──────────┘      └──────────┘                  │
│                            │                  │                      │
│                            ▼                  ▼                      │
│                     ┌──────────┐      ┌──────────┐                  │
│                     │  Types   │      │ Validator│                  │
│                     │          │      │          │                  │
│                     │ Endpoint │      │ Code     │                  │
│                     │ APISpec  │      │ MCP      │                  │
│                     │ Config   │      │ Protocol │                  │
│                     └──────────┘      └──────────┘                  │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│                          模块说明                                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  parser.py        - OpenAPI/Swagger 文档解析                        │
│                    支持 URL、文件、字典输入                          │
│                    提取端点、参数、响应、认证信息                     │
│                                                                     │
│  generator.py     - MCP 服务器代码生成                              │
│                    Python: FastMCP 框架                             │
│                    TypeScript: @modelcontextprotocol/sdk            │
│                    Jinja2 模板渲染                                  │
│                                                                     │
│  types.py         - 核心数据类型定义                                │
│                    Endpoint, Parameter, Response                     │
│                    APISpec, MCPServerConfig                          │
│                    枚举: HTTPMethod, ParamLocation, Language         │
│                                                                     │
│  validator.py     - 代码和协议验证                                  │
│                    Python/TypeScript 语法检查                       │
│                    MCP 协议规范验证                                  │
│                                                                     │
│  cli.py           - 命令行接口                                      │
│                    generate: 从规范生成服务器                        │
│                    validate: 验证生成的代码                          │
│                    init: 初始化新项目                                │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## 核心模块详细说明

### 1. Parser (parser.py)

```python
class OpenAPIParser:
    """OpenAPI 3.x 规范解析器"""

    def __init__(spec_source: str | dict) -> None
        """初始化：支持 URL、文件路径、或已解析的字典"""

    def parse(self) -> dict[str, Any]
        """解析 OpenAPI 规范"""

    def extract_endpoints(self) -> list[dict[str, Any]]
        """提取所有 API 端点"""

    def to_api_spec(self) -> dict[str, Any]
        """转换为标准化的 API 规范字典"""
```

**支持的功能:**
- 从 URL 获取 OpenAPI 规范
- 从本地文件读取 YAML/JSON 格式
- 提取端点、参数、请求体、响应
- 解析认证方案（Bearer Token, API Key 等）
- 支持路径参数、查询参数、请求头

### 2. Generator (generator.py)

```python
class BaseGenerator:
    """生成器基类"""

class PythonMCPGenerator(BaseGenerator):
    """Python FastMCP 服务器生成器"""

    def generate(output_dir: Path) -> None
        """生成完整的 Python MCP 服务器项目"""

class TypeScriptMCPGenerator(BaseGenerator):
    """TypeScript MCP 服务器生成器"""

    def generate(output_dir: Path) -> None
        """生成完整的 TypeScript MCP 服务器项目"""
```

**生成的文件结构:**

Python 项目:
```
my-mcp/
├── pyproject.toml      # Poetry 配置
├── README.md           # 使用文档
└── my_mcp/             # Python 包
    ├── __init__.py
    └── server.py       # MCP 服务器主文件
```

TypeScript 项目:
```
my-mcp/
├── package.json        # npm 配置
├── tsconfig.json       # TypeScript 配置
├── README.md
└── src/
    └── index.ts        # MCP 服务器主文件
```

### 3. Types (types.py)

```python
# 枚举类型
class HTTPMethod(str, Enum)
class ParamLocation(str, Enum)
class Language(str, Enum)

# 数据类
@dataclass
class Parameter:
    """API 参数定义"""
    name: str
    type: str
    location: ParamLocation
    required: bool
    description: Optional[str]
    # ...

@dataclass
class Endpoint:
    """API 端点定义"""
    path: str
    method: HTTPMethod
    operation_id: str
    summary: Optional[str]
    parameters: list[Parameter]
    # ...

@dataclass
class APISpec:
    """完整 API 规范"""
    title: str
    version: str
    endpoints: list[Endpoint]
    # ...

@dataclass
class MCPServerConfig:
    """MCP 服务器配置"""
    name: str
    version: str
    language: Language
    api_spec: APISpec
    # ...
```

### 4. Validator (validator.py)

```python
class CodeValidator:
    """代码语法验证"""

    @staticmethod
    def validate_python(code: str) -> list[str]
    @staticmethod
    def validate_typescript(code: str) -> list[str]

class MCPValidator:
    """MCP 协议验证"""

    REQUIRED_METHODS = ["tools/list", "tools/call", "resources/list"]
    REQUIRED_FIELDS = ["name", "version"]
```

## API 文档

### 编程 API

```python
from auto_mcp.core.parser import OpenAPIParser
from auto_mcp.core.generator import PythonMCPGenerator
from auto_mcp.core.types import APISpec, Language, MCPServerConfig

# 1. 解析 API 规范
parser = OpenAPIParser("path/to/openapi.yaml")
parser.parse()
spec_data = parser.to_api_spec()

# 2. 创建配置
api_spec = APISpec(
    title=spec_data["title"],
    version=spec_data["version"],
    endpoints=spec_data["endpoints"],
)

config = MCPServerConfig(
    name="my-mcp",
    version="1.0.0",
    description="My MCP Server",
    language=Language.PYTHON,
    api_spec=api_spec,
)

# 3. 生成代码
generator = PythonMCPGenerator(config)
generator.generate(Path("./output"))
```

### 命令行 API

```bash
# 从文件生成
auto-mcp generate --spec openapi.yaml --lang python --output ./my-mcp

# 从 URL 生成
auto-mcp generate --url https://api.example.com/docs.json --lang typescript

# 初始化项目
auto-mcp init my-project

# 验证生成的代码
auto-mcp validate ./my-mcp
```

## 使用示例

### 示例 1: 生成天气 API MCP 服务器

```python
from pathlib import Path
from auto_mcp.core.generator import PythonMCPGenerator
from auto_mcp.core.parser import OpenAPIParser
from auto_mcp.core.types import APISpec, Language, MCPServerConfig

# 定义 OpenAPI 规范
WEATHER_API_SPEC = {
    "openapi": "3.0.0",
    "info": {
        "title": "Weather API",
        "version": "1.0.0",
    },
    "paths": {
        "/weather": {
            "get": {
                "operationId": "get_weather",
                "parameters": [
                    {
                        "name": "location",
                        "in": "query",
                        "required": True,
                        "schema": {"type": "string"}
                    }
                ]
            }
        }
    }
}

# 解析和生成
parser = OpenAPIParser(WEATHER_API_SPEC)
parser.parse()
spec_data = parser.to_api_spec()

api_spec = APISpec(
    title=spec_data["title"],
    version=spec_data["version"],
    endpoints=spec_data["endpoints"],
)

config = MCPServerConfig(
    name="weather-mcp",
    version="1.0.0",
    description="Weather API MCP Server",
    language=Language.PYTHON,
    api_spec=api_spec,
)

generator = PythonMCPGenerator(config)
generator.generate(Path("./weather_mcp"))
```

### 示例 2: 命令行生成

```bash
# 生成 Python MCP 服务器
auto-mcp generate \
    --spec https://petstore.swagger.io/v2/swagger.json \
    --lang python \
    --name petstore-mcp \
    --output ./petstore-mcp

# 生成 TypeScript MCP 服务器
auto-mcp generate \
    --spec openapi.yaml \
    --lang typescript \
    --output ./my-ts-mcp
```

## 开发状态

### 已完成功能 (✅)

- [x] OpenAPI 3.x 规范解析
- [x] 端点提取（包含所有 HTTP 方法）
- [x] 参数解析（路径、查询、请求头、Cookie）
- [x] 响应结构解析
- [x] 认证方案提取
- [x] Python FastMCP 服务器生成
- [x] TypeScript MCP SDK 服务器生成
- [x] 命令行工具（generate, validate, init）
- [x] 项目文件生成（pyproject.toml, package.json, README）
- [x] 代码语法验证
- [x] 单元测试覆盖

### TODO / 待改进功能

- [ ] 支持更多 OpenAPI 版本（Swagger 2.0）
- [ ] 支持请求体（POST/PUT）的完整处理
- [ ] 改进类型推断（支持复杂 schema）
- [ ] 添加更多模板定制选项
- [ ] 支持插件系统
- [ ] 添加更多验证规则
- [ ] 改进错误处理和用户反馈
- [ ] 添加交互式配置模式
- [ ] 支持从 GraphQL API 生成
- [ ] 生成的代码集成测试

### 已知限制

1. **类型映射**: 当前仅支持基础类型（string, integer, number, boolean, array, object）
2. **请求体**: POST/PUT 请求的 request body 处理较基础
3. **认证**: 生成的代码中认证是占位符，需要手动配置
4. **复杂 Schema**: 嵌套对象和引用（$ref）处理不完整

## 测试

```bash
# 运行所有测试
poetry run pytest

# 运行特定测试
poetry run pytest tests/test_parser.py
poetry run pytest tests/test_generator.py

# 带覆盖率报告
poetry run pytest --cov=auto_mcp
```

## 依赖项

```
python >= 3.11
click >= 8.1.7
jinja2 >= 3.1.3
pydantic >= 2.5.0
httpx >= 0.26.0
pyyaml >= 6.0.1
jsonschema >= 4.20.0
rich >= 13.7.0
```

## License

MIT
