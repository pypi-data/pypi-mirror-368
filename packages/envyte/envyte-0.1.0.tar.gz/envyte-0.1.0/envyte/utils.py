from os import getenv




def get(key, default = None):
    """
    Get environment variable.

    Args:
        key (str): The environment variable key.
        default (Any, optional): The default value if the key is not found. Defaults to None.
    """
    
    return getenv(key, default)



def getBool(key, default = False):
    """
    Get environment variable as boolean.

    Args:
        key (str): The environment variable key.
        default (bool, optional): The default value if the key is not found. Defaults to False.
    """
    
    value = getenv(key, str(default)).lower()

    return value in ["1", "true", "yes", "y", "on"]



def getInt(key, default = 0):
    """
    Get environment variable as integer.

    Args:
        key (str): The environment variable key.
        default (int, optional): The default value if the key is not found. Defaults to 0.
    """
    
    try:
        return int(getenv(key, default))
    except (ValueError, TypeError):
        return default



def getString(key, default = ""):
    """
    Get environment variable as string.

    Args:
        key (str): The environment variable key.
        default (str, optional): The default value if the key is not found. Defaults to "".
    """

    return str(getenv(key, default))