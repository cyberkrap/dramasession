def lazy(f):
	'''
	Prevents certain properties from having to be recomputed each time they are referenced
	'''
	def wrapper(*args, **kwargs):
		o = args[0]
		if "_lazy" not in o.__dict__:
			o.__dict__["_lazy"] = {}
		name = f.__name__ + str(args) + str(kwargs),
		if name not in o.__dict__["_lazy"]:
			o.__dict__["_lazy"][name] = f(*args, **kwargs)
		return o.__dict__["_lazy"][name]
	wrapper.__name__ = f.__name__
	return wrapper
