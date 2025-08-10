"""# lucidium.environments.tic_tac_toe.args

Argument definitions and parsing for Tic-Tac-Toe environment.
"""

__all__ = ["register_tic_tac_toe_parser"]

from argparse   import _ArgumentGroup, ArgumentParser, _SubParsersAction

def register_tic_tac_toe_parser(
    parent_subparser:   _SubParsersAction
) -> None:
    """# Register Tic-Tac-Toe Argument Parser.

    ## Args:
        * parent_subparser  (_SubParsersAction):    Parent's sub-parser object.
    """
    # Initialize parser.
    _parser_:           ArgumentParser =    parent_subparser.add_parser(
        name =          "tic-tac-toe",
        help =          "Tic-Tac-Toe environment",
        description =   """Tic-Tac-Toe is a two-player game where players take turns marking a 
                        square in a 3x3 grid. The first player to align three of their marks 
                        horizontally, vertically, or diagonally wins the game. This environment 
                        provides a simple but strategic domain for testing neuro-symbolic 
                        reinforcement learning approaches.""",
        epilog =        """Example usage of creating a 4x4 Tic-Tac-Toe game with custom reward 
                        structure: lucidium tictactoe --size 4 --win-reward 2.0 
                        --invalid-move-penalty -1.0"""
    )
    
    # Define sub-parser for actions (train, play, analyze, etc.)
    _subparser_:        _SubParsersAction = _parser_.add_subparsers(
        title =         "action",
        description =   "Tic-Tac-Toe environment commands.",
        dest =          "action"
    )

    # +============================================================================================+
    # | BEGIN ARGUMENTS                                                                            |
    # +============================================================================================+
    
    # BOARD CONFIGURATION ==========================================================================
    _configuration_:    _ArgumentGroup =    _parser_.add_argument_group(
        title =         "Board Configuration",
        description =   """Basic game setup parameters."""
    )
    
    _configuration_.add_argument(
        "--size",
        dest =          "size",
        type =          int,
        default =       3,
        choices =       range(3, 11),
        help =          """Size of (square) game board. Must be between 3 and 10. Defaults to 3 for 
                        standard tic-tac-toe."""
    )
    
    # REWARD/PENALTY ===============================================================================
    _rewards_:          _ArgumentGroup =    _parser_.add_argument_group(
        title =         "Rewards/Penalties",
        description =   """Configure reward/penalty values."""
    )
    
    _rewards_.add_argument(
        "--win-reward",
        dest =          "win_reward",
        type =          float,
        default =       1.0,
        help =          """Reward yielded by winning the game. Defaults to 1.0."""
    )
    
    _rewards_.add_argument(
        "--loss-penalty",
        dest =          "loss_penalty",
        type =          float,
        default =       -1.0,
        help =          """Penalty incurred by losing the game. Defaults to -1.0."""
    )
    
    _rewards_.add_argument(
        "--draw-penalty",
        dest =          "draw_penalty",
        type =          float,
        default =       -0.0,
        help =          """Reward yielded/penalty incurred when game ends in a draw (Neither player 
                        wins). Defaults to -0.0."""
    )
    
    _rewards_.add_argument(
        "--invalid-move-penalty",
        dest =          "invalid_move_penalty",
        type =          float,
        default =       -0.5,
        help =          """Penalty incurred for attempting an invalid move. Defaults to -0.5."""
    )
    
    _rewards_.add_argument(
        "--move-penalty",
        dest =          "move_penalty",
        type =          float,
        default =       -0.1,
        help =          """Cost of making any move during the game. Defaults to -0.1."""
    )

    # +============================================================================================+
    # | END ARGUMENTS                                                                              |
    # +============================================================================================+