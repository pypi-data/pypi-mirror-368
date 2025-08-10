"""# lucidium.spaces

Defines various space definitions for actions and observations.
"""

__all__ =   [
                # Abstract space.
                "Space",
                
                # Box space.
                "Box",
                
                # Composite space.
                "Composite",
                
                # Continuous spaces.
                "Continuous",
                "MultiContinuous",
                
                # Discrete spaces.
                "Discrete",
                "MultiDiscrete"
            ]

# Abstract space.
from lucidium.spaces.__base__           import Space

# Box space.
from lucidium.spaces.box                import Box

# Composite space.
from lucidium.spaces.composite          import Composite

# Continuous spaces.
from lucidium.spaces.continuous         import Continuous
from lucidium.spaces.multi_continuous   import MultiContinuous

# Discrete spaces.
from lucidium.spaces.discrete           import Discrete
from lucidium.spaces.multi_discrete     import MultiDiscrete