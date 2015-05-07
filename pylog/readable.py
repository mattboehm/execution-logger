"""Convert default pylog output to a human-readable format"""
import fileinput
import json
for line in fileinput.input():
    event = json.loads(line)
    print u"{time}\t{file}:{line}\t{type}\t{function}".format(
        time=event["timestamp"],
        file=event["file_name"],
        line=event["line_number"],
        type=event["type"],
        function=event.get("function_name", ""),
    )
