"""
Command-line interface for AutoMCP.
"""

from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from auto_mcp.core.generator import PythonMCPGenerator, TypeScriptMCPGenerator
from auto_mcp.core.parser import OpenAPIParser
from auto_mcp.core.types import APISpec, Language, MCPServerConfig
from auto_mcp.core.validator import CodeValidator, MCPValidator

console = Console()


@click.group()
@click.version_option(version="0.1.0")
def main() -> None:
    """AutoMCP - Generate MCP servers from API documentation."""
    pass


@main.command()
@click.option("--spec", "-s", type=click.Path(exists=True), help="Path to OpenAPI spec file")
@click.option("--url", "-u", help="URL to OpenAPI spec")
@click.option("--lang", "-l", type=click.Choice(["python", "typescript"]), default="python", help="Output language")
@click.option("--output", "-o", type=click.Path(), default="./mcp-server", help="Output directory")
@click.option("--name", "-n", help="Server name (defaults to derived name)")
@click.option("--description", "-d", help="Server description")
def generate(
    spec: Optional[str],
    url: Optional[str],
    lang: str,
    output: str,
    name: Optional[str],
    description: Optional[str],
) -> None:
    """Generate an MCP server from an API specification."""
    if not spec and not url:
        console.print("[red]Error: Either --spec or --url must be provided[/red]")
        raise click.Abort()

    source = spec or url  # type: ignore

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        # Parse the specification
        parse_task = progress.add_task("Parsing API specification...", total=None)
        parser = OpenAPIParser(source)
        parser.parse()
        spec_data = parser.to_api_spec()
        progress.remove_task(parse_task)

        # Extract metadata
        info = parser._raw_spec.get("info", {})
        server_name = name or info.get("title", "api-server").lower().replace(" ", "-")
        server_version = info.get("version", "1.0.0")
        server_description = description or info.get("description", f"MCP server for {server_name}")

        # Create API spec object
        api_spec = APISpec(
            title=spec_data["title"],
            version=spec_data["version"],
            description=spec_data.get("description"),
            base_url=spec_data.get("base_url"),
            endpoints=spec_data["endpoints"],
        )

        # Create MCP server config
        config = MCPServerConfig(
            name=server_name,
            version=server_version,
            description=server_description,
            language=Language(lang),
            api_spec=api_spec,
        )

        # Generate the server
        gen_task = progress.add_task(f"Generating {lang} MCP server...", total=None)
        output_path = Path(output)

        if lang == "python":
            generator = PythonMCPGenerator(config)
        else:
            generator = TypeScriptMCPGenerator(config)

        generator.generate(output_path)
        progress.remove_task(gen_task)

    console.print(f"[green]Successfully generated MCP server at: {output_path}[/green]")
    console.print("\n[next steps]Next steps:[/next steps]")
    console.print(f"  1. cd {output_path}")
    if lang == "python":
        console.print("  2. poetry install")
        console.print(f"  3. poetry run {server_name}")
    else:
        console.print("  2. npm install")
        console.print("  3. npm run build")
        console.print("  4. npm start")


@main.command("list")
@click.option("--format", "-f", type=click.Choice(["json", "yaml", "text"]), default="json", help="Output format")
def list_endpoints(directory: str, format: str) -> None:
    """List all endpoints in an API specification."""
    parser = OpenAPIParser(directory)
    parser.parse()
    endpoints = parser.extract_endpoints()

    if format == "json":
        import json as json_module
        console.print_json(endpoints, indent=2)
    else:
        console.print_yaml(endpoints)


@main.command()
@click.argument("name")
def init(name: str) -> None:
    """Initialize a new AutoMCP project."""
    project_dir = Path(name)
    project_dir.mkdir(parents=True, exist_ok=True)

    # Create basic structure
    (project_dir / "spec.yaml").write_text("""# OpenAPI Specification
# Place your API spec here or use --url to fetch from a URL
openapi: 3.0.0
info:
  title: My API
  version: 1.0.0
  description: API description
paths: {}
""")

    (project_dir / "README.md").write_text(f"""# {name}

AutoMCP generated project.

## Usage

1. Edit `spec.yaml` with your API specification
2. Run: `auto-mcp generate --spec spec.yaml --output ./dist`
""")

    console.print(f"[green]Created AutoMCP project: {name}[/green]")
    console.print(f"  Edit {project_dir / 'spec.yaml'} and run:")
    console.print(f"  auto-mcp generate --spec spec.yaml --output ./dist")


if __name__ == "__main__":
    main()
