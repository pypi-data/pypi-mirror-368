from .core import autoLoadEnvironmentVariables
from .utils import get, getBool, getInt, getString





# Load env immediately on import
autoLoadEnvironmentVariables()

__all__ = ["get", "getBool", "getInt", "getString", "autoLoadEnvironmentVariables"]
