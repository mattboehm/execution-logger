"""Execution logger

Usage:
  pylog <command> [<program> [<args>...]] [--output=FILE]

Options:
  -o FILE --output=FILE  output file [default: log.txt]

Commands:
  test: run the tests
  record: log an execution

"""
import docopt
import subprocess
import sys

from pylog import test_pylog, debugger

def main():
    options = docopt.docopt(__doc__)
    print options
    if options["<command>"] == "test":
        print "testing"
    elif options["<command>"] == "record":
        log_file = open(options["--output"], "w")
        event_logger = debugger.JsonFileEventLogger(log_file)
        debug_options = debugger.Options(log_lines=True, log_args=True, log_retval=True)
        dbg = debugger.LoggingDebugger(event_logger, options=debug_options)
        dbg.set_trace()
        program = options["<program>"]
        sys.argv = [program] + options["<args>"]
        execfile(program)
        dbg.set_quit()
