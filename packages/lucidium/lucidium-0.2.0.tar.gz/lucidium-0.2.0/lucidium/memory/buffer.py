"""# lucidium.memory.buffer

Defines structure and functionality of experience/memory buffer.
"""

__all__ = ["ExperienceBuffer"]

from collections                import deque
from random                     import sample
from typing                     import Dict, List

from lucidium.memory.experience import Experience

class ExperienceBuffer():
    """# Experience Buffer.
    
    Circular buffer for storing and retrieving experiences for learning and discovery.
    
    Provides efficient storage and retrieval methods for experience-based learning and pattern 
    mining operations.
    """
    
    def __init__(self,
        capacity:   int =   10000
    ):
        """# Instantiate Experience Buffer.

        ## Args:
            * capacity  (int, optional):    Maximum experience capacity. Defaults to 10000.
        """
        # Define capacity.
        self._capacity_:        int =                   capacity
        
        # Initialize buffer.
        self._buffer_:          deque =                 deque(maxlen = self._capacity_)
        
    # METHODS ======================================================================================
    
    def add(self,
        experience: Experience
    ) -> None:
        """# Add Experience.

        ## Args:
            * experience    (Experience):   Experience data being added.
        """
        # Add experience to buffer.
        self._buffer_.append(experience)
        
    def clear(self) -> None:
        """# Clear Buffer."""
        self._buffer_.clear()
        
    def get_random_batch(self,
        batch_size: int
    ) -> List[Experience]:
        """# Get Random Batch of Experiences.

        ## Args:
            * batch_size    (int):  Number of experiences to fetch.

        ## Returns:
            * List[Experience]: Batch of random experiences.
        """
        return sample(list(self._buffer_), min(batch_size, len(self._buffer_)))
        
    def get_recent(self,
        n:  int
    ) -> List[Experience]:
        """# Get Recent Experiences.

        ## Args:
            * n (int):  Number of recent experiences to fetch.

        ## Returns:
            * List[Experience]: Recent experiences.
        """
        return list(self._buffer_)[-min[n, len(self._buffer_)]]