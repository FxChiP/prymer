
__all__ = ["FromAttr", "KeyOrDefault", "Template"]

def FromAttr(attr_name, *default):
	def impl(source):
		return getattr(source, attr_name, *default)
	return impl

def KeyOrDefault(key_name, *default):
	def impl(source):
		return source.get(key_name, *default)
	return impl

def Template(template, resolver=None):
	def impl(source):
		if callable(resolver):
			source = resolver(source)
		return template.format(**source)
	return impl