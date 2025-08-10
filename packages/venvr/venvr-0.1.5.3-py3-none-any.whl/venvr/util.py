import os, sys
from fyg.util import Named, basiclog
from subprocess import getoutput, call

def log(*msg):
	basiclog("venvr", *msg)

def err(*msg):
	log("error!", *msg)
	sys.exit()

class Basic(Named):
	def out(self, cmd, background=False):
		self.log("out", cmd)
		if background:
			return call("%s &"%(cmd,), shell=True)
		out = getoutput(cmd)
		self.log(out)
		return out

	def based(self, fname, base=None):
		return os.path.join(base or self.config.path.base, fname)