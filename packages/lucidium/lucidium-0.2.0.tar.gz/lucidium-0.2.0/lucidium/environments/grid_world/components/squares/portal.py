"""# lucidium.environments.grid_world.components.squares.portal

Defines the portal square component of Grid World environment.
"""

__all__ = ["Portal"]

from typing                                                         import Any, Dict, override, Optional, Tuple

from lucidium.environments.grid_world.components.squares.__base__   import Square

class Portal(Square):
    """# (Grid World) Portal

    Portal square representation.
    """
    
    def __init__(self,
        coordinate:     Tuple[int, int],
        destination:    Tuple[int, int],
        value:          Optional[float] =   -0.01
    ):
        """# Instantiate Portal (Square).

        ## Args:
            * coordinate    (Tuple[int, int]):  Row and column at which square is located in grid.
            * destination   (Tuple[int, int]):  Coordinate at which agent will appear after 
                                                interacting with (entering) portal.
            * value         (float):            Penalty incurred for landing on loss square. 
                                                Defaults to -0.01.
        """
        # Instantiate square.
        super(Portal, self).__init__(coordinate = coordinate, value = value)
        
        # Define destination.
        self._destination_: Tuple[int, int] =   destination
        
    # METHODS ======================================================================================
    
    @override
    def interact(self) -> Tuple[Tuple[int, int], float, bool, Dict[str, Any]]:
        """# Interact with Portal (Square).

        ## Returns:
            * Tuple[int, int]:  Square's location.
            * float:            Penalty incurred for entering portal.
            * bool:             True if square represents a terminal state.
            * Dict[str, Any]:   Description of interaction event.
        """
        # Increment interaction count.
        self._interactions_ += 1
        
        # Return interaction result.
        return self._destination_, self.value, self.is_terminal, {"event": f"entered portal to {self._destination_}"}
    
    # DUNDERS ======================================================================================
    
    @override
    def __repr__(self) -> str:
        """# (Portal) Object Representation"""
        return f"""<Portal(coordinate = {self.coordinate}, value = {self.value}, destination = {self._destination_})>"""
    
    @override
    def __str__(self) -> str:
        """# (Portal) String Representation"""
        return "░"