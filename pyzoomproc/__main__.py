import pyzoomproc
import click

import logging
import psutil
import os
import sys
import pwd
import re
import time
import shlex
import subprocess

mlog = logging.getLogger('pyzoomproc')


@click.command()
@click.option('--onair', 'onair_cmd', required=True, type=click.Path(),
	          help='Script to run when joining a Zoom meeting')
@click.option('--offair', 'offair_cmd', type=click.Path(),
			  help='Script to run when leaving a Zoom meeting')
@click.option('--process', 'process_regex', default='^CptHost$',
			  help='Regex to match for process name, used to debug')
@click.option('--loglevel', 'loglevel', default='WARN',
	          type=click.Choice(['ERROR', 'WARN', 'INFO', 'DEBUG'], case_sensitive=False))
def main(onair_cmd, offair_cmd, process_regex, loglevel):
	"""Runs scripts in response to you joining or leaving a Zoom call

	If no offair script is provided, then the onair script will be run with
	the argument 'on' when joining a Zoom call and 'off' when leaving.
	Otherwise, the scripts will be called without arguments.
	"""
	logging.basicConfig(stream=sys.stderr, level=getattr(logging, loglevel))
	print(f"Loglevel requested: {loglevel}")

	# if no offair script supplied, then pass "on" for onair and "off" for offair
	if offair_cmd is None:
		offair_cmd = onair_cmd + " off"
		onair_cmd = onair_cmd + " on"

	while True:
	# Does a process matching the CptHost zoom process and owned by me exist?
	# that's a reliable proxy for "I am in a meeting"
		proc = pyzoomproc.scan_for_proc(
			matching=re.compile(process_regex),
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
			psutil.wait_procs(
				[proc], 
				callback=pyzoomproc.process_end(shlex.split(offair_cmd)))

		# if we're not waiting for a process to end, only check every 5 seconds
		time.sleep(5)


if __name__ == '__main__':
	main(auto_envvar_prefix='PYZOOMPROC')