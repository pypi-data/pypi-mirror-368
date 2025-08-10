"""# ludorum.environments.grid_world.actions

Defines actions available in Grid World environment.
"""

__all__ = ["GridWorldActions"]

from typing             import Dict, Tuple, Union

from lucidium.spaces    import Discrete

class GridWorldActions(Discrete):
    """# Grid World Actions
    
    Discrete(n = 4) space representation of possible agent movements in 2D Grid World.
    """
    
    def __init__(self):
        """# Instantiate Grid World Actions (Space)."""
        # Initialize space.
        super(GridWorldActions, self).__init__(n = 4)
        
        # Define actions.
        self._actions_: Dict[int, Dict[str, Union[str, Tuple[int, int]]]] = {
                                                                                0:  {
                                                                                        "name":     "up",
                                                                                        "delta":    (-1, 0),
                                                                                        "symbol":   "↑"
                                                                                    },
                                                                                1:  {
                                                                                        "name":     "down",
                                                                                        "delta":    (1, 0),
                                                                                        "symbol":   "↓"
                                                                                    },
                                                                                2:  {
                                                                                        "name":     "left",
                                                                                        "delta":    (0, -1),
                                                                                        "symbol":   "←"
                                                                                    },
                                                                                3:  {
                                                                                        "name":     "right",
                                                                                        "delta":    (0, 1),
                                                                                        "symbol":   "→"
                                                                                    }
                                                                            }
        
    # METHODS ======================================================================================
    
    def get_delta(self,
        index:  int
    ) -> str:
        """# Get (Action) Delta.

        ## Args:
            * index (int):  Index of action whose delta is being fetched.

        ## Returns:
            * str:  Action's delta.
        """
        return self[index]["delta"]
    
    def get_name(self,
        index:  int
    ) -> str:
        """# Get (Action) Name.

        ## Args:
            * index (int):  Index of action whose name is being fetched.

        ## Returns:
            * str:  Action's name.
        """
        return self[index]["name"]
    
    def get_symbol(self,
        index:  int
    ) -> str:
        """# Get (Action) Symbol.

        ## Args:
            * index (int):  Index of action whose symbol is being fetched.

        ## Returns:
            * str:  Action's symbol.
        """
        return self[index]["symbol"]
    
    # DUNDERS ======================================================================================
    
    def __getitem__(self,
        index:  int
    ) -> Dict[str, Union[str, Tuple[int, int]]]:
        """# Get Item.

        ## Returns:
            * Dict[str, Union[str, Tuple[int, int]]]:   Action property mapping.
        """
        return self._actions_[index]
    
    def __len__(self) -> int:
        """# Number of Actions"""
        return len(self._actions_)