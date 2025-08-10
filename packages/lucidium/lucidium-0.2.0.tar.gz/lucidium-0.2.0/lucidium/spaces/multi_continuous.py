"""# lucidium.spaces.multi_continuous

Defines a multi-dimensional continuous space.
"""

__all__ = ["MultiContinuous"]

from random                     import uniform
from typing                     import Tuple, Union

from lucidium.spaces.__base__   import Space

class MultiContinuous(Space):
    """# Multi-Continuous (Space)

    Vector-valued continuous space.
    """
    
    def __init__(self,
        bounds: Tuple[Tuple[Union[float, int], Union[float, int]]]
    ):
        # Define bounds.
        self._bounds_:  Tuple[Tuple[Union[float, int], Union[float, int]]] =    bounds
        
    def __post_init__(self) -> None:
        """# Validate Parameters.
        
        ## Raises:
            * AssertionError:   If any dimension's upper bound is less than its corresponding lower 
                                bound.
        """
        # For each dimension...
        for d, dimension in enumerate(self.bounds, start = 1):
            
            # Assert that upper bound is greater than lower bound.
            assert dimension[0] < dimension[1], \
                f"Dimension {d}: Upper bound {dimension[1]} must be greater than lower bound {dimension[0]}"
        
    # PROPERTIES ===================================================================================
    
    @property
    def bounds(self) -> Tuple[Tuple[float, float]]:
        """# (Multi-Continuous Space) Bounds.

        ## Returns:
            * Tuple[Tuple[float, ...]]: Multi-dimensional bounds of space.
        """
        return self._bounds_
    
    # METHODS ======================================================================================
    
    def contains(self,
        v:  Tuple[Union[float, int], ...]
    ) -> bool:
        """# (Multi-Continuous Space) Contains?

        ## Args:
            * v (Tuple[Union[float, int], ...]):    Vector value being verified.

        ## Returns:
            * bool: True if v ∈ S.
        """
        return  all([
                    isinstance(v, tuple),
                    len(v) == len(self.bounds),
                    all(
                        bound[0] <= v_i < bound[1]
                        for v_i, bound
                        in zip(v, self.bounds)
                    )
                ])
        
    def sample(self) -> Tuple[float, ...]:
        """# Sample (Multi-Continuous Space).

        ## Returns:
            * Tuple[float, ...]:    Random vector value from space.
        """
        return (uniform(bound[0], bound[1]) for bound in self.bounds)
    
    # DUNDERS ======================================================================================
    
    def __repr__(self) -> str:
        """# Object Representation.

        Object representation of multi-continuous space.
        """
        return f"<MultiContinuous(bounds = {self.bounds})>"