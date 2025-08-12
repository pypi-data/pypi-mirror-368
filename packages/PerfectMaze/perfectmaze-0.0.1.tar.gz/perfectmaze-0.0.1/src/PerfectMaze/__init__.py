from importlib.metadata import version

_package_name = "PerfectMaze"
__version__   = version(_package_name)
__author__    = "星灿长风v(StarWindv)"


from .HilbertMaze import HilbertMaze
from .utils import is_perfect_maze