
__all__ = ["FromAttr", "KeyOrDefault", "Template"]

def FromAttr(attr_name, *default):
	def impl(source):
		return getattr(source, attr_name, *default)
	return impl

def KeyOrDefault(key_name, *default):
	def impl(source):
		try:
			return source[key_name]
		except (KeyError, IndexError) as e:
			if not default:
				raise
			else:
				return default[0]
	return impl

def Template(template, resolver=None):
	def impl(source):
		if callable(resolver):
			source = resolver(source)
		if isinstance(source, dict):
			return template.format(**source)
		else:
			return template.format(*source)
	return impl