from optparse import OptionParser
from .venvr import call, install, profile
from .util import log, err
from .config import config

cli = {
	"call": call,
	"install": install,
	"profile": profile
}

def invoke():
	parser = OptionParser("venvr [call|install|profile] [env] [arg1] [arg2] ...")
	parser.add_option("-v", "--vstore", dest="vstore",
		default=config.vstore, help="where all the venvs live")
	options, args = parser.parse_args()
	if options.vstore != config.vstore:
		log("using vstore", options.vstore)
		config.update("vstore", options.vstore)
	args or err("what command?")
	cmd = args.pop(0)
	if cmd != "profile":
		args or err("what enviroment?")
	cli[cmd](*args)