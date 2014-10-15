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
                event_json = json.loads(line)
                event_class = events.event_lookup[event_json["type"]]
                yield event_class.from_data(event_json)

