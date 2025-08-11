import logging
from .gmpe import BCHydro, Boore, ChiouYoungs, Campbell
from .additional import approx
logging.getLogger('GMPE').addHandler(logging.NullHandler())


