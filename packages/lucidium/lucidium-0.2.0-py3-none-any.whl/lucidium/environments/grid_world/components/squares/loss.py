"""# lucidium.environments.grid_world.components.squares.loss

Defines the loss square component of Grid World environment.
"""

__all__ = ["Loss"]

from typing                                                         import Any, Dict, override, Optional, Tuple

from termcolor                                                      import colored

from lucidium.environments.grid_world.components.squares.__base__   import Square

class Loss(Square):
    """# (Grid World) Loss
    
    Loss square representation.
    """
    
    def __init__(self,
        coordinate: Tuple[int, int],
        value:      Optional[float] =   -1.0
    ):
        """# Instantiate Loss (Square).

        ## Args:
            * coordinate    (Tuple[int, int]):  Row and column at which square is located in grid.
            * value         (float):            Penalty incurred for landing on loss square. 
                                                Defaults to -1.0.
        """
        # Instantiate square.
        super(Loss, self).__init__(coordinate = coordinate, value = value)
        
        # Override terminal property.
        self._terminal_:    bool =  True
        
    # METHODS ======================================================================================
    
    @override
    def interact(self) -> Tuple[Tuple[int, int], float, bool, Dict[str, Any]]:
        """# Interact with Loss (Square).

        ## Returns:
            * Tuple[int, int]:  Square's location.
            * float:            Penalty incurred for landing on loss square.
            * bool:             True if square represents a terminal state.
            * Dict[str, Any]:   Description of interaction event.
        """
        # Increment interaction count.
        self._interactions_ += 1
        
        # Return interaction result.
        return self.coordinate, self.value, self.is_terminal, {"event": "lost (reached loss square)"}
    
    # DUNDERS ======================================================================================
    
    @override
    def __repr__(self) -> str:
        """# (Loss) Object Representation"""
        return f"""<>Loss(coordinate = {self.coordinate}, value = {self.value})>"""
    
    @override
    def __str__(self) -> str:
        """# (Loss) String Representation"""
        return colored(text = "◯", color = "red")