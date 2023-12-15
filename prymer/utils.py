
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
