import os
import sys

# from .run import main
from .fuzz import main
from .util.conf import config
from .util.log import Log

_log = Log('entry')

def entry():
	sys.exit(0)
	seed = config.runtime.seed
	if seed is None:
		seed = '1337h4CK$'
	_log.info('Starting fuzzer seed:%s step:%s/%s'%(seed, config.runtime.step, config.runtime.rounds))
	try:
		sys.exit(main(config.runtime.seed, config.runtime.rounds, config.runtime.step))
	except Exception as e:
		_log.error('Caught unhandled exception! Logging and exiting')
		_log.exception(e)
		sys.exit(1)
