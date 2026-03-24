"""
MCP Server code generator for AutoMCP.
"""

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

from auto_mcp.core.types import APISpec, Endpoint, Language, MCPServerConfig


class BaseGenerator:
    """Base class for MCP server generators."""

    def __init__(self, config: MCPServerConfig) -> None:
        """
        Initialize the generator.

        Args:
            config: MCP server configuration
        """
        self.config = config
        self.template_env = self._create_template_env()

    def _create_template_env(self) -> Environment:
        """Create Jinja2 template environment."""
        template_dir = Path(__file__).parent.parent / "templates"
        env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        # Add custom filters
        env.filters['python_type'] = self._python_type_filter
        return env

    @staticmethod
    def _python_type_filter(type_str: str) -> str:
        """Convert OpenAPI type to Python type."""
        type_mapping = {
            'string': 'str',
            'integer': 'int',
            'number': 'float',
            'boolean': 'bool',
            'array': 'list',
            'object': 'dict',
        }
        return type_mapping.get(type_str, 'Any')

    def generate(self, output_dir: Path) -> None:
        """
        Generate the MCP server project.

        Args:
            output_dir: Output directory path
        """
        raise NotImplementedError


class PythonMCPGenerator(BaseGenerator):
    """Generator for Python FastMCP servers."""

    def generate(self, output_dir: Path) -> None:
        """Generate Python MCP server project."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Create package directory
        pkg_dir = output_dir / self.config.name.replace("-", "_")
        pkg_dir.mkdir(exist_ok=True)

        # Generate server.py
        self._generate_server_file(pkg_dir)

        # Generate __init__.py
        self._generate_init_file(pkg_dir)

        # Generate pyproject.toml
        self._generate_pyproject(output_dir)

        # Generate README.md
        self._generate_readme(output_dir)

    def _generate_server_file(self, pkg_dir: Path) -> None:
        """Generate the main server file."""
        template = self.template_env.get_template("python_server.py.j2")
        content = template.render(
            name=self.config.name,
            version=self.config.version,
            description=self.config.description,
            endpoints=self.config.api_spec.endpoints,
            base_url=self.config.api_spec.base_url,
            has_auth=bool(self.config.api_spec.authentication),
        )

        (pkg_dir / "server.py").write_text(content)

    def _generate_init_file(self, pkg_dir: Path) -> None:
        """Generate the __init__.py file."""
        content = f'''"""
{self.config.description} MCP Server
"""

__version__ = "{self.config.version}"

from {self.config.name.replace("-", "_")}.server import mcp

__all__ = ["mcp", "__version__"]
'''
        (pkg_dir / "__init__.py").write_text(content)

    def _generate_pyproject(self, output_dir: Path) -> None:
        """Generate pyproject.toml."""
        package_name = self.config.name.replace("-", "_")

        dependencies = {
            "fastmcp": "^0.1.0",
            "httpx": "^0.26.0",
            "pydantic": "^2.5.0",
        }
        dependencies.update(self.config.dependencies)

        deps_str = "\n".join(
            f'{k} = "{v}"' for k, v in sorted(dependencies.items())
        )

        content = f'''[tool.poetry]
name = "{self.config.name}"
version = "{self.config.version}"
description = "{self.config.description}"
authors = ["{self.config.author or "AutoMCP"}"]
readme = "README.md"
packages = [{{include = "{package_name}"}}]

[tool.poetry.dependencies]
python = "^3.11"
{deps_str}

[tool.poetry.scripts]
{self.config.name} = "{package_name}.server:main"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
'''
        (output_dir / "pyproject.toml").write_text(content)

    def _generate_readme(self, output_dir: Path) -> None:
        """Generate README.md."""
        content = f'''# {self.config.name}

{self.config.description}

## Installation

```bash
pip install {self.config.name}
```

## Usage

Run the server:

```bash
{self.config.name}
```

Or with MCP inspector:

```bash
npx @modelcontextprotocol/inspector {self.config.name}
```

## Tools

This MCP server provides the following tools:

'''
        for endpoint in self.config.api_spec.endpoints:
            # Handle both dict and Endpoint dataclass
            if hasattr(endpoint, 'operation_id'):
                # Endpoint dataclass
                op_id = endpoint.operation_id
                display_desc = endpoint.summary or endpoint.description or 'No description'
            else:
                # dict
                op_id = endpoint.get('operation_id', endpoint.get('path', ''))
                display_desc = endpoint.get('summary', endpoint.get('description') or 'No description')
            content += f"- `{op_id}`: {display_desc}\n"

        content += f'''

## API Base URL

{self.config.api_spec.base_url or "Not configured"}

## License

{self.config.license or "MIT"}
'''
        (output_dir / "README.md").write_text(content)


class TypeScriptMCPGenerator(BaseGenerator):
    """Generator for TypeScript MCP servers using @modelcontextprotocol/sdk."""

    def generate(self, output_dir: Path) -> None:
        """Generate TypeScript MCP server project."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Create src directory
        src_dir = output_dir / "src"
        src_dir.mkdir(exist_ok=True)

        # Generate server.ts
        self._generate_server_file(src_dir)

        # Generate package.json
        self._generate_package_json(output_dir)

        # Generate tsconfig.json
        self._generate_tsconfig(output_dir)

        # Generate README.md
        self._generate_readme(output_dir)

    def _generate_server_file(self, src_dir: Path) -> None:
        """Generate the main server file."""
        template = self.template_env.get_template("typescript_server.ts.j2")
        content = template.render(
            name=self.config.name,
            version=self.config.version,
            description=self.config.description,
            endpoints=self.config.api_spec.endpoints,
            base_url=self.config.api_spec.base_url,
            has_auth=bool(self.config.api_spec.authentication),
        )

        (src_dir / "index.ts").write_text(content)

    def _generate_package_json(self, output_dir: Path) -> None:
        """Generate package.json."""
        dependencies = {
            "@modelcontextprotocol/sdk": "^1.0.0",
            "axios": "^1.6.0",
        }
        dependencies.update(self.config.dependencies)

        dev_dependencies = {
            "@types/node": "^20.0.0",
            "typescript": "^5.0.0",
            "tsx": "^4.0.0",
        }
        dev_dependencies.update(self.config.dev_dependencies)

        content = {
            "name": self.config.name,
            "version": self.config.version,
            "description": self.config.description,
            "type": "module",
            "bin": {
                self.config.name.replace("-", "_"): "./dist/index.js"
            },
            "scripts": {
                "build": "tsc",
                "start": "node dist/index.js",
                "dev": "tsx src/index.ts"
            },
            "dependencies": dependencies,
            "devDependencies": dev_dependencies,
            "author": self.config.author or "AutoMCP",
            "license": self.config.license or "MIT"
        }

        import json
        (output_dir / "package.json").write_text(json.dumps(content, indent=2))

    def _generate_tsconfig(self, output_dir: Path) -> None:
        """Generate tsconfig.json."""
        content = {
            "compilerOptions": {
                "target": "ES2022",
                "module": "Node16",
                "moduleResolution": "Node16",
                "outDir": "./dist",
                "rootDir": "./src",
                "strict": True,
                "esModuleInterop": True,
                "skipLibCheck": True,
                "forceConsistentCasingInFileNames": True,
                "declaration": True,
                "declarationMap": True,
                "sourceMap": True
            },
            "include": ["src/**/*"],
            "exclude": ["node_modules", "dist"]
        }

        import json
        (output_dir / "tsconfig.json").write_text(json.dumps(content, indent=2))

    def _generate_readme(self, output_dir: Path) -> None:
        """Generate README.md."""
        content = f'''# {self.config.name}

{self.config.description}

## Installation

```bash
npm install {self.config.name}
```

## Usage

Build and run:

```bash
npm run build
npm start
```

Or with MCP inspector:

```bash
npx @modelcontextprotocol/inspector npm start
```

## Tools

This MCP server provides the following tools:

'''
        for endpoint in self.config.api_spec.endpoints:
            # Handle both dict and Endpoint dataclass
            if hasattr(endpoint, 'operation_id'):
                # Endpoint dataclass
                op_id = endpoint.operation_id
                display_desc = endpoint.summary or endpoint.description or 'No description'
            else:
                # dict
                op_id = endpoint.get('operation_id', endpoint.get('path', ''))
                display_desc = endpoint.get('summary', endpoint.get('description') or 'No description')
            content += f"- `{op_id}`: {display_desc}\n"

        content += f'''

## API Base URL

{self.config.api_spec.base_url or "Not configured"}

## License

{self.config.license or "MIT"}
'''
        (output_dir / "README.md").write_text(content)
