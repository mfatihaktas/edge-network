from debug_utils import *
import simpy

class Task():
	def __init__(self, _id, serv_time):
		self._id = _id
		self.serv_time = serv_time

	def __repr__(self):
		return "Task[id= {}, serv_time= {}]".format(self._id, self.serv_time)

class TaskGen(object):
	def __init__(self, env, interarrival_time_rv, serv_time_rv, out, arrival_slicer=None, **kwargs):
		self.env = env
		self.interarrival_time_rv = interarrival_time_rv
		self.serv_time_rv = serv_time_rv
		self.arrival_slicer = arrival_slicer
		self.out = out

		self.num_jobs_sent = 0

		self.action = self.env.process(self.run())

	def run(self):
		while 1:
			# random.expovariate(self.ar)
			yield self.env.timeout(self.interarrival_time_rv.sample())

			send = False
			if self.arrival_slicer is not None:
				send = self.arrival_slicer()

			if send:
				self.num_jobs_sent += 1
				self.out.put(Task(_id = self.num_jobs_sent,
													serv_time = self.serv_time_rv.sample()))

class Q(object):
	def __init__(self, _id, env):
		self._id = _id
		self.env = env

class FCFS(Q): # First Come First Serve
	def __init__(self, _id, env, out=None):
		super().__init__(_id, env)
		self.out = out

		self.store = simpy.Store(env)
		self.action = env.process(self.run())

		self.wait_time_l = []
		self.busy_time = 0
		self.idle_time = 0

	def __repr__(self):
		return "FCFS[_id= {}]".format(self._id)

	def load(self):
		return self.busy_time / (self.busy_time + self.idle_time)

	def put(self, task):
		task.arrival_time = self.env.now
		slog(DEBUG, self.env, self, "recved", task)
		return self.store.put(task)

	def run(self):
		while True:
			idle_start = self.env.now
			task = yield self.store.get()
			self.idle_time += self.env.now - idle_start

			busy_start = self.env.now
			slog(DEBUG, self.env, self, "will serve", task)
			yield self.env.timeout(task.serv_time)
			slog(DEBUG, self.env, self, "done serving", task)
			self.busy_time += self.env.now - busy_start

			self.wait_time_l.append(self.env.now - task.arrival_time)
			if self.out is not None:
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
		return "Sink[_id= {}, num_tasks= {}]".format(self._id, self.num_tasks)

	def put(self, task):
		slog(DEBUG, self.env, self, "recved, num_tasksRecvedSoFar= {}".format(self.num_tasksRecvedSoFar), task)
		return self.store.put(task)

	def run(self):
		while True:
			task = yield self.store.get()

			self.num_tasksRecvedSoFar += 1
			if self.num_tasksRecvedSoFar >= self.num_tasks:
				return
