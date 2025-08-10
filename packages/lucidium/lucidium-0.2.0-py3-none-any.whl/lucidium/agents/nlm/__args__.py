"""# lucidium.agents.nlm.args

Argument definitions and parsing for Neural Logic Machine agent.
"""

__all__ = ["register_nlm_parser"]

from argparse   import _ArgumentGroup, ArgumentParser, _SubParsersAction

def register_nlm_parser(
    parent_subparser:   _SubParsersAction
) -> None:
    """# Register Neural Logic Machine Argument Parser.
    
    Add NLM agent sub-parser & arguments to parent's sub-parser.

    ## Args:
        * parent_subparser  (_SubParsersAction):    Parent's sub-parser object.
    """
    # Initialize Neural Logic Machine agent parser.
    _parser_:           ArgumentParser =    parent_subparser.add_parser(
        name =          "nlm",
        help =          "Neural Logic Machine",
        description =   """Neural Logic Machine (NLM) is a neural-symbolic architecture for both 
                        inductive learning and logic reasoning. NLMs use tensors to represent logic 
                        predicates. This is done by grounding the predicate as True or False over a 
                        fixed set of objects. Based on the tensor representation, rules are 
                        implemented as neural operators that can be applied over the premise 
                        tensors and generate conclusion tensors.""",
        epilog =        """Implementation based on "Neural Logic Machines" by Honghua Dong et. al. 
                        (2019). Link to paper: https://arxiv.org/pdf/1904.11694.pdf"""
    )
    
    # Define sub-parser.
    _subparser_:        _SubParsersAction = _parser_.add_subparsers(
        title =         "action",
        description =   """Neural Logic Machine commands.""",
        dest =          "action"
    )

    # +============================================================================================+
    # | BEGIN ARGUMENTS                                                                            |
    # +============================================================================================+
    
    # DIMENSIONALITY ===============================================================================
    _dimensionality_:   _ArgumentGroup =    _parser_.add_argument_group(title = "Dimensionality")
    
    _dimensionality_.add_argument(
        "--depth",
        dest =          "depth",
        type =          int,
        default =       3,
        help =          """Number of logic layers with which NLM will be initialized. Defaults to 
                        3."""
    )
    
    _dimensionality_.add_argument(
        "--breadth",
        dest =          "breadth",
        type =          int,
        default =       2,
        help =          """Breadth with which each logic layer will be initialized. Defaults to 
                        2."""
    )
    
    _dimensionality_.add_argument(
        "--hidden-dimension",
        dest =          "hidden_dimension",
        type =          int,
        default =       128,
        help =          """Dimension of hidden layers within logic layers. Defaults to 128."""
    )
    
    # FEATURE FLAGS ================================================================================
    _flags_:            _ArgumentGroup =    _parser_.add_argument_group(title = "Feature Flags")
    
    _flags_.add_argument(
        "--exclude-self",
        dest =          "exclude_self",
        action =        "store_true",
        default =       False,
        help =          """Exclude multiple occurrences of the same variable."""
    )
    
    _flags_.add_argument(
        "--io-residual",
        dest =          "io_residual",
        action =        "store_true",
        default =       False,
        help =          """Use input/output-only residual connections. Mututally exclusive to using 
                        "--residual" flag."""
    )
    
    _flags_.add_argument(
        "--residual",
        dest =          "residual",
        action =        "store_true",
        default =       False,
        help =          """Use fully residual connections. Mututally exclusive to using 
                        "--io-residual" flag."""
    )
    
    _flags_.add_argument(
        "--recursion",
        dest =          "recursion",
        action =        "store_true",
        default =       False,
        help =          """Enable recursion for weight sharing."""
    )

    # +============================================================================================+
    # | END ARGUMENTS                                                                              |
    # +============================================================================================+