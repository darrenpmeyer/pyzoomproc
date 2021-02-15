# PyZoomProc

Monitors your Mac for a process that indicates Zoom is connected to a meeting,
in order to run on-air/off-air scripts.

I use this to turn on an "on air light" whenever I join a Zoom meeting, and 
turn it off when I exit a meeting.

**NOTE:** The `pyzoomproc.py` script is configured to use bash to launch 
Python 3.8 via `pyenv`. If that doesn't suit you, modify the first lines or
run `python3 pyzoomproc.py`. Examples here use the latter.

```
python3 pyzoomproc.py /path/to/onair-script.sh
```

The python script checks every 5 seconds to see if you're joined to a Zoom
meeting.

When you join, it executes `/path/to/onair-script.sh on` and waits for the
Zoom meeting to end.

When you leave the zoom meeting, it executes `/path/to/onair-script.sh off`
and resumes checking every 5 seconds to see if you have joined a meeting.

If you want different scripts to be run, *with no parameters*, use:

```
python3 pyzoomproc.py /path/to/onair-script.sh /path/to/offair-script.sh
```

# Running automatically at login

Modify the included `com.darrenpmeyer.pyzoomproc.plist` with the correct paths
and arguments for your setup.

**NOTE:** if you do not use pyenv, you should change the `pyzoomproc.py` or
edit the plist to call python3 explicitly, or you'll have a bad time

Copy the plist file to `~/Library/LaunchAgents`

```
launchctl load ~/Library/LaunchAgents/com.darrenpmeyer.pyzoomproc.plist
```

The agent will now run at login time; if it quits for any reason, launchd will
wait 10 seconds before respawning it.