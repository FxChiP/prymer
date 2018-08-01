
__all__ = [
    "FromAttr",
    "KeyOrDefault",
    "OnlyIfExists",
    "Template",
    "SkipIteration"
]


class SkipIteration(Exception):
    """
    Like StopIteration, but instead just skips
    the current iterated item -- used to prevent
    list items or key/value pairs from being added
    to the final product if a condition is not
    met

    If an exception caused it, store the exception
    using the constructor so that it can reraise
    for operations (e.g. Get) that shouldn't
    typically get much use out of SkipIteration
    """
    def __init__(self, e=None):
        self._e = e

    def reraise(self):
        if self._e:
            e = self._e
            while e and isinstance(e, SkipIteration):
                # race to the bottom
                e = e._e
            if e:
                raise e
            else:
                raise TypeError("SkipIteration without cause told to reraise")
        else:
            raise TypeError("SkipIteration without cause told to reraise")


def Composite(func):
    # Take the parameters
    def param_collections(*args, **kwargs):
        # Take the data to apply to
        def source_data(source):
            # Call the composite with the source
            # data and the parameters
            return func(source, *args, **kwargs)
        return source_data
    return param_collections


@Composite
def FromAttr(source, attr_name, *default):
    return getattr(source, attr_name, *default)


@Composite
def KeyOrDefault(source, key_name, *default):
    try:
        return source[key_name]
    except (KeyError, IndexError) as e:
        if not default:
            raise
        else:
            return default[0]


@Composite
def Template(source, template, resolver=None):
    if callable(resolver):
        source = resolver(source)
    if isinstance(source, dict):
        return template.format(**source)
    else:
        return template.format(*source)


@Composite
def OnlyIfExists(source, key):
    try:
        if callable(key):
            r = key(source)
        else:
            # Assume it's a dict key against source itself
            # If it's an attr, FromAttr should be used and
            # it will be callable. If it's nested,
            # Get should be used and it will be callable,
            # etc.
            r = source[key]
        return r
    except (KeyError, AttributeError, IndexError,
            ValueError, TypeError, SkipIteration) as e:
        raise SkipIteration(e)
