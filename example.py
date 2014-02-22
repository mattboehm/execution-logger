"""Uses the LoggingDebuger on an example program"""
from pylog import JsonFileEventLogger, LoggingDebugger

def foo(n):
    "foos"
    print 'foo(', n, ')'
    x = bar(n*10)
    print 'bar returned', x

def bar(a):
    "bars"
    print 'bar(', a, ')'
    return a/2

def main():
    "main"
    log_file = open("trace.txt", "w")
    event_logger = JsonFileEventLogger(log_file)
    debugger = LoggingDebugger(event_logger)
    debugger.set_trace()
    foo(10)
    debugger.set_quit()

if __name__ == '__main__':
    main()
