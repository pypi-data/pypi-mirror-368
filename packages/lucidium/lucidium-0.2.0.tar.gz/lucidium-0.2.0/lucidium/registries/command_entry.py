"""# lucidium.registries.command_entry

Defines the structure and utility of a command registry entry.
"""

__all__ = ["CommandEntry"]

from argparse   import _SubParsersAction
from typing     import Callable

class CommandEntry():
    """# Command Entry
    
    Storage of command registration entry data.
    """
    
    def __init__(self,
        name:           str,
        entry_point:    Callable,
        parser:         Callable
    ):
        """# Instantiate Command Registration Entry.

        ## Args:
            * name          (str):      Name of command.
            * entry_point   (Callable): Command's main process entry point.
            * parser        (Callable): Command argument parser registeration handler.
        """
        # Define properties.
        self._name_:        str =       name
        self._entry_point_: Callable =  entry_point
        self._parser_:      Callable =  parser
        
    # PROPERTIES ===================================================================================
    
    @property
    def entry_point(self) -> Callable:
        """# Command's Entry Point

        Command's main process entry point.
        """
        return self._entry_point_
    
    @property
    def name(self) -> str:
        """# Command's Name"""
        return self._name_
    
    @property
    def parser(self) -> Callable:
        """# Command's Parser

        Command argument parser registeration handler.
        """
        return self._parser_
    
    # METHODS ======================================================================================
    
    def register_parser(self,
        subparser:  _SubParsersAction
    ) -> None:
        """# Register Parser.

        ## Args:
            * sub_parser    (_SubParsersAction):    Parent's sub parser.
        """
        self._parser_(subparser)
        
    # DUNDERS ======================================================================================
    
    def __repr__(self) -> str:
        """# Command Entry Object Representation"""
        return f"""<CommandEntry(command = {self.name}, entry_point = {self.entry_point}, parser = {self.parser})>"""