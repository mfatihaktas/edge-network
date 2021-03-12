from debug_utils import *
import simpy

class Task():
	def __init__(self, _id, serv_time):
		self._id = _id
		self.serv_time = serv_time

	def __repr__(self):
		return "Task[id= {}]".format(self._id)

class TaskGen(object):
	def __init__(self, env, interarrival_time_rv, serv_time_rv, out, **kwargs):
		self.env = env
		self.interarrival_time_rv = interarrival_time_rv
		self.serv_time_rv = serv_time_rv
		self.out = out

		self.num_jobs_sent = 0

		self.action = self.env.process(self.run())

	def run(self):
		while 1:
			# random.expovariate(self.ar)
			yield self.env.timeout(self.interarrival_time_rv.sample())

			self.num_jobs_sent += 1
			self.out.put(Task(_id = self.num_jobs_sent,
												serv_time = self.serv_time_rv))

class Q(object):
	def __init__(self, _id, env):
		self._id = _id
		self.env = env

class FCFS(Q): # First Come First Serve
	def __init__(self, _id, env, out=None):
		super().__init__(_id, env)
		self.out = out

		self.wait_time_l = []

		self.store = simpy.Store(env)
		self.action = env.process(self.run())

	def __repr__(self):
		return "FCFS[_id= {}]".format(self._id)

	def put(self, task):
		task.arrival_time = self.env.now
		slog(DEBUG, self.env, self, "recved", task)
		return self.store.put(task)

	def run(self):
		while True:
			task = yield self.store.get()

			slog(DEBUG, self.env, self, "will serve", task)
			yield self.env.timeout(task.serv_time)
			slog(DEBUG, self.env, self, "done serving", task)

			self.wait_time_l.append(self.env.now - task.arrival_time)
			if out is None:
				self.out.put(task)

class Sink():
	def __init__(self, _id, env, num_tasks):
		self._id = _id
		self.env = env
		self.num_tasks = num_tasks

		self.store = simpy.Store(env)
		self.num_tasksRecvedSoFar = 0

		self.wait_forAllTasks = env.process(self.run())

	def __repr__(self):
		return "Sink[_id= {}]".format(self._id)

	def put(self, task):
		slog(DEBUG, self.env, self, "recved", task)

		return self.store.put(task)

	def run(self):
		while True:
			task = yield self.store.get()

			self.num_tasksRecvedSoFar += 1
			if self.num_tasksRecvedSoFar >= self.num_tasks:
				return
