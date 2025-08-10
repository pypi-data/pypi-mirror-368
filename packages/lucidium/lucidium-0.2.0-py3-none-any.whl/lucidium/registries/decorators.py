"""# lucidium.registries.decorators

Registration decorators for agents/environments.
"""

__all__ = ["register_agent", "register_environment"]

from typing import Callable, List, Optional, Type

def register_agent(
    name:           str,
    tags:           Optional[List[str]] =   [],
    entry_point:    Optional[Callable] =    None,
    parser:         Optional[Callable] =    None
) -> Callable:
    """# Register Agent.

    ## Args:
        * name          (str):                  Name of agent registration entry.
        * tags          (Optional[List[str]]):  Tags that describe the agent's taxonomy.
        * entry_point   (Optional[Callable]):   Agent's main process entry point.
        * parser        (Optional[Callable]):   Agent's argument registration handler.

    ## Returns:
        * Callable: Registration decorator.
    """
    # Define decorator.
    def decorator(
        cls:    Type
    ) -> Type:
        """# Registration Decorator

        ## Args:
            * cls   (Type): Agent class being registered.
        """
        # Load registry.
        from lucidium.registries    import AGENT_REGISTRY
        
        # Register agent.
        AGENT_REGISTRY.register(
            cls =           cls,
            name =          name,
            tags =          tags,
            entry_point =   entry_point,
            parser =        parser
        )
        
        # Return registered class.
        return cls
    
    # Expose decorator.
    return decorator

def register_agent_command(
    name:           str,
    parser:         Callable
) -> Callable:
    """# Register Agent Command.

        ## Args:
            * name          (str):      Name of command.
            * entry_point   (Callable): Command's main process entry point.
            * parser        (Callable): Command argument parser registeration handler.

    ## Returns:
        * Callable: Registration decorator.
    """
    # Define decorator.
    def decorator(
        entry_point:    Callable
    ) -> Callable:
        """# Agent Command Registration Decorator.

        ## Args:
            * entry_point   (Callable): Command's main process entry point.
        """
        # Load registry.
        from lucidium.registries    import AGENT_COMMAND_REGISTRY
        
        # Register agent command.
        AGENT_COMMAND_REGISTRY.register(
            name =          name,
            entry_point =   entry_point,
            parser =        parser
        )
        
        # Return entry point.
        return entry_point
    
    # Expose decorator.
    return decorator

def register_environment(
    name:           str,
    tags:           Optional[List[str]] =   [],
    entry_point:    Optional[Callable] =    None,
    parser:         Optional[Callable] =    None
) -> Callable:
    """# Register Environment.

    ## Args:
        * name          (str):                  Name of environment registration entry.
        * tags          (Optional[List[str]]):  Tags that describe the environment's taxonomy.
        * entry_point   (Optional[Callable]):   Environment's main process entry point.
        * parser        (Optional[Callable]):   Environment's argument registration handler.

    ## Returns:
        * Callable: Registration decorator.
    """
    # Define decorator.
    def decorator(
        cls:    Type
    ) -> Type:
        """# Registration Decorator

        ## Args:
            * cls   (Type): Environment class being registered.
        """
        # Load registry.
        from lucidium.registries    import ENVIRONMENT_REGISTRY
        
        # Register environment.
        ENVIRONMENT_REGISTRY.register(
            cls =           cls,
            name =          name,
            tags =          tags,
            entry_point =   entry_point,
            parser =        parser
        )
        
        # Return registered class.
        return cls
    
    # Expose decorator.
    return decorator

def register_environment_command(
    name:           str,
    parser:         Callable
) -> Callable:
    """# Register Environment Command.

        ## Args:
            * name          (str):      Name of command.
            * entry_point   (Callable): Command's main process entry point.
            * parser        (Callable): Command argument parser registeration handler.

    ## Returns:
        * Callable: Registration decorator.
    """
    # Define decorator.
    def decorator(
        entry_point:    Callable
    ) -> Callable:
        """# Environment Command Registration Decorator.

        ## Args:
            * entry_point   (Callable): Command's main process entry point.
        """
        # Load registry.
        from lucidium.registries    import ENVIRONMENT_COMMAND_REGISTRY
        
        # Register environment command.
        ENVIRONMENT_COMMAND_REGISTRY.register(
            name =          name,
            entry_point =   entry_point,
            parser =        parser
        )
        
        # Return entry point.
        return entry_point
    
    # Expose decorator.
    return decorator