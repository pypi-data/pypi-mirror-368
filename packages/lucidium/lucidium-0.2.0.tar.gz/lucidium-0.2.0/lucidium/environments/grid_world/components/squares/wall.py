"""# lucidium.environments.grid_world.components.squares.wall

Defines the wall square component of Grid World environment.
"""

__all__ = ["Wall"]

from typing                                                         import Any, Dict, override, Optional, Tuple

from lucidium.environments.grid_world.components.squares.__base__   import Square

class Wall(Square):
    """# (Grid World) Wall
    
    Wall square representation.
    """
    
    def __init__(self,
        coordinate: Tuple[int, int],
        value:      Optional[float] =   -0.1
    ):
        """# Instantiate Wall (Square).

        ## Args:
            * coordinate    (Tuple[int, int]):  Row and column at which square is located in grid.
            * value         (float):            Penalty incurred for colliding with wall. Defaults to -0.1.
        """
        # Instantiate square.
        super(Wall, self).__init__(coordinate = coordinate, value = value)
        
        # Override walkable property.
        self._walkable_:    bool =  False
        
    # METHODS ======================================================================================
    
    @override
    def interact(self) -> Tuple[Tuple[int, int], float, bool, Dict[str, Any]]:
        """# Interact with Wall (Square).

        ## Returns:
            * Tuple[int, int]:  Square's location.
            * float:            Penalty incurred for colliding with wall.
            * bool:             True if square represents a terminal state.
            * Dict[str, Any]:   Description of interaction event.
        """
        # Increment interaction count.
        self._interactions_ += 1
        
        # Return interaction result.
        return None, self.value, self.is_terminal, {"event": "collided with wall"}
    
    # DUNDERS ======================================================================================
    
    @override
    def __repr__(self) -> str:
        """# (Wall) Object Representation"""
        return f"""<Wall(coordinate = {self.coordinate}, value = {self.value})>"""
    
    @override
    def __str__(self) -> str:
        """# (Wall) String Representation"""
        return "█"