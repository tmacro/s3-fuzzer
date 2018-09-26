import os
import sys

from .run import main
from .util.conf import config
from .util.log import Log

_log = Log('entry')

def entry(seed, count, step):
    _log.info('Starting fuzzer seed:%s step:%s/%s'%(seed, step, count))
    try:
        main(seed, count, step)
    except Exception as e:
        _log.error('Caught unhandled exception! Logging and exiting')
        _log.exception(e)

def usage(app):
    print('Usage: %s <seed> [rounds] [step]'%os.path.basename(app))
    print('\trounds: How many listings to try. Pass -1 for infinite rounds')
    print('\tstep: Which round to start on. NOTE: step begins at 0')


if __name__ == '__main__':
    if len(sys.argv) == 1:
        usage(sys.argv[0])
        sys.exit()

    SEED = int(sys.argv[1])

    COUNT = -1
    if len(sys.argv) > 2:
        COUNT = int(sys.argv[2])

    STEP = 0
    if len(sys.argv) > 3:
        STEP = int(sys.argv[3])


    entry(SEED, COUNT, STEP)
