"""# lucidium.environments.grid_world.components.grid

Defines the basic grid component of Grid World environment.
"""

__all__ = ["Grid"]

from typing                                                 import Any, Dict, List, Optional, Set, Tuple

from termcolor                                              import colored

from lucidium.environments.grid_world.components.squares    import *

class Grid():
    """# (Grid World) Grid
    
    Basic grid representation.
    """
    
    def __init__(self,
        # Dimensions.
        rows:               Optional[int] =                                 4,
        columns:            Optional[int] =                                 4,
        
        # Features.
        start:              Optional[Tuple[int, int]] =                     (0, 0),
        goal:               Optional[Set[Tuple[int, int]]] =                None,
        loss:               Optional[Set[Tuple[int, int]]] =                set(),
        walls:              Optional[Set[Tuple[int, int]]] =                set(),
        coins:              Optional[Set[Tuple[int, int]]] =                set(),
        portals:            Optional[List[Dict[str, Tuple[int, int]]]] =    [],
        wrap_map:           Optional[bool] =                                False,
        
        # Rewards/Penalties.
        goal_reward:        Optional[float] =                                1.0,
        step_penalty:       Optional[float] =                               -0.01,
        collision_penalty:  Optional[float] =                               -0.1,
        loss_penalty:       Optional[float] =                               -1.0,
        coin_reward:        Optional[float] =                                0.5,
        **kwargs
    ):
        """# Instantiate (Grid World) Grid.
        
        NOTE: Column indices are in order from left to right, but row indices are in reverse order 
        (from bottom to top).

        ## Dimensions:
            * rows              (int):                              Number of rows with which grid 
                                                                    will be initialized (max = 10). 
                                                                    Defaults to 4.
            * columns           (int):                              Number of columns with which 
                                                                    grid will be initialized (max = 
                                                                    10). Defaults to 4.

        ## Features:
            * coins             (Set[Tuple[int, int]]):             Set of coordinates at which coin 
                                                                    squares will be located within 
                                                                    grid.
            * goal              (Set[Tuple[int, int]]):             Coordinate at which the goal 
                                                                    square will be located in the 
                                                                    grid. Defaults to the top right 
                                                                    corner.
            * loss              (Set[Tuple[int, int]]):             Set of coordinates at which loss 
                                                                    squares will be located within 
                                                                    grid.
            * portals           (List[Dict[str, Tuple[int, int]]]): List of entry -> exit coordinate 
                                                                    mappings at which portal entries 
                                                                    and exits will be located within 
                                                                    grid.
            * start             (Tuple[int, int]):                  Coordinate at which the agent 
                                                                    will begin the game at the start 
                                                                    of each episode. Defaults to 
                                                                    (0, 0) (bottom left corner).
            * walls             (Set[Tuple[int, int]]):             Set of coordinates at which wall 
                                                                    squares will be located within 
                                                                    grid.
            * wrap_map          (bool):                             If true, the agent will not 
                                                                    collide with grid boundaries, 
                                                                    but will instead appear at the 
                                                                    opposite side of the grid.

        ## Rewards/Penalties:
            * coin_reward       (float):                            Reward yielded by collecting 
                                                                    coins. NOTE: Coins are ephemeral 
                                                                    (they can only be collected once 
                                                                    per episode). If coin has 
                                                                    already been collected, the 
                                                                    penalty incurred for re-entering 
                                                                    the square will be the negative 
                                                                    of the reward.
            * collision_penalty (float):                            Penalty incurred for colliding 
                                                                    with wall squares or the grid 
                                                                    boundary (if wrap_map == False).
            * goal_reward       (float):                            Reward yielded by reaching goal 
                                                                    square.
            * loss_penalty      (float):                            Penalty incurred for landing on 
                                                                    loss square(s).
            * step_penalty      (float):                            Penalty incurred for each step 
                                                                    that the agent takes during an 
                                                                    episode.
        """
        # Define dimensions.
        self._columns_:             int =                               columns
        self._rows_:                int =                               rows
        
        # Define features.
        self._coins_:               Set[Tuple[int, int]] =              coins
        self._goal_:                Set[Tuple[int, int]] =              goal if goal is not None else {(self._rows_ - 1, self._columns_ - 1),}
        self._loss_:                Set[Tuple[int, int]] =              loss
        self._portals_:             List[Dict[str, Tuple[int, int]]] =  portals
        self._start_:               Tuple[int, int] =                   start
        self._walls_:               Set[Tuple[int, int]] =              walls
        self._wrap_map_:            bool =                              wrap_map
        
        # Define rewards/penalties.
        self._coin_reward_:         float =                             coin_reward
        self._collisision_penalty_: float =                             collision_penalty
        self._goal_reward_:         float =                             goal_reward
        self._loss_penalty_:        float =                             loss_penalty
        self._step_penalty_:        float =                             step_penalty
        
        # Set agent location to start square.
        self._agent_:               Tuple[int, int] =                   self._start_
        
        # Validate parameters.
        self.__post_init__()
        
        # Populate squares.
        self._populate_()
        
    def __post_init__(self) -> None:
        """# Verify Parameters.
        
        Verify parameters provided upon initialization.
        
        ## Raises:
            AssertionError: If any parameter violates constraints.
        """
        # Assert that no more than 10 rows and columns are specified.
        assert 1 < self.rows    <= 10, f"Row quantity ({self._rows_}) must be 2 - 10"
        assert 1 < self.columns <= 10, f"Column quantity ({self._columns_}) must be 2 - 10"
        
        # Create affidavit of coordinate sets.
        features:       Dict[str, Set[Tuple[int, int]]] =   {
                                                                "start":    {self._start_},
                                                                "goal":     self._goal_,
                                                                "loss":     self._loss_,
                                                                "walls":    self._walls_,
                                                                "coins":    self._coins_,
                                                                "entry":    {portal["entry"]    for portal in self._portals_},
                                                                "exit":     {portal["exit"]     for portal in self._portals_}
                                                            }
        
        # Flatten coordinates into a single set.
        coordinates:    Set[Tuple[int, int]] =              set.union(*features.values())
        
        # For each coordinate...
        for coordinate in coordinates:
            
            # Assert that coordinate is in bounds.
            assert self._is_in_bounds_(coordinate = coordinate), f"Coordinate is out of bounds: {coordinate}"
            
        # Initialize coordinate tracking.
        seen:           Set[Tuple[int, int]] =              set()
        
        # For each feature type and coordinate pair...
        for feature, coordinates in features.items():
            
            # Make intersection.
            intersection:   Set[Tuple[int, int]] =  seen & coordinates
            
            # Assert that there is not intersection with coordinates seen thus far.
            assert not intersection, f"Intersecting coordinates found for {feature} at {intersection}"
            
            # Update set of coordinates seen.
            seen |= coordinates
            
    # PROPERTIES ===================================================================================
    
    @property
    def coin_reward(self) -> float:
        """# Coin Reward

        Reward yielded by collecting a coin.
        """
        return self._coin_reward_
    
    @property
    def coins(self) -> Set[Tuple[int, int]]:
        """# (Grid) Coins.
        
        Set of coordinates at which coin square(s) is/are located.
        """
        return self._coins_.copy()
    
    @property
    def collision_penalty(self) -> float:
        """# Collision Penalty

        Penalty incurred by colliding with walls or boundaries (if map is not wrapped).
        """
        return self._collisision_penalty_
    
    @property
    def columns(self) -> int:
        """# (Grid) Columns

        Quantity of columns in grid.
        """
        return self._columns_
    
    @property
    def done(self) -> bool:
        """# Game is Done?

        True if agent is currently located on a goal or loss square.
        """
        return self._agent_ in self._goal_ or self._agent_ in self._loss_
    
    @property
    def goal(self) -> Set[Tuple[int, int]]:
        """# (Grid) Goal(s).

        Set of coordinates at which goal square(s) is/are located.
        """
        return self._goal_
    
    @property
    def goal_reward(self) -> float:
        """# Goal Reward

        Reward yielded by landing on goal square(s).
        """
        return self._goal_reward_
    
    @property
    def is_wrapped(self) -> bool:
        """# (Grid) is Wrapped?

        If true, the agent will not collide with grid boundaries, but will instead appear at the 
        opposite side of the grid.
        """
        return self._wrap_map_
    
    @property
    def loss(self) -> Set[Tuple[int, int]]:
        """# (Grid) Loss(es)

        Set of coordinates at which loss square(s) is/are located.
        """
        return self._loss_
    
    @property
    def loss_penalty(self) -> float:
        """# Loss Penalty

        Penalty incurred by landing on loss square(s).
        """
        return self._loss_penalty_
    
    @property
    def portals(self) -> List[Dict[str, Tuple[int, int]]]:
        """# (Grid) Portals

        List of mappings for portal entry and destination coordinate(s).
        """
        return self._portals_
    
    @property
    def progress(self) -> Dict[str, Any]:
        """# (Game) Progress

        Progress tracking statistics.
        """
        return  {
                    "squares_visited":      len(self._squares_visited_),
                    "collisions":           self._collisions_,
                    "coins_collected":      self._coins_collected_,
                    "portals_activated":    self._portals_activated_
                }
    
    @property
    def rows(self) -> int:
        """# (Grid) Rows

        Wuantity of rows in grid.
        """
        return self._rows_
    
    @property
    def shape(self) -> Tuple[int, int]:
        """# (Grid) Shape

        Two-dimensional shape of grid.
        """
        return self._rows_, self._columns_
    
    @property
    def step_penalty(self) -> float:
        """# Step Penalty

        Penalty/cost incurred by submitting any action to environment.
        """
        return self._step_penalty_
    
    @property
    def walls(self) -> Set[Tuple[int, int]]:
        """# (Grid) Walls
        
        Set of coordinates at which wall square(s) is/are located.
        """
        return self._walls_
    
    # METHODS ======================================================================================
    
    def move(self,
        action_delta:   Tuple[int, int]
    ) -> Tuple[Tuple[int, int], float, bool, Dict[str, Any]]:
        """# Move (Agent in Grid).

        ## Args:
            * action_delta  (Tuple[int, int]):  Delta of action submitted by agent.

        ## Returns:
            * int:              Agent's new location (index).
            * float:            Reward yielded/penalty incurred by agent's action.
            * bool:             True if new location represents a terminal state.
            * Dict[str, Any]:   Description of interaction event.
        """
        # Compute agent's new location.
        new_location:   Tuple[int, int] =   (
                                                self._agent_[0] + action_delta[0],
                                                self._agent_[1] + action_delta[1]
                                            )
        
        # If new location is out of bounds..
        if not self._is_in_bounds_(coordinate = new_location):
            
            # And map is not wrapped...
            if not self.is_wrapped:
                
                # Increment collision count.
                self._collisions_ += 1
                
                # Assign penalty for boundary collision.
                return  self._coordinate_to_index_(coordinate = self._agent_), self.collision_penalty, False, {"event": "collided with boundary"}
            
            # Otherwise, map is wrapped, so we should module new location.
            new_location: Tuple[int, int] = self._modulate_(coordinate = new_location)
            
        # Uupdate statistics based on new location.
        self._update_statistics_(new_location = new_location)
            
        # Interact with square.
        new_state, value, done, metadata =  self._get_square_(coordinate = new_location).interact()
        
        # Update agent location.
        self._agent_:   Tuple[int, int] =   new_state if new_state is not None else self._agent_
        
        # Provide result of agent's action.
        return self._coordinate_to_index_(coordinate = self._agent_), value, done, metadata
    
    def reset(self) -> int:
        """# Reset (Grid).

        Reset grid to initial state.

        ## Returns:
            * int:  Agent's starting location/state.
        """
        # For each row in grid...
        for row in self._grid_:
            
            # Reset each square in row.
            for square in row: square.reset()
            
        # Reset agent.
        self._agent_:   Tuple[int, int] =   self._start_
        
        # Initialize progress statistics.
        self._squares_visited_:     Set[Tuple[int, int]] =  set()
        self._collisions_:          int =                   0
        self._coins_collected_:     int =                   0
        self._portals_activated_:   int =                   0
        
        # Provide agent's starting location/state.
        return self._coordinate_to_index_(coordinate = self._agent_)
    
    # HELPERS ======================================================================================
    
    def _coordinate_to_index_(self,
        coordinate: Tuple[int, int]
    ) -> int:
        """# (Convert) Coordinate to Index.

        ## Args:
            * coordinate    (Tuple[int, int]):  Coordinate being converted to index.

        ## Returns:
            * int:  Index equivalent of coordinate.
        """
        return coordinate[0] * self.columns + coordinate[1]
    
    def _get_square_(self,
        coordinate: Tuple[int, int]
    ) -> Square:
        """# Get Square.

        ## Args:
            * coordinate    (Tuple[int, int]):  Coordinate of sqaure being fetched.
            
        ## Raises:
            * ValueError:   If square coordinate is out of bounds.

        ## Returns:
            * Square:   Square requested.
        """
        # If coordinate is out of bounds...
        if not self._is_in_bounds_(coordinate = coordinate):
            
            # Report error.
            raise ValueError(f"Square coordinate {coordinate} is out of bounds.")
        
        # Otherwise, provide the sqaure requested.
        return self._grid_[coordinate[0]][coordinate[1]]
    
    def _index_to_coordinate_(self,
        index:  int
    ) -> Tuple[int, int]:
        """# (Convert) Index to Coordinate.

        ## Args:
            * index (int):  Index being converted to coordinate.

        ## Returns:
            * Tuple[int, int]:  Coordinate equivalent of index.
        """
        return index // self.rows, index % self.columns
    
    def _is_in_bounds_(self,
        coordinate: Tuple[int, int]
    ) -> bool:
        """# (Coordinate) is in Bounds?

        ## Args:
            * coordinate    (Tuple[int, int]):  Coordinate being verified.

        ## Returns:
            * bool: True if coordinate is within grid bounds.
        """
        return 0 <= coordinate[0] < self._rows_ and 0 <= coordinate[1] < self._columns_
    
    def _modulate_(self,
        coordinate: Tuple[int, int]
    ) -> Tuple[int, int]:
        """# Module (Coordinate).

        ## Args:
            * coordinate    (Tuple[int, int]):  Coordinate being modulated.

        ## Returns:
            * Tuple[int, int]:  Modulated coordinate.
        """
        return coordinate[0] % self.rows, coordinate[1] % self.columns
    
    def _populate_(self) -> None:
        """# Populate (Grid).
        
        Populate grtid with squares of types specified by feature parameters.
        """
        # Instantiate grid of empty squares.
        self._grid_:    List[List[Square]] =    [
                                                    [
                                                        Square(coordinate = (r, c), value = self.step_penalty)
                                                        for c in range(self.columns)
                                                    ]   for r in range(self.rows)
                                                ]
        
        # Populate features.
        for r, c in self.coins: self._grid_[r][c] = Coin(coordinate = (r, c), value = self.coin_reward)
        for r, c in self.goal:  self._grid_[r][c] = Goal(coordinate = (r, c), value = self.goal_reward)
        for r, c in self.loss:  self._grid_[r][c] = Loss(coordinate = (r, c), value = self.loss_penalty)
        for r, c in self.walls: self._grid_[r][c] = Wall(coordinate = (r, c), value = self.collision_penalty)
        
        # For each portal...
        for portal in self.portals:
            
            # Populate portals.
            self._grid_[portal["entry"][0]][portal["entry"][1]] =   Portal(
                                                                        coordinate =    portal["entry"],
                                                                        destination =   portal["exit"],
                                                                        value =         self.step_penalty
                                                                    )
            
    def _update_statistics_(self,
        new_location:   Tuple[int, int]
    ) -> None:
        """# Update Statistics.
        
        Add new locatino to squares visited and compute progress trackers.

        ## Args:
            * new_location  (Tuple[int, int]):  Agent's new location.
        """
        # If new location has not already been visited...
        if new_location not in self._squares_visited_:
            
            # Add new location.
            self._squares_visited_.add(new_location)
            
            # If new location was a coin square, increment count of collected coins.
            if new_location in self._coins_:                                    self._coins_collected_ += 1
            
        # If new location was a wall, increment collision count.
        if new_location in self._walls_:                                    self._collisions_ += 1
        
        # If new location was a portal entrance, increment portal activation count.
        if new_location in [portal["entry"] for portal in self._portals_]:  self._portals_activated_ += 1
            
    # DUNDERS ======================================================================================
    
    def __repr__(self) -> str:
        """# (Grid) Object Representation"""
        return f"<Grid(rows = {self.rows}, columns = {self.columns}, start = {self.start}, goal = {self.goal})>"
    
    def __str__(self) -> str:
        """# (Grid) String Representation"""
        # Predefine border and index strings.
        column_index:   str =   (" " * 4) + " ".join(f" {column} " for column in range(self.columns))
        top_border:     str =   "\n   ┌" + ((("─" * 3) + "┬") * (self.columns - 1)) + ("─" * 3) + "┐"
        middle_line:    str =   "\n   ├" + ((("─" * 3) + "┼") * (self.columns - 1)) + ("─" * 3) + "┤"
        bottom_border:  str =   "\n   └" + ((("─" * 3) + "┴") * (self.columns - 1)) + ("─" * 3) + "┘"
        
        # Initialize grid string to which rendering will be appended.
        grid_string:    str =   column_index + top_border
        
        # For each row in grid...
        for r, row in enumerate(self._grid_):
            
            # Start new row with index.
            grid_string     += f"\n {r} │"
            
            # For each square in row...
            for c, square in enumerate(row):
                
                # Append square or agent symbol.
                grid_string += f""" {colored("A", color= "blue") if self._agent_ == (r, c) else square} │"""
                
            # Append row separator or bottom border.
            grid_string     += middle_line if r != self.rows - 1 else bottom_border
                                        
        # Return grid representation.
        return grid_string