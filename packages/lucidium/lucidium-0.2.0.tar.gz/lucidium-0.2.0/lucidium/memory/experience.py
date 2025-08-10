"""# lucidium.memory.experience

Defines structure and use of experience.
"""

__all__ = ["Experience"]

from dataclasses        import dataclass, field
from typing             import Any, Dict, Set, Tuple, Union

from lucidium.symbolic  import Predicate

@dataclass
class Experience():
    """# Experience
    
    Single environment interaction record containing observations and symbolic state.
    
    ## Args:
        * action            (Any):                              The action taken during the 
                                                                interaction.
        * reward            (float):                            The reward yielded or penalty 
                                                                incurred by the action.
        * observation       (Any):                              The original state or observation 
                                                                before the action.
        * next_observation  (Any):                              The updated state or observation 
                                                                after the action.
        * predicates        (Union[Set[Predicate], Predicate]): The symbolic representation of the 
                                                                original state.
        * next_predicates   (Union[Set[Predicate], Predicate]): The symbolic representation of the 
                                                                updated state.
        * done              (bool):                             True if the updated state is a 
                                                                terminal state.
        * episode           (int):                              The episode number in which the 
                                                                interaction occurred.
        * step              (int):                              The step number within the episode.
        * metadata          (Dict[str, Any]):                   Additional metadata associated with 
                                                                the interaction.
    """
    # Define properties.
    action:             Any
    reward:             float
    observation:        Any
    next_observation:   Any
    predicates:         Union[Set[Predicate], Predicate]
    next_predicates:    Union[Set[Predicate], Predicate]
    done:               bool
    episode:            int
    step:               int
    metadata:           Dict[str, Any] =    field(default_factory = dict)
    
    def __post_init__(self) -> None:
        """# Validate Properties."""
        # If predicates are not provided as sets, convert them to sets.
        if not isinstance(self.predicates, set):        self.predicates:        Set[Predicate] =    set(self.predicates)
        if not isinstance(self.next_predicates, set):   self.next_predicates:   Set[Predicate] =    set(self.next_predicates)
        
    # PROPERTIES ===================================================================================
    
    @property
    def state_transition(self) -> Tuple[Any, Any, float, Any, bool]:
        """# State Transition.
        
        Transition data using observation space representations of states.

        ## Returns:
            * Tuple[Any, Any, float, Any, bool]:
                * Original state/observation
                * Action taken
                * Reward yielded/penalty incurred by action
                * Updated state/observation
                * True if updated state is a terminal state
        """
        return  (
                    self.observation,
                    self.action,
                    self.reward,
                    self.next_observation,
                    self.done
                )
        
    @property
    def symbolic_transition(self) -> Tuple[Set[Predicate], Any, float, Set[Predicate], bool]:
        """# Symbolic Transition.
        
        Transition data using predicate representation of states.

        ## Returns:
            * Tuple[Any, Any, float, Any, bool]:
                * Original state/observation
                * Action taken
                * Reward yielded/penalty incurred by action
                * Updated state/observation
                * True if updated state is a terminal state
        """
        return  (
                    self.predicates,
                    self.action,
                    self.reward,
                    self.next_predicates,
                    self.done
                )
        
    # METHODS ======================================================================================
    
    def get_all_predicates(self) -> Set[Predicate]:
        """# Get All Predicates.

        ## Returns:
            * Set[Predicate]:   Union of original and updates predicates.
        """
        return self.predicates.union(self.next_predicates)