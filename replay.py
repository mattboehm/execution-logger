import collections

class ImmutableStack(object):
    def __init__(self, items=None):
        self.items = tuple(items) if items else tuple()
    def push(self, item):
        return self.new(self.items + (item,))
    def pop(self):
        return self.new(self.items[:-1])
    def top(self):
        return self.items[-1]
    def __iter__(self):
        return self.items.__iter__()
    def __len__(self):
        return len(self.items)
    def __repr__(self):
        return u"ImmutableStack{}".format(repr(self.items))
    @classmethod
    def new(cls, items):
        return cls(items)

#class Cursor(object):
    #def __init__(self, iterable, index):
        #self._iterable = iterable
        #self._index = index
    
    #def has_previous(self):
        #pass

    #def has_next(self):
        #pass

    #@classmethod
    #def new(cls, iterable, index, *args, **kwargs):
        #return cls(iterable, index, *args, **kwargs)

Location = collections.namedtuple("Location", ["file", "line"])

class PushLocation(object):
    def __init__(self, location):
        self.location = location

    def undo_command(self):
        return PopLocation(self.location)

    def apply(self, stack):
        return stack.push(self.location)

class PopLocation(object):
    def __init__(self, location):
        self.location = location

    def undo_command(self):
        return PushLocation(self.location)

    def apply(self, stack):
        return stack.pop()

class ChangeLine(object):
    def __init__(self, old, new):
        self.old = old
        self.new = new

    def undo_command(self):
        return ChangeLine(self.new, self.old)

    def apply(self, stack):
        old_location = stack.top()
        return stack.pop().push(Location(old_location.file, self.new))

def get_command(stack, event):
    if event.event_type == "call":
        return PushLocation(Location(event.file_name, event.line_number))
    elif event.event_type in {"return", "exception"}:
        return PopLocation(stack.top())
    elif event.event_type == "line":
        #if the stack is empty (i.e. lines executed before a function is ever called), push a location on
        if not stack:
            return PushLocation(Location(event.file_name, event.line_number))
        return ChangeLine(stack.top().line, event.line_number)

#class LocationStack(object):
    #def __init__(self, locations=tuple()):
        #self.locations = ImmutableStack(locations)

    #def get_command(self, event):
        #return get_command(self.locations, event)

    #def apply(self, command):
        #return command.apply(self.locations)

class Stepper(object):
    def __init__(self, events):
        self.events = list(events)
        self.commands = []
        self.locations = ImmutableStack()
        self.next_event_index = 0

    def at_last_step(self):
        return self.next_event_index == len(self.events)

    def at_first_step(self):
        return self.next_event_index == 0

    def step_forwards(self):
        if not self.at_last_step():
            command = get_command(self.locations, self.events[self.next_event_index])
            self.commands.append(command)
            self.locations = command.apply(self.locations)
            self.next_event_index += 1

    def step_backwards(self):
        if not self.at_first_step():
            last_command = self.commands.pop()
            self.locations = last_command.undo_command().apply(self.locations)
            self.next_event_index -= 1

    def step_out(self):
        stack_depth = len(self.locations)
        while len(self.locations) >= stack_depth and not self.at_last_step():
            self.step_forwards()

    def step_over(self):
        stack_depth = len(self.locations)
        self.step_forwards()
        #if we stepped in, step back out
        if stack_depth < len(self.locations):
            self.step_out()

    def step_until_location(self, location):
        while self.locations.top() != location and not self.at_last_step():
            self.step_forwards()

if __name__ == '__main__':
    import fileinput
    import logreader
    from pprint import pprint
    reader = logreader.JsonFileEventReader(fileinput.input())
    stepper = Stepper(reader.iter_events())
    while not stepper.at_last_step():
        stepper.step_forwards()
        pprint(stepper.locations)
