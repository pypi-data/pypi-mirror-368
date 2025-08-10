"""# lucidium.agents.nlm.layers.logic

Defines a logic layer that performs differentiable logic deduction.
"""

__all__ = ["LogicLayer"]

from logging                                import Logger
from typing                                 import Any, List, Union

from torch                                  import cat, Tensor
from torch.nn                               import Module, ModuleList

from lucidium.agents.nlm.layers.expansion   import DimensionExpander
from lucidium.agents.nlm.layers.inference   import InferenceLayer
from lucidium.agents.nlm.layers.permutation import DimensionPermuter
from lucidium.agents.nlm.layers.reduction   import DimensionReducer
from lucidium.utilities                     import get_child

class LogicLayer(Module):
    """# Logic Layer
    
    A logic layer that performs differentiable logic deduction.
    
    Each logic layer computes inference over input predicates by applying logic rules. The logic is 
    performed in two stages: 
    * Expansion/Reduction:      For inter-group deduction
    * Logic model application:  For intra-group deduction
    
    Adapted from: https://github.com/google/neural-logic-machines/blob/master/difflogic/nn/neural_logic/layer.py
    """
    
    def __init__(self,
        breadth:            int,
        input_dimensions:   List[int],
        output_dimensions:  List[int],
        hidden_dimension:   int,
        exclude_self:       bool =      True,
        residual:           bool =      False
    ):
        """# Initialize Logic Layer.

        ## Args:
            * breadth           (int):          The breadth (max order) of the logic layer.
            * input_dimensions  (List[int]):    The number of input channels for each input group.
            * output_dimensions (List[int]):    The number of output channels for each group.
            * hidden_dimension  (int):          The hidden dimension of the logic model.
            * exclude_self      (bool):         Whether to exclude multiple occurrences of the same 
                                                variable in logic deduction.
            * residual          (bool):         Whether to use residual connections for the outputs.
        """
        # Initialize module.
        super(LogicLayer, self).__init__()
        
        # Initialize logger.
        self.__logger__:                Logger =            get_child("logic-layer")
        
        # Assert that breadth is positive.
        assert 0 < breadth, f"Breadth expected to be positive, got {breadth}"
        
        # Warn of performance complications for breadth greater than 3.
        if breadth > 3: self.__logger__.warning(f"Using a breadth greater than 3 may cause performance complications (speed & memory).")
        
        # Define maximum order (degree) of logic.
        self._max_order_:               int =               breadth
        
        # Set residual flag.
        self._residual_:                bool =              residual
        
        # Ensure input and output dimensions are lists of the correct length, being no greater than 
        # max order.
        input_dimensions:               List[int] =             self._make_list_(
                                                                    x =     input_dimensions, 
                                                                    n =     self._max_order_ + 1,
                                                                    dtype = int
                                                                )
        output_dimensions:              List[int] =             self._make_list_(
                                                                    x =     output_dimensions,
                                                                    n =     self._max_order_ + 1,
                                                                    dtype = int
                                                                )
        
        # Initialize module lists.
        self._logic_:                   ModuleList =            ModuleList()
        self._dimension_permuters_:     ModuleList =            ModuleList()
        self._dimension_expanders_:     ModuleList =            ModuleList()
        self._dimension_reducers_:      ModuleList =            ModuleList()
        
        # For each order of logic prescribed...
        for order in range(self._max_order_ + 1):
            
            # Start with input dimension.
            current_dimension:          int =                   input_dimensions[order]
            
            # For all but the first order...
            if order > 0:
                
                # Initialize expander.
                expander:               DimensionExpander =     DimensionExpander(
                                                                    dimension = order - 1
                                                                )
                
                # Append to expanders list.
                self._dimension_expanders_.append(expander)
                
                # Add expanded dimension.
                current_dimension +=                            expander.get_output_dimension(
                                                                    input_dimension = input_dimensions[order - 1]
                                                                )
            
            # Otherwise, no expansion is needed for first degree.
            else: self._dimension_expanders_.append(None)
            
            # For the next degree...
            if order + 1 < self._max_order_ + 1:
                
                # Define a dimension reducer.
                reducer:                DimensionReducer =      DimensionReducer(
                                                                    dimension =     order + 1,
                                                                    exclude_self =  exclude_self
                                                                )
                
                # Append to reducers list.
                self._dimension_reducers_.append(reducer)
                
                # Add reduced dimension.
                current_dimension +=                            reducer.get_output_dimension(
                                                                    input_dimension = input_dimensions[order + 1]
                                                                )
            
            # Otherwise, no reduction is needed for first degree.
            else: self._dimension_reducers_.append(None)
            
            # For the first order...
            if current_dimension == 0:
                
                # Do no create logic or permutation.
                self._dimension_permuters_.append(None)
                self._logic_.append(None)
                
                # Set output dimension to zero when no logic is applied.
                output_dimensions[order] =                      0
                
            # Otherwise...
            else:
                
                # Create permutation layer for this group.
                permutation:            DimensionPermuter = DimensionPermuter(
                                                                dimension = order
                                                            )
                
                # Append to permutation list.
                self._dimension_permuters_.append(permutation)
                
                # Apply permutation to current dimensions.
                current_dimension:      int =               permutation.get_output_dimension(
                                                                input_dimension =   current_dimension
                                                            )
                
                # Append logic layer.
                self._logic_.append(InferenceLayer(
                    input_dimension =   current_dimension,
                    output_dimension =  output_dimensions[order],
                    hidden_dimension =  hidden_dimension,
                    activation =        True
                ))
                
        # Define dimensions lists.
        self._input_dimensions_:        List[int] =             input_dimensions
        self._output_dimensions_:       List[int] =             output_dimensions
        
        # If residual connections is specified...
        if self._residual_:
            
            # For each input dimension, add input dimensions to output dimensions for residual.
            for i in range(len(self._input_dimensions_)): self._output_dimensions_[i] += self._input_dimensions_[i]
            
    # PROPERTIES ===================================================================================
    
    @property
    def breadth(self) -> int:
        """# Breadth (int)
        
        The maximum order of the logic layer.
        """
        return self._max_order_
    
    @property
    def exclude_self(self) -> bool:
        """# Exclude Self (bool)
        
        Whether to exclude multiple occurrences of the same variable in logic deduction.
        """
        return self._residual_
    
    @property
    def expanders(self) -> ModuleList:
        """# Dimension Expanders (ModuleList)
        
        List of dimension expanders for each group of the logic layer.
        """
        return self._dimension_expanders_
    
    @property
    def input_dimensions(self) -> List[int]:
        """# Input Dimensions (List[int])
        
        Number of input channels for each group of the logic layer.
        """
        return self._input_dimensions_
    
    @property
    def logic(self) -> ModuleList:
        """# Logic Inference Layers (ModuleList)
        
        List of logic inference layers for each group of the logic layer.
        """
        return self._logic_
    
    @property
    def max_order(self) -> int:
        """# Max Order (int)
        
        The maximum order of the logic layer.
        """
        return self._max_order_
    
    @property
    def output_dimensions(self) -> List[int]:
        """# Output Dimensions (List[int])
        
        Number of output channels for each group of the logic layer.
        """
        return self._output_dimensions_
    
    @property
    def permuters(self) -> ModuleList:
        """# Dimension Permutations (ModuleList)
        
        List of dimension permutations for each group of the logic layer.
        """
        return self._dimension_permuters_
    
    @property
    def reducers(self) -> ModuleList:
        """# Dimension Reducers (ModuleList)
        
        List of dimension reducers for each group of the logic layer.
        """
        return self._dimension_reducers_
    
    @property
    def residual(self) -> bool:
        """# Residual (bool)
        
        Whether to use residual connections for the outputs.
        """
        return self._residual_
            
    # METHODS ======================================================================================
            
    def forward(self,
        inputs: List[Tensor]
    ) -> List[Tensor]:
        """# Forward Pass.
        
        Forward pass through logic layer.

        ## Args:
            * inputs    (list[Tensor]): List on inputs for each group of the logic layer.

        ## Returns:
            * list[Tensor]: Output from each logic layer group.
        """
        # Assert that the number of inputs matches expected order.
        assert len(inputs) == self.max_order + 1, f"Number of input tensors ({len(inputs)} should be {self.max_order})"
        
        # Initialize list to store outputs.
        outputs:        List[Tensor] =  []
        
        # For each group of logic layer...
        for group in range(self.max_order + 1):
            
            # Initialize temporary list to store input of adjacent groups.
            temp:       List[Tensor] =  []
            
            # If not the first group...
            if group > 0 and self.input_dimensions[group - 1] > 0:
                
                # Reference expansion size.
                n:      int =           inputs[group].size(1) if group == 1 else None
                
                # Append expanded tensor to temporary list.
                temp.append(self.expanders[group](inputs[group -1], n))
                
            # If not the last group, and to temporary list.
            if group < len(inputs) and self.input_dimensions[group] > 0: temp.append(inputs[group])
            
            # Reduce inputs from next group.
            if group + 1 < len(inputs) and self.input_dimensions[group + 1] > 0: temp.append(self.reducers[group](inputs[group + 1]))
            
            # If no inputs were collected, output should be None.
            if len(temp) == 0: output: Tensor = None
            
            # Otherwise...
            else:
                
                # Concatenate all inputs along the last dimension.
                temp =                  cat(tensors = temp, dim = -1)
                
                # Apply permutation to the concatenated inputs.
                temp =                  self.permuters[group](temp)
                
                # Apply logic inference layer.
                output: Tensor =        self.logic[group](temp)
                
            # If residual is specified...
            if self.residual and self.input_dimensions[group] > 0:
                
                # Concatenate the input with the output.
                output: Tensor =        cat(tensors = [inputs[group], output], dim = -1)
                
            # Append output to list.
            outputs.append(output)
            
        # Return final output list.
        return outputs
    
    # HELPERS ======================================================================================
        
    def _make_list_(self,
        x:      Union[List, Any],
        n:      int,
        dtype:  type
    ) -> List[any]:
        """# Make List of N Elements.
        
        Ensure that `x` is either a list of `n` elements or single element of type `dtype`.

        ## Args:
            * x     (List | Any):   Element or list.
            * n     (int):          Desired length of list.
            * dtype (type):         Expected type of list elements.

        ## Returns:
            * list[any]:    List of length `n` and type `dtype`.
        """
        # Assert that data type is not list.
        assert dtype is not list,               f"Data type should not be list."
        
        # If `x` is a single element of type `dtype`, create an `n` length list of it.
        if isinstance(x, dtype): x = [x,] * n
        
        # Assert that list is desired length.
        assert len(x) == n,                     f"Parameters should be {dtype} or list of {n} elements."
        
        # For each element in list...
        for e, element in enumerate(x):
            
            # Assert that it is of proper type.
            assert isinstance(element, dtype),  f"Elements expected to be {dtype}, but x[{e}] is {type(element)}"
            
        # Return list.
        return x