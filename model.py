from rvs import *
from math_utils import *
from debug_utils import *

def EW_MG1(ar, X):
	EX = X.moment(1)
	ro = ar*EX
	if ro >= 1:
		log(WARNING, "ro= {} > 1, returning None.".format(ro))
		return None

	EX2 = X.moment(2)
	return ar*EX2/2/(1 - ar*EX)

def EW_MG1_fromRoAndCVX(ro, CVX):
	# CVX = CoeffVar(X)
	return ro/(1 - ro) * (CVX**2 + 1)/2
