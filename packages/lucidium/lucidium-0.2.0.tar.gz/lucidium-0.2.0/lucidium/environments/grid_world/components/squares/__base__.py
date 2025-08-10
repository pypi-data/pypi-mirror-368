"""# lucidium.environments.grid_world.components.sqaures.base

Defines the basic square component of Grid World environment.
"""

__all__ = ["Square"]

from typing import Any, Dict, Optional, Tuple

class Square():
    """# (Grid World) Square
    
    Basic square representation.
    """
    
    def __init__(self,
        coordinate: Tuple[int, int],
        value:      Optional[float] =   -0.01
    ):
        """# Instantiate Square.

        ## Args:
            * coordinate    (Tuple[int, int]):  Row and column at which square is located in grid.
            * value         (float):            Reward yielded/penalty incurred from interacting 
                                                with square. Defaults to -0.01.
        """
        # Define properties.
        self._coordinate_:          Tuple[int, int] =   coordinate
        self._terminal_:            bool =              False
        self._value_:               float =             value
        self._interactions_:        int =               0
        self._walkable_:            bool =              True
        
    # PROPERTIES ===================================================================================
    
    @property
    def column(self) -> int:
        """# (Square's) Column

        Column in which square is located within grid.
        """
        return self._coordinate_[1]
    
    @property
    def coordinate(self) -> Tuple[int, int]:
        """# (Square's) Coordinate/Grid Location

        The row, column coordinate at which square is located within grid.
        """
        return self._coordinate_
    
    @property
    def is_terminal(self) -> bool:
        """# (Square) is Terminal?

        True if square represents a terminal state/concludes interaction episode.
        """
        return self._terminal_
    
    @property
    def row(self) -> int:
        """# (Square's) Row

        Row in which square is located within grid.
        """
        return self._coordinate_[0]
    
    @property
    def value(self) -> float:
        """# (Square's) Value

        Reward yielded/penalty incurred from interacting with square.
        """
        return self._value_
    
    @property
    def interactions(self) -> int:
        """# (Square) Interactions

        Number of times that agent has interacted with square since initialization.
        """
        return self._interactions_
    
    # METHODS ======================================================================================
    
    def interact(self) -> Tuple[Optional[Tuple[int, int]], float, bool, Dict[str, Any]]:
        """# Interact With Square.

        ## Returns:
            * Tuple[int, int]:  Square's location.
            * float:            Reward yielded/penalty incurred by interacting with square.
            * bool:             True if square represents a terminal state.
            * Dict[str, Any]:   Description of interaction event.
        """
        # Increment interaction count.
        self._interactions_ += 1
        
        # Return interaction result.
        return self.coordinate, self.value, self.is_terminal, {"event": "landed on empty square"}
    
    def reset(self) -> None:
        """# Reset (Square).
        
        Reset square to initial state.
        """
        # Reset interaction count.
        self._interactions_:    int =   0
        
    # DUNDERS ======================================================================================
    
    def __repr__(self) -> str:
        """# (Square) Object Representation"""
        return f"""<Square(coordinate = {self.coordinate}, value = {self.value})>"""
    
    def __str__(self) -> str:
        """# (Square) String Representation"""
        return " "