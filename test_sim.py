import numpy as np

from sim_objs import *
from rvs import *
from model import *

def test_FCFS():
	ar = 0.7 # 1
	X = Exp(ar)
	S = TPareto(1, 100, 10) # Exp(2)
	log(INFO, "", EX=X.mean(), ES=S.mean())
	V = DiscreteRV(p_l=[1], v_l=[1])

	env = simpy.Environment()
	s = Sink(0, env, num_jobs=20000)
	q = FCFS(0, env, out=s)
	JobGen(env, interarrival_time_rv=X, size_bits_rv=S, serv_time_rv=V, out=q)
	env.run(until=s.wait_forAllJobs)

	log(INFO, "",
			num_served=q.num_served,
			avg_load=q.load(),
			avg_wait_time=np.mean(q.wait_time_l),
			EW=EW_MG1(ar, S))

if __name__ == '__main__':
	test_FCFS()
