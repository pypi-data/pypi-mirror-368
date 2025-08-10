"""# lucidium.agents.q_learning

This package implements the Q-Learning agent proposed in the 1992 paper by Watkins & Dayan.
"""

__all__ =   [
                # Agent class.
                "QLearning",
                
                # Main process.
                "main"
            ]

# Agent class.
from lucidium.agents.q_learning.__base__    import QLearning

# Main process.
from lucidium.agents.q_learning.__main__    import main