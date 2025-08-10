"""# lucidium.symbolic.predicate.decorator

Decorator for predicate definitions/signatures.
"""

__all__ = ["predicate"]

from typing import Callable, List, Optional, Union

def predicate(
    name:       Optional[str] =         None,
    arguments:  Optional[List[str]] =   []
) -> Callable:
    """# Predicate (Decorator)

    ## Args:
        * name          (str]):         Custom predicate name. Defaults to None.
        * arguments     (List[str]):    List of object attributes to include as predicate arguments. Defaults to None.
        * condition     (Callable):     Function that takes the result and returns boolean for whether to extract. Defaults to None.
        * extract_when  (str):
            * "always":     Always extract (default)
            * "true":       Only when result is truthy
            * "false":      Only when result is falsy
            * "not_none":   Only when result is not None
            * "exists":     Extract just for the existence of the property/method

    ## Returns:
        * Callable: Predicate decorator.
    """
    # Define predicate decorator.
    def decorator(
        function:   Union[Callable, property]
    ) -> Union[Callable, property]:
        # Define properties of predicate.
        function._is_predicate_ =       True
        function._predicate_name_ =     name
        function._predicate_arity_ =    len(arguments)
        function._predicate_args_ =     arguments
        
        # Return predicate callable.
        return function
        
    # Provide decorator.
    return decorator