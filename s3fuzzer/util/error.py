class S3FuzzError(Exception):
	'''Root exception for all macrup errors'''

class UnknownError(S3FuzzError):
	'''You done fucked up. something happened, probably in a catch all'''

class ConfigError(S3FuzzError):
	'''Error regarding configuration'''

class InvalidConfigError(ConfigError):
	'''Error parsing a users configuration'''

class NoConfigError(ConfigError):
	'''Error locating a users config'''

class ConfigImportError(ConfigError):
	'''Error locating a child config file'''

class WorkloadTimeoutError(S3FuzzError):
	'''Raised when a workload exceeds its timeout'''
