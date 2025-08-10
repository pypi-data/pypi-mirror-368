## Copyright (c) 2019 - 2025 Geode-solutions

import os, pathlib
os.add_dll_directory(pathlib.Path(__file__).parent.resolve().joinpath('bin'))

from .core_numerics import *
from .frame_field import *
from .surface_numerics import *
from .scalar_function import *
