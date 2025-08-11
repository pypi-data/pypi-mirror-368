import pkg_resources

DATA_PATH = pkg_resources.resource_filename("lhcb_rex", "")

from .inference.runner import run_from_tuple
from .inference.runner import run

__all__ = [
    "run",
    "run_from_tuple",
]  # controls what is imported if someone were to from <module> import *
