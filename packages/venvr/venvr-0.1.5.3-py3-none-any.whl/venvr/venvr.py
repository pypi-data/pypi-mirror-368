from .manager import Manager

manny = None

def getman(vstore=None):
	global manny
	if not manny:
		manny = Manager(vstore)
	return manny

def getagent(name, deps=[], persistent=True):
	return getman().agent(name, deps, persistent)

def run(envname, deps, func, *args, **kwargs):
	agent = getagent(envname, deps)
	if type(func) is not str:
		func = agent.register(func)
	return agent.run(func, *args, **kwargs)

def call(envname, func, *args, **kwargs):
	return getagent(envname, persistent=False).run(func, *args, **kwargs)

def install(envname, pname, upgrade=False):
	getagent(envname).builder.install(pname, upgrade)

def profile(envname=None):
	(envname and getagent(envname) or getman()).profile()