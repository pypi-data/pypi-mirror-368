"""# lucidium.agents.commands.play.args

Argument definitions and parsing for game play process.
"""

__all__ = ["register_play_parser"]

from argparse               import _ArgumentGroup, ArgumentParser, _SubParsersAction
from typing                 import Union

from lucidium.registries    import ENVIRONMENT_REGISTRY

def register_play_parser(
    parent_subparser:   _SubParsersAction
) -> None:
    """# Register Play Parser.
    
    Add parser for agent game play.

    ## Args:
        * parent_subparser  (_SubParsersAction):    Parent's sub-parser object.
    """
    # Initialize Q-Learning Agent parser.
    _parser_:           ArgumentParser =    parent_subparser.add_parser(
        name =          "play",
        help =          "Make agent play a game.",
        description =   """Initiate episodic game play process."""
    )
    
    _subparser_:        _SubParsersAction = _parser_.add_subparsers(
        dest =          "environment",
        help =          """Environment that agent will interact with."""
    )

    # +============================================================================================+
    # | BEGIN ARGUMENTS                                                                            |
    # +============================================================================================+
    
    # CONFIGURATION ================================================================================
    _configuration_:    _ArgumentGroup =    _parser_.add_argument_group(title = "Configuration")
    
    _configuration_.add_argument(
        "--episodes",
        dest =          "episodes",
        type =          int,
        default =       100,
        help =          """Number of episodes for which agent will interact with environment. Each 
                        episode will represent the agent playing the game from beginning to end. 
                        Defaults to 100."""
    )
    
    _configuration_.add_argument(
        "--max-steps",
        dest =          "max_steps",
        type =          int,
        default =       100,
        help =          """Maximum number of steps that the agent is allowed to take during an 
                        episode. If the agent reaches the limit, the episode will conclude, even if 
                        the agent has not reached a terminal environment state. Defaults to 100."""
    )
    
    # ANIMATION ====================================================================================
    _animation_:        _ArgumentGroup =    _parser_.add_argument_group(title = "Animation")
    
    _animation_.add_argument(
        "--animate",
        dest =          "animate",
        action =        "store_true",
        default =       False,
        help =          """Animate game play visualization."""
    )
    
    _animation_.add_argument(
        "--animation-rate",
        dest =          "animation_rate",
        type =          Union[float, int],
        default =       0.1,
        help =          """Rate at which animation display will be refreshed (in seconds). Defaults 
                        to 0.1 seconds."""
    )
    
    # RESULTS ======================================================================================
    _results_:          _ArgumentGroup =    _parser_.add_argument_group(title = "Results")
    
    _results_.add_argument(
        "--save-results", "--save",
        dest =          "save_results",
        action =        "store_true",
        default =       False,
        help =          """Save game results to JSON file."""
    )
    
    _results_.add_argument(
        "--save-path", "--save-to",
        dest =          "save_path",
        type =          str,
        default =       "output/games",
        help =          """Path at which game results will be saved. NOTE: Only applies if 
                        `--save-results` or `--save` flags are passed. Defaults to 
                        "./output/games/"."""
    )

    # +============================================================================================+
    # | END ARGUMENTS                                                                              |
    # +============================================================================================+
    
    # Register environment parsers.
    ENVIRONMENT_REGISTRY.register_parsers(parent_subparser = _subparser_)