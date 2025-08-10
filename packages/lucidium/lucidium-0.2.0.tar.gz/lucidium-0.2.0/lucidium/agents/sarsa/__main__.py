"""# lucidium.agents.sarsa.main"""

from logging                                import Logger

from lucidium.utilities                     import get_child

def main(
    action: str,
    **kwargs
) -> None:
    """# Execute SARSA Action.

    ## Args:
        * action    (str):  SARSA action being executed.
    """
    # Initialize logger.
    _logger_:       Logger =            get_child(
                                            logger_name =   "sarsa.main"
                                        )
    
    try:# Execute action.
        print("QLearning.main")
    
    except Exception as e:  _logger_.critical(f"Unexpected error caught: {e}", exc_info = True)