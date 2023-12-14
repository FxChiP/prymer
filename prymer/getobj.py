
#
# The Get object
#

from prymer.op import SkipIteration


__all__ = ["Get"]


def _get_bracket(target, target_name):
    return target[target_name]


class _GetChainLink(object):
    """
    _GetChainLink
    
    This is the crux of the implementation and the point
    of prymer. The idea is that we want to easily and 
    recursively define an access for an arbitrarily deep
    object, dict, or list, in a readable, not-multiline way.
    Ideally, for instance, something like:

    get_first_image = prymer.Get.obj['spec']['template']['spec']['containers'][0]['image']

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
    getattr() called on prymer.Get has a default in mind, for
    instance. To work around that, we have a special case: if the
    key to the prymer.Get[] invocation is a callable, that callable
    is run instead of getting the key, and the result of *that* is
    passed down the chain.[1] As an extension of that special case,
    you can also implement callables that take one argument (the
    data to extract from) and use them in the square brackets to apply
    that operation at that particular point in time.

    [1] If your source dict key is a callable, you will have to use
        prymer.Get[prymer.KeyOrDefault(your_callable)] to get at it.
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
        self.__op = op
        self.__op_arg = op_arg
        self.__parent = parent

    def __getattr__(self, target_attr):
        """
        prymer.Get.something
        """
        return _GetChainLink(self, getattr, target_attr)

    def __getitem__(self, target_whatever):
        """
        prymer.Get["something"]
        or
        prymer.Get[FromAttr("something","default")]
        """
        return _GetChainLink(self, _get_bracket, target_whatever)
    
    def __repr__(self):
        if self.__op is None and self.__parent is None:
            return "prymer.Get"
        else:
            if self.__op is getattr:
                return f"{self.__parent.__repr__()}.{self.__op_arg}"
            elif self.__op is _get_bracket:
                if callable(self.__op_arg):
                    return f"{self.__parent.__repr__()}[{self.__op_arg.__name__}(...)]"
                else:
                    return f"{self.__parent.__repr__()}[{self.__op_arg.__repr__()}]"

    def __call__(self, source):
        """
        Run the entire chain on source

        This will recurse up the chain (i.e. each
        _GetChainLink calling into its self.__parent)
        before running this chain link's operation with
        op arg and returning the result (either to its
        child or to the actual caller)
        """

        # Recurse up the chain
        if self.__parent:
            current = self.__parent(source)
        else:
            current = source

        if callable(self.__op_arg):
            # Means we want to do an operation
            # while we're doing the get
            # The operation will completely
            # transform the result, and that
            # transformation is what should go
            # down the line
            try:
                result = self.__op_arg(current)
            except SkipIteration as e:
                # SkipIteration doesn't have any
                # special meaning to prymer.Get
                # see prymer.op for more details
                # but we want to raise whatever
                # got SkipIteration'd
                e.reraise()
        elif self.__op is None:
            # noop: identity
            result = current
        else:
            result = self.__op(current, self.__op_arg)

        return result


Get = _GetChainLink()
