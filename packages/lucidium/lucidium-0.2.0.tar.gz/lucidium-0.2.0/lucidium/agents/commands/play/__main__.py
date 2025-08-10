"""# lucidium.agents.commands.play

Agent's game-play process.
"""

__all__ = ["Game"]

from dashing                                import HSplit, Log, Text, VSplit
from json                                   import dump, dumps
from math                                   import inf
from os                                     import makedirs
from time                                   import sleep
from typing                                 import Any, Dict

from lucidium.agents                        import Agent
from lucidium.agents.commands.play.__args__ import register_play_parser
from lucidium.environments                  import Environment
from lucidium.registries                    import AGENT_REGISTRY, ENVIRONMENT_REGISTRY, register_agent_command
from lucidium.utilities                     import TIMESTAMP

class Game():
    """# Game (Process)
    
    Process execution for agent game-play.
    """
    
    def __init__(self,
        agent:          str,
        environment:    str,
        episodes:       int =   100,
        max_steps:      int =   100,
        animate:        bool =  False,
        animation_rate: float = 0.1,
        save_results:   bool =  False,
        save_path:      str =   "output/games",
        **kwargs
    ):
        """# Instantiate Game Process.

        ## Args:
            * agent             (str):      Agent interacting with environment.
            * environment       (str):      Environment with which agent will interact.
            * episodes          (int):      Episodes for which agent will interact with environment. 
                                            Defaults to 100.
            * max_steps         (int):      Maximum number of steps agent is allowed to interact 
                                            with environment in each episode. Defaults to 100.
            * animate           (bool):     Animate interaction. Defaults to False.
            * animation_rate    (float):    Rate at which animation will be refresed in seconds. 
                                            Defaults to 0.1.
            * save_results      (bool):     If true, results will be saved to JSON file.
            * save_path         (str):      Path at which game results will be saved. NOTE: Only 
                                            applies if `--save-results` or `--save` flags are 
                                            passed. Defaults to "./output/games/"
        """
        # Load environment.
        self._environment_:     Environment =   ENVIRONMENT_REGISTRY.load(
                                                    name = environment,
                                                    **kwargs
                                                )
        
        # Load 
        self._agent_:           Agent =         AGENT_REGISTRY.load(
                                                    name =              agent,
                                                    action_space =      self._environment_.action_space,
                                                    observation_space = self._environment_.observation_space,
                                                    **kwargs
                                                )
        
        # Define game play parameters.
        self._episodes_:        int =           episodes
        self._max_steps_:       int =           max_steps
        
        # Define animation parameters.
        self._is_animated_:     bool =          animate
        self._animation_rate_:  float =         animation_rate
        
        # If animation is enabled, initialize display.
        if self._is_animated_:  self._initialize_display_()
        
        # Set flag to save results.
        self._save_results_:    bool =          save_results
        self._save_path_:       str =           save_path
        
    # METHODS ======================================================================================
    
    def execute(self) -> Dict[str, Any]:
        """# Execute Game.

        ## Returns:
            * Dict[str, Any]:   Game statistics.
        """
        # Initialize game statistics.
        self._game_statistics_: Dict[str, Any] =    {
                                                        "episodes":     {},
                                                        "best_episode": {
                                                                            "reward":   -inf,
                                                                            "episode":  0
                                                                        }
                                                    }
        
        # For each episode prescribed...
        for self._current_episode_ in range(1, self._episodes_ + 1):
            
            # Execute episode.
            self._game_statistics_["episodes"].update({self._current_episode_: self._execute_episode()})
            
            # If this episode yielded a record reward...
            if self._game_statistics_["episodes"][self._current_episode_]["cumulative_reward"] > self._game_statistics_["best_episode"]["reward"]:
                
                # Update best episode statistics.
                self._game_statistics_["best_episode"]["reward"] =  self._game_statistics_["episodes"][self._current_episode_]["cumulative_reward"]
                self._game_statistics_["best_episode"]["episode"] = self._current_episode_
                
        # Save results if requested.
        if self._save_results_:
            
            # Ensure that directories exist.
            makedirs(name = self._save_path_, exist_ok = True)
            
            # Save results.
            dump(
                self._game_statistics_,
                open(
                    f"{self._save_path_}/{self._agent_.name}_{self._environment_.name}_{TIMESTAMP}.json",
                    "w", encoding = "utf-8"
                ),
                indent =    2,
                default =   str
            )
                
        # Provide final game statistics.
        return self._game_statistics_
        
    # HELPERS ======================================================================================
    
    def _append_event_(self) -> None:
        """# Append Event."""
        self._logging_panel_.append(msg = self._step_statistics_["metadata"]["event"])
        
    def _execute_episode(self) -> Dict[str, Any]:
        """# Execute Episode.

        ## Returns:
            * Dict[str, Any]:   Episode statistics.
        """
        # Reset environment.
        self._current_state_:   Any =   self._environment_.reset()
        
        # Initialize episode statistics.
        self._episode_statistics_:  Dict[str, Any] =    {
                                                            "steps":                {},
                                                            "cumulative_reward":    0.0,
                                                            "steps_taken":          0,
                                                            "completed":            False
                                                        }
        
        # For each allowed step...
        for self._current_step_ in range(1, self._max_steps_ + 1):
            
            # Execute step.
            self._episode_statistics_["steps"].update({self._current_step_: self._execute_step_()})
            
            # Update cumulative reward.
            self._episode_statistics_["cumulative_reward"] += self._episode_statistics_["steps"][self._current_step_]["reward"]
            
            # Increment step count.
            self._episode_statistics_["steps_taken"] += 1
            
            # If environment has reached a terminal state...
            if self._episode_statistics_["steps"][self._current_step_]["done"]:
                
                # Record that game was completed.
                self._episode_statistics_["completed"] = True
                
                # Conclude episode.
                break
        
        # Provide final episode statistics.
        return self._episode_statistics_
        
    def _execute_step_(self) -> Dict[str, Any]:
        """# Execute Step.

        ## Returns:
            * Dict[str, Any]:   Step statistics.
        """
        # Prompt agent to choose action.
        action:                 Any =               self._agent_.act(self._current_state_)
        
        # Submit agent's action to environment.
        new_state, reward, done, metadata = self._environment_.step(action = action)
        
        # Prompt agent to observe the result of its action.
        self._agent_.observe(new_state = new_state, reward = reward, done = done)
        
        # Define step statistics.
        self._step_statistics_: Dict[str, Any] =    {
                                                        "old_state":    self._current_state_,
                                                        "action":       action,
                                                        "new_state":    new_state,
                                                        "reward":       reward,
                                                        "done":         done,
                                                        "metadata":     metadata
                                                    }
        
        # Update current state.
        self._current_state_:   Any =               new_state
        
        # If game-play is animated, update display.
        if self._is_animated_: self._update_display_()
        
        # Provide step result.
        return self._step_statistics_
    
    def _initialize_display_(self) -> None:
        """# Initialize (Animation) Layout."""
        # Instantiate UI layout.
        self._ui_:  VSplit =    VSplit(HSplit(
                                    # Environment state panel.
                                    Text("",            title = "State",        border_color = 7, color = 7),
                                    
                                    # Statistics panel.
                                    VSplit(
                                        
                                        # Game play statistics.
                                        HSplit(
                                            
                                            # Episode statistics.
                                            Text("",    title = "Episode",      border_color = 7, color = 7),
                                            
                                            # Step statistics.
                                            Text("",    title = "Step",         border_color = 7, color = 7)
                                        ),
                                        
                                        # Agent/Environment statistics.
                                        HSplit(
                                            
                                            # Environment statistics.
                                            Text("",    title = "Environment",  border_color = 7, color = 7),
                                            
                                            # Agent statistics.
                                            Text("",    title = "Agent",        border_color = 7, color = 7)
                                        ),
                                        # Set parameters for statistics panel.
                                        title = "Statistics", border_color = 7, color = 7
                                    ),
                                    
                                    # Logging panel.
                                    Log(                title = "Events",       border_color = 7, color = 7),
                                    
                                    # Set parameters for display.
                                    title = f"{self._agent_.name} playing {self._environment_.name}", border_color = 7, color = 7
                                ))
        
        # Extract components for updates.
        self._environment_state_panel_:         Text =      self._ui_.items[0].items[0]
        self._episode_statistics_panel_:        Text =      self._ui_.items[0].items[1].items[0].items[0]
        self._step_statistics_panel_:           Text =      self._ui_.items[0].items[1].items[0].items[1]
        self._environment_statistics_panel_:    Text =      self._ui_.items[0].items[1].items[1].items[0]
        self._agent_statistics_panel_:          Text =      self._ui_.items[0].items[1].items[1].items[1]
        self._logging_panel_:                   Log =       self._ui_.items[0].items[2]
    
    def _update_agent_statistics_panel_(self) -> None:
        """# Update Agent Statistics Panel."""
        self._agent_statistics_panel_.text = dumps(self._agent_.statistics, indent = 2, default = str)
        
    def _update_display_(self) -> None:
        """# Update (Animation) Display."""
        # Update panels.
        self._append_event_()
        self._update_agent_statistics_panel_()
        self._update_environment_state_panel_()
        self._update_environment_statistics_panel_()
        self._update_episode_statistics_panel_()
        self._update_step_statistics_panel_()
        
        # Render display.
        self._ui_.display()
        
        # Simulate refersh rate.
        sleep(self._animation_rate_)
    
    def _update_environment_state_panel_(self) -> None:
        """# Update Environment State Panel."""
        self._environment_state_panel_.text = str(self._environment_)
        
    def _update_environment_statistics_panel_(self) -> None:
        """# Update Environment Statistics Panel."""
        self._environment_statistics_panel_.text = dumps(self._environment_.statistics, indent = 2, default = str)
        
    def _update_episode_statistics_panel_(self) -> None:
        """# Update Episode Statistics Panel."""
        # Update episode count.
        self._episode_statistics_panel_.title = f"Episode {self._current_episode_}/{self._episodes_}"
        
        # Update episode statistics.
        self._episode_statistics_panel_.text =  dumps({k:v for k,v in self._episode_statistics_.items() if k != "steps"}, indent = 2, default = str)
        
    def _update_step_statistics_panel_(self) -> None:
        """# Update Step Statistics Panel."""
        # Update step count.
        self._step_statistics_panel_.title =    f"Step {self._current_step_}/{self._max_steps_}"
        
        # Update step statistics.
        self._step_statistics_panel_.text =     dumps(self._step_statistics_, indent = 2, default = str)
        
        
# Define main process driver.
@register_agent_command(
    name =      "play",
    parser =    register_play_parser
)
def main(**kwargs) -> Dict[str, Any]:
    """# Execute Game.

    ## Returns:
        * Dict[str, Any]:   Game statistics.
    """
    # Execute game.
    return Game(**kwargs).execute()