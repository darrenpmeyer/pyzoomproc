#!/bin/bash
"pyenv" "exec" "python3.8" "$0" "$@"
"exit" "$?"
# ^ above lines use pyenv to execute; modify or replace the shebang line 
#   if you don't use pyenv

import psutil
import subprocess
import os
import pwd
import sys
import time
import shlex
import re

# set up logging:
#   users can set the log level by setting an env var named 'PYZOOMPROC_LOG'
#   to a string matching one of the logging levels ('INFO' sets logging.INFO)
#   defaults to 'WARN', which selects logging.WARN
import logging
logging.basicConfig(
	stream=sys.stderr,
	level=getattr(logging, os.getenv('PYZOOMPROC_LOG', 'WARN')) )
mlog = logging.getLogger(__name__)


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
		subprocess.call(shlex.split(command))

	return pend_callback


def parse_command_line(args=sys.argv[1:], command_name=sys.argv[0]):
	if len(args) == 2:
		onair, offair = args
	elif len(args) == 1:
		onair = args[0] + " on"
		offair = args[0] + " off"
	else:
		mlog.critical(f"Incorrect command line parameters")
		print(f"Usage: {command_name} ONAIR_CMD OFFAIR_CMD")
		print(f"       {command_name} TOGGLE_CMD")
		print(f"TOGGLE_CMD will execute with 'on' or 'off' as a parameter")
		print(f"")
		print(f"Set log level with environment var 'PYZOOMPROC_LOG'")
		exit(1)

	mlog.info(f"Commands: onair='{onair}', offair='{offair}'")
	return onair, offair

# main program loop
onair_cmd, offair_cmd = parse_command_line()

while True:
	# Does a process matching the CptHost zoom process and owned by me exist?
	# that's a reliable proxy for "I am in a meeting"
	proc = scan_for_proc(
		matching=re.compile('^CptHost$'),
		for_user=pwd.getpwuid( os.getuid() )[0]
	)

	# we found one!
	if proc:
		# execute the on-air command
		mlog.info(f"Matching process found, executing '{onair_cmd}'")
		subprocess.call(shlex.split(onair_cmd))

		# and then wait for the found process to exit
		# when it does, the callback will execute the off-air command
		mlog.info(f"{proc.info} - waiting for exit")
		psutil.wait_procs([proc], callback=process_end(offair_cmd))

	# if we're not waiting for a process to end, only check every 5 seconds
	time.sleep(5)
