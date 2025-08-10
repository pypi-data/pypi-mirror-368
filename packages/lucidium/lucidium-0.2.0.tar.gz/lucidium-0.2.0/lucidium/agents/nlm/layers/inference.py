"""# lucidium.agents.nlm.layers.inference

Defines the inference layers for neural logic machines.
"""

__all__ = ["InferenceLayer"]

from torch                          import Tensor
from torch.nn                       import Module, Sequential, Sigmoid

from lucidium.agents.nlm.layers.mlp import MLPLayer

class InferenceLayer(Module):
    """# Inference Layer

    MLP-based implementation for logic and logits inference.
    
    Adapted from: https://github.com/google/neural-logic-machines/blob/master/difflogic/nn/neural_logic/modules/neural_logic.py
    """
    
    def __init__(self,
        input_dimension:    int,
        output_dimension:   int,
        hidden_dimension:   int,
        activation:         bool =  False
    ):
        """# Initialize Inference Layer.

        ## Args:
            * input_dimensions  (list[int]):    The number of input channels for each input group.
            * output_dimensions (list[int]):    The number of output channels for each group.
            * hidden_dimension  (int):          The hidden dimension of the logic model.
            * activation        (bool):         Whether to add an activation layer after the MLP. Defaults to False.
        """
        # Initialize module.
        super(InferenceLayer, self).__init__()
        
        # Define dimensions.
        self._input_dimension_:     int =   input_dimension
        self._output_dimension_:    int =   output_dimension
        self._hidden_dimension_:    int =   hidden_dimension
        
        # Define layers.
        self._layer_:               Sequential =    Sequential(
                                                        MLPLayer(
                                                            input_dimension =   self._input_dimension_,
                                                            output_dimension =  self._output_dimension_,
                                                            hidden_dimensions = self._hidden_dimension_
                                                        )
                                                    )
        
        # Add activation layer if required.
        if activation: self._layer_.add_module(name = str(len(self._layer_)), module = Sigmoid())
        
    # PROPERTIES ===================================================================================
    
    @property
    def hidden_dimension(self) -> int:
        """# Hidden Dimension (int)
        
        The hidden dimension of the inference layer.
        """
        return self._hidden_dimension_
    
    @property
    def input_dimension(self) -> int:
        """# Input Dimension (int)
        
        The input dimension of the inference layer.
        """
        return self._input_dimension_
    
    @property
    def layer(self) -> Sequential:
        """# Layer (Sequential)
        
        The inference layer, which is a sequential module containing the MLP and optional 
        activation.
        """
        return self._layer_
    
    @property
    def output_dimension(self) -> int:
        """# Output Dimension (int)
        
        The output dimension of the inference layer.
        """
        return self._output_dimension_
    
    # METHODS ======================================================================================
        
    def forward(self,
        inputs: Tensor
    ) -> Tensor:
        """# Forward Pass.
        
        Make forward pass through inference layer.

        ## Args:
            * inputs    (Tensor):   Tensor input.

        ## Returns:
            * Tensor:   Output tensor.
        """
        # Reference input size and channels.
        size:       int =   inputs.size()[:-1]
        channel:    int =   inputs.size(-1)
        
        # Flatten input.
        inputs:     Tensor =    inputs.view(-1, channel)
        
        # Pass through layer.
        inputs:     Tensor =    self.layer(inputs)
        
        # Return flattened output.
        return inputs.view(*size, -1)