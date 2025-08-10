"""# lucidium.environments

This package defines the various type of reinforcement learning environments.
"""

__all__ =   [
                # Abstract environment class.
                "Environment",
                
                # Concrete environment classes.
                "BlockWorld",
                "GridWorld",
                "TicTacToe"
]

# Abstract environment class.
from lucidium.environments.__base__     import Environment

# Concrete environment classes.
from lucidium.environments.block_world  import BlockWorld
from lucidium.environments.grid_world   import GridWorld
from lucidium.environments.tic_tac_toe  import TicTacToe