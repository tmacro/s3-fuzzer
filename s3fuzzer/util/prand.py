import itertools
import random
import string


class PRNG:
	_alphabet = string.ascii_letters + string.digits + "!_.,"
	def __init__(self, seed):
		self._prng = random.Random()
		self._prng.seed(seed)

	def rint(self, bits=128, between=None):
		if between:
			if between[0] == between[1]:
				return between[0]
			return self._prng.randint(*between)
		return self._prng.getrandbits(bits)

	def rstr(self, length, alpha=None):
		if alpha is None:
			alpha = self._alphabet
		return ''.join(self._prng.choice(alpha) for x in range(length))

	def flip(self):
		return self._prng.choice([True, False])

	def choice(self, items):
		if isinstance(items, dict):
			return self._prng.choice(list(items.keys()))
		return self._prng.choice(items)

def iter_prng(seed, count = -1, step = 0):
	_prng = PRNG(seed)
	for _ in range(step):
		_prng.rint()
	for i in itertools.count(step):
		yield _prng.rint()
		if count != -1 and i >= count - 1:
			break
