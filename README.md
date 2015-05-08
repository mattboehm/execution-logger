Pylog is a Python debugger that logs events (function called, function returned, line executed, exception raised) as a program executes.

These logs are meant to be used by other applications to visualize program execution or otherwise help a developer understand what their application is doing.

WARNING: This project is still in an alpha phase. It produces MASSIVE logs, is very slow, and the API may change frequently. Use at your own risk.

Usage
=====

Instead of saying `python foo.py arg1 arg2` say `pylog record foo.py arg1 arg2`. This will dump the log of events into a log.txt file in the current directory.

To view a flame chart of the log file, you could then run `pylog-web log.txt` and navigate to localhost:8080.
