"""# lucidium.agents.sarsa.args

Argument definitions and parsing for SARSA agent.
"""

__all__ = ["register_sarsa_parser"]

from argparse   import _ArgumentGroup, ArgumentParser, _SubParsersAction

def register_sarsa_parser(
    parent_subparser:   _SubParsersAction
) -> None:
    """# Register SARSA Argument Parser.
    
    Add SARSA agent sub-parser & arguments to parent's sub-parser.

    ## Args:
        * parent_subparser  (_SubParsersAction):    Parent's sub-parser object.
    """
    # Initialize SARSA Agent parser.
    _parser_:       ArgumentParser =    parent_subparser.add_parser(
        name =          "sarsa",
        help =          "SARSA agent.",
        description =   """SARSA is an off-policy, tabular-based, value-based algorithm.""",
        epilog =        """Implementation based on "SARSA" by Watkins & Dayan (1992). Link to 
                        paper: https://link.springer.com/content/pdf/10.1007/BF00992698.pdf"""
    )
    
    _subparser_:    _SubParsersAction = _parser_.add_subparsers(
        dest =          "action",
        help =          """Action that agent will execute."""
    )

    # +============================================================================================+
    # | BEGIN ARGUMENTS                                                                            |
    # +============================================================================================+
    
    # LEARNING ============================================================
    _learning_:     _ArgumentGroup =    _parser_.add_argument_group(title = "Learning (Alpha)")

    _learning_.add_argument(
        "--learning-rate", "--alpha",
        dest =      "learning_rate",
        type =      float,
        default =   0.1,
        help =      """Controls how much new information overrides old information when updating 
                    Q-values. A higher learning rate means the agent learns faster, updating 
                    Q-values more significantly with new experiences. Conversely, a lower learning 
                    rate leads to more gradual updates, potentially stabilizing training but slowing 
                    down convergence. Defaults to 0.1."""
    )
    
    # DISCOUNT ============================================================
    _discount_:     _ArgumentGroup =    _parser_.add_argument_group(title = "Discount (Gamma)")
    
    _discount_.add_argument(
        "--discount-rate", "--gamma",
        dest =      "discount_rate",
        type =      float,
        default =   0.99,
        help =      """Determines the importance of future rewards. A factor of 0 will make the 
                    agent "myopic" (or short-sighted) by only considering current rewards, while a 
                    factor approaching 1 will make it strive for a long-term high reward. Defaults 
                    to 0.99."""
    )
    
    # EXPLORATION =========================================================
    _exploration_:  _ArgumentGroup =    _parser_.add_argument_group(title = "Exploration (Epsilon)")
    
    _exploration_.add_argument(
        "--exploration-rate", "--epsilon",
        dest =      "exploration_rate",
        type =      float,
        default =   1.0,
        help =      """Probability that the agent will choose a random action, rather than selecting 
                    the action that is believed to be optimal based on its current knowledge (i.e., 
                    the action with the highest Q-value). When set high, the agent is more likely to 
                    explore new actions. When low, the agent favors exploiting its current knowledge. 
                    To utilize a SARSA agent as presented in the seminal paper, simply define 
                    this value as 0.0 to neglect exploration. Defaults to 1.0."""
    )
    
    _exploration_.add_argument(
        "--exploration-decay", "--epsilon-decay",
        dest =      "exploration_decay",
        type =      float,
        default =   0.99,
        help =      """Controls how quickly the exploration rate (ϵϵ) decreases over time. The 
                    exploration rate determines how often the agent selects random actions 
                    (explores) versus exploiting its learned knowledge (selecting the best action 
                    based on Q-values). A decay factor less than 1 (e.g., 0.995) causes the 
                    exploration rate to gradually decrease, leading to more exploitation as the 
                    agent learns more about the environment. Defaults to 0.99."""
    )
    
    _exploration_.add_argument(
        "--exploration-min", "--epsilon-min",
        dest =      "exploration_min",
        type =      float,
        default =   0.01,
        help =      """Specifies the minimum exploration rate that the agent will reach after the 
                    exploration decay process. This ensures that the agent does not completely stop 
                    exploring and retains a small chance to explore randomly, even in later stages 
                    of training. By setting a minimum value for exploration, the agent can still 
                    occasionally discover new actions, avoiding getting stuck in a local optimum.
                    Defaults to 0.01."""
    )
    
    _exploration_.add_argument(
        "--decay-interval",
        dest =      "decay_interval",
        type =      str,
        choices =   ["by-episode", "by-step"],
        default =   "by-step",
        help =      """Interval by which exploration rate will decay. Decaying by step at a small 
                    rate is convention, however decaying by episode at a larger rate is sometimes 
                    used."""
    )
    
    # Q-TABLE INITIALIZATION ==============================================
    _q_table_:      _ArgumentGroup =    _parser_.add_argument_group(title = "Q-Table Initialization")
    
    _q_table_.add_argument(
        "--initialization-method", "--init-method",
        dest =      "initialization_method",
        type =      str,
        choices =   ["zeros", "random", "small-random", "optimistic"],
        default =   "zeros",
        help =      """Initialize Q-Table with specific values. "zeros" is a common choice when you 
                    assume that the agent has no prior knowledge of the environment and should learn 
                    everything from scratch. All states and actions start with equal value. "random" 
                    is useful when you want the agent to start with some variability in its Q-values 
                    and potentially avoid any symmetry in the learning process. It may help in 
                    environments where different actions in the same state can have varying levels 
                    of importance or expected rewards. "small-random" is similar to random 
                    initialization, but with smaller values to prevent large, unrealistic initial 
                    biases. It's a good choice when you want to start with some exploration but 
                    without the extreme variance that might come with large random values. 
                    "optimistic" is often used to encourage exploration by making every state-action 
                    pair initially appear to be rewarding. Over time, the agent will update these 
                    values based on the actual rewards received.Defaults to "zeros"."""
    )

    # +============================================================================================+
    # | END ARGUMENTS                                                                              |
    # +============================================================================================+