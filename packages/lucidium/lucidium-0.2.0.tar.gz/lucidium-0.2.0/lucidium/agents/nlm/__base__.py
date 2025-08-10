"""# lucidium.agents.nlm.base

Implementation of Neural Logic Machine as presented in the 2019 paper by Honghua Dong et. al.

## References:
Paper:  https://arxiv.org/pdf/1904.11694.pdf
Source: https://github.com/google/neural-logic-machines
"""

from logging                        import Logger
from typing                         import Any, List, override, Optional, Tuple

from torch                          import cat, load, no_grad, save, Tensor
from torch.nn                       import Module, ModuleList

from lucidium.agents.__base__       import Agent
from lucidium.agents.nlm.__args__   import register_nlm_parser
from lucidium.agents.nlm.layers     import LogicLayer
from lucidium.registries            import register_agent
from lucidium.utilities.logger      import get_child

@register_agent(
    name =      "nlm",
    tags =      ["neuro-symbolic", "value-based", "model-free"],
    parser =    register_nlm_parser
)
class NeuralLogicMachine(Module, Agent):
    """# Neural Logic Machine

    Neural Logic Machine (NLM) is a neural-symbolic architecture for both inductive learning and 
    logic reasoning. NLMs use tensors to represent logic predicates. This is done by grounding the 
    predicate as True or False over a fixed set of objects. Based on the tensor representation, 
    rules are implemented as neural operators that can be applied over the premise tensors and 
    generate conclusion tensors.

    ## References:
    * Paper:  https://arxiv.org/pdf/1904.11694.pdf
    * Source: https://github.com/google/neural-logic-machines
    """
    
    def __init__(self,
        depth:              int,
        breadth:            int,
        input_dimensions:   Tuple[int],
        output_dimensions:  Tuple[int],
        hidden_dimension:   int,
        exclude_self:       bool =              True,
        residual:           bool =              False,
        io_residual:        bool =              False,
        recursion:          bool =              False,
        connections:        List[List[bool]] =  None
    ):
        """# Initialize Neural Logic Machine.

        ## Args:
            * depth             (int):              The number of logic layers.
            * breadth           (int):              The breadth of each logic layer.
            * input_dimensions  (Tuple[int]):       Input dimensions for each layer.
            * output_dimensions (Tuple[int]):       Output dimensions for each layer.
            * hidden_dimension  (int):              Hidden dimension of the logic model.
            * exclude_self      (bool):             Exclude multiple occurrences of the same 
                                                    variable.
            * residual          (bool):             Use residual connections.
            * io_residual       (bool):             Use input/output-only residual connections.
            * recursion         (bool):             Enable recursion for weight sharing.
            * connections       (List[List[bool]]): Connections between layers.
        """
        # Initialize module.
        super(NeuralLogicMachine, self).__init__()
        
        # Define attributes.
        self._depth_:               int =               depth
        self._breadth_:             int =               breadth
        self._residual_:            bool =              residual
        self._io_residual_:         bool =              io_residual
        self._recursion_:           bool =              recursion
        self._connections_:         List[List[bool]] =  connections
        
        # Assert that exactly one type of recursion is being requested.
        assert self._residual_ ^ self._io_residual_,    f"Only one type of residual connection type allowed."
        
        # Initialize module list.
        self._layers_:              ModuleList =        ModuleList()
        
        # Start with the input input dimension of the first layer.
        current_dimensions:         List[int] =         input_dimensions
        
        # Calculate total dimensions needed for IO residual option.
        total_output_dimension:     List[int] =         [0 for _ in range(self._breadth_ + 1)]
        
        # For each layer prescribed by depth...
        for layer in range(depth):
            
            # If IO residual option indicated, and not on first layer...
            if layer > 0 and self._io_residual_:
                
                # Update current dimensions.
                current_dimensions: list[int] =         [x + y for x, y in zip(current_dimensions, input_dimensions)]
            
            # Create a logic layer for this depth.
            layer:                  LogicLayer =        LogicLayer(
                                                            breadth =           breadth,
                                                            input_dimensions =  current_dimensions,
                                                            output_dimensions = output_dimensions,
                                                            hidden_dimension =  hidden_dimension,
                                                            exclude_self =      exclude_self,
                                                            residual =          residual
                                                        )
            
            # Update current dimensions to the output of the layer.
            current_dimensions:     Tensor =            layer._output_dimensions_
            
            # Apply masking to dimension.
            current_dimensions:     Tensor =            self._mask_(
                                                            dimensions =        current_dimensions,
                                                            index =             layer,
                                                            masked_value =      0
                                                        )
            
            # Append to layers list.
            self._layers_.append(layer)
            
        # Set output dimensions for IO residual or set to last layer's output dimensions by default.
        self._output_dimensions_:   List[int] =         total_output_dimension if io_residual else current_dimensions
        
    # PROPERTIES ===================================================================================
    
    @property
    def breadth(self) -> int:
        """# Breadth (int)
        
        The breadth of each logic layer in the Neural Logic Machine.
        """
        return self._breadth_
    
    @property
    def connections(self) -> List[List[bool]]:
        """# Connections (List[List[bool]])
        
        The connections between layers in the Neural Logic Machine.
        """
        return self._connections_
    
    @property
    def depth(self) -> int:
        """# Depth (int)
        
        The number of logic layers in the Neural Logic Machine.
        """
        return self._depth_
    
    @property
    def io_residual(self) -> bool:
        """# IO Residual (bool)
        
        Whether input/output-only residual connections are used in the Neural Logic Machine.
        """
        return self._io_residual_
    
    @property
    def layers(self) -> ModuleList:
        """# Layers (ModuleList)
        
        The list of logic layers in the Neural Logic Machine.
        """
        return self._layers_
    
    @property
    def output_dimensions(self) -> List[int]:
        """# Output Dimensions (List[int])
        
        The output dimensions of the Neural Logic Machine.
        """
        return self._output_dimensions_
    
    @property
    def recursion(self) -> bool:
        """# Recursion (bool)
        
        Whether recursion is enabled for weight sharing in the Neural Logic Machine.
        """
        return self._recursion_
    
    @property
    def residual(self) -> bool:
        """# Residual (bool)
        
        Whether residual connections are used in the Neural Logic Machine.
        """
        return self._residual_
        
    # METHODS ======================================================================================
    
    @override
    def act(self,
        state:  Any
    ) -> Any:
        """# Select Action.

        ## Args:
            * state (Any):  Observation of current environment state.

        ## Returns:
            * Any:  Action chosen.
        """
        # Ensure module is in evaluation mode.
        self.eval()
        
        # Forward pass.
        with no_grad(): return self.forward(state)
    
    def forward(self,
        inputs: List[Tensor],
        depth:  int =           None
    ) -> List[Tensor]:
        """# Forward Pass.
        
        Forward pass through Neural Logic Machine.

        ## Args:
            * inputs    (List[Tensor]):     List of input tensors.
            * depth     (int, optional):    Depth of layers to use for inference. Defaults to None.

        ## Returns:
            * list[Tensor]: Final output after logical inference.
        """
        # Initialize outputs for each group.
        outputs:    List[Tensor] =      [None for _ in range(self.breadth + 1)]
        
        # Initialize copy of input tensors.
        temp:       List[Tensor] =      inputs
        
        # If no specific depth is provided, use default.
        if depth is None:       depth:  int =   self.depth
        
        # If recursion not requested, ensure depth does not exceed the machine depth.
        if not self.recursion:  depth:  int =   min(depth, self.depth)
        
        # Define helper merge function.
        def merge(
            x:  Optional[Tensor],
            y:  Optional[Tensor]
        ) -> Tensor:
            """# Merge Tensors.

            ## Args:
                * x (Tensor | None):    Tensor input 1.
                * y (Tensor | None):    Tensor input 2.

            ## Returns:
                * Tensor:   Merged tensors.
            """
            # If x is not provided, return y.
            if x is None:   return y
            
            # If y is not provided, return x.
            if y is None:   return x
            
            # Otherwise, return concatenated tensors.
            return cat(tensors = [x, y], dim = -1)
        
        # Initialize last layer for recursion.
        last_layer: LogicLayer | None = None
        
        # For each depth level...
        for level in range(depth):
            
            # If using IO residual and not on first level...
            if level > 0 and self.io_residual:
                
                # Merge pairs of input tensors.
                for i, input in enumerate(inputs): temp[i] = merge(temp[i], input)
                
            # If recursion is enabled...
            if self._recursion_ and level >= 3:
                
                # Assert that residual is not also being used.
                assert not self.residual, "Recursion not permitted while also using residual"
                
                # Alternate between layers for weight sharing.
                last_layer, layer =     last_layer, self._layers_[level]
                
            # Otherwise, last layer is current layer.
            else: last_layer =          self._layers_[level]
            
            # Forward pass inputs through current layer.
            temp:   List[Tensor] =      last_layer(temp)
            
            # Apply mask to outputs.
            temp:   List[Tensor] =      self._mask_(
                                            dimensions = temp,
                                            index = level,
                                            masked_value = None
                                        )
            
            # If IO residual...
            if self.io_residual:
                
                # Merge outputs.
                for o, output in enumerate(temp): outputs[o] = merge(outputs[o], output)
                
        # If no IO residual, just use the final output as the result.
        if not self.io_residual: outputs = temp
        
        # Return outputs.
        return outputs
    
    @override
    def load_model(self,
        path:   str
    ) -> None:
        """# Load Agent Model.

        ## Args:
            * path  (str):  Path from which model save file can be located/loaded.
        """
        # Load model state from file.
        self.load_state_dict(load(path))
        
    @override
    def observe(self,
        new_state:  Any,
        reward:     float,
        done:       bool
    ) -> None:
        """# Observe.

        Store the transition (if needed). For NLM, this is a placeholder unless batching is used.
        """
        # NLM is stateless unless using memory buffer.
        pass
        
    @override
    def save_model(self,
        path:   str
    ) -> None:
        """# Save Agent's Model.

        ## Args:
            * path  (str):  Path at which agent's model will be saved.
        """
        # Save model state to file.
        save(self.state_dict(), path)
        
    # HELPERS ======================================================================================
        
    def _mask_(self,
        dimensions:     List[int],
        index:          int,
        masked_value:   int
    ) -> list[int]:
        """# Mask Entries.
        
        Mask out specific entries in a layer's output based on the specified connection mask.

        ## Args:
            * dimensions    (List[int]):    The dimensions of the current layer.
            * index         (int):          Index of the layer.
            * masked_value  (int):          Value to replace masked entries.

        ## Returns:
            * list[int]:    Modified dimensions list with masked entries.
        """
        # If connections have been defined...
        if self.connections is not None:
            
            # Assert that index is valid for connections.
            assert index < len(self.connections), f"Index {index} invalid for list of length {len(self.connections)}"
            
            # Reference mask for the layer's connection.
            mask:   list[bool] =    self.connections[index]
            
            # If the mask is defined...
            if mask is not None:
                
                # Assert compatible dimensions.
                assert len(mask) == len(dimensions),    f"Length of mask ({len(mask)} incompatible with dimensions length {len(dimensions)})"
                
                # Apply mask.
                dimensions: list[int] = [x if y else masked_value for x, y in zip(dimensions, mask)]
                
        # Return dimensions.
        return dimensions