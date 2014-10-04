import json
import bdb
from events import LineEvent, CallEvent, ReturnEvent, ExceptionEvent

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
    def __init__(self, event_logger, state=None, skip=None, log_lines=True):
        bdb.Bdb.__init__(self, skip)
        self.event_logger = event_logger
        self.state = state or ProgramState()
        if log_lines:
            self.user_line = self.user_line_func

    def user_call(self, frame, args):
        self.state.frame = frame
        call_event = CallEvent.from_state(self.state)
        self.event_logger.log_event(call_event)
        self.state.add_call(call_event.uuid)

    def user_line_func(self, frame):
        self.state.frame = frame
        line_event = LineEvent.from_state(self.state)
        self.event_logger.log_event(line_event)
        self.state.add_line(line_event.uuid)

        #import linecache
        #name = frame.f_code.co_name
        #fn = self.canonic(frame.f_code.co_filename)
        #line = linecache.getline(fn, frame.f_lineno, frame.f_globals)
        #print '+++', fn, frame.f_lineno, name, ':', line.strip()

    def user_return(self, frame, retval):
        self.state.frame = frame
        return_event = ReturnEvent.from_state(self.state)
        self.event_logger.log_event(return_event)
        self.state.pop_call()

    def user_exception(self, frame, exc_stuff):
        self.state.frame = frame
        exception_event = ExceptionEvent.from_state(self.state)
        self.event_logger.log_event(exception_event)
        self.state.pop_call()
        self.set_continue()
