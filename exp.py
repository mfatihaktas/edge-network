import numpy as np

from sim_objs import *
from rvs import *

def sim_EW(X, S, V, num_qs, to_which_q, num_tasks):
	env = simpy.Environment()
	s = Sink(0, env, num_tasks)
	q_l = [FCFS(0, env, out=s) for _ in range(num_qs)]
	js = JobSplitter(0, env, q_l, to_which_q)
	JobGen(env, interarrival_time_rv=X, size_bits_rv=S, serv_time_rv=V, out=js)
	env.run(until=s.wait_forAllTasks)
	log(INFO, "Average load= {}".format((q.load() for q in q_l)))

	log(INFO, "Average wait time= {}".format((np.mean(q.wait_time_l) for q in q_l)))

def exp_interarrival_dist():
	num_qs = 3
	num_tasks = num_qs*1000
	X = TPareto(1, 20, 1.2)
	S = Exp(0.1)
	V = Exp(0.1)
	log(INFO, "", X=X, S=S)

	# total_load = 1/X.mean(1) * S.mean(1)
	load_frac_l = [1/num_qs for _ in range(num_qs)]

	## Random
	def to_which_q():
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
