import os

from . import settings

def cleanup():
	"""Routine responsible to cleaning up the files when shell is closed
	"""
	#removing temporary files
	os.rmdir(settings.tmp_folder)