from .util import Basic
from .agent import Agent
from .config import config, getPortBlock

class Manager(Basic):
	def __init__(self, vstore=None):
		self.name = vstore or config.vstore
		self.nextPort = getPortBlock()
		self.venvrs = {} # detect?

	def getport(self):
		np = self.nextPort
		pslice = config.port.slice
		self.log("assigning ports", np, "to", np + pslice - 1)
		self.nextPort += pslice
		return np

	def profile(self):
		self.log("profile")
		self.out("ls %s"%(self.name,))

	def agent(self, name, deps=[], py="python3", persistent=True):
		if name not in self.venvrs:
			self.log("delegating agent", name)
			self.venvrs[name] = Agent(name, self.name, deps,
				py, persistent, persistent and self.getport())
		return self.venvrs[name]