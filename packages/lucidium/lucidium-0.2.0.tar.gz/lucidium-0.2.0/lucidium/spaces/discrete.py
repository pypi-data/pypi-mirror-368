"""# lucidium.spaces.discrete

Defines a discrete (integer-indexed) space.
"""

__all__ = ["Discrete"]

from random                     import randint

from lucidium.spaces.__base__   import Space

class Discrete(Space):
    """# Discrete (Space)

    Scalar-valued discrete space.
    """
    
    def __init__(self,
        n:  int
    ):
        """# Instantiate Discrete (Space).

        ## Args:
            * n (int):  Number of elements.
        """
        # Define number of elements.
        self._n_:   int =   n
        
        # Validate parameters.
        self.__post_init__()
        
    def __post_init__(self) -> None:
        """# Validate parameters.
        
        ## Raises:
            * AssertionError:   If n is not a positive integer.
        """
        assert self.n > 0, f"Discrete space must have positive number of elements, got n = {self.n}"
    
    # PROPERTIES ===================================================================================
    
    @property
    def n(self) -> int:
        """# (Discrete Space) N

        Number of elements in space.
        """
        return self._n_
        
    # METHODS ======================================================================================
    
    def contains(self,
        x:  int
    ) -> bool:
        """# (Discrete Space) Contains?
        
        ## Args:
            * x (int):  Value being verified.

        ## Returns:
            * bool: True if x ∈ S.
        """
        return isinstance(x, int) and 0 <= x < self.n
    
    def sample(self) -> int:
        """# Sample (Discrete Space).

        ## Returns:
            * int:  Random element from space.
        """
        return randint(0, self.n - 1)
    
    # DUNDERS ======================================================================================
    
    def __repr__(self) -> str:
        """# Object Representation.

        Object representation of discrete space.
        """
        return f"<Discrete(n = {self.n})>"