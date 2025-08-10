"""# lucidium.spaces.continuous

Defines a continuous space for real-valued scalar actions or observations.
"""

__all__ = ["Continuous"]

from math                       import inf
from random                     import uniform
from typing                     import Tuple, Union

from lucidium.spaces.__base__   import Space

class Continuous(Space):
    """# Continuous (Space)

    Scalar-valued continuous space.
    """
    
    def __init__(self,
        lower:  Union[float, int] = -inf,
        upper:  Union[float, int] =  inf
    ):
        """# Instantiate Continuous (Space).

        ## Args:
            * lower (float):    Lower bound. Defaults to negative infinity.
            * upper (float):    Upper bound. Defaults to positive infinity.
        """
        # Define bounds.
        self._lower_:   Union[float, int] = float(lower)
        self._upper_:   Union[float, int] = float(upper)
        
        # Validate parameters.
        self.__post_init__()
        
    def __post_init__(self) -> None:
        """# Validate Parameters.
        
        ## Raises:
            * AssertionError:   If upper bound is less than lower bound.
        """
        assert self.upper > self.lower, \
            f"Upper bound {self.upper} must be greater than lower bound {self.lower}"
        
    # PROPERTIES ===================================================================================
    
    @property
    def bounds(self) -> Tuple[float, float]:
        """# (Continuous Space) Bounds

        Lower and upper bounds of space.
        """
        return self.lower, self.upper
    
    @property
    def lower(self) -> float:
        """# (Continuous Space) Lower Bound

        Lower bound of continuous space range.
        """
        return self._lower_
    
    @property
    def upper(self) -> float:
        """# (Continuous Space) Upper Bound

        Upper bound of continuous space range.
        """
        return self._upper_
    
    # METHODS ======================================================================================
    
    def contains(self,
        x:  Union[float, int]
    ) -> bool:
        """# (Continuous Space) Contains?

        ## Args:
            * x (Union[float, int]):    Scalar value being verified.

        ## Returns:
            * bool: True if x ∈ S.
        """
        return isinstance(x, (float, int)) and self.lower <= x < self.upper
    
    def sample(self) -> float:
        """# Sample (Continuous Space).
        
        Get a random number in the range [min, max) or [min, max] depending on rounding.

        ## Returns:
            * float:    Random scalar value from space.
        """
        return uniform(self.lower, self.upper)
    
    # DUNDERS ======================================================================================
    
    def __repr__(self) -> str:
        """# Object Representation.

        Object representation of continuous space.
        """
        return f"<Continuous(lower = {self.lower}, upper = {self.upper})>"