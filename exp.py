import numpy as np

from sim_objs import *
from rvs import *

def sim_EW(X, S, V, num_qs, to_which_q, num_tasks):
	env = simpy.Environment()
	s = Sink(0, env, num_tasks)
	q_l = [FCFS(0, env, out=s) for _ in range(num_qs)]
	js = JobSplitter(0, env, q_l, to_which_q)
	JobGen(env, interarrival_time_rv=X, size_bits_rv=S, serv_time_rv=V, out=js)
	env.run(until=s.wait_forAllJobs)
	log(INFO, "Average load= {}".format([q.load() for q in q_l]))

	log(INFO, "Average wait time= {}".format([np.mean(q.wait_time_l) for q in q_l]))

def exp_interarrival_dist():
	num_qs = 3
	num_tasks = num_qs*20000
	X = Exp(2.5) # TPareto(1, 20, 1.2)
	S = Exp(1)
	V = Exp(1)
	log(INFO, "", X=X, S=S)

	# total_load = 1/X.mean(1) * S.mean(1)
	load_frac_l = [1/num_qs for _ in range(num_qs)]

	intervals_for_probs(X, load_frac_l)

	## Random
	rv = DiscreteRV(load_frac_l, list(range(num_qs)))
	def to_which_q(job):
		return rv.sample()
	log(INFO, "Random:")
	sim_EW(X, S, V, num_qs, to_which_q, num_tasks)

	## Size based
	interval_l = intervals_for_probs(S, load_frac_l)
	log(INFO, "", interval_l=interval_l)
	for i, (a, b) in enumerate(interval_l):
		ES = moment(S, 1, a, b)
		log(INFO, "Interval-{}".format(i), ES=ES)
	def to_which_q(job):
		i_ = None
		for i, interval in enumerate(interval_l):
			if interval[0] <= job.size_bits <= interval[1]:
				i_ = i
				break
		check(i_ is not None, "Job size did not fit into any of the intervals.")
		return i_
	log(INFO, "Size based:")
	sim_EW(X, S, V, num_qs, to_which_q, num_tasks)

	## Skewed round-robin
	# count = 0
	# def to_which_q():
	#		nonlocal count
	#		s = True if count < n else False
	#		count = (count + 1) % N
	#		return s
	# EW = sim_EW(X, S, to_which_q, num_tasks)
	# log(INFO, "Skewed round-robin", EW=EW)

	## Balanced round-robin
	# count = 0
	# def arrival_slicer():
	#		nonlocal count
	#		s = True if count % int(N/n) == 0 else False
	#		count = (count + 1) % N
	#		return s
	# EW = sim_EW(X, S, arrival_slicer, num_tasks)
	# log(INFO, "Balanced round-robin", EW=EW)

if __name__ == '__main__':
	# exp_interarrival_dist_2qs()
	exp_interarrival_dist()
