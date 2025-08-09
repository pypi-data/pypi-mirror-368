import typer
from pathlib import Path
from typing import Optional, List
from rich.panel import Panel
from prompt_toolkit import prompt
from prompt_toolkit.completion import PathCompleter
from ..common import console, _handle_error, _print_success
from ...operations.runtime import (
    validate_agent_name,
    launch_agentrun,
    configure_agentrun
)
from ...utils.runtime.entrypoint import parse_entrypoint


def _validate_requirements_file(file_path: str) -> str:
    """Validate requirements file and return the path."""
    from ...utils.runtime.entrypoint import validate_requirements_file

    try:
        deps = validate_requirements_file(Path.cwd(), file_path)
        _print_success(f"Using requirements file: [dim]{deps.resolved_path}[/dim]")
        return file_path
    except (FileNotFoundError, ValueError) as e:
        _handle_error(str(e), e)


def _prompt_for_requirements_file(prompt_text: str, default: str = "") -> Optional[str]:
    """Prompt user for requirements file path with validation."""
    response = prompt(prompt_text, completer=PathCompleter(), default=default)

    if response.strip():
        return _validate_requirements_file(response.strip())

    return None

def configure(
    entrypoint: Optional[str] = None,
    agent_name: Optional[str] = None,
    container_runtime: Optional[str] = None,
    requirements_file: Optional[str] = None,
    region: Optional[str] = None,
    protocol: Optional[str] = None,
):
    """Configure a AgentRun agent. The agent name defaults to your Python file name."""
    if not entrypoint:
        _handle_error("--entrypoint is required")

    if protocol and protocol.upper() not in ["HTTP", "MCP"]:
        _handle_error("Error: --protocol must be either HTTP or MCP")

    console.print("[cyan]Configuring Bedrock AgentCore...[/cyan]")
    try:
        _, file_name = parse_entrypoint(entrypoint)
        agent_name = agent_name or file_name

        valid, error = validate_agent_name(agent_name)
        if not valid:
            _handle_error(error)

        console.print(f"[dim]Agent name: {agent_name}[/dim]")
    except ValueError as e:
        _handle_error(f"Error: {e}", e)

    final_requirements_file = _handle_requirements_file_display(requirements_file) 

    try:
        result = configure_agentrun(
            agent_name=agent_name,
            entrypoint_path=Path(entrypoint),
            container_runtime=container_runtime,
            requirements_file=final_requirements_file,
            region=region,
            protocol=protocol.upper() if protocol else None,
        )
        console.print(
            Panel(
                f"[green]Configuration Summary[/green]\n\n"
                f"Name: {agent_name}\n"
                f"Runtime: {result.runtime}\n"
                f"Region: {result.region}\n"
                f"Configuration saved to: {result.config_path}",
                title="AgentRun Configured",
                border_style="green",
            )
        )

    except ValueError as e:
        # Handle validation errors from core layer
        _handle_error(str(e), e)
    except Exception as e:
        _handle_error(f"Configuration failed: {e}", e)

def create(
    entrypoint: Optional[str] = typer.Option(None, "--entrypoint", "-e", help="Python file with AgentRunApp"),
    agent_name: Optional[str] = typer.Option(None, "--name", "-n"),
    requirements_file: Optional[str] = typer.Option(
        None, "--requirements-file", "-rf", help="Path to requirements file"
    ),
    container_runtime: Optional[str] = typer.Option(None, "--container-runtime", "-ctr"),
    region: Optional[str] = typer.Option(None, "--region", "-r"),
    protocol: Optional[str] = typer.Option(None, "--protocol", "-p", help="Server protocol (HTTP or MCP)"),

    local: bool = typer.Option(
        False, "--local", "-l", help="Build locally and run container locally - requires Docker/Finch/Podman"
    ),
    envs: List[str] = typer.Option(  # noqa: B008
        None, "--env", "-env", help="Environment variables for agent (format: KEY=VALUE)"
    ),
):
    """Launch AgentRun with three deployment modes.
    --local: Local build + local runtime
       - Build container locally and run locally
       - requires Docker/Finch/Podman
       - For local development and testing
    """
    configure(entrypoint, agent_name, container_runtime, requirements_file, region, protocol)

    config_path = Path.cwd() / ".agentrun.yaml"

    try:
        # Show launch mode with enhanced migration guidance
        if local:
            mode = "local"
            console.print(f"[cyan]🏠 Launching Bedrock AgentCore ({mode} mode)...[/cyan]")
            console.print("[dim]   • Build and run container locally[/dim]")
            console.print("[dim]   • Requires Docker/Finch/Podman to be installed[/dim]")
            console.print("[dim]   • Perfect for development and testing[/dim]\n")

        with console.status("[bold]Launching AgentRun...[/bold]"):
            env_vars = None
            if envs:
                env_vars = {}
                for env_var in envs:
                    if "=" not in env_var:
                        _handle_error(f"Invalid environment variable format: {env_var}. Use KEY=VALUE format.")
                    key, value = env_var.split("=", 1)
                    env_vars[key] = value

            result = launch_agentrun(
                config_path=config_path,
                agent_name=agent_name,
                local=local,
                env_vars=env_vars,
            )

        if result.mode == "local":
            _print_success(f"Docker image built: {result.tag}")
            _print_success("Ready to run locally")
            console.print("Starting server at http://localhost:8080")
            console.print("[yellow]Press Ctrl+C to stop[/yellow]\n")

            if result.runtime is None or result.port is None:
                _handle_error("Unable to launch locally")

            try:
                result.runtime.run_local(result.tag, result.port, result.env_vars)
            except KeyboardInterrupt:
                console.print("\n[yellow]Stopped[/yellow]")

    except FileNotFoundError:
        _handle_error(".bedrock_agentcore.yaml not found. Run 'agentcore configure --entrypoint <file>' first")
    except ValueError as e:
        _handle_error(str(e), e)
    except RuntimeError as e:
        _handle_error(str(e), e)
    except Exception as e:
        if not isinstance(e, typer.Exit):
            _handle_error(f"Launch failed: {e}", e)
        raise

def _handle_requirements_file_display(requirements_file: Optional[str]) -> Optional[str]:
    """Handle requirements file with display logic for CLI."""
    from ...utils.runtime.entrypoint import detect_dependencies

    if requirements_file:
        # User provided file - validate and show confirmation
        return _validate_requirements_file(requirements_file)

    # Auto-detection with interactive prompt
    deps = detect_dependencies(Path.cwd())

    if deps.found:
        console.print(f"\n🔍 [cyan]Detected dependency file:[/cyan] [bold]{deps.file}[/bold]")
        console.print("[dim]Press Enter to use this file, or type a different path (use Tab for autocomplete):[/dim]")

        result = _prompt_for_requirements_file("Path or Press Enter to use detected dependency file: ", default="")

        if result is None:
            # Use detected file
            _print_success(f"Using detected file: [dim]{deps.file}[/dim]")

        return result
    else:
        console.print("\n[yellow]⚠️  No dependency file found (requirements.txt or pyproject.toml)[/yellow]")
        console.print("[dim]Enter path to requirements file (use Tab for autocomplete), or press Enter to skip:[/dim]")

        result = _prompt_for_requirements_file("Path: ")

        if result is None:
            _handle_error("No requirements file specified and none found automatically")

        return result