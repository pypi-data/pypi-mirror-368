"""# lucidium.agents.commands.play

Defines the game play process for agents.
"""

__all__ =   [
                # Argument parser registration.
                "register_play_parser",
                
                # Entry point.
                "main"
            ]

# Argument parser registration.
from lucidium.agents.commands.play.__args__ import register_play_parser

# Entry point.
from lucidium.agents.commands.play.__main__ import main