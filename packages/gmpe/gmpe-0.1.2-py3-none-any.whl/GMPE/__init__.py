import logging
from .gmpe import BCHydro, Boore, ChioYoungs, Campbell
from .additional import approx
logging.getLogger('GMPE').addHandler(logging.NullHandler())


