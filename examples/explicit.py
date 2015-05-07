"""Only log function marked with @log_function.
This is done by enabling the explicit_only option"""
from pylog.debugger import JsonFileEventLogger, LoggingDebugger, Options, log_function

@log_function
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

@log_function
def bax():
    pass

def baz():
    baz2()

@log_function
def baz2():
    pass

def main():
    "main"
    log_file = open("explicit_trace.txt", "w")
    event_logger = JsonFileEventLogger(log_file)
    options = Options(explicit_only=True)
    debugger = LoggingDebugger(event_logger, options=options)
    debugger.set_trace()
    foo(10)
    debugger.set_quit()

if __name__ == '__main__':
    main()
