from rvs import *
from model import *

def binary_search(l, target, get_value):
	r = (l + 1) * 10**3
	while get_value(r) < target:
		r *= 10
	log(DEBUG, "Starting", l=l, r=r)

	while (r - l > 0.01):
		m = (l + r)/2
		# log(DEBUG, "", m=m)
		if get_value(m) < target:
			l = m
		else:
			r = m

	return (l + r)/2

## Pr{a < X < right_boundary (?)} = prob
def right_boundary_forGivenPr(X, a, prob):
	if Prob(X, a) <= prob:
		log(WARNING, "Cannot find the right boundary, returning the max possible value.", X=X, a=a, prob=prob)
		return X.u

	return binary_search(a, prob, lambda r: Prob(X, a, r))

def test_right_boundary_forGivenPr():
	X = Exp(1)
	log(INFO, "", X=X)

	a = 0.2
	prob = 0.3
	b = right_boundary_forGivenPr(X, a, prob)
	prob_ = Prob(X, a, b)
	log(INFO, "", a=a, b=b, prob=prob, prob_=prob_)

def intervals_forProbs(X, prob_l):
	check(X.l > float('-Inf'), "Lower limit cannot be -inf.")
	check(sum(prob_l) == 1, "Probabilities should sum to 1.")

	interval_l = []
	a = X.l
	for prob in prob_l[:-1]:
		b = right_boundary_forGivenPr(X, a, prob)
		interval_l.append((a, b))
		log(DEBUG, "", a=a, b=b, prob=prob)
		a = b
	interval_l.append((a, min(float('Inf'), X.u)))

	return interval_l

def test_intervals_forProbs():
	X = Exp(1)
	log(INFO, "", X=X)

	prob_l = [0.2, 0.8]
	interval_l = intervals_forProbs(X, prob_l)
	prob_computed_l = [Prob(X, a, b) for (a, b) in interval_l]
	log(INFO, "", prob_l=prob_l, interval_l=interval_l, prob_computed_l=prob_computed_l)

## E[X | a < X < right_boundary (?)} = mean
def right_boundary_forGivenMean(X, a, mean):
	if Mean(X, a) <= mean:
		log(WARNING, "Cannot find the right boundary, returning the max possible value.", X=X, a=a, mean=mean)
		return X.u

	return binary_search(a, mean, lambda r: Mean(X, a, r))

def test_right_boundary_forGivenMean():
	X = Exp(1)
	log(INFO, "", X=X)

	a = 0.2
	mean = 0.6
	b = right_boundary_forGivenMean(X, a, mean)
	mean_ = Mean(X, a, b)
	log(INFO, "", a=a, b=b, mean=mean, mean_=mean_)

def intervals_forMeanFracs(X, frac_l):
	check(X.l > float('-Inf'), "Lower limit cannot be -inf.")
	check(sum(frac_l) == 1, "Fractions should sum to 1.")
	EX = Mean(X)

	interval_l = []
	a = X.l
	for frac in frac_l[:-1]:
		mean_ = frac*EX
		b = right_boundary_forGivenMean(X, a, mean_)
		interval_l.append((a, b))
		log(DEBUG, "", a=a, b=b, mean_=mean_)
		a = b
	interval_l.append((a, min(float('Inf'), X.u)))

	return interval_l

def test_intervals_forMeanFracs():
	X = Exp(1)
	log(INFO, "", X=X)

	frac_l = [0.2, 0.8]
	interval_l = intervals_forMeanFracs(X, frac_l)
	meanFracs_computed_l = [Mean(X, a, b) for (a, b) in interval_l]
	log(INFO, "", frac_l=frac_l, interval_l=interval_l, meanFracs_computed_l=meanFracs_computed_l)

## Pr{a < X < right_boundary} x E[X | a < X < right_boundary (?)} = mean
def right_boundary_forGivenProbTimesMean(X, a, probTimesMean):
	if Prob(X, a) * Mean(X, a) <= probTimesMean:
		log(WARNING, "Cannot find the right boundary, returning the max possible value.", X=X, a=a, probTimesMean=probTimesMean)
		return X.u

	return binary_search(a, probTimesMean, lambda r: Prob(X, a, r) * Mean(X, a, r))

def test_right_boundary_forGivenProbTimesMean():
	X = Exp(1)
	log(INFO, "", X=X)

	a = 0.2
	probTimesMean = 0.6
	b = right_boundary_forGivenProbTimesMean(X, a, probTimesMean)
	probTimesMean_ = Prob(X, a, b) * Mean(X, a, b)
	log(INFO, "", a=a, b=b, probTimesMean=probTimesMean, probTimesMean_=probTimesMean_)

def intervals_forProbTimesMeanFracs(X, frac_l):
	check(X.l > float('-Inf'), "Lower limit cannot be -inf.")
	check(sum(frac_l) == 1, "Fractions should sum to 1.")
	EX = Mean(X)

	interval_l = []
	a = X.l
	for frac in frac_l[:-1]:
		probTimesMean = frac*EX
		b = right_boundary_forGivenProbTimesMean(X, a, probTimesMean)
		interval_l.append((a, b))
		log(DEBUG, "", a=a, b=b, probTimesMean=probTimesMean)
		a = b
	interval_l.append((a, min(float('Inf'), X.u)))

	return interval_l

def test_intervals_forProbTimesMeanFracs():
	def test(X, frac_l):
		log(INFO, "", X=X, frac_l=frac_l)
		interval_l = intervals_forProbTimesMeanFracs(X, frac_l)
		EX = Mean(X)
		probTimesMeanFracs_computed_l = [Prob(X, a, b) * Mean(X, a, b) / EX for (a, b) in interval_l]
		log(INFO, "", frac_l=frac_l, interval_l=interval_l, probTimesMeanFracs_computed_l=probTimesMeanFracs_computed_l)

	test(X=Exp(1), frac_l=[0.2, 0.8])
	test(X=TPareto(2, 100, 1.2), frac_l=[0.35, 0.65])

def midpoint_forEvenEWs(ar, S, a, b):
	log(INFO, "Started", a=a, b=b)
	l = a
	r = min((l + 1) * 10, b)
	while True:
		m = (l + r)/2
		# log(INFO, "", l=l, m=m, r=r)
		EW_leftMG1 = EW_MG1(ar*Prob(S, a, m), TruncatedX(S, a, m))
		EW_rightMG1 = EW_MG1(ar*Prob(S, m, b), TruncatedX(S, m, b))
		if EW_leftMG1 > EW_rightMG1:
			break
		if r*10 < b:
			r = r*10
		else:
			break
	# log(INFO, "Starting", l=l, r=r)

	while (r - l > 0.01):
		m = (l + r)/2
		# log(DEBUG, "", m=m)
		EW_leftMG1 = EW_MG1(ar*Prob(S, a, m), TruncatedX(S, a, m))
		EW_rightMG1 = EW_MG1(ar*Prob(S, m, b), TruncatedX(S, m, b))
		if EW_leftMG1 < EW_rightMG1:
			l = m
		else:
			r = m

	return (l + r)/2

def test_midpoint_forEvenEWs():
	ar = 0.9
	S = Exp(1)
	log(INFO, "", ar=ar, S=S)

	a, b = S.l, S.u
	m = midpoint_forEvenEWs(ar, S, a, b)
	print("m= {}".format(m))
	EW_left = EW_MG1(ar*Prob(S, a, m), TruncatedX(S, a, m))
	EW_right = EW_MG1(ar*Prob(S, m, b), TruncatedX(S, m, b))
	log(INFO, "", a=a, b=b, m=m, EW_left=EW_left, EW_right=EW_right)

# Job size intervals for evenly balancing the average waiting times across M/G/1's.
def intervals_forEvenEWs(ar, S, num_qs):
	check(num_qs % 2 == 0, "Implemented only for even number of q's.")

	def helper(ar, S, a, b, num_qs):
		log(INFO, "Started", a=a, b=b, num_qs=num_qs)
		if num_qs == 1:
			return [(a, b)]

		m = midpoint_forEvenEWs(ar, S, a, b)
		log(INFO, "", m=m)
		prob_to_left = Prob(S, a, m) / Prob(S, a, b)
		interval_left_l = helper(ar * prob_to_left, S, a, m, num_qs//2)
		interval_right_l = helper(ar * (1 - prob_to_left), S, m, b, num_qs//2)

		return interval_left_l + interval_right_l

	return helper(ar, S, S.l, S.u, num_qs)

def test_intervals_forEvenEWs():
	def test(ar, S, num_qs):
		log(INFO, "", S=S, num_qs=num_qs)
		interval_l = intervals_forEvenEWs(ar, S, num_qs)

		for (a, b) in interval_l:
			EW = EW_MG1(ar*Prob(S, a, b), TruncatedX(S, a, b))
			log(INFO, "", interval=(a, b), EW=EW)
		print("\n")

	test(ar=1, S=Exp(1), num_qs=4)
	# test(ar=0.3, S=TPareto(2, 100, 3), num_qs=2)

if __name__ == '__main__':
	# test_moment()
	# test_right_boundary_forGivenPr()
	# test_intervals_forProbs()
	# test_right_boundary_forGivenMean()
	# test_intervals_forMeanFracs()
	# test_right_boundary_forGivenProbTimesMean()
	# test_intervals_forProbTimesMeanFracs()
	# test_midpoint_forEvenEWs()
	test_intervals_forEvenEWs()
