"""# lucidium.spaces.multi_discrete

Defines a multi-discrete space (vector of discrete values).
"""

__all__ = ["MultiDiscrete"]

from random                     import randint
from typing                     import Tuple

from lucidium.spaces.__base__   import Space

class MultiDiscrete(Space):
    """# Multi-Discrete (Space)
    
    Vector-valued discrete space.
    """
    
    def __init__(self,
        shape:  Tuple[int, ...]
    ):
        """# Instantiate Multi-Discrete (Space).

        ## Args:
            * shape (Tuple[int, ...]):  Shape of space. Each dimension d will contain shape[d] 
                                        elements.
        """
        # Define shape.
        self._shape_:   Tuple[int, ...] =   shape
        
        # Validate parameters.
        self.__post_init__()
        
    def __post_init__(self) -> None:
        """# Validate Parameters.
        
        ## Raises:
            * AssertionError:   If any dimension of shape is not a positive integer.
        """
        return all(d > 0 for d in self.shape)
    
    # PROPERTIES ===================================================================================
    
    @property
    def shape(self) -> Tuple[int, ...]:
        """# (Multi-Discrete Space) Shape

        Represents the number of elements contained in each dimension of space.
        """
        return self._shape_
    
    # METHODS ======================================================================================
    
    def contains(self,
        v:  Tuple[int, ...]
    ) -> bool:
        """# (Multi-Discrete Space) Contains?

        ## Args:
            * v (Tuple[int, ...]):  Vector value being verified.

        ## Returns:
            * bool: True if v ∈ S.
        """
        return  all([
                    isinstance(v, tuple),
                    len(v) == len(self.shape),
                    all(
                        0 <= v_i < dimension
                        for v_i, dimension
                        in zip(v, self.shape)
                    )
                ])
        
    def sample(self) -> Tuple[int, ...]:
        """# Sample (Multi-Discrete Space).

        ## Returns:
            * Tuple[int, ...]:  Random vector value within space.
        """
        return (randint(0, dimension - 1) for dimension in self.shape)
    
    # DUNDERS ======================================================================================
    
    def __repr__(self) -> str:
        """# Object Representation.

        Object representation of multi-discrete space.
        """
        return f"<MultiDiscrete(shape = {self.shape})>"