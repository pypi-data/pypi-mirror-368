"""# lucidium.utilities.timestamp

Define global timestamp.
"""

__all__ = ["TIMESTAMP"]

from datetime   import datetime

TIMESTAMP:  str =   datetime.now().strftime(format = "%Y%m%d_%H%M%S")