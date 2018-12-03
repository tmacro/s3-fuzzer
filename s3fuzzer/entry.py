import os
import sys

from .run import main
from .util.conf import config
from .util.log import Log

_log = Log('entry')

def entry():
    if len(sys.argv) == 1:
        usage(sys.argv[0])
        sys.exit()

    seed = int(sys.argv[1])

    count = -1
    if len(sys.argv) > 2:
        count = int(sys.argv[2])

    step = 0
    if len(sys.argv) > 3:
        step = int(sys.argv[3])

    _log.info('Starting fuzzer seed:%s step:%s/%s'%(seed, step, count))
    try:
        sys.exit(main(seed, count, step))
    except Exception as e:
        _log.error('Caught unhandled exception! Logging and exiting')
        _log.exception(e)
        sys.exit(1)

def usage(app):
    print('Usage: %s <seed> [rounds] [step]'%os.path.basename(app))
    print('\trounds: How many listings to try. Pass -1 for infinite rounds')
    print('\tstep: Which round to start on. NOTE: step begins at 0')
