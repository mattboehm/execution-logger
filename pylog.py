import json
import bdb
from events import LineEvent, CallEvent, ReturnEvent

#set efm=%.%#line_number\":\ %l\\,\ \"file_name\":\ \"%f\"%.%#

class ProgramState(object):
    def __init__(self, frame=None, last_line=None, call_stack=None):
        self.frame = frame
        self.last_line = last_line
        self.call_stack = call_stack or []

    @property
    def current_file_name(self):
        return self.frame.f_code.co_filename

    @property
    def current_line_number(self):
        return self.frame.f_lineno

    @property
    def current_function_name(self):
        return self.frame.f_code.co_name

    @property
    def last_call(self):
        return (self.call_stack and self.call_stack[-1]) or None

    def add_line(self, line_id):
        self.last_line = line_id

    def add_call(self, call_id):
        self.call_stack.append(call_id)

    def pop_call(self):
        if self.call_stack:
            return self.call_stack.pop()
        return None
    
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
