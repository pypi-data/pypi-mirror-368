"""# lucidium.spaces.base

Defines the abstract class representation for action and observation spaces.
"""

__all__ = ["Space"]

from abc    import ABC, abstractmethod
from typing import Any

class Space(ABC):
    """# Abstract Space

    Defines the abstract interface for an action or observation space.
    """
    
    # METHODS ======================================================================================
    
    @abstractmethod
    def contains(self,
        value:  Any
    ) -> bool:
        """(Space) Contains?
        
        ## Args:
            * value (Any):  Value being verified.

        True if value is an element of space.
        """
        pass
    
    @abstractmethod
    def sample(self) -> Any:
        """# Sample (Space).

        Randomly sample a valid element from space.
        """
        pass
    
    # DUNDERS ======================================================================================
    
    @abstractmethod
    def __repr__(self) -> str:
        """# Object Representation.

        Object representation of space.
        """
        pass