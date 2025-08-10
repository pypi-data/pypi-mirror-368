"""# lucidium.agents.nlm.layers

This package defines the various layer components of the Neural Logic Machine.
"""

__all__ =   [
                "DimensionExpander",
                "DimensionPermuter",
                "DimensionReducer",
                "LinearLayer",
                "LogicLayer",
                "MLPLayer"
            ]

from lucidium.agents.nlm.layers.expansion   import DimensionExpander
from lucidium.agents.nlm.layers.permutation import DimensionPermuter
from lucidium.agents.nlm.layers.reduction   import DimensionReducer
from lucidium.agents.nlm.layers.linear      import LinearLayer
from lucidium.agents.nlm.layers.logic       import LogicLayer
from lucidium.agents.nlm.layers.mlp         import MLPLayer