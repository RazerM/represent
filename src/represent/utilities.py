from collections import namedtuple


def inherit_docstrings(cls):
    """Add docstrings from superclass if missing.

    Adapted from this StackOverflow answer by Raymond Hettinger:
    http://stackoverflow.com/a/8101598/2093785
    """
    for name, func in vars(cls).items():
        if not func.__doc__:
            for parent in cls.__bases__:
                parfunc = getattr(parent, name, None)
                if parfunc and getattr(parfunc, "__doc__", None):
                    func.__doc__ = parfunc.__doc__
                    break
    return cls


Parantheses = namedtuple("Parantheses", "left, right")
ReprInfo = namedtuple("ReprInfo", "fstr, args, kw")
