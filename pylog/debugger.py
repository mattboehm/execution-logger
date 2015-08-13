"""Execution logger

Usage:
  pylog <command>


Commands:
  test: run the tests

"""
import bdb
import collections
import inspect
import json
import os
from events import LineEvent, CallEvent, ReturnEvent, ExceptionEvent, FunctionSet, FunctionCall

class ProgramState(object):
    def __init__(self, file_name, line_number, function_name):
        self.file_name = file_name
        self.line_number = line_number
        self.function_name = function_name

    def to_data(self):
        return [self.file_name, self.line_number, self.function_name]

    @classmethod
    def from_data(cls, data):
        return cls(*data)

    @classmethod
    def from_frame(cls, frame):
        return cls(
            file_name=os.path.abspath(frame.f_code.co_filename),
            line_number=frame.f_lineno,
            function_name=frame.f_code.co_name,
        )

State = collections.namedtuple("State", ["file_name", "line_number", "function_name", "args", "retval", "exception"])
def get_state(frame, args=None, retval=None, exception=None):
    return State(
        file_name=os.path.abspath(frame.f_code.co_filename),
        line_number=frame.f_lineno,
        function_name=frame.f_code.co_name,
        args=args,
        retval=retval,
        exception=exception,
    )

def log_function(f):
    """decorator that tells pylog to explicitly log this function"""
    f.__log_call = True
    return f

class JsonFileEventLogger(object):
    def __init__(self, log_file):
        """log_file: an apen stream to write to"""
        self.log_file = log_file

    def log_event(self, event):
        self.log_file.write(json.dumps(event.to_data()) + "\n")

Option = collections.namedtuple("Option", ["name", "description", "default"])
class Options(object):
    options = [
        Option(
            name="log_lines",
            description="Whether the logger should log lines or not",
            default=False,
        ),
        Option(
            name="log_args",
            description="Whether the logger should log a function's arguments when it's called",
            default=False,
        ),
        Option(
            name="log_retval",
            description="Whether the logger should log the return value for Return events",
            default=False,
        ),
        Option(
            name="explicit_only",
            description="If true, only log functions with @log_function decorator",
            default=False,
        ),
            
    ]

    def __init__(self, **kwargs):
        self._data = {
            option.name: kwargs.get(option.name, option.default)
            for option in self.options
        }

    def __getitem__(self, key):
        return self._data[key]

class LoggingDebugger(bdb.Bdb):
    def __init__(self, event_logger, skip=None, options=None):
        bdb.Bdb.__init__(self, skip)
        self.event_logger = event_logger
        self.options = options or Options()
        if self.options["log_lines"]:
            self.user_line = self.user_line_func

    def user_call(self, frame, args):
        if self.should_log(frame):
            arg_string = None
            if self.options["log_args"]:
                arg_string = self.format_args(inspect.getargvalues(frame))

            state = get_state(frame, args=arg_string)
            call_event = CallEvent.from_state(state)
            self.event_logger.log_event(call_event)

    def user_line_func(self, frame):
        if self.should_log(frame):
            line_event = LineEvent.from_state(ProgramState.from_frame(frame))
            self.event_logger.log_event(line_event)

    def user_return(self, frame, retval):
        if self.should_log(frame):
            retval_string = self.format_retval(retval) if self.options["log_retval"] else None
            state = get_state(frame, retval=retval_string)
            return_event = ReturnEvent.from_state(state)
            self.event_logger.log_event(return_event)

    def user_exception(self, frame, exc_stuff):
        if self.should_log(frame):
            exception_event = ExceptionEvent.from_state(ProgramState.from_frame(frame))
            self.event_logger.log_event(exception_event)

    def format_args(self, args):
        """Format the arguments"""
        return inspect.formatargvalues(*args)[:500]

    def format_retval(self, retval):
        """Format the return value"""
        return repr(retval)[:500]

    def format_exc_stuff(self, exc_stuff):
        pass

    def should_log(self, frame):
        return (not self.options["explicit_only"]) or getattr(frame.f_globals[frame.f_code.co_name], "__log_call", False)
