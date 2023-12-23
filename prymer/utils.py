
import asyncio
from prymer.op import Composite, SkipIteration

@Composite
def Template(src, template):
    """
    Template

    "Class-like" style for prymer.utils.port

    e.g. 

    x = prymer.Template({"a": prymer.Get['name']})
    x({"name": "Fx"})   # {"a": "Fx"}
    """
    return port(src, template)


def port(src, dst):
    """
    port
    
    Parameters:
        src: The source data object
        dst: The "destination" object (more like a template)
    
    port is one of the biggest core features of prymer.
    The whole purpose of it is to take a source/input 
    data object, such as:

    src = {
        "user": {
            "id": 0,
            "name": "test",
            "group": "Admin"
        },
        "post": {
            "title": "test title",
            "content": "lorem ipsum..."
        }
    }

    And convert it using a dst object, like:

    dst = {
        "author": prymer.Get['user']['name'],
        "title": prymer.Get['post']['title'],
        "content": prymer.Get['post']['content']
    }

    Such that the result of `prymer.port(src, dst)` is:

    {
        "author": "test",
        "title": "test title",
        "content": "lorem ipsum..."
    }

    All of the keys and values in the dst object
    run through port, which eventually delegates them
    down to port_ident -- which will either return
    the value if it isn't a callable or, if it is,
    will return the value of the result of calling the
    callable with src as a sole argument. This way,
    you can define your desired output object and all
    of the accesses you would need to make on an input
    object to build it at the same time, like a template.

    This will also work with async -- if a callable
    happens to return a coroutine object (i.e. if the
    callable was defined with `async def`), the result
    of the entire operation will also be a coroutine,
    and you just have to `await` it to get your result as 
    an extra step.

    Potential gotcha: if a callable in a seq item or a dict
    raises prymer.SkipIteration, that entire list item or key/value
    pair will be skipped. This is a deliberate side effect
    that allows prymer.OnlyIfExists to have its intended
    effect (i.e. to only have a k/v pair or a particular
    index if there is such a source value).

    Returns:
        Either the fully-resolved object in dst
        (i.e. with all callables on input resolved)
        or a coroutine that, when awaited, will
        return the fully-resolved object. The coroutine
        will only be returned if *any one* callable in
        dst returned a coroutine (checked via
        asyncio.iscoroutine).
    
    Raises:
        Any underlying exception that isn't SkipIteration.
    """
    portmap = {
        dict: port_dict,
        list: port_seq(list),
        tuple: port_seq(tuple),
        set: port_seq(set)
    }

    if type(dst) in portmap:
        return portmap[type(dst)](src, dst)
    else:
        h = port_ident(src, dst)
        if asyncio.iscoroutine(h):
            return port_async(src, h)
        else:
            return h


async def port_async(src, dst):
    real_dst = dst
    while asyncio.iscoroutine(real_dst):
        real_dst = await real_dst
        real_dst = port(src, real_dst)
    return real_dst


def port_dict(src, dst):
    ret_dict = {}
    must_async_resolve = False
    for k, v in dst.items():
        try:
            ret_dict_key = port(src, k)
            ret_dict_val = port(src, v)
            if asyncio.iscoroutine(ret_dict_key) or asyncio.iscoroutine(ret_dict_val):
                must_async_resolve = True
            ret_dict[ret_dict_key] = ret_dict_val
        except SkipIteration:
            pass
    if must_async_resolve:
        return async_port_dict(src, ret_dict)
    else:
        return ret_dict


async def async_port_dict(src, dst):
    ret_dict = {}
    for k, v in dst.items():
        while asyncio.iscoroutine(k):
            k = await k
            k = port(src, k)
        while asyncio.iscoroutine(v):
            v = await v
            v = port(src, v)
        
        ret_dict[k] = v
    
    return ret_dict


def port_seq(which_type):
    def impl(src, dst):
        r = []
        async_resolve = False
        for i in dst:
            try:
                result = port(src, i)
                r.append(result)
                if asyncio.iscoroutine(result):
                    async_resolve = True
            except SkipIteration:
                pass
        if async_resolve:
            return async_port_seq(which_type, src, r)
        else:
            return which_type(r)
    return impl


async def async_port_seq(which_type, src, dst):
    r = []
    for i in dst:
        while asyncio.iscoroutine(i):
            i = await i
            i = port(src, i)
        r.append(i)
    return which_type(r)
        

def port_ident(src, dst):
    if callable(dst):
        result = dst(src)
        if asyncio.iscoroutine(result):
            return port_async(src, result)
        else:
            return result
    return dst
