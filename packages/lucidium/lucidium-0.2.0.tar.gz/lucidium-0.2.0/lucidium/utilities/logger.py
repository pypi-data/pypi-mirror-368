"""# lucidium.utilities.logger

Logging utilities.
"""

__all__ = ["get_child", "get_logger"]

from logging                import getLogger, Formatter, Logger, StreamHandler
from logging.handlers       import RotatingFileHandler
from os                     import makedirs
from sys                    import stdout

# Declare logger object.
LOGGER:         Logger

def get_logger(
    logger_name:    str,
    logging_level:  str =   "INFO",
    logging_path:   str =   "logs"
) -> Logger:
    """# Initialize Logger.
    
    Initialize a logger object with configuration provided.

    ## Args:
        * logger_name   (str):              Name attributed to logger object. This should usually 
                                            be the module identifier.
        * logging_level (str, optional):    Minimum logging level (DEBUG < INFO < WARNING < ERROR < 
                                            CRITICAL). Defaults to "INFO".
        * logging_path  (str, optional):    Path at which logs will be written. Defaults to "logs".

    ## Returns:
        * Logger:   Logger object, initialized with provided parameters.
    """
    # Ensure that logging path exists
    makedirs(name = logging_path, exist_ok = True)
    
    # Declare globals.
    global LOGGER

    # Initialize logger
    LOGGER =                                getLogger(
                                                name =          logger_name
                                            )

    # Set logging level
    LOGGER.setLevel(level = logging_level)

    # Define console handler
    stdout_handler: StreamHandler =         StreamHandler(
                                                stream =        stdout
                                            )

    # Define file handler
    file_handler:   RotatingFileHandler =   RotatingFileHandler(
                                                filename =      f"{logging_path}/{logger_name}.log",
                                                maxBytes =      1048576,
                                                backupCount =   10
                                            )
    
    # Define format for console handler.
    stdout_handler.setFormatter(Formatter("%(levelname)s | %(name)s | %(message)s"))
    
    # Define format fror file handler.
    file_handler.setFormatter(Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s"))
    
    # Add handlers to logger.
    LOGGER.addHandler(hdlr = stdout_handler)
    LOGGER.addHandler(hdlr = file_handler)
    
    # Return logger object.
    return LOGGER
    
def get_child(
    logger_name:    str
) -> Logger:
    """# Initialize Child Logger.
    
    Declares a logger child descendent of root logger.

    ## Args:
        * logger_name   (str):  Name attributed to child logger.

    ## Returns:
        * Logger:   Child logger.
    """
    # Declare globals.
    global LOGGER
    
    # Simply return child logger.
    return LOGGER.getChild(logger_name)