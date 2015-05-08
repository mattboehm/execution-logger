"""Events represent things happening during a program exection. They include:
Function call/return
Line of code executed
Exception raised"""
from datetime import datetime
import itertools
from six import itervalues, string_types

TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"

class Event(object):
    """The base class for anything that happens that should be logged
    timestamp: datetime.datetime of when it happened, default:now"""
    #event_type: string specifying what kind of event it is
    event_type = "event"
    stack_change = 0

    def __init__(self, timestamp=None, file_name=None, line_number=None):
        if timestamp and isinstance(timestamp, string_types):
            timestamp = datetime.strptime(timestamp, TIME_FORMAT)
        self.file_name = file_name
        self.line_number = line_number
        self.timestamp = timestamp or datetime.now()

    def to_data(self):
        """return json-serializable version of the event"""
        return {
            "type": self.event_type,
            "timestamp": self.timestamp.strftime(TIME_FORMAT),
            "file_name": self.file_name,
            "line_number": self.line_number,
        }

    @classmethod
    def get_attributes_from_data(cls, data):
        assert data.get("type", cls.event_type) == cls.event_type, "Bad event type"
        return {
            "timestamp": data.get("timestamp"),
            "file_name": data.get("file_name"),
            "line_number": data.get("line_number"),
        }

    @classmethod
    def from_data(cls, data):
        """construct an instance of the class from a data representation"""
        return cls(**cls.get_attributes_from_data(data))

    @classmethod
    def get_attributes_from_state(cls, state):
        attributes = {
            "file_name": state.file_name,
            "line_number": state.line_number,
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
    """Base class for events related to functions (call, return, exception)"""
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
        attributes["function_name"] = state.function_name
        return attributes


class CallEvent(FunctionEvent):
    """Function call event"""
    event_type = "call"
    stack_change = 1
    def __init__(self, args=None, **kwargs):
        super(CallEvent, self).__init__(**kwargs)
        self.args = args

    def to_data(self):
        data = super(CallEvent, self).to_data()
        data.update({
            "args": self.args,
        })
        return data

    @classmethod
    def get_attributes_from_data(cls, data):
        """construct an instance from a python frame"""
        attributes = super(CallEvent, cls).get_attributes_from_data(data)
        attributes["args"] = data.get("args")
        return attributes

    @classmethod
    def get_attributes_from_state(cls, state):
        attributes = super(CallEvent, cls).get_attributes_from_state(state)
        attributes["args"] = state.args
        return attributes

class ReturnEvent(FunctionEvent):
    """When a function returns"""
    event_type = "return"
    stack_change = -1
    def __init__(self, retval=None, **kwargs):
        super(ReturnEvent, self).__init__(**kwargs)
        self.retval = retval

    def to_data(self):
        data = super(ReturnEvent, self).to_data()
        data.update({
            "retval": self.retval,
        })
        return data

    @classmethod
    def get_attributes_from_data(cls, data):
        attributes = super(ReturnEvent, cls).get_attributes_from_data(data)
        attributes["retval"] = data.get("retval")
        return attributes

    @classmethod
    def get_attributes_from_state(cls, state):
        attributes = super(ReturnEvent, cls).get_attributes_from_state(state)
        attributes["retval"] = state.retval
        return attributes

class ExceptionEvent(FunctionEvent):
    """Event representing an exception being raised
    There will be a separate event for each level of the stack
        that an exception is raised"""
    event_type = "exception"
    stack_change = -1

#A list of all valid event classes
EVENT_CLASSES = (Event, LineEvent, FunctionEvent, CallEvent, ReturnEvent, ExceptionEvent)
EVENT_LOOKUP = {event.event_type: event for event in EVENT_CLASSES}

def event_from_data(data, event_lookup=EVENT_LOOKUP):
    """Convert a python dict to an Event class"""
    event_class = event_lookup[data["type"]]
    return event_class.from_data(data)

#TODO move to different file?
class ExecutionTree(object):
    def __init__(self, sub_events=None):
        self.sub_events = sub_events or []

    @classmethod
    def from_events(cls, events):
        result = cls()
        call_stack = [result]
        for event in events:
            if event.stack_change > 0:
                call_stack.append(FunctionCall(event))
                call_stack[-2].sub_events.append(call_stack[-1])
            elif event.stack_change < 0:
                popped_call = call_stack.pop()
                if call_stack:
                    popped_call.return_event = event
                else:
                    return popped_call
        return result

    def to_data(self):
        return [event.to_data() for event in self.sub_events]

    def to_flame_chart(self, max_depth):
        start_time = self.sub_events[0].call_event.timestamp
        stop_time = self.sub_events[-1].return_event.timestamp
        total_seconds = (stop_time - start_time).total_seconds()
        id_gen = itertools.count(1)
        result = {
            "start_time": start_time.strftime(TIME_FORMAT),
            "total_seconds": total_seconds,
            "calls": [],
        }
        for sub_event in self.sub_events:
            for call in sub_event.to_flame_chart(max_depth, 0, None, start_time, id_gen):
                result["calls"].append(call)
        return result

class FunctionCall(object):
    def __init__(self, call_event=None, sub_events=None, return_event=None):
        self.call_event = call_event
        self.sub_events = sub_events or []
        self.return_event = return_event

    def to_data(self, depth=None, parent=None):
        """serialize to data
        
        @param depth [int, None] how many levels deep to go.
            0: no sub-events.
            1: 1 level of sub-events
            None: no limit"""
        if depth is not None:
            depth -= 1
        result = {
            "call_event": self.call_event.to_data(),
            "sub_events": [],
            "return_event": self.return_event.to_data(),
        }
        if depth != -1:
            result["sub_events"] = [event.to_data(depth, self) for event in self.sub_events]
        return result

    def to_flame_chart(self, max_depth, cur_depth, parent_id, start_time, id_gen):
        this_id = next(id_gen)
        if self.call_event and self.return_event:
            yield {
                "id": this_id,
                "depth": cur_depth,
                "parent_id": parent_id,
                "call_time": (self.call_event.timestamp - start_time).total_seconds(),
                "ret_time": (self.return_event.timestamp - start_time).total_seconds(),
                "name": self.call_event.function_name,
                "args": self.call_event.args,
                "retval": self.return_event.retval,
            }
        if cur_depth < max_depth:
            for evt in self.sub_events:
                for call in evt.to_flame_chart(max_depth, cur_depth + 1, this_id, start_time, id_gen):
                    yield call


class Function(object):
    def __init__(self, name, file_name, line_number, called_by=None, calls=None):
        self.name = name
        self.file_name = file_name
        self.line_number = line_number
        self.called_by = set(called_by or [])
        self.calls = set(calls or [])

    @property
    def key(self):
        return (self.name, self.file_name, self.line_number)

    def to_data(self):
        return {
            "name": self.name,
            "file_name": self.file_name,
            "line_number": self.line_number,
            "called_by": list(sorted(self.called_by)),
            "calls": list(sorted(self.calls)),
        }

class FunctionSet(object):
    def __init__(self, functions=None):
        self.functions = functions or {}

    def get_function(self, name, file_name, line_number):
        return self.functions.get((name, file_name, line_number))

    def add_function_from_event(self, event):
        return self.add_function(event.function_name, event.file_name, event.line_number)

    def add_function(self, name, file_name, line_number):
        function = self.get_function(name, file_name, line_number)
        if not function:
            function = Function(name, file_name, line_number)
            self.functions[(name, file_name, line_number)] = function
        return function

    def add_call(self, caller, callee):
        """assumes both functions have been added"""
        self.functions[caller.key].calls.add(callee.key)
        self.functions[callee.key].called_by.add(caller.key)

    def to_data(self):
        return [function.to_data() for function in itervalues(self.functions)]

    @classmethod
    def from_events(cls, events):
        result = cls()
        call_stack = []
        for event in events:
            if event.stack_change > 0:
                function = result.add_function_from_event(event)
                if call_stack:
                    result.add_call(call_stack[-1], function)
                call_stack.append(function)
            elif event.stack_change < 0:
                if call_stack:
                    call_stack.pop()
        return result
