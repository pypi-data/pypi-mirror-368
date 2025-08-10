"""# lucidium.environments.grid_world.components.squares.goal

Defines the goal square component of Grid World environment.
"""

__all__ = ["Goal"]

from typing                                                         import Any, Dict, override, Optional, Tuple

from termcolor                                                      import colored

from lucidium.environments.grid_world.components.squares.__base__   import Square

class Goal(Square):
    """# (Grid World) Goal
    
    Goal square representation.
    """
    
    def __init__(self,
        coordinate: Tuple[int, int],
        value:      Optional[float] =   1.0
    ):
        """# Instantiate Goal (Square).

        ## Args:
            * coordinate    (Tuple[int, int]):  Row and column at which square is located in grid.
            * value         (float):            Reward yielded for reaching goal square. Defaults 
                                                to +1.0.
        """
        # Instantiate square.
        super(Goal, self).__init__(coordinate = coordinate, value = value)
        
        # Override terminal property.
        self._terminal_:    bool =  True
        
    # METHODS ======================================================================================
    
    @override
    def interact(self) -> Tuple[Tuple[int, int], float, bool, Dict[str, Any]]:
        """# Interact with Goal (Square).

        ## Returns:
            * Tuple[int, int]:  Square's location.
            * float:            Reward yielded by reaching goal.
            * bool:             True if square represents a terminal state.
            * Dict[str, Any]:   Description of interaction event.
        """
        # Increment interaction count.
        self._interactions_ += 1
        
        # Return interaction result.
        return self.coordinate, self.value, self.is_terminal, {"event": "won (reached goal square)"}
        
    # DUNDERS ======================================================================================
    
    @override
    def __repr__(self) -> str:
        """# (Goal) Object Representation"""
        return f"""<Goal(coordinate = {self.coordinate}, value = {self.value})>"""
    
    @override
    def __str__(self) -> str:
        """# (Goal) String Representation"""
        return colored("◯", color = "green")