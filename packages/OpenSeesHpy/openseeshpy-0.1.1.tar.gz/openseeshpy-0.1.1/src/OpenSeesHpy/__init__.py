import sys

# requires Python 3.13 x64 on Windows
if sys.maxsize < 2**31:
    raise RuntimeError('64 bit system is required')

# platform dependent
if not sys.platform.startswith('win'):
  raise RuntimeError('OpenSeesH  is currently provided for Windows systems only.')
if not (sys.version_info[0] == 3 and sys.version_info[1] == 13):
  raise RuntimeError('Python version 3.13 is needed for OpenSeesH to run')
from .OpenSeesHpy import *