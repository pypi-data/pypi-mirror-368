import requests
from .util import Basic

class Runner(Basic):
	def __init__(self, name, config):
		self.name = name
		self.config = config

	def runner(self, fname, args=[], noblock=False):
		path = self.config.path
		rstr = "%s %s"%(path.py, path.run[fname])
		if args:
			rstr = "%s %s"%(rstr, " ".join(['"%s"'%(a,) for a in args]))
		return self.out(rstr, noblock)

	def start(self, fname, port):
		self.log("start", fname, port)
		self.runner(fname, noblock=True)

	def run(self, fname, *args, **kwargs):
		cfg = self.config
		self.log("run", *args, kwargs)
		if cfg.persistent:
			self.log("persistent (via post)")
			resp = requests.post("http://localhost:%s/"%(cfg.registered[fname],), json={
				"args": args,
				"kwargs": kwargs
			}).content.decode()
			self.log(resp)
			return resp
		else:
			self.log("single (dropping kwargs)", *args)
			return self.runner(fname, args)