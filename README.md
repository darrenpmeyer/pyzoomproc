# PyZoomProc

Monitors your Mac for a process that indicates Zoom is connected to a meeting,
in order to run on-air/off-air scripts.

I use this to turn on an "on air light" whenever I join a Zoom meeting, and 
turn it off when I exit a meeting.

After setting up (see Setup section below):

```
pyzoomproc --onair /path/to/onair-script.sh
```

The python script checks every 5 seconds to see if you're joined to a Zoom
meeting.

When you join, it executes `/path/to/onair-script.sh on` and waits for the
Zoom meeting to end.

When you leave the zoom meeting, it executes `/path/to/onair-script.sh off`
and resumes checking every 5 seconds to see if you have joined a meeting.

If you want different scripts to be run, *with no parameters*, use:

```
pyzoomproc --onair /path/to/onair-script.sh \
           --offair /path/to/offair-script.sh
```

You can run `pyzoomproc --help` for more options

# Setup

Make sure you have at least Python3.6

For most uses:

```
pip3 install git+https://github.com/darrenpmeyer/pyzoomproc
```

But note that **this does not work with launchd** (or at least, I can't
figure out how to make it work); see the "run without installing" section if
you want to use the Launch Agent

## Run without installing

This includes using a virtualenv; you may need to `pip3 install virtualenv`
before proceeding. Python 3.6+ is required.

```
git clone https://github.com/darrenpmeyer/pyzoomproc.git
cd pyzoomproc
python3 -m virtualenv venv
venv/bin/pip install -e .
```

To run:

```
cd /path/to/pyzoomproc
venv/bin/python3 -m pyzoomproc [OPTIONS]
```

To update, just `git pull`

# Running automatically at login

*Modify the included `com.darrenpmeyer.pyzoomproc.plist` with the correct paths
and arguments for your setup. Make sure you use an absolute path!*

**NOTES:** 

1. This isn't working with `pip install`, you are required to follow the 
   "run without installing" section of the Setup
2. it is important to set the WorkingDirectory value to the path where
   you checked out this repository. 

Copy the plist file to `~/Library/LaunchAgents`

```
launchctl load ~/Library/LaunchAgents/com.darrenpmeyer.pyzoomproc.plist
```

The agent will now run at login time; if it quits for any reason, launchd will
wait 10 seconds before respawning it.