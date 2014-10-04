"""Events represent things happening during a program exection. They include:
Function call/return
Line of code executed
Exception raised"""
from datetime import datetime
from uuid import uuid4

TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"

class Event(object):
    """The base class for anything that happens that should be logged
    timestamp: datetime.datetime of when it happened, default:now"""
    #event_type: string specifying what kind of event it is
    event_type = "event"

    def __init__(self, uuid=None, timestamp=None, file_name=None, line_number=None, last_line=None, last_call=None):
        self.uuid = uuid or str(uuid4())
        if timestamp and isinstance(timestamp, basestring):
            timestamp = datetime.strptime(timestamp, TIME_FORMAT)
        self.file_name = file_name
        self.line_number = line_number
        self.timestamp = timestamp or datetime.now()
        self.last_line = last_line
        self.last_call = last_call

    def to_data(self):
        """return json-serializable version of the event"""
        return {
            "type": self.event_type,
            "uuid": self.uuid,
            "timestamp": self.timestamp.strftime(TIME_FORMAT),
            "file_name": self.file_name,
            "line_number": self.line_number,
            "last_line": self.last_line,
            "last_call": self.last_call,
        }

    @classmethod
    def get_attributes_from_data(cls, data):
        return {
            "uuid": data.get("uuid"),
            "timestamp": data.get("timestamp"),
            "file_name": data.get("file_name"),
            "line_number": data.get("line_number"),
            "last_line": data.get("last_line"),
            "last_call": data.get("last_call"),
        }

    @classmethod
    def from_data(cls, data):
        """construct an instance of the class from a data representation"""
        return cls(**cls.get_attributes_from_data(data))
    
    @classmethod
    def get_attributes_from_state(cls, state):
        attributes = {
            "file_name": state.current_file_name,
            "line_number": state.current_line_number,
            "last_line": state.last_line,
            "last_call": state.last_call,
        }
        return attributes
    @classmethod
    def from_state(cls, state):
        """construct an instance from a python frame"""
        return cls(**cls.get_attributes_from_state(state))

class LineEvent(Event):
    """An event signifying when a line of code is executed"""
    event_type = "line"

class FunctionEvent(Event):
    """base class for events related to functions (call, return, exception)"""
    event_type = "function"
    def __init__(self, function_name, **kwargs):
        super(FunctionEvent, self).__init__(**kwargs)
        self.function_name = function_name

    def to_data(self):
        data = super(FunctionEvent, self).to_data()
        data.update({
            "function_name": self.function_name,
        })
        return data

    @classmethod
    def get_attributes_from_data(cls, data):
        """construct an instance from a python frame"""
        attributes = super(FunctionEvent, cls).get_attributes_from_data(data)
        attributes["function_name"] = data.get("function_name")
        return attributes

    @classmethod
    def get_attributes_from_state(cls, state):
        """construct an instance from a python frame"""
        attributes = super(FunctionEvent, cls).get_attributes_from_state(state)
        attributes["function_name"] = state.current_function_name
        return attributes


class CallEvent(FunctionEvent):
    """Function call event"""
    event_type = "call"

class ReturnEvent(FunctionEvent):
    """Function call event"""
    event_type = "return"

class ExceptionEvent(FunctionEvent):
    """Event representing an exception being raised
    There will be a separate event for each level of the stack
        that an exception is raised"""
    event_type = "exception"

#A list of all valid event classes
event_classes = (Event, LineEvent, FunctionEvent, CallEvent, ReturnEvent, ExceptionEvent)
event_lookup = {event.event_type: event for event in event_classes}
