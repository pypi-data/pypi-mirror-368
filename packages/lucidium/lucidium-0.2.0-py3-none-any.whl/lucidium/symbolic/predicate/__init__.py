"""# lucidium.symbolic.predicate

This package defines predicate structure and functionality.
"""

__all__ =   [
                "Predicate",
                "predicate",
                "extract_predicates"
            ]

from lucidium.symbolic.predicate.__base__   import Predicate
from lucidium.symbolic.predicate.decorator  import predicate
from lucidium.symbolic.predicate.extraction import extract_predicates