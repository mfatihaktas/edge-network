import numpy as np

from sim_objs import *
from rvs import *

def sim_EW(X, S, num_tasks=10000):
	env = simpy.Environment()
	s = Sink(0, env, num_tasks)
	q = FCFS(0, env, out=s)
	TaskGen(env, interarrival_time_rv=X, serv_time_rv=S, out=q)

	return np.mean(q.wait_time_l)

"""
Keeping the arrival rate fixed, change the inter-arrival distribution.
"""
def exp_interarrival_dist():
	S = Exp(1)
	X = Exp(1)
	EW = sim_EW(X, S, num_tasks=100)

	log(INFO, "", EW=EW, X=x)

if __name__ == '__main__':
	exp_interarrival_dist()
