import numpy as np

from sim_objs import *
from sching_utils import *

def sim_EW(X, S, V, num_qs, to_which_q, num_jobs):
	env = simpy.Environment()
	s = Sink(0, env, num_jobs)
	q_l = [FCFS(0, env, out=s) for _ in range(num_qs)]
	js = JobDispatcher(0, env, q_l, to_which_q)
	JobGen(env, interarrival_time_rv=X, size_bits_rv=S, serv_time_rv=V, out=js)
	env.run(until=s.wait_forAllJobs)
	log(INFO, "",
			num_served=[q.num_served for q in q_l],
			average_load=[q.load() for q in q_l],
			average_wait_time=[np.mean(q.wait_time_l) for q in q_l])

def exp_interarrival_dist():
	num_qs = 3
	num_jobs = num_qs*50000
	X = Exp(2.5) # TPareto(1, 20, 1.2)
	S = Exp(1) # TPareto(1, 100, 0.8)
	log(INFO, "", ES=Mean(S), ES2=Moment(S, 2))
	V = DiscreteRV(p_l=[1], v_l=[1])
	ar = 1/Mean(X)
	log(INFO, "", X=X, S=S, ar=ar)

	# total_load = 1/X.mean(1) * S.mean(1)
	load_frac_l = [1/num_qs for _ in range(num_qs)]

	## Random
	rv = DiscreteRV(p_l=load_frac_l, v_l=list(range(num_qs)))
	def to_which_q(job):
		return rv.sample()
	log(INFO, "Random:")
	sim_EW(X, S, V, num_qs, to_which_q, num_jobs)
	log(INFO, "", EW_model=[EW_MG1(ar*load_frac, S) for load_frac in load_frac_l])
	print("\n")

	## Size based
	interval_l = intervals_forProbTimesMeanFracs(S, load_frac_l)
	for i, (a, b) in enumerate(interval_l):
		ES = Moment(S, 1, a, b)
		ES2 = Moment(S, 2, a, b)
		CVS = CoeffVar(S, a, b)
		log(INFO, "Interval-{}".format(i), interval=(a, b), ES=ES, ES2=ES2, CVS=CVS)
	def to_which_q(job):
		i_ = None
		for i, (a, b) in enumerate(interval_l):
			if a <= job.size_bits <= b:
				i_ = i
				break
		check(i_ is not None, "Job size did not fit into any of the intervals.")
		return i_
	log(INFO, "Size based:")
	sim_EW(X, S, V, num_qs, to_which_q, num_jobs)

	log(INFO, "", EW_model=[EW_MG1(ar*Prob(S, a, b), TruncatedX(S, a, b)) for (a, b) in interval_l])
	print("\n")

	## Skewed round-robin
	# count = 0
	# def to_which_q():
	#		nonlocal count
	#		s = True if count < n else False
	#		count = (count + 1) % N
	#		return s
	# EW = sim_EW(X, S, to_which_q, num_jobs)
	# log(INFO, "Skewed round-robin", EW=EW)

	## Balanced round-robin
	# count = 0
	# def arrival_slicer():
	#		nonlocal count
	#		s = True if count % int(N/n) == 0 else False
	#		count = (count + 1) % N
	#		return s
	# EW = sim_EW(X, S, arrival_slicer, num_jobs)
	# log(INFO, "Balanced round-robin", EW=EW)

if __name__ == '__main__':
	# exp_interarrival_dist_2qs()
	exp_interarrival_dist()
