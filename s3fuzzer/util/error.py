class S3FuzzError(Exception):
	'''Root exception for all macrup errors'''
	pass

class UnknownError(S3FuzzError):
	'''You done fucked up. something happened, probably in a catch all'''
	pass

class ConfigError(S3FuzzError):
	'''Error regarding configuration'''
	pass

class InvalidConfigError(ConfigError):
	'''Error parsing a users configuration'''
	pass

class NoConfigError(ConfigError):
	'''Error locating a users config'''
	pass

class ConfigImportError(ConfigError):
	'''Error locating a child config file'''
