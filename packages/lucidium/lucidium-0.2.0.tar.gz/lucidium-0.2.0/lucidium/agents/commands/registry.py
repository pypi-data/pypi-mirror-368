"""# lucidium.agents.commands.registry

Define agent commands registry.
"""

__all__ = ["AGENT_COMMAND_REGISTRY"]

from argparse                   import _SubParsersAction
from typing                     import Callable, Dict

from lucidium.agents.commands   import play

# Define agent commands registry.
AGENT_COMMAND_REGISTRY: Dict[str, Dict[str, Callable]] =    {
                                                                "play": {
                                                                            "parser":   play.register_play_parser,
                                                                            "entry":    play.main
                                                                }
                                                            }

# Define argument registration.
def register_agent_command_parsers(self,
    parent_subparser:   _SubParsersAction
) -> None:
    """# Register Agent Command Parsers.

    ## Args:
        * parent_subparser  (_SubParsersAction): Parent's subparser.
    """
    # For each registered command...
    for command in AGENT_COMMAND_REGISTRY.values:
        
        # Register it's arguments with the agent's parser.
        command["parser"](parent_subparser = parent_subparser)