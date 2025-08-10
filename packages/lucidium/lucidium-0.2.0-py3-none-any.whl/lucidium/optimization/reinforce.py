"""# lucidium.optimization.reinforce

Reinforce loss algorithm as presented in the 1992 paper by Ronald J. Williams.

## References:
Paper: https://link.springer.com/content/pdf/10.1007/BF00992696.pdf
"""

__all__ = ["ReinforceLoss"]

from typing     import Dict, Optional, Tuple

from torch      import Tensor
from torch.nn   import Module, NLLLoss

class ReinforceLoss(Module):
    """# Reinforce Loss

    Reinforce loss function.

    ## References:
    Paper: https://link.springer.com/content/pdf/10.1007/BF00992696.pdf
    """
    
    def __init__(self,
        entropy_beta:   Optional[float] =   None
    ):
        """# Instantiate Reinforce Loss.

        ## Args:
            * entropy_beta  (float):    Coefficient for entropy regularization.
        """
        # Initialize module.
        super(ReinforceLoss, self).__init__()
        
        # Define negative log-likelihood loss.
        self._nlll_:            NLLLoss =   NLLLoss(reduction = "none")
        
        # Define entropy.
        self._entropy_beta_:    float =     entropy_beta
        
    # METHODS ======================================================================================
    
    def forward(self,
        policy:             Tensor,
        action:             Tensor,
        discount_reward:    Tensor,
        entropy_beta:       Optional[float]
    ) -> Tuple[Tensor, Dict[str, Tensor]]:
        """# Compute Reinforce Loss.

        ## Args:
            * policy            (Tensor):   Action probability distribution.
            * action            (Tensor):   Actions taken (indices).
            * discount_reward   (Tensor):   Discounted returns for each action.
            * entropy_beta      (float):    Override for entropy beta.

        ## Returns:
            * loss      (Tensor):               Scalar loss tensor.
            * monitors  (Dict[str, Tensor]):    Dictionary with monitoring terms.
        """
        # Initialize monitors map.
        monitors:       Dict[str, Tensor] = {}
        
        # Compute entropy.
        entropy:        Tensor =            -(policy * policy.log()).sum(dim = 1).mean()
        
        # Compute negative log-likelihood for chosen actions.
        nll:            Tensor =            self._nlll_(policy.log(), action)
        
        # Multiply by discounted rewards.
        loss:           Tensor =            (nll * discount_reward).mean()
        
        # Determine use of entropy beta provided or the one defined on initialization.
        entropy_beta:   float =             entropy_beta or self._entropy_beta_
        
        # If at least one of those is defined...
        if entropy_beta is not None:
            
            # Define loss.
            monitors["reinforce_loss"] =    loss
            monitors["entropy_loss"] =      -entropy * entropy_beta
            
            # Compute total loss.
            loss -= entropy * entropy_beta
            
        # Define entropy.
        monitors["entropy"] = entropy
        
        # Provide results.
        return loss, monitors