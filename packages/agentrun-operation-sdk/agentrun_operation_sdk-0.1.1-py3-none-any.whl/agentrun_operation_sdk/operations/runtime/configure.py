import re
import logging
from pathlib import Path
from typing import Optional, Tuple
from .models import ConfigureResult
from ...utils.runtime.config import merge_agent_config, save_config
from ...utils.runtime.container import ContainerRuntime
from ...utils.runtime.schema import (
    AgentRunAgentSchema,
)

AGENT_NAME_REGEX = r"^[a-zA-Z][a-zA-Z0-9_]{0,47}$"
AGENT_NAME_ERROR = (
    "Invalid agent name. Must start with a letter, contain only letters/numbers/underscores, "
    "and be 1-48 characters long."
)

log = logging.getLogger(__name__)

def configure_agentrun(
    agent_name: str,
    entrypoint_path: Path,
    container_runtime: Optional[str] = None,
    requirements_file: Optional[str] = None,
    region: Optional[str] = None,
    protocol: Optional[str] = None,    
) -> ConfigureResult:
    """Configure AgentRun application with deployment settings.

    Args:
        agent_name: name of the agent,
        entrypoint_path: Path to the entrypoint file
        container_runtime: Container runtime to use
        equirements_file: Path to requirements file
        region: HW Cloud region for deployment
        protocol: agent server protocol, must be either HTTP or MCP

    Returns:
        ConfigureResult model with configuration details
    """
    build_dir = Path.cwd()
    region = region or "cn-north-4" 
    runtime = ContainerRuntime(container_runtime)
    agentrun_name = None
    dockerfile_path = runtime.generate_dockerfile(
        entrypoint_path,
        build_dir,
        agentrun_name or "agentrun",
        region,
        requirements_file,
    )
    dockerignore_path = build_dir / ".dockerignore"
    log.info("Generated Dockerfile: %s", dockerfile_path)
    if dockerignore_path.exists():
        log.info("Generated .dockerignore: %s", dockerignore_path)

    config_path = build_dir / ".agentrun.yaml"
    entrypoint_path_str = entrypoint_path.as_posix()
    if agentrun_name:
        entrypoint = f"{entrypoint_path_str}:{agentrun_name}"
    else:
        entrypoint = entrypoint_path_str

    config = AgentRunAgentSchema(
        name=agent_name,
        entrypoint=entrypoint,
        platform=ContainerRuntime.DEFAULT_PLATFORM,
        container_runtime=runtime.runtime,
    )
    
    project_config = merge_agent_config(config_path, agent_name, config)
    save_config(project_config, config_path)

    return ConfigureResult(
        config_path=config_path,
        dockerfile_path=dockerfile_path,
        dockerignore_path=dockerignore_path if dockerignore_path.exists() else None,
        runtime=runtime.get_name(),
        region=region,
    )

def validate_agent_name(name: str) -> Tuple[bool, str]:
    """Check if name matches the pattern [a-zA-Z][a-zA-Z0-9_]{0,47}.

    This pattern requires:
    - First character: letter (a-z or A-Z)
    - Remaining 0-47 characters: letters, digits, or underscores
    - Total maximum length: 48 characters

    Args:
        name: The string to validate

    Returns:
        bool: True if the string matches the pattern, False otherwise
    """
    match = bool(re.match(AGENT_NAME_REGEX, name))

    if match:
        return match, ""
    else:
        return match, AGENT_NAME_ERROR
