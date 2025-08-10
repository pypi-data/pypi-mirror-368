"""# lucidium.agents.nlm.layers.permutation

Defines a dimension permutation layer for neural logic machines.
"""

__all__ = ["DimensionPermuter"]

from itertools  import permutations
from typing     import List, Tuple

from torch      import cat, Tensor
from torch.nn   import Module

class DimensionPermuter(Module):
    """# Dimension Permutation

    Creates r! new predicates by permuting the axes for r-arity predicates.

    This operation generates all permutations of the specified dimension and concatenates them along 
    the last dimension.
    
    Adapted from : https://github.com/google/neural-logic-machines/blob/master/difflogic/nn/neural_logic/modules/dimension.py
    """
    
    def __init__(self,
        dimension:      int
    ):
        """# Initialize Dimension Permutation.

        ## Args:
            * dimension (int):  Dimension along which to permute axes.
        """
        # Initialize module.
        super(DimensionPermuter, self).__init__()
        
        # Define dimension.
        self._dimension_:   int =   dimension
        
    # PROPERTIES ===================================================================================
    
    @property
    def dimension(self) -> int:
        """# Dimension (int)
        
        Dimension along which to permute axes.
        """
        return self._dimension_
    
    # METHODS ======================================================================================
        
    def forward(self,
        inputs: Tensor
    ) -> Tensor:
        """# Permute Input.
        
        Apply permutations to the input tensor along the specified dimension.

        ## Args:
            * inputs    (Tensor):   The input tensor to be permuted.

        ## Returns:
            * Tensor:   The tensor with permutations applied.
        """
        # If input dimension is one or less, permutation is not needed.
        if self.dimension <= 1: return inputs

        # Record number of dimensions in input tensor.
        dimensions:         int =           len(inputs.size())
        
        # Create index for all dimensions except for last.
        index:              Tuple[int] =    tuple(range(dimensions - 1))
        
        # Determine starting dimension for permutation.
        start_dimension:    int =           dimensions - 1 - self.dimension
        
        # Ensure starting dimension is valid.
        assert start_dimension > 0, "First dimension must be greater than zero"
        
        # Initialize list of permuted results.
        results:            List[Tensor] =  []

        # For all permutations possible in specified dimension...
        for i in permutations(index[start_dimension:]):
            
            # Make permutatiuon.
            permutation:    Tuple[int] =    index[:start_dimension] + i + (dimensions - 1,)
            
            # Apply permutation and append to results.
            results.append(inputs.permute(dims = permutation))

        # Provide concatenation of all permuted tensors along last dimension.
        return cat(tensors = results, dim = -1)
        
    def get_output_dimension(self,
        input_dimension:    int
    ) -> int:
        """# Get Output Dimension.
        
        Calculate the output dimension after permutation.

        ## Args:
            * input_dimension   (int):  The input dimension.

        ## Returns:
            * int:  The output dimension after permutation.
        """
        # Initialize multiplier.
        multiplier: int =   1
        
        # For each degree of dimension...
        for i in range(self.dimension):
            
            # Multiply by factorial of dimension.
            multiplier *=   i + 1
            
        # Provide input dimension multiplied by factorial.
        return input_dimension * multiplier