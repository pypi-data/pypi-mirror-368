import yaml
import logging
from typing import Optional
from pathlib import Path
from .schema import AgentRunConfigSchema, AgentRunAgentSchema

log = logging.getLogger(__name__)

def _is_legacy_format(data: dict) -> bool:
    """Detect old single-agent format."""
    return isinstance(data, dict) and "agents" not in data and "name" in data and "entrypoint" in data

def _transform_legacy_to_multi_agent(data: dict) -> AgentRunConfigSchema:
    """Transform old format to new format at runtime."""
    agent_config = AgentRunAgentSchema.model_validate(data)
    return AgentRunConfigSchema(default_agent=agent_config.name, agents={agent_config.name: agent_config})

def load_config(config_path: Path) -> AgentRunConfigSchema:
    """Load config with automatic legacy format transformation."""
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration not found: {config_path}")

    with open(config_path, "r") as f:
        data = yaml.safe_load(f) or {}

    # Auto-detect and transform legacy format
    if _is_legacy_format(data):
        return _transform_legacy_to_multi_agent(data)

    # New format
    try:
        return AgentRunConfigSchema.model_validate(data)
    except Exception as e:
        raise ValueError(f"Invalid configuration format: {e}") from e
    
def load_config_if_exists(config_path: Path) -> Optional[AgentRunConfigSchema]:
    """Load configuration if file exists, otherwise return None.

    Args:
        config_path: Path to configuration file

    Returns:
        BedrockAgentCoreConfigSchema instance or None if file doesn't exist
    """
    if not config_path.exists():
        return None
    return load_config(config_path)

def save_config(config: AgentRunConfigSchema, config_path: Path):
    """Save configuration to YAML file.

    Args:
        config: BedrockAgentCoreConfigSchema instance to save
        config_path: Path to save configuration file
    """
    with open(config_path, "w") as f:
        yaml.dump(config.model_dump(), f, default_flow_style=False, sort_keys=False)

def merge_agent_config(
    config_path: Path, agent_name: str, new_config: AgentRunConfigSchema
) -> AgentRunConfigSchema:
    """Merge agent configuration into config.

    Args:
        config_path: Path to configuration file
        agent_name: Name of the agent to add/update
        new_config: Agent configuration to merge

    Returns:
        Updated project configuration
    """
    config = load_config_if_exists(config_path)

    # Handle None case - create new config
    if config is None:
        config = AgentRunConfigSchema()

    # Add/update agent
    config.agents[agent_name] = new_config

    # Log default agent change and always set current agent as default
    old_default = config.default_agent
    if old_default != agent_name:
        if old_default:
            log.info("Changing default agent from '%s' to '%s'", old_default, agent_name)
        else:
            log.info("Setting '%s' as default agent", agent_name)
    else:
        log.info("Keeping '%s' as default agent", agent_name)

    # Always set current agent as default (the agent being configured becomes the new default)
    config.default_agent = agent_name

    return config