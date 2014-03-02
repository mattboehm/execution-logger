import json
import bdb
from events import LineEvent, CallEvent, ReturnEvent

#set efm=%.%#line_number\":\ %l\\,\ \"file_name\":\ \"%f\"%.%#

class JsonFileEventLogger(object):
    def __init__(self, log_file):
        """log_file: an apen stream to write to"""
        self.log_file = log_file
    
    def log_event(self, event):
        self.log_file.write(json.dumps(event.to_data()) + "\n")

class LoggingDebugger(bdb.Bdb):
    def __init__(self, event_logger, skip=None):
        bdb.Bdb.__init__(self, skip)
        self.event_logger = event_logger
        self.last_line = None
        self.call_stack = []

    def user_call(self, frame, args):
        event = CallEvent.from_debugger(frame)
        self.event_logger.log_event(event)
        self.user_line(frame)

    def user_line(self, frame):
        event = LineEvent.from_debugger(frame, self.last_line)
        self.event_logger.log_event(event)
        self.last_line = event
        #import linecache
        #name = frame.f_code.co_name
        #fn = self.canonic(frame.f_code.co_filename)
        #line = linecache.getline(fn, frame.f_lineno, frame.f_globals)
        #print '+++', fn, frame.f_lineno, name, ':', line.strip()

    def user_return(self, frame, retval):
        event = ReturnEvent.from_debugger(frame)
        self.event_logger.log_event(event)

    def user_exception(self, frame, exc_stuff):
        #TODO implement
        print '<<< exception', exc_stuff
        self.set_continue()
