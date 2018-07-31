
__all__ = ["FromAttr", "KeyOrDefault", "Template"]


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
