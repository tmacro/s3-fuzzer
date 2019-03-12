from .util.arg import option, flag

@option(dest='runtime.seed', metavar="SEED", nargs='?', default=None, help="Value used to seed the internal PRNG")
def seed(value):
	return value

@flag('-d', '--dry-run', dest='runtime.dry_run')
def dry_run(value):
	return True

@flag('-v', '--verbose', dest='logging.loglvl')
def verbose(value):
	return 'debug'

@flag('--no-cleanup', dest='runtime.cleanup')
def no_cleanup(value):
    return False

@option('-r', '--rounds',
		dest='runtime.rounds',
		type=int,
		metavar='ROUNDS',
		help='Number of rounds of fuzzing to perfom')
def rounds(value):
	return value

@option('-s', '--step',
		dest='runtime.step',
		type=int,
		metavar='STEP',
		help='Begin at this round, skipping previous')
def step(value):
	return value
