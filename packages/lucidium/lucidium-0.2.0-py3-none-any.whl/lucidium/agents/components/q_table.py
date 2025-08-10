"""# lucidium.agents.components.q_table

Defines the structure and utility of the Q-Table.
"""

__all__ = ["QTable"]

from ast                import literal_eval
from collections        import defaultdict
from json               import dump, load
from pathlib            import Path
from typing             import Any, Dict, Hashable, List, Literal, Tuple, Union

from numpy              import argmax, array, asarray, float64, full, max as np_max, ndarray, zeros
from numpy.random       import uniform
from numpy.typing       import NDArray

from lucidium.spaces    import Discrete

class QTable():
    """# Q-Table
    
    Structure for tracking action "qualities" for tabular agents.
    """
    
    def __init__(self,
        action_space:           Union[int, Discrete],
        initialization_method:  Literal["zeros", "random", "small-random", "optimistic"] =  "zeros"
    ):
        """# Instantiate Q-Table.

        ## Args:
            * actions               (int | Discrete):   Actions accounted for by Q-Table.
            * initialization_method (str):              Method by which table values will be initialized. Defaults to "zeros".
                * "zeros":          Common choice when you assume that the agent has no prior 
                                    knowledge of the environment and should learn everything from 
                                    scratch. All states and actions start with equal value.
                * "random":         Useful when you want the agent to start with some variability 
                                    in its Q-values and potentially avoid any symmetry in the 
                                    learning process. It may help in environments where different 
                                    actions in the same state can have varying levels of importance 
                                    or expected rewards.
                * "small-random":   Similar to random initialization, but with smaller values to 
                                    prevent large, unrealistic initial biases. It's a good choice 
                                    when you want to start with some exploration but without the 
                                    extreme variance that might come with large random values.
                * "optimistic":     Often used to encourage exploration by making every state-action 
                                    pair initially appear to be rewarding. Over time, the agent will 
                                    update these values based on the actual rewards received.
        """
        # Assert that action space is either an integer or a discrete space.
        assert isinstance(action_space, (int, Discrete)), f"Invalid action space type provided: {type(action_space)}"
        
        # Define number of actions.
        self._number_of_actions:        int =                   action_space                        \
                                                                if isinstance(action_space, int)    \
                                                                else action_space.n
        
        # Define value initialization method.
        self._initialization_method_:   str =                   initialization_method
        
        # Initialize table.
        self._table_:                   Dict[int, NDArray] =    defaultdict(self._initialize_row_)
        
    # METHODS ======================================================================================
    
    def deserialize(self,
        data:   Dict[Any, List[float]]
    ) -> None:
        """# Deserialize Dictionary to Table."""
        # Read dictionary into table.
        for k, v in data.items(): self._table_[literal_eval(k)] = array(v, dtype = float64)
        
    def get_best_action(self,
        state:  Union[Tuple[Union[int, float], ...], int]
    ) -> int:
        """# Get Bast Action.
        
        Get the highest quality action for the given state.

        ## Args:
            * state (Tuple[Union[int, float], ...] | int):  State being evaluated.

        ## Returns:
            * int:  Highest quality action for state.
        """
        return int(argmax(self[state]))
    
    def get_best_value(self,
        state:  Union[Tuple[Union[int, float], ...], int]
    ) -> float:
        """# Get Best Value.

        ## Args:
            * state (Tuple[Union[int, float], ...] | int):  State being evaluated.

        ## Returns:
            * float:    Highest action value found for state.
        """
        return np_max(self[state])
        
    def load(self,
        path:   Union[str, Path]
    ) -> None:
        """# Load (Table from File).

        ## Args:
            * path  (str | Path):   Path from which table will be loaded.
        """
        # Load table from file.
        with Path(path).open("r", encoding = "utf-8") as file_in: self.deserialize(data = load(file_in))
        
    def save(self,
        path:   Union[str, Path]
    ) -> None:
        """# Save (Table to File).

        ## Args:
            * path  (Union[str, Path]): Path at which table will be saved.
        """
        # Ensure path is proper.
        path:   Path =  Path(path)
        
        # Create directories if they dont exist.
        path.parent.mkdir(parents = True, exist_ok = True)
        
        # Write table to file.
        with path.open(mode = "w", encoding = "utf-8") as file_out: dump(self.serialize(), fp = file_out)
    
    def serialize(self) -> Dict[Any, List[float]]:
        """# Serialize Table to Dictionary.
        
        ## Returns:
            * Dict[Any, List[Float]]:   JSON-compatible table format.
        """
        return {k: v.tolist() for k, v in self._table_.items()}
            
    # HELPERS ======================================================================================
    
    def _initialize_row_(self) -> NDArray:
        """# Initialize Row.
        
        ## Raises:
            * ValueError:   If invalid initialization method is provided.

        ## Returns:
            * NDArray:  Registry of action values for given state.
        """
        # Match initialization method.
        match self._initialization_method_:
            
            # Optimistic.
            case "optimistic":      return full(shape = self._number_of_actions, fill_value = 1.0, dtype = float64)
            
            # Random.
            case "random":          return uniform(low = -1.0, high = 1.0, size = self._number_of_actions).astype(float64)
            
            # Small Random.
            case "small-random":    return uniform(low = -0.1, high = 0.1, size = self._number_of_actions).astype(float64)
            
            # Zeros.
            case "zeros":           return zeros(shape = self._number_of_actions, dtype = float64)
            
            # Invalid method.
            case _:                 raise ValueError(f"Invalid initialization method: {self._initialization_method_}")
            
    def _normalize_state_(self,
        state:  Union[int, List, Tuple, NDArray]
    ) -> Hashable:
        """# Normalize State.

        ## Args:
            * state (Union[int, List, Tuple, NDArray]): State provided by agent.

        ## Returns:
            * Hashable: Hashable representation of unique state.
        """
        # Just provide state if it is an integer.
        if isinstance(state, int): return state
        
        # Otherwise, normalize other formats.
        return tuple(asarray(state).flatten().astype(float64))
    
    # DUNDERS ======================================================================================
    
    def __contains__(self,
        state:  Union[Tuple[Union[int, float], ...], int]
    ) -> bool:
        """# Table Contains State?

        ## Args:
            * state (Union[Tuple[Union[int, float], ...], int]):    State being searched for.

        ## Returns:
            * bool: True if state exists in table.
        """
        return self._normalize_state_(state = state) in self._table_
    
    def __getitem__(self,
        state:  Union[Tuple[Union[int, float], ...], int]
    ) -> NDArray:
        """# Get Action Values.

        ## Args:
            * state (Tuple[Union[int, float], ...] | int):  State whose action value(s) is being 
                                                            fetched.

        ## Returns:
            * NDArray:  State's action value(s).
        """
        return self._table_[self._normalize_state_(state = state)]
    
    def __len__(self) -> int:
        """# Table Length.

        ## Returns:
            * int:  Number of states currently represented by table.
        """
        return len(self._table_)
    
    def __setitem__(self,
        key:    Tuple[Union[Tuple[Union[int, float], ...], int], int],
        value:  float
    ) -> None:
        """# Set Action Value.

        ## Args:
            * key:
                * Tuple[Tuple[int | float] | int:   State index.
                * int:                              Action index.
            * value (float):                        Value being assigned at state, action index.
        """
        self._table_[self._normalize_state_(state = key[0])][key[1]] = value