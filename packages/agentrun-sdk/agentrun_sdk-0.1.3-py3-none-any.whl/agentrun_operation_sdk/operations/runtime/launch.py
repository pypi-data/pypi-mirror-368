import logging
from typing import Optional
from pathlib import Path
from ...utils.runtime.container import ContainerRuntime
from .models import LaunchResult
from ...utils.runtime.config import load_config

log = logging.getLogger(__name__)

def launch_agentrun(
    config_path: Path,
    agent_name: Optional[str] = None,
    local: bool = False,
    env_vars: Optional[dict] = None,
) -> LaunchResult:
    """Launch Bedrock AgentCore locally or to cloud.

    Args:
        agent_name: Name of agent to launch (for project configurations)
        local: Whether to run locally
        env_vars: Environment variables to pass to local container (dict of key-value pairs)

    Returns:
        LaunchResult model with launch details
    """
    project_config = load_config(config_path)
    agent_config = project_config.get_agent_config(agent_name)

    mode = "locally" if local else "to cloud"
    log.info("Launching Bedrock AgentCore agent '%s' %s", agent_config.name, mode)

    # Validate configuration
    errors = agent_config.validate(for_local=local)
    if errors:
        raise ValueError(f"Invalid configuration: {', '.join(errors)}")
    
    runtime = ContainerRuntime(agent_config.container_runtime)

    if local and not runtime.has_local_runtime:
        raise RuntimeError(
            "Cannot run locally - no container runtime available\n"
            "💡 Recommendation: Use CodeBuild for cloud deployment\n"
            "💡 Run 'agentcore launch' (without --local) for CodeBuild deployment\n"
            "💡 For local runs, please install Docker, Finch, or Podman"
        )
    
    agentrun_name = agent_config.name

    tag = f"agentrun-{agentrun_name}:latest"

    build_dir = config_path.parent
    success, output = runtime.build(build_dir, tag)

    if not success:
        error_lines = output[-10:] if len(output) > 10 else output
        error_message = " ".join(error_lines)

        # Check if this is a container runtime issue and suggest CodeBuild
        if "No container runtime available" in error_message:
            raise RuntimeError(
                f"Build failed: {error_message}\n"
                "💡 Recommendation: Use CodeBuild for building containers in the cloud\n"
                "💡 Run 'agentcore launch' (default) for CodeBuild deployment"
            )
        else:
            raise RuntimeError(f"Build failed: {error_message}")

    log.info("Docker image built: %s", tag)

    if local:
        # Return info for local deployment
        return LaunchResult(
            mode="local",
            tag=tag,
            port=8080,
            runtime=runtime,
            env_vars=env_vars,
        )
    else:
        raise RuntimeError(
                "Build failed: only support local build\n"
            )