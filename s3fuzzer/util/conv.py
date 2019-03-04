
def nonezip(a,b):
	'''
		Returns an element from both iterables, falling back to None if no element is found
	'''
	while True:
		va = next(a, None)
		vb = next(b, None)
		if va is not None and vb is not None:
			yield va, vb
		else:
			break
