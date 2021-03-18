import simpy

from debug_utils import *

class Job():
	def __init__(self, _id, size_bits, serv_time):
		self._id = _id
		self.size_bits = size_bits
		self.serv_time = serv_time

	def __repr__(self):
		return "Job[id= {}, size_bits= {}, serv_time= {}]".format(self._id, self.size_bits, self.serv_time)

class JobGen(object):
	def __init__(self, env, interarrival_time_rv, size_bits_rv, serv_time_rv, out, **kwargs):
		self.env = env
		self.interarrival_time_rv = interarrival_time_rv
		self.size_bits_rv = size_bits_rv
		self.serv_time_rv = serv_time_rv
		self.out = out

		self.num_jobs_sent = 0

		self.action = self.env.process(self.run())

	def run(self):
		while 1:
			# random.expovariate(self.ar)
			yield self.env.timeout(self.interarrival_time_rv.sample())

			self.num_jobs_sent += 1
			self.out.put(Job(_id = self.num_jobs_sent,
											 size_bits = self.size_bits_rv.sample(),
											 serv_time = self.serv_time_rv.sample()))

class Q(object):
	def __init__(self, _id, env):
		self._id = _id
		self.env = env

class FCFS(Q): # First Come First Serve
	def __init__(self, _id, env, speed=1, out=None):
		super().__init__(_id, env)
		self.speed = speed
		self.out = out

		self.store = simpy.Store(env)
		self.action = env.process(self.run())

		self.wait_time_l = []
		self.busy_time = 0
		self.idle_time = 0

		self.num_served = 0

	def __repr__(self):
		return "FCFS[_id= {}]".format(self._id)

	def load(self):
		return self.busy_time / (self.busy_time + self.idle_time)

	def put(self, job):
		job.arrival_time = self.env.now
		slog(DEBUG, self.env, self, "recved", job)
		return self.store.put(job)

	def run(self):
		while True:
			idle_start = self.env.now
			job = yield self.store.get()
			self.idle_time += self.env.now - idle_start

			self.wait_time_l.append(self.env.now - job.arrival_time)
			busy_start = self.env.now
			t = job.size_bits / self.speed
			slog(DEBUG, self.env, self, "will serve for t= {}".format(t), job)
			yield self.env.timeout(t)
			slog(DEBUG, self.env, self, "done serving", job)
			self.num_served += 1
			self.busy_time += self.env.now - busy_start

			if self.out is not None:
				self.out.put(job)

class Sink():
	def __init__(self, _id, env, num_jobs):
		self._id = _id
		self.env = env
		self.num_jobs = num_jobs

		self.store = simpy.Store(env)
		self.num_jobsRecvedSoFar = 0

		self.wait_forAllJobs = env.process(self.run())

	def __repr__(self):
		return "Sink[_id= {}, num_jobs= {}]".format(self._id, self.num_jobs)

	def put(self, job):
		slog(DEBUG, self.env, self, "recved, num_jobsRecvedSoFar= {}".format(self.num_jobsRecvedSoFar), job)
		return self.store.put(job)

	def run(self):
		while True:
			job = yield self.store.get()

			self.num_jobsRecvedSoFar += 1
			if self.num_jobsRecvedSoFar >= self.num_jobs:
				return

class JobDispatcher():
	def __init__(self, _id, env, q_l, to_which_q):
		self._id = _id
		self.env = env
		self.q_l = q_l
		self.to_which_q = to_which_q

	def __repr__(self):
		return "JobDispatcher[_id= {}]".format(self._id)

	def put(self, job):
		slog(DEBUG, self.env, self, "recved", job)

		i = self.to_which_q(job)
		check(i < len(self.q_l), "i= {} should have been < len(q_l)= {}".format(i, len(self.q_l)))

		return self.q_l[i].put(job)
