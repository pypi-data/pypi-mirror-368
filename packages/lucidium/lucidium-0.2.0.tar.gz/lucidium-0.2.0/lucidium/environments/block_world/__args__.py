"""# lucidium.environments.block_world.args

Argument definitions and parsing for Block World environment.
"""

__all__ = ["register_block_world_parser"]

from argparse   import _ArgumentGroup, ArgumentParser, _SubParsersAction

def register_block_world_parser(
    parent_subparser:   _SubParsersAction
) -> None:
    """# Register Block World Argument Parser.

    ## Args:
        * parent_subparser  (_SubParsersAction):    Parent's sub-parser object.
    """
    # Initialize parser.
    _parser_:           ArgumentParser =    parent_subparser.add_parser(
        name =          "block-world",
        help =          "Block World environment.",
        description =   """BlockWorld is a classic AI planning domain where blocks can be stacked on 
                        top of each other or placed on a table. The goal is to rearrange blocks from 
                        an initial configuration to achieve a target configuration. This environment 
                        provides a rich domain for testing neuro-symbolic reinforcement learning 
                        approaches.""",
        epilog =    """Example usage: lucidium blockworld --nr-blocks 5 --random-order 
                    --move-penalty -0.1 --success-reward 10.0"""
    )
    
    # Define sub-parser for actions.
    _subparser_:        _SubParsersAction = _parser_.add_subparsers(
        title =         "action",
        description =   "Block World environment commands.",
        dest =          "action"
    )

    # +============================================================================================+
    # | BEGIN ARGUMENTS                                                                            |
    # +============================================================================================+
    
    # WORLD CONFIGURATION ==========================================================================
    _configuration_:    _ArgumentGroup =    _parser_.add_argument_group(
        title =         "World Configuration",
        description =   """Basic world setup parameters."""
    )
    
    _configuration_.add_argument(
        "--block-quantity",
        dest =          "block_quantity",
        type =          int,
        default =       4,
        choices =       range(2, 10),
        help =          """Number of blocks in world. Must be between 2 and 10. Defaults to 4."""
    )
    
    _configuration_.add_argument(
        "--one-stack",
        dest =          "one_stack",
        action =        "store_true",
        default =       False,
        help =          """Initialize blocks in one stack at the start of each episode."""
    )
    
    _configuration_.add_argument(
        "--random-order",
        dest =          "random_order",
        action =        "store_true",
        default =       False,
        help =          """Randomly permute block indices to preventmemorization of 
                        configuration."""
    )
    
    # DYNAMICS =====================================================================================
    _dynamics_:         _ArgumentGroup =    _parser_.add_argument_group(
        title =         "Interaction Dynamics",
        description =   """Configure environment dynamics and noise."""
    )
    
    _dynamics_.add_argument(
        "--fall-probability",
        dest =          "fall_probability",
        type =          float,
        default =       0.0,
        help =          """Probability that moved blocks fall to ground. Defaults to 0.0."""
    )
    
    _dynamics_.add_argument(
        "--no-effect-probability",
        dest =          "no_effect_probability",
        type =          float,
        default =       0.0,
        help =          """Probability that an action has no effect. Defaults to 0.0."""
    )
    
    # REWARD/PENALTY ===============================================================================
    _rewards_:          _ArgumentGroup =    _parser_.add_argument_group(
        title =         "Rewards/Penalties",
        description =   """Configure reward/penalty values."""
    )
    
    _rewards_.add_argument(
        "--success-reward",
        dest =          "success_reward",
        type =          float,
        default =       1.0,
        help =          """Reward yielded for achieving target block configuration. Defaults to 
                        1.0."""
    )
    
    _rewards_.add_argument(
        "--move-penalty",
        dest =          "move_penalty",
        type =          float,
        default =       -0.1,
        help =          """Cost of making any move during the game. Defaults to -0.1."""
    )
    
    _rewards_.add_argument(
        "--invalid-move-penalty",
        dest =          "invalid_move_penalty",
        type =          float,
        default =       -0.5,
        help =          """Penalty incurred for attempting an invalid move. Defaults to -0.5."""
    )

    # +============================================================================================+
    # | END ARGUMENTS                                                                              |
    # +============================================================================================+