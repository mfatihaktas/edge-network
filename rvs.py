import random

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
