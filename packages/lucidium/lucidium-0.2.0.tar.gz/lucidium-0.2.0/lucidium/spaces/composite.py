"""# lucidium.spaces.composite

Defines a composite space combining named subspaces.
"""

__all__ = ["Composite"]

from typing                     import Any, Dict

from lucidium.spaces.__base__   import Space

class Composite(Space):
    """# Composite (Space)

    Dictionary-style combination of named subspaces.
    """
    
    def __init__(self,
        subspaces: Dict[str, Space]
    ):
        """# Instantiate Composite (Space).

        ## Args:
            * subspaces (Dict[str, Space]): Subspace mapping(s).
        """
        # Define subspaces.
        self._subspaces_:   Dict[str, Space] =  subspaces
        
    # PROPERTIES ===================================================================================
    
    @property
    def subspaces(self) -> Dict[str, Space]:
        """# (Composite Space) Spaces.

        ## Returns:
            * Dict[str, Space]: Mapping of subspaces.
        """
        return self._subspaces_
        
    # METHODS ======================================================================================
    
    def contains(self,
        m: Dict[str, Any]
    ) -> bool:
        """# (Composite Space) Contains?

        ## Args:
            * m (Dict[str, Any]):   Mapping of values being verified.

        ## Returns:
            * bool: True if all values of mapping exist within subspaces.
        """
        return  all([
                    isinstance(m, dict),
                    all(
                        [
                            key in self.subspaces,
                            self.subspaces[key.contains[m[key]]]
                        ]
                        for key in self.subspaces.items()
                    ) 
                ])
        
    def sample(self) -> Dict[str, Any]:
        """# Sample (Composite Space).

        ## Returns:
            * Dict[str, Any]:   Random value samples from each subspace.
        """
        return {key: space.sample() for key, space in self.subspaces.items()}
    
    # DUNDERS ======================================================================================
    
    def __repr__(self) -> str:
        """# Object Representation.

        Object representation of composite space.
        """
        return f"""<Composite(subspaces = {", ".join(f"{k}: {v}" for k, v in self.subspaces.items())})>"""