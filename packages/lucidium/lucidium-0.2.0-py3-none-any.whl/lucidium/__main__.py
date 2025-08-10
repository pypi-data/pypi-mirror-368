"""# lucidium.main

Lucidium application driver.
"""

from argparse               import Namespace
from logging                import Logger
from typing                 import Any

from lucidium.__args__      import parse_lucidium_arguments
from lucidium.registries    import AGENT_REGISTRY, ENVIRONMENT_REGISTRY
from lucidium.utilities     import BANNER, get_logger

def main(*args, **kwargs) -> Any:
    """# Execute Application."""
    # Parse arguments.
    _arguments_:    Namespace = parse_lucidium_arguments()
    
    # Initialize logger.
    _logger_:       Logger =    get_logger(
                                    logger_name =   "lucidium",
                                    logging_level = _arguments_.logging_level,
                                    logging_path =  _arguments_.logging_path
                                )
    
    try:# Log banner.
        _logger_.info(BANNER)
        
        # If command corresponds to agents...
        if _arguments_.command in AGENT_REGISTRY:
            
            # Add agent to arguments.
            _arguments_.agent =         _arguments_.command
            
            # Dispatch agent.
            return AGENT_REGISTRY.dispatch(cls = _arguments_.command, **vars(_arguments_))
            
        # If command corresponds to environments...
        if _arguments_.command in ENVIRONMENT_REGISTRY:
            
            # Add environment to arguments.
            _arguments_.environment =   _arguments_.command
            
            # Dispatch environment.
            return ENVIRONMENT_REGISTRY.dispatch(cls = _arguments_.command, **vars(_arguments_))
    
    # Catch wildcard errors.
    except Exception as e:  _logger_.critical(f"Unexpected error: {e}", exc_info = True)
    
    # Exit gracefully.
    finally:                _logger_.debug("Exiting")

if __name__ == "__main__": main()