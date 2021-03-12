import numpy as np

from sim_objs import *
from rvs import *

def sim_EW(X, S, arrival_slicer=None, num_tasks=10000):
	env = simpy.Environment()
	s = Sink(0, env, num_tasks)
	q = FCFS(0, env, out=s)
	TaskGen(env, interarrival_time_rv=X, serv_time_rv=S, out=q, arrival_slicer=arrival_slicer)
	env.run(until=s.wait_forAllTasks)
	log(INFO, "Average load= {}".format(q.load()))

	return np.mean(q.wait_time_l)

def exp_interarrival_dist_2qs():
	num_tasks = 10000
	S = Exp(10)
	X = Exp(18)
	log(INFO, "", S=S, X=X)

	def arrival_slicer():
		return True if random.uniform(0, 1) < 0.5 else False
	EW = sim_EW(X, S, arrival_slicer, num_tasks)
	log(INFO, "Arrival to Q with probability 0.5", EW=EW)

	# rv_l = [Exp(8), Exp(8)]
	# X = SumOfRVs(rv_l)
	count = 0
	def arrival_slicer():
		nonlocal count
		s = True if count == 0 else False
		count = (count + 1) % 2
		return s
	EW = sim_EW(X, S, arrival_slicer, num_tasks)
	log(INFO, "Arrival to Q round-robin", EW=EW)

def exp_interarrival_dist():
	num_tasks = 10000*10
	S = Exp(0.1)
	# X = Exp(35)
	X = TPareto(1, 20, 1.2)
	log(INFO, "", S=S, X=X)

	N = 12
	n = 3

	## Random
	def arrival_slicer():
		return True if random.uniform(0, 1) < n/N else False
	EW = sim_EW(X, S, arrival_slicer, num_tasks)
	log(INFO, "Random w.p. {}".format(n/N), EW=EW)

	## Skewed round-robin
	count = 0
	def arrival_slicer():
		nonlocal count
		s = True if count < n else False
		count = (count + 1) % N
		return s
	EW = sim_EW(X, S, arrival_slicer, num_tasks)
	log(INFO, "Skewed round-robin", EW=EW)

	## Balanced round-robin
	count = 0
	def arrival_slicer():
		nonlocal count
		s = True if count % int(N/n) == 0 else False
		count = (count + 1) % N
		return s
	EW = sim_EW(X, S, arrival_slicer, num_tasks)
	log(INFO, "Balanced round-robin", EW=EW)

if __name__ == '__main__':
	# exp_interarrival_dist_2qs()
	exp_interarrival_dist()
