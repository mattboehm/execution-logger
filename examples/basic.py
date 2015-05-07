"""Uses the LoggingDebuger on an example program
saves the trace to a trace.txt file in the current directory
For this to work currently, the parent directory should be in your python path"""
from pylog.debugger import JsonFileEventLogger, LoggingDebugger, Options

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

def inefficient_fib(n):
    if n < 3:
        return 1
    else:
        return inefficient_fib(n-1) + inefficient_fib(n-2)

def main():
    "main"
    log_file = open("basic_trace.txt", "w")
    event_logger = JsonFileEventLogger(log_file)
    options = Options(log_lines=True, log_args=True, log_retval=True)
    debugger = LoggingDebugger(event_logger, options=options)
    debugger.set_trace()
    foo(10)
    inefficient_fib(10)
    debugger.set_quit()

if __name__ == '__main__':
    main()
