"""# lucidium.agents.nlm.util

Defines utility functions for the Neural Logic Machine (NLM) package.
"""

__all__ =   [
                "broadcast",
                "concatenate_shape",
                "exclude_mask",
                "mask_value",
            ]

from collections.abc    import Sequence
from typing             import List, Tuple, Union

from torch              import arange, long, Size, Tensor
        
def broadcast(
    tensor:     Tensor,
    dimension:  int,
    size:       int
) -> Tensor:
    """# Broadcast Tensor.
    
    Broadcast a specific dimension for `size` times. Originally the dimension size must be 1.
    
    Adapted from jatorch.functional.shape: https://github.com/vacancy/Jacinle/blob/master/jactorch/functional/shape.py

    ## Args:
        * tensor    (Tensor):   Tensor being broadcasted.
        * dimension (int):      Dimension of tensor being broadcasted.
        * size      (int):      Size of target dimension.

    ## Returns:
        * Tensor:   Broadcasted tensor.
    """
    # If dimension is less than zero, increment.
    if dimension < 0: dimension += tensor.dim()
    
    # Assert that the tensor's dimension size is one.
    assert tensor.size(dim = dimension) == 1
    
    # Broadcast tensor.
    return  tensor.expand(
                size =  concatenate_shape(
                            tensor.size()[:dimension],
                            size,
                            tensor.size()[dimension + 1:]
                        )
            )
    

def concatenate_shape(
    *shapes:    Union[Size, Tuple[int, ...], List[int], int]
) -> Tuple[int, ...]:
    """# Concatenate Shapes into Tuple.
    
    Concatenate shapes into a tuple. The values can be either torch.Size, tuple, list, or integer.
    
    Adapted from jatorch.functional.shape: https://github.com/vacancy/Jacinle/blob/master/jactorch/functional/shape.py
    
    ## Returns:
        * Tuple[int, ...]:  Tuple of shapes.
    """
    # Initialize output list.
    output: List =  []
    
    # For shape provided...
    for s in shapes:
        
        # If shape is a sequence, add elements to output list.
        if isinstance(s, Sequence): output.extend(s)
        
        # Otherwise simply append single element.
        output.append(int(s))
        
    # Provide tuple of shapes.
    return tuple(output)


def exclude_mask(
    inputs:     Tensor,
    count:      int =   2,
    dimension:  int =   1
) -> Tensor:
    """# Produce Exclusive Mask.
    
    Produce an exclusive mask for a tensor, ensuring mutually exclusive coordinates.

    Specifically, for `cnt=2`, given an array `a[i, j]` of size `n * n`, this function produces a 
    mask where only `a[i, j] == 1` if and only if `i != j`.
    
    Adapted from: https://github.com/google/neural-logic-machines/blob/master/difflogic/nn/neural_logic/modules/_utils.py

    ## Args:
        * inputs    (Tensor):           The tensor to be masked.
        * count     (int, optional):    The number of dimensions over which the operation is 
                                        performed. Default is 2.
        * dimension (int, optional):    The starting dimension for the exclusive mask. Default is 1.

    ## Returns:
        * Tensor:   A mask tensor where each coordinate pair is mutually exclusive.
    """
    # Assert that the count is greater than zero.
    assert count > 0, f"Count({count}) expected to be greater than zero."
    
    # Adjust dimension if negative.
    if dimension < 0: dimension += inputs.dim()
    
    # Reference size of input.
    n:      Size =      inputs.size(dim = dimension)
    
    # Assert that size of all input dimensions are equal.
    for i in range(1, count): assert n == inputs.size(dim = dimension + i), \
        f"Size of dimensions in count must be equal."
        
    # Initialize range of values along dimension.
    values: Tensor =    arange(start = 0, end = n, dtype = long, device = inputs.device)
    
    # Initialize list to track index ranges.
    q:      List =      []
    
    # For each count...
    for i in range(count):
        
        # Start with range of values 0 to n-1.
        p:  Tensor =    values
        
        # For other axes...
        for j in range(count):
            
            # Make sure we're not looking at the same axis.
            if i != j:
                
                # Unsqueeze the indices along the specified dimension.
                p:  Tensor =    p.unsqueeze(j)
                
        # Expand the indices to cover the entire grid.
        p:  Tensor =    p.expand(size = (n,) * count)
        
        # Append to expanded indices list.
        q.append(p)
        
    # Initialize mask where first condition holds.
    mask:   Tensor =    q[0] == q[0]
    
    # Apply mutually exclusive condition.
    for i in range(count):
        for j in range(count):
            if i != j: mask *= q[i] != q[j]
    
    # Unsqueeze mask along leading dimensions.
    for i in range(dimension):                          mask.unsqueeze_(dim = 0)
    for j in range(inputs.dim() - dimension - count):   mask.unsqueeze_(dim = -1)
    
    # Expand mask to match the input size.
    return mask.expand(size = inputs.size()).float()
    
def mask_value(
    inputs: Tensor,
    mask:   Tensor,
    value:  float
) -> Tensor:
    """# Apply Mask to Tensor.
    
    Apply a mask to a tensor, setting the masked elements to a specified value.

    This function will multiply the `inputs` tensor with the `mask`, and set all elements where the 
    `mask` is zero to the given `value`.
    
    Adapted from: https://github.com/google/neural-logic-machines/blob/master/difflogic/nn/neural_logic/modules/_utils.py

    ## Args:
        * inputs    (Tensor):   The input tensor to be modified.
        * mask      (Tensor):   A binary mask tensor, where `1` means the value should remain, and 
                                `0` means it should be replaced.
        * value     (float):    The value to replace the elements where the mask is `0`.

    ## Returns:
        * Tensor:   The modified tensor after applying the mask.
    """
    # Assert that the sizes of the input and mask are the same.
    assert inputs.size() == mask.size(), f"Size of inputs {inputs.size()} and mask {mask.size()} expected to be the same"
    
    # Apply mask to inputs.
    return inputs * mask + value * (1 - mask)