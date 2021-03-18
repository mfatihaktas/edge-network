import math, scipy

def lcm(*args):
	if len(args) == 2 and isinstance(args[0], int) and isinstance(args[1], int):
		[a, b] = args
		return abs(a*b) // math.gcd(a, b)
	elif len(args) == 1 and isinstance(args[0], list):
		r = 1
		for x in args:
			r = lcm(r, x)
		return r
	else:
		log(ERROR, "Unexpected args.")
		return None

def lcm(x_l):
	r = 1
	for x in x_l:
		r = lcm(r, x)

	return r

def G(z, x=None, type_=None):
	if x is None:
		return scipy.special.gamma(z)
	elif type_ == 'lower':
		return float(scipy.special.gammainc(z, x)*G(z) )
	elif type_ == 'upper':
		# return (1 - scipy.special.gammainc(z, x) )*G(z)
		return float(scipy.special.gammaincc(z, x)*G(z) )
