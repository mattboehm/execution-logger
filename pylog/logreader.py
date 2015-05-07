import json
import events
class JsonFileEventReader(object):
    """Reads a log file"""

    def __init__(self, log_file):
        """log_file: an open file to read from"""
        self.log_file = log_file

    def iter_events(self):
        for line in self.log_file:
            if line:
                event_data = json.loads(line)
                yield events.event_from_data(event_data)
