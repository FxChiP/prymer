
def port(src, dst):
    portmap = {
        dict: port_dict,
        list: port_seq(list),
        tuple: port_seq(tuple)
    }

    if type(dst) in portmap:
        return portmap[type(dst)](src, dst)
    else:
        return port_ident(src, dst)


def port_dict(src, dst):
    ret_dict = {}
    for k, v in dst.items():
        ret_dict_key = port(src, k)
        ret_dict_val = port(src, v)
        ret_dict[ret_dict_key] = ret_dict_val

    return ret_dict


def port_seq(which_type):
    def impl(src, dst):
        r = []
        for i in dst:
            r.append(port(src, i))
        return which_type(r)
    return impl


def port_ident(src, dst):
    if callable(dst):
        return dst(src)
    return dst
