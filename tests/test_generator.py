"""Tests for MCP server generators."""

from pathlib import Path
import tempfile

from auto_mcp.core.generator import PythonMCPGenerator, TypeScriptMCPGenerator
from auto_mcp.core.types import (
    APISpec,
    Endpoint,
    Language,
    MCPServerConfig,
    Parameter,
    ParamLocation,
)


def test_python_generator():
    """Test Python MCP generator."""
    api_spec = APISpec(
        title="Test API",
        version="1.0.0",
        description="Test API",
        base_url="https://api.test.com",
        endpoints=[
            Endpoint(
                path="/test",
                method="get",
                operation_id="test_endpoint",
                summary="Test endpoint",
            )
        ],
    )

    config = MCPServerConfig(
        name="test-mcp",
        version="1.0.0",
        description="Test MCP Server",
        language=Language.PYTHON,
        api_spec=api_spec,
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        generator = PythonMCPGenerator(config)
        generator.generate(Path(tmpdir))

        # Check files were created
        assert (Path(tmpdir) / "pyproject.toml").exists()
        assert (Path(tmpdir) / "README.md").exists()
        assert (Path(tmpdir) / "test_mcp" / "server.py").exists()
        assert (Path(tmpdir) / "test_mcp" / "__init__.py").exists()


def test_typescript_generator():
    """Test TypeScript MCP generator."""
    api_spec = APISpec(
        title="Test API",
        version="1.0.0",
        description="Test API",
        base_url="https://api.test.com",
        endpoints=[
            Endpoint(
                path="/test",
                method="get",
                operation_id="test_endpoint",
                summary="Test endpoint",
            )
        ],
    )

    config = MCPServerConfig(
        name="test-mcp",
        version="1.0.0",
        description="Test MCP Server",
        language=Language.TYPESCRIPT,
        api_spec=api_spec,
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        generator = TypeScriptMCPGenerator(config)
        generator.generate(Path(tmpdir))

        # Check files were created
        assert (Path(tmpdir) / "package.json").exists()
        assert (Path(tmpdir) / "tsconfig.json").exists()
        assert (Path(tmpdir) / "README.md").exists()
        assert (Path(tmpdir) / "src" / "index.ts").exists()


# Round 16: Generator with parameters
def test_python_generator_with_parameters():
    """Test Python generator with endpoint parameters."""
    api_spec = APISpec(
        title="Test API",
        version="1.0.0",
        description="Test API",
        base_url="https://api.test.com",
        endpoints=[
            Endpoint(
                path="/users/{id}",
                method="get",
                operation_id="get_user",
                summary="Get user by ID",
                parameters=[
                    Parameter(
                        name="id",
                        type="integer",
                        location=ParamLocation.PATH,
                        required=True,
                    ),
                    Parameter(
                        name="include",
                        type="string",
                        location=ParamLocation.QUERY,
                        required=False,
                    ),
                ],
            )
        ],
    )

    config = MCPServerConfig(
        name="test-mcp",
        version="1.0.0",
        description="Test MCP Server",
        language=Language.PYTHON,
        api_spec=api_spec,
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        generator = PythonMCPGenerator(config)
        generator.generate(Path(tmpdir))

        server_content = (Path(tmpdir) / "test_mcp" / "server.py").read_text()

        # Check parameter handling in generated code
        assert "def get_user(" in server_content
        assert "id: int" in server_content
        assert "include: str = None" in server_content
        assert 'path_params["id"]' in server_content


# Round 17: Generator with authentication
def test_python_generator_with_auth():
    """Test Python generator with authentication."""
    api_spec = APISpec(
        title="Test API",
        version="1.0.0",
        description="Test API",
        base_url="https://api.test.com",
        endpoints=[],
        authentication={"bearerAuth": {"type": "http", "scheme": "bearer"}},
    )

    config = MCPServerConfig(
        name="test-mcp",
        version="1.0.0",
        description="Test MCP Server",
        language=Language.PYTHON,
        api_spec=api_spec,
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        generator = PythonMCPGenerator(config)
        generator.generate(Path(tmpdir))

        server_content = (Path(tmpdir) / "test_mcp" / "server.py").read_text()

        # Check auth handling in generated code
        assert "AUTH_TOKEN" in server_content
        assert "Authorization" in server_content


# Round 18: Generator with multiple endpoints
def test_python_generator_multiple_endpoints():
    """Test Python generator with multiple endpoints."""
    api_spec = APISpec(
        title="Test API",
        version="1.0.0",
        description="Test API",
        base_url="https://api.test.com",
        endpoints=[
            Endpoint(
                path="/users",
                method="get",
                operation_id="list_users",
                summary="List users",
            ),
            Endpoint(
                path="/users/{id}",
                method="get",
                operation_id="get_user",
                summary="Get user",
            ),
            Endpoint(
                path="/users",
                method="post",
                operation_id="create_user",
                summary="Create user",
            ),
        ],
    )

    config = MCPServerConfig(
        name="test-mcp",
        version="1.0.0",
        description="Test MCP Server",
        language=Language.PYTHON,
        api_spec=api_spec,
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        generator = PythonMCPGenerator(config)
        generator.generate(Path(tmpdir))

        server_content = (Path(tmpdir) / "test_mcp" / "server.py").read_text()

        # Check all endpoints are generated
        assert "@mcp.tool()" in server_content
        assert "def list_users(" in server_content
        assert "def get_user(" in server_content
        assert "def create_user(" in server_content


# Round 19: TypeScript generator with parameters
def test_typescript_generator_with_parameters():
    """Test TypeScript generator with endpoint parameters."""
    api_spec = APISpec(
        title="Test API",
        version="1.0.0",
        description="Test API",
        base_url="https://api.test.com",
        endpoints=[
            Endpoint(
                path="/items/{id}",
                method="get",
                operation_id="get_item",
                summary="Get item",
                parameters=[
                    Parameter(
                        name="id",
                        type="string",
                        location=ParamLocation.PATH,
                        required=True,
                    ),
                ],
            )
        ],
    )

    config = MCPServerConfig(
        name="test-mcp",
        version="1.0.0",
        description="Test MCP Server",
        language=Language.TYPESCRIPT,
        api_spec=api_spec,
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        generator = TypeScriptMCPGenerator(config)
        generator.generate(Path(tmpdir))

        server_content = (Path(tmpdir) / "src" / "index.ts").read_text()

        # Check TypeScript generation
        assert "function get_item(" in server_content
        assert "case \"get_item\"" in server_content


# Round 20: README generation
def test_readme_generation():
    """Test README.md generation."""
    api_spec = APISpec(
        title="Test API",
        version="1.0.0",
        description="Test API",
        base_url="https://api.test.com",
        endpoints=[
            Endpoint(
                path="/test1",
                method="get",
                operation_id="test1",
                summary="Test endpoint 1",
            ),
            Endpoint(
                path="/test2",
                method="post",
                operation_id="test2",
                summary="Test endpoint 2",
            ),
        ],
    )

    config = MCPServerConfig(
        name="test-mcp",
        version="1.0.0",
        description="Test MCP Server",
        language=Language.PYTHON,
        api_spec=api_spec,
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        generator = PythonMCPGenerator(config)
        generator.generate(Path(tmpdir))

        readme_content = (Path(tmpdir) / "README.md").read_text()

        # Check README content
        assert "# test-mcp" in readme_content
        assert "Test MCP Server" in readme_content
        assert "`test1`" in readme_content
        assert "`test2`" in readme_content
        assert "https://api.test.com" in readme_content


# Round 21: pyproject.toml generation
def test_pyproject_generation():
    """Test pyproject.toml generation."""
    api_spec = APISpec(
        title="Test API",
        version="2.0.0",
        description="Test API",
        base_url="https://api.test.com",
        endpoints=[],
    )

    config = MCPServerConfig(
        name="my-mcp",
        version="2.0.0",
        description="My MCP Server",
        author="Test Author",
        license="MIT",
        language=Language.PYTHON,
        api_spec=api_spec,
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        generator = PythonMCPGenerator(config)
        generator.generate(Path(tmpdir))

        pyproject_content = (Path(tmpdir) / "pyproject.toml").read_text()

        # Check pyproject.toml content
        assert 'name = "my-mcp"' in pyproject_content
        assert 'version = "2.0.0"' in pyproject_content
        assert "Test Author" in pyproject_content
        assert "fastmcp" in pyproject_content
        assert "httpx" in pyproject_content
