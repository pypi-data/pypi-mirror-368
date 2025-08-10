"""# lucidium.registries.command_registry

Defines the command registry system.
"""

__all__ = ["CommandRegistry"]

from argparse                           import _SubParsersAction
from typing                             import Any, Callable, Dict

from lucidium.registries.command_entry  import CommandEntry

class CommandRegistry():
    """# Command Registry
    
    Command registry system.
    """
    
    def __init__(self,
        name:   str
    ):
        """# Instantiate Command Registry.

        ## Args:
            * name  (str):  Name of the class that the registry stores commands for.
        """
        # Define name.
        self._name_:    str =   name
        
        # Initialize entry map.
        self._entries_: Dict[str, CommandEntry] =   {}
        
    # PROPERTIES ===================================================================================
    
    @property
    def entries(self) -> Dict[str, CommandEntry]:
        """# Command Registry Entries"""
        return self._entries_
    
    @property
    def name(self) -> str:
        """# Command Registry Name"""
        return self._name_
    
    # METHODS ======================================================================================
    
    def dispatch(self,
        command:    str,
        **kwargs
    ) -> Any:
        """# Dispatch (Command).

        ## Args:
            * command   (str):  Command to which arguments are being dispatched.

        ## Returns:
            * Any:  Data returned from command.
        """
        return self._entries_[command].entry_point(**kwargs)
    
    def register(self,
        name:           str,
        entry_point:    Callable,
        parser:         Callable
    ) -> None:
        """# Register Command.

        ## Args:
            * name          (str):      Name of command.
            * entry_point   (Callable): Command's main process entry point.
            * parser        (Callable): Command argument parser registeration handler.
        """
        # Assert that entry does not already exist.
        if name in self._entries_: raise ValueError(f"{name} is already registered.")
        
        # Register entry.
        self._entries_[name] =  CommandEntry(
                                    name =          name,
                                    entry_point =   entry_point,
                                    parser =        parser
                                )
    
    def register_parsers(self,
        subparser:  _SubParsersAction
    ) -> None:
        """# Register Argument Parsers.

        ## Args:
            * subparser (_SubParsersAction):    Command sub parser of parent parser.
        """
        # For each registered command...
        for command in self._entries_.values():
            
            # Register its parser.
            command.register_parser(subparser = subparser)
    
    # DUNDERS ======================================================================================
    
    def __getitem__(self,
        key:    str
    ) -> CommandEntry:
        """# Get Command Registry Entry.

        ## Args:
            * key   (str):  Key of command entry requested.
            
        ## Raises:
            * KeyError: If registry entry does not exist.

        ## Returns:
            * CommandEntry: Command entry requested.
        """
        # Assert that entry exists.
        if key not in self._entries_: raise KeyError(f"{key} is not registered.")
        
        # Provide requested entry.
        return self._entries_[key]
    
    def __len__(self) -> int:
        """# Number of Registrations"""
        return len(self._entries_)
    
    def __repr__(self) -> str:
        """# Command Registry Object Representation"""
        return f"""<CommandRegistry({len(self._entries_)} entries)>"""