"""# lucidium.agents.nlm.layers.mlp

Defines a multi-layer perceptron (MLP) layer with activation for neural logic machines.
"""

__all__ = ["MLPLayer"]

from typing                             import List, Union

from torch                              import Tensor
from torch.nn                           import Linear, Module, Sequential

from lucidium.agents.nlm.layers.linear  import LinearLayer

class MLPLayer(Module):
    """# MLP Layer
    
    A multi-layer perceptron (MLP) layer with activation for hidden layers.

    Adapted from jatorch.nn.cnn.layers: https://github.com/vacancy/Jacinle/blob/master/jactorch/nn/cnn/layers.py
    """
    
    def __init__(self,
        input_dimension:    int,
        output_dimension:   int,
        hidden_dimensions:  Union[List[int], int]
    ):
        """# Initialize MLP Layer.

        ## Args:
            * input_dimension   (int):              Number of input features.
            * output_dimension  (int):              Number of output features.
            * hidden_dimensions (List[int] | int):  List of hidden layer sizes.
        """
        # Initialize module.
        super(MLPLayer, self).__init__()
        
        # Define dimensions.
        self._input_dimension_:     int =           input_dimension
        self._output_dimension_:    int =           output_dimension
        self._hidden_dimensions_:   List[int] =     hidden_dimensions if isinstance(hidden_dimensions, list) else [hidden_dimensions]
        
        # Define attributes.
        self._flatten_:             bool =          True
        self._last_activation_:     bool =          False
        
        # Define dimensions list.
        dimensions:                 List[int] =     [self._input_dimension_] + self._hidden_dimensions_ + [self._output_dimension_]
        
        # Initialize modules list.
        modules:                    List[Module] =  []
        
        # or each hidden dimension...
        for i in range(len(self._hidden_dimensions_)):
            
            # Create hidden layer.
            modules.append(LinearLayer(
                in_features =   dimensions[i],
                out_features =  dimensions[i + 1]
            ))
            
        # Append final layer.
        modules.append(Linear(
            in_features =   dimensions[-2],
            out_features =  dimensions[-1],
            bias =          True
        ))
        
        # Apply layers sequentially.
        self._mlp_:                 Sequential =    Sequential(*modules)
        
    # PROPERTIES ===================================================================================
    
    @property
    def flatten(self) -> bool:
        """# Flatten (bool)
        
        Whether to flatten the input before passing it through the MLP.
        """
        return self._flatten_
    
    @property
    def hidden_dimensions(self) -> List[int]:
        """# Hidden Dimensions (List[int])
        
        List of hidden layer sizes.
        """
        return self._hidden_dimensions_
    
    @property
    def input_dimension(self) -> int:
        """# Input Dimension (int)
        
        Dimension of input features.
        """
        return self._input_dimension_
    
    @property
    def last_activation(self) -> bool:
        """# Last Activation (bool)
        
        Whether to apply an activation function after the last layer.
        """
        return self._last_activation_
    
    @property
    def mlp(self) -> Sequential:
        """# MLP (Sequential)
        
        The sequential module containing the MLP layers.
        """
        return self._mlp_
    
    @property
    def output_dimension(self) -> int:
        """# Output Dimension (int)
        
        Dimension of output features.
        """
        return self._output_dimension_
    
    # METHODS ======================================================================================

    def forward(self,
        input:  Tensor
    ) -> Tensor:
        """# Forward Pass.
        
        Forward pass through the MLP.

        ## Args:
            * input (Tensor):   The input tensor.

        ## Returns:
            * Tensor:   The output tensor after passing through the MLP layers.
        """
        # Flatten if desired.
        if self.flatten: input: Tensor = input.view(input.size(0), -1)
        
        # Make forward pass through layer.
        return self.mlp(input)
    
    def reset_parameters(self) -> None:
        """# Reset Parameters.
        
        Reset parameters of linear layer.
        """
        # For each module in layer...
        for module in self.modules():
            
            # If it is a linear layer, reset the parameters.
            if isinstance(module, Linear): module.reset_parameters()