"""# lucidium.environments.block_world.components.world

Defines the Block World container that manages all logical block relationships and actions.
"""

__all__ = ["World"]

from functools                                              import cached_property
from random                                                 import choice, shuffle
from typing                                                 import Dict, List, Optional, Tuple

from numpy                                                  import array
from numpy.typing                                           import NDArray
from torch                                                  import float32, tensor, Tensor

from lucidium.environments.block_world.components.block     import Block

class World():
    """# (Block World) World

    Central logic container for a Block World environment instance. Manages relationships between 
    blocks and enforces movement rules.

    Blocks are arranged as trees rooted in a single ground block, and actions such as `move()` 
    manipulate the tree by reassigning parent-child links.
    
    Adapted from: https://github.com/google/neural-logic-machines/tree/master/scripts/blocksworld
    """
    
    def __init__(self,
        block_quantity: List[Block] =   3,
        random_order:   bool =          False,
        one_stack:      bool =          False,
        **kwargs
    ):
        """# Instantiate World.

        ## Args:
            * block_quantity    (int):  Number of blocks to place in environment. Defaults to 3.
            * random_order      (bool): Use random block ordering.
            * one_stack         (bool): Initialize blocks in one stack.
        """
        # Define configuration.
        self._block_quantity_:      int =           block_quantity
        self._use_random_order_:    bool =          random_order
        self._use_one_stack_:       bool =          one_stack
        
        # Initialize block storage and ordering.
        self._blocks_:              List[Block] =   []
        self._random_order_:        List[int] =     None
        self._inverse_order_:       List[int] =     None
        
        # Trigger block generation.
        self.reset()
        
    # PROPERTIES ===================================================================================
    
    @property
    def blocks(self) -> List[Block]:
        """# Blocks.

        Blocks currently stored in world.
        """
        # If no random ordering is being used, simply return blocks.
        if not self._use_random_order_: return self._blocks_.copy()
        
        # Otherwise, return blocks in random order prescribed.
        return [self._blocks_[self._random_order_[b]] for b in range(len(self._blocks_))].copy()
    
    @property
    def size(self) -> int:
        """# Block Quantity

        Quantity of blocks in world.
        """
        return self._block_quantity_
    
    @property
    def stacks(self) -> List[List[Block]]:
        """# (Block) Stacks.

        Current stack(s) of blocks in world.
        """
        # Extract ground block.
        ground: Block = self._blocks_[0]
        
        # Define recursive child appender.
        def collect_chain(block: Block) -> List[Block]:
            """# Collect (Block) Chain.

            ## Args:
                * block (Block):    Block whose children will be added to stack.
                
            ## Returns:
                * List[Block]:  Block's child chain.
            """
            return [block] + [child for c in block.children for child in collect_chain(c)]
            
        # Append chain to list of stacks.
        return [collect_chain(block = root) for root in [block for block in ground.children]]
    
    # METHODS ======================================================================================
            
    def block_is_moveable(self,
        from_index: int,
        to_index:   int
    ) -> bool:
        """# Block is Moveable?

        ## Args:
            * from_index    (int):  Block to be picked up.
            * to_index      (int):  Block to be stacked onto.

        ## Returns:
            * bool: True if block in question is moveable and the other block is placeable.
        """
        return self._blocks_[from_index].is_moveable and self._blocks_[to_index].is_placeable
    
    def encode(self) -> Tensor:
        """# Encode World.

        ## Returns:
            * Tensor:   Tensor representation of world.
        """
        return tensor(self._get_coordinates_(), dtype = float32)
    
    def get_configuration(self) -> List[int]:
        """# Get Configuration.

        ## Returns:
            * List[int]:    Parent index for each block (-1 for ground).
        """
        return [block.parent.id if block.parent is not None else -1 for block in self._blocks_]
    
    def get_coordinates(self,
        absolute:   bool =  False,
        sort:       bool =  False
    ) -> NDArray:
        """# Get Coordinates.

        Args:
            absolute (bool, optional): _description_. Defaults to False.
            sort (bool, optional): _description_. Defaults to False.

        Returns:
            NDArray: _description_
        """
        # Initialize list of coordinates.
        coordinates:    List[Tuple[int, int]] = [None for _ in range(self._block_quantity_)]
        
        # Define depth first search recursion.
        def depth_first_search(block: Block) -> None:
            """# Depth First Search

            ## Args:
                * block (Block):    Block whose sub-tree is being searched.
            """
            # If this block is the ground...
            if block.is_ground:
                
                # It's coordinate is the origin.
                coordinates[block.id] = (0, 0)
                
                # For each child...
                for c, child in enumerate(block.children):
                    
                    # Assign its coordinate.
                    coordinates[child.id] = (self._get_inverse_index_(child.id) if absolute else c, 1)
                    
                # Recurse on child.
                depth_first_search(block = child)
                
            # Otherwise...
            else:
                
                # Extract coordinate already found.
                coordinate: Tuple[int, int] =   coordinates[block.id]
                
                # Assert that one was defined.
                assert coordinate is not None, f"Block {block.id} coordinate was not defined yet."
                
                # Extract components.
                x, y = coordinate
                
                # For each child...
                for child in block.children:
                    
                    # Increment the child's y component.
                    coordinates[child.id] = (x, y + 1)
                    
                    # Recurse on child.
                    depth_first_search(child)
                    
        # Begin search from ground.
        depth_first_search(block = self._blocks_[0])
        
        # Apply permutation.
        coordinates:    NDArray =   array(self._permute_(sequence = coordinates))
        
        # Provide coordinates.
        return array(sorted(list(map(tuple, coordinates)))) if sorted else coordinates
    
    def move_block(self,
        from_index: int,
        to_index:   int
    ) -> Tuple[bool, Dict[str, str]]:
        """# Move Block.

        Move a block onto another, if the move is allowed.

        ## Args:
            * from_index    (int):  Block to be picked up.
            * to_index      (int):  Block to be stacked onto.
            
        ## Returns:
            * bool:             True if move was made successfully.
            * Dict[str, str]:   Event string.
        """
        # As long as indices are not the same, and the move is valid...
        if from_index != to_index \
            and self.block_is_moveable(from_index = from_index, to_index = to_index):
                
            # Pick up block.
            self._blocks_[from_index].pick_up()
            
            # Place block at intended position.
            self._blocks_[from_index].place_on(block = self._blocks_[to_index])
            
            # Provide result.
            return True, {"event": f"placed block {from_index} on {to_index}"}
        
        # Otherwise, report failure.
        return False, {"event": "attempted invalid move"}
    
    def reset(self) -> None:
        """# Reset (World).
        
        Reset world to initial state.
        """
        # Clear existing blocks.
        self._blocks_.clear()
        
        # Initialize ground block.
        self._blocks_:  List[Block] =   [Block(id = 0)]
        
        # Initialize list of leaves.
        leaves:         List[Block] =   [self._blocks_[0]]
        
        # For each block needing to be initialized.
        for b in range(1, self.size + 1):
            
            # Choose a random leaf block.
            other:  Block = choice(leaves)
            
            # Create a new block.
            this:   Block = Block(id = b)
            
            # Place this block on the other block.
            this.place_on(block = other)
            
            # If the other block is no longer placeable, or if we're creating only one stack...
            if self._one_stack_:
                
                # Remove the other block from leaves.
                leaves.remove(other)
                
            # Add new block to lists.
            self._blocks_.append(this)
            leaves.append(this)
            
        # If random ordering is enabled, set random order.
        if self._use_random_order_: self.set_random_order()
        
    def set_random_order(self) -> None:
        """# Set Random Order.
        
        Set random block index and calculate its inverse.
        """
        # Generate random block order.
        self._random_order_:    List[int] = shuffle(list(range(self._block_quantity_)))
        
        # Calculate inverse.
        self._inverse_order_:   List[int] = sorted(range(self._block_quantity_), key = lambda x: self._random_order_[x])
            
    # HELPERS ======================================================================================
    
    def _get_coordinates_(self,
        absolute:   bool =  False
    ) -> NDArray:
        """# Get coordinates of each block in world.
        
        ## Args:
            * absolute  (bool):
                * When True:    Block's coordinate will be (block's ID, block's height)
                * When False:   Block's coordinate will be (stack #, block's height)

        ## Returns:
            * NDArray:  Numpy array of block coordinates.
        """
        # Initialize array of coordinates.
        coordinates:    List[Tuple[int, int]] = []
        
        # For each block...
        for block in self._blocks_:
            
            # Append coordinate.
            coordinates.append((block.id if absolute and not block.is_ground else block.stack_root))
            
        # # Apply random ordering if set.
        # if self._random_order_ is not None: coordinates = [coordinates[self._random_order_[i]] for i in range(len(self.size))]
            
    
    def _get_ground_blocks_(self) -> Tensor:
        """# Get Ground Blocks.

        ## Returns:
            * Tensor:   Tensor representation of ground blocks.
        """
        return tensor([block.is_ground for block in self._blocks_])
    
    def _get_moveable_blocks_(self) -> Tensor:
        """# Get Moveable Blocks.

        ## Returns:
            * Tensor:   Tensor representation of moveable blocks.
        """
        return tensor([block.is_moveable for block in self._blocks_])
    
    def _get_placeable_blocks_(self) -> Tensor:
        """# Get Placeable Blocks.

        ## Returns:
            * Tensor:   Tensor representation of placeable blocks.
        """
        return tensor([block.is_placeable for block in self._blocks_])
    
    def _get_inverse_index_(self,
        index:  int
    ) -> int:
        """# Get Inverse Index.

        ## Args:
            * index (int):  Index whose inverse is being retrieved.

        ## Returns:
            * int:  Inverse of index provided.
        """
        return self._inverse_order_[index] if self._inverse_order_ is not None else index
        
    # DUNDERS ======================================================================================
    
    def __eq__(self,
        other:  "World"
    ) -> bool:
        """# (Worlds) Are Equal?"""
        # Indicate that blocks in each world are equal.
        return  all([
                    this_block == other_block 
                    for this_block, other_block 
                    in zip(self.blocks, other.blocks)
                ])
    
    def __repr__(self) -> str:
        """# (World) Object Representation."""
        return f"""<World(size = {self.size})>"""
    
    def __str__(self) -> str:
        """# (World) String Representation."""
        # Initialize row lines.
        world:  List[str] = []
        
        # For each possible block level...
        for level in reversed(range(self.size)):
            
            # Initialize rendering rows.
            top, middle = [], []
            
            # For each block stack...
            for stack in self.stacks:
                
                # If there is a block in the stack at the current level...
                if len(stack) > level:
                    
                    # Append the top of the block.
                    top.append("┏━━━┓")
                    
                    # Append the block ID.
                    middle.append(f"┃{stack[level].id:^3}┃")
                    
                # Otherwise...
                else:
                    
                    # Append empty spaces.
                    top.append("     ")
                    middle.append("     ")
                    
            # Write to line.
            world.extend([" ".join(top), " ".join(middle)])
            
        # Form platform.
        world.append("━" * (self.size * 5 + self.size - 1))
        
        # Return world string.
        return "\n".join(world)