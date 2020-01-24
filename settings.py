import os
import tempfile

#if windows
tmp_folder = f"{tempfile.gettempdir()}/rpg-shell"
campaing_folder = os.getcwd()

try:
	os.mkdir(tmp_folder)
except Exception:
	pass