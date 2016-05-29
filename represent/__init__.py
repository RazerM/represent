from __future__ import absolute_import, print_function

from .core import *
from .deprecated import *
from .helper import *
from .utilities import deprecated as _deprecated

__all__ = core.__all__ + helper.__all__

__author__ = 'Frazer McLean <frazer@frazermclean.co.uk>'
__version__ = '1.5.1'
__license__ = 'MIT'
__description__ = 'Create __repr__ automatically or declaratively.'


RepresentationHelper = _deprecated(
    ReprHelper,
    __name__,
    'RepresentationHelper has been renamed to ReprHelper.',
    DeprecationWarning
)

PrettyRepresentationHelper = _deprecated(
    PrettyReprHelper,
    __name__,
    'PrettyRepresentationHelper has been renamed to PrettyReprHelper.',
    DeprecationWarning
)
