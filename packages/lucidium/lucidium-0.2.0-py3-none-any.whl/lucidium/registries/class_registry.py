"""# lucidium.registries.class_registry

Defines the class registry system.
"""

__all__ = ["ClassRegistry"]

from argparse                           import _SubParsersAction
from typing                             import Any, Callable, Dict, List, Optional, Type

from lucidium.registries.class_entry    import ClassEntry

class ClassRegistry():
    """# Class Registry
    
    Class registry system with lazy loading.
    """
    
    def __init__(self,
        name:   str
    ):
        """# Instantiate Class Registry.
        
        ## Args:
            * name  (str):  Name of the sub-module that the registry represents (e.g., "agents", 
                            "environments")
        """
        # Define sub-module name.
        self._name_:    str =                   name
        
        # Initialize entry map.
        self._entries_: Dict[str, ClassEntry] = {}
        
        # Initialize loaded flag.
        self._loaded_:  bool =                  False
        
    # PROPERTIES ===================================================================================
    
    @property
    def entries(self) -> Dict[str, ClassEntry]:
        """# Class Registry Entries"""
        return {name: entry.cls for name, entry in self._entries_.items()}.copy()
    
    @property
    def is_loaded(self) -> bool:
        """# Class Registry is Loaded?"""
        return self._loaded_
    
    @property
    def name(self) -> str:
        """# Class Registry Name."""
        return self._name_
        
    # METHODS ======================================================================================
    
    def dispatch(self,
        cls:    str,
        *args,
        **kwargs
    ) -> Any:
        """# Dispatch Command.

        ## Args:
            * cls   (str):  Class whose main process arguments are being dispatched to.

        ## Returns:
            * Any:  Data returned from command.
        """
        return self._entries_[cls].entry_point(*args, **kwargs)
    
    def get_entry(self,
        key:    str
    ) -> ClassEntry:
        """# Get Class Registry Entry.

        ## Args:
            * key   (str):  Key of entry being fetched.

        ## Returns:
            * ClassEntry:    Class Registry entry requested.
        
        ## Raises:
            * KeyError: If registry entry does not exist.
        """
        # Ensure that registry is loaded.
        self._ensure_loaded_()
        
        # Assert that entry exists.
        if key not in self._entries_: raise KeyError(f"{key} is not registered.")
        
        # Provide requested entry.
        return self._entries_[key]
    
    def list(self,
        filter_by:  Optional[List[str]] =   []
    ) -> Optional[List[str]]:
        """# List Entries.

        ## Args:
            * filter_by (Optional[List[str]], optional):    Tags by which entries will be filtered.

        ## Returns:
            * Optional[List[str]]:  List of entry names that satisfy tag filter(s).
        """
        # Ensure that registry is loaded.
        self._ensure_loaded_()
        
        # If no filters are provided, simply return all entries.
        if not filter_by: return list(self._entries_.keys())
        
        # Otherwise, returned filtered entries.
        return  [
                    name for name, entry 
                    in self._entries_.items() 
                    if  all(
                            tag in entry.tags
                            for tag in filter_by
                        )
                ]
        
    def load(self,
        name:       str,
        **kwargs
    ) -> Any:
        """# Load Registered Class.

        ## Args:
            * name  (str):  Class Registry entry name.

        ## Returns:
            * Any:  Instantiated class.
        """
        # Fetch entry according to name.
        entry:  ClassEntry =    self.get_entry(key = name)
        
        # Extract class.
        cls:    Type =          entry.cls
        
        # Load class.
        return cls(**kwargs)
        
    def load_all(self) -> None:
        """# Load all Registered Modules."""
        # Simply return if registry has already been loaded.
        if self.is_loaded: return
        
        # Otherwise, import all modules...
        self._import_all_modules_()
        
        # Record that registry has now been loaded.
        self._loaded_:  bool =  True
    
    def register(self,
        cls:            Type,
        name:           str,
        tags:           Optional[List[str]] =   [],
        entry_point:    Optional[Callable] =    None,
        parser:         Optional[Callable] =    None
    ) -> None:
        """# Register (Type).

        ## Args:
            * cls           (Type):                 Class being registered.
            * name          (str):                  Name of entry.
            * tags          (Optional[List[str]]):  Tags that describe the taxonomy of the class being registered.
            * entry_point   (Optional[Callable]):   Classe's main process entry point.
            * parser        (Optional[Callable]):   Argument parser handler.
                                                        
        ## Raises:
            * ValueError:   If entry already exists.
        """
        # Assert that entry does not already exist.
        if name in self._entries_: raise ValueError(f"{name} if already registered.")
        
        # Register entry.
        self._entries_[name] =  ClassEntry(
                                    cls =           cls,
                                    name =          name,
                                    tags =          tags,
                                    entry_point =   entry_point,
                                    parser =        parser
                                )
        
    def register_parsers(self,
        parent_subparser:   _SubParsersAction
    ) -> None:
        """# Register Argument Parsers.

        ## Args:
            * parent_subparser  (_SubParsersAction):    Command sub parser of parent parser.
        """
        # Ensure that registry is loaded.
        self._ensure_loaded_()
        
        # For each registered item...
        for entry in self._entries_.values():
            
            # If entry contains argument parser...
            if entry.parser:
                
                # Register parser.
                entry.register_parser(subparser = parent_subparser)
        
    # HELPERS ======================================================================================
    
    def _ensure_loaded_(self) -> None:
        """# Ensure Class Registry is Loaded."""
        if not self.is_loaded: self.load_all()
        
    def _import_all_modules_(self) -> None:
        """# Import All Modules.
        
        Dynamically import all modules in the package to trigger decorators.
        """
        from importlib  import import_module
        from pkgutil    import walk_packages
        from types      import ModuleType
        
        # Import the main package to get its path.
        package:    ModuleType = import_module(f"lucidium.{self._name_}")
        
        try:# Walk through all modules in the package.
            for _, module, _ in walk_packages(
                path =      package.__path__,
                prefix =    f"lucidium.{self._name_}.",
                onerror =   lambda x: None
            ):
                try:# Attempt import of module.
                    import_module(name = module)
                    
                # If a module cannot be imported...
                except ImportError as e:
                    
                    # Report error.
                    print(f"Error importing {module} module: {e}")
                   
        # If a package cannot be imported...
        except ImportError as e:
                    
            # Report error.
            print(f"Error importing {package} package: {e}")
        
    # DUNDERS ======================================================================================
    
    def __contains__(self,
        key:    str
    ) -> bool:
        """# ClassRegistry Contains Key?
        
        True if key is registered.
        """
        return key in self._entries_
    
    def __getitem__(self,
        key:    str
    ) -> ClassEntry:
        """# Get Class Registry Entry.

        ## Args:
            * key   (str):  Key of entry being fetched.

        ## Returns:
            * ClassEntry:    Class Registry entry requested.
        
        ## Raises:
            * KeyError: If registry entry does not exist.
        """
        # Assert that entry exists.
        if key not in self._entries_: raise KeyError(f"{key} is not registered.")
        
        # Provide requested entry.
        return self._entries_[key].cls
    
    def __len__(self) -> int:
        """# Number of Registrations."""
        return len(self._entries_)
    
    def __repr__(self) -> str:
        """# Class Registry Object Representation"""
        return f"""<ClassRegistry({len(self._entries_)} entries)>"""