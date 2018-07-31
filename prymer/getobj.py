
#
# The Get object
#

__all__ = ["Get"]


class _GetChainLink(object):
	def __init__(self, parent=None, op=None, op_arg=None):
		self.op = op
		self.op_arg = op_arg
		self.parent = parent

	def __getattr__(self, target_attr):
	    return _GetChainLink(self, getattr, target_attr)

	def __getitem__(self, target_whatever):
		return _GetChainLink(self, _GetChainLink.bracket, target_whatever)

	@staticmethod
	def bracket(target, target_name):
		return target[target_name]

	def __call__(self, source):
		if self.parent:
			current = self.parent(source)
		else:
			current = source

		if callable(self.op_arg):
			# Means we want to do an operation
			# while we're doing the get
			# The operation will completely
			# transform the result, and that
			# transformation is what should go
			# down the line
			result = self.op_arg(current)
		elif self.op is None:
			# noop: identity
			result = current
		else:
			result = self.op(current, self.op_arg)

		return result

Get = _GetChainLink()
