import random, scipy, math
import scipy.integrate
import scipy.stats

from debug_utils import *

class RV(): # Random Variable
	def __init__(self, l_l, u_l):
		self.l_l = l_l
		self.u_l = u_l

class Exp(RV):
	def __init__(self, mu, D=0):
		super().__init__(l_l=D, u_l=float("inf") )
		self.D = D
		self.mu = mu

	def __repr__(self):
		if self.D == 0:
			return r'Exp(\mu={})'.format(self.mu)
		return r'{} + Exp(\mu={})'.format(self.D, self.mu)

	def tail(self, x):
		if x <= self.l_l:
			return 1
		return math.exp(-self.mu*(x - self.D) )

	def cdf(self, x):
		if x <= self.l_l:
			return 0
		return 1 - math.exp(-self.mu*(x - self.D) )

	def pdf(self, x):
		if x <= self.l_l:
			return 0
		return self.mu*math.exp(-self.mu*(x - self.D) )

	def mean(self):
		return self.D + 1/self.mu

	def var(self):
		return 1/self.mu**2

	def moment(self, i):
		if i == 1:
			return self.mean()
		elif i == 2:
			return 1/self.mu**2 + self.mean()**2
		return moment_ith(i, self)

	def laplace(self, s):
		if self.D > 0:
			log(ERROR, "D= {} != 0".format(D) )
		return self.mu/(s + self.mu)

	def sample(self):
		return self.D + random.expovariate(self.mu)

class TPareto(RV): # Truncated
	def __init__(self, l, u, a):
		super().__init__(l_l=l, u_l=u)
		self.l = l
		self.u = u
		self.a = a

	def __repr__(self):
		return "TPareto(l= {}, u= {}, a= {})".format(self.l, self.u, self.a)

	def to_latex(self):
		return r'TPareto($\min= {}$, $\max= {}$, $\alpha= {}$)'.format(self.l, self.u, self.a)

	def pdf(self, x):
		if x < self.l: return 0
		elif x >= self.u: return 0
		else:
			return self.a*self.l**self.a * 1/x**(self.a+1) / (1 - (self.l/self.u)**self.a)

	def cdf(self, x):
		if x < self.l: return 0
		elif x >= self.u: return 1
		else:
			return (1 - (self.l/x)**self.a)/(1 - (self.l/self.u)**self.a)

	def tail(self, x):
		return 1 - self.cdf(x)

	def mean(self):
		return self.moment(1)

	def std(self):
		return math.sqrt(self.moment(2) - self.mean()**2)

	def moment(self, k):
		if k == self.a:
			return math.log(self.u_l/self.l)
		else:
			try:
				r = self.l/self.u
				return self.a*self.l**k/(self.a-k) * \
							 (1 - r**(self.a-k))/(1 - r**self.a)
			except:
				# x = math.log(self.l) - math.log(self.u)
				# return self.a*self.l**k/(self.a-k) * \
				#       (1 - math.exp((self.a-k)*x) )/(1 - math.exp(self.a*x) )
				r = self.l/self.u
				log(INFO, "", r=r, a=self.a, k=k)
				return self.a*self.l**k/(self.a-k) * \
							 (r**k - r**self.a)/(r**k - r**(self.a + k) )

	def sample(self):
		r = random.uniform(0, 1)
		s = self.l*(1 - r*(1-(self.l/self.u)**self.a) )**(-1/self.a)
		if s < self.l or s > self.u:
			log(ERROR, "illegal sample! s= {}".format(s) )
			return None
		return s

class DiscreteRV():
	def __init__(self, p_l, v_l):
		self.p_l = p_l
		self.v_l = v_l
		self.dist = scipy.stats.rv_discrete(name='discrete', values=(v_l, p_l))

	def __repr__(self):
		return 'DiscreteRV:\n' + \
			'\t p_l= {}\n'.format(self.p_l) + \
			'\t rv_l= {}\n'.format(self.rv_l)

	def mean(self):
		return self.dist.mean()

	def sample(self):
		return self.dist.rvs()

class SumOfRVs(RV):
	def __init__(self, rv_l):
		super().__init__(l_l=sum(rv.l_l for rv in rv_l), u_l=sum(rv.u_l for rv in rv_l))
		self.rv_l = rv_l

	def __repr__(self):
		return r'SumOfRVs(rv_l= {})'.format(self.rv_l)

	def sample(self):
		return sum(rv.sample() for rv in self.rv_l)

class CycleOverRVs(RV):
	def __init__(self, rv_l):
		super().__init__(l_l=min(rv.l_l for rv in rv_l), u_l=max(rv.u_l for rv in rv_l))
		self.rv_l = rv_l

		self.cur_i = 0

	def __repr__(self):
		return r'CycleOverRVs(rv_l= {})'.format(self.rv_l)

	def sample(self):
		s = self.rv_l[self.cur_i].sample()
		self.cur_i = self.cur_i % len(self.rv_l)
		return s

# ################################  utils  ################################ #

## Pr{a < X < b}
def Pr_X(X, a=None, b=None):
	if a is None and b is None:
		return 1

	if a is not None and b is not None:
		check(a < b, "a= {} < b= {} should have hold!".format(a, b))

	low = X.l_l if a is None else max(X.l_l, a)
	high = X.u_l if b is None else min(X.u_l, b)
	Pr, _ = scipy.integrate.quad(lambda y: X.pdf(y), low, high)
	return Pr

## Pr{a < X < right_boundary (?)} = prob
def right_boundary_forGivenPr(X, a, prob):
	if Pr_X(X, a) <= prob:
		log(WARNING, "Cannot find the right boundary, returning the max possible value.", X=X, a=a, prob=prob)
		return X.u_l

	l = a
	r = (a + 1) * 10**3
	while Pr_X(X, a, r) < prob:
		r *= 10
	log(DEBUG, "Starting binary search", l=l, r=r)

	while (r - l > 0.01):
		m = (l + r)/2
		# log(DEBUG, "", m=m)
		if Pr_X(X, a, m) < prob:
			l = m
		else:
			r = m

	return (l + r)/2

def test_right_boundary_forGivenPr():
	X = Exp(1)
	log(INFO, "", X=X)

	a = 0.2
	prob = 0.3
	b = right_boundary_forGivenPr(X, a, prob)
	prob_ = Pr_X(X, a, b)
	log(INFO, "", a=a, b=b, prob=prob, prob_=prob_)

def intervals_for_probs(X, prob_l):
	check(X.l_l > float('-Inf'), "Lower limit cannot be -inf.")
	check(sum(prob_l) == 1, "Probabilities should sum to 1.")

	interval_l = []
	a = X.l_l
	for prob in prob_l[:-1]:
		b = right_boundary_forGivenPr(X, a, prob)
		interval_l.append((a, b))
		log(DEBUG, "", a=a, b=b, prob=prob)
		a = b
	interval_l.append((a, min(float('Inf'), X.u_l)))

	return interval_l

def test_intervals_for_probs():
	X = Exp(1)
	log(INFO, "", X=X)

	prob_l = [0.2, 0.8]
	interval_l = intervals_for_probs(X, prob_l)
	prob_computed_l = [Pr_X(X, a, b) for (a, b) in interval_l]
	log(INFO, "", prob_l=prob_l, interval_l=interval_l, prob_computed_l=prob_computed_l)

## E[X^i | a < X < b]
def moment(X, i, a=None, b=None):
	if a is None and b is None:
		return X.moment(i)

	if a is not None and b is not None:
		check(a < b, "a < b should hold!")

	low = X.l_l if a is None else max(X.l_l, a)
	high = X.u_l if b is None else min(X.u_l, b)
	r, abserr = scipy.integrate.quad(lambda y: y**i*X.pdf(y), low, high)
	Pr_X_between_low_high, _ = scipy.integrate.quad(lambda y: X.pdf(y), low, high)
	check(Pr_X_between_low_high != 0, "Pr_X_between_low_high cannot be 0!")

	return r / Pr_X_between_low_high

def mean(X, a=None, b=None):
	return moment(X, 1, a, b)

def test_moment():
	X = Exp(1)
	EX = mean(X)

	low, mid = 0.2, 0.5
	EX_low = moment(X, 1, b=low)
	Pr_low = Pr_X(X, b=low)
	log(INFO, "", EX_low=EX_low, Pr_low=Pr_low)

	EX_mid = moment(X, 1, a=low, b=mid)
	Pr_mid = Pr_X(X, a=low, b=mid)
	log(INFO, "", EX_mid=EX_mid, Pr_mid=Pr_mid)

	EX_high = moment(X, 1, a=mid)
	Pr_high = Pr_X(X, a=mid)
	log(INFO, "", EX_high=EX_high, Pr_high=Pr_high)

	EX_total = Pr_low*EX_low + Pr_mid*EX_mid + Pr_high*EX_high
	log(INFO, "", EX=EX, EX_total=EX_total)

if __name__ == '__main__':
	# test_moment()
	# test_right_boundary_forGivenPr()
	test_intervals_for_probs()
