import sys
from s3fuzzer.util.log import setupLogging

setupLogging()

from s3fuzzer import entry

entry.entry()
