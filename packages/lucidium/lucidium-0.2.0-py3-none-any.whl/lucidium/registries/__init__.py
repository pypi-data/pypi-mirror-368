"""# lucidium.registries

This package defines the agent & environment registration systems.
"""

__all__ =   [
                # Class Registry & component classes.
                "ClassRegistry",
                "ClassEntry",
                
                # Command Registry & component classes.
                "CommandRegistry",
                "CommandEntry",
                
                # Specific registries
                "AGENT_REGISTRY",
                "AGENT_COMMAND_REGISTRY",
                "ENVIRONMENT_REGISTRY",
                "ENIRONMENT_COMMAND_REGISTRY",
                
                # Registration decorators  
                "register_agent",
                "register_agent_command",
                "register_environment",
                "register_environment_command"
            ]

# ClassRegistry & component classes.
from lucidium.registries.class_entry        import ClassEntry
from lucidium.registries.class_registry     import ClassRegistry
from lucidium.registries.command_entry      import CommandEntry
from lucidium.registries.command_registry   import CommandRegistry

# Agent Registries.
AGENT_REGISTRY:                 ClassRegistry =     ClassRegistry(name = "agents")
AGENT_COMMAND_REGISTRY:         CommandRegistry =   CommandRegistry(name = "agents")
ENVIRONMENT_REGISTRY:           ClassRegistry =     ClassRegistry(name = "environments")
ENVIRONMENT_COMMAND_REGISTRY:   CommandRegistry =   CommandRegistry(name = "environments")

# Registration decorators.
from lucidium.registries.decorators import  (
                                                register_agent,
                                                register_agent_command,
                                                register_environment,
                                                register_environment_command
                                            )