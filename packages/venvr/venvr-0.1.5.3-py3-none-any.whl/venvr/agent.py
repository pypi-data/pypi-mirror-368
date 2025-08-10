from os.path import isdir
from time import sleep
from fyg import Config
from .util import Basic
from .runner import Runner
from .builder import Builder

class Agent(Basic):
	def __init__(self, name, vstore, deps=[], py="python3", persistent=True, port=None):
		self.name = name
		if persistent:
			self.log("adding dez dependency for persistent mode")
			deps.append("dez")
		self.config = Config({
			"py": py,
			"deps": deps,
			"running": {},
			"registered": {},
			"nextport": port,
			"vstore": vstore,
			"persistent": persistent
		})
		self.setup()

	def getport(self):
		cfg = self.config
		if not cfg.persistent:
			return
		np = cfg.nextport
		cfg.update("nextport", cfg.nextport + 1)
		self.log("getport", np)
		return np

	def start(self, fname):
		cfg = self.config
		port = cfg.registered[fname]
		self.log("starting", fname, port)
		cfg.running.update(fname, True)
		self.runner.start(fname, port)

	def run(self, fname, *args, **kwargs):
		self.log("run", fname, args, kwargs)
		if self.config.persistent and not self.config.running[fname]:
			self.start(fname)
			self.log("waiting 1 sec for initialization")
			sleep(1)
		return self.runner.run(fname, *args, **kwargs)

	def register(self, func, withpath=False):
		port = self.getport()
		name = self.builder.register(func, port, withpath)
		self.log("registered", name, port)
		self.config.registered.update(name, port)
		return name

	def profile(self):
		self.log("profile")
		self.out("ls %s"%(self.config.path.base,))

	def setup(self):
		self.log("setup")
		self.setpaths()
		self.runner = Runner(self.name, self.config)
		self.builder = Builder(self.name, self.config)
		isdir(self.config.path.base) or self.builder.build()

	def setpaths(self):
		base = self.based(self.name, self.config.vstore)
		self.log("setpaths", base)
		venv = self.based("venv", base)
		binp = self.based("bin", venv)
		self.config.update("path", {
			"run": {},
			"base": base,
			"venv": venv,
			"pip": self.based("pip", binp),
			"py": self.based("python", binp)
		})