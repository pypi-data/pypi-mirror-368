"""# lucidium.args

Lucidium application argument definitions and parsing.
"""

__all__ = ["parse_lucidium_arguments"]

from argparse                           import Action, ArgumentParser, _ArgumentGroup, HelpFormatter, Namespace, _SubParsersAction
from typing                             import override

from lucidium.registries                import AGENT_REGISTRY, ENVIRONMENT_REGISTRY

def parse_lucidium_arguments() -> Namespace:
    """# Parse Lucidium Arguments.
    
    This function should be called at the entry point of the Lucidium application. The name space of 
    argument keys and values that it provides will be passed/provided to subsequent module entry 
    points.
    
    ## Returns:
        * NameSpace:    Name space of parsed arguments and their values.
    """
    # Initialize primary parser
    _parser_:       ArgumentParser =    ArgumentParser(
        prog =          "lucidium",
        description =   """Suite of environments, models, & methods in pursuit of achieving organic 
                        reasoning & logic by means of deep reinforcement learning.""",
        formatter_class =   CommandHelpFormatter
    )

    # Initialize sub-parser
    _subparser_:    _SubParsersAction = _parser_.add_subparsers(
        dest =          "command",
        help =          "Lucidium commands."
    )

    # +============================================================================================+
    # | BEGIN ARGUMENTS                                                                            |
    # +============================================================================================+

    # LOGGING ======================================================================================
    _logging_:      _ArgumentGroup =    _parser_.add_argument_group(
        title =         "Logging",
        description =   "Logging configuration."    
    )

    _logging_.add_argument(
        "--logging-level",
        type =          str,
        choices =       ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "NOTSET"],
        default =       "INFO",
        help =          """Minimum logging level (DEBUG < INFO < WARNING < ERROR < CRITICAL). 
                        Defaults to "INFO"."""
    )

    _logging_.add_argument(
        "--logging-path",
        type =          str,
        default =       "logs",
        help =          """Path at which logs will be written. Defaults to "./logs/"."""
    )

    # +============================================================================================+
    # | END ARGUMENTS                                                                              |
    # +============================================================================================+
    
    # Register agent and environment parsers.
    AGENT_REGISTRY.register_parsers(parent_subparser = _subparser_)
    ENVIRONMENT_REGISTRY.register_parsers(parent_subparser = _subparser_)

    # Parse arguments
    return _parser_.parse_args()

class CommandHelpFormatter(HelpFormatter):
    """# Command Help Formatter.
    
    Custom help formatter that groups subcommands by category.
    """
    
    def __init__(self, *args, **kwargs):
        """# Instantiate Command Help Formatter."""
        # Initialize formatter.
        super(CommandHelpFormatter, self).__init__(*args, **kwargs)
    
    @override
    def _format_action(self,
        action: Action
    ) -> str:
        """# Format Action.
        
        Format an action for display in help output.
        
        Checks if the action is a subparsers action and applies categorized formatting if so, 
        otherwise defers to the parent implementation.

        ## Args:
            * action    (Action):   Action object being formatted.

        ## Returns:
            * str:  Formatted string representation of the action.
        """
        # If action has choices and a parser map...
        if hasattr(action, 'choices') and hasattr(action, '_name_parser_map'):
            
            # This is a subparsers action.
            return self._format_categorized_subparsers(action)
        
        # Otherwise, return simple command.
        return super()._format_action(action)
    
    @override
    def _format_categorized_subparsers(self,
        action: Action
    ) -> str:
        """Format Categorized Subparsers.
        
        Format subparsers grouped by category (Agents vs Environments).
        
        Loads the agent and environment registries to determine which commands belong to which 
        category, then formats them in separate sections.
        
        ## Args:
            * action:   The subparsers Action object containing command choices.
            
        ## Returns:
            * str:  Multi-line string with categorized command listings.
            
        **Note**: This method has side effects - it loads all registry entries to determine 
        categorization. Debug output is printed to help with troubleshooting registration issues.
        """        
        # Build the help text with categories.
        parts = []
        
        # Add the main description.
        if action.help: parts.append(f"{action.help}\n")
            
        # Add the agents section header.
        parts.append("Agents:\n")
        
        # For each registered agent...
        for name in AGENT_REGISTRY.entries:
            
            # If that agent corresponds to a command...
            if name in action.choices:
                
                # Extract the parser.
                parser:     ArgumentParser =    action.choices[name]
                
                # Get its description.
                help_text:  str =               getattr(parser, "description", "")
                
                # Append agent command entry.
                parts.append(f"  {name:<21} {help_text}")
            
        # Add the agents section header.
        parts.append("Environments:\n")
                
        # For each registered environment...
        for name in ENVIRONMENT_REGISTRY.entries:
            
            # If that environment corresponds to a command...
            if name in action.choices:
                
                # Extract the parser.
                parser:     ArgumentParser =    action.choices[name]
                
                # Get its description.
                help_text:  str =               getattr(parser, "description", "")
                
                # Append environment command entry.
                parts.append(f"  {name:<21} {help_text}")
        
        # Provide agent/environment help menus.
        return '\n'.join(parts)