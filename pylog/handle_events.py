"""A script to test a few alternate formats.

Pipe a file into it (or call it w/ a file as an arg) and it prints:
* FunctionSet format
* FunctionCall  format
It also generates files ./functions.dot and ./functions.dot.svg"""
import fileinput
from pylog import events
from pprint import pprint
import graphviz

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
    return dot

def main():
    """"""
    evts = events.events_from_file(fileinput.input())
    func_set = events.FunctionSet.from_events(evts)
    graph = make_function_graph(func_set)
    graph.format = "svg"
    graph.render('functions.dot')

if __name__ == '__main__':
    main()
