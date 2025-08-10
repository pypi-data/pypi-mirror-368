import os, inspect
from .util import Basic
from .templates import RTMP, PTMP

class Builder(Basic):
	def __init__(self, name, config):
		self.name = name
		self.config = config

	def build(self):
		self.log("build")
		self.dir()
		self.env()
		self.deps()

	def dir(self):
		bp = self.config.path.base
		self.log("dir", bp)
		os.makedirs(bp)

	def env(self):
		py = self.config.py
		vp = self.config.path.venv
		self.log("env", py, vp)
		self.out("%s -m venv %s"%(py, vp))

	def deps(self):
		deps = self.config.deps
		self.log("deps", *deps)
		for dep in deps:
			self.install(dep)

	def clone(self, package):
		self.log("clone", package)
		gp = package["git"]
		pjoin = os.path.join
		gdir = gp.split("/").pop()
		os.chdir(self.config.path.base)
		self.out("git clone https://github.com/%s.git"%(gp,))
		sym = package.get("sym")
		sym and self.out("ln -s %s"%(pjoin(gdir, sym),))
		os.chdir(pjoin("..", ".."))
		return gdir

	def req(self, req, rfile=False, upgrade=False):
		if rfile:
			req = "-r %s"%(req,)
		if upgrade:
			req = "-U %s"%(req,)
		self.out("%s install %s"%(self.config.path.pip, req))

	def reqs(self, reqfile="requirements.txt", gdir=None):
		self.log("reqs", reqfile, gdir)
		if gdir:
			reqfile = os.path.join(self.config.path.base, gdir, reqfile)
		self.req(reqfile, True)

	def install(self, package, upgrade=False):
		self.log("install", package)
		if type(package) is str:
			return self.req(package, package.endswith(".txt"), upgrade)
		gdir = package.get("git") and self.clone(package)
		reqs = package.get("requirements")
		reqs and self.reqs(reqs, gdir)

	def register(self, func, port, withpath=False):
		cfg = self.config
		fsrc = inspect.getsource(func)
		name = fsrc.split(" ", 1).pop(1).split("(", 1).pop(0)
		rp = self.based("%s.py"%(name,))
		cfg.path.run.update(name, rp)
		caller = fsrc.startswith("class") and "%s(log)"%(name,) or name
		self.log("register", name, rp)
		codestring = (cfg.persistent and PTMP or RTMP)%(fsrc, caller)
		if cfg.persistent:
			codestring = codestring.replace("WITHPATH", str(withpath))
			codestring = codestring.replace("PID", str(os.getpid()))
			codestring = codestring.replace("PORT", str(port))
		with open(rp, "w") as f:
			f.write(codestring)
		return name