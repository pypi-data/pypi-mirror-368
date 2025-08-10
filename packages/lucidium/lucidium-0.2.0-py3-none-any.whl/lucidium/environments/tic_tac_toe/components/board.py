"""# lucidium.environments.tic_tac_toe.components.board

Implementation of board component for tic-tac-toe.
"""

from typing                                             import List, Literal, Optional, Set, Tuple, Union

from torch                                              import tensor, Tensor

from lucidium.environments.tic_tac_toe.components.cell  import Cell
from lucidium.symbolic                                  import Predicate

class Board():
    """# (Tic-Tac-Toe) Board
    
    Board representation and utilities.
    """
    
    def __init__(self,
        size:   int =   3
    ):
        """# Instanstiate Board.

        ## Args:
            * size  (int):  Dimension of (square) board. Maximum is 10. Defaults to 3.
        """
        # Assert that size is in range 3 - 10.
        assert 3 <= size <= 10, f"Board size must be 3 - 10, got {size}"
        
        # Define properties.
        self._size_:    int =   size
        
        # Instantiate cells.
        self._grid_:    List[List[Cell]] =  [
                                                [
                                                    Cell(coordinate = (r, c)) 
                                                    for c in range(self._size_)
                                                ]
                                                for r in range(self._size_)
                                            ]
        
    # PROPERTIES ===================================================================================
    
    @property
    def available_moves(self) -> List[Tuple[int, int]]:
        """# Available Moves

        Coordinates of currently available moves.
        """
        return [(r, c) for r in range(self._size_) for c in range(self._size_) if self._grid_[r][c].is_empty]
    
    @property
    def has_winner(self) -> bool:
        """# (Game) has Winner?
        
        True if a player has won the game.
        """
        return any(self._line_is_a_win_(line) for line in self.lines)
    
    @property
    def is_draw(self) -> bool:
        """# (Game) is Draw?
        
        True if board is full and there is now winner.
        """
        return self.is_full and not self.has_winner
    
    @property
    def is_full(self) -> bool:
        """# (Board) is Full?

        True if no empty cells remain.
        """
        return all(not cell.is_empty for row in self._grid_ for cell in row)
    
    @property
    def lines(self) -> List[List[Cell]]:
        """# (Board) Lines

        Cell groupings for each row, column, & diagonal.
        """
        return  [[self._grid_[r][c] for c in range(self._size_)] for r in range(self._size_)]   +\
                [[self._grid_[c][r] for c in range(self._size_)] for r in range(self._size_)]   +\
                [[self._grid_[i][i] for i in range(self._size_)]]                               +\
                [[self._grid_[i][self._size_ - i - 1] for i in range(self._size_)]]
        
    # METHODS ======================================================================================
    
    def mark(self,
        row:    int,
        column: int,
        entry:  Union[str, int, Tensor]
    ) -> bool:
        """# Mark Cell.

        ## Args:
            * row       (int):                      Row containing cell to mark.
            * column    (int):                      Column containing cell to mark.
            * entry     (Union[str, int, Tensor]):  Player entry representation:
                * Symbol ("X", "O", " ")
                * Number (1, -1, 0)
                * One-hot tensor (e.g., [1, 0, 0])
                
        ## Returns:
            * bool: True if cell was marked.
        """
        return self._grid_[row][column].mark(entry = entry)
    
    def mark_by_index(self,
        index:  int,
        entry:  Union[str, int, Tensor]
    ) -> bool:
        """# Mark Cell by Index.

        ## Args:
            * index (int):                      Index of cell to mark
            * entry (Union[str, int, Tensor]):  Player entry representation:
                * Symbol ("X", "O", " ")
                * Number (1, -1, 0)
                * One-hot tensor (e.g., [1, 0, 0])
                
        ## Returns:
            * bool: True if cell was marked.
        """
        return self.mark(*self._index_to_coordinate_(index = index), entry = entry)
    
    def reset(self) -> None:
        """# Reset (Board).
        
        Reset board and all contained cells to their initial states.
        """
        # For each row...
        for row in self._grid_:
            
            # Reset each cell in row.
            for cell in row: cell.reset()
            
    def to_predicate(self) -> Set[Predicate]:
        """# (Board) to Predicate(s)
        
        Extract all symbolic predicates from the board state.

        ## Returns:
            * Set[Predicate]:   Predicate representation of board state.
        """
        # Initialize predicate set with positions.
        predicates: Set[Predicate] =    set(
                                            cell.to_predicate()
                                            for row in self._grid_
                                            for cell in row
                                        )
        
        # Analyze lines.
        predicates.update(self._extract_line_predicates_())
        
        # Discard any instances of None.
        predicates.discard(None)
        
        # Provide predicates.
        return predicates
            
    def to_tensor(self) -> Tensor:
        """# (Board) to Tensor

        ## Returns:
            * Tensor:   Board state as tensor (shape = size x size).
        """
        return  tensor(
                    [
                        [
                            cell.to_tensor().item()
                            for cell
                            in row
                        ]
                        for row
                        in self._grid_
                    ],
                    dtype = int
                )
            
    # HELPERS ======================================================================================
    
    def _analyze_line_(self,
        cells:      List[Cell],
        line_type:  Literal["row", "column", "diagonal"],
        line_index: int
    ) -> Optional[Predicate]:
        """# Analyze Line.
        
        Analuze line for applicable predicates.

        ## Args:
            * cells         (List[Cell]):   List of cells in line.
            * line_type     (str):          One of "row", "column", "diagonal", or "anti-diagonal".
            * line_index    (int):          Index of the line.

        ## Returns:
            * Predicate:    Predicate applicable to line, if any.
        """
        # Count positions in line.
        x_count:    int =   sum(1 for cell in cells if cell.entry == "X")
        o_count:    int =   sum(1 for cell in cells if cell.entry == "O")
        
        # If neither player has a position, no predicates apply.
        if x_count == 0 and o_count == 0:   return None
        
        # If both players have position(s), the line has been blocked.
        if x_count > 0 and o_count > 0:     return Predicate("blocked_line", (line_type, line_index))
        
        # If X occupies a line, but not O...
        if x_count > 0 and o_count == 0:
            
            # If X occupies the whole line, it's a win.
            if x_count == self._size_:      return Predicate("win", ("X", line_type, line_index))
            
            # Otherwise, specify how many positions X occupies.
            else:                           return Predicate(f"{x_count}_in_line", ("X", line_type, line_index))
        
        # If O occupies a line, but not O...
        if o_count > 0 and x_count == 0:
            
            # If O occupies the whole line, it's a win.
            if o_count == self._size_:      return Predicate("win", ("O", line_type, line_index))
            
            # Otherwise, specify how many positions O occupies.
            else:                           return Predicate(f"{o_count}_in_line", ("O", line_type, line_index))
    
    def _coordinate_to_index_(self,
        coordinate: Tuple[int, int]
    ) -> int:
        """# (Convert) to Index.
        
        Convert cell coordinate to board index.

        ## Args:
            * coordinate    (Tuple[int, int]):  Row, column coordinate being converted.

        ## Returns:
            * int:  Index equivalent of coordinate provided.
        """
        return coordinate[0] * self._size_ + coordinate[1]
    
    def _extract_line_predicates_(self) -> Set[Predicate]:
        """# Extract Line Predicates.
        
        Extract predicates pertaining to lines (rows, columns, diagonals).

        ## Returns:
            * Set[Predicate]:   Line-based predicates.
        """
        # Initialize predicate set.
        predicates: Set[Predicate] =    set()
        
        # For each row...
        for r in range(self._size_):
            
            # Extract cells.
            cells:  List[Cell] =    [self._grid_[r][c] for c in range(self._size_)]
            
            # Analyze row.
            predicates.add(self._analyze_line_(
                cells =         cells,
                line_type =     "row",
                line_index =    r
            ))
            
        # For each column...
        for c in range(self._size_):
            
            # Extract cells.
            cells:  List[Cell] =    [self._grid_[r][c] for r in range(self._size_)]
            
            # Analyze column.
            predicates.add(self._analyze_line_(
                cells =         cells,
                line_type =     "column",
                line_index =    c
            ))
            
        # Analyze main diagonal.
        predicates.add(self._analyze_line_(
            cells =         [self._grid_[i][i] for i in range(self._size_)],
            line_type =     "diagonal",
            line_index =    0
        ))
        
        # Analyze anti-diagonal.
        predicates.add(self._analyze_line_(
            cells =         [self._grid_[i][self._size_ - i - 1] for i in range(self._size_)],
            line_type =     "anti-diagonal",
            line_index =    0
        ))
        
        # Provide discovered predicates.
        return predicates
    
    def _index_to_coordinate_(self,
        index:  int
    ) -> Tuple[int, int]:
        """# (Convert) to Coordinate.
        
        Convert board index to cell coordinate.

        ## Args:
            * index (int):  Board index being converted.

        ## Returns:
            * Tuple[int, int]:  Coordinate equivalent of index provided.
        """
        return divmod(index, self._size_)
    
    def _line_is_a_win_(self,
        line:   List[Cell]
    ) -> bool:
        """# Line is a Win?

        ## Args:
            * line  (List[Cell]):   Cell grouping being verified.

        ## Returns:
            * bool: True if line if occupied by one player.
        """
        # If any cells are empty, there is no win.
        if any(cell.is_empty for cell in line): return False
        
        # Otherwise, indicate that only one player occupies all cells.
        return len({cell.entry for cell in line}) == 1
    
    # DUNDERS ======================================================================================
    
    def __repr__(self) -> str:
        """# Object Representation

        Object representation of board.
        """
        return f"<Board(size = {self._size_})>"
    
    def __str__(self) -> str:
        """# String Representation

        String representation of board.
        """
        # Predefine separation line and column index.
        line:           str =   ("\n   " + ("───┼" * (self._size_ - 1)) + ("─" * 3))
        grid_string:    str =   ("   ") + " ".join(f" {column} " for column in range(self._size_))
        
        # For each row in grid...
        for r, row in enumerate(self._grid_):
            
            # Render cell row.
            grid_string += f"\n {r} " + "│".join(f" {cell} " for cell in row)
            
            # Append line if not on last row.
            grid_string += line if r < self._size_ - 1 else ""
            
        # Return string representation.
        return grid_string