import json
import bdb
import os
from events import LineEvent, CallEvent, ReturnEvent, ExceptionEvent, FunctionSet, FunctionCall

#set efm=%.%#line_number\":\ %l\\,\ \"file_name\":\ \"%f\"%.%#

class ProgramState(object):
    def __init__(self, frame=None, last_line=None, call_stack=None):
        self.frame = frame
        self.last_line = last_line
        self.call_stack = call_stack or []

    @property
    def current_file_name(self):
        return os.path.abspath(self.frame.f_code.co_filename)

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
        #self.state.add_call(call_event.uuid)

    def user_line_func(self, frame):
        self.state.frame = frame
        line_event = LineEvent.from_state(self.state)
        self.event_logger.log_event(line_event)
        #self.state.add_line(line_event.uuid)

        #import linecache
        #name = frame.f_code.co_name
        #fn = self.canonic(frame.f_code.co_filename)
        #line = linecache.getline(fn, frame.f_lineno, frame.f_globals)
        #print '+++', fn, frame.f_lineno, name, ':', line.strip()

    def user_return(self, frame, retval):
        self.state.frame = frame
        return_event = ReturnEvent.from_state(self.state)
        self.event_logger.log_event(return_event)
        #self.state.pop_call()

    def user_exception(self, frame, exc_stuff):
        self.state.frame = frame
        exception_event = ExceptionEvent.from_state(self.state)
        self.event_logger.log_event(exception_event)

class EventHandler(object):
    def __init__(self, events):
        """events is an iterable of Event objects"""
        self.events = events

    def process_events(self):
        self.function_set = FunctionSet()
        self.root_calls = []
        function_call_stack = []
        state = ProgramState()
        
        for event in self.events:
            if event.event_type == "call":
                function = self.function_set.add_function_from_event(event)
                if state.last_call:
                    self.function_set.add_call(state.last_call, function)
                function_call_stack.append(FunctionCall(event))
                if len(function_call_stack) > 1:
                    function_call_stack[-2].sub_events.append(function_call_stack[-1])
                state.add_call(function)

            elif event.event_type in {"return", "exception"}:
                if function_call_stack:
                    function_call_stack[-1].return_event = event
                    popped_call = function_call_stack.pop()
                    if len(function_call_stack) == 1:
                        self.root_calls.append(popped_call)
                state.pop_call()
