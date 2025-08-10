"""# lucidium.environments.block_world..components.block

Defines the block component for the Block World environment.
"""

__all__ = ["Block"]

from typing             import List, Optional

from lucidium.symbolic  import predicate

class Block():
    """# (Block World) Block

    Represents a single block in the BlocksWorld domain, structured as a tree node with optional 
    parent and child links to form stacks.

    Each block maintains its parent (`father`) and a list of children, enabling construction of 
    multiple vertical stacks (towers) of blocks.

    A block is considered:
    * **Grounded** if it has no parent.
    * **Placeable** if it is grounded or has no children.
    * **Moveable** if it is not grounded and has no children.
    
    Adapted from: https://github.com/google/neural-logic-machines/tree/master/scripts/blocksworld
    """
    
    def __init__(self,
        id:  int,
        parent: Optional["Block"] =   None
    ):
        """# Instantiate Block.

        ## Args:
            * id        (int):      Id of block within storage context.
            * parent    (Block):    Block's parent, if block is not grounded.
        """
        # Define properties.
        self._id_:          int =               id
        self._parent_:      Optional[Block] =   parent
        self._children_:    List[Block] =       []
        
        # If parent if provided, add this block as its child.
        if parent is not None: parent.add_child(child = self)
        
    # PROPERTIES ===================================================================================
    
    @property
    def children(self) -> List["Block"]:
        """# (Block's) Children

        Children belonging to this block.
        """
        return self._children_.copy()
    
    @property
    def height(self) -> int:
        """# (Block's) Height.

        Height at which block is currently located.
        """
        # If this block is on the ground, its height is zero.
        if self.is_ground: return 0
        
        # Otherwise, this block is one unit higher than its parent.
        return self.parent.height + 1
    
    @property
    def id(self) -> int:
        """# (Block's) Id.

        Id of this block.
        """
        return self._id_
    
    @property
    def index(self) -> int:
        """# (Block) Index
        
        Block's index in world's block storage.
        """
        return self._id_
    
    @property
    @predicate(name = "ground")
    def is_ground(self) -> bool:
        """# (Block) is Ground?

        True if block is located on ground (has no parent). Semantically, this means that the block 
        *is the ground*.
        """
        return self._parent_ is None
    
    @property
    @predicate(name = "moveable")
    def is_moveable(self) -> bool:
        """# (Block) is Moveable?

        True if block is the ground (has no parent) and there are no blocks on top of it (has no 
        children).
        """
        return self._parent_ is not None and len(self._children_) == 0
    
    @property
    @predicate(name = "placeable")
    def is_placeable(self) -> bool:
        """# (Block) is Placeable?

        True if there are no blocks on top of this block (has no children) or this block is the 
        ground (has no parent).
        """
        return self._parent_ is None or len(self._children_) == 0
    
    @property
    def parent(self) -> "Block":
        """# (Block's) Parent

        Parent of this block.
        """
        return self._parent_
    
    @property
    def stack_size(self) -> int:
        """# (Block's) Stack Size.

        Number of blocks stacked on this block.
        """
        return 1 + sum(child.stack_size for child in self._children_)
    
    @property
    def stack_root(self) -> "Block":
        """# (Block's) Stack Root.

        The block at the bottom of the stack.
        """
        # If this block is the ground, root is this block.
        if self.is_ground: return self
        
        # Otherwise, starting with this block...
        current:    Block = self
        
        # Parse through parents until we find the ground...
        while not current.parent.is_ground:
            
            # Move to parent.
            current:    Block = current.parent
            
        # Provide the block located on the ground when we find it.
        return current
            
    
    # METHODS ======================================================================================
        
    def add_child(self,
        child:  "Block"
    ) -> None:
        """# Add Child.

        ## Args:
            * child (Block):    Child block being added.
        """
        # Add child, if it doesn't already exist.
        if child not in self._children_: self._children_.append(child)
    
    def pick_up(self) -> None:
        """# Pick Up (Block).
        
        Detach block from parent.
        
        ## Raises:
            * ValueError:   If block has no parent or is not moveable.
        """
        # If block has no parent...
        if self._parent_ is None:
            
            # Report error.
            raise ValueError(f"Block {self._id_} cannot be picked up (has no parent/is ground).")
        
        # If block is not moveable (has children on top)...
        if not self.is_moveable:
            
            # Report error.
            raise ValueError(f"Block {self._id_} is not moveable (has {len(self._children_)} children).")
        
        # Otherwise, remove this block from its parent.
        self._parent_.remove_child(child = self)
        
        # Remove parent.
        self._parent_ = None
        
    def place_on(self,
        block:  "Block"
    ) -> bool:
        """# Place on (Block).

        ## Args:
            * block (Block):    Block upon which this block will be placed.
            
        ## Returns:
            * bool: True is block is placed successfully.
        """
        # If target block is not placeable, this block cannot be placed.
        if not block.is_placeable: return False
        
        # Assign new parent.
        self._parent_ = block
        
        # Add this block to parent's children.
        block.add_child(child = self)
        
        # Indicate that block was successfully placed.
        return True
        
    def remove_child(self,
        child:  "Block"
    ) -> None:
        """# Remove Child.

        ## Args:
            * child (Block):    Child block being removed.

        ## Raises:
            * ValueError:   If the child is not actually attached to this block.
        """
        # If child does not exist for parent...
        if child not in self._children_:
            
            # Report error.
            raise ValueError(f"Block {child.id} is not a child of block {self._id_}")
        
        # Otherwise, remove child.
        self._children_.remove(child)
        
    def reset(self) -> None:
        """# Reset (Block).

        Reset block to initial state.
        """
        # Remove children.
        self._children_.clear()
        
        # Remove parent.
        self._parent_ = None
        
    # DUNDERS ======================================================================================
    
    def __eq__(self,
        other:  "Block"
    ) -> bool:
        """# (Blocks) Are Equal?"""
        # If other object is not a block, no comparison can be made.
        if not isinstance(other, Block): return False
        
        # Indicate if blocks have the same...
        return  all([
                    # ID
                    self.id             == other.id,
                    # Parent
                    self.parent.id      == other.parent.id,
                    # And children
                    set(self.children)  == set(other.children)
                ])
    
    def __hash__(self) -> int:
        """# (Block) Hash"""
        return hash(self._id_)
    
    def __repr__(self) -> str:
        """# (Block) Object Representation."""
        return  (
                    f"""<Block(id = {self._id_}, """
                    f"""ground = {self.is_ground}, """
                    f"""moveable = {self.is_moveable}, """
                    f"""placeable = {self.is_placeable}), """
                    f"""parent = {self.parent}>"""
                )
        
    def __str__(self) -> str:
        """# (Block) String Representation."""
        return str(self._id_)