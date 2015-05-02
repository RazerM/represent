from __future__ import absolute_import, print_function

from .core import *
from .utilities import deprecated as _deprecated

__all__ = core.__all__

__author__ = 'Frazer McLean <frazer@frazermclean.co.uk>'
__version__ = '1.2.0'
__license__ = 'MIT'
__description__ = 'Create __repr__ automatically or declaratively.'


RepresentationMixin = _deprecated(
    ReprMixin,
    __name__,
    'RepresentationMixin has been renamed to ReprMixin.',
    DeprecationWarning
)

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
