"""# lucidium.agents

This package defines various types of reinforcement learning agents.
"""

__all__ =   [
                # Abstract agent class.
                "Agent",
                
                # Concrete agent classes.
                "NeuralLogicMachine",
                "QLearning",
                "SARSA"
            ]

# Abstract agent class.
from lucidium.agents.__base__   import Agent

# Concrete agent classes.
from lucidium.agents.nlm        import NeuralLogicMachine
from lucidium.agents.q_learning import QLearning
from lucidium.agents.sarsa      import SARSA