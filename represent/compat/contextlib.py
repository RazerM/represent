"""contextlib functionality from Python 3"""
from __future__ import absolute_import

try:
    from contextlib import suppress
except ImportError:
    class suppress(object):
        """Context manager to suppress specified exceptions

        After the exception is suppressed, execution proceeds with the next
        statement following the with statement.

             with suppress(FileNotFoundError):
                 os.remove(somefile)
             # Execution still resumes here if the file was already removed
        """

        def __init__(self, *exceptions):
            self._exceptions = exceptions

        def __enter__(self):
            pass

        def __exit__(self, exctype, excinst, exctb):
            # Unlike isinstance and issubclass, CPython exception handling
            # currently only looks at the concrete type hierarchy (ignoring
            # the instance and subclass checking hooks). While Guido considers
            # that a bug rather than a feature, it's a fairly hard one to fix
            # due to various internal implementation details. suppress provides
            # the simpler issubclass based semantics, rather than trying to
            # exactly reproduce the limitations of the CPython interpreter.
            #
            # See http://bugs.python.org/issue12029 for more details
            return exctype is not None and issubclass(exctype, self._exceptions)
