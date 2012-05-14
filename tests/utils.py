import os

def open_file(filepath, mode='r'):
	"""Helper function to open files from within the tests directory."""
	return open(os.path.join(os.path.dirname(__file__), filepath), mode)