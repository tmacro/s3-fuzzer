import sys
from s3fuzzer import entry


if len(sys.argv) == 1:
    entry.usage(sys.argv[0])
    sys.exit()

SEED = int(sys.argv[1])

COUNT = -1
if len(sys.argv) > 2:
    COUNT = int(sys.argv[2])

STEP = 0
if len(sys.argv) > 3:
    STEP = int(sys.argv[3])


entry.entry(SEED, COUNT, STEP)
