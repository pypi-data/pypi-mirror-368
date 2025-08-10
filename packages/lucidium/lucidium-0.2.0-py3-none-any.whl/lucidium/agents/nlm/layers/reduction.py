"""# lucidium.agents.nlm.layers.reduction

Defines the dimension reduction layer for neural logic machines.
"""

__all__ = ["DimensionReducer"]

from torch                          import max, min, Size, stack, Tensor
from torch.nn                       import Module

from lucidium.agents.nlm.__util__   import exclude_mask, mask_value

class DimensionReducer(Module):
    """# Dimension Reducer

    Reduces a variable via quantifiers (exists/forall), implemented by max/min pooling.
    
    Adapted from : https://github.com/google/neural-logic-machines/blob/master/difflogic/nn/neural_logic/modules/dimension.py
    """
    
    def __init__(self,
        dimension:      int,
        exclude_self:   bool =  True,
        exists:         bool =  True
    ):
        """# Initialize Dimension Reducer.

        ## Args:
            * dimension     (int):  Dimension along which reduction will occur.
            * exclude_self  (bool): Exclude the self variable in the reduction.
            * exists        (bool): Use "exists" (True) or "forall" (False) quantifier.
        """
        # Initialize module.
        super(DimensionReducer, self).__init__()
        
        # Define dimension.
        self._dimension_:       int =   dimension
        
        # Define flags.
        self._exclude_self_:    bool =  exclude_self
        self._exists_:          bool =  exists
        
    # PROPERTIES ===================================================================================
    
    @property
    def dimension(self) -> int:
        """# Dimension (int)
        
        Dimension along which reduction will occur.
        """
        return self._dimension_
    
    @property
    def exclude_self(self) -> bool:
        """# Exclude Self (bool)
        
        Whether to exclude the self variable in the reduction.
        """
        return self._exclude_self_
    
    @property
    def exists(self) -> bool:
        """# Exists (bool)
        
        Whether to use "exists" (True) or "forall" (False) quantifier.
        """
        return self._exists_
    
    # METHODS ======================================================================================
        
    def forward(self,
        inputs: Tensor,
        n:      int | None =    None
    ) -> Tensor:
        """# Reduce Input.
        
        Reduce input tensor by performing pooling operations based on the quantifier type.

        ## Args:
            * inputs    (Tensor):   Input tensor being reduced.

        ## Returns:
            * Tensor:   Reduced tensor.
        """
        # Reference size of input tensor.
        shape:      Size =          inputs.size()
        
        # Create two copies of input for pooling.
        input1:     Tensor =        inputs
        input2:     Tensor =        inputs
        
        # If excluding self...
        if self.exclude_self:
            
            # Calculate mask.
            mask:   Tensor =    exclude_mask(
                                    inputs =    inputs,
                                    count =     self.dimension,
                                    dimension = -1 - self.dimension
                                )
            
            # Mask input with zeros for excluded values.
            input1: Tensor =    mask_value(inputs = inputs, mask = mask, value = 0.0)
            
            # Mask input with ones for remaining values.
            input2: Tensor =    mask_value(inputs = inputs, mask = mask, value = 1.0)
            
        # If using "exists" quantifier...
        if self.exists:
            
            # Adjust shape to accommodate both exists and forall values.
            shape:  Size =      shape[:-2] + (shape[-1] * 2,)
            
            # Apply max pooling along the specified dimension.
            exists: Tensor =    max(input = input1, dim = -2)[0]
            
            # Apply min pooling along the specified dimension.
            forall: Tensor =    min(input = input2, dim = -2)[0]
            
            # Stack and reshape the results.
            return stack(tensors = (exists, forall), dim = -1).view(shape)
        
    def get_output_dimension(self,
        input_dimension:    int
    ) -> int:
        """# Get Output Dimension.
        
        Get output dimension after reduction.

        ## Args:
            * input_dimension   (int):  Input dimension.

        ## Returns:
            * int:  Output dimension after reduction.
        """
        # If using the "exists" quantifier, output dimension is doubled.
        if self.exists: return input_dimension * 2
        
        # Otherwise, simply reutrn input dimension.
        return input_dimension