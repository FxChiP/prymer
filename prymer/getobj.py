
#
# The Get object
#

from prymer.op import SkipIteration


__all__ = ["Get"]


def _get_bracket(target, target_name):
    return target[target_name]


class _GetChainLink(object):
    def __init__(self, parent=None, op=None, op_arg=None):
        self.__op = op
        self.__op_arg = op_arg
        self.__parent = parent

    def __getattr__(self, target_attr):
        return _GetChainLink(self, getattr, target_attr)

    def __getitem__(self, target_whatever):
        return _GetChainLink(self, _get_bracket, target_whatever)

    def __call__(self, source):
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
                # This doesn't make any sense here
                e.reraise()
        elif self.__op is None:
            # noop: identity
            result = current
        else:
            result = self.__op(current, self.__op_arg)

        return result


Get = _GetChainLink()
