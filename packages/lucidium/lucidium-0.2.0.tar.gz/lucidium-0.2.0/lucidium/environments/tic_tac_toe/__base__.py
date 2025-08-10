"""# lucidium.environments.tic_tac_toe.base

Defines the Tic Tac Toe game framework.
"""

from functools                                      import cached_property
from logging                                        import Logger
from typing                                         import Any, Dict, List, override, Tuple, Union

from torch                                          import Tensor

from lucidium.environments.tic_tac_toe.__args__     import register_tic_tac_toe_parser
from lucidium.environments.tic_tac_toe.components   import *
from lucidium.environments.__base__                 import Environment
from lucidium.registries                            import register_environment
from lucidium.spaces                                import Box, Discrete
from lucidium.symbolic                              import Predicate
from lucidium.utilities                             import get_child

@register_environment(
    name =      "tic-tac-toe",
    tags =      ["game", "two-player", "turn-based", "discrete", "strategic"],
    parser =    register_tic_tac_toe_parser
)
class TicTacToe(Environment):
    """# Tic-Tac-Toe (Environment)
    
    Tic-Tac-Toe is a two-player game where players take turns marking a square in a 3x3 grid. The 
    first player to align three of their marks horizontally, vertically, or diagonally wins the 
    game.
    """
    
    def __init__(self,
        size:                   int =    3,
        win_reward:             float =  1.0,
        loss_penalty:           float = -1.0,
        draw_reward:            float =  0.0,
        invalid_move_penalty:   float = -0.5,
        move_penalty:           float = -0.1,
        **kwargs
    ):
        """# Instantiate Tic-Tac-Toe Environment

        ## Args:
            * size                  (int, optional):    Size of (square) board. Defaults to 3.
            * win_reward            (float, optional):  Reward yielded from winning a game. Defaults 
                                                        to 1.0.
            * loss_penalty          (float, optional):  Penalty incurred by losing a game. Defaults 
                                                        to -1.0.
            * draw_reward           (float, optional):  Reward yielded by ending game in a draw 
                                                        (neither player wins). Defaults to 0.0.
            * invalid_move_penalty  (float, optional):  Penalty incurred for attempting an invalid 
                                                        move. Defaults to -0.5.
            * move_penalty          (float, optional):  Cost of making a single move. Defaults to 
                                                        -0.1.
        """
        # Inititialize environment.
        super(TicTacToe, self).__init__(**kwargs)
        
        # Initialize logger.
        self.__logger__:                Logger =    get_child("tic-tac-toe")
        
        # Define environment properties
        self._size_:                    int =       size
        self._win_reward_:              float =     win_reward
        self._loss_penalty_:            float =     loss_penalty
        self._draw_reward_:             float =     draw_reward
        self._invalid_move_penalty_:    float =     invalid_move_penalty
        self._move_penalty_:            float =     move_penalty
        
        # Instantiate board.
        self._board_:                   Board =     Board(size = size)
        
        # Define players.
        self._player_x_:                Player =    Player.X
        self._player_o_:                Player =    Player.O
        self._current_player_:          Player =    self._player_x_
        self._winner_:                  Player =    Player.EMPTY
        
        # Log for debugging.
        self.__logger__.debug(f"Initialized TicTacToe environment ({locals()})")
        
    # PROPERTIES ===================================================================================
    
    @override
    @cached_property
    def action_space(self) -> Discrete:
        """# (Tic-Tac-Toe) Action Space"""
        return Discrete(n = self._size_ ** 2)
    
    @property
    def current_player(self) -> Player:
        """# Current Player"""
        return self._current_player_
    
    @property
    def done(self) -> bool:
        """# Game Over?
        
        True if game has a winner or has ended in a draw.
        """
        return self._board_.has_winner or self._board_.is_draw
    
    @override
    @cached_property
    def state_space(self) -> Box:
        """# (Tic-Tac-Toe) Observation Space"""
        return Box(lower = -1, upper = 1, shape = (self._size_, self._size_), dtype = int)
    
    @property
    def winner(self) -> Player:
        """# Winning Player."""
        return self._winner_
    
    # METHODS ======================================================================================
    
    @override
    def reset(self) -> Union[Tensor, List[Predicate]]:
        """# Reset (Environment).
        
        Reset environment to initial state.

        ## Returns:
            * Union[Tensor, List[Predicate]]:   Observation of environment state after reset.
        """
        # Reset board.
        self._board_.reset()
        
        # Initialize game state.
        self._current_player_:  Player =    self._player_x_
        self._winner_:          Player =    Player.EMPTY
        
        # Log action for debugging.
        self.__logger__.debug("Tic-Tac-Toe environment reset.")
        
        # Provide observation.
        return self._get_observation_()
    
    @override
    def step(self,
        action: int
    ) -> Tuple[Union[Tensor, List[Predicate]], float, bool, Dict[str, Any]]:
        """# Step
        
        Update environment based on action submitted.

        ## Args:
            * action    (int):  Action submitted by agent.

        ## Returns:
            * Tuple[Union[Tensor, List[Predicate]], float, bool, Dict[str, Any]]:
                * Updated state after action
                * Reward yielded/penalty incurred by action
                * True if environment has reached a terminal state
                * Metadata
        """
        # If game has already concluded, an action cannot be submitted.
        if self.done: raise RuntimeError(f"Game has already concluded. Call reset() to start a new game.")
        
        # Log action for debugging.
        self.__logger__.debug(f"Player {self._current_player_} submitted action: {action}")
        
        # If action is not valid...
        if  not self.action_space.contains(action) or \
            not self._board_.mark_by_index(index = action, entry = self._current_player_.symbol):
                
            # Assign penalty, but don't switch players.
            return  self._get_observation_(),   \
                    self._invalid_move_penalty_,\
                    False,                      \
                    {"event": f"Player {self._current_player_} attempted invalid move {action}"}
                    
        # If player made a winning move...
        if self._board_.has_winner:
            
            # Assign reward.
            return  self._get_observation_(),   \
                    self._win_reward_,          \
                    True,                       \
                    {"event": f"Player {self._current_player_} won the game."}
                    
        # If board is full...
        if self._board_.is_full:
            
            # Assign draw reward.
            return  self._get_observation_(),   \
                    self._draw_reward_,         \
                    True,                       \
                    {"event": f"Game ended in draw."}
                    
        # Otherwise, switch players.
        self._switch_player_()
                    
        # Assign cost of move.
        return  self._get_observation_(),   \
                self._move_penalty_,        \
                False,                      \
                {"event": f"Player {self._current_player_} made move {action}"}
                
    # HELPERS ======================================================================================
    
    def _get_observation_(self) -> Dict[str, Union[Tensor, List[Predicate]]]:
        """# Get Observation.
        
        Provide observation of environment's current state.

        ## Returns:
            * Dict[str, Union[Tensor, List[Predicate]]]:
                * "tensor":     Tensor state representation
                * "predicate":  Symbolic predicates that apply to current state
        """
        return  {
                    "tensor":       self._board_.to_tensor(),
                    "predicate":    self._board_.to_predicate()
                }
        
    def _switch_player_(self) -> None:
        """# Switch Player.

        Switch to current player's opponent.
        """
        self._current_player_: Player = self._current_player_.opponent
        
    def to_tensor(self) -> Tensor:
        """# Board to Tensor.
        
        Convert board state to tensor representation by aggregating cell tensors.

        ## Returns:
            * Tensor:   Board state as tensor (shape = size x size).
        """
        
        
    # DUNDERS ======================================================================================
    
    def __repr__(self) -> str:
        """# Object Representation"""
        return f"""TicTacToe(size = {self._size_})"""
    
    def __str__(self) -> str:
        """# String Representation"""
        return str(self._board_)