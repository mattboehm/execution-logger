"""A script to test a few alternate formats.

Pipe a file into it (or call it w/ a file as an arg) and it prints:
* FunctionSet format
* FunctionCall  format
It also generates files ./functions.dot and ./functions.dot.svg"""
import fileinput
from pylog import EventHandler
import logreader
from pprint import pprint
import graphviz
reader = logreader.JsonFileEventReader(fileinput.input())
event_handler = EventHandler(reader.iter_events())
event_handler.process_events()
pprint(event_handler.function_set.to_data())
pprint([call.to_data() for call in event_handler.root_calls])
def fmt_key(key):
    return " ".join(map(str, key))

def make_function_graph(function_set):
    dot = graphviz.Digraph()
    for key, function in function_set.functions.iteritems():
        dot.node(
            fmt_key(key),
            "{}\\n{}:{}".format(function.name, function.file_name, function.line_number),
            shape="box",
        )
        for call in function.calls:
            dot.edge(fmt_key(key), fmt_key(call))
    dot.format = "svg"
    dot.render('functions.dot')
make_function_graph(event_handler.function_set)
