"""# lucidium.environments.grid_world.components.squares.coin

Defines the coin square component of Grid World environment.
"""

__all__ = ["Coin"]

from typing                                                         import Any, Dict, override, Optional, Tuple

from termcolor                                                      import colored

from lucidium.environments.grid_world.components.squares.__base__   import Square

class Coin(Square):
    """# (Grid World) Coin

    Coin square representation.
    """
    
    def __init__(self,
        coordinate: Tuple[int, int],
        value:      Optional[float] =   0.5
    ):
        """# Instantiate Coin (Square).

        ## Args:
            * coordinate    (Tuple[int, int]):  Row and column at which square is located in grid.
            * value         (float):            Reward yielded for collecting coin. Defaults to 
                                                +0.5.
        """
        # Instantiate square.
        super(Coin, self).__init__(coordinate = coordinate, value = value)
        
        # Define initial state.
        self._collected_:   bool =  False
        
    # PROPERTIES ===================================================================================
    
    @property
    def was_collected(self) -> bool:
        """# (Coin) Was Collected?

        True if coin was already collected.
        """
        return self._collected_
    
    @override
    @property
    def value(self) -> float:
        """# (Coin's) Value

        Reward yielded by collecting coin or penalty for revisiting square.
        """
        return -self._value_ if self.was_collected else self._value
    
    # METHODS ======================================================================================
    
    @override
    def interact(self) -> Tuple[Tuple[int, int], float, bool, Dict[str, Any]]:
        """# Interact with Coin (Square).

        ## Returns:
            * Tuple[int, int]:  Square's location.
            * float:            Reward yielded by collecting coin or penalty for revisiting square.
            * bool:             True if square represents a terminal state.
            * Dict[str, Any]:   Description of interaction event.
        """
        # Increment interaction count.
        self._interactions_ += 1
        
        # If coin has already been collected...
        if self.was_collected:
            
            # Simply assign penalty.
            return self.coordinate, self.value, self.is_terminal, {"event": "landed on empty square"}
        
        # Otherwise, store reward.
        reward:             float = self.value
        
        # Collect coin.
        self._collected_:   bool =  True
        
        # Return interaction result.
        return self.coordinate, reward, self.is_terminal, {"event": "collected a coin"}
    
    @override
    def reset(self) -> None:
        """# Reset (Coin).
        
        Reset coin square to initial state.
        """
        # Reset collected flag.
        self._collected_:       bool =  False
        
        # Reset ineraction count.
        self._interactions_:    int =   0
        
    # DUNDERS ======================================================================================
    
    @override
    def __repr__(self) -> str:
        """# (Coin) Object Representation"""
        return f"""<Coin(coordinate = {self.coordinate}, value = {self.value}, collected = {self.was_collected})>"""
    
    @override
    def __str__(self) -> str:
        """# (Coin) String Representation"""
        return " " if self.was_collected else colored(text = "$", color = "yellow")