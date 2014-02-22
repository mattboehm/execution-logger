"""Events represent things happening during a program exection. They include:
Function call/return
Line of code executed
Exception raised"""
from datetime import datetime
from uuid import uuid4

class Event(object):
    """The base class for anything that happens that should be logged
    timestamp: datetime.datetime of when it happened, default:now
    event_type: string specifying what kind of event it is"""
    def __init__(self, uuid=None, timestamp=None):
        self.event_type = "event"
        self.uuid = uuid or uuid4()
        self.timestamp = timestamp or datetime.now()

    def to_data(self):
        """return json-serializable version of the event"""
        return {
            "type": self.event_type,
            "uuid": self.uuid,
            "timestamp": self.timestamp.strftime("%Y-%m-%DT%H:%M:%S.%f"),
        }

    @classmethod
    def from_data(cls, data):
        """construct an instance of the class from a data representation"""
        return cls(
            uuid=data.get("uuid"),
            timestamp=data.get("timestamp"),
        )

    @classmethod
    def from_debugger(cls, frame):
        """construct an instance from a python frame"""
        #TODO this is pretty pointless-- consider raising NotImplemented
        return cls()

class LineEvent(Event):
    """An event signifying when a line of code is executed"""
    def __init__(self, file_name, line_number, uuid=None, timestamp=None):
        super(LineEvent, self).__init__(uuid, timestamp)
        self.event_type = "line"
        self.file_name = file_name
        self.line_number = line_number

    def to_data(self):
        data = super(LineEvent, self).to_data()
        data.update({
            "file_name": self.file_name,
            "line_number": self.line_number,
        })
        return data

    @classmethod
    def from_data(cls, data):
        return cls(
            file_name=data.get("file_name"),
            line_number=data.get("line_number"),
            uuid=data.get("uuid"),
            timestamp=data.get("timestamp"),
        )

    @classmethod
    def from_debugger(cls, frame):
        #line = linecache.getline(fn, frame.f_lineno, frame.f_globals)
        return cls(
            file_name=frame.f_code.co_filename,
            line_number=frame.f_lineno,
        )

class FunctionEvent(Event):
    """base class for events related to functions (call, return, exception)"""
    def __init__(self, function_name, uuid=None, timestamp=None):
        super(FunctionEvent, self).__init__(uuid=uuid, timestamp=timestamp)
        self.event_type = "function"
        self.function_name = function_name

    def to_data(self):
        data = super(FunctionEvent, self).to_data()
        data.update({
            "function_name": self.function_name,
        })
        return data

    @classmethod
    def from_data(cls, data):
        return cls(
            function_name=data.get("function_name"),
        )

    @classmethod
    def from_debugger(cls, frame):
        """construct an instance from a python frame"""
        return cls(
            function_name=frame.f_code.co_name
        )


class CallEvent(FunctionEvent):
    """Function call event"""
    def __init__(self, function_name, uuid=None, timestamp=None):
        super(CallEvent, self).__init__(
            function_name=function_name,
            uuid=uuid,
            timestamp=timestamp,
        )
        self.event_type = "call"

class ReturnEvent(FunctionEvent):
    """function return event"""
    def __init__(self, function_name, uuid=None, timestamp=None):
        super(ReturnEvent, self).__init__(
            function_name=function_name,
            uuid=uuid,
            timestamp=timestamp,
        )
        self.event_type = "return"

class ExceptionEvent(Event):
    """Event representing an exception being raised
    There will be a separate event for each level of the stack
        that an exception is raised"""
    def __init__(self, function_name, uuid=None, timestamp=None):
        super(ExceptionEvent, self).__init__(
            function_name=function_name,
            uuid=uuid,
            timestamp=timestamp,
        )
        self.event_type = "exception"
