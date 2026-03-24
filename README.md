# AutoMCP

[English](#english) | [中文](#中文)

---

<a name="english"></a>
## English

### Automatically Generate MCP Server Code from OpenAPI Specifications

AutoMCP is a powerful tool that automatically generates MCP (Model Context Protocol) Server code from OpenAPI/Swagger specifications. It bridges the gap between existing REST APIs and the MCP ecosystem, enabling seamless integration with AI assistants like Claude.

### Features

- **Multi-format Support**: Parse OpenAPI 3.x specs from YAML, JSON, URLs, or dictionaries
- **Dual Language Output**: Generate Python (FastMCP) or TypeScript (@modelcontextprotocol/sdk) servers
- **Complete Project Generation**: Produces ready-to-run projects with configuration files
- **CLI & Programmatic API**: Use via command line or import as a library
- **Code Validation**: Built-in syntax checking for generated code

### Installation

```bash
pip install auto-mcp
```

Or with Poetry:

```bash
poetry add auto-mcp
```

### Quick Start

#### Command Line

```bash
# Generate from local file
auto-mcp generate --spec openapi.yaml --lang python --output ./my-mcp

# Generate from URL
auto-mcp generate --url https://api.example.com/openapi.json --lang typescript

# Initialize new project
auto-mcp init my-project
```

#### Python API

```python
from auto_mcp.core.parser import OpenAPIParser
from auto_mcp.core.generator import PythonMCPGenerator
from auto_mcp.core.types import APISpec, Language, MCPServerConfig
from pathlib import Path

# Parse OpenAPI spec
parser = OpenAPIParser("path/to/openapi.yaml")
parser.parse()
spec_data = parser.to_api_spec()

# Create configuration
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

# Generate code
generator = PythonMCPGenerator(config)
generator.generate(Path("./output"))
```

### Generated Project Structure

**Python Project:**
```
my-mcp/
├── pyproject.toml      # Poetry configuration
├── README.md           # Usage documentation
└── my_mcp/             # Python package
    ├── __init__.py
    └── server.py       # MCP server main file
```

**TypeScript Project:**
```
my-mcp/
├── package.json        # npm configuration
├── tsconfig.json       # TypeScript configuration
├── README.md
└── src/
    └── index.ts        # MCP server main file
```

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     AutoMCP Pipeline                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────┐     ┌──────────┐     ┌──────────┐            │
│  │   CLI    │────▶│  Parser  │────▶│ Generator│            │
│  │          │     │          │     │          │            │
│  │ - init   │     │ OpenAPI  │     │ Python   │            │
│  │ - gen    │     │ 3.x      │     │ TS       │            │
│  │ - val    │     │          │     │          │            │
│  └──────────┘     └──────────┘     └──────────┘            │
│                        │                │                    │
│                        ▼                ▼                    │
│                 ┌──────────┐     ┌──────────┐              │
│                 │  Types   │     │ Validator│              │
│                 │          │     │          │              │
│                 │ Endpoint │     │ Code     │              │
│                 │ APISpec  │     │ MCP      │              │
│                 └──────────┘     └──────────┘              │
└─────────────────────────────────────────────────────────────┘
```

### Development

```bash
# Install dev dependencies
poetry install

# Run tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=auto_mcp

# Code formatting
poetry run black auto_mcp/
poetry run ruff check auto_mcp/
```

### Test Coverage

- **131 tests** with **95% coverage**
- Comprehensive tests for parser, generator, types, validator, and CLI

### License

MIT

---

<a name="中文"></a>
## 中文

### 从 OpenAPI 规范自动生成 MCP 服务器代码

AutoMCP 是一个强大的工具，能够从 OpenAPI/Swagger 规范自动生成 MCP（模型上下文协议）服务器代码。它连接了现有 REST API 与 MCP 生态系统，实现与 Claude 等 AI 助手的无缝集成。

### 功能特性

- **多格式支持**：从 YAML、JSON、URL 或字典解析 OpenAPI 3.x 规范
- **双语言输出**：生成 Python (FastMCP) 或 TypeScript (@modelcontextprotocol/sdk) 服务器
- **完整项目生成**：生成可直接运行的完整项目，包含配置文件
- **命令行与编程 API**：支持命令行使用或作为库导入
- **代码验证**：内置语法检查确保生成代码质量

### 安装

```bash
pip install auto-mcp
```

或使用 Poetry:

```bash
poetry add auto-mcp
```

### 快速开始

#### 命令行

```bash
# 从本地文件生成
auto-mcp generate --spec openapi.yaml --lang python --output ./my-mcp

# 从 URL 生成
auto-mcp generate --url https://api.example.com/openapi.json --lang typescript

# 初始化新项目
auto-mcp init my-project
```

#### Python API

```python
from auto_mcp.core.parser import OpenAPIParser
from auto_mcp.core.generator import PythonMCPGenerator
from auto_mcp.core.types import APISpec, Language, MCPServerConfig
from pathlib import Path

# 解析 OpenAPI 规范
parser = OpenAPIParser("path/to/openapi.yaml")
parser.parse()
spec_data = parser.to_api_spec()

# 创建配置
api_spec = APISpec(
    title=spec_data["title"],
    version=spec_data["version"],
    endpoints=spec_data["endpoints"],
)

config = MCPServerConfig(
    name="my-mcp",
    version="1.0.0",
    description="我的 MCP 服务器",
    language=Language.PYTHON,
    api_spec=api_spec,
)

# 生成代码
generator = PythonMCPGenerator(config)
generator.generate(Path("./output"))
```

### 生成的项目结构

**Python 项目：**
```
my-mcp/
├── pyproject.toml      # Poetry 配置
├── README.md           # 使用文档
└── my_mcp/             # Python 包
    ├── __init__.py
    └── server.py       # MCP 服务器主文件
```

**TypeScript 项目：**
```
my-mcp/
├── package.json        # npm 配置
├── tsconfig.json       # TypeScript 配置
├── README.md
└── src/
    └── index.ts        # MCP 服务器主文件
```

### 核心模块

| 模块 | 功能 |
|------|------|
| `parser.py` | OpenAPI/Swagger 文档解析，支持 URL、文件、字典输入 |
| `generator.py` | MCP 服务器代码生成，Python/TypeScript 双语言支持 |
| `types.py` | 核心数据类型定义（Endpoint, Parameter, Response 等） |
| `validator.py` | 代码语法验证和 MCP 协议规范检查 |
| `cli.py` | 命令行接口（generate, validate, init） |

### 开发

```bash
# 安装开发依赖
poetry install

# 运行测试
poetry run pytest

# 带覆盖率报告
poetry run pytest --cov=auto_mcp

# 代码格式化
poetry run black auto_mcp/
poetry run ruff check auto_mcp/
```

### 测试覆盖

- **131 个测试**，**95% 覆盖率**
- 全面覆盖解析器、生成器、类型系统、验证器和 CLI

### 许可证

MIT
