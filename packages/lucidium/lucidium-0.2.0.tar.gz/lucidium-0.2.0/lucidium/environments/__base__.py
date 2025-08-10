"""# lucidium.environments.base

This module provides the base class for all environments in the Lucidium framework.
"""

__all__ = ["Environment"]

from abc        import ABC, abstractmethod
from typing     import Any, Dict, Tuple

class Environment(ABC):
    """Abstract Environment Class
    
    This class defines the base structure for an environment that can be interacted with by agents.
    
    ## Properties:
        * action_space  (Any):  Actions possible within the environment.
        * state_space   (Any):  Quantification of possible states in which the environment can be 
                                observed.
    """
        
    # PROPERTIES ===================================================================================
    
    @property
    @abstractmethod
    def action_space(self) -> Any:
        """# (Environment) Action Space
        
        Actions possible within environment.
        """
        pass
    
    @property
    @abstractmethod
    def done(self) -> bool:
        """# (Environment) is Done?

        True if environment has reached a terminal state.
        """
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """# (Environment's) Name
        
        Proper name of environment.
        """
        pass
    
    @property
    @abstractmethod
    def observation_space(self) -> Any:
        """# (Environment) Observation Space
        
        Observations possible within environment.
        """
        pass
    
    @property
    @abstractmethod
    def statistics(self) -> Dict[str, Any]:
        """# (Environment) Statistics

        Running statistics pertaining to interactions with the environemnt
        """
        pass
    
    # METHODS ======================================================================================
    
    @abstractmethod
    def reset(self) -> Any:
        """# Reset Environment.
        
        Reset environment and provide the initial state.
        
        ## Returns:
            * Any:  Initial state of the environment.
        """
        pass
    
    @abstractmethod
    def step(self,
        action: Any
    ) -> Tuple[Any, float, bool, Dict]:
        """# Step.

        The second critical step in the reinforcement learning loop.

        Applies the agent's action, updates the environment state, and returns the resulting new 
        state, reward, done flag, and optional metadata.
        
        ## Args:
            * action    (Any):  Action submitted by agent.
        
        ## Returns:
            * Any:              New state of the environment.
            * float:            Reward yielded/penalty incurred by action submitted by agent.
            * bool:             True if new state of environment is terminal.
            * Dict[str, Any]:   Metadata/information related to interaction event.
        """
        pass