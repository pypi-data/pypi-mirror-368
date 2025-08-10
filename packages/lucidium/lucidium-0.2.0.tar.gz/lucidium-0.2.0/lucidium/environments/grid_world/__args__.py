"""# ludorum.environments.grid_world.args

Argument definitions & parsing for Grid World environment.
"""

__all__ = ["register_grid_world_parser"]

from argparse   import _ArgumentGroup, ArgumentParser, _SubParsersAction
from ast        import literal_eval
from typing     import Dict, List, Set, Tuple

def register_grid_world_parser(
    parent_subparser:   _SubParsersAction
) -> None:
    """# Register Grid World Parser.

    ## Args:
        * parent_subparser  (_SubParsersAction):    Parent's subparser object.
    """
    # Initialize Grid World game parser
    _parser_:       ArgumentParser =    parent_subparser.add_parser(
        name =          "grid-world",
        help =          """Grid World environment.""",
        description =   """Grid World is a simple, discrete, grid-based environment where an agent 
                        navigates the grid to achieve a goal. The environment consists of a grid 
                        with rows and columns, where each grid cell can have different attributes, 
                        such as obstacles, rewards, or special features."""
    )

    # +============================================================================================+
    # | BEGIN ARGUMENTS                                                                            |
    # +============================================================================================+
    
    # GRID DIMENSIONS ==============================================================================
    _dimensions_:   _ArgumentGroup =    _parser_.add_argument_group("Grid Dimensions")
    
    _dimensions_.add_argument(
        "--rows",
        type =      int,
        default =   4,
        help =      """Number of rows with which grid will be initialized. Defaults to 4."""
    )
    
    _dimensions_.add_argument(
        "--columns",
        type =      int,
        default =   4,
        help =      """Number of columns with which grid will be initialized. Defaults to 4."""
    )
    
    # GRID FEATURES ================================================================================
    _features_:     _ArgumentGroup =    _parser_.add_argument_group("Grid Features")
    
    _features_.add_argument(
        "--goal",
        type =      set_of_tuples,
        default =   None,
        help =      """Set of (row, column) coordinates at which goal square(s) will be located. Defaults to 
                    top-right corner of grid."""
    )
    
    _features_.add_argument(
        "--start",
        type =      tuple,
        default =   (0, 0),
        help =      """(row, column) coordinate at which agent will begin the game. Defaults to 
                    (0, 0) or the bottom-left corner of the grid."""
    )
    
    _features_.add_argument(
        "--loss",
        type =      set_of_tuples,
        default =   set(),
        help =      """Set of (row, column) coordinates at which loss sqaure(s) will be located. 
                    Example: "{(1, 0), ...}"."""
    )
    
    _features_.add_argument(
        "--walls",
        type =      set_of_tuples,
        default =   set(),
        help =      """Set of (row, column) coordinates at which wall square(s) will be located. 
                    Example: "{(1, 0), ...}"."""
    )
    
    _features_.add_argument(
        "--coins",
        type =      set_of_tuples,
        default =   set(),
        help =      """Set of (row, column) coordinates at which coin square(s) will be located. 
                    Example: "{(1, 0), ...}"."""
    )
    
    _features_.add_argument(
        "--portals",
        type =      list_of_dictionaries,
        default =   [],
        help =      """List of dictionaries mapping "entry" and "exit" coordinates at which portal 
                    components will be located. Example: "[{'entry': (1,0), 'exit': (0,1)}, 
                    ...]"."""
    )
    
    _features_.add_argument(
        "--wrap-map",
        dest =      "wrap_map",
        action =    "store_true",
        default =   False,
        help =      """Allow agent to pass through grid borders, such that it appears on the 
                    opposing side of the grid on boundery collisions. Example, if the agent is 
                    located at (0, 0), and submits the "DOWN" action, the agent's next position will 
                    be the top most row of column 0."""
    )
    
    # REWARDS & PENALTIES ==========================================================================
    _rewards_:      _ArgumentGroup =    _parser_.add_argument_group("Rewards & Penalties")
    
    _rewards_.add_argument(
        "--goal-reward",
        dest =      "goal_reward",
        type =      float,
        default =   1.0,
        help =      """Reward received when agent reaches goal square. Defaults to +1.0."""
    )
    
    _rewards_.add_argument(
        "--step-penalty",
        dest =      "step_penalty",
        type =      float,
        default =   -0.01,
        help =      """Cost for each action that the agent takes. Defaults to -0.01."""
    )
    
    _rewards_.add_argument(
        "--wall-penalty",
        dest =      "wall_penalty",
        type =      float,
        default =   -0.1,
        help =      """Penalty received in the case that the agent collides with a wall. Defaults 
                    to -0.1."""
    )
    
    _rewards_.add_argument(
        "--loss-penalty",
        dest =      "loss_penalty",
        type =      float,
        default =   -0.5,
        help =      """Penalty received in the case that the agent lands on a loss square. Defaults 
                    to -0.5."""
    )
    
    _rewards_.add_argument(
        "--coin-reward",
        dest =      "coin_reward",
        type =     float,
        default =   0.5,
        help =      """Reward received in the case that the agent lands on a coin square. Defaults 
                    to +0.5."""
    )

    # +============================================================================================+
    # | END ARGUMENTS                                                                              |
    # +============================================================================================+
    
# Define function for parsing set of tuples.
def set_of_tuples(
    arg:    str
) -> Set[Tuple[int, ...]]:
    """# Parse Set of Tuples.
    
    Parse string argument into set of tuples of integers.

    ## Args:
        * arg   (str):  Argument being passed.

    ## Returns:
        * Set[Tuple[int, ...]]:    Set of tuples of integers.
    """
    return  literal_eval(arg)
    
# Define function for parsing list of dictionaries.
def list_of_dictionaries(
    arg:    str
) -> List[Dict[str, int]]:
    """# Parse List of Dictionaries.
    
    Parse string argument into list of dictionaries of string to tuples of integers.

    ## Args:
        * arg   (str):  Argument being passed.

    ## Returns:
        * List[Dict[str, int]]: List of dictionaries.
    """
    return  literal_eval(arg)