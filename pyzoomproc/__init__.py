import psutil

import subprocess
import logging
mlog = logging.getLogger('pyzoomproc')


def scan_for_proc(matching, for_user=None):
	"""scans process list for matching process
	
	Returns the first running process belonging to the user named in 
	``for_user`` and whose processname (not full path!) matches the regex in
	``matching``

	If none is found, returns None

	Params:

		:matching: compiled regular expression
		:for_user: string
	"""
	mlog.debug(f"Looking for processes matching {matching} owned by {for_user}")
	for proc in psutil.process_iter(['pid', 'name', 'username']):
		if for_user is not None:
			if proc.info['username'] != for_user:
				mlog.debug(f"Skipping {proc.info['pid']}, belongs to {proc.info['username']}")
				continue
		
		mlog.debug(f"Considering {proc.info}")
		match = matching.search(proc.info['name'])
		if not match:
			mlog.debug(f"{proc.info['pid']}:{proc.info['name']} does not match, skipping")
			continue

		mlog.info(f"Found process match: {proc.info}")
		return proc

	return None


def process_end(command):
	"""generates a psutil.proc_wait() callback that executes ``command``
	
	Returns a function that accepts a ``pstil.Process`` object. When the
	returned function is called, it will execute ``command`` using the
	``subprocess.call`` method. 
	"""

	def pend_callback(proc):
		mlog.info(f"Executing '{command}' from process end callback")
		subprocess.call(command)

	return pend_callback