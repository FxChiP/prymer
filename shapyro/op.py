
import functools

__all__ = [
    "FromAttr",
    "KeyOrDefault",
    "OnlyIfExists",
    "StringTemplate",
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
    """
    Composite

    A decorator that takes a callable with signature:

    callable(source, ...)

    And returns a function composite_func with signature

    composite_func(...)

    The composite_func captures the subsequent parameters
    for callable (like a partial, but for the tail
    rather than the head) and returns a function source_data
    with signature:
    
    source_data(source)

    This function will apply the parameters given to
    composite_func() as trailing arguments to the original
    callable, with source taking its position as first
    parameter.

    This makes it so you can just write a function
    that takes source and parameters all in one place
    and this decorator will make it work in the way that
    shapyro.Get[] expects.

    Note well that this also means calling those functions
    will return a *function* rather than the result; that
    *function* is what is called on the input data to get
    the actual final result.

    For documented @shapyro.Composite functions, an *ultimate*
    return will be documented instead of the direct return,
    which will always be a function that takes one parameter:
    the value to operate on.
    """
    # Take the parameters
    def composite_func(*args, **kwargs):
        # Take the data to apply to
        @functools.wraps(func)
        def source_data(source):
            # Call the composite with the source
            # data and the parameters
            return func(source, *args, **kwargs)
        return source_data
    return composite_func


@Composite
def FromAttr(source, attr_name, *default):
    """
    FromAttr

    Parameters:
        source: object: The object to get an attr from.
        attr_name: str: the attribute to return
        default: object: the default value of the attr
    
    FromAttr is a proxy call to getattr() . The reason
    it's necessary is because a getattr on shapyro.Get
    will end up getting a function that is supposed to
    be called on some input data to get that attribute
    (i.e. shapyro.Get will *defer* that getattr until
    the call of the returned function).

    The intended usage is:

    get_hello = shapyro.Get[shapyro.FromAttr("hello","world")]
    get_hello(dict)  # world (because of the default)

    But you can also just do:
    
    get_hello = shapyro.FromAttr("hello","world")
    get_hello(dict)  # world (because of the default)
    
    Ultimate return:
        object: The value of obj.attr_name if any.
    
    Might raise:
        AttributeError if no value or default.
    """
    return getattr(source, attr_name, *default)


@Composite
def KeyOrDefault(source, key_name, *default):
    """
    KeyOrDefault

    Parameters:
        source: object: The object to get an attr from.
        key_name: key: the key/index to return
        default: object: the default value of the attr
    
    KeyOrDefault is *very similar* to dict.get except that
    it functions on arrays too; it's more like accessing a
    sequence/map using brackets that also allows for a default.

    Like FromAttr, it's necessary because doing shapyro.Get.get
    will defer getting the `get` attribute until the resulting
    function is called on the input data. 

    The intended usage is:

    get_2 = shapyro.Get[KeyOrDefault(2,"not found")]
    get_2([0,1,5])                               # 5
    get_2({"hello": "world"})                    # "not found"
    get_2({"hello": "world", 2: "here I am"})    # "here I am"
    get_2({"hello": "world", "2": "nope"})       # "not found"

    But you can also just do:
    
    get_2 = shapyro.KeyOrDefault(2,"not found")
    get_2([0,1,5])                               # 5
    get_2({"hello": "world"})                    # "not found"
    get_2({"hello": "world", 2: "here I am"})    # "here I am"
    get_2({"hello": "world", "2": "nope"})       # "not found"

    Ultimate return:
        object: input_data[key_name] or default if specified

    Might raise:
        If no default: KeyError for dicts, IndexError for sequences
        (if you're not using a default, you should use shapyro.Get[])
    """
    try:
        return source[key_name]
    except (KeyError, IndexError) as e:
        if not default:
            raise
        else:
            return default[0]


@Composite
def StringTemplate(source, template, resolver=None):
    """
    StringTemplate

    Parameters:
        source: dict/list/tuple: A container of values to be interpolated in the string
        template: str: A string template to be filled with values from source
        resolver: Callable[obj => list/dict]: resolver(source) -- convert source to .format'able data type
    
    StringTemplate is a deferred call to template.format(*source) or template.format(**source)
    depending on whether source is a sequence type or a dict. If resolver is provided,
    it will be called on source and its *result* will go into template.format with
    the same rules (for instance if you want to convert a full object to a dict).

    You *can* use it in shapyro.Get[] like shapyro.Get[shapyro.StringTemplate(...)]
    but it's probably more readable on its own.

    Example:

    a = shapyro.StringTemplate("Hello, {name}")
    a({"name": "world"})  # "Hello, world"

    Ultimate return:
        str: template.format(*source/**source)
    
    Might raise:
        KeyError/IndexError/any other error str.format may raise
    """
    if callable(resolver):
        source = resolver(source)
    if isinstance(source, dict):
        return template.format(**source)
    else:
        return template.format(*source)


@Composite
def OnlyIfExists(source, key):
    """
    OnlyIfExists

    Parameters:
        source: object: The input data to check
        key: callable, dict key, or index: what to check for

    OnlyIfExists is a really special case primarily for
    usage with shapyro.utils.port() and friends. The intent
    is to allow for skipping indexes or k/v *pairs* in dicts
    when the source element does not exist. e.g.:

    tpl = {"my_name": shapyro.Get["name"], "my_attrs": shapyro.OnlyIfExists("attrs")}
    src1 = {"name": "Fx"}
    src2 = {"name": "Andy", "attrs": {"the_best": "true"}}
    shapyro.port(src1, tpl)    # {'my_name': 'Fx'}
    shapyro.port(src2, tpl)    # {'my_name': 'Andy', 'my_attrs': {'the_best': 'true'}}

    By default, it expects the input data to be a dict. You can implement
    this check against an object's attribute instead by invoking it like:

    shapyro.OnlyIfExists(shapyro.FromAttr("name"))

    Example of this usage:

    from collections import namedtuple
    nr = namedtuple("NameRecord", ["name", "index", "other_index"])
    tpl = {"my_name": shapyro.OnlyIfExists(shapyro.FromAttr("name")), "my_2": shapyro.Get[2]}
    src = (0, 1, "beep")
    src2 = nr("Fx", 0, 5)
    shapyro.port(src, tpl)    # {'my_2': 'beep'}
    shapyro.port(src2, tpl)   # {'my_name': 'Fx', 'my_2': 5}

    Ultimate return:
        source[key] if key is not callable
        key(source) if key is callable (allowing shapyro.Get usage)
    
    Might raise:
        SkipIteration on KeyError, AttributeError, IndexError, ValueError, TypeError, or SkipIteration
        (whichever was the original cause will be nested in SkipIteration)
    """
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
