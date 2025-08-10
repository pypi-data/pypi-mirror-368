"""# lucidium.spaces.box

Defines a multi-dimensional array space representation.
"""

__all__ = ["Box"]

from typing                     import Tuple, Union

from numpy                      import all, array, ndarray
from numpy.random               import uniform

from lucidium.spaces.__base__   import Space

class Box(Space):
    """# Box (Space)

    Multi-dimensional array space.
    """
    
    def __init__(self,
        lower:  Union[int, float],
        upper:  Union[int, float],
        shape:  Tuple[Union[int, float], ...],
        dtype:  Union[type, str] =              float
    ):
        """# Instantiate Box (Space).

        ## Args:
            * lower (Union[int, float]):                Lower bound.
            * upper (Union[int, float]):                Upper bound.
            * shape (Tuple[Union[int, float], ...]):    Shape of space.
            * dtype (Union[type, str], optional):       Data type (e.g., int, float). Defaults to 
                                                        float.
        """
        # Define bounds.
        self._lower_:   Union[int, float] =             lower
        self._upper_:   Union[int, float] =             upper
        
        # Define shape.
        self._shape_:   Tuple[Union[int, float], ...] = shape
        
        # Define data type.
        self._dtype_:   Union[type, str] =              dtype
    
    # PROPERTIES ===================================================================================
    
    @property
    def dtype(self) -> Union[type, str]:
        """# (Box Space) Data Type

        The data type of all elements within space.
        """
        return self._dtype_
    
    @property
    def lower_bound(self) -> Union[int, float]:
        """# (Box Space) Lower Bound

        Lower bound of all dimensions of space.
        """
        return self._lower_
    
    @property
    def shape(self) -> Tuple[Union[int, float], ...]:
        """# (Box Space) Shape.

        Shape of space.
        """
        return self._shape_
    
    @property
    def upper_bound(self) -> Union[int, float]:
        """(# Box Space) Upper Bound

        Upper bound of all dimensions of space.
        """
        return self._upper_
        
    # METHODS ======================================================================================
    
    def contains(self,
        x:  ndarray
    ) -> bool:
        """# (Box Space) Contains?

        ## Args:
            * x (ndarray):  Element being verified.

        ## Returns:
            * bool: True if x ∈ S.
        """
        # Convert x to an ndarray if it is another type.
        if not isinstance(x, ndarray): x: ndarray = array(x)
        
        # Evaluate existence.
        return  (
                    x.shape == self._shape_ and
                    all(x >= self._lower_)  and
                    all(x <= self._upper_)
                )
        
    def sample(self) -> ndarray:
        """# Sample (Box Space).

        ## Returns:
            * ndarray:  Random sample from box space.
        """
        return  uniform(
                    low =   self._lower_,
                    high =  self._upper_,
                    size =  self._shape_
                ).astype(self._dtype_)
    
    # DUNDERS ======================================================================================
    
    def __repr__(self) -> str:
        """# Object Representation.

        Object representation of box space.
        """
        return f"<Box(lower = {self._lower_}, upper = {self._upper_}, shape = {self._shape_})>"