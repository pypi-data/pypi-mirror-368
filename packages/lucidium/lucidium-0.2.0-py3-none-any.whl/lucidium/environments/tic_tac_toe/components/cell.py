"""# lucidium.environments.tic_tac_toe.components.cell

Implementation of cell component for tic-tac-toe board.
"""

from typing                                                 import Tuple, Union

from torch                                                  import Tensor

from lucidium.environments.tic_tac_toe.components.players   import Player
from lucidium.symbolic                                      import Predicate

class Cell():
    """(Tic-Tac-Toe) Cell

    Represents a single square on the Tic-Tac-Toe board.
    Tracks the occupying Player and supports symbolic and tensor interfaces.
    """
    
    def __init__(self,
        coordinate: Tuple[int, int]
    ):
        """# Instantiate Cell.

        ## Args:
            * coordinate    (Tuple[int, int]):  Row, column coordinate at which cell is located on 
                                                board.
        """
        # Define location.
        self._row_:         int =               coordinate[0]
        self._column_:      int =               coordinate[1]
        
        # Start with empty cell.
        self._player_:      Player =            Player.EMPTY
        
    # PROPERTIES ===================================================================================
    
    @property
    def coordinate(self) -> Tuple[int, int]:
        """# (Cell) Coordinate

        Row, column coordinate of cell.
        """
        return (self._row_, self._column_)
    
    @property
    def entry(self) -> str:
        """# (Cell) Entry

        Current entry in cell.
        """
        return self._player_.symbol
    
    @property
    def is_empty(self) -> bool:
        """# (Cell) is Empty?

        True if cell is empty.
        """
        return self._player_ == Player.EMPTY
    
    # METHODS ======================================================================================
    
    def mark(self,
        entry:  Union[str, int, Tensor]
    ) -> bool:
        """# Mark (Cell).

        ## Args:
            * entry (Union[str, int, Tensor]): Player entry representation:
                * Symbol ("X", "O", " ")
                * Number (1, -1, 0)
                * One-hot tensor (e.g., [1, 0, 0])
                
        ## Returns:
            * bool: True if cell was marked.
        """
        # If cell is not empty, it cannot be marked.
        if not self.is_empty: return False
        
        # Otherwise, mark cell.
        self._set_player_(player = entry)
        
        # Indicate that cell was marked.
        return True
    
    def reset(self) -> None:
        """# Reset (Cell).

        Reset cell to initial state.
        """
        self._player_: Player = Player.EMPTY
        
    def to_predicate(self) -> Predicate:
        """# (Cell) to Symbolic Representation

        ## Returns:
            * Predicate: Predicate representation of cell.
        """
        # If cell is empty, provide empty predicate.
        if self.is_empty: return Predicate("empty", (self._row_, self._column_))
        
        # Otherwise, provide predicate specifying player position.
        return Predicate("position", (self._player_.symbol, self._row_, self._column_))
    
    def to_tensor(self) -> Tensor:
        """# (Cell) to Tensor
        
        ## Returns:
            * Tensor:   Tensor encoding of player state.
        """
        return self._player_.to_tensor()
        
    # HELPERS ======================================================================================
    
    def _set_player_(self,
        player: Union[Player, str, int, Tensor]
    ) -> None:
        """# Set Player.

        ## Args:
            * entry (Union[Player, str, int, Tensor]): Player entry representation:
                * Player object
                * Symbol ("X", "O", " ")
                * Number (1, -1, 0)
                * One-hot tensor (e.g., [1, 0, 0])
        """
        # Match data type.
        match player:
            
            # Player object.
            case Player()   as p:   self._player_ = p
            
            # Symbol.
            case str()      as p:   self._player_ = Player.from_symbol(symbol = p)
            
            # Number.
            case int()      as p:   self._player_ = Player.from_number(number = p)
            
            # One-hot tensor.
            case Tensor()   as p:   self._player_ = Player.from_encoding(encoding = p)
            
            # Invalid representation.
            case _: raise TypeError(f"Player representation type not recognized: {player} ({type(player)})")
            
    # DUNDERS ======================================================================================
    
    def __repr__(self) -> str:
        """# Object Representation"""
        return f"""<Cell(row = {self._row_}, column = {self._column_}, player = {self._player_})>"""
    
    def __str__(self) -> str:
        """# String Representation"""
        return str(self._player_)