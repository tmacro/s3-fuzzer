import sys
from . import entry

__version__ = '0.0.1'


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
