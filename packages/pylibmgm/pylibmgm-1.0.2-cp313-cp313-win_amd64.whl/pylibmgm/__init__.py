"""""" # start delvewheel patch
def _delvewheel_patch_1_11_1():
    import os
    if os.path.isdir(libs_dir := os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'pylibmgm.libs'))):
        os.add_dll_directory(libs_dir)


_delvewheel_patch_1_11_1()
del _delvewheel_patch_1_11_1
# end delvewheel patch

from ._pylibmgm import *
from . import solver, io, _pylibmgm
import logging

_LOGGER = logging.getLogger("libmgm")
_LOGGER.setLevel(logging.INFO)

_pylibmgm._register_api_logger(_LOGGER)
io._register_io_logger(_LOGGER)

# hide background module und functions from help() and documentation tools.
del _pylibmgm 
del io._register_io_logger
