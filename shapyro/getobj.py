
#
# The Get object
#

import asyncio

from shapyro.op import SkipIteration


__all__ = ["Get"]


def _get_bracket(target, target_name):
    return target[target_name]


class _GetChainLink(object):
    """
    _GetChainLink
    
    This is the crux of the implementation and the point
    of shapyro. The idea is that we want to easily and 
    recursively define an access for an arbitrarily deep
    object, dict, or list, in a readable, not-multiline way.
    Ideally, for instance, something like:

    get_first_image = shapyro.Get.obj['spec']['template']['spec']['containers'][0]['image']

    which would always get us the first image in a Kubernetes
    Deployment/StatefulSet/etc. returned from e.g. pykube-ng.
    That way, we can define that once, and then just:

    get_first_image(pykube.Deployments.objects(k).get(name="test"))

    In order to do this, we implement each access as another link
    in a chain of them. So in this example, the first access is
    getattr(source, "obj"). The next access should get the "spec"
    key from the result of that: (getattr(source, "obj"))["spec"].
    And then ((getattr(source, "obj"))["spec"])["template"]... and
    so on. The ultimate result is what happens when there are no
    more things left to call. Unless an exception got raised --
    which, because of the way we're implemented, should be the
    *exact* same exception that would get raised if you did the
    access in question more eagerly.

    This also acts as a limitation, though: we can't know if the
    getattr() called on shapyro.Get has a default in mind, for
    instance. To work around that, we have a special case: if the
    key to the shapyro.Get[] invocation is a callable, that callable
    is run instead of getting the key, and the result of *that* is
    passed down the chain.[1] As an extension of that special case,
    you can also implement callables that take one argument (the
    data to extract from) and use them in the square brackets to apply
    that operation at that particular point in time.

    [1] If your source dict key is a callable, you will have to use
        shapyro.Get[shapyro.KeyOrDefault(your_callable)] to get at it.
    """
    def __init__(self, parent=None, op=None, op_arg=None):
        """
        parent is the previous access step
        op is the current access callable i.e. op(source, op_arg)
        op_arg is the argument to the op
            note that if op_arg is callable(source)
            it's expected to transform the result into something to
            pass down the line
        """
        def _call(source):
            """
            Run the entire chain on source

            This will recurse up the chain (i.e. each
            _GetChainLink calling into its self.__parent)
            before running this chain link's operation with
            op arg and returning the result (either to its
            child or to the actual caller)
            """
            def _shapyro_Get_resolve_from_current(current):
                """
                This part will just resolve what the current op
                on the current link is. We're defining it here
                so that we can re-use the functionality if we
                happen to hit an asyncio coroutine vs. inlining
                the whole thing.
                """
                if callable(op_arg):
                    # Means we want to do an operation
                    # while we're doing the get
                    # The operation will completely
                    # transform the result, and that
                    # transformation is what should go
                    # down the line
                    try:
                        result = op_arg(current)
                    except SkipIteration as e:
                        # SkipIteration doesn't have any
                        # special meaning to shapyro.Get
                        # see shapyro.op for more details
                        # but we want to raise whatever
                        # got SkipIteration'd
                        e.reraise()
                elif op is None:
                    # noop: identity
                    result = current
                else:
                    result = op(current, op_arg)
                
                return result

            async def _shapyro_async_Get_resolve(current, result=None):
                """
                Either parent or current link is asyncio coroutine
                So we must await the parent or the current or both
                """

                # maybe await parent
                if asyncio.iscoroutine(current):
                    current = await current
                
                if result is None:
                    # XXX: if it turned out the result of the current
                    # op is None, we technically take a slight perf hit
                    # here from doing it again ¯\_(ツ)_/¯
                    result = _shapyro_Get_resolve_from_current(current)

                if asyncio.iscoroutine(result):
                    result = await result
                
                return result
            

            # Recurse up the chain
            if parent:
                current = parent(source)
            else:
                current = source

            if asyncio.iscoroutine(current):
                # We have to return the coroutine that
                # resolves this chain
                return _shapyro_async_Get_resolve(current)
            else:
                # Parent was fine, let's try this link
                result = _shapyro_Get_resolve_from_current(current)
                if asyncio.iscoroutine(result):
                    # We have to return the coroutine that
                    # resolves this chain
                    return _shapyro_async_Get_resolve(current, result)
                else:
                    # We're all sync, so we're all good
                    return result
        
        def _repr():
            if op is None and parent is None:
                return "shapyro.Get"
            else:
                if op is getattr:
                    return f"{parent.__repr__()}.{op_arg}"
                elif op is _get_bracket:
                    if callable(op_arg):
                        return f"{parent.__repr__()}[{op_arg.__name__}(...)]"
                    else:
                        return f"{parent.__repr__()}[{op_arg.__repr__()}]"
        self.__call_repr = (_call, _repr)

    def __getattr__(self, target_attr):
        """
        shapyro.Get.something
        """
        return _GetChainLink(self, getattr, target_attr)

    def __getitem__(self, target_whatever):
        """
        shapyro.Get["something"]
        or
        shapyro.Get[FromAttr("something","default")]
        """
        return _GetChainLink(self, _get_bracket, target_whatever)
    
    def __repr__(self):
        _, _repr = self.__call_repr
        return _repr()
    
    def __call__(self, source):
        _call, _ = self.__call_repr
        return _call(source)


Get = _GetChainLink()
