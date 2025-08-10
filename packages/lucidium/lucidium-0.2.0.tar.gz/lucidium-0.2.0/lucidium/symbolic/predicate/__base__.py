"""# lucidium.symbolic.predicate.base

Symbolic predicate definition, structure, and utilities.
"""

__all__ = ["Predicate"]

from dataclasses    import dataclass
from typing         import Any, Dict, Tuple

from torch          import tensor, Tensor

@dataclass(frozen = True)
class Predicate():
    """# Predicate
    
    Symbolic representation of a grounded predicate.
    """
    # Define properties.
    name:   str
    args:   Tuple[Any, ...]
        
    # PROPERTIES ===================================================================================
    
    @property
    def arity(self) -> int:
        """# (Predicate) Arity

        Number of arguments attrbuted to predicate.
        """
        return len(self.args)
        
    # METHODS ======================================================================================
    
    def to_tensor(self,
        vocabulary: Dict[str, int]
    ) -> Tensor:
        """# (Predicate) to Tensor

        ## Args:
            * vocabulary    (Dict[str, int]):   Mapping of terms to their numeric value.

        ## Returns:
            * Tensor:   Tensor representation of predicate.
        """
        return tensor([vocabulary.get(str(arg), -1) for arg in (self.name, *self.args)])
    
    def to_tuple(self) -> Tuple[Any]:
        """# (Predicate) to Tuple

        Tuple representation of predicate.
        """
        return (self.name, *self.args)
    
    # DUNDERS ======================================================================================
    
    def __eq__(self,
        other: "Predicate"
    ) -> bool:
        """# Predicate Equality.

        ## Args:
            * other (Predicate):    Predicate being compared.

        ## Returns:
            * bool: True if predicates have the same name and arguments.
        """
        return isinstance(other, Predicate) and self.to_tuple() == other.to_tuple()
    
    def __repr__(self) -> str:
        """# Object Representation."""
        return f"""<Predicate(name = {self.name}, arity = {self.arity})>"""
    
    def __str__(self) -> str:
        """# String Representation."""
        return f"""{self.name}({",".join(map(str, self.args))})"""