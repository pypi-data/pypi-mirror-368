from pathlib import Path
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict
from ...utils.runtime.container import ContainerRuntime

# Launch operation models
class LaunchResult(BaseModel):
    """Result of launch operation."""

    mode: str = Field(..., description="Launch mode: local, cloud, or codebuild")
    tag: str = Field(..., description="Docker image tag")
    env_vars: Optional[Dict[str, str]] = Field(default=None, description="Environment variables for local deployment")

    # Local mode fields
    port: Optional[int] = Field(default=None, description="Port for local deployment")
    runtime: Optional[ContainerRuntime] = Field(default=None, description="Container runtime instance")

    # Build output (optional)
    build_output: Optional[List[str]] = Field(default=None, description="Docker build output")

    model_config = ConfigDict(arbitrary_types_allowed=True)  # For runtime field

# Configure operation models
class ConfigureResult(BaseModel):
    """Result of configure operation."""

    config_path: Path = Field(..., description="Path to configuration file")
    dockerfile_path: Path = Field(..., description="Path to generated Dockerfile")
    dockerignore_path: Optional[Path] = Field(None, description="Path to generated .dockerignore")
    runtime: str = Field(..., description="Container runtime name")
    region: str = Field(..., description="HW Cloud region")