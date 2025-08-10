"""# lucidium.environments.block_world.base

Block World environment implementation.
"""

from logging                                            import Logger
from typing                                             import Any, Dict, override, Tuple, Union

from lucidium.environments.__base__                     import Environment
from lucidium.environments.block_world.__args__         import register_block_world_parser
from lucidium.environments.block_world.components.world import World
from lucidium.registries                                import register_environment
from lucidium.spaces                                    import MultiDiscrete
from lucidium.utilities                                 import get_child

@register_environment(
    name =      "block-world",
    tags =      ["planning", "symbolic", "discrete"],
    parser =    register_block_world_parser
)
class BlockWorld(Environment):
    """# Block World (Environment)
    
    BlockWorld is a classic AI planning domain where blocks can be stacked on top of each other or 
    placed on a table. The goal is to rearrange blocks from an initial configuration to achieve a 
    target configuration.
    
    Adapted from: https://github.com/google/neural-logic-machines/tree/master/scripts/blocksworld
    """
    
    def __init__(self,
        # Configuration.
        block_quantity:         int =   3,
        random_order:           bool =  False,
        one_stack:              bool =  False,
        shape_only:             bool =  False,
        fix_ground:             bool =  False,
        
        # Dynamics.
        fall_probability:       float = 0.0,
        no_effect_probability:  float = 0.0,
        
        # Reward/Penalty.
        success_reward:         float = 1.0,
        move_penalty:           float = -0.1,
        invalid_move_penalty:   float = -0.5,
        **kwargs
    ):
        """# Instantiate Block World (Environment).

        ## Args:
            * block_quantity        (int, optional):    Number of blocks in world. Must be between 2 
                                                        and 10. Defaults to 3.
            * random_order          (bool, optional):   Randomly permute block indices to prevent 
                                                        memorization of configuration. Defaults to 
                                                        False.
            * one_stack             (bool, optional):   Initialize blocks in one stack. Defaults to 
                                                        False.
            * fall_probability      (float, optional):  Probability that moved blocks will fall to 
                                                        ground. Defaults to 0.0.
            * no_efect_probability  (float, optional):  Probability that an action has no effect. 
                                                        Defaults to 0.0.
            * success_reward        (float, optional):  Reward yielded upon achieving target block 
                                                        configuration. Defaults to 1.0.
            * move_penalty          (float, optional):  Cost of making any move during game. 
                                                        Defaults to -0.1.
            * invalid_move_penalty  (float, optional):  Penalty incurred for attempting an invalid 
                                                        move. Defaults to -0.5.
        """
        # Initialize environment.
        super(BlockWorld, self).__init__()
        
        # Initialize logger.
        self.__logger__:                Logger =    get_child("block-world")
        
        # Define configuration.
        self._block_quantity_:          int =       block_quantity
        self._fall_probability_:        float =     fall_probability
        self._no_efect_probability_:    float =     no_effect_probability
        self._success_reward_:          float =     success_reward
        self._move_penalty_:            float =     move_penalty
        self._invalid_move_penalty_:    float =     invalid_move_penalty
        
        # Initialize world.
        self._world_:                   World =     World(
                                                        block_quantity =    block_quantity,
                                                        random_order =      random_order,
                                                        one_stack =         one_stack
                                                    )
        
        # Define target world.
        self._target_:                  World =     World(
                                                        block_quantity =    block_quantity,
                                                        random_order =      random_order,
                                                        one_stack =         one_stack
                                                    )
        
        # Log initialization for debugging.
        self.__logger__.debug(f"Initialized BlockWorld ({locals()})")
        
    # PROPERTIES ===================================================================================
    
    @override
    @property
    def action_space(self) -> MultiDiscrete:
        """# (Block World) Action Space."""
        return MultiDiscrete(shape = (self._block_quantity_, self._block_quantity_))
    
    @property
    def done(self) -> bool:
        """# (Grid World) Game is Done?

        True if current environment state matches target world state.
        """
        return self._world_ == self._target_
    
    @override
    @property
    def observation_space(self) -> MultiDiscrete:
        """# (Block World) Observation Space."""
        return MultiDiscrete(shape = (self._block_quantity_, self._block_quantity_, self._block_quantity_))
    
    # METHODS ======================================================================================
    
    def reset(self) -> None:
        """# Reset (Environment).
        
        Reset environment to a new initial state.
        """
        # Generate new initial world.
        self._world_.reset()
        
        # Generate new target world.
        self._target_.reset()
        
        # provide new environment state.
        return self._world_.encode()
    
    def step(self,
        action: Union[int, Tuple[int, int]]
    ) -> Tuple[Any, float, bool, Dict[str, Any]]:
        """# Step
        
        Update environment based on action submitted.

        ## Args:
            * action    (int | Tuple[int, int]):    Action submitted by agent.

        ## Returns:
            * Any:              Updated state after action.
            * float:            Reward yielded/penalty incurred by action.
            * bool:             True if environment has reached a terminal state.
            * Dict[str, Any]:   Metadata/environment information.
        """
        # Translate action to indices.
        from_index: int =   action // self._block_quantity_ if isinstance(action, int) else action[0]
        to_index:   int =   action %  self._block_quantity_ if isinstance(action, int) else action[1]
        
        # Attempt move.
        successful, event = self._world_.move_block(from_index = from_index, to_index = to_index)
        
        # Calculate penalty based on result (and validity) of action.
        penalty:    float = self._move_penalty_ if successful else self._invalid_move_penalty_
                            
        # Add reward for completion if target world is achieved.
        reward:     float = penalty + (self._success_reward_ if self.done else 0)
        
        # Provide action result.
        return self._world_.encode(), reward, self.done, event