"""Uses the LoggingDebuger on an example program
saves the trace to a trace.txt file in the current directory
For this to work currently, the parent directory should be in your python path"""
from pylog import JsonFileEventLogger, LoggingDebugger

def foo(n):
    "foos"
    print 'foo(', n, ')'
    x = bar(n*10)
    print 'bar returned', x

def bar(a):
    "bars"
    print 'bar(', a, ')'
    bax()
    baz()
    return a/2

def bax():
    pass

def baz():
    baz2()

def baz2():
    pass

def main():
    "main"
    log_file = open("basic_trace.txt", "w")
    event_logger = JsonFileEventLogger(log_file)
    debugger = LoggingDebugger(event_logger, log_lines=True)
    debugger.set_trace()
    foo(10)
    debugger.set_quit()

if __name__ == '__main__':
    main()
