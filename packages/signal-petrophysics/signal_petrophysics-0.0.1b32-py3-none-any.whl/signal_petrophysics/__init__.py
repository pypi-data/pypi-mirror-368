# src/signal_petrophysics/__init__.py

"""Signal Petrophysics package for well log analysis."""

# Import submodules as objects
from . import load_data
from . import pattern_find
from . import plot
from . import signal_adapt
from . import utils
from . import postprocessing  # Add this line

# Import all functions directly for convenience
from .load_data import *
from .pattern_find import *
from .plot import *
from .signal_adapt import *
from .utils import *
from .postprocessing import *  # Add this line

__version__ = "0.1.0"
