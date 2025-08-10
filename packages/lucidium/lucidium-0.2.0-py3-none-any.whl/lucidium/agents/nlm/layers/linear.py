"""# lucidium.agents.nlm.layers.linear

Defines a linear layer with activation for neural logic machines.
"""

__all__ = ["LinearLayer"]

from torch.nn   import Linear, ReLU, Sequential

class LinearLayer(Sequential):
    """# Linear Layer
    
    A fully connected layer with activation.

    Adapted from jatorch.nn.cnn.layers: https://github.com/vacancy/Jacinle/blob/master/jactorch/nn/cnn/layers.py
    """
    
    def __init__(self,
        in_features:    int,
        out_features:   int
    ):
        """# Initialize Linear Layer.
        
        ## Args:
            * in_features   (int):  The number of input features.
            * out_features  (int):  The number of output features.
        """
        # Initialize sequential module.
        super(LinearLayer, self).__init__([
            Linear(
                    in_features =   in_features,
                    out_features =  out_features,
                    bias =          True
            ),
            ReLU(
                    inplace =       True
            )
        ])
        
        # Define features.
        self._in_features_:     int =   in_features
        self._out_features_:    int =   out_features
        
    # PROPERTIES ===================================================================================
        
    @property
    def input_dimension(self) -> int:
        """# Input Dimension (int)
        
        Dimension of input features.
        """
        return self._in_features_
    
    @property
    def output_dimension(self) -> int:
        """# Output DImension (int)
        
        Dimension of output features.
        """
        return self._out_features_
    
    # METHODS ======================================================================================
    
    def reset_parameters(self) -> None:
        """# Reset Parameters.
        
        Reset parameters of linear layer.
        """
        # For each module in layer...
        for module in self.modules():
            
            # If it is a linear layer, reset the parameters.
            if isinstance(module, Linear): module.reset_parameters()