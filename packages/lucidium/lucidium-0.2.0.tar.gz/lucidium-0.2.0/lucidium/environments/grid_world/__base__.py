"""# lucidium.environments.grid_world.base

Defines the Grid World environment.
"""

__all__ = ["GridWorld"]

from typing                                         import Any, Dict, List, override, Optional, Set, Tuple

from lucidium.environments.__base__                 import Environment
from lucidium.environments.grid_world.__args__      import register_grid_world_parser
from lucidium.environments.grid_world.actions       import GridWorldActions
from lucidium.environments.grid_world.components    import Grid
from lucidium.registries                            import register_environment
from lucidium.spaces                                import Discrete

@register_environment(
    name =      "grid-world",
    tags =      ["game", "single-player", "planning", "navigation"],
    parser =    register_grid_world_parser
)
class GridWorld(Environment):
    """# Grid World (Environment).
    
    Discrete, deterministic grid environment.
    """
    
    def __init__(self,
        # Dimensions.
        rows:               Optional[int] =                                 4,
        columns:            Optional[int] =                                 4,
        
        # Features.
        start:              Optional[Tuple[int, int]] =                     (0, 0),
        goal:               Optional[Set[Tuple[int, int]]] =                None,
        loss:               Optional[Set[Tuple[int, int]]] =                set(),
        walls:              Optional[Set[Tuple[int, int]]] =                set(),
        coins:              Optional[Set[Tuple[int, int]]] =                set(),
        portals:            Optional[List[Dict[str, Tuple[int, int]]]] =    [],
        wrap_map:           Optional[bool] =                                False,
        
        # Rewards/Penalties.
        goal_reward:        Optional[float] =                                1.0,
        step_penalty:       Optional[float] =                               -0.01,
        collision_penalty:  Optional[float] =                               -0.1,
        loss_penalty:       Optional[float] =                               -1.0,
        coin_reward:        Optional[float] =                                0.5,
        **kwargs
    ):
        """# Instantiate Grid World Environment.
        
        NOTE: Column indices are in order from left to right, but row indices are in reverse order 
        (from bottom to top).

        ## Dimensions:
            * rows              (int):                              Number of rows with which grid 
                                                                    will be initialized (max = 10). 
                                                                    Defaults to 4.
            * columns           (int):                              Number of columns with which 
                                                                    grid will be initialized (max = 
                                                                    10). Defaults to 4.

        ## Features:
            * coins             (Set[Tuple[int, int]]):             Set of coordinates at which coin 
                                                                    squares will be located within 
                                                                    grid.
            * goal              (Set[Tuple[int, int]]):             Coordinate at which the goal 
                                                                    square will be located in the 
                                                                    grid. Defaults to the top right 
                                                                    corner.
            * loss              (Set[Tuple[int, int]]):             Set of coordinates at which loss 
                                                                    squares will be located within 
                                                                    grid.
            * portals           (List[Dict[str, Tuple[int, int]]]): List of entry -> exit coordinate 
                                                                    mappings at which portal entries 
                                                                    and exits will be located within 
                                                                    grid.
            * start             (Tuple[int, int]):                  Coordinate at which the agent 
                                                                    will begin the game at the start 
                                                                    of each episode. Defaults to 
                                                                    (0, 0) (bottom left corner).
            * walls             (Set[Tuple[int, int]]):             Set of coordinates at which wall 
                                                                    squares will be located within 
                                                                    grid.
            * wrap_map          (bool):                             If true, the agent will not 
                                                                    collide with grid boundaries, 
                                                                    but will instead appear at the 
                                                                    opposite side of the grid.

        ## Rewards/Penalties:
            * coin_reward       (float):                            Reward yielded by collecting 
                                                                    coins. NOTE: Coins are ephemeral 
                                                                    (they can only be collected once 
                                                                    per episode). If coin has 
                                                                    already been collected, the 
                                                                    penalty incurred for re-entering 
                                                                    the square will be the negative 
                                                                    of the reward.
            * collision_penalty (float):                            Penalty incurred for colliding 
                                                                    with wall squares or the grid 
                                                                    boundary (if wrap_map == False).
            * goal_reward       (float):                            Reward yielded by reaching goal 
                                                                    square.
            * loss_penalty      (float):                            Penalty incurred for landing on 
                                                                    loss square(s).
            * step_penalty      (float):                            Penalty incurred for each step 
                                                                    that the agent takes during an 
                                                                    episode.
        """
        # Instantiate grid.
        self._grid_:    Grid =              Grid(**{k: v for k, v in locals().items() if k != "self"})
        
        # Define possible actions.
        self._actions_: GridWorldActions =  GridWorldActions()
        
    # PROPERTIES ===================================================================================
    
    @override
    @property
    def action_space(self) -> Discrete:
        """# (Grid World) Action Space

        Possible Grid World actions.
        """
        return Discrete(n = len(self._actions_))
    
    @override
    @property
    def done(self) -> bool:
        """# (Grid World) is Done?

        True if agent has reached a goal or loss square.
        """
        return self._grid_.done
    
    @override
    @property
    def name(self) -> str:
        """# (Grid World) Name

        Grid World's proper name.
        """
        return "Grid World"
    
    @override
    @property
    def observation_space(self) -> Discrete:
        """# (Grid World) Observation Space

        Possible Grid World states.
        """
        return Discrete(n = (self._grid_.rows * self._grid_.columns))
    
    @override
    @property
    def statistics(self) -> Dict[str, Any]:
        """# (Grid World) Statistics

        Statistics pertaining to environment interaction.
        """
        return self._grid_.progress
    
    # METHODS ======================================================================================
    
    @override
    def reset(self) -> int:
        """# Reset (Grid World).
        
        Reset environment to initial state.

        ## Returns:
            * int:  Agent's initial state.
        """
        return self._grid_.reset()
        
    @override
    def step(self,
        action: int
    ) -> Tuple[int, float, bool, Dict[str, Any]]:
        """# Step.
        
        Apply agent's chosen action to environment.

        ## Args:
            * action    (int):  Action submitted by agent.

        ## Returns:
            * int:              Agent's new location (index).
            * float:            Reward yielded/penalty incurred by agent's action.
            * bool:             True if new location represents a terminal state.
            * Dict[str, Any]:   Description of interaction event.
        """
        # If game has already concluded, report error.
        if self.done: raise RuntimeError(f"Game has concluded. Call reset() to start new game.")
        
        # Otherwise, provide results of action.
        return self._grid_.move(action_delta = self._actions_[action]["delta"])
        
    # DUNDERS ======================================================================================
    
    def __repr__(self) -> str:
        """# (Grid World) Object Representation"""
        return f"""<GridWorld(shape = ({self._grid_.rows}, {self._grid_.columns}))>"""
    
    def __str__(self) -> str:
        """# (Grid World) String Representation"""
        return str(self._grid_)