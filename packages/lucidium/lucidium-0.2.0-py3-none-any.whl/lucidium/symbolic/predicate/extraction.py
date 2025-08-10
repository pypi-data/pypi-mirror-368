"""# lucidium.symbolic.predicate.extraction

Defines holistic predicate extractor.
"""

__all__ = ["extract_predicates"]

from typing import Any, Callable, List, Tuple

def extract_predicates(
    obj:    Any
) -> List[Tuple[str, Callable, int]]:
    """# Extract Predicates.
    
    Extract all callables from object that are designated as predicates.

    ## Args:
        * obj   (Any):  Object whose predicate callables are being extracted.

    ## Returns:
        * List[Tuple[str, Callable, int]]:  All designated predicates under object.
    """
    # Initialize list of predicates.
    predicates: List[Tuple[str, Callable, int]] =   []
    
    # For each attribute name of object...
    for attribute_name in dir(obj):
        
        # Extract the attribute itself.
        attribute:  Any =   getattr(obj, attribute_name)
        
        # If this attribute is a callable and is designated as a predicate...
        if callable(attribute) and getattr(attribute, "_is_predicate_", False):
            
            # Add it to the list of extracted predicates.
            predicates.append((attribute._predicate_name_, attribute, attribute._predicate_arity_))
            
    # Provide extracted predicates.
    return predicates